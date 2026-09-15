# Geometry helpers for building accessories in Blender from code.
#
# Every coordinate passed in is in the CAR frame the web page uses: millimetres,
# +Y up from the ground, +Z forward, and +X towards the vehicle's LEFT side
# (the model is left-hand drive; its steering wheel sits at +X). The
# glTF exporter turns Blender's Z-up into Y-up by mapping Blender (x, y, z) to
# glTF (x, z, -y), so car (X, Y, Z) is stored as Blender (X, -Z, Y). Parts built
# here therefore load in the page already sitting in the right place on the car.

import math
import bmesh
import bpy
from mathutils import Vector, Matrix

MM = 0.001


def P(x, y, z):
    """Car-frame millimetres -> Blender metres."""
    return Vector((x * MM, -z * MM, y * MM))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ---------------------------------------------------------------- materials
_MATS = {}


def material(name, color, rough=0.5, metal=0.0, alpha=1.0, emit=None):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(color), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*srgb(emit), 1)
        b.inputs['Emission Strength'].default_value = 1.0
    _MATS[name] = m
    return m


def srgb(hexcol):
    c = [((hexcol >> s) & 255) / 255 for s in (16, 8, 0)]
    return [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]


# ------------------------------------------------------------------ objects
def box_uv(bm, scale=0.1):
    """Box-projected UVs (one repeat per `scale` metres) so tiling grain maps work."""
    bm.normal_update()
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [i for i in range(3) if i != ax]
        for l in f.loops:
            co = l.vert.co
            l[uv].uv = (co[a] / scale, co[b] / scale)


