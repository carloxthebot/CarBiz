// Renders one face-on PNG per rim style into model/wheels/, so the configurator
// can show what a wheel actually looks like instead of describing it in words.
// Run after any change to the rim geometry in blender/build_parts.py:
//
//   node tools/render_wheels.mjs
//
// The thumbnails come from the same parts.glb the page loads, so they can never
// drift from the 3D model the way a hand-drawn icon would.
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'model', 'wheels');

// Every `style` any WHEELS entry in parts.js can ask for.
const STYLES = ['stock', 'steel', 'eight', 'six', 'ten', 'slot5', 'eightpin', 'daytona',
  'moon', 'watanabe', 'renkon', 'arc4', 'dwindow', 'turbine', 'beadlock', 'seven'];

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.glb': 'model/gltf-binary', '.png': 'image/png', '.webp': 'image/webp', '.json': 'application/json', '.hdr': 'image/vnd.radiance' };

const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404).end(); return; }
  res.writeHead(200, { 'content-type': TYPES[path.extname(p)] ?? 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 500, height: 500 } });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(`${base}/tools/wheelshot.html`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });

fs.mkdirSync(OUT, { recursive: true });
for (const style of STYLES) {
  const url = await page.evaluate(s => window.__shot(s), style);
  const buf = Buffer.from(url.split(',')[1], 'base64');
  fs.writeFileSync(path.join(OUT, `${style}.webp`), buf);
  console.log(`${style}.webp  ${(buf.length / 1024).toFixed(1)} KB`);
}
if (errs.length) console.error('PAGE ERRORS: ' + errs.join(' | '));
await browser.close();
server.close();
console.log(errs.length ? 'FAIL' : `ok — ${STYLES.length} thumbnails in model/wheels/`);
process.exit(errs.length ? 1 : 0);
