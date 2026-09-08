// SQLite backing store, using Node 22.5+ 內建的 node:sqlite —— 零編譯、零依賴。
//
// 為什麼還要 DB:
//   - webhook 回 200 之後 Claude 在背景跑,結果 push 之前程序若被砍,
//     重新啟動可以看到 status=running 的任務、決定要標成 failed 或重試
//   - event_id UNIQUE 是 LINE 重送去重的核心防線
//   - 之後要看歷史(誰下了什麼、跑多久、對了沒)有一份可撈
import { DatabaseSync } from 'node:sqlite'
import { env } from './env'

export type TaskRow = {
  id: string
  event_id: string
  line_user_id: string
  channel_id: string
  raw_message: string
  image_paths: string | null // JSON array of absolute paths under worker/state/inbox
  status: 'pending' | 'running' | 'done' | 'failed'
  result_text: string | null
  error_text: string | null
  created_at: number
  finished_at: number | null
}

const db = new DatabaseSync(env.DB_PATH)
db.exec(`PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL;`)

// 一支 process 自己管 schema。要改欄位就多加一條 migration,別動舊的。
db.exec(`
  CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    event_id      TEXT NOT NULL UNIQUE,
    line_user_id  TEXT NOT NULL,
    channel_id    TEXT NOT NULL,
    raw_message   TEXT NOT NULL,
    status        TEXT NOT NULL,
    result_text   TEXT,
    error_text    TEXT,
    created_at    INTEGER NOT NULL,
    finished_at   INTEGER
  );
  CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at);

  -- 每個 LINE channel(1:1 = userId、group = groupId、room = roomId)
  -- 對應一個 Claude Code session。resume 讓連續問答有前文記憶。
  -- context_tokens 是上一輪結束後的 session 累積大小,超過 80% 上限
  -- 就在下一輪先跑 /compact。
  CREATE TABLE IF NOT EXISTS sessions (
    channel_id      TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    context_tokens  INTEGER NOT NULL DEFAULT 0,
    context_window  INTEGER NOT NULL DEFAULT 200000,
    needs_compact   INTEGER NOT NULL DEFAULT 0,
    updated_at      INTEGER NOT NULL
  );
`)

// migration 0002:圖片路徑(JSON array)。sqlite 沒有 ADD COLUMN IF NOT EXISTS,先查。
{
  const cols = (db.prepare(`PRAGMA table_info(tasks)`).all() as { name: string }[]).map((c) => c.name)
  if (!cols.includes('image_paths')) db.exec(`ALTER TABLE tasks ADD COLUMN image_paths TEXT`)
}

// 上一次跑到一半就掛掉的任務,啟動時全部標成 failed —— 不重跑,因為使用者
// 可能已經看到 loading 動畫消失、自己重打了。寧可漏一則也不要意外重複寫入。
// 拿到的 channel_id 交給 server.ts 開機時 push 一句道歉,不然使用者無感失蹤。
const orphans = db.prepare(
  `SELECT id, channel_id, raw_message FROM tasks WHERE status IN ('pending','running')`,
).all() as { id: string; channel_id: string; raw_message: string }[]
db.prepare(
  `UPDATE tasks SET status = 'failed', error_text = 'server restarted mid-run', finished_at = ?
    WHERE status IN ('pending','running')`,
).run(Date.now())
export const orphanedOnBoot = orphans

export { db }
