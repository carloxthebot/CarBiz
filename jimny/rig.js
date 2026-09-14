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
    const n = o.name || '';
    if (/roda_1_1/.test(n)) { spare.push(o); return; }
    const m = n.match(/roda([1-4])\b/);
    if (m) corners['roda' + m[1]].push(o);
  });

  // Pull each corner into its own group, pivoted on the wheel centre so that
  // scaling changes the tyre's diameter about the hub instead of sliding it.
  const wheelGroups = [];
  for (const key of Object.keys(corners)) {
    const meshes = corners[key];
    if (!meshes.length) continue;
    const g = new THREE.Group(); g.name = key;
    const box = new THREE.Box3();
    for (const m of meshes) box.expandByObject(m);
    const centre = box.getCenter(new THREE.Vector3());
    g.position.copy(centre);
    for (const m of meshes) {
      m.updateMatrixWorld(true);
      const keep = m.matrixWorld.clone();
      g.add(m);
      m.matrix.copy(g.matrixWorld.clone().invert().multiply(keep));
      m.matrix.decompose(m.position, m.quaternion, m.scale);
    }
    WHEELS.add(g);
    const sz = box.getSize(new THREE.Vector3());
    g.userData.baseDia = Math.max(sz.y, sz.z);     // metres
    g.userData.baseCentre = centre.clone();
    wheelGroups.push(g);
  }

  const spareGroup = new THREE.Group(); spareGroup.name = 'spare';
  if (spare.length) {
    const box = new THREE.Box3();
    for (const m of spare) box.expandByObject(m);
    const centre = box.getCenter(new THREE.Vector3());
    spareGroup.position.copy(centre);
    for (const m of spare) {
      m.updateMatrixWorld(true);
      const keep = m.matrixWorld.clone();
      spareGroup.add(m);
      m.matrix.copy(spareGroup.matrixWorld.clone().invert().multiply(keep));
      m.matrix.decompose(m.position, m.quaternion, m.scale);
    }
    BODY.add(spareGroup);                          // the spare rides with the body
    const sz = box.getSize(new THREE.Vector3());
    spareGroup.userData.baseDia = Math.max(sz.y, sz.z);
  }

  // ---- paint: clone so the swatch cannot bleed into other materials -----
  const painted = [];
  raw.traverse((o) => {
    if (o.isMesh && /pintura/i.test(o.material?.name || '')) painted.push(o);
  });
  let paintMat = null;
  if (painted.length) {
    paintMat = painted[0].material.clone();
    paintMat.name = 'BodyPaint';
    paintMat.roughness = 0.45;
    paintMat.metalness = 0.25;
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

  const dims = {
    mmPerUnit,
    lengthM: (full.max.z - full.min.z),
    widthM: (full.max.x - full.min.x),
    heightM: (full.max.y - full.min.y),
  };

  root.userData = {
    BODY, WHEELS, wheelGroups, spareGroup,
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
  if (U.roofMat) {
    const twoTone = !!cfg.twoTone;
    U.roofMat.color.setHex(twoTone ? (cfg.roofColor ?? 0x1e2326) : (cfg.bodyColor ?? 0x6a6866));
    for (const m of U.roofMeshes) m.material = twoTone ? U.roofMat : U.paintMat;
  }

  // tyre diameter: scale each corner about its hub
  const targetDia = (cfg.tyreDia ?? 693) * mm;
  const k = U.baseTyreDia ? targetDia / U.baseTyreDia : 1;
  for (const g of U.wheelGroups) {
    g.scale.setScalar(k);
    // keep the tyre touching the floor: hub height = radius
    g.position.y = targetDia / 2;
    // lift raises the body, which reads the same as dropping the wheels
    g.position.y -= (cfg.lift ?? 0) * mm;
  }
  if (U.spareGroup && U.spareGroup.userData.baseDia) {
    const sk = cfg.spareMatches === false ? 1 : k;
    U.spareGroup.scale.setScalar(sk);
  }

  // body sits at lift height above its rigged rest position
  U.BODY.position.y = (cfg.lift ?? 0) * mm + (targetDia - U.baseTyreDia) / 2;
}
