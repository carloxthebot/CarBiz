// Render one fitted shot per catalogue part, straight off the configurator, so
// the hover card can SHOW the part on the car instead of describing it. These
// are our own renders of our own model -- the makers' product photos are their
// copyright and this repo is public.
//
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/partshots.mjs [family ...]
//
// Writes model/shots/<key>-<id>.webp. Re-run after changing a part's geometry.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'model', 'shots');
const APP = process.env.APP || 'http://127.0.0.1:8899/app.html';
fs.mkdirSync(OUT, { recursive: true });

// family -> the parts.js array it reads. Matches SPOT_LIST in app.html.
const FAMILIES = ['frontBumper', 'grille', 'rearBumper', 'hood', 'spareCoverKit', 'mirrors',
  'roofRack', 'awning', 'sideStep', 'ladder', 'snorkel', 'exhaust',
  'lightBar', 'roofLights', 'grilleLight', 'extinguisher'];
const want = process.argv.slice(2);
const families = want.length ? FAMILIES.filter(f => want.includes(f)) : FAMILIES;

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 880, height: 600 }, deviceScaleFactor: 1 });
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
const spin = (n = 6) => page.evaluate((n) =>
  new Promise(r => { let i = 0; const f = () => (++i > n ? r() : requestAnimationFrame(f)); f(); }), n);

const items = await page.evaluate((fams) => Object.fromEntries(fams.map((k) => {
  const L = window.__jimnyLists?.[k] ?? null;
  return [k, L ? L.map((x) => x.id) : []];
})), families);

let made = 0, skipped = 0;
const failed = [];
for (const key of families) {
  for (const id of items[key] || []) {
    if (id === 'none' || id === 'stock') { skipped++; continue; }
    const file = path.join(OUT, `${key}-${id}.webp`);
    // resumable: a run that dies part way through does not redo the rest
    if (!process.env.FORCE && fs.existsSync(file)) { skipped++; continue; }
    const box = await page.evaluate(async ([key, id]) => {
      const J = window.__jimny;
      J.S[key] = id;
      J.update();
      const aim = window.__jimnyAim(key);
      if (aim) J.setOrbit({ az: aim[0], el: aim[1], dist: aim[2] * 0.72 });
      await new Promise(r => { let i = 0; const f = () => (++i > 7 ? r() : requestAnimationFrame(f)); f(); });
      return window.__jimnyShotBox(key);
    }, [key, id]);
    if (!box) { skipped++; continue; }
    await spin(3);
    try {
      const buf = await page.screenshot({ clip: box, type: 'webp', quality: 86, timeout: 120000 });
      fs.writeFileSync(file, buf);
    } catch (e) { failed.push(`${key}/${id}: ${e.message.split('\n')[0]}`); continue; }
    made++;
    process.stderr.write(`\r${made} shots  (${key}/${id})            `);
  }
  await page.evaluate((k) => { window.__jimny.S[k] = window.__jimnyDefault(k); window.__jimny.update(); }, key);
}
console.error(`\n${made} written, ${skipped} skipped, ${failed.length} failed, ${errs.length} page errors`);
if (failed.length) console.error(failed.slice(0, 8).join('\n'));
if (errs.length) console.error(errs.slice(0, 5));
await browser.close();
