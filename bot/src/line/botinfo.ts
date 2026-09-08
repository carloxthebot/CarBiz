// Bot 自己的 LINE userId,拿來判斷群組訊息有沒有 @ 到自己。
// 用 /v2/bot/info 抓一次快取住,不用寫進 .env(少一個要維護的值)。
import { env } from '../env'

let cached: string | null = null
let inflight: Promise<string> | null = null

export async function getBotUserId(): Promise<string> {
  if (cached) return cached
  if (inflight) return inflight
  inflight = (async () => {
    const res = await fetch('https://api.line.me/v2/bot/info', {
      headers: { authorization: `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}` },
    })
    if (!res.ok) throw new Error(`GET /bot/info failed: ${res.status} ${await res.text()}`)
    const data = (await res.json()) as { userId: string; displayName?: string }
    if (!data.userId) throw new Error(`/bot/info response missing userId`)
    cached = data.userId
    console.log(`[bot info] userId=${data.userId} name=${data.displayName ?? '?'}`)
    return data.userId
  })()
  try {
    return await inflight
  } finally {
    inflight = null
  }
}
