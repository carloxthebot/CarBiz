// Node 入口。啟一支 Hono HTTP server,LINE webhook 掛在 /api/line/webhook。
// cloudflared 從外面把 tunnel 轉進這個 port。
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { env } from './env'
import { webhookApp } from './webhook'

const app = new Hono().basePath('/api')

app.get('/health', (c) => c.json({ ok: true }))
app.route('/line', webhookApp)

serve({ fetch: app.fetch, port: env.PORT, hostname: '127.0.0.1' }, (info) => {
  console.log(`[carbiz-bot] listening on http://127.0.0.1:${info.port}`)
  console.log(`[carbiz-bot] LINE webhook path: /api/line/webhook`)
})
