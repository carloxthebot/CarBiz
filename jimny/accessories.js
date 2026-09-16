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

import { loadFinishes } from './rig.js';

let PARTS = null;

export function loadParts(loader, url, THREE) {
  return new Promise((resolve) => loader.load(url, (g) => {
    PARTS = {};
    // Real surface finishes (Poly Haven, CC0): normal + roughness maps for
    // powder coat / textured plastic (leather grain reads right at this
    // scale), rubber, canvas and PVC. Parts carry box-projected UVs at one
    // repeat per 100 mm; `mm` is the texture's real size so grain stays true.
    const finish = THREE && loadFinishes(THREE);
    const seen = new Set();
    g.scene.traverse((o) => {
      const m = o.material;
      if (!m || seen.has(m)) return;
      seen.add(m);
      if (!finish) return;
      const f = /TextureBlack|PowderBlack|LugNut|RimBarrel/.test(m.name) ? finish.powder
        : /Rubber/.test(m.name) ? finish.rubber
        : /Canvas|Webbing/.test(m.name) ? finish.canvas
        : /AwningPVC/.test(m.name) ? finish.pvc : null;
      // fabric roughness maps read as gloss under the HDR and turned the bags white; keep those matte
      if (f) { m.normalMap = f.nor; if (f !== finish.canvas && f !== finish.pvc) m.roughnessMap = f.rough; m.normalScale.set(f.k, f.k); m.needsUpdate = true; }
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
