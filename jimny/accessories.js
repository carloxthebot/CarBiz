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

let PARTS = null;

export function loadParts(loader, url) {
  return new Promise((resolve) => loader.load(url, (g) => {
    PARTS = {};
    for (const o of g.scene.children) PARTS[o.name] = o;
    resolve(PARTS);
  }, undefined, () => resolve(null)));
}

export function buildAccessory(kind, variant) {
  const node = PARTS?.[variant ? `${kind}_${variant}` : kind];
  if (!node) return null;
  const n = node.clone(true);
  n.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return n;
}
