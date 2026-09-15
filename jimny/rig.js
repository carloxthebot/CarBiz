// Rig the downloaded Jimny so the configurator can drive it.
//
// The model arrives as 4,873 separate meshes with Portuguese names and no
// hierarchy worth the name — everything is a sibling. Three things have to be
// recovered before any of it is controllable:
//
//   1. SCALE.    The file is in arbitrary units. The car is 3550mm long, so the
//                longest bound gives the conversion and every later number can
//                be written in millimetres like the rest of the project.
//   2. WHEELS.   Meshes whose name contains roda1..roda4 are the four corners;
//                roda_1_1 is the tailgate spare. They get pulled into their own
//                groups so tyre diameter can scale them and lift can drop them.
//   3. PAINT.    Carro_Pintura is the body colour. It is shared by many meshes,
//                so it gets cloned once and swapped in — mutating the original
//                would also tint anything else that happens to reference it.
//
// Lift is applied by moving the WHEELS DOWN rather than the body up. Same
// visual result, but it leaves the body at the origin so accessory positions
// stay in one frame of reference.

export const MODEL_SCALE_TARGET = 3550;   // mm, JB74 overall length

/** Tileable grain for textured plastic and powder coat. `size` is the feature
 *  size in texture pixels; the map repeats every ~10 cm of surface. */
export function noiseBump(THREE, size = 6, repeat = 10) {
  const N = 256, c = document.createElement('canvas'); c.width = c.height = N;
  const ctx = c.getContext('2d'), img = ctx.createImageData(N, N), d = img.data;
  const cells = Math.max(2, Math.round(N / size)), grid = new Float32Array(cells * cells);
  let seed = 7;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < grid.length; i++) grid[i] = rnd();
  const at = (x, y) => grid[((y % cells) + cells) % cells * cells + ((x % cells) + cells) % cells];
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const gx = x / size, gy = y / size, x0 = Math.floor(gx), y0 = Math.floor(gy);
    const tx = gx - x0, ty = gy - y0, sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
    const v = (at(x0, y0) * (1 - sx) + at(x0 + 1, y0) * sx) * (1 - sy) + (at(x0, y0 + 1) * (1 - sx) + at(x0 + 1, y0 + 1) * sx) * sy;
    const g = Math.round(90 + v * 80 + (rnd() - 0.5) * 24);
    const i = (y * N + x) * 4; d[i] = d[i + 1] = d[i + 2] = g; d[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat, repeat);
  return t;
}

