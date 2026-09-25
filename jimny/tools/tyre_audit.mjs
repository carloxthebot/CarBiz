// Every part, alone on a stock car and inside each style: does any vertex
// sit inside a tyre? Front tyres are also checked turned 30 degrees.
//
//   python3 -m http.server 8899 -d jimny   (in another shell)
//   node tools/tyre_audit.mjs              -> {} when clean
//
// Run it after touching any bumper, step, stripe or fender. It found front
// bumpers wrapping 40-80 mm into the front tyres, rear corner blocks and
// low stripes across the rear tyres, all invisible in a three-quarter shot.
import { chromium } from 'playwright-core';
const b = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 800, height: 600 } });
await p.goto('http://127.0.0.1:8899/app.html', { timeout: 120000 });
await p.waitForFunction(() => window.__jimny && document.getElementById('boot')?.style.display === 'none', null, { timeout: 240000 });
await p.waitForFunction(() => !/載入中/.test(document.getElementById('hVer').textContent), null, { timeout: 240000 });
await p.evaluate(() => { window.__jimnyStill = true; });
const res = await p.evaluate(async () => {
  const J = window.__jimny, THREE = J.THREE, U = J.rig.userData, L = window.__jimnyLists;
  const v = new THREE.Vector3();
  function check(tag) {
    J.update();
    U.BODY.updateMatrixWorld(true); U.WHEELS.updateMatrixWorld(true);
    const S = J.S;
    const wheels = (U.builtWheels ?? []).slice(0, 4).map(w => { const c = new THREE.Vector3(); w.getWorldPosition(c); return c; });
    const R = 0, hits = [], worst = {};
    const lists = window.__jimnyLists;
    const tyre = window.__jimnyTyre();                      // { dia, width } mm
    const r = tyre.dia / 2000, hw = tyre.width / 2000 * 0.95;
    const acc = U.BODY.children.find(o => o.isGroup && o !== J.rig.userData.BODY.children[0]);
    J.rig.userData.BODY.traverse(o => {
      if (!o.isMesh || !o.visible) return;
      // only accessories: the body mesh itself lives under the raw model
      let q = o, isAcc = false; while (q) { if (q.userData?.__acc) { isAcc = q.userData.__acc; break; } q = q.parent; }
      if (!isAcc) return;
      const pos = o.geometry.attributes.position; if (!pos) return;
      const step = Math.max(1, Math.floor(pos.count / 4000));
      for (let i = 0; i < pos.count; i += step) {
        v.fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld);
        for (let k = 0; k < wheels.length; k++) {
          const c = wheels[k];
          const front = c.z > 0;
          // straight, and (front) steered 30 deg: widen the x band by the swing
          const dx = Math.abs(v.x - c.x), d = Math.hypot(v.y - c.y, v.z - c.z);
          const inside = dx < hw && d < r - 0.004;
          const steer = front && !inside && d < r - 0.004 && dx < hw + r * Math.sin(30 * Math.PI / 180) * 0.6;
          if (inside || steer) { const k2 = `${isAcc}${steer ? ' (轉向時)' : ''}`; const depth = Math.round((r - d) * 1000);
            const cur = worst[k2]; if (!cur || depth > cur.depth) worst[k2] = { depth, at: [v.x, v.y, v.z].map(n => Math.round(n * 1000)), wheel: front ? 'front' : 'rear', mesh: o.name }; }
        }
      }
    });
    return Object.entries(worst).map(([k, w]) => `${k}: ${w.depth}mm @${w.at} ${w.wheel} ${w.mesh}`);
  }
  const out = {};
  // single parts on a stock car
  const DEF = {}; for (const k of Object.keys(J.S)) DEF[k] = window.__jimnyDefault(k);
  for (const [key, list] of Object.entries(L)) for (const it of list) {
    if (it.id === 'none' || it.id === 'stock') continue;
    for (const k of Object.keys(DEF)) J.S[k] = DEF[k];
    J.S[key] = it.id;
    const h = check();
    if (h.length) out[`stock+${key}=${it.id}`] = h;
  }
  // each style as shipped
  for (const id of [...document.querySelectorAll('[data-style]')].map(e => e.dataset.style)) {
    document.querySelector(`[data-style="${id}"]`).click();
    await new Promise(r => setTimeout(r, 300));
    const h = check();
    if (h.length) out[`style ${id}`] = h;
  }
  return out;
});
console.log(JSON.stringify(res, null, 1));
await b.close();
