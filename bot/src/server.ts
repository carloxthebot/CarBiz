// Node 入口。啟一支 Hono HTTP server,LINE webhook 掛在 /api/line/webhook。
// cloudflared 從外面把 tunnel 轉進這個 port。
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { env } from './env'
import { webhookApp } from './webhook'
import { orphanedOnBoot } from './db'
import { push } from './line/client'
import { startCacheRefresher } from './cache'
import { startDigestScheduler } from './digest'

startCacheRefresher()
startDigestScheduler()

const app = new Hono().basePath('/api')

app.get('/health', (c) => c.json({ ok: true }))
app.route('/line', webhookApp)

serve({ fetch: app.fetch, port: env.PORT, hostname: '127.0.0.1' }, (info) => {
  console.log(`[carbiz-bot] listening on http://127.0.0.1:${info.port}`)
  console.log(`[carbiz-bot] LINE webhook path: /api/line/webhook`)
})

// 上次跑到一半就掛掉的任務(通常是重啟導致的),補一句道歉給使用者,免得
// 他們以為 bot 卡住。每 channel 只推一則(合併),不逐 task 洗版。
if (orphanedOnBoot.length > 0) {
  const byChannel = new Map<string, number>()
  for (const t of orphanedOnBoot) {
    byChannel.set(t.channel_id, (byChannel.get(t.channel_id) ?? 0) + 1)
  }
  console.log(`[boot] ${orphanedOnBoot.length} orphaned tasks across ${byChannel.size} channels — pushing apology`)
  for (const [channelId, count] of byChannel) {
    const msg = count === 1
      ? '不好意思,剛才的問題因為 bot 重啟沒答完,請重問一次。'
      : `不好意思,剛才有 ${count} 則問題因為 bot 重啟沒答完,請重問。`
    push(channelId, msg).catch((err) => console.error('boot apology push failed', channelId, err))
  }
}
