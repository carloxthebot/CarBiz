"""Measure every part in parts.glb and check it against the spec table.

The builders place parts by hand-typed millimetres, so a bad number lands
silently: the part is simply in the wrong place, and nobody notices until
it shows up in a render. This reads the EXPORTED file -- the thing the page
actually loads -- and prints each part group's bounding box in car
coordinates (+Y up, +Z forward, +X vehicle left), then compares it against
tools/calib/specs.json where an entry exists.

    Blender -b --factory-startup -P spec_gate.py -- [glb] [specs.json]

A part that violates its spec makes the script exit 1, so it can gate a
build. Parts with no spec entry are only listed.
"""
import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
# the wheels ship in their own file so the page can draw the car sooner, so
# the gate has to read both or it silently stops checking the rims
GLBS = argv[:1] if argv else [os.path.join(ROOT, 'model', 'parts.glb'),
                              os.path.join(ROOT, 'model', 'rims.glb')]
SPECS = argv[1] if len(argv) > 1 else os.path.join(ROOT, 'tools', 'calib', 'specs.json')

# glTF export maps car (X, Y, Z) -> (X, -Z, Y); undo it on the way back in
def to_car(v):
    return Vector((v.x, v.z, -v.y)) * 1000.0


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for g in GLBS:
        if os.path.exists(g):
            bpy.ops.import_scene.gltf(filepath=g)

    parts = {}
    for o in bpy.context.scene.objects:
        if o.parent is not None or o.type == 'EMPTY' and not o.children:
            continue
        top = o
        while top.parent:
            top = top.parent
        meshes = [m for m in [top] + list(top.children_recursive) if m.type == 'MESH']
        if not meshes:
            continue
        lo = Vector((1e9, 1e9, 1e9))
        hi = Vector((-1e9, -1e9, -1e9))
        for m in meshes:
            for c in m.bound_box:
                w = to_car(m.matrix_world @ Vector(c))
                lo = Vector((min(lo[i], w[i]) for i in range(3)))
                hi = Vector((max(hi[i], w[i]) for i in range(3)))
        parts[top.name] = {
            'min': [round(v) for v in lo], 'max': [round(v) for v in hi],
            'size': [round(hi[i] - lo[i]) for i in range(3)],
            'tris': sum(len(m.data.loop_triangles) or len(m.data.polygons) for m in meshes),
        }

    doc = json.load(open(SPECS)) if os.path.exists(SPECS) else {}
    specs, rules = doc.get('parts', {}), doc.get('rules', {})
    bad = []
    print(f'{"part":34} {"x mm":>16} {"y mm":>16} {"z mm":>18}  size (w h d)')
    for name in sorted(parts):
        p = parts[name]
        print(f'{name:34} {p["min"][0]:7} {p["max"][0]:7}  {p["min"][1]:7} {p["max"][1]:7}  '
              f'{p["min"][2]:8} {p["max"][2]:8}  {p["size"][0]:5} {p["size"][1]:4} {p["size"][2]:5}')
        spec = dict(next((v for k, v in rules.items() if name.startswith(k)), {}))
        spec.update(specs.get(name, {}))
        if not spec:
            continue
        for k, want in spec.items():
            if k == 'note':
                continue
            axis = {'w': 0, 'h': 1, 'd': 2}.get(k)
            got = p['size'][axis] if axis is not None else None
            if axis is None:                       # min/max bound on an axis, e.g. "y_min": [600, 700]
                ax, side = k.rsplit('_', 1)
                got = p[{'min': 'min', 'max': 'max'}[side]]['xyz'.index(ax)]
            lo, hi = want
            if not lo <= got <= hi:
                bad.append(f'{name}.{k} = {got}, expected {lo}..{hi}')

    missing = [n for n in specs if n not in parts]
    for m in missing:
        bad.append(f'{m} is in specs.json but not in the file')
    checked = sum(1 for n in parts if n in specs or any(n.startswith(k) for k in rules))
    print(f'\n{len(parts)} parts measured, {checked} checked '
          f'({len(rules)} family rules, {len(specs)} named)')
    for b in bad:
        print(f'FAIL  {b}')
    sys.exit(1 if bad else 0)


main()