export function rigJimny(THREE, gltfScene) {
  const root = new THREE.Group();
  root.name = 'jimny-rig';

  const raw = gltfScene;
  const bb0 = new THREE.Box3().setFromObject(raw);
  const size0 = bb0.getSize(new THREE.Vector3());
  const longest = Math.max(size0.x, size0.y, size0.z);
  const mmPerUnit = MODEL_SCALE_TARGET / longest;
  const s = mmPerUnit * 0.001;              // model units -> metres

  raw.scale.setScalar(s);
  raw.updateMatrixWorld(true);

  // re-measure in metres and sit the car on the floor, centred
  const bb = new THREE.Box3().setFromObject(raw);
  const c = bb.getCenter(new THREE.Vector3());
  raw.position.x -= c.x;
  raw.position.z -= c.z;
  raw.position.y -= bb.min.y;
  raw.updateMatrixWorld(true);

  const BODY = new THREE.Group(); BODY.name = 'body';
  const WHEELS = new THREE.Group(); WHEELS.name = 'wheels';
  root.add(BODY, WHEELS);
  BODY.add(raw);

  // ---- find the wheels ---------------------------------------------------
  const corners = { roda1: [], roda2: [], roda3: [], roda4: [] };
  const spare = [];
  raw.traverse((o) => {
    if (!o.isMesh) return;
    // GLTFLoader sanitises node names (whitespace -> '_'), so the file's
    // "roda_1_2 roda1" arrives as "roda_1_2_roda1". A \b after the digit never
    // matches before '_' — that silently found zero wheels, left them inside
    // the body, and made every lift and tyre change float the whole car.
    const n = o.name || '';
    if (/roda_1_1(?!\d)/.test(n)) { spare.push(o); return; }
    const m = n.match(/roda([1-4])(?!\d)/);
    if (m) corners['roda' + m[1]].push(o);
  });

  // Pull each corner into its own group, pivoted on the wheel centre, so the
  // wheel can be placed on the ground independently of the body.
  const wheelGroups = [];
  root.updateMatrixWorld(true);
  for (const key of Object.keys(corners)) {
    const meshes = corners[key];
    if (!meshes.length) continue;
    const g = new THREE.Group(); g.name = key;
    const box = new THREE.Box3();
    for (const m of meshes) box.expandByObject(m);
    const centre = box.getCenter(new THREE.Vector3());
    g.position.copy(centre);
    WHEELS.add(g);
    g.updateMatrixWorld(true);
    // attach() keeps each mesh's world transform while reparenting
    for (const m of meshes) g.attach(m);
    const sz = box.getSize(new THREE.Vector3());
    g.userData.baseDia = Math.max(sz.y, sz.z);     // metres
    g.userData.baseCentre = centre.clone();
    wheelGroups.push(g);
  }

  // The model already carries a tailgate-mounted spare. Earlier this code
  // reparented it to scale with the road tyres, and the transform maths threw
  // it off the car. It is left exactly where the artist put it; only its
  // measured position is exported, so a spare-wheel bag can be placed on it.
  let spareBox = null;
  if (spare.length) {
    spareBox = new THREE.Box3();
    for (const m of spare) spareBox.expandByObject(m);
  }

  // ---- paint: clone so the swatch cannot bleed into other materials -----
  const painted = [];
  raw.traverse((o) => {
    if (o.isMesh && /pintura/i.test(o.material?.name || '')) painted.push(o);
  });
  let paintMat = null;
  if (painted.length) {
    // car paint is a colour coat under clear lacquer; the clearcoat layer is
    // what gives the sharp reflection on top of a soft base
    paintMat = new THREE.MeshPhysicalMaterial({ name: 'BodyPaint', color: 0x6a6866, roughness: 0.42, metalness: 0.15,
      clearcoat: 1.0, clearcoatRoughness: 0.06 });
    for (const m of painted) m.material = paintMat;
  }

  // ---- roof, for two-tone: painted meshes in the top fifth of the car ----
  const roofMeshes = [];
  const full = new THREE.Box3().setFromObject(raw);
  const roofLine = full.min.y + (full.max.y - full.min.y) * 0.78;
  for (const m of painted) {
    const b = new THREE.Box3().setFromObject(m);
    if (b.min.y > roofLine) roofMeshes.push(m);
  }
  let roofMat = null;
  if (roofMeshes.length && paintMat) {
    roofMat = paintMat.clone();
    roofMat.name = 'RoofPaint';
  }

  // ---- anchors, MEASURED ------------------------------------------------
  // Accessories were previously positioned from hand-guessed constants copied
  // off an earlier hand-built model. On this mesh those numbers put the roof
  // rack in mid-air and drove the snorkel through the floor. Everything below
  // is measured off the actual geometry instead, in millimetres.
  const M = 1000;                                  // metres -> mm
  const paintedBox = new THREE.Box3();
  for (const m of painted) paintedBox.expandByObject(m);

  // roof: the top of the painted shell, ignoring the aerial
  let roofY = -Infinity, roofXHalf = 0, roofZMin = Infinity, roofZMax = -Infinity;
  for (const m of painted) {
    const b = new THREE.Box3().setFromObject(m);
    if (b.max.y > paintedBox.min.y + (paintedBox.max.y - paintedBox.min.y) * 0.80) {
      const w = Math.max(Math.abs(b.min.x), Math.abs(b.max.x));
      if (b.max.x - b.min.x > 0.4) {              // a real roof panel, not a trim strip
        roofY = Math.max(roofY, b.max.y);
        roofXHalf = Math.max(roofXHalf, w);
        roofZMin = Math.min(roofZMin, b.min.z);
        roofZMax = Math.max(roofZMax, b.max.z);
      }
    }
  }
  if (!isFinite(roofY)) { roofY = paintedBox.max.y; roofXHalf = paintedBox.max.x; }

  // body sides at door height (half-way up the painted shell)
  const midY = (paintedBox.min.y + paintedBox.max.y) / 2;
  let sideXHalf = 0;
  for (const m of painted) {
    const b = new THREE.Box3().setFromObject(m);
    if (b.min.y < midY && b.max.y > midY)
      sideXHalf = Math.max(sideXHalf, Math.abs(b.min.x), Math.abs(b.max.x));
  }
  if (!sideXHalf) sideXHalf = paintedBox.max.x;

  const wheelZ = wheelGroups.map((g) => g.position.z);
  const frontAxleZ = Math.max(...wheelZ), rearAxleZ = Math.min(...wheelZ);

  const anchors = {
    bodyW: sideXHalf * 2 * M,
    halfW: sideXHalf * M,
    roofY: roofY * M,
    roofZFront: roofZMax * M,
    roofZRear: roofZMin * M,
    roofHalfW: roofXHalf * M,
    noseZ: paintedBox.max.z * M,
    tailZ: paintedBox.min.z * M,
    sillY: paintedBox.min.y * M,
    beltY: (paintedBox.min.y + (paintedBox.max.y - paintedBox.min.y) * 0.56) * M,
    frontAxleZ: frontAxleZ * M,
    rearAxleZ: rearAxleZ * M,
    spare: spareBox ? {
      x: (spareBox.min.x + spareBox.max.x) / 2 * M,
      y: (spareBox.min.y + spareBox.max.y) / 2 * M,
      z: (spareBox.min.z + spareBox.max.z) / 2 * M,
      dia: Math.max(spareBox.max.y - spareBox.min.y, spareBox.max.x - spareBox.min.x) * M,
    } : null,
  };
  anchors.glassY = anchors.beltY + (anchors.roofY - anchors.beltY) * 0.45;
  anchors.glassH = (anchors.roofY - anchors.beltY) * 0.62;
  anchors.grilleY = anchors.beltY - (anchors.beltY - anchors.sillY) * 0.30;
  anchors.bumperY = anchors.sillY + (anchors.beltY - anchors.sillY) * 0.22;
  anchors.beltline = anchors.beltY;          // accessories use this name

  // ---- trim: give the exported greys their real finishes ------------------
  // The OBJ export flattened every material to a mid grey, so the bumper,
  // grille surround and flares read as primer, the Suzuki "S" as dull plastic
  // and the headlamps as empty black holes. JB74 facts: textured black bumper,
  // grille and arches; chrome badge; chrome reflector bowls behind clear lenses.
  // Runs AFTER the anchors so re-painting the roof panel cannot move the rack.
  const grain = noiseBump(THREE, 6);
  const TRIM = {
    black: new THREE.MeshStandardMaterial({ name: 'TrimBlack', color: 0x1a1b1d, roughness: 0.78, metalness: 0,
      bumpMap: grain, bumpScale: 0.6 }),
    glass: new THREE.MeshPhysicalMaterial({ name: 'Glass', color: 0x0b0f12, roughness: 0.04, metalness: 0,
      transparent: true, opacity: 0.6 }),
    satin: new THREE.MeshStandardMaterial({ name: 'TrimSatin', color: 0x161719, roughness: 0.5, metalness: 0.1 }),
    chrome: new THREE.MeshStandardMaterial({ name: 'Chrome', color: 0xe2e5e8, roughness: 0.14, metalness: 1 }),
    // lamp lenses were 40% black glass, which hid the chrome bowl and reflector
    // the model already has behind them; clear glass lets those show
    lens: new THREE.MeshStandardMaterial({ name: 'LampLens', color: 0xffffff, roughness: 0.05, metalness: 0,
      transparent: true, opacity: 0.12, depthWrite: false }),
  };
  TRIM.blackFlat = TRIM.black.clone(); TRIM.blackFlat.bumpMap = null; TRIM.blackFlat.name = 'TrimBlackFlat';
  const byName = {
    Carro_Plastico: TRIM.black,          // flares, mirrors, sills, lower grille mesh
    Carro_Interno_1: TRIM.satin,         // grille surround (+ cabin trim)
    Carro_Metal_Preto_1: TRIM.black,     // bumper, grille slats
    Carro_Metal_Farol: TRIM.chrome,      // badge, lamp rings
  };
  const lampZ = frontAxleZ + 0.3;         // lenses ahead of this are head/fog lamps
  raw.traverse((o) => {
    if (!o.isMesh || Array.isArray(o.material)) return;
    const name = o.material.name || '';
    if (name === 'Carro_Metal_Preto_1') {
      // the roof skin shares the bumper's material but is body-coloured on a JB74
      const b = new THREE.Box3().setFromObject(o);
      if (b.min.y > roofLine && b.max.x - b.min.x > 0.4 && paintMat) {
        o.material = paintMat; painted.push(o); roofMeshes.push(o); return;
      }
    }
    if (name === 'Carro_Vidros') {
      const b = new THREE.Box3().setFromObject(o);
      if (b.min.z > lampZ && b.max.y < roofLine * 0.75) o.material = TRIM.lens;
      else o.material = TRIM.glass;
      return;
    }
    if (byName[name]) {
      // bump maps need texture coordinates; the export only has them on some meshes
      o.material = byName[name] === TRIM.black && !o.geometry.attributes.uv ? TRIM.blackFlat : byName[name];
    }
  });
  // the roof skin only joins roofMeshes here, so two-tone had no roof to paint
  if (!roofMat && roofMeshes.length && paintMat) {
    roofMat = paintMat.clone();
    roofMat.name = 'RoofPaint';
  }

  // ---- stock front bumper and grille, so aftermarket ones can replace them
  // Bumper: everything black ahead of the axle and below the bonnet line,
  // plus the fog lamps set into it. Grille: the satin surround panel, its
  // slats and inserts, the signal bezels and the badge. Headlamp units stay.
  const stockBumper = [], stockGrille = [], stockRear = [], stockMirrors = [];
  raw.traverse((o) => {
    if (!o.isMesh || Array.isArray(o.material)) return;
    const b = new THREE.Box3().setFromObject(o);
    const c = b.getCenter(new THREE.Vector3()).multiplyScalar(1000);
    const n = o.material.name;
    // rear bumper: the one big satin shell under the tailgate; the tail lamps set into it stay
    if (c.z < -1400 && c.y < 650 && n === 'TrimSatin' && (b.max.x - b.min.x) > 1.0) { stockRear.push(o); return; }
    // door mirrors: the glass and its two housing shells outboard of the door skin
    if (Math.abs(c.x) > 780 && c.y > 1050 && c.y < 1300 && c.z > 350 && c.z < 550 && /Espelhos|^TrimBlack/.test(n)) { stockMirrors.push(o); return; }
    if (c.z < 1500) return;
    // (TrimBlackFlat is the same finish on meshes without UVs)
    if (c.y < 720 && c.z > 1550 && (/^TrimBlack/.test(n) || (c.y < 650 && /Chrome|LampLens|Carro_Ref/.test(n))))
      stockBumper.push(o);
    else if (c.y >= 740 && c.y < 1000 && (n === 'TrimSatin' || (/^TrimBlack/.test(n) && c.z > 1560) ||
      (n === 'Chrome' && Math.abs(c.x) < 100)))
      stockGrille.push(o);
  });

  const dims = {
    mmPerUnit,
    lengthMM: (full.max.z - full.min.z) * M,
    widthMM: (full.max.x - full.min.x) * M,
    heightMM: (full.max.y - full.min.y) * M,
  };

  root.userData = {
    BODY, WHEELS, wheelGroups, spareBox, spare, anchors, stockBumper, stockGrille, stockRear, stockMirrors,
    paintMat, roofMat, roofMeshes, painted, dims,
    baseTyreDia: wheelGroups[0]?.userData.baseDia ?? 0.693,
  };
  return root;
}

