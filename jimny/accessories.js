// Bolt-on accessories, generated procedurally and attached to the loaded model.
//
// These stay hand-built on purpose: a roof rack or a snorkel is tubes and plates,
// so code describes them fine, and generating them means every combination is
// available without sourcing a separate mesh per product. The car itself is a
// downloaded model because a car body is a sculpted surface and code is the
// wrong tool for that.
//
// All positions are millimetres in the same frame the rig exposes: +X right,
// +Z forward, +Y up from the ground at stock ride height.

const MM = 0.001;

export const SPEC = {
  length: 3550, width: 1645, height: 1730,
  wheelbase: 2250, trackF: 1395, trackR: 1405,
  clearance: 210,
  frontOverhang: 510, rearOverhang: 790,   // Suzuki publishes neither; 3550-2250=1300 split from photo geometry
  stockWheelDia: 15, stockTyre: '195/80R15',
};

// --- helpers ----------------------------------------------------------------

const mat = (THREE, color, opts = {}) => new THREE.MeshStandardMaterial({
  color, roughness: opts.rough ?? 0.62, metalness: opts.metal ?? 0.05, ...opts,
});

function box(THREE, w, h, d, material, x = 0, y = 0, z = 0, r = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w * MM, h * MM, d * MM), material);
  m.position.set(x * MM, y * MM, z * MM);
  if (r) m.rotation.x = r;
  m.castShadow = m.receiveShadow = true;
  return m;
}

function cyl(THREE, rTop, rBot, h, seg, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop * MM, rBot * MM, h * MM, seg), material);
  m.position.set(x * MM, y * MM, z * MM);
  m.castShadow = m.receiveShadow = true;
  return m;
}

/** Rounded slab — the body panels all have a soft edge, which is what keeps
 *  the render from looking like a stack of cardboard. */
function slab(THREE, w, h, d, rad, material, x = 0, y = 0, z = 0) {
  const s = new THREE.Shape();
  const W = w * MM / 2, H = h * MM / 2, R = Math.min(rad * MM, W, H);
  s.moveTo(-W + R, -H);
  s.lineTo(W - R, -H); s.quadraticCurveTo(W, -H, W, -H + R);
  s.lineTo(W, H - R);  s.quadraticCurveTo(W, H, W - R, H);
  s.lineTo(-W + R, H); s.quadraticCurveTo(-W, H, -W, H - R);
  s.lineTo(-W, -H + R); s.quadraticCurveTo(-W, -H, -W + R, -H);
  const g = new THREE.ExtrudeGeometry(s, { depth: d * MM, bevelEnabled: false, curveSegments: 6 });
  g.translate(0, 0, -d * MM / 2);
  const m = new THREE.Mesh(g, material);
  m.position.set(x * MM, y * MM, z * MM);
  m.castShadow = m.receiveShadow = true;
  return m;
}

const group = (THREE, name) => { const g = new THREE.Group(); g.name = name; return g; };

// --- accessories ------------------------------------------------------------
// Each returns a group positioned in body space. The body group is what gets
// lifted, so accessories ride with it automatically.

const ACC = {};

ACC.snorkel = (THREE, C) => {
  const g = group(THREE, 'snorkel');
  const m = mat(THREE, 0x1c1f24, { rough: 0.8 });
  const x = C.bodyW / 2 - 30, zA = 300;
  g.add(cyl(THREE, 52, 52, 980, 14, m, x, C.beltline + 300, zA));           // riser
  const elbow = cyl(THREE, 52, 52, 300, 14, m, x, C.beltline - 180, zA + 120);
  elbow.rotation.x = Math.PI / 2; g.add(elbow);
  const head = box(THREE, 130, 150, 240, m, x, C.beltline + 830, zA + 60);  // ram head
  g.add(head);
  g.add(box(THREE, 120, 24, 24, m, x, C.beltline + 180, zA));               // guard clamp
  return g;
};

ACC.roofRack = (THREE, C, variant = 'platform') => {
  const g = group(THREE, 'roofRack');
  const m = mat(THREE, 0x24272c, { rough: 0.75 });
  const y = C.roofY + 60, L = variant === 'platform' ? 1500 : 1250, W = C.bodyW - 120;
  g.add(box(THREE, W, 26, L, m, 0, y, -80));                                 // deck
  const slats = variant === 'platform' ? 9 : 5;
  for (let i = 0; i < slats; i++)
    g.add(box(THREE, W - 40, 34, 22, m, 0, y + 22, -80 - L / 2 + 60 + i * ((L - 120) / (slats - 1))));
  for (const side of [-1, 1]) {                                              // side rails
    g.add(box(THREE, 30, 70, L, m, side * (W / 2 - 12), y + 36, -80));
    for (const z of [-L / 2 + 120, 0, L / 2 - 120])                          // feet
      g.add(box(THREE, 46, 90, 60, m, side * (W / 2 - 60), y - 66, z - 80));
  }
  if (variant === 'basket')
    for (const side of [-1, 1]) g.add(box(THREE, 26, 150, L, m, side * (W / 2 - 12), y + 100, -80));
  return g;
};

