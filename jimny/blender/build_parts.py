# Build the bolt-on accessories as real meshes and export model/parts.glb.
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
#       -P jimny/blender/build_parts.py
#
# Each top-level object is one accessory (or one variant, "roofRack_platform"),
# built in the car frame from blender/car.json — a raycast sample of the body
# surface taken from the page itself — so it sits on the actual roof, gutter,
# tailgate and sill instead of on guessed numbers. Sizes follow the real
# products named at each builder; where a maker publishes no figure the value
# is an estimate from photos and says so.

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import P, box, tube, sweep, group, material, rounded_rect, circle, fillet  # noqa: E402
from mathutils import Vector  # noqa: E402

CAR = json.load(open(os.path.join(HERE, 'car.json')))
OUT = os.path.join(HERE, '..', 'model', 'parts.glb')

lib.reset()

# ------------------------------------------------------------- finishes
BLACK = material('PowderBlack', 0x1b1c1e, rough=0.55, metal=0.25)
TEXBLACK = material('TextureBlack', 0x151618, rough=0.85, metal=0.05)
ALU = material('Aluminium', 0xb9bcbf, rough=0.35, metal=1.0)
STEEL = material('ZincSteel', 0x9a9d9f, rough=0.4, metal=1.0)
RUBBER = material('Rubber', 0x0e0e0f, rough=0.9)
CANVAS = material('Canvas', 0x2f3330, rough=0.95)
PVC = material('AwningPVC', 0x2a2c2e, rough=0.7, metal=0.05)
LENS = material('LedLens', 0xdfe6ec, rough=0.08, metal=0.0)
CHROME = material('LedReflector', 0xe8ebee, rough=0.12, metal=1.0)
WEBBING = material('Webbing', 0x141515, rough=0.95)


# ------------------------------------------------------------- body facts
# +X is the vehicle's LEFT, so the vehicle's right side is negative X.
RIGHT = -1
def top_y(x, z):
    """Roof/bonnet height (mm) at (x, z) from the raycast grid, nearest sample."""
    best = min(CAR['top'], key=lambda p: (p[0] - x) ** 2 + (p[2] - z) ** 2)
    return best[1]


ROOF_Y_EDGE = 1580        # roof surface height at the gutters (sampled x = +-600)
ROOF_Y_MID = 1622         # crown of the roof
ROOF_Z_FRONT = 380        # roof panel ends where the windscreen header starts
ROOF_Z_REAR = -1445
GUTTER_X = 615            # rain gutter line either side
BODY_X = 705              # door skin at belt height
GLASS_X = 628             # side glass plane
TAIL_Z = -1527            # tailgate skin
SPARE = CAR['anchors']['spare']
SPARE_FACE_Z = -1772      # outer face of the spare tyre (sampled)
QUARTER = dict(z0=-1270, z1=-670, y0=1110, y1=1470)   # rear quarter glass, sampled
SILL_Y = 350              # lower edge of the door skin
FRONT_ARCH_Z = 700        # rear edge of the front wheel arch opening
REAR_ARCH_Z = -610        # front edge of the rear wheel arch opening