/** Apply a configuration to a rigged model. Pure geometry — no UI here. */
export function applyConfig(THREE, rig, cfg) {
  const U = rig.userData;
  const mm = 0.001;

  if (U.paintMat && cfg.bodyColor != null) U.paintMat.color.setHex(cfg.bodyColor);
  for (const m of U.stockBumper) m.visible = !cfg.hideBumper;
  for (const m of U.stockGrille) m.visible = !cfg.hideGrille;
  for (const m of U.stockRear) m.visible = !cfg.hideRear;
  for (const m of U.stockMirrors) m.visible = !cfg.hideMirrors;
  if (U.roofMat) {
    const twoTone = !!cfg.twoTone;
    U.roofMat.color.setHex(twoTone ? (cfg.roofColor ?? 0x1e2326) : (cfg.bodyColor ?? 0x6a6866));
    for (const m of U.roofMeshes) m.material = twoTone ? U.roofMat : U.paintMat;
  }

  // Wheels. The model's own are hidden and a built wheel takes each place, so
  // the rim you chose is the rim you see, and fitting a taller tyre grows the
  // SIDEWALL instead of scaling a 15" rim into a 17" one.
  //
  // Heights, ground at y = 0:
  //   wheel centre = tyre radius                (the tyre is always on the ground)
  //   body         = rest + lift + half the tyre's growth
  // An earlier version also pushed the wheels DOWN by the lift while raising
  // the body, applying it twice and leaving the tyres hanging in mid-air.
  const targetDia = (cfg.tyreDia ?? 693) * mm;

  if (cfg.buildWheel) {
    for (const w of U.builtWheels ?? []) w.parent?.remove(w);
    U.builtWheels = [];
    for (const g of U.wheelGroups) {
      g.visible = false;                       // reference geometry only
      const w = cfg.buildWheel({
        rimDia: cfg.rimDia ?? 15, tyreDia: cfg.tyreDia ?? 693,
        width: cfg.tyreWidth ?? 195, style: cfg.wheelStyle ?? 'stock',
        tread: cfg.tread ?? 'at', rimColor: cfg.rimColor ?? 0xc8ccd0,
      });
      const side = Math.sign(g.position.x) || 1;
      // turn, don't mirror: a mirrored wheel reads its sidewall lettering backwards
      w.rotation.y = side < 0 ? Math.PI : 0;
      w.position.set(g.position.x + side * (cfg.spacer ?? 0) * mm, targetDia / 2, g.position.z);
      w.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      U.WHEELS.add(w);
      U.builtWheels.push(w);
    }
    // the tailgate spare matches the road wheels: the model's own is hidden
    // and a built one hung in its place, face to the rear
    if (U.spareBox) {
      for (const m of U.spare) m.visible = false;
      const w = cfg.buildWheel({
        rimDia: cfg.rimDia ?? 15, tyreDia: cfg.tyreDia ?? 693,
        width: cfg.tyreWidth ?? 195, style: cfg.wheelStyle ?? 'stock',
        tread: cfg.tread ?? 'at', rimColor: cfg.rimColor ?? 0xc8ccd0,
      });
      const c = U.spareBox.getCenter(new THREE.Vector3());
      const spareDia = U.spareBox.max.y - U.spareBox.min.y;
      w.rotation.y = -Math.PI / 2;               // axle along Z, face towards -Z
      w.position.set(c.x, c.y + (targetDia - spareDia) * 0.25, c.z + (cfg.tyreWidth ?? 195) * 0.92 * mm / 2 - (U.spareBox.max.z - U.spareBox.min.z) / 2);
      w.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      U.BODY.add(w);
      U.builtWheels.push(w);
    }
  } else {
    for (const g of U.wheelGroups) { g.visible = true; g.position.y = targetDia / 2; }
  }

  U.BODY.position.y = (cfg.lift ?? 0) * mm + (targetDia - U.baseTyreDia) / 2;
}
