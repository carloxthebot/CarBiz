// Agent 執行器:承接 webhook 建的任務,spawn `claude -p` 跑,結果 push 回 LINE。
//
// 多輪對話:每個 LINE channel 綁一段 Claude session。每輪拿回新 session_id
// 存回,下輪 `--resume` 續。這樣「上個月訂單」→「那哪一筆最大?」自然接。
//
// Context 上限:偵測 `cache_read + input + creation + output` 累積超過模型
// contextWindow 的 80% → 標 needs_compact。下輪先跑 `/compact` 再跑真的問題
// (該輪多 5-15 秒)。/compact 失敗就 evict session,新開一段。
//
// Per-channel serialization:同一個 channel 的問題排隊,避免 session_id 撞。
// 全域仍受 MAX_CONCURRENT 限制以免搶 CPU。
import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { env } from './env'
import { markDone, markFailed, markRunning } from './tasks'
import { push } from './line/client'
import { evictSession, getSession, saveSession, type SessionRow } from './sessions'
import type { TaskRow } from './db'

const COMPACT_THRESHOLD = 0.8

let inflight = 0
const globalQueue: TaskRow[] = []
const channelQueues = new Map<string, TaskRow[]>() // per-channel FIFO
const channelBusy = new Set<string>()

export function enqueue(task: TaskRow): void {
  globalQueue.push(task)
  pump()
}

function pump(): void {
  while (inflight < env.MAX_CONCURRENT && globalQueue.length > 0) {
    // 找一個沒在跑的 channel 的任務;有的話送出去
    const nextIdx = globalQueue.findIndex((t) => !channelBusy.has(t.channel_id))
    if (nextIdx === -1) return // 目前全域待跑的任務,所在 channel 都各自在跑,等
    const task = globalQueue.splice(nextIdx, 1)[0]
    channelBusy.add(task.channel_id)
    inflight++
    runOne(task).finally(() => {
      inflight--
      channelBusy.delete(task.channel_id)
      pump()
    })
  }
}

async function runOne(task: TaskRow): Promise<void> {
  markRunning(task.id)
  const started = Date.now()
  const short = task.id.slice(0, 8)
  console.log(`[task ${short}] start (channel=${task.channel_id.slice(0, 8)}): ${task.raw_message.slice(0, 60)}`)

  try {
    let session = getSession(task.channel_id)

    // 上一輪標記要 compact —— 這輪先壓一次 /compact 再問問題
    if (session && session.needs_compact) {
      console.log(`[task ${short}] compacting session before turn`)
      try {
        const compacted = await runClaude({ resumeId: session.session_id, prompt: '/compact' })
        saveSession(task.channel_id, {
          sessionId: compacted.sessionId,
          contextTokens: compacted.contextTokens,
          contextWindow: compacted.contextWindow,
          needsCompact: false,
        })
        session = getSession(task.channel_id) // reload
      } catch (err) {
        console.warn(`[task ${short}] /compact failed, evicting:`, err)
        evictSession(task.channel_id)
        session = null
      }
    }

    const result = await runClaude({
      resumeId: session?.session_id ?? null,
      prompt: await loadAgentPrompt(),
      stdin: await buildStdinPayload(task),
    })

    const overThreshold = result.contextWindow > 0
      && result.contextTokens / result.contextWindow >= COMPACT_THRESHOLD
    saveSession(task.channel_id, {
      sessionId: result.sessionId,
      contextTokens: result.contextTokens,
      contextWindow: result.contextWindow,
      needsCompact: overThreshold,
    })
    if (overThreshold) {
      const pct = ((result.contextTokens / result.contextWindow) * 100).toFixed(1)
      console.log(`[task ${short}] context ${pct}% — will compact next turn`)
    }

    markDone(task.id, result.text)
    console.log(`[task ${short}] done in ${sec(started)}s (ctx=${result.contextTokens}/${result.contextWindow})`)
    await push(task.channel_id, result.text)
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    markFailed(task.id, msg)
    console.error(`[task ${short}] failed in ${sec(started)}s:`, msg)
    // resume 失敗最常見 = session 過期。掉了 session 讓下輪重來
    if (/session|resume/i.test(msg)) evictSession(task.channel_id)
    await push(task.channel_id, `處理失敗:${msg.slice(0, 200)}`).catch((e) =>
      console.error(`[task ${short}] push-failed also failed:`, e),
    )
  }
}

async function loadAgentPrompt(): Promise<string> {
  return readFile(resolve(env.REPO_ROOT, 'worker/prompts/agent.md'), 'utf8')
}