# =================================================================== ROOF RACK
# Front Runner Slimline II kit for the Jimny 2018+ (KRSJ003T): tray 1560 L x
# 1345 W x 50 mm, double-walled side rails (about 50 x 30), about 14 slats
# across the car at 110 mm pitch with L-section slats at the ends, six gutter
# legs 130 mm tall (front, middle, rear each side), top of tray ~180 mm above
# the gutter, one-piece 1345 mm wind deflector. Black powder coat.
# The basket variant is a generic 32 mm tube basket on the same legs.
def roof_rack(variant):
    root = group(f'roofRack_{variant}')
    W, L = (1345, 1560) if variant == 'platform' else (1250, 1300)
    zc = (ROOF_Z_FRONT + ROOF_Z_REAR) / 2 - 20
    top = ROOF_Y_EDGE + 180
    deck = top - 50                              # underside of the tray
    z0, z1 = zc - L / 2, zc + L / 2

    for s in (-1, 1):                            # side rails with a T-slot down the outside
        sweep(f'rail{s}', [(s * (W / 2 - 25), deck + 25, z0), (s * (W / 2 - 25), deck + 25, z1)],
              rounded_rect(50, 50, 5), BLACK, root)
        box(f'railSlot{s}', (s * W / 2, deck + 25, zc), (2, 10, L - 20), TEXBLACK, root, bevel=0)
    n = 14 if variant == 'platform' else 11
    pitch = (L - 60) / (n - 1)
    for i in range(n):
        z = z0 + 30 + i * pitch
        end = i in (0, n - 1)
        box(f'slat{i}', (0, top - 8, z), (W - 100, 15, 62), BLACK, root, bevel=2)
        box(f'slot{i}', (0, top, z), (W - 120, 1.5, 9), TEXBLACK, root, bevel=0)
        if end:                                  # L-section lip at front and rear
            box(f'lip{i}', (0, top - 30, z + (30 if i else -30)), (W - 100, 45, 4), BLACK, root, bevel=1)
    for s in (-1, 1):                            # six gutter legs, 130 tall, clamp under the gutter
        for k in range(3):
            z = z0 + 170 + k * (L - 340) / 2
            yg = ROOF_Y_EDGE - 6
            leg = [(s * (GUTTER_X + 18), yg - 25, z), (s * (GUTTER_X + 18), yg + 40, z),
                   (s * (W / 2 - 25), deck, z)]
            sweep(f'leg{s}{k}', [tuple(p) for p in fillet(leg, 30)], rounded_rect(64, 22, 5), BLACK, root)
            box(f'legPlate{s}{k}', (s * (W / 2 - 25), deck - 4, z), (70, 8, 70), BLACK, root, bevel=2)
            box(f'pad{s}{k}', (s * (GUTTER_X + 5), yg + 3, z), (40, 8, 64), RUBBER, root, bevel=2)
    zf = z1 + 70
    from mathutils import Matrix
    box('deflector', (0, top - 55, zf), (W - 60, 90, 3), BLACK, root, bevel=1,
        rot=Matrix.Rotation(math.radians(-58), 3, 'X'))
    for s in (-1, 1):
        box(f'deflBracket{s}', (s * (W / 2 - 40), top - 45, zf - 40), (6, 60, 90), BLACK, root, bevel=1)

    if variant == 'basket':
        y = top + 150
        hoop = [(-W / 2 + 20, y, z0 + 20), (W / 2 - 20, y, z0 + 20), (W / 2 - 20, y, z1 - 20),
                (-W / 2 + 20, y, z1 - 20), (-W / 2 + 20, y, z0 + 20), (W / 2 - 20, y, z0 + 20)]
        pts = fillet(hoop, 90)
        sweep('hoop', [tuple(p) for p in pts[:-3]], circle(16, 14), BLACK, root, caps=False)
        m = int(L // 250)
        for s in (-1, 1):
            for k in range(m + 1):
                z = z0 + 20 + k * (L - 40) / m
                tube(f'up{s}{k}', [(s * (W / 2 - 20), top, z), (s * (W / 2 - 20), y, z)], 22, BLACK, root)
        for k in range(1, int(W // 250)):
            x = -W / 2 + k * W / int(W // 250)
            for z in (z0 + 20, z1 - 20):
                tube(f'upx{k}{z}', [(x, top, z), (x, y, z)], 22, BLACK, root)
    return root


# ===================================================================== SNORKEL
# Safari-style snorkel for the JB74: on the vehicle's RIGHT (1.5 L airbox),
# out of the top of the right front wing just ahead of the windscreen base,
# up the A-pillar to about gutter height, forward-facing air ram on top.
# Black textured polyethylene; body ~95 x 75 mm rounded rectangle, ram about
# 180 L x 130 W x 150 H, two A-pillar brackets (estimates from photos).
def snorkel(side=1):
    root = group('snorkel')
    off = 58                                    # centreline outboard of the pillar skin
    path = [
        (side * 690, 840, 830),                 # through the side of the wing
        (side * 752, 850, 830),
        (side * 760, 1000, 800),
        (side * (690 + off), 1150, 650),        # A-pillar base
        (side * (640 + off), 1450, 440),        # following the pillar rake
        (side * (635 + off), 1530, 400),
    ]
    pts = fillet(path, 120, steps=10)
    sweep('body', [tuple(p) for p in pts], rounded_rect(95, 75, 30, 5), TEXBLACK, root)
    box('wingSeal', (side * 710, 845, 830), (8, 130, 130), RUBBER, root, bevel=3)
    # air ram: rounded hood, open mouth facing forward with a rubber-lined grille
    hx, hy, hz = side * (635 + off), 1560, 430
    sweep('ram', [(hx, hy, hz - 110), (hx, hy + 10, hz + 70)], rounded_rect(130, 150, 50, 6), TEXBLACK, root)
    sweep('mouth', [(hx, hy + 10, hz + 68), (hx, hy + 10, hz + 82)], rounded_rect(116, 134, 44, 6), RUBBER, root)
    for k in range(6):
        box(f'vane{k}', (hx, hy - 45 + k * 18 + 10, hz + 84), (104, 4, 5), TEXBLACK, root, bevel=0)
    for (y, z, x) in ((1210, 610, 690), (1440, 450, 645)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


# ================================================================ ROCK SLIDERS
# ARB rock sliders for the JB74 (4424010): 60.3 mm main tube parallel to the
# sill with no kick-out, three 47.6 mm support tubes per side into the chassis,
# 4 mm folded plate brackets, textured black. Tube ~90 mm outboard of and
# ~50 mm below the sill (estimate).
def rock_sliders():
    root = group('rockSliders')
    y = SILL_Y - 55
    x = BODY_X + 60
    zf, zr = FRONT_ARCH_Z - 40, REAR_ARCH_Z + 40
    for s in (-1, 1):
        rail = [(s * (x - 70), y + 10, zf + 10), (s * x, y, zf - 90), (s * x, y, zr + 90), (s * (x - 70), y + 10, zr - 10)]
        tube(f'main{s}', rail, 60.3, TEXBLACK, root, bend=110)
        for k, z in enumerate((zf - 170, (zf + zr) / 2, zr + 170)):
            tube(f'support{s}{k}', [(s * (x - 20), y, z), (s * 470, y + 30, z)], 47.6, TEXBLACK, root)
            box(f'bracket{s}{k}', (s * 455, y + 50, z), (70, 110, 90), TEXBLACK, root, bevel=4)
            box(f'gusset{s}{k}', (s * (x - 55), y + 32, z), (70, 4, 50), TEXBLACK, root, bevel=1)
    return root


# ====================================================================== LADDER
# Front Runner ladder for the Jimny 2018+ (LASJ002/4), from its fitting
# manual: on the RIGHT (hinge) side of the tailgate between the spare and the
# door edge; hooks over the top edge of the door, bolts to the lower hinge on
# 10 mm spacers, diagonal arm to the spare-carrier bolt; 950 mm from bottom to
# top step, four steps (top hook step + 3 pressed channel rungs, rubber grips
# top and bottom), about 135 mm stand-off. Width ~220 mm (estimate).
def ladder():
    root = group('ladder')
    s = RIGHT
    xin, xout = s * 395, s * 615
    zface = TAIL_Z - 110
    y0 = 560
    top_step = y0 + 950
    for x in (xin, xout):
        rail = [(x, y0 - 8, zface), (x, 1260, zface), (x, 1420, zface + 45),
                (x, 1495, TAIL_Z + 20), (x, 1520, TAIL_Z + 60)]
        sweep(f'rail{x}', [tuple(p) for p in fillet(rail, 70)], rounded_rect(20, 40, 4), BLACK, root)
    for k in range(3):                                   # pressed channel rungs
        y = y0 + k * 300
        box(f'rung{k}', ((xin + xout) / 2, y, zface - 5), (abs(xout - xin) + 20, 14, 60), BLACK, root, bevel=3)
        box(f'rungLip{k}', ((xin + xout) / 2, y - 14, zface - 34), (abs(xout - xin) + 20, 30, 4), BLACK, root, bevel=1)
        if k == 0:
            box('gripBottom', ((xin + xout) / 2, y + 9, zface - 5), (abs(xout - xin) - 30, 4, 50), RUBBER, root, bevel=1)
    box('topStep', ((xin + xout) / 2, top_step, TAIL_Z - 20), (abs(xout - xin) + 30, 12, 110), BLACK, root, bevel=3)
    box('gripTop', ((xin + xout) / 2, top_step + 8, TAIL_Z - 20), (abs(xout - xin) - 20, 4, 90), RUBBER, root, bevel=1)
    box('hook', ((xin + xout) / 2, 1500, TAIL_Z + 55), (abs(xout - xin) + 30, 60, 8), BLACK, root, bevel=2)
    for x in (xin, xout):                                # hinge bolt spacers
        lib.cylinder(f'spacer{x}', (x, 700, (TAIL_Z + zface) / 2), (0, 0, 1), 26, abs(TAIL_Z - zface), STEEL, root)
    tube('arm', [(xin, 820, zface), (s * 140, 760, SPARE_FACE_Z + 150)], 20, BLACK, root)
    return root


# ================================================================ WINDOW GUARDS
# Rear-quarter window guards: 25 x 8 mm flat-bar frame on stand-offs, filled
# with 45-degree diamond mesh of 12 mm strip, pitch about 90 mm.
def window_guards():
    root = group('windowGuards')
    q = QUARTER
    pad = 25
    z0, z1, y0, y1 = q['z0'] - pad, q['z1'] + pad, q['y0'] - pad, q['y1'] + pad
    for s in (-1, 1):
        x = s * (GLASS_X + 55)
        ring = [(x, y0, z0), (x, y0, z1), (x, y1, z1 - 40), (x, y1, z0), (x, y0, z0), (x, y0, z1)]
        sweep(f'frame{s}', [tuple(p) for p in fillet(ring, 40)][:-2], rounded_rect(10, 26, 3), BLACK, root, caps=False)
        pitch = 90
        W, H = z1 - z0, y1 - y0
        for d in (1, -1):
            for k in range(-int(H // pitch) - 1, int((W + H) // pitch) + 2):
                # line z = z0 + k*pitch + d*(y - y0) clipped to the frame
                yy0, yy1 = y0 + 8, y1 - 8
                za = z0 + k * pitch
                zb = za + d * (yy1 - yy0)
                seg = [(za, yy0), (zb, yy1)]
                # clip to z range
                (sa, ya), (sb, yb) = seg
                if max(sa, sb) < z0 + 8 or min(sa, sb) > z1 - 8:
                    continue

                def clip(zv, yv, zo, yo):
                    lo, hi = z0 + 8, z1 - 8
                    if lo <= zv <= hi:
                        return zv, yv
                    zt = lo if zv < lo else hi
                    t = (zt - zo) / (zv - zo)
                    return zt, yo + (yv - yo) * t
                ca = clip(sa, ya, sb, yb)
                cb = clip(sb, yb, sa, ya)
                if abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) < 20:
                    continue
                sweep(f'mesh{s}{d}{k}', [(x - s * 3, ca[1], ca[0]), (x - s * 3, cb[1], cb[0])],
                      rounded_rect(4, 12, 1.5, 2), BLACK, root, smooth=False)
        for (yy, zz) in ((y0, z0), (y0, z1), (y1, z0), (y1, z1 - 40)):
            box(f'bolt{s}{yy}{zz}', (s * (GLASS_X + 30), yy, zz), (50, 20, 20), BLACK, root, bevel=3)
    return root


# ================================================================== LIGHT BAR
# IPF 600 S-Series 40" double-row bar (642SD) on the 642JM2 A-pillar bracket
# set: straight, across the windscreen header just ahead of and above the
# roof's front edge. Housing ~1050 L x 80 H x 70 D die-cast with rear fins,
# clear lens over two rows of reflector cups (estimates from photos).
def light_bar():
    root = group('lightBar')
    L, y, z = 1050, ROOF_Y_EDGE + 70, ROOF_Z_FRONT + 90
    sweep('housing', [(-L / 2, y, z), (L / 2, y, z)], rounded_rect(70, 80, 14, 4), BLACK, root)
    box('bezel', (0, y, z + 34), (L - 24, 66, 4), BLACK, root, bevel=1)
    box('lens', (0, y, z + 37), (L - 50, 56, 2), LENS, root, bevel=0.5)
    n = 18
    for row in (-1, 1):
        for k in range(n):
            xk = -L / 2 + 50 + k * (L - 100) / (n - 1)
            lib.cylinder(f'cup{row}{k}', (xk, y + row * 14, z + 31), (0, 0, 1), 24, 6, CHROME, root, n=12)
    for k in range(30):
        box(f'fin{k}', (-L / 2 + 30 + k * (L - 60) / 29, y, z - 38), (5, 70, 12), BLACK, root, bevel=0)
    for s in (-1, 1):                                    # A-pillar bracket: plate up from the pillar top
        arm = [(s * 610, ROOF_Y_EDGE - 150, ROOF_Z_FRONT + 40), (s * 620, ROOF_Y_EDGE - 20, ROOF_Z_FRONT + 60),
               (s * (L / 2 + 15), y, z)]
        sweep(f'bracket{s}', [tuple(p) for p in fillet(arm, 40)], rounded_rect(50, 8, 2), BLACK, root)
        box(f'endCap{s}', (s * (L / 2 + 6), y, z), (12, 84, 74), BLACK, root, bevel=3)
    return root


# ===================================================================== AWNING
# ARB Touring 2000 x 2500 awning (814200): PVC bag 2130 L x 120 x 120 mm,
# black/grey with end caps, two L-brackets into the rack's side T-slot about
# 1200 apart. On a 1560 rack it overhangs ~285 mm in total.
def awning(side):
    root = group(f'awning_{side}')
    s = -RIGHT if side == 'left' else RIGHT
    L = 2130
    rack_top = ROOF_Y_EDGE + 180
    x, y, zc = s * (1345 / 2 + 75), rack_top - 40, (ROOF_Z_FRONT + ROOF_Z_REAR) / 2 - 20
    sweep('bag', [(x, y, zc - L / 2 + 20), (x, y, zc + L / 2 - 20)], rounded_rect(120, 120, 40, 6), PVC, root)
    for k in (-1, 1):
        z = zc + k * (L / 2 - 10)
        sweep(f'cap{k}', [(x, y, z - 18), (x, y, z + 18)], rounded_rect(128, 128, 44, 6), BLACK, root)
        box(f'strap{k}', (x, y, zc + k * 600), (124, 124, 40), WEBBING, root, bevel=10)
    box('zip', (x + s * 60, y - 30, zc), (3, 8, L - 120), WEBBING, root, bevel=0)
    for k in (-1, 1):
        z = zc + k * 600
        box(f'lbracketH{k}', (s * (1345 / 2 + 20), y + 55, z), (120, 6, 50), BLACK, root, bevel=2)
        box(f'lbracketV{k}', (s * (1345 / 2 + 5), y + 20, z), (6, 70, 50), BLACK, root, bevel=2)
    return root


# ================================================================== SPARE BAG
# Trasharoo spare-tyre bag: padded polyester bag centred on the wheel, about
# 500 W x 450 H x 250 D when full, held by an X-harness of four straps that
# meet behind it and hook onto the tread. Drain grommets along the bottom.
def spare_bag():
    root = group('spareBag')
    cx, cy, dia = SPARE['x'], SPARE['y'], SPARE['dia']
    W, H, D = 500, 450, 230
    zc = SPARE_FACE_Z - D / 2 + 25
    bag = box('bag', (cx, cy, zc), (W, H, D), CANVAS, root, bevel=70)
    bag.modifiers['bevel'].segments = 6
    sub = bag.modifiers.new('soft', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    zf = zc - D / 2
    for k in range(3):                                   # MOLLE rows
        box(f'molle{k}', (cx, cy - 80 + k * 70, zf - 1), (W - 150, 26, 5), WEBBING, root, bevel=1)
    box('lid', (cx, cy + H / 2 - 60, zf + 4), (W - 60, 6, 6), STEEL, root, bevel=0)
    r = dia / 2 + 4
    for ang in (45, 135, 225, 315):                      # X harness to the tread
        a = math.radians(ang)
        cxr, cyr = cx + math.cos(a) * (W / 2 - 60), cy + math.sin(a) * (H / 2 - 60)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        strap = [(cxr, cyr, zf + 30), (px, py, SPARE_FACE_Z + 5), (px, py, SPARE_FACE_Z + 90)]
        sweep(f'strap{ang}', strap, rounded_rect(4, 38, 1), WEBBING, root)
        box(f'hook{ang}', (px, py, SPARE_FACE_Z + 100), (30, 30, 20), STEEL, root, bevel=4)
    for k in range(3):
        lib.cylinder(f'grommet{k}', (cx - 120 + k * 120, cy - H / 2 + 22, zf + 30), (0, 1, 0), 22, 6, STEEL, root, n=12)
    return root


# ================================================================ SPARE COVER
# Suzuki genuine JB74W hard spare cover (9923B-77R21-003): hard resin face and
# side ring, brushed-metal-look face, ~720 dia x 230 deep, rounded outer edge.
def spare_cover():
    root = group('spareCover')
    cx, cy = SPARE['x'], SPARE['y']
    R, D = 360, 230
    zb = SPARE_FACE_Z + 190
    prof = [(R * 0.0, zb), (R - 10, zb), (R, zb - 20), (R + 6, zb - D + 50), (R - 20, zb - D + 8),
            (R - 60, zb - D), (0, zb - D - 6)]
    import bmesh
    bm = bmesh.new()
    seg = 64
    rings = []
    for (r, z) in prof:
        rings.append([bm.verts.new(P(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg), z))
                      for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lib.new_object('shell', bm, TEXBLACK, root)
    face = material('CoverFace', 0xa9adb0, rough=0.45, metal=0.6)
    lib.cylinder('face', (cx, cy, zb - D - 12), (0, 0, 1), 2 * (R - 70), 6, face, root, n=64)
    lib.cylinder('ring', (cx, cy, zb - D - 10), (0, 0, 1), 2 * (R - 62), 6, BLACK, root, n=64)
    return root


def build():
    for v in ('platform', 'basket'):
        roof_rack(v)
    snorkel(RIGHT)
    rock_sliders()
    ladder()
    window_guards()
    light_bar()
    awning('left')
    awning('right')
    spare_bag()
    spare_cover()
    lib.export(os.path.abspath(OUT))


build()
print('exported', os.path.abspath(OUT))
