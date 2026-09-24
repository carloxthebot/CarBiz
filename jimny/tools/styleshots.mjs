// One render per style, for the style cards. Three colour chips cannot tell
// anyone what a style looks like, and the whole point of the step is that you
// choose by looking. Same idea as tools/partshots.mjs, but framed on the
// whole car and always from the same angle so the five are comparable.
//
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/styleshots.mjs [id ...]
//
// Writes model/shots/style-<id>.webp.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'model', 'shots');
const APP = process.env.APP || 'http://127.0.0.1:8899/app.html';
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 600 }, deviceScaleFactor: 1 });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(APP);
await page.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none',
  null, { timeout: 240000 });
await page.evaluate(() => {
  document.querySelectorAll('.panel,.hud,.views,.badge,.credit,#spots').forEach(e => e.style.display = 'none');
  document.querySelector('.app').style.gridTemplateColumns = '1fr 0px';
  dispatchEvent(new Event('resize'));
});

const ids = await page.evaluate(() => [...document.querySelectorAll('[data-style]')].map(e => e.dataset.style));
const want = process.argv.slice(2);
const list = want.length ? ids.filter(i => want.includes(i)) : ids;

let made = 0;
const failed = [];
for (const id of list) {
  // the same three-quarter view every time, so five cards are comparable
  await page.evaluate(async (id) => {
    document.querySelector('[data-s="0"]').click();
    document.querySelector(`[data-style="${id}"]`).click();
    await new Promise(r => setTimeout(r, 900));
    window.__jimny.setOrbit({ az: 0.86, el: 0.15, dist: 8.2, ty: 1.0 });
    await new Promise(r => { let i = 0; const f = () => (++i > 20 ? r() : requestAnimationFrame(f)); f(); });
  }, id);
  const box = await page.evaluate(() => {
    const cv = document.getElementById('cv').getBoundingClientRect();
    const w = Math.round(cv.width * 0.66), h = Math.round(w * 10 / 16);
    return { x: Math.round(cv.left + (cv.width - w) / 2), y: Math.round(cv.top + cv.height * 0.30 - h / 2 + h / 2 - h * 0.08),
      width: w, height: h };
  });
  try {
    fs.writeFileSync(path.join(OUT, `style-${id}.webp`),
      await page.screenshot({ clip: box, type: 'webp', quality: 88, timeout: 120000 }));
    made++;
    process.stderr.write(`\r${made} shots  (${id})            `);
  } catch (e) { failed.push(`${id}: ${e.message.split('\n')[0]}`); }
}
console.error(`\n${made} written, ${failed.length} failed, ${errs.length} page errors`);
if (failed.length) console.error(failed.join('\n'));
if (errs.length) console.error(errs.slice(0, 5));
await browser.close();
