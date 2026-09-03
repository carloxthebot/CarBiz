// LINE webhook handler。設計原則跟 CF 版一模一樣,差別在 push 不再繞遠路:
//   1. HMAC 驗簽先做,壞的直接 401
//   2. 立刻回 200(否則 LINE 5 秒沒收到會重送)
//   3. 白名單 + 去重 + 觸發等待畫面 + 建 task + enqueue —— 全部在 background
//   4. agent.ts 收 task 跑 Claude,結果 push 給使用者
import { Hono } from 'hono'
import { verifyLineSignature } from './line/signature'
import { reply } from './line/client'
import { startLoading } from './line/loading'
import { createTask } from './tasks'
import { enqueue } from './agent'
import { env } from './env'
import type { LineEvent, LineWebhookBody } from './types'

export const webhookApp = new Hono()

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

  // 白名單:非管理員不建 task;有 replyToken 就回一句、沒有就靜音
  if (admins.size > 0 && !admins.has(userId)) {
    if (ev.replyToken) await reply(ev.replyToken, '您沒有權限使用這個機器人。')
    return
  }

  // 目前只吃文字訊息;圖片、貼圖之後再擴。
  if (ev.message.type !== 'text' || !ev.message.text) {
    if (ev.replyToken) await reply(ev.replyToken, '目前只支援文字訊息哦。')
    return
  }

  const task = createTask({
    eventId: ev.webhookEventId,
    lineUserId: userId,
    channelId,
    rawMessage: ev.message.text,
  })
  if (!task) return // 重送已被去重

  // 等待畫面:1:1 用 loading animation(不佔額度)、群組退回 reply「收到」
  if (ev.source.type === 'user') {
    await startLoading(channelId, 30)
  } else if (ev.replyToken) {
    await reply(ev.replyToken, '收到,處理中…')
  }

  enqueue(task)
}
