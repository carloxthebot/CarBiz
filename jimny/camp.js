// The camping area: tents and awnings OPEN, which is what they are bought for
// and what nobody can picture from a packed bag on a roof rack.
//
// These are built here rather than in Blender because an open tent is a
// handful of fabric planes and poles whose sizes come straight from the
// catalogue entry (awning length, projection, radius; tent open L x W x H),
// so one parametric builder covers every model. Everything is in the car
// frame in millimetres -- +Y up, +Z forward, +X the vehicle's LEFT -- and
// the group is added under BODY, so `groundY` (mm, negative) is where the
// ground is in that frame once the body has been lifted.
//
// Geometry follows docs/jb74-camping.json `modellingNotes`. Where the makers
// publish a figure (ARB 2500 projection, 1900-2100 leg height, Rhino 1900 /
// 2500 radius, Kamado 2100 x 1120 x 970 open) it is used; hinge sides,
// overhangs and ladder angles are that file's stated assumptions.

// same numbers as blender/build_parts.py, which places the packed bags
const RACK_TOP = 1684, RACK_ZC = -552.5, RACK_W = 1285, ROOF_Y = 1622, ROOF_ZF = 380, ROOF_ZR = -1445;

let MATS = null;
function mats(THREE) {
  if (MATS) return MATS;
  const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0, side: THREE.DoubleSide, ...o });
  MATS = {
    canvas: std(0x6d6a5a),                    // khaki-grey poly-cotton
    canvasDark: std(0x3f423d),
    tentShell: std(0x2a2c2e, { roughness: 0.5, metalness: 0.2 }),
    tentFabric: std(0x7c7f72),
    mesh: std(0x1b1d1e, { transparent: true, opacity: 0.55 }),
    pole: new THREE.MeshStandardMaterial({ color: 0xb9bcbf, roughness: 0.35, metalness: 1 }),
    black: new THREE.MeshStandardMaterial({ color: 0x1b1c1e, roughness: 0.55, metalness: 0.25 }),
    rope: new THREE.MeshStandardMaterial({ color: 0xc9b06a, roughness: 0.9 }),
    tarp: std(0x8a8a78),
  };
  return MATS;
}

const MM = 0.001;
const v = (THREE, x, y, z) => new THREE.Vector3(x * MM, y * MM, z * MM);

/** A round tube from a to b (mm points). */
function rod(THREE, a, b, dia, mat) {
  const A = v(THREE, ...a), B = v(THREE, ...b);
  const len = A.distanceTo(B);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(dia / 2 * MM, dia / 2 * MM, len, 10), mat);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  return m;
}

