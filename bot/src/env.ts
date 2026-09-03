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

  CLAUDE_CONFIG_DIR: required('CLAUDE_CONFIG_DIR'),
  CLAUDE_BIN: optional('CLAUDE_BIN', 'claude'),
  CLAUDE_TIMEOUT_MS: Number(optional('CLAUDE_TIMEOUT_MS', String(8 * 60 * 1000))),
  MAX_CONCURRENT: Number(optional('MAX_CONCURRENT', '2')),

  REPO_ROOT: optional('REPO_ROOT', new URL('../../', import.meta.url).pathname),
  SHEETS_SERVICE_ACCOUNT_JSON: required('SHEETS_SERVICE_ACCOUNT_JSON'),
  SHEETS_FOLDER_ID: required('SHEETS_FOLDER_ID'),
} as const

export type Env = typeof env
