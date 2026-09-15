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
//   tread            — { pattern: at | rt | mt, brand, model, owl } or 'at' / 'mt'
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

  const rim = mat(THREE, rimColor, { rough: 0.38, metal: 0.72 });
  const hubMat = mat(THREE, 0x202328, { rough: 0.7, metal: 0.3 });

  const cyl = (r1, r2, h, seg, m, x = 0) => {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(r1 * MM, r2 * MM, h * MM, seg), m);
    c.rotation.z = Math.PI / 2; c.position.x = x * MM;
    c.castShadow = c.receiveShadow = true; return c;
  };

  g.add(buildTyre(THREE, { tR, rR, half: W / 2, sidewall, width, tread }));

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

// ============================================================ TYRE ==========
// One parametric surface: the cross-section (bead -> sidewall -> shoulder ->
// tread -> back) revolved around the axle, with every vertex pushed INWARD by
// the tread pattern's groove depth at that spot. Blocks are therefore real
// geometry, and A/T, R/T and M/T differ the way the tyres do: block size,
// void width and how far the shoulder lugs wrap down the sidewall. The same
// pattern function also paints the colour map, so groove floors read dark and
// sipes (too fine to model) are drawn on top. Sidewall lettering is a canvas
// texture with a bump map, white or embossed black.
//
// Coordinates inside a pattern: u = mm around the circumference (wraps at the
// tyre's true circumference, so the pitch count is always a whole number),
// v = mm across the section from the tread centre, positive towards the outer
// face. `tw` is tread width, `shArc` the length of the rounded shoulder.

const smooth = (d, e) => d <= -e ? 1 : d >= e ? 0 : 0.5 - d / (2 * e);   // 1 inside
const wrap = (u, P) => ((u % P) + P) % P;
const tri = (u, P) => 1 - 4 * Math.abs(wrap(u, P) / P - 0.5);            // -1..1
// lateral groove: width w, repeating every P, leaning by `slope` mm per mm of v
const lateral = (u, v, P, phase, w, slope, vmid, e) =>
  smooth(Math.abs(wrap(u - phase - slope * (v - vmid) + P / 2, P) - P / 2) - w / 2, e);
// circumferential groove around v = vc, zig-zagging by amp every `period`
const circG = (u, v, vc, w, amp, period, e) => smooth(Math.abs(v - vc - amp * tri(u, period)) - w / 2, e);
const band = (v, a, b, e) => smooth(Math.max(a - v, v - b), e);           // 1 inside [a, b]