/** A fabric surface through rows of mm points (a grid, rows x cols). */
function sheet(THREE, rows, mat) {
  const pos = [], idx = [];
  const nr = rows.length, nc = rows[0].length;
  for (const r of rows) for (const p of r) pos.push(p[0] * MM, p[1] * MM, p[2] * MM);
  for (let i = 0; i < nr - 1; i++) for (let j = 0; j < nc - 1; j++) {
    const a = i * nc + j, b = a + 1, c = a + nc, d = c + 1;
    idx.push(a, c, b, b, c, d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

/** A flat polygon (mm points, convex, in order). */
function poly(THREE, pts, mat) {
  const pos = pts.flatMap(p => [p[0] * MM, p[1] * MM, p[2] * MM]), idx = [];
  for (let i = 1; i < pts.length - 1; i++) idx.push(0, i, i + 1);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, mat); m.castShadow = true;
  return m;
}

const lerp = (a, b, t) => a + (b - a) * t;

// ---------------------------------------------------------------- awnings
/**
 * An awning rolled out of its bag on the rack side rail. `aw` is the AWNINGS
 * entry: `open` carries the deployed geometry -- { kind: 'rect', along,
 * projection, legs } or { kind: 'fan', radius, arms } for the 270-degree
 * batwings, which pivot at the REAR end of the bag and sweep round the tail.
 */
export function openAwning(THREE, aw, side, groundY, room = false) {
  const M = mats(THREE), g = new THREE.Group();
  const s = side === 'left' ? 1 : -1;
  const o = aw.open;
  const bagX = s * (RACK_W / 2 + 70), bagY = RACK_TOP + 20;
  if (o.kind === 'rect') {
    const L = o.along, P = o.projection, z0 = RACK_ZC - L / 2, z1 = RACK_ZC + L / 2;
    // ARB publish 1900-2100 mm at the legs, so the outer edge sits at 2000 above
    // the ground -- above the bag on a stock-height Jimny, pitched up
    const outY = Math.max(bagY - 70, groundY + 2000);
    const rows = [];
    for (let i = 0; i <= 8; i++) {            // across: bag -> outer edge, with a slight sag
      const t = i / 8, x = bagX + s * P * t, y = lerp(bagY, outY, t) - Math.sin(t * Math.PI) * 60;
      rows.push([0, 0.5, 1].map(k => [x, y, lerp(z0, z1, k)]));
    }
    g.add(sheet(THREE, rows, M.canvas));
    const legTop = outY - 10;
    for (const z of [z0, z1]) {
      g.add(rod(THREE, [bagX, bagY, z], [bagX + s * P, outY, z], 25, M.pole));          // swing arms
      g.add(rod(THREE, [bagX + s * P, legTop, z], [bagX + s * P, groundY, z], 25, M.pole));  // legs
      g.add(rod(THREE, [bagX + s * P, legTop, z], [bagX + s * (P + 900), groundY, z + (z > RACK_ZC ? 500 : -500)], 4, M.rope));
    }
    if (room) {                                // ARB Deluxe Awning Room 813108 under a 2500 x 2500
      const h = legTop - groundY, x0 = bagX + s * 60, x1 = bagX + s * P;
      const wall = (a, b) => poly(THREE, [[a[0], groundY, a[1]], [b[0], groundY, b[1]], [b[0], groundY + h, b[1]], [a[0], groundY + h, a[1]]], M.canvasDark);
      g.add(wall([x1, z0], [x1, z1]), wall([x0, z0], [x1, z0]), wall([x0, z1], [x1, z1]));
      // the outer wall's door, rolled half up, as a mesh panel
      const dz = (z1 - z0) * 0.3;
      g.add(poly(THREE, [[x1 + s * 4, groundY, RACK_ZC - dz / 2], [x1 + s * 4, groundY, RACK_ZC + dz / 2],
        [x1 + s * 4, groundY + h * 0.8, RACK_ZC + dz / 2], [x1 + s * 4, groundY + h * 0.8, RACK_ZC - dz / 2]], M.mesh));
    }
  } else {
    const R = o.radius, pz = RACK_ZC - aw.bagL / 2;   // pivot at the rear end of the bag
    const px = bagX, py = bagY, n = 36, edgeDrop = 420, sweep = o.sweep ?? 270;
    const rows = [];
    for (let i = 0; i <= 6; i++) {
      const t = i / 6, r = R * t;
      const row = [];
      for (let k = 0; k <= n; k++) {
        const th = (sweep * k / n) * Math.PI / 180;
        const x = px + s * r * Math.sin(th), z = pz + r * Math.cos(th);
        row.push([x, py - edgeDrop * t * t - Math.sin(t * Math.PI) * 40, z]);
      }
      rows.push(row);
    }
    g.add(sheet(THREE, rows, M.canvas));
    const arms = o.arms ?? 4;
    for (let a = 0; a < arms; a++) {
      const th = (sweep * (a + 0.5) / arms) * Math.PI / 180;
      const x = px + s * R * Math.sin(th), z = pz + R * Math.cos(th), y = py - edgeDrop;
      g.add(rod(THREE, [px, py + 30, pz], [x, y, z], 22, M.pole));
      if (a >= (o.freeArms ?? 0)) g.add(rod(THREE, [x, y, z], [x, groundY, z], 22, M.pole));
    }
    g.add(rod(THREE, [px, py - 40, pz], [px, py + 120, pz], 40, M.black));   // pivot post
  }
  return g;
}

// ------------------------------------------------------------ roof tents
/**
 * A roof-top tent, closed or open. `t.shape` picks the mechanism:
 *   'wedge'   Kamado Canotier J3: hard lid hinged at the front, rear lifts,
 *             and a rear section that extends over the tailgate.
 *   'foldout' Front Runner TENT031: floor flips out over one side, the ladder
 *             props the outer half, a dome of fabric over the whole floor.
 *   'popup'   Autohome Columbus: the lid rises level on gas struts.
 * `base` is the height the tent sits on (the roof itself, or a rack).
 */
export function roofTent(THREE, t, open, side, groundY, base) {
  const M = mats(THREE), g = new THREE.Group();
  const s = side === 'left' ? 1 : -1;
  const zc = (ROOF_ZF + ROOF_ZR) / 2 - 40;
  const box = (w, h, d, x, y, z, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w * MM, h * MM, d * MM), mat);
    m.position.set(x * MM, y * MM, z * MM); m.castShadow = true; return m;
  };
  if (t.shape === 'wedge') {
    const L = 1500, W = 1120, H = 200, zf = zc + L / 2, zr = zc - L / 2;
    g.add(box(W, 70, L, 0, base + 35, zc, M.tentShell));                    // base shell on the roof
    if (!open) { g.add(box(W, H - 70, L, 0, base + 70 + (H - 70) / 2, zc, M.tentShell)); return g; }
    const oL = t.open.L, oH = t.open.H, ext = oL - L;                        // rear section runs back over the tailgate
    const zBack = zr - ext;
    // lid: hinged at the front, rear edge lifted to the published open height
    const lid = [[-W / 2, base + 80, zf], [W / 2, base + 80, zf], [W / 2, base + oH, zBack], [-W / 2, base + oH, zBack]];
    g.add(poly(THREE, lid, M.tentShell));
    for (const x of [-W / 2, W / 2])                                          // wedge side walls
      g.add(poly(THREE, [[x, base + 70, zf], [x, base + 70, zBack], [x, base + oH, zBack], [x, base + 80, zf]], M.tentFabric));
    g.add(poly(THREE, [[-W / 2, base + 70, zBack], [W / 2, base + 70, zBack], [W / 2, base + oH, zBack], [-W / 2, base + oH, zBack]], M.tentFabric));
    g.add(box(W, 30, ext, 0, base + 55, zr - ext / 2, M.tentShell));       // extension floor
    for (const x of [-W / 2 + 40, W / 2 - 40])                                // gas struts
      g.add(rod(THREE, [x, base + 90, zr + 200], [x, base + oH - 60, zBack + 150], 18, M.black));
    for (const x of [-W / 2 + 60, W / 2 - 60])                                // props under the extension
      g.add(rod(THREE, [x, base + 40, zBack + 40], [x, base - 380, zr + 40], 22, M.black));
    // telescopic ladder off the side, about 72 degrees
    const lx = s * (W / 2 + 40), topY = base + 60, foot = s * (W / 2 + 40 + (topY - groundY) / Math.tan(72 * Math.PI / 180));
    for (const dz of [-200, 200]) g.add(rod(THREE, [lx, topY, zr + 250 + dz], [foot, groundY, zr + 250 + dz], 28, M.pole));
    for (let k = 1; k < 7; k++) { const t2 = k / 7; g.add(rod(THREE, [lerp(lx, foot, t2), lerp(topY, groundY, t2), zr + 50], [lerp(lx, foot, t2), lerp(topY, groundY, t2), zr + 450], 22, M.pole)); }
    return g;
  }
  if (t.shape === 'foldout') {
    const L = t.open.W, half = t.open.L / 2, H = 330;            // 1300 along the car, 2400 across open
    if (!open) {
      g.add(box(half, H, L, 0, base + H / 2, zc, M.tentShell));
      g.add(box(half + 10, 20, L + 10, 0, base + H - 10, zc, M.black));
      return g;
    }
    const xin = -s * half / 2, xout = s * (half / 2 + half), z0 = zc - L / 2, z1 = zc + L / 2;
    g.add(box(half, 40, L, 0, base + 20, zc, M.tentShell));                                 // the half on the rack
    g.add(box(half, 40, L, s * half, base + 20, zc, M.tentShell));                          // the half flipped out
    const peak = base + 40 + 1200;
    // two hoops over the floor, fabric between them
    const rows = [];
    for (let i = 0; i <= 10; i++) {
      const t2 = i / 10, x = lerp(xin, xout, t2), y = base + 40 + Math.sin(t2 * Math.PI) * 1200;
      rows.push([z0, zc, z1].map(z => [x, y, z]));
    }
    g.add(sheet(THREE, rows, M.tentFabric));
    for (const z of [z0, z1]) g.add(poly(THREE, Array.from({ length: 11 }, (_, i) => {
      const t2 = i / 10; return [lerp(xin, xout, t2), base + 40 + Math.sin(t2 * Math.PI) * 1200, z]; }), M.tentFabric));
    // the flysheet overhang at the outer door, and the ladder that props it
    g.add(poly(THREE, [[xout, base + 700, z0 - 100], [xout, base + 700, z1 + 100], [xout + s * 450, base + 620, z1 + 100], [xout + s * 450, base + 620, z0 - 100]], M.canvasDark));
    const foot = xout + s * (base + 40 - groundY) / Math.tan(70 * Math.PI / 180);
    for (const dz of [-180, 180]) g.add(rod(THREE, [xout, base + 20, zc + dz], [foot, groundY, zc + dz], 30, M.pole));
    for (let k = 1; k < 7; k++) { const t2 = k / 7; const x = lerp(xout, foot, t2), y = lerp(base + 20, groundY, t2); g.add(rod(THREE, [x, y, zc - 180], [x, y, zc + 180], 24, M.pole)); }
    return g;
  }
  // popup
  const L = t.open.L, W = t.open.W, H0 = 300, lift = 1150;
  g.add(box(W, 140, L, 0, base + 70, zc, M.tentShell));
  const lidY = open ? base + 140 + lift : base + H0 - 80;
  g.add(box(W, 160, L, 0, lidY + 80, zc, M.tentShell));
  if (open) {
    const y0 = base + 140, y1 = lidY;
    for (const x of [-W / 2 + 10, W / 2 - 10]) g.add(poly(THREE, [[x, y0, zc - L / 2 + 10], [x, y0, zc + L / 2 - 10], [x, y1, zc + L / 2 - 10], [x, y1, zc - L / 2 + 10]], M.tentFabric));
    for (const z of [zc - L / 2 + 10, zc + L / 2 - 10]) g.add(poly(THREE, [[-W / 2 + 10, y0, z], [W / 2 - 10, y0, z], [W / 2 - 10, y1, z], [-W / 2 + 10, y1, z]], M.tentFabric));
    // side door, rolled up to mesh; ladder under it
    g.add(poly(THREE, [[s * (W / 2 - 6), y0 + 60, zc - 400], [s * (W / 2 - 6), y0 + 60, zc + 400], [s * (W / 2 - 6), y1 - 80, zc + 400], [s * (W / 2 - 6), y1 - 80, zc - 400]], M.mesh));
    const foot = s * (W / 2 + (y0 - groundY) / Math.tan(72 * Math.PI / 180));
    for (const dz of [-200, 200]) g.add(rod(THREE, [s * W / 2, y0, zc + dz], [foot, groundY, zc + dz], 28, M.pole));
    for (const x of [-W / 2 + 60, W / 2 - 60]) for (const z of [zc - L / 2 + 80, zc + L / 2 - 80])
      g.add(rod(THREE, [x, y0 + 20, z], [x, y1 - 20, z], 16, M.black));
  }
  return g;
}

