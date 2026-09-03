// 任務生命週期:sqlite 插一列 → 交給 agent 跑 → agent 回填 result/status。
// 這裡不做任何 LINE 或 Claude 相關的事,只是資料層。
import { randomUUID } from 'node:crypto'
import { db, type TaskRow } from './db'

export function createTask(input: {
  eventId: string
  lineUserId: string
  channelId: string
  rawMessage: string
}): TaskRow | null {
  const id = randomUUID()
  const now = Date.now()
  try {
    db
      .prepare(
        `INSERT INTO tasks
           (id, event_id, line_user_id, channel_id, raw_message, status, created_at)
         VALUES (?, ?, ?, ?, ?, 'pending', ?)`,
      )
      .run(id, input.eventId, input.lineUserId, input.channelId, input.rawMessage, now)
    return db.prepare(`SELECT * FROM tasks WHERE id = ?`).get(id) as TaskRow | null
  } catch (err) {
    // event_id 撞 UNIQUE = LINE 重送了同一則 webhook,靜靜跳過
    if (String(err).includes('UNIQUE')) return null
    throw err
  }
}

export function markRunning(id: string): void {
  db.prepare(`UPDATE tasks SET status = 'running' WHERE id = ?`).run(id)
}

export function markDone(id: string, text: string): void {
  db.prepare(
    `UPDATE tasks SET status = 'done', result_text = ?, finished_at = ? WHERE id = ?`,
  ).run(text, Date.now(), id)
}

export function markFailed(id: string, error: string): void {
  db.prepare(
    `UPDATE tasks SET status = 'failed', error_text = ?, finished_at = ? WHERE id = ?`,
  ).run(error, Date.now(), id)
}
