// Bolt-on accessories.
//
// Every part is a real mesh built by blender/build_parts.py to the dimensions
// of a named product (Front Runner Slimline II rack, Safari-style snorkel,
// Front Runner ladder, ARB sliders and awning, IPF light bar, Suzuki hard
// spare cover), shaped against a raycast sample of this car's body, and
// exported into model/parts.glb already positioned in the car frame. The page
// only clones the node it needs. An earlier version generated boxes in code
// and did not look like accessories at all.
//
// To change a part: edit build_parts.py, run it with Blender, then run
// `npx gltf-transform draco model/parts.glb model/parts.glb`.

import { noiseBump } from './rig.js';

let PARTS = null;

export function loadParts(loader, url, THREE) {
  return new Promise((resolve) => loader.load(url, (g) => {
    PARTS = {};
    // powder coat and textured plastic are not smooth; the exporter's flat
    // colours get a tileable grain (parts carry box-projected UVs for it)
    const grain = THREE && noiseBump(THREE, 5, 12);
    const seen = new Set();
    g.scene.traverse((o) => {
      const m = o.material;
      if (!m || seen.has(m)) return;
      seen.add(m);
      if (grain && /TextureBlack|PowderBlack|Canvas|AwningPVC|Rubber|Webbing/.test(m.name)) {
        m.bumpMap = grain; m.bumpScale = /Canvas|Webbing/.test(m.name) ? 1.2 : 0.5; m.needsUpdate = true;
      }
      if (m.name === 'BodyPaint') return;                 // swapped per clone
    });
    for (const o of g.scene.children) PARTS[o.name] = o;
    resolve(PARTS);
  }, undefined, () => resolve(null)));
}

// Parts painted body colour (KLC's ivory bumper and grille) carry a material
// named BodyPaint; it is swapped for the car's own paint so the swatch applies.
export const getPart = (name) => PARTS?.[name] ?? null;

export function buildAccessory(kind, variant, paintMat) {
  const node = PARTS?.[variant ? `${kind}_${variant}` : kind];
  if (!node) return null;
  const n = node.clone(true);
  n.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = true; o.receiveShadow = true;
    if (paintMat && o.material?.name === 'BodyPaint') o.material = paintMat;
  });
  return n;
}
