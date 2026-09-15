// Sample the car body surface by raycasting the model inside the page, so the
// Blender parts can be shaped to it. Writes blender/car.json.
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   npm i --no-save playwright-core && node blender/probe.mjs
import { chromium } from 'playwright-core';
import { writeFileSync } from 'node:fs';
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
await page.goto(process.argv[2] || 'http://127.0.0.1:8899/app.html');
await page.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none', null, { timeout: 120000 });
const data = await page.evaluate(() => {
  const { THREE, rig } = window.__jimny; const U = rig.userData;
  const meshes = []; U.BODY.traverse((o) => { if (o.isMesh && o.visible) meshes.push(o); });
  const rc = new THREE.Raycaster();
  const hit = (o, d) => { rc.set(o, d.normalize()); const h = rc.intersectObjects(meshes, false)[0];
    return h ? [Math.round(h.point.x * 1000), Math.round(h.point.y * 1000), Math.round(h.point.z * 1000), h.object.material.name] : null; };
  const V = (x, y, z) => new THREE.Vector3(x / 1000, y / 1000, z / 1000);
  const out = { anchors: U.anchors, dims: U.dims, side: [], top: [], rear: [], front: [] };
  for (let z = -1850; z <= 1850; z += 50) for (let y = 100; y <= 1950; y += 50) {
    const h = hit(V(2500, y, z), V(-1, 0, 0)); if (h) out.side.push(h); }
  for (let x = -900; x <= 900; x += 50) for (let z = -1850; z <= 1850; z += 50) {
    const h = hit(V(x, 3000, z), V(0, -1, 0)); if (h) out.top.push(h); }
  for (let x = -900; x <= 900; x += 50) for (let y = 100; y <= 1950; y += 50) {
    const r = hit(V(x, y, -3000), V(0, 0, 1)); if (r) out.rear.push(r);
    const f = hit(V(x, y, 3000), V(0, 0, -1)); if (f) out.front.push(f); }
  out.glass = [];
  for (let z = -1700; z <= 700; z += 20) for (let y = 1000; y <= 1650; y += 20) {
    const h = hit(V(2500, y, z), V(-1, 0, 0)); if (h && /Vidros|Lens/.test(h[3])) out.glass.push(h); }
  out.rearFine = [];
  for (let x = -800; x <= 800; x += 20) for (let y = 300; y <= 1700; y += 20) {
    const h = hit(V(x, y, -3000), V(0, 0, 1)); if (h) out.rearFine.push(h); }
  return out;
});
writeFileSync(new URL('./car.json', import.meta.url), JSON.stringify(data));
console.log(JSON.stringify(data.anchors), data.side.length, data.top.length, data.rear.length, data.front.length);
await browser.close();
