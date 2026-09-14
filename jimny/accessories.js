// Bolt-on accessories, generated procedurally and attached to the loaded model.
//
// These stay hand-built on purpose: a roof rack or a snorkel is tubes and
// plates, so code describes them fine, and generating them means every
// combination is available without sourcing a mesh per product. The car body is
// a downloaded model because a car body is a sculpted surface, which code is
// the wrong tool for.
//
// Everything positions itself from the anchors rig.js MEASURED off the mesh —
// roof height, half-width, nose and tail Z, the spare's actual centre. An
// earlier version used constants copied from a hand-built model and put the
// rack in mid-air and the snorkel through the floor; nothing here may hard-code
// a position that could instead be derived from `C`.
//
// Units are millimetres. +X right, +Z forward (nose), +Y up from the ground.

const MM = 0.001;

const mat = (THREE, color, opts = {}) => new THREE.MeshStandardMaterial({
  color, roughness: opts.rough ?? 0.62, metalness: opts.metal ?? 0.05, ...opts,
});

function box(THREE, w, h, d, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w * MM, h * MM, d * MM), material);
  m.position.set(x * MM, y * MM, z * MM);
  m.castShadow = true;
  return m;
}

function cyl(THREE, r, h, seg, material, x = 0, y = 0, z = 0, axis = 'y') {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r * MM, r * MM, h * MM, seg), material);
  m.position.set(x * MM, y * MM, z * MM);
  if (axis === 'x') m.rotation.z = Math.PI / 2;
  if (axis === 'z') m.rotation.x = Math.PI / 2;
  m.castShadow = true;
  return m;
}

const group = (THREE, name) => { const g = new THREE.Group(); g.name = name; return g; };
const STEEL = (THREE) => mat(THREE, 0x23262b, { rough: 0.62, metal: 0.35 });

const ACC = {};

// Roof rack sits ON the measured roof, spanning the measured roof panel.
ACC.roofRack = (THREE, C, variant = 'platform') => {
  const g = group(THREE, 'roofRack');
  const m = STEEL(THREE);
  const W = C.roofHalfW * 2 * 0.92;
  const zF = C.roofZFront, zR = C.roofZRear;
  const len = (zF - zR) * (variant === 'platform' ? 0.92 : 0.72);
  const zC = (zF + zR) / 2 + (variant === 'platform' ? 0 : -(zF - zR) * 0.08);
  const footH = 55;
  const deckY = C.roofY + footH + 14;

  for (const s of [-1, 1]) for (const z of [zC - len / 2 + 90, zC, zC + len / 2 - 90])
    g.add(box(THREE, 44, footH, 70, m, s * (W / 2 - 55), C.roofY + footH / 2, z));
  g.add(box(THREE, W, 26, len, m, 0, deckY, zC));
  const slats = variant === 'platform' ? 8 : 5;
  for (let i = 0; i < slats; i++)
    g.add(box(THREE, W - 50, 26, 26, m, 0, deckY + 24, zC - len / 2 + 70 + i * ((len - 140) / (slats - 1))));
  for (const s of [-1, 1]) g.add(box(THREE, 26, 58, len, m, s * (W / 2 - 10), deckY + 28, zC));
  if (variant === 'basket')
    for (const s of [-1, 1]) g.add(box(THREE, 22, 130, len, m, s * (W / 2 - 10), deckY + 90, zC));
  return g;
};

// Light bar clamps to the leading edge of the roof.
ACC.lightBar = (THREE, C) => {
  const g = group(THREE, 'lightBar');
  const hsg = mat(THREE, 0x16181c, { rough: 0.55 });
  const lens = new THREE.MeshStandardMaterial({
    color: 0xe6ecf3, emissive: 0x9db3cb, emissiveIntensity: 0.4, roughness: 0.22,
  });
  const W = C.roofHalfW * 2 * 0.74;
  const y = C.roofY + 118, z = C.roofZFront - 40;
  for (const s of [-1, 1]) g.add(box(THREE, 34, 100, 40, hsg, s * (W / 2 - 30), C.roofY + 52, z + 10));
  g.add(box(THREE, W, 80, 62, hsg, 0, y, z));
  g.add(box(THREE, W - 46, 46, 22, lens, 0, y, z - 26));
  return g;
};

// Snorkel: rises alongside the A-pillar from the guard to just above the roof.
ACC.snorkel = (THREE, C) => {
  const g = group(THREE, 'snorkel');
  const m = mat(THREE, 0x1a1d22, { rough: 0.78 });
  const x = C.halfW + 34;
  const zA = C.noseZ - (C.noseZ - C.frontAxleZ) * 0.30;   // just behind the front wheel
  const yBot = C.beltY - 120;
  const yTop = C.roofY + 40;
  g.add(cyl(THREE, 48, yTop - yBot, 14, m, x, (yBot + yTop) / 2, zA));
  g.add(box(THREE, 106, 120, 190, m, x, yTop + 60, zA + 34));               // ram head
  g.add(cyl(THREE, 48, 200, 12, m, x, yBot, zA + 60, 'z'));                 // into the guard
  for (const y of [yBot + 180, yTop - 220])
    g.add(box(THREE, 92, 20, 20, m, x - 16, y, zA));                        // pillar clamps
  return g;
};