const PATTERNS = {
  // 5-rib all-terrain (KO2 / Open Country A/T III): narrow zig-zag grooves,
  // small blocks, heavy siping, shoulder blocks just over the edge.
  at(tw, circ, shArc) {
    const n = Math.round(circ / 42), P = circ / n, e = 1.4, half = tw / 2;
    const g1 = tw * 0.13, g2 = tw * 0.37;
    return {
      P, depth: 13, sideScale: 0.5,
      g(u, v) {
        const av = Math.abs(v), sg = v < 0 ? -1 : 1;
        let g = Math.max(circG(u, av, g1, 10, 4, 2 * P, e), circG(u, av, g2, 11, 4, 2 * P, e));
        g = Math.max(g, Math.min(lateral(u, v, P, 0, 8, 0.6, 0, e), band(av, -1e9, g1 - 2, e)));   // rib spans v = 0
        g = Math.max(g, Math.min(lateral(u, av, P, sg > 0 ? P * 0.5 : P * 0.25, 9, -sg * 0.5, (g1 + g2) / 2, e),
          band(av, g1, g2, e)));
        g = Math.max(g, Math.min(lateral(u, av, P, sg > 0 ? P * 0.15 : P * 0.65, 13, sg * 0.25, half, e),
          band(av, g2, half + shArc + 6, e)));
        return g;
      },
      sipe(u, v) {
        const av = Math.abs(v), sg = v < 0 ? -1 : 1;
        return Math.min(lateral(u, av, P / 3, sg > 0 ? 6 : 13, 1.2, sg * 0.3, av, 0.5), band(av, 0, half - 2, e));
      },
    };
  },
  // hybrid / rugged-terrain (Open Country R/T, Ridge Grappler): two staggered
  // centre rows, wider voids than an A/T, alternating long and short shoulder
  // lugs that reach a little way down the sidewall.
  rt(tw, circ, shArc) {
    const n = Math.round(circ / 52), P = circ / n, e = 1.6, half = tw / 2;
    const rowIn = tw * 0.03, rowOut = tw * 0.25, voidC = tw * 0.31;
    return {
      P, depth: 14, sideScale: 0.55,
      g(u, v) {
        const av = Math.abs(v), sg = v < 0 ? -1 : 1;
        let g = circG(u, v, 0, 10, 5, P, e);
        g = Math.max(g, circG(u, av, voidC, tw * 0.09, 6, P, e));
        g = Math.max(g, Math.min(lateral(u, av, P, sg > 0 ? 0 : P / 2, P * 0.30, sg * 0.35, (rowIn + rowOut) / 2, e),
          band(av, rowIn - 2, rowOut + 2, e)));
        const phase = sg > 0 ? P * 0.25 : P * 0.75;
        g = Math.max(g, Math.min(lateral(u, av, P, phase, P * 0.36, sg * 0.15, half, e), band(av, tw * 0.36, 1e9, e)));
        const sd = av - (half + shArc);
        if (sd > 0) { const k = Math.floor(wrap(u - phase, 2 * P) / P); g = Math.max(g, smooth((k ? 6 : 16) - sd, 2.5)); }
        return g;
      },
      sipe(u, v) {
        const av = Math.abs(v), sg = v < 0 ? -1 : 1;
        return Math.min(lateral(u, av, P / 4, sg > 0 ? 4 : 9, 1.1, sg * 0.25, av, 0.5), band(av, rowIn, rowOut, e));
      },
    };
  },
  // mud-terrain (Open Country M/T, KM3): three ribs, huge blocks, wide open
  // voids, scalloped shoulder lugs wrapping well down the sidewall.
  mt(tw, circ, shArc) {
    const n = Math.round(circ / 68), P = circ / n, e = 1.8, half = tw / 2;
    const rowIn = tw * 0.03, rowOut = tw * 0.24, voidC = tw * 0.31;
    return {
      P, depth: 17, sideScale: 0.55,
      g(u, v) {
        const av = Math.abs(v), sg = v < 0 ? -1 : 1;
        let g = circG(u, v, 0, 9, 5, P, e);
        g = Math.max(g, circG(u, av, voidC, tw * 0.12, 7, P, e));
        g = Math.max(g, Math.min(lateral(u, av, P, sg > 0 ? 0 : P / 2, P * 0.36, sg * 0.35, (rowIn + rowOut) / 2, e),
          band(av, rowIn - 2, rowOut + 2, e)));
        const phase = sg > 0 ? P * 0.25 : P * 0.75;
        g = Math.max(g, Math.min(lateral(u, av, P, phase, P * 0.42, sg * 0.15, half, e), band(av, tw * 0.37, 1e9, e)));
        const sd = av - (half + shArc);
        if (sd > 0) { const k = Math.floor(wrap(u - phase, 2 * P) / P); g = Math.max(g, smooth((k ? 8 : 24) - sd, 3)); }
        return g;
      },
      sipe() { return 0; },
    };
  },
};

const TEX_CACHE = new Map();

function tyreProfile(tR, rR, half, sidewall) {
  const sh = Math.min(sidewall * 0.12, 24);              // shoulder radius: LT tyres have a wide, flat crown
  const bulge = half * 0.12;
  const pts = [];
  const push = (r, x) => pts.push({ r, x });
  const br = rR + sidewall * 0.45, bx = half + bulge;    // bulge point (mirrored later)
  // inner side, bead outward
  push(rR, -half * 0.86);
  for (let i = 1; i <= 4; i++) push(rR + (br - rR) * i / 4, -half * 0.86 - (bx - half * 0.86) * i / 4);
  for (let i = 1; i <= 5; i++) push(br + (tR - sh - br) * i / 5, -bx + (bx - half) * i / 5);
  for (let i = 1; i <= 8; i++) { const a = Math.PI / 2 * i / 8; push(tR - sh + Math.sin(a) * sh, -half + sh - Math.cos(a) * sh); }
  const tw = 2 * (half - sh), N = Math.max(30, Math.round(tw / 3.5));   // ~3.5 mm across, so 10 mm grooves survive
  for (let i = 1; i <= N; i++) push(tR, -half + sh + tw * i / N);
  const m = pts.length;                                   // mirror, skipping the last (centre-symmetric) point
  for (let i = m - 2; i >= 0; i--) push(pts[i].r, -pts[i].x);
  let s = 0;
  for (let i = 0; i < pts.length; i++) {
    if (i) s += Math.hypot(pts[i].r - pts[i - 1].r, pts[i].x - pts[i - 1].x);
    pts[i].s = s;
  }
  for (let i = 0; i < pts.length; i++) {                  // outward normal of the polyline
    const a = pts[Math.max(i - 1, 0)], b = pts[Math.min(i + 1, pts.length - 1)];
    const tr = b.r - a.r, tx = b.x - a.x, l = Math.hypot(tr, tx) || 1;
    pts[i].nr = tx / l; pts[i].nx = -tr / l;
  }
  return { pts, L: s, tw, shArc: sh * Math.PI / 2, sh };
}