ACC.lightBar = (THREE, C) => {
  const g = group(THREE, 'lightBar');
  const hsg = mat(THREE, 0x1a1d21, { rough: 0.6 });
  const lens = new THREE.MeshStandardMaterial({ color: 0xdfe7f0, emissive: 0x9fb4cc, emissiveIntensity: 0.45, roughness: 0.25 });
  const y = C.roofY + 150, z = C.frontZ - 240;
  g.add(box(THREE, 1100, 90, 70, hsg, 0, y, z));
  g.add(box(THREE, 1040, 52, 26, lens, 0, y, z - 30));
  for (const s of [-1, 1]) g.add(box(THREE, 40, 120, 40, hsg, s * 420, y - 90, z + 10));
  return g;
};

ACC.frontBumper = (THREE, C, variant = 'tube') => {
  const g = group(THREE, 'frontBumper');
  const m = mat(THREE, 0x212429, { rough: 0.7, metal: 0.2 });
  const z = C.frontZ - 30, y = C.bumperY;
  if (variant === 'delete') {
    g.add(box(THREE, C.bodyW - 120, 90, 120, m, 0, y + 40, z + 60));
    return g;
  }
  g.add(box(THREE, C.bodyW - 40, 150, 180, m, 0, y, z));                     // main beam
  if (variant === 'bull' || variant === 'winch') {
    for (const s of [-1, 1]) {                                               // uprights
      const u = cyl(THREE, 26, 26, 620, 12, m, s * 330, y + 320, z - 40);
      g.add(u);
      g.add(box(THREE, 150, 300, 26, m, s * (C.bodyW / 2 - 90), y + 150, z - 20)); // wing
    }
    const top = cyl(THREE, 26, 26, 700, 12, m, 0, y + 620, z - 40);          // hoop
    top.rotation.z = Math.PI / 2; g.add(top);
    g.add(box(THREE, 640, 26, 26, m, 0, y + 330, z - 40));
  }
  if (variant === 'winch') {
    g.add(cyl(THREE, 95, 95, 420, 16, m, 0, y + 130, z + 90));               // drum
    g.add(box(THREE, 500, 40, 90, mat(THREE, 0x2f3339), 0, y + 130, z - 30)); // fairlead
  }
  for (const s of [-1, 1]) g.add(cyl(THREE, 34, 34, 120, 10, mat(THREE, 0xc44a12), s * 250, y - 20, z - 60)); // recovery points
  return g;
};

ACC.rearBumper = (THREE, C, variant = 'tube') => {
  const g = group(THREE, 'rearBumper');
  const m = mat(THREE, 0x212429, { rough: 0.7, metal: 0.2 });
  const z = C.rearZ + 30, y = C.bumperY;
  if (variant === 'delete') { g.add(box(THREE, C.bodyW - 200, 80, 90, m, 0, y + 30, z - 40)); return g; }
  g.add(box(THREE, C.bodyW - 40, 150, 170, m, 0, y, z));
  if (variant === 'tube')
    for (const s of [-1, 1]) g.add(box(THREE, 120, 220, 26, m, s * (C.bodyW / 2 - 80), y + 150, z + 10));
  for (const s of [-1, 1]) g.add(cyl(THREE, 34, 34, 120, 10, mat(THREE, 0xc44a12), s * 240, y - 20, z + 50));
  return g;
};

ACC.rockSliders = (THREE, C) => {
  const g = group(THREE, 'rockSliders');
  const m = mat(THREE, 0x1e2126, { rough: 0.75, metal: 0.2 });
  for (const s of [-1, 1]) {
    g.add(cyl(THREE, 38, 38, 1500, 12, m, s * (C.bodyW / 2 + 10), C.sillY - 40, 60));
    for (const z of [-560, 60, 680])
      g.add(box(THREE, 200, 40, 60, m, s * (C.bodyW / 2 - 60), C.sillY - 30, z));
  }
  return g;
};

ACC.ladder = (THREE, C) => {
  const g = group(THREE, 'ladder');
  const m = mat(THREE, 0x24272c, { rough: 0.7 });
  const x = -C.bodyW / 2 + 240, z = C.rearZ - 20;
  for (const s of [-1, 1]) g.add(cyl(THREE, 20, 20, 1180, 10, m, x + s * 150, C.sillY + 560, z));
  for (let i = 0; i < 6; i++) {
    const r = cyl(THREE, 15, 15, 300, 8, m, x, C.sillY + 60 + i * 210, z);
    r.rotation.z = Math.PI / 2; g.add(r);
  }
  return g;
};

