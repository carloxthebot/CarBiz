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
`)

// 上一次跑到一半就掛掉的任務,啟動時全部標成 failed —— 不重跑,因為使用者
// 可能已經看到 loading 動畫消失、自己重打了。寧可漏一則也不要意外重複寫入。
db.prepare(
  `UPDATE tasks SET status = 'failed', error_text = 'server restarted mid-run', finished_at = ?
    WHERE status IN ('pending','running')`,
).run(Date.now())

export { db }
