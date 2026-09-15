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
  color, roughness: o.rough ?? 0.6, metalness: o.metal ?? 0.05,
  side: o.side ?? THREE.FrontSide,
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

  const rubber = mat(THREE, 0x1c1e21, { rough: 0.95 });
  const rubberSide = mat(THREE, 0x26292d, { rough: 0.9, side: THREE.DoubleSide });
  const rim = mat(THREE, rimColor, { rough: 0.38, metal: 0.72 });
  const hubMat = mat(THREE, 0x202328, { rough: 0.7, metal: 0.3 });

  const cyl = (r1, r2, h, seg, m, x = 0) => {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(r1 * MM, r2 * MM, h * MM, seg), m);
    c.rotation.z = Math.PI / 2; c.position.x = x * MM;
    c.castShadow = c.receiveShadow = true; return c;
  };

  // --- tyre: a hollow ring revolved from its cross-section ---------------
  // It used to be a solid cylinder, which hid the rim completely and rendered
  // every wheel as a black disc. The lathe profile runs bead -> sidewall bulge
  // -> rounded shoulder -> tread -> back, leaving the centre open so the rim
  // shows, and the sidewall height is exactly tyre radius minus rim radius.
  const sh = Math.min(sidewall * 0.28, W * 0.22);       // shoulder radius
  const bulge = W * 0.06;
  const prof = [];
  const half = W / 2;
  prof.push(new THREE.Vector2(rR * MM, -half * 0.86 * MM));                       // inner bead
  prof.push(new THREE.Vector2((rR + sidewall * 0.45) * MM, (-half - bulge) * MM)); // sidewall bulge
  for (let i = 0; i <= 6; i++) {                                                   // shoulder
    const a = Math.PI / 2 * (i / 6);
    prof.push(new THREE.Vector2((tR - sh + Math.sin(a) * sh) * MM, (-half + sh - Math.cos(a) * sh) * MM));
  }
  for (let i = 0; i <= 6; i++) {
    const a = Math.PI / 2 * (i / 6);
    prof.push(new THREE.Vector2((tR - sh + Math.cos(a) * sh) * MM, (half - sh + Math.sin(a) * sh) * MM));
  }
  prof.push(new THREE.Vector2((rR + sidewall * 0.45) * MM, (half + bulge) * MM));
  prof.push(new THREE.Vector2(rR * MM, half * 0.86 * MM));                         // outer bead
  const tyre = new THREE.Mesh(new THREE.LatheGeometry(prof, 56), rubberSide);
  tyre.rotation.z = Math.PI / 2;
  tyre.castShadow = tyre.receiveShadow = true;
  g.add(tyre);

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
      b.position.set(s * W * 0.30 * MM, Math.sin(a + stagger * 0.1) * (tR - lugH * 0.72) * MM,
        Math.cos(a + stagger * 0.1) * (tR - lugH * 0.72) * MM);
      b.rotation.x = -a;
      b.castShadow = true;
      g.add(b);
    }
    // centre blocks
    const c = new THREE.Mesh(
      new THREE.BoxGeometry(W * 0.26 * MM, lugH * MM, (tyreDia * 0.05) * MM), rubber);
    c.position.set(stagger * W * 0.5 * MM, Math.sin(a) * (tR - lugH * 0.72) * MM, Math.cos(a) * (tR - lugH * 0.72) * MM);
    c.rotation.x = -a; c.castShadow = true; g.add(c);
  }

  // --- rim --------------------------------------------------------------
  // open-ended barrel: a capped one sat in front of the spokes and hid them
  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(rR * MM, rR * MM, W * 0.80 * MM, 36, 1, true),
    mat(THREE, rimColor, { rough: 0.4, metal: 0.7, side: THREE.DoubleSide }));
  barrel.rotation.z = Math.PI / 2; g.add(barrel);
  const lip = new THREE.Mesh(new THREE.TorusGeometry((rR + 4) * MM, 9 * MM, 8, 40), rim);
  lip.rotation.y = Math.PI / 2; lip.position.x = W * 0.40 * MM; g.add(lip);
  // dark backing dish, set inboard so spokes read against it
  g.add(cyl(rR * 0.96, rR * 0.96, W * 0.04, 36, mat(THREE, 0x121417, { rough: 0.8 }), W * 0.12));

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
