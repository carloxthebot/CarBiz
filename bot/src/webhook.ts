// LINE webhook handler。設計原則跟 CF 版一模一樣,差別在 push 不再繞遠路:
//   1. HMAC 驗簽先做,壞的直接 401
//   2. 立刻回 200(否則 LINE 5 秒沒收到會重送)
//   3. 白名單 + 去重 + 觸發等待畫面 + 建 task + enqueue —— 全部在 background
//   4. agent.ts 收 task 跑 Claude,結果 push 給使用者
import { Hono } from 'hono'
import { verifyLineSignature } from './line/signature'
import { reply } from './line/client'
import { startLoading } from './line/loading'
import { getBotUserId } from './line/botinfo'
import { createTask } from './tasks'
import { enqueue } from './agent'
import { saveImage, stashImage, takePendingImages } from './images'
import { pushDigest } from './digest'
import { env } from './env'
import type { LineEvent, LineMentionee, LineWebhookBody } from './types'

export const webhookApp = new Hono()

// 純文字觸發:訊息開頭是 「@瑞斯」「瑞斯,」「RaysRevo:」之類就算叫 bot。
// 只看開頭,避免聊天中提到「瑞斯」就誤觸。
const TEXT_TRIGGER = (() => {
  const aliases = env.BOT_ALIASES.split(',').map((s) => s.trim()).filter(Boolean)
    .sort((a, b) => b.length - a.length) // 長的先比,免得「瑞斯」吃掉「瑞斯車業」
    .map((s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  return aliases.length ? new RegExp(`^\\s*@?\\s*(?:${aliases.join('|')})(?:車業)?\\s*[,，:：、]?\\s*`, 'i') : null
})()

async function isAddressed(text: string, mentionees: LineMentionee[]): Promise<boolean> {
  if (TEXT_TRIGGER?.test(text)) return true
  try {
    const botId = await getBotUserId()
    return mentionees.some((m) => m.userId === botId)
  } catch (err) {
    console.error('cannot determine bot userId', err)
    return false
  }
}

webhookApp.post('/webhook', async (c) => {
  const signature = c.req.header('x-line-signature')
  const rawBody = await c.req.text()
  if (!(await verifyLineSignature(env.LINE_CHANNEL_SECRET, rawBody, signature))) {
    return c.text('bad signature', 401)
  }
  let body: LineWebhookBody
  try {
    body = JSON.parse(rawBody)
  } catch {
    return c.text('bad json', 400)
  }
  // fire-and-forget:立刻回 200,細節在背景做
  handleEvents(body.events ?? []).catch((err) => console.error('handleEvents crashed', err))
  return c.text('ok', 200)
})

async function handleEvents(events: LineEvent[]): Promise<void> {
  const admins = new Set(
    env.ADMIN_LINE_USER_IDS
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean),
  )
  for (const ev of events) {
    try {
      await handleEvent(ev, admins)
    } catch (err) {
      console.error('handleEvent error', err)
    }
  }
}

async function handleEvent(ev: LineEvent, admins: Set<string>): Promise<void> {
  if (ev.type !== 'message' || !ev.message || !ev.source) return
  if (!ev.webhookEventId) return // 沒 id 就沒法去重,寧可跳過

  const userId = ev.source.userId
  const channelId =
    ev.source.type === 'group' ? ev.source.groupId :
    ev.source.type === 'room'  ? ev.source.roomId  :
    userId
  if (!userId || !channelId) return

  const isGroup = ev.source.type !== 'user'

  // 圖片:1:1 直接成任務;群組先暫存,等同一人 5 分鐘內叫 bot 的文字一起帶上。
  if (ev.message.type === 'image') {
    if (admins.size > 0 && !admins.has(userId)) return
    let path: string
    try { path = await saveImage(ev.message.id) } catch (err) {
      console.error('image download failed', err); return
    }
    if (isGroup) { stashImage(channelId, userId, path); return }
    const task = createTask({
      eventId: ev.webhookEventId, lineUserId: userId, channelId,
      rawMessage: '(使用者傳了一張圖片,沒有文字。看圖判斷要做什麼。)',
      imagePaths: [path],
    })
    if (!task) return
    await startLoading(channelId, 30)
    enqueue(task)
    return
  }

  if (ev.message.type !== 'text' || !ev.message.text) {
    if (!isGroup && ev.replyToken) await reply(ev.replyToken, '目前只支援文字與圖片。')
    return
  }

  const mentionees = ev.message.mention?.mentionees ?? []

  // `myid` 是給非白名單使用者查自己 userId 的暗號,不吃 Claude、不看白名單。
  // 1:1 直接回;群組要 @ bot 才回,避免無故廣播。
  const rawText = ev.message.text
  const bodyText = stripMentions(rawText, mentionees).replace(TEXT_TRIGGER ?? /$^/, '').trim()

  if (bodyText.toLowerCase() === 'myid') {
    if (isGroup && !(await isAddressed(rawText, mentionees))) return
    if (ev.replyToken) await reply(ev.replyToken, `你的 userId:\n\n${userId}`)
    return
  }

  // 群組/多人聊天:必須叫到 bot(真 @mention 或開頭打別名)才回應。
  // 沒叫 = 一般聊天,完全靜默,也不做白名單檢查(不然會廣播「您沒有權限」)。
  if (isGroup && !(await isAddressed(rawText, mentionees))) return

  // 白名單:非管理員不建 task。1:1 明確回一句;群組已 @ 過了但不是白名單
  // 使用者,只 log 讓管理者能撈 userId,不對群組廣播。
  if (admins.size > 0 && !admins.has(userId)) {
    console.warn(`[whitelist reject] channel=${channelId} userId=${userId} msg="${ev.message.text.slice(0,60)}"`)
    if (!isGroup && ev.replyToken) {
      await reply(ev.replyToken, '您沒有權限使用這個機器人。若需存取請找管理員將您的 userId 加入白名單(打 myid 查你自己的 userId)。')
    }
    return
  }

  // @mention 與別名前綴都已切掉,給 Claude 乾淨的問題
  const cleanText = bodyText
  if (!cleanText) return // 只有 @ 沒實質內容,略過

  // 「早報」走固定報表,不經 Claude(0 token、3 秒),推回這個 channel
  if (/^(早報|每日摘要|摘要|digest)$/i.test(cleanText)) {
    await pushDigest(`manual by ${userId.slice(0, 8)}`, [channelId])
    return
  }

  const task = createTask({
    eventId: ev.webhookEventId,
    lineUserId: userId,
    channelId,
    rawMessage: cleanText,
    imagePaths: takePendingImages(channelId, userId), // 群組剛丟的圖一起帶上;1:1 通常是空的
  })
  if (!task) return // 重送已被去重

  // 等待畫面:1:1 有 loading 動畫(不佔額度),群組沒有 —— 直接等結果,
  // 「收到,處理中」廣播沒意義又吵。
  if (ev.source.type === 'user') {
    await startLoading(channelId, 30)
  }

  enqueue(task)
}

// 把 mention 的 @xxx 文字段從原文切掉。反向切避免 index 位移。
function stripMentions(text: string, mentionees: LineMentionee[]): string {
  if (!mentionees.length) return text
  const sorted = [...mentionees].sort((a, b) => (b.index ?? 0) - (a.index ?? 0))
  let out = text
  for (const m of sorted) {
    if (m.index === undefined || m.length === undefined) continue
    out = out.slice(0, m.index) + out.slice(m.index + m.length)
  }
  return out
}
