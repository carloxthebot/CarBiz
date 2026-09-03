// Agent 執行器:承接 webhook 建的任務,spawn `claude -p` 跑,結果 push 回 LINE。
//
// 為什麼這裡不做 LINE reply,只做 push:
//   - webhook handler 已經在幾秒內回過 200 給 LINE(必須,否則 LINE 判失敗重送)
//   - Claude 通常要 20-60 秒,替 reply token 早就過期
//   - 所以最終回覆一律用 push
//
// MAX_CONCURRENT 是為了不跟工作 Claude session 搶 CPU/記憶體,不是為了 rate limit。
import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { env } from './env'
import { markDone, markFailed, markRunning } from './tasks'
import type { TaskRow } from './db'
import { push } from './line/client'

let inflight = 0
const queue: TaskRow[] = []

/** Fire-and-forget 進 queue,不 await —— webhook 已經回 200 給 LINE 了。 */
export function enqueue(task: TaskRow): void {
  queue.push(task)
  pump()
}

function pump(): void {
  while (inflight < env.MAX_CONCURRENT && queue.length > 0) {
    const task = queue.shift()!
    inflight++
    runOne(task).finally(() => {
      inflight--
      pump()
    })
  }
}

async function runOne(task: TaskRow): Promise<void> {
  markRunning(task.id)
  const started = Date.now()
  const short = task.id.slice(0, 8)
  console.log(`[task ${short}] start: ${task.raw_message.slice(0, 60)}`)

  try {
    const text = await runClaude(task)
    markDone(task.id, text)
    console.log(`[task ${short}] done in ${sec(started)}s`)
    await push(task.channel_id, text)
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    markFailed(task.id, msg)
    console.error(`[task ${short}] failed in ${sec(started)}s:`, msg)
    await push(task.channel_id, `處理失敗:${msg.slice(0, 200)}`).catch((e) =>
      console.error(`[task ${short}] push-failed also failed:`, e),
    )
  }
}

async function runClaude(task: TaskRow): Promise<string> {
  const prompt = await readFile(resolve(env.REPO_ROOT, 'worker/prompts/agent.md'), 'utf8')
  const sheetsMap = await readFile(
    resolve(env.REPO_ROOT, 'worker/state/sheets-map.json'),
    'utf8',
  ).catch(() => '{"note":"sheets_map.py not yet run — worker should list folder"}')

  const stdinPayload = JSON.stringify({
    task_id: task.id,
    raw_message: task.raw_message,
    line_user_id: task.line_user_id,
    image_ids: [], // MVP:不處理圖片
    sheets_map: JSON.parse(sheetsMap),
  })

  const child = spawn(
    env.CLAUDE_BIN,
    ['-p', prompt, '--output-format', 'json', '--dangerously-skip-permissions'],
    {
      cwd: env.REPO_ROOT,
      env: {
        ...process.env,
        CLAUDE_CONFIG_DIR: env.CLAUDE_CONFIG_DIR,
        SHEETS_SERVICE_ACCOUNT_JSON: env.SHEETS_SERVICE_ACCOUNT_JSON,
        SHEETS_FOLDER_ID: env.SHEETS_FOLDER_ID,
      },
      stdio: ['pipe', 'pipe', 'pipe'],
    },
  )

  const stdoutChunks: Buffer[] = []
  const stderrChunks: Buffer[] = []
  child.stdout.on('data', (c) => stdoutChunks.push(c))
  child.stderr.on('data', (c) => stderrChunks.push(c))
  child.stdin.end(stdinPayload)

  const timer = setTimeout(() => child.kill('SIGKILL'), env.CLAUDE_TIMEOUT_MS)
  const code: number = await new Promise((r) => child.on('exit', (c) => r(c ?? -1)))
  clearTimeout(timer)

  const stdout = Buffer.concat(stdoutChunks).toString('utf8').trim()
  const stderr = Buffer.concat(stderrChunks).toString('utf8').trim()

  if (code !== 0) {
    throw new Error(stderr || stdout || `claude exit ${code}`)
  }

  // `--output-format json` 印一段 JSON,通常有 result 欄。parse 失敗就當純文字。
  const parsed = safeJson(stdout)
  const body =
    (parsed && (parsed.result ?? parsed.output ?? parsed.text)) ?? stdout
  if (!body) throw new Error('claude returned empty output')
  return String(body)
}

function safeJson(s: string): { result?: unknown; output?: unknown; text?: unknown } | null {
  try {
    return JSON.parse(s)
  } catch {
    return null
  }
}

function sec(fromMs: number): string {
  return ((Date.now() - fromMs) / 1000).toFixed(1)
}