ACC.spare = (THREE, C, { cover = 'soft', tyreDia = 686, bag = false }) => {
  const g = group(THREE, 'spare');
  const z = C.rearZ + 190;
  const y = C.sillY + 620;
  if (cover !== 'none') {
    const carrier = mat(THREE, 0x24272c, { rough: 0.7 });
    g.add(box(THREE, 180, 180, 90, carrier, 120, y, C.rearZ + 60));           // carrier arm
  }
  const t = buildWheel(THREE, { rimDia: 15, tyreDia, width: 180, style: 'steel' });
  t.rotation.y = Math.PI / 2; t.position.set(0, y * MM, z * MM); g.add(t);
  if (cover === 'hard' || cover === 'soft') {
    const cm = cover === 'hard'
      ? mat(THREE, 0x2b2f35, { rough: 0.5 })
      : mat(THREE, 0x1a1c20, { rough: 0.92 });
    const c = cyl(THREE, tyreDia / 2 + 14, tyreDia / 2 + 14, 60, 32, cm, 0, y, z + 110);
    c.rotation.z = Math.PI / 2; c.rotation.y = Math.PI / 2; g.add(c);
    g.add(cyl(THREE, tyreDia / 2 + 14, tyreDia / 2 + 14, 10, 32, cm, 0, y, z + 140));
  }
  if (bag) {                                                                  // スペアタイヤバッグ
    const bm = mat(THREE, 0x3a4a3c, { rough: 0.95 });
    g.add(box(THREE, 520, 360, 170, bm, 0, y - 40, z + 190));
    g.add(box(THREE, 540, 60, 30, mat(THREE, 0x20281f), 0, y + 120, z + 250));
    for (const s of [-1, 1]) g.add(box(THREE, 40, 300, 24, mat(THREE, 0x20281f), s * 180, y - 40, z + 268));
  }
  return g;
};

ACC.windowGuards = (THREE, C) => {
  const g = group(THREE, 'windowGuards');
  const m = mat(THREE, 0x1a1d21, { rough: 0.8 });
  for (const s of [-1, 1]) {
    const x = s * (C.bodyW / 2 + 12);
    for (const [z, w] of [[430, 620], [-330, 560]]) {                         // front door, rear quarter
      g.add(box(THREE, 22, C.glassH, 26, m, x, C.glassY, z + w / 2));
      g.add(box(THREE, 22, C.glassH, 26, m, x, C.glassY, z - w / 2));
      g.add(box(THREE, 22, 26, w, m, x, C.glassY + C.glassH / 2, z));
      g.add(box(THREE, 22, 26, w, m, x, C.glassY - C.glassH / 2, z));
      for (let i = 1; i <= 3; i++) g.add(box(THREE, 18, C.glassH, 16, m, x, C.glassY, z - w / 2 + i * (w / 4)));
      g.add(box(THREE, 18, 16, w, m, x, C.glassY, z));
    }
  }
  return g;
};

ACC.awning = (THREE, C, side = 'left') => {
  const g = group(THREE, 'awning');
  const s = side === 'left' ? -1 : 1;
  const caseM = mat(THREE, 0x2a2d33, { rough: 0.6 });
  const x = s * (C.bodyW / 2 + 70);
  g.add(box(THREE, 170, 170, 1900, caseM, x, C.roofY + 40, -60));             // stowed case
  for (const z of [-700, 500]) g.add(box(THREE, 150, 40, 90, caseM, s * (C.bodyW / 2 - 10), C.roofY + 40, z));
  return g;
};

ACC.grille = (THREE, C, variant = 'stock', bodyMat) => {
  const g = group(THREE, 'grille');
  const dark = mat(THREE, 0x15171a, { rough: 0.7 });
  const z = C.frontZ + 4, y = C.grilleY;
  const W = C.bodyW - 300, H = 300;
  if (variant === 'retro') {
    // JA11-style horizontal-bar face
    g.add(box(THREE, W, H, 40, dark, 0, y, z));
    for (let i = 0; i < 4; i++)
      g.add(box(THREE, W - 60, 26, 50, bodyMat, 0, y - H / 2 + 55 + i * 62, z + 8));
  } else if (variant === 'mesh') {
    g.add(box(THREE, W, H, 40, dark, 0, y, z));
    for (let i = 0; i < 13; i++) g.add(box(THREE, 14, H - 30, 46, mat(THREE, 0x2c3037), -W / 2 + 30 + i * ((W - 60) / 12), y, z + 6));
    for (let i = 0; i < 5; i++) g.add(box(THREE, W - 30, 12, 46, mat(THREE, 0x2c3037), 0, y - H / 2 + 40 + i * ((H - 80) / 4), z + 6));
  } else {
    // factory: five vertical slots in a black surround
    g.add(box(THREE, W, H, 40, dark, 0, y, z));
    for (let i = 0; i < 5; i++)
      g.add(box(THREE, 58, H - 70, 52, mat(THREE, 0x0e1013), -W / 2 + 110 + i * ((W - 220) / 4), y, z + 6));
  }
  return g;
};


export function buildAccessory(THREE, kind, C, variant) {
  const fn = ACC[kind];
  return fn ? fn(THREE, C, variant) : null;
}
