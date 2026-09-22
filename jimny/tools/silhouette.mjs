// Trace the car's own side profile out of the 3D model, so the loading screen
// draws THIS car instead of a generic one. Writes two masks plus the wheel
// centres; tools/silhouette.py turns them into the SVG paths in app.html.
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/silhouette.mjs && python3 tools/silhouette.py
import { chromium } from 'playwright-core';
import { writeFileSync } from 'node:fs';
const OUT = process.env.OUT || '/private/tmp/claude-501/-Users-carlox-Personal/bae455ed-b844-4d8b-bf32-ff71834ff136/scratchpad';
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1400, height: 800 } });
await page.goto('http://127.0.0.1:8899/app.html');
await page.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none', null, { timeout: 180000 });
await page.evaluate(() => {
  document.querySelectorAll('.panel,.hud,.views,.badge,.credit').forEach(e => e.style.display = 'none');
  const J = window.__jimny;
  J.scene.background = new J.THREE.Color(0x000000);
  // hide everything that is not the car: floor disc, shadow catcher, helpers
  J.scene.children.slice().forEach(o => { if (o !== J.rig && !o.isLight) o.visible = false; });
  document.querySelector('.stage').style.background = '#000';
  // remember which meshes are glass before flattening every material to white
  window.__glass = [];
  J.rig.traverse(o => { if (o.isMesh && /Vidros|Glass/i.test(o.material?.name || '')) window.__glass.push(o); });
  J.rig.traverse(o => { if (o.isMesh && o.material) {
    const m = Array.isArray(o.material) ? o.material : [o.material];
    m.forEach(x => { x.map = null; x.transparent = false; x.opacity = 1; x.emissive?.setHex(0xffffff); x.color?.setHex(0xffffff); });
  } });
});
await page.evaluate(() => { window.__jimny.setOrbit({ az: 1.5707963, el: 0, dist: 8.6, ty: 0.88 }); });
const spin = () => page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n > 25 ? r() : requestAnimationFrame(f)); f(); }));
await spin();
writeFileSync(`${OUT}/sil_body.png`, await page.screenshot());
// now only the glass is drawn, so the window openings can be traced separately
await page.evaluate(() => {
  const J = window.__jimny;
  J.rig.traverse(o => { if (o.isMesh) o.visible = window.__glass.includes(o); });
});
await spin();
writeFileSync(`${OUT}/sil_glass.png`, await page.screenshot());
// the wheels, in the same screen coordinates
const wheels = await page.evaluate(() => {
  const J = window.__jimny, out = [];
  J.rig.traverse(o => {
    if (!/wheel/i.test(o.name) || !o.children.length) return;
    const b = new J.THREE.Box3().setFromObject(o), c = b.getCenter(new J.THREE.Vector3());
    if (c.x < 0) return;                       // near side only
    const r = (b.max.y - b.min.y) / 2;
    // project into the CANVAS, not the window: the stage is narrower than the
    // page, and the camera's aspect follows the canvas
    const cv = document.getElementById('cv').getBoundingClientRect();
    const s = (v) => { const p = v.clone().project(J.cam);
      return [cv.left + (p.x * 0.5 + 0.5) * cv.width, cv.top + (-p.y * 0.5 + 0.5) * cv.height]; };
    const [cx, cy] = s(c), [, ty] = s(c.clone().add(new J.THREE.Vector3(0, r, 0)));
    out.push({ name: o.name, x: cx, y: cy, r: Math.abs(cy - ty) });
  });
  return out;
});
writeFileSync(`${OUT}/sil_wheels.json`, JSON.stringify(wheels, null, 1));
await browser.close();
console.error('wrote sil_body.png, sil_glass.png, sil_wheels.json');