ACC.rockSliders = (THREE, C) => {
  const g = group(THREE, 'rockSliders');
  const m = STEEL(THREE);
  const len = (C.frontAxleZ - C.rearAxleZ) * 0.78;
  const y = C.sillY + 30;
  for (const s of [-1, 1]) {
    g.add(cyl(THREE, 36, len, 12, m, s * (C.halfW + 26), y, 0, 'z'));
    for (const z of [-len / 2 + 140, 0, len / 2 - 140])
      g.add(box(THREE, 150, 34, 56, m, s * (C.halfW - 40), y + 26, z));
  }
  return g;
};

ACC.ladder = (THREE, C) => {
  const g = group(THREE, 'ladder');
  const m = STEEL(THREE);
  const x = -C.halfW * 0.52;                    // offset to the non-spare side
  const z = C.tailZ - 26;
  const yBot = C.sillY + 120, yTop = C.roofY - 40;
  for (const s of [-1, 1]) g.add(cyl(THREE, 17, yTop - yBot, 10, m, x + s * 130, (yBot + yTop) / 2, z));
  const rungs = 6;
  for (let i = 0; i < rungs; i++)
    g.add(cyl(THREE, 13, 260, 8, m, x, yBot + i * ((yTop - yBot) / (rungs - 1)), z, 'x'));
  for (const y of [yTop - 60, yBot + 60])
    g.add(box(THREE, 260, 18, 70, m, x, y, z + 40));
  return g;
};

ACC.windowGuards = (THREE, C) => {
  const g = group(THREE, 'windowGuards');
  const m = mat(THREE, 0x16191d, { rough: 0.8 });
  const h = C.glassH * 0.82;
  const y = C.glassY;
  // two apertures per side, sized from the cabin's measured length
  const cabLen = (C.frontAxleZ - C.rearAxleZ) * 0.86;
  const panes = [[cabLen * 0.22, cabLen * 0.42], [-cabLen * 0.30, cabLen * 0.34]];
  for (const s of [-1, 1]) {
    const x = s * (C.halfW + 16);
    for (const [zc, w] of panes) {
      g.add(box(THREE, 16, h, 22, m, x, y, zc + w / 2));
      g.add(box(THREE, 16, h, 22, m, x, y, zc - w / 2));
      g.add(box(THREE, 16, 22, w, m, x, y + h / 2, zc));
      g.add(box(THREE, 16, 22, w, m, x, y - h / 2, zc));
      for (let i = 1; i <= 3; i++) g.add(box(THREE, 13, h, 13, m, x, y, zc - w / 2 + i * (w / 4)));
      g.add(box(THREE, 13, 13, w, m, x, y, zc));
    }
  }
  return g;
};

ACC.awning = (THREE, C, side = 'left') => {
  const g = group(THREE, 'awning');
  const s = side === 'left' ? -1 : 1;
  const m = mat(THREE, 0x2b2e34, { rough: 0.58 });
  const len = (C.roofZFront - C.roofZRear) * 0.94;
  const x = s * (C.roofHalfW + 76);
  g.add(box(THREE, 150, 155, len, m, x, C.roofY + 62, (C.roofZFront + C.roofZRear) / 2));
  for (const z of [-len * 0.3, len * 0.3])
    g.add(box(THREE, 130, 34, 74, m, s * (C.roofHalfW + 8), C.roofY + 62, z + (C.roofZFront + C.roofZRear) / 2));
  return g;
};

// Spare-wheel bag: hangs on the spare the model already carries.
ACC.spareBag = (THREE, C) => {
  if (!C.spare) return null;
  const g = group(THREE, 'spareBag');
  const canvas = mat(THREE, 0x3b4a3d, { rough: 0.95 });
  const strap = mat(THREE, 0x1e241d, { rough: 0.9 });
  const d = C.spare.dia;
  const w = d * 0.78, h = d * 0.54;
  const z = C.spare.z - 150;                       // outboard of the wheel face
  g.add(box(THREE, w, h, 160, canvas, C.spare.x, C.spare.y - d * 0.06, z));
  g.add(box(THREE, w + 20, 52, 26, strap, C.spare.x, C.spare.y + h * 0.42, z - 74));
  for (const s of [-1, 1])
    g.add(box(THREE, 34, h * 0.86, 20, strap, C.spare.x + s * w * 0.34, C.spare.y - d * 0.06, z - 82));
  return g;
};

export function buildAccessory(THREE, kind, C, variant) {
  const fn = ACC[kind];
  return fn ? fn(THREE, C, variant) : null;
}
