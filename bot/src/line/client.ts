// LINE Messaging API:reply(webhook 收到時、免額度)與 push(背景跑完後、吃額度)。
import { env } from '../env'

const API = 'https://api.line.me/v2/bot'

type TextMessage = { type: 'text'; text: string }

export function textMsg(text: string): TextMessage {
  const body = text.length > 4900 ? text.slice(0, 4900) + '\n…（內容過長，已截斷）' : text
  return { type: 'text', text: body }
}

export async function reply(replyToken: string, text: string): Promise<void> {
  await send(`${API}/message/reply`, { replyToken, messages: [textMsg(text)] })
}

export async function push(to: string, text: string): Promise<void> {
  await send(`${API}/message/push`, { to, messages: [textMsg(text)] })
}

async function send(url: string, payload: unknown): Promise<void> {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}`,
    },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    // 本機測試的 replyToken 是假的,一定會失敗;把原欲送出內容 log 出來才看得到
    console.error('LINE send failed', res.status, await res.text(), JSON.stringify(payload))
  }
}