function tyreTexture(THREE, key, { circ, L, tw, shArc, pat, brand, model, owl }) {
  if (TEX_CACHE.has(key)) return TEX_CACHE.get(key);
  const W = 2048, H = Math.round(W * L / circ), mmpx = circ / W;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const bump = document.createElement('canvas'); bump.width = W; bump.height = H;
  const c = cv.getContext('2d'), b = bump.getContext('2d');
  c.fillStyle = '#1e2023'; c.fillRect(0, 0, W, H);
  b.fillStyle = '#808080'; b.fillRect(0, 0, W, H);
  // tread band: groove floors dark, sipes as fine dark lines
  const img = c.getImageData(0, 0, W, H), d = img.data;
  const y0 = Math.max(0, Math.floor((L / 2 - tw / 2 - shArc - 26) / mmpx)), y1 = Math.min(H, Math.ceil((L / 2 + tw / 2 + shArc + 26) / mmpx));
  for (let y = y0; y < y1; y++) {
    const v = y * mmpx - L / 2;
    for (let x = 0; x < W; x++) {
      const u = x * mmpx;
      const g = pat.g(u, v), sp = pat.sipe(u, v);
      const k = 1 - 0.55 * g - 0.5 * sp;
      const i = (y * W + x) * 4;
      d[i] = 30 * k + 4; d[i + 1] = 32 * k + 4; d[i + 2] = 35 * k + 4;
    }
  }
  c.putImageData(img, 0, 0);
  // outer sidewall lettering: outer face is the high-s end
  const sideTop = (L / 2 + tw / 2 + shArc + 6) / mmpx, sideBot = H;
  const bandH = sideBot - sideTop;
  const yText = sideTop + bandH * 0.62;
  // four words spaced a quarter turn apart, each shrunk to fit its slot
  const draw = (ctx, fill) => {
    ctx.fillStyle = fill; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (const [t, at, big] of [[brand, 0.0, true], [model, 0.25, false], [brand, 0.5, true], [model, 0.75, false]]) {
      let fs = Math.round(bandH * (big ? 0.30 : 0.24));
      const font = (n) => `${big ? '900' : '700'} ${n}px "Helvetica Neue", Arial, sans-serif`;
      ctx.font = font(fs);
      const w = ctx.measureText(t).width;
      if (w > W * 0.20) { fs = Math.floor(fs * W * 0.20 / w); ctx.font = font(fs); }
      ctx.fillText(t, W * (at + 0.125), yText);
    }
  };
  draw(c, owl ? '#ece9dd' : '#2b2d31');
  draw(b, '#ffffff');
  const map = new THREE.CanvasTexture(cv), bmap = new THREE.CanvasTexture(bump);
  for (const t of [map, bmap]) { t.flipY = false; t.wrapS = THREE.RepeatWrapping; t.anisotropy = 8; }
  map.colorSpace = THREE.SRGBColorSpace;
  const out = { map, bmap };
  TEX_CACHE.set(key, out);
  return out;
}

export function buildTyre(THREE, { tR, rR, half, sidewall, width, tread }) {
  const spec = typeof tread === 'string' ? { pattern: tread } : (tread || {});
  const pattern = PATTERNS[spec.pattern] ? spec.pattern : 'at';
  const brand = spec.brand ?? 'TOYO TIRES', model = spec.model ?? 'OPEN COUNTRY A/T III', owl = !!spec.owl;
  const { pts, L, tw, shArc } = tyreProfile(tR, rR, half, sidewall);
  const circ = 2 * Math.PI * tR;
  const pat = PATTERNS[pattern](tw, circ, shArc);
  const N = Math.max(360, Math.round(circ / 3.5));        // ~3.5 mm around
  const M = pts.length;
  const pos = new Float32Array((N + 1) * M * 3), uv = new Float32Array((N + 1) * M * 2);
  for (let i = 0; i <= N; i++) {
    const th = 2 * Math.PI * i / N, u = (i % N) / N * circ;
    for (let j = 0; j < M; j++) {
      const p = pts[j];
      const v = p.s - L / 2, av = Math.abs(v);
      const side = av > tw / 2 + shArc;
      const d = pat.depth * pat.g(u, v) * (side ? pat.sideScale : 1);
      const r = p.r - d * p.nr, x = p.x - d * p.nx;
      const k = (i * M + j);
      pos[k * 3] = x * MM; pos[k * 3 + 1] = r * Math.sin(th) * MM; pos[k * 3 + 2] = r * Math.cos(th) * MM;
      uv[k * 2] = i / N; uv[k * 2 + 1] = p.s / L;
    }
  }
  const idx = [];
  for (let i = 0; i < N; i++) for (let j = 0; j < M - 1; j++) {
    const a = i * M + j, b = a + M;
    idx.push(a, a + 1, b, a + 1, b + 1, b);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  const key = [pattern, brand, model, owl, Math.round(tR), Math.round(rR), Math.round(width)].join('|');
  const { map, bmap } = tyreTexture(THREE, key, { circ, L, tw, shArc, pat, brand, model, owl });
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    map, bumpMap: bmap, bumpScale: 0.0025, roughness: 0.93, metalness: 0 }));
  m.castShadow = m.receiveShadow = true;
  m.name = 'tyre';
  return m;
}
