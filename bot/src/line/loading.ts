// LINE loading animation:1:1 私聊專用,顯示「打字中…」最長 60 秒,
// 不吃 push 額度、不佔訊息位。群組/多人聊天沒這個 API,呼叫會 400。
import { env } from '../env'

export async function startLoading(chatId: string, seconds = 30): Promise<void> {
  const res = await fetch('https://api.line.me/v2/bot/chat/loading/start', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}`,
    },
    // loadingSeconds 只接受 5 的倍數,範圍 5-60
    body: JSON.stringify({
      chatId,
      loadingSeconds: Math.min(60, Math.max(5, Math.round(seconds / 5) * 5)),
    }),
  })
  if (!res.ok) {
    // 群組 chat 打這個會回 400,不是錯誤,只是不適用 —— 靜靜吞掉
    if (res.status !== 400) console.error('loading start failed', res.status, await res.text())
  }
}
