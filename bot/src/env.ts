// 一次讀完環境變數,程式其他地方就拿 typed 的 env 用,不再摸 process.env。
import 'dotenv/config'

function required(name: string): string {
  const v = process.env[name]
  if (!v) throw new Error(`${name} is required (check bot/.env)`)
  return v
}

function optional(name: string, fallback: string): string {
  return process.env[name] ?? fallback
}

export const env = {
  PORT: Number(optional('PORT', '8787')),
  DB_PATH: optional('DB_PATH', './carbiz.sqlite'),

  LINE_CHANNEL_SECRET: required('LINE_CHANNEL_SECRET'),
  LINE_CHANNEL_ACCESS_TOKEN: required('LINE_CHANNEL_ACCESS_TOKEN'),
  ADMIN_LINE_USER_IDS: optional('ADMIN_LINE_USER_IDS', ''),
  // 群組裡除了真 @mention,訊息開頭打這些字(可加 @)也算叫 bot。逗號分隔。
  // LINE 手打 @xxx 沒從清單點選是不會帶 mention 欄位的,這是保險。
  BOT_ALIASES: optional('BOT_ALIASES', '瑞斯,RaysRevo'),

  CLAUDE_CONFIG_DIR: required('CLAUDE_CONFIG_DIR'),
  CLAUDE_BIN: optional('CLAUDE_BIN', 'claude'),
  // 留空 = 帳號預設(目前 Opus)。填 sonnet / opus / 完整 model id 會帶 --model。
  CLAUDE_MODEL: optional('CLAUDE_MODEL', ''),
  // 本機 sheet 快取多久重抓一次(分鐘)。0 = 只在啟動時抓。
  SHEETS_REFRESH_MIN: Number(optional('SHEETS_REFRESH_MIN', '10')),
  // 每日早報:推到哪些 channel(群組 id / userId,逗號分隔)、幾點(本機時間;-1 關閉)
  DIGEST_CHANNEL_IDS: optional('DIGEST_CHANNEL_IDS', '').split(',').map((s) => s.trim()).filter(Boolean),
  DIGEST_HOUR: Number(optional('DIGEST_HOUR', '8')),
  CLAUDE_TIMEOUT_MS: Number(optional('CLAUDE_TIMEOUT_MS', String(8 * 60 * 1000))),
  MAX_CONCURRENT: Number(optional('MAX_CONCURRENT', '2')),

  REPO_ROOT: optional('REPO_ROOT', new URL('../../', import.meta.url).pathname),
  SHEETS_SERVICE_ACCOUNT_JSON: required('SHEETS_SERVICE_ACCOUNT_JSON'),
  SHEETS_FOLDER_ID: required('SHEETS_FOLDER_ID'),
  // 選填:worker 的 Python venv bin 路徑,會被 prepend 到 spawn claude 的 PATH,
  // 讓 sheets.py 用得到 venv 裡的 gspread。留空就假設 python3 已能 import gspread。
  WORKER_VENV_BIN: optional('WORKER_VENV_BIN', ''),
} as const

export type Env = typeof env
