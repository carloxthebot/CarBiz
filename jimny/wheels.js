// Procedurally built wheel + tyre, used to REPLACE the ones in the downloaded
// model so the configurator actually shows the product you picked.
//
// Scaling the model's own wheel was wrong twice over: a 15" rim grew when you
// fitted a taller tyre, which no rim does, and every choice looked identical
// because it was the same mesh at a different size. Fitting a bigger tyre
// changes the SIDEWALL; fitting a different wheel changes the RIM. Those are
// separate inputs here, which is also how the parts catalogue describes them.
//
//   rimDia   inches  — the wheel itself, 15 or 16 on a JB74
//   tyreDia  mm      — overall diameter, from the tyre size
//   width    mm      — section width, drives how fat the tyre looks
//   style            — rim design: stock / steel / spoke / beadlock
//   tread            — at (chunky blocks) or mt (bigger, more open)
//
// Sidewall height falls out: (tyreDia - rimDia*25.4) / 2. That is why a
// 195/80R15 and a 235/75R15 look different on the same rim.

const MM = 0.001;

const mat = (THREE, color, o = {}) => new THREE.MeshStandardMaterial({
  color, roughness: o.rough ?? 0.6, metalness: o.metal ?? 0.05, ...o,
});

export function buildWheel(THREE, {
  rimDia = 15, tyreDia = 693, width = 195,
  style = 'stock', tread = 'at', rimColor = 0xc8ccd0,
} = {}) {
  const g = new THREE.Group();
  g.name = 'wheel';

  const tR = tyreDia / 2;                  // tyre outer radius, mm
  const rR = (rimDia * 25.4) / 2;          // rim radius, mm
  const sidewall = Math.max(tR - rR, 40);  // what actually changes with tyre size
  const W = width * 0.92;

  const rubber = mat(THREE, 0x15171a, { rough: 0.96 });
  const rubberLit = mat(THREE, 0x1d2024, { rough: 0.94 });
  const rim = mat(THREE, rimColor, { rough: 0.38, metal: 0.72 });
  const hubMat = mat(THREE, 0x202328, { rough: 0.7, metal: 0.3 });

  const cyl = (r1, r2, h, seg, m, x = 0) => {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(r1 * MM, r2 * MM, h * MM, seg), m);
    c.rotation.z = Math.PI / 2; c.position.x = x * MM;
    c.castShadow = c.receiveShadow = true; return c;
  };

  // --- tyre: carcass, shoulders, sidewall bulge -------------------------
  g.add(cyl(tR, tR, W, 44, rubber));
  // shoulders taper in, which is what stops it reading as a barrel
  g.add(cyl(tR - sidewall * 0.10, tR, W * 0.22, 44, rubber, W * 0.40));
  g.add(cyl(tR, tR - sidewall * 0.10, W * 0.22, 44, rubber, -W * 0.40));
  // sidewall face, slightly proud so the tyre has a lip over the rim
  g.add(cyl(rR + sidewall * 0.62, rR + sidewall * 0.62, W * 1.01, 40, rubberLit));

  // --- tread ------------------------------------------------------------
  const mt = tread === 'mt';
  const lugs = mt ? 16 : 24;
  const lugH = sidewall * (mt ? 0.16 : 0.11);
  const lugW = mt ? 0.40 : 0.30;
  for (let i = 0; i < lugs; i++) {
    const a = (i / lugs) * Math.PI * 2;
    const stagger = (i % 2) ? 0.16 : -0.16;
    for (const s of [-1, 1]) {
      const b = new THREE.Mesh(
        new THREE.BoxGeometry(W * lugW * MM, lugH * MM, (tyreDia * (mt ? 0.075 : 0.055)) * MM), rubber);
      b.position.set(s * W * 0.30 * MM, Math.sin(a + stagger * 0.1) * (tR - lugH * 0.4) * MM,
        Math.cos(a + stagger * 0.1) * (tR - lugH * 0.4) * MM);
      b.rotation.x = -a;
      b.castShadow = true;
      g.add(b);
    }
    // centre blocks
    const c = new THREE.Mesh(
      new THREE.BoxGeometry(W * 0.26 * MM, lugH * MM, (tyreDia * 0.05) * MM), rubber);
    c.position.set(stagger * W * 0.5 * MM, Math.sin(a) * (tR - lugH * 0.4) * MM, Math.cos(a) * (tR - lugH * 0.4) * MM);
    c.rotation.x = -a; c.castShadow = true; g.add(c);
  }

  // --- rim --------------------------------------------------------------
  g.add(cyl(rR, rR, W * 0.80, 36, rim));                    // barrel
  g.add(cyl(rR + 8, rR + 8, W * 0.07, 36, rim, W * 0.38));  // outer lip
  const face = cyl(rR * 0.97, rR * 0.97, W * 0.10, 36, rim, W * 0.30);
  g.add(face);

  const spokes = { stock: 5, spoke: 8, beadlock: 8, steel: 0 }[style] ?? 5;
  if (style === 'steel') {
    g.add(cyl(rR * 0.94, rR * 0.94, W * 0.12, 32, rim, W * 0.26));
    for (let i = 0; i < 6; i++) {                            // vent holes
      const a = (i / 6) * Math.PI * 2;
      const h = new THREE.Mesh(new THREE.CylinderGeometry(rR * 0.13 * MM, rR * 0.13 * MM, W * 0.4 * MM, 14),
        mat(THREE, 0x0b0c0e));
      h.rotation.z = Math.PI / 2;
      h.position.set(W * 0.26 * MM, Math.sin(a) * rR * 0.55 * MM, Math.cos(a) * rR * 0.55 * MM);
      g.add(h);
    }
  } else {
    for (let i = 0; i < spokes; i++) {
      const a = (i / spokes) * Math.PI * 2;
      const wSpoke = style === 'stock' ? 0.30 : 0.17;
      const s = new THREE.Mesh(
        new THREE.BoxGeometry(W * 0.16 * MM, (rR * 1.30) * MM, (rR * wSpoke) * MM), rim);
      s.position.set(W * 0.30 * MM, Math.sin(a) * rR * 0.44 * MM, Math.cos(a) * rR * 0.44 * MM);
      s.rotation.x = -a; s.castShadow = true;
      g.add(s);
      // window between spokes reads as depth
      const wdw = new THREE.Mesh(
        new THREE.CylinderGeometry(rR * 0.13 * MM, rR * 0.13 * MM, W * 0.5 * MM, 12), mat(THREE, 0x101215));
      wdw.rotation.z = Math.PI / 2;
      const b = a + Math.PI / spokes;
      wdw.position.set(W * 0.24 * MM, Math.sin(b) * rR * 0.62 * MM, Math.cos(b) * rR * 0.62 * MM);
      g.add(wdw);
    }
  }
  if (style === 'beadlock') {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(rR * 0.95 * MM, 10 * MM, 8, 36),
      mat(THREE, 0xb8410f, { rough: 0.45, metal: 0.3 }));
    ring.position.x = W * 0.36 * MM; ring.rotation.y = Math.PI / 2; g.add(ring);
    for (let i = 0; i < 16; i++) {                           // bolts
      const a = (i / 16) * Math.PI * 2;
      const b = new THREE.Mesh(new THREE.CylinderGeometry(6 * MM, 6 * MM, 16 * MM, 6), hubMat);
      b.rotation.z = Math.PI / 2;
      b.position.set(W * 0.40 * MM, Math.sin(a) * rR * 0.95 * MM, Math.cos(a) * rR * 0.95 * MM);
      g.add(b);
    }
  }

  // hub + studs
  g.add(cyl(rR * 0.26, rR * 0.26, W * 0.24, 20, hubMat, W * 0.34));
  for (let i = 0; i < 5; i++) {                              // 5x139.7
    const a = (i / 5) * Math.PI * 2;
    const n = new THREE.Mesh(new THREE.CylinderGeometry(9 * MM, 9 * MM, 14 * MM, 6), hubMat);
    n.rotation.z = Math.PI / 2;
    n.position.set(W * 0.38 * MM, Math.sin(a) * rR * 0.17 * MM, Math.cos(a) * rR * 0.17 * MM);
    g.add(n);
  }

  g.userData = { tyreDia, rimDia, width, sidewall };
  return g;
}