// ------------------------------------------------------- rear / side extras
/** Tailgate pop-up tent (LX-MODE jim817, 2000 x 2000 x 2250, centre 2450)
 *  standing behind the car, its sleeve reaching up to the tailgate; or the
 *  Suzuki car tarp ACAZ (2500 x 2500), one edge on the roof's side edge by
 *  suction cups, the outer edge on two 2200 poles. */
export function campExtra(THREE, e, side, groundY) {
  const M = mats(THREE), g = new THREE.Group();
  const s = side === 'left' ? 1 : -1;
  if (e.shape === 'tailgate') {
    const W = 2000, D = 2000, H = 2250, Hc = 2450, z0 = -1800, z1 = z0 - D;
    const y0 = groundY, y1 = groundY + H, yc = groundY + Hc;
    const walls = [
      [[-W / 2, y0, z1], [W / 2, y0, z1], [W / 2, y1, z1], [-W / 2, y1, z1]],
      [[-W / 2, y0, z0], [-W / 2, y0, z1], [-W / 2, y1, z1], [-W / 2, y1, z0]],
      [[W / 2, y0, z0], [W / 2, y0, z1], [W / 2, y1, z1], [W / 2, y1, z0]],
    ];
    for (const w of walls) g.add(poly(THREE, w, M.tentFabric));
    // four-sided roof up to the centre height
    const c = [0, yc, (z0 + z1) / 2];
    for (const [a, b] of [[[-W / 2, y1, z1], [W / 2, y1, z1]], [[W / 2, y1, z1], [W / 2, y1, z0]], [[W / 2, y1, z0], [-W / 2, y1, z0]], [[-W / 2, y1, z0], [-W / 2, y1, z1]]])
      g.add(poly(THREE, [a, b, c], M.tentFabric));
    // the sleeve that seals against the open tailgate
    g.add(poly(THREE, [[-750, groundY + 450, z0], [750, groundY + 450, z0], [700, 1500, -1690], [-700, 1500, -1690]], M.canvasDark));
    g.add(poly(THREE, [[-W / 2 + 300, y0, z1 - 2], [W / 2 - 300, y0, z1 - 2], [W / 2 - 300, y1 - 250, z1 - 2], [-W / 2 + 300, y1 - 250, z1 - 2]], M.mesh));
    return g;
  }
  // side tarp
  const S = 2500, zc = RACK_ZC, x0 = s * 650, y0 = ROOF_Y - 20, x1 = s * (650 + S * 0.92), y1 = groundY + 2200;
  const rows = [];
  for (let i = 0; i <= 6; i++) { const t2 = i / 6; rows.push([-1, 0, 1].map(k => [lerp(x0, x1, t2), lerp(y0, y1, t2) - Math.sin(t2 * Math.PI) * 70, zc + k * S / 2])); }
  g.add(sheet(THREE, rows, M.tarp));
  for (const k of [-1, 1]) {
    const z = zc + k * S / 2;
    g.add(rod(THREE, [x1, y1 + 80, z], [x1, groundY, z], 25, M.pole));
    g.add(rod(THREE, [x1, y1 + 60, z], [x1 + s * 1100, groundY, z + k * 600], 4, M.rope));
  }
  return g;
}
