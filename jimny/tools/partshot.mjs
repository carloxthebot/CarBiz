// Close-ups of one accessory from the angles a reference photo was taken at,
// for checking a rebuilt part against the real thing.
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/partshot.mjs
import { chromium } from 'playwright-core';
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
await page.goto(process.env.APP || 'http://127.0.0.1:8899/app.html');
await page.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none', null, { timeout: 180000 });
await page.evaluate(() => { document.querySelectorAll('.panel,.hud,.views,.badge,.credit').forEach(e => e.style.display = 'none'); });
await page.setViewportSize({ width: 1000, height: 1000 });
await page.waitForTimeout(400);
console.log(await page.evaluate(() => {
  const J = window.__jimny; J.S.snorkel = 'tw_cowl'; J.update();
  let found = null;
  J.rig.traverse(o => { if (/snorkel/i.test(o.name)) found = o; });
  if (!found) return 'no snorkel node';
  const b = new J.THREE.Box3().setFromObject(found);
  const mm = (v) => [v.x, v.y, v.z].map(n => Math.round(n * 1000)).join(' ');
  return `${found.name}  min ${mm(b.min)}  max ${mm(b.max)}`;
}));
const spin = () => page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n > 20 ? r() : requestAnimationFrame(f)); f(); }));
const OUT = '/private/tmp/claude-501/-Users-carlox-Personal/bae455ed-b844-4d8b-bf32-ff71834ff136/scratchpad';
const AIM = [-0.62, 1.34, 0.44];
const shots = [
  ['side', [-3.1, 1.46, 0.42]],     // straight at the flank
  ['q34', [-2.1, 1.52, 1.9]],        // front three-quarter, like the green car photo
  ['front', [-1.4, 1.66, 2.4]],
];
for (const [name, pos] of shots) {
  await page.evaluate(([pos, aim]) => {
    const { cam } = window.__jimny;
    window.__lockcam = () => { cam.position.set(...pos); cam.lookAt(...aim); };
    window.__lockcam();
  }, [pos, AIM]);
  await page.evaluate(() => new Promise(r => { let n = 0; const f = () => { window.__lockcam(); (++n > 20 ? r() : requestAnimationFrame(f)); }; f(); }));
  await page.screenshot({ path: `${OUT}/snork_${name}.png` });
}
await browser.close();
