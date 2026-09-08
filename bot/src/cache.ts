// 定期重抓 sheet 快取。sheets_map.py 把最新那本帳的每個 tab 倒進
// worker/state/data/,Claude 讀本機檔而不是打 Google —— 這是回答從
// 60–180 秒降到 20–40 秒、也不再撞讀取配額的關鍵。
//
// 寫入(append/update/undo)由 sheets.py 自己刷對應 tab,這裡的定時只是
// 接住「有人直接在 Google Sheets 裡改」的情況。
import { spawn } from 'node:child_process'
import { resolve } from 'node:path'
import { env } from './env'
import { pruneInbox } from './images'

let running = false

export function refreshSheetsCache(reason: string): Promise<void> {
  if (running) return Promise.resolve()
  running = true
  const started = Date.now()
  return new Promise((done) => {
    const child = spawn('python3', ['worker/tools/sheets_map.py'], {
      cwd: env.REPO_ROOT,
      env: {
        ...process.env,
        PATH: env.WORKER_VENV_BIN ? `${env.WORKER_VENV_BIN}:${process.env.PATH ?? ''}` : process.env.PATH,
        SHEETS_SERVICE_ACCOUNT_JSON: env.SHEETS_SERVICE_ACCOUNT_JSON,
        SHEETS_FOLDER_ID: env.SHEETS_FOLDER_ID,
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let out = ''
    child.stdout.on('data', (c) => (out += c))
    child.stderr.on('data', (c) => (out += c))
    child.on('exit', (code) => {
      running = false
      const secs = ((Date.now() - started) / 1000).toFixed(1)
      if (code === 0) console.log(`[cache] refreshed (${reason}) in ${secs}s — ${out.trim().split('\n').pop()}`)
      else console.error(`[cache] refresh failed (${reason}) code=${code}: ${out.trim().slice(-300)}`)
      done()
    })
  })
}

export function startCacheRefresher(): void {
  void refreshSheetsCache('boot')
  if (env.SHEETS_REFRESH_MIN > 0) {
    setInterval(() => void refreshSheetsCache('interval'), env.SHEETS_REFRESH_MIN * 60_000).unref()
  }
  // 圖片 inbox 每天清一次 7 天以上的
  const prune = () => void pruneInbox().then((n) => n && console.log(`[inbox] pruned ${n} old images`))
  prune()
  setInterval(prune, 86_400_000).unref()
}

export const cacheDir = resolve(env.REPO_ROOT, 'worker/state')