async function buildStdinPayload(task: TaskRow): Promise<string> {
  const sheetsMap = await readFile(
    resolve(env.REPO_ROOT, 'worker/state/sheets-map.json'),
    'utf8',
  ).catch(() => '{"note":"sheets_map.py not yet run — worker should list folder"}')
  return JSON.stringify({
    task_id: task.id,
    raw_message: task.raw_message,
    line_user_id: task.line_user_id,
    image_paths: task.image_paths ? (JSON.parse(task.image_paths) as string[]) : [],
    sheets_map: JSON.parse(sheetsMap),
  })
}

type RunResult = {
  text: string
  sessionId: string
  contextTokens: number
  contextWindow: number
}

async function runClaude(opts: {
  prompt: string
  stdin?: string
  resumeId?: string | null
}): Promise<RunResult> {
  const args = [
    '-p', opts.prompt,
    '--output-format', 'json',
    '--dangerously-skip-permissions',
  ]
  if (env.CLAUDE_MODEL) args.push('--model', env.CLAUDE_MODEL)
  if (opts.resumeId) args.push('--resume', opts.resumeId)

  const child = spawn(env.CLAUDE_BIN, args, {
    cwd: env.REPO_ROOT,
    env: {
      ...process.env,
      PATH: env.WORKER_VENV_BIN
        ? `${env.WORKER_VENV_BIN}:${process.env.PATH ?? ''}`
        : process.env.PATH,
      CLAUDE_CONFIG_DIR: env.CLAUDE_CONFIG_DIR,
      SHEETS_SERVICE_ACCOUNT_JSON: env.SHEETS_SERVICE_ACCOUNT_JSON,
      SHEETS_FOLDER_ID: env.SHEETS_FOLDER_ID,
    },
    stdio: ['pipe', 'pipe', 'pipe'],
  })

  const stdoutChunks: Buffer[] = []
  const stderrChunks: Buffer[] = []
  child.stdout.on('data', (c) => stdoutChunks.push(c))
  child.stderr.on('data', (c) => stderrChunks.push(c))
  if (opts.stdin !== undefined) child.stdin.end(opts.stdin)
  else child.stdin.end()

  const timer = setTimeout(() => child.kill('SIGKILL'), env.CLAUDE_TIMEOUT_MS)
  const code: number = await new Promise((r) => child.on('exit', (c) => r(c ?? -1)))
  clearTimeout(timer)

  const stdout = Buffer.concat(stdoutChunks).toString('utf8').trim()
  const stderr = Buffer.concat(stderrChunks).toString('utf8').trim()

  if (code !== 0) {
    throw new Error(stderr || stdout || `claude exit ${code}`)
  }

  const parsed = safeJson(stdout)
  if (!parsed) throw new Error(`unparseable claude output: ${stdout.slice(0, 200)}`)

  const text = String(parsed.result ?? parsed.output ?? parsed.text ?? '').trim()
  if (!text) throw new Error(`claude returned empty output; is_error=${parsed.is_error}`)

  const sessionId = String(parsed.session_id ?? '')
  if (!sessionId) throw new Error('claude output missing session_id')

  // 累積這輪 session 大概吃了多少 context tokens。cache_read 是 resume 時
  // Claude 從前文讀了多少、input/creation/output 是這輪新增。加起來就是
  // 「這輪跑完後 session 大概有多大」。
  const usage = parsed.usage ?? {}
  const contextTokens =
    (usage.cache_read_input_tokens ?? 0) +
    (usage.cache_creation_input_tokens ?? 0) +
    (usage.input_tokens ?? 0) +
    (usage.output_tokens ?? 0)

  // 上限從 modelUsage 抓:一輪可能用到多個 model(主模型 + subagent),取最大的。
  // 全都沒報就看 model 名有沒有 [1m],沒有才退回 200k。之前直接拿第一個 + 200k
  // fallback,群組那段 session 一輪就被誤標成要 compact。
  const modelUsage = (parsed.modelUsage ?? {}) as Record<string, { contextWindow?: number }>
  let contextWindow = 0
  for (const [name, u] of Object.entries(modelUsage)) {
    const w = Number(u?.contextWindow ?? 0) || (name.includes('[1m]') ? 1_000_000 : 0)
    if (w > contextWindow) contextWindow = w
  }
  if (!contextWindow) contextWindow = 200_000

  return { text, sessionId, contextTokens, contextWindow }
}

function safeJson(s: string): Record<string, any> | null {
  try {
    return JSON.parse(s)
  } catch {
    return null
  }
}

function sec(fromMs: number): string {
  return ((Date.now() - fromMs) / 1000).toFixed(1)
}
