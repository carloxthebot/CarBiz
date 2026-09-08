// 每日早報:跑 worker/tools/digest.py(純快取計算,不經 Claude),push 到指定
// channel。每天 DIGEST_HOUR:00 本機時間一次;群裡打「早報」也會立刻跑一次。
import { spawn } from 'node:child_process'
import { env } from './env'
import { push } from './line/client'

export function runDigest(): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn('python3', ['worker/tools/digest.py'], {
      cwd: env.REPO_ROOT,
      env: { ...process.env, PATH: env.WORKER_VENV_BIN ? `${env.WORKER_VENV_BIN}:${process.env.PATH ?? ''}` : process.env.PATH },
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let out = '', err = ''
    child.stdout.on('data', (c) => (out += c))
    child.stderr.on('data', (c) => (err += c))
    child.on('exit', (code) => (code === 0 && out.trim() ? resolve(out.trim()) : reject(new Error(err.trim() || `digest exit ${code}`))))
  })
}

export async function pushDigest(reason: string, channels = env.DIGEST_CHANNEL_IDS): Promise<void> {
  if (!channels.length) { console.log(`[digest] no DIGEST_CHANNEL_IDS, skipping (${reason})`); return }
  try {
    const text = await runDigest()
    for (const ch of channels) await push(ch, text)
    console.log(`[digest] pushed (${reason}) to ${channels.length} channel(s)`)
  } catch (e) {
    console.error(`[digest] failed (${reason}):`, e)
  }
}

export function startDigestScheduler(): void {
  if (env.DIGEST_HOUR < 0 || !env.DIGEST_CHANNEL_IDS.length) { console.log('[digest] scheduler off'); return }
  let lastFired = ''
  const tick = () => {
    const now = new Date()
    const key = now.toDateString()
    if (now.getHours() === env.DIGEST_HOUR && now.getMinutes() < 5 && lastFired !== key) {
      lastFired = key
      void pushDigest('scheduled')
    }
  }
  setInterval(tick, 60_000).unref()
  console.log(`[digest] scheduled daily at ${String(env.DIGEST_HOUR).padStart(2, '0')}:00 → ${env.DIGEST_CHANNEL_IDS.length} channel(s)`)
}
