// 每個 LINE channel 對應一段 Claude Code session,讓多輪對話有前文記憶。
// channel_id 是 push 目的地 (group/room/user id) —— 對「同一個聊天」用同一
// 段 session,群裡任何人接話都看得到前文,自然。
import { db } from './db'

export type SessionRow = {
  channel_id: string
  session_id: string
  context_tokens: number
  context_window: number
  needs_compact: number // 0 | 1
  updated_at: number
}

export function getSession(channelId: string): SessionRow | null {
  return (
    (db.prepare(`SELECT * FROM sessions WHERE channel_id = ?`).get(channelId) as SessionRow | undefined) ??
    null
  )
}

export function saveSession(
  channelId: string,
  input: {
    sessionId: string
    contextTokens: number
    contextWindow: number
    needsCompact: boolean
  },
): void {
  db.prepare(
    `INSERT INTO sessions (channel_id, session_id, context_tokens, context_window, needs_compact, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(channel_id) DO UPDATE SET
       session_id     = excluded.session_id,
       context_tokens = excluded.context_tokens,
       context_window = excluded.context_window,
       needs_compact  = excluded.needs_compact,
       updated_at     = excluded.updated_at`,
  ).run(
    channelId,
    input.sessionId,
    input.contextTokens,
    input.contextWindow,
    input.needsCompact ? 1 : 0,
    Date.now(),
  )
}

export function evictSession(channelId: string): void {
  db.prepare(`DELETE FROM sessions WHERE channel_id = ?`).run(channelId)
}