def new_object(name, bm, mat, parent=None, smooth=True, bevel=0.0, segments=2):
    box_uv(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        mod = ob.modifiers.new('bevel', 'BEVEL')
        mod.width = bevel * MM
        mod.segments = segments
        mod.limit_method = 'ANGLE'
        mod.harden_normals = False
    if parent is not None:
        ob.parent = parent
    return ob


def group(name, parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def box(name, centre, size, mat, parent=None, bevel=2.0, rot=None):
    """Axis-aligned (car frame) box, size = (sx, sy, sz) mm, bevelled edges."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    # car (X, Y, Z) sizes -> Blender (x, y, z) = (X, Z, Y)
    bmesh.ops.scale(bm, vec=Vector((sx * MM, sz * MM, sy * MM)), verts=bm.verts)
    if rot is not None:
        bmesh.ops.rotate(bm, cent=Vector(), matrix=rot, verts=bm.verts)
    bmesh.ops.translate(bm, vec=P(*centre), verts=bm.verts)
    return new_object(name, bm, mat, parent, smooth=False, bevel=bevel)


def fillet(points, radius, steps=6):
    """Round every interior corner of a polyline with an arc of `radius` mm."""
    pts = [Vector(p) for p in points]
    if len(pts) < 3 or radius <= 0:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d1, d2 = (a - b), (c - b)
        l1, l2 = d1.length, d2.length
        if l1 < 1e-6 or l2 < 1e-6:
            continue
        d1.normalize(); d2.normalize()
        ang = d1.angle(d2)
        if ang > math.pi - 1e-3:
            out.append(b)
            continue
        t = min(radius / math.tan(ang / 2), l1 * 0.49, l2 * 0.49)
        p1, p2 = b + d1 * t, b + d2 * t
        # quadratic Bezier through the corner approximates the arc well enough
        for s in range(steps + 1):
            u = s / steps
            out.append(p1 * (1 - u) ** 2 + b * 2 * u * (1 - u) + p2 * u * u)
    out.append(pts[-1])
    return out


def _frames(path):
    """Parallel-transport frames along a polyline (no twisting at bends)."""
    tangents = []
    for i in range(len(path)):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, len(path) - 1)]
        tangents.append((b - a).normalized())
    t0 = tangents[0]
    up = Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    n = t0.cross(up).normalized()
    frames = []
    for t in tangents:
        n = (n - t * n.dot(t)).normalized()
        frames.append((t, n, t.cross(n).normalized()))
    return frames


def sweep(name, path_mm, profile, mat, parent=None, caps=True, smooth=True, closed=False):
    """Sweep a 2D profile [(u, v) mm] along a car-frame path [(X, Y, Z) mm]."""
    path = [P(*p) for p in path_mm]
    frames = _frames(path)
    bm = bmesh.new()
    rings = []
    for p, (t, n, bn) in zip(path, frames):
        rings.append([bm.verts.new(p + n * (u * MM) + bn * (v * MM)) for (u, v) in profile])
    k = len(profile)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
    if caps and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat, parent, smooth=smooth)


def circle(r, n=16):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rounded_rect(w, h, r, n=4):
    """Rounded rectangle profile, w x h mm, corner radius r."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                       (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def tube(name, points_mm, dia, mat, parent=None, bend=None, n=16):
    """Round tube through car-frame points with bends of radius `bend` (default 2.5 x dia)."""
    pts = fillet(points_mm, bend if bend is not None else dia * 2.5)
    return sweep(name, [tuple(p) for p in pts], circle(dia / 2, n), mat, parent)


def cylinder(name, centre, axis, dia, length, mat, parent=None, n=24, bevel=1.0):
    c = Vector(centre)
    a = Vector(axis).normalized()
    return sweep(name, [tuple(c - a * length / 2), tuple(c + a * length / 2)], circle(dia / 2, n), mat, parent,
                 smooth=True)


def annulus(name, centre, r_in, r_out, depth, mat, parent=None, n=48):
    """Flat ring in the car X-Y plane (facing +Z), `depth` mm thick towards -Z."""
    cx, cy, cz = centre
    bm = bmesh.new()
    rings = []
    for r, z in ((r_in, cz), (r_out, cz), (r_out, cz - depth), (r_in, cz - depth)):
        rings.append([bm.verts.new(P(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z))
                      for i in range(n)])
    loops = rings + [rings[0]]
    for a, b in zip(loops, loops[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat, parent, smooth=True)


def sphere(name, centre, dia, mat, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=dia / 2 * MM)
    bmesh.ops.translate(bm, vec=P(*centre), verts=bm.verts)
    return new_object(name, bm, mat, parent, smooth=True)


def text(name, body, centre, size, depth, mat, parent=None):
    """Extruded text standing on the car's front face (reads from +Z)."""
    cu = bpy.data.curves.new(name, type='FONT')
    cu.body = body
    cu.size = size * MM
    cu.extrude = depth / 2 * MM
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    tmp = bpy.data.objects.new(name + '_curve', cu)
    bpy.context.scene.collection.objects.link(tmp)
    tmp.rotation_euler = (math.pi / 2, 0, 0)
    tmp.location = P(*centre)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me.transform(tmp.matrix_world)
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    return ob


def apply_modifiers(ob):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        for m in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)


def cut(ob, cutters):
    """Boolean-subtract each cutter object from ob, then delete the cutters."""
    for c in cutters:
        mod = ob.modifiers.new('cut', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = c
        mod.solver = 'EXACT'
    apply_modifiers(ob)
    for c in cutters:
        me = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(me)


def lathe(name, profile, mat, parent=None, n=64, smooth=True):
    """Revolve a closed (r, x) polyline around the car X axis at the origin."""
    bm = bmesh.new()
    rings = []
    for r, x in profile:
        rings.append([bm.verts.new(P(x, r * math.sin(2 * math.pi * i / n), r * math.cos(2 * math.pi * i / n)))
                      for i in range(n)])
    loops = rings + [rings[0]]
    for a, b in zip(loops, loops[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat, parent, smooth=smooth)


def prism(name, poly, x0, x1, mat, parent=None, smooth=False):
    """Polygon given as (y, z) car-frame points, extruded from x0 to x1."""
    bm = bmesh.new()
    a = [bm.verts.new(P(x0, y, z)) for (y, z) in poly]
    b = [bm.verts.new(P(x1, y, z)) for (y, z) in poly]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    k = len(poly)
    for i in range(k):
        bm.faces.new((a[i], b[i], b[(i + 1) % k], a[(i + 1) % k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat, parent, smooth=smooth)


def export(path, draco=False):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True, export_apply=True,
                              export_extras=False, export_draco_mesh_compression_enable=draco)
