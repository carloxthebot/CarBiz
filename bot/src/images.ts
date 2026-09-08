// 圖片訊息的落地與配對。
//
// 1:1:一張圖就是一個任務,Claude 直接看。
// 群組:圖片訊息沒辦法 @ 人,bot 不知道是不是給它的。先存起來,等同一個人
//       在 5 分鐘內打一句叫到 bot 的文字,再把圖一起帶進那個任務。
//
// 圖檔放 worker/state/inbox/<messageId>.jpg,Claude 用 Read 直接看(多模態),
// 不用 OCR。7 天以上的由 cache refresher 順手清掉。
import { mkdir, readdir, stat, unlink, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { env } from './env'
import { fetchContent } from './line/client'

export const INBOX_DIR = resolve(env.REPO_ROOT, 'worker/state/inbox')
const PENDING_TTL_MS = 5 * 60_000
const PENDING_MAX = 5

type Pending = { path: string; at: number }
const pending = new Map<string, Pending[]>() // `${channelId}:${userId}` → images

export async function saveImage(messageId: string): Promise<string> {
  await mkdir(INBOX_DIR, { recursive: true })
  const buf = await fetchContent(messageId)
  const path = resolve(INBOX_DIR, `${messageId}.jpg`)
  await writeFile(path, buf)
  return path
}

export function stashImage(channelId: string, userId: string, path: string): void {
  const key = `${channelId}:${userId}`
  const list = (pending.get(key) ?? []).filter((p) => Date.now() - p.at < PENDING_TTL_MS)
  list.push({ path, at: Date.now() })
  pending.set(key, list.slice(-PENDING_MAX))
}

/** 取出並清空這個人在這個 channel 最近 5 分鐘丟的圖。 */
export function takePendingImages(channelId: string, userId: string): string[] {
  const key = `${channelId}:${userId}`
  const list = (pending.get(key) ?? []).filter((p) => Date.now() - p.at < PENDING_TTL_MS)
  pending.delete(key)
  return list.map((p) => p.path)
}

export async function pruneInbox(maxAgeDays = 7): Promise<number> {
  let removed = 0
  try {
    const cutoff = Date.now() - maxAgeDays * 86_400_000
    for (const name of await readdir(INBOX_DIR)) {
      const p = resolve(INBOX_DIR, name)
      if ((await stat(p)).mtimeMs < cutoff) { await unlink(p); removed++ }
    }
  } catch { /* inbox 不存在就算了 */ }
  return removed
}
