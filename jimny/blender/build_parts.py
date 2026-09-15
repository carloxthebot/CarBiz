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
from lib import P, box, tube, sweep, group, material, rounded_rect, circle, fillet, annulus, sphere, text, cut  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
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
PAINT = material('BodyPaint', 0xe8e0c8, rough=0.45, metal=0.25)     # swapped for the car's paint in the page
PLATE = material('NumberPlate', 0xf2f2ec, rough=0.5)
ALU_CHEQ = material('AluChequer', 0xb0b3b6, rough=0.5, metal=0.9)
RED = material('FairleadRed', 0xb0261c, rough=0.4, metal=0.3)


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
    top = ROOF_Y_MID + 95                      # tray just clears the roof crown
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
# Safari-style snorkel for the JB74, from fitted photos: on the vehicle's
# RIGHT, rising straight out of the TOP of the front wing just behind the
# wheel arch and directly ahead of the A-pillar, then hugging the pillar to
# an air ram whose top sits ~80 mm above the roof line, mouth facing forward.
# Body ~95 x 75 mm rounded rectangle, ram ~180 L x 130 W x 150 H (estimates).
def snorkel(side=1):
    root = group('snorkel')
    off = 40                                    # centreline outboard of the pillar skin
    wing_y = top_y(side * 700, 660)
    path = [
        (side * 705, wing_y - 60, 660),         # sunk into the wing top, right under the pillar base
        (side * 705, wing_y + 80, 660),
        (side * (660 + off), 1160, 630),        # A-pillar base
        (side * (640 + off), 1400, 500),        # following the pillar rake
        (side * (612 + off), 1560, 410),
        (side * (612 + off), 1590, 400),
    ]
    pts = fillet(path, 110, steps=10)
    sweep('body', [tuple(p) for p in pts], rounded_rect(95, 75, 30, 5), TEXBLACK, root)
    box('wingSeal', (side * 705, wing_y + 6, 660), (140, 10, 140), RUBBER, root, bevel=4)
    hx, hy, hz = side * (612 + off), 1622, 410
    sweep('ram', [(hx, hy, hz - 110), (hx, hy + 8, hz + 70)], rounded_rect(130, 150, 50, 6), TEXBLACK, root)
    sweep('mouth', [(hx, hy + 8, hz + 68), (hx, hy + 8, hz + 82)], rounded_rect(116, 134, 44, 6), RUBBER, root)
    for k in range(6):
        box(f'vane{k}', (hx, hy - 45 + k * 18 + 10, hz + 84), (104, 4, 5), TEXBLACK, root, bevel=0)
    for (y, z, x) in ((1260, 575, 655), (1500, 445, 625)):
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
    for k in range(3):                                   # 25 mm tube rungs
        y = y0 + k * 300
        tube(f'rung{k}', [(xin, y, zface - 5), (xout, y, zface - 5)], 25, BLACK, root)
        if k == 0:
            box('gripBottom', ((xin + xout) / 2, y + 11, zface - 5), (abs(xout - xin) - 30, 3, 22), RUBBER, root, bevel=1)
    box('topStep', ((xin + xout) / 2, top_step, TAIL_Z - 20), (abs(xout - xin) + 30, 12, 110), BLACK, root, bevel=3)
    box('gripTop', ((xin + xout) / 2, top_step + 8, TAIL_Z - 20), (abs(xout - xin) - 20, 4, 90), RUBBER, root, bevel=1)
    box('hook', ((xin + xout) / 2, 1500, TAIL_Z + 55), (abs(xout - xin) + 30, 60, 8), BLACK, root, bevel=2)
    for x in (xin, xout):                                # hinge bolt spacers
        lib.cylinder(f'spacer{x}', (x, 700, (TAIL_Z + zface) / 2), (0, 0, 1), 26, abs(TAIL_Z - zface), STEEL, root)
    tube('arm', [(xin, 820, zface), (s * 140, 760, SPARE_FACE_Z + 150)], 20, BLACK, root)
    return root


# ================================================================ WINDOW GUARDS
# WLM 4x4 Motors rear-quarter window guards (JB7408/JB7409): one laser-cut
# steel plate per side, 795 x 533 mm, black powder coat, standing 20 mm off
# the body. A field of about 10 x 7 square holes (~55 mm) inside a plain
# border that carries a row of small accessory holes; big rounded corners.
# Two clips at the top hook into the roof gutter, two hinge blocks at the
# bottom sit on the panel under the window. Rear quarter glass only.
def window_guards():
    root = group('windowGuards')
    q = QUARTER
    PW, PH, T = 795, 533, 4
    cz, cy = (q['z0'] + q['z1']) / 2, (q['y0'] + q['y1']) / 2 + 20
    cols, rows, hole, bar = 10, 7, 55, 8
    fw, fh = cols * hole + (cols - 1) * bar, rows * hole + (rows - 1) * bar
    bw, bh = (PW - fw) / 2, (PH - fh) / 2          # border widths, sides / top-bottom
    for s in (-1, 1):
        x = s * 712
        # border ring: rounded-rectangle path, thin rectangular profile
        ring = [(x, cy - PH / 2 + bh / 2, cz - PW / 2 + bw / 2), (x, cy - PH / 2 + bh / 2, cz + PW / 2 - bw / 2),
                (x, cy + PH / 2 - bh / 2, cz + PW / 2 - bw / 2), (x, cy + PH / 2 - bh / 2, cz - PW / 2 + bw / 2)]
        loop = ring + ring[:2]
        pts = fillet(loop, 45)
        sweep(f'ring{s}', [tuple(p) for p in pts[:-1]], [(-T / 2, -bh / 2), (T / 2, -bh / 2), (T / 2, bh / 2), (-T / 2, bh / 2)],
              BLACK, root, caps=False, smooth=False)
        # fill the wider side borders between the ring and the hole field
        for k in (-1, 1):
            box(f'sideFill{s}{k}', (x, cy, cz + k * (fw / 2 + (bw - bh) / 2 + bh / 2)), (T, fh, bw - bh), BLACK, root, bevel=0)
        # hole field: vertical and horizontal bars
        for i in range(1, cols):
            z = cz - fw / 2 + i * (hole + bar) - bar / 2
            box(f'vbar{s}{i}', (x, cy, z), (T, fh, bar), BLACK, root, bevel=0)
        for j in range(1, rows):
            y = cy - fh / 2 + j * (hole + bar) - bar / 2
            box(f'hbar{s}{j}', (x, y, cz), (T, bar, fw), BLACK, root, bevel=0)
        # accessory holes along the border, drawn as dark discs
        for i in range(12):
            z = cz - fw / 2 + 20 + i * (fw - 40) / 11
            for y in (cy - PH / 2 + bh / 2, cy + PH / 2 - bh / 2):
                lib.cylinder(f'hole{s}{i}{y}', (x, y, z), (1, 0, 0), 7, T + 0.6, RUBBER, root, n=10)
        # gutter clips on top, hinge blocks below
        for k in (-1, 1):
            z = cz + k * PW * 0.30
            clip = [(x, cy + PH / 2 - 10, z), (x, ROOF_Y_EDGE - 30, z), (s * (GUTTER_X + 12), ROOF_Y_EDGE - 30, z),
                    (s * (GUTTER_X + 12), ROOF_Y_EDGE + 6, z)]
            sweep(f'clip{s}{k}', [tuple(p) for p in fillet(clip, 12)], [(-2, -20), (2, -20), (2, 20), (-2, 20)], BLACK, root)
            box(f'hinge{s}{k}', (s * 700, cy - PH / 2 + 12, z), (26, 30, 40), BLACK, root, bevel=3)
            lib.cylinder(f'knob{s}{k}', (x + s * 8, cy + PH / 2 - bh / 2, z), (1, 0, 0), 22, 14, STEEL, root, n=12)
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


# ===================================================================== GRILLES
# Every aftermarket grille replaces the whole stock panel (1310 x 241 mm, the
# satin surround with the headlamp and indicator holes), so each starts from
# the same panel following the measured face, z = 1664 - 1.9e-4 x^2, and cuts
# its own centre opening. The headlamp units themselves stay on the car.
G_Y0, G_Y1 = 738, 979
LAMP = ((-460, 866), (460, 866))
SIGNAL = ((-599, 922), (599, 922))


def face_z(x):
    return 1664 - 1.9e-4 * x * x


def grille_panel(name, root, mat, opening, thick=14, proud=8):
    """Curved slab with headlamp/indicator holes and a rectangular centre opening (w, h, cy)."""
    nx, ny = 52, 8
    bm = bmesh.new()
    grid = []
    for j in range(ny + 1):
        y = G_Y0 + (G_Y1 - G_Y0) * j / ny
        row = []
        for i in range(nx + 1):
            x = -655 + 1310 * i / nx
            z = face_z(x) + proud
            row.append(bm.verts.new(P(x, y, z)))
        grid.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = lib.new_object(name, bm, mat, root, smooth=True)
    sol = ob.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = thick * MM
    sol.offset = -1
    lib.apply_modifiers(ob)
    cutters = []
    for k, (x, y) in enumerate(LAMP):
        cutters.append(lib.cylinder(f'cutLamp{k}', (x, y, face_z(x)), (0, 0, 1), 192, 120, mat, None, n=48))
    for k, (x, y) in enumerate(SIGNAL):
        cutters.append(lib.cylinder(f'cutSig{k}', (x, y, face_z(x)), (0, 0, 1), 78, 120, mat, None, n=32))
    if opening:
        w, h, cy = opening
        cutters.append(box('cutOpen', (0, cy, face_z(0)), (w, h, 140), mat, None, bevel=0))
    cut(ob, cutters)
    return ob


MM = lib.MM


def lamp_bezels(root, mat, style='round'):
    for k, (x, y) in enumerate(LAMP):
        z = face_z(x) + 8
        if style == 'round':
            annulus(f'bezel{k}', (x, y, z + 12), 96, 114, 20, mat, root)
        else:                                            # squared bezel with a round bore
            b = box(f'bezel{k}', (x, y, z + 6), (232, 232, 12), mat, root, bevel=14)
            c = lib.cylinder(f'cutB{k}', (x, y, z), (0, 0, 1), 192, 60, mat, None, n=48)
            cut(b, [c])
    for k, (x, y) in enumerate(SIGNAL):
        annulus(f'sigBezel{k}', (x, y, face_z(x) + 14), 39, 48, 8, mat, root)


def wire_mesh(root, mat, cx, cy, z, w, h, pitch=10, bar=1.6):
    for i in range(int(w // pitch) + 1):
        x = cx - w / 2 + i * pitch
        box(f'mv{cx}{cy}{i}', (x, cy, z), (bar, h, bar), mat, root, bevel=0)
    for j in range(int(h // pitch) + 1):
        y = cy - h / 2 + j * pitch
        box(f'mh{cx}{cy}{j}', (cx, y, z), (w, bar, bar), mat, root, bevel=0)


def hex_mesh(root, mat, cx, cy, z, w, h, cell=25, bar=2.4):
    """Honeycomb: flat-topped hexagons, edges drawn once."""
    r = cell / 2 / math.cos(math.pi / 6)              # circumradius for a cell `cell` across flats
    dx, dy = 1.5 * r, cell
    edges = set()
    col = 0
    x = cx - w / 2 + r
    while x < cx + w / 2 - r * 0.5:
        y0 = cy - h / 2 + (dy / 2 if col % 2 else 0) + cell / 2
        y = y0
        while y < cy + h / 2 - cell * 0.45:
            for k in range(6):
                a0, a1 = math.pi / 3 * k, math.pi / 3 * (k + 1)
                p0 = (round(x + r * math.cos(a0)), round(y + r * math.sin(a0)))
                p1 = (round(x + r * math.cos(a1)), round(y + r * math.sin(a1)))
                edges.add(tuple(sorted((p0, p1))))
            y += dy
        x += dx
        col += 1
    for i, ((x0, y0), (x1, y1)) in enumerate(sorted(edges)):
        sweep(f'hx{i}', [(x0, y0, z), (x1, y1, z)], [(-bar / 2, -bar / 2), (bar / 2, -bar / 2), (bar / 2, bar / 2), (-bar / 2, bar / 2)],
              mat, root, smooth=False)


# SHOWA GARAGE ABS front grille (E00500): stock outline, round lamp bezels,
# a rounded-rectangle frame ~440 x 120 in the centre with a recessed hex
# honeycomb, matte black.
def grille_showa():
    root = group('grille_showa_hex')
    grille_panel('panel', root, TEXBLACK, (440, 120, 858))
    lamp_bezels(root, TEXBLACK, 'round')
    # frame lip around the opening
    fw, fh = 470, 150
    for (cx, cy, sx, sy) in ((0, 858 + fh / 2, fw, 16), (0, 858 - fh / 2, fw, 16), (-fw / 2, 858, 16, fh), (fw / 2, 858, 16, fh)):
        box(f'lip{cx}{cy}', (cx, cy, face_z(cx) + 10), (sx, sy, 10), TEXBLACK, root, bevel=3)
    hex_mesh(root, BLACK, 0, 858, face_z(0) - 16, 436, 118)
    box('backing', (0, 858, face_z(0) - 30), (440, 120, 3), RUBBER, root, bevel=0)
    return root


# OUTCLASS Vintage G grille: textured black ASA, squared lamp bezels, four
# horizontal slats ~450 x 30 with 15 mm gaps split by a centre post, fine
# mesh behind.
def grille_outclass():
    root = group('grille_outclass_g')
    ow, oh = 470, 175
    grille_panel('panel', root, TEXBLACK, (ow, oh, 858))
    lamp_bezels(root, TEXBLACK, 'square')
    for k in range(4):
        y = 858 - oh / 2 + 15 + 15 + k * 45
        for sx in (-1, 1):
            box(f'slat{k}{sx}', (sx * (ow / 4 + 6), y, face_z(0) + 2), (ow / 2 - 26, 30, 22), TEXBLACK, root, bevel=4)
    box('post', (0, 858, face_z(0) + 3), (22, oh, 24), TEXBLACK, root, bevel=3)
    wire_mesh(root, BLACK, 0, 858, face_z(0) - 20, ow - 10, oh - 10, pitch=9)
    box('backing', (0, 858, face_z(0) - 32), (ow, oh, 3), RUBBER, root, bevel=0)
    return root


# KLC Face Grille SJ: one-piece painted face (shown in body colour), seven
# tall rounded slots ~40 x 200 at 70 mm pitch over aluminium mesh, round lamp
# bezels, raised SUZUKI lettering above the slots.
def grille_klc():
    root = group('grille_klc_sj')
    panel = grille_panel('panel', root, PAINT, None)
    cutters = []
    for k in range(7):
        x = -210 + k * 70
        cutters.append(box(f'cutSlot{k}', (x, 850, face_z(x)), (40, 190, 140), PAINT, None, bevel=0))
    cut(panel, cutters)
    lamp_bezels(root, PAINT, 'round')
    wire_mesh(root, STEEL, 0, 850, face_z(0) - 18, 480, 200, pitch=8, bar=1.2)
    box('backing', (0, 850, face_z(0) - 30), (490, 210, 3), RUBBER, root, bevel=0)
    text('suzuki', 'SUZUKI', (0, 955, face_z(0) + 9), 42, 3, BLACK, root)
    return root


# ============================================================== FRONT BUMPERS
# All three replace the stock bumper (hidden by the page). The stock one is
# 1565 wide, y 342-714, front face z ~1770; a black valance behind each new
# bar closes the gap to the radiator that the stock bumper used to cover.
def valance(root, corners=True):
    box('valance', (0, 560, 1500), (1200, 280, 24), RUBBER, root, bevel=4)
    for s in (-1, 1):                                    # chassis-rail mounts
        box(f'mount{s}', (s * 330, 540, 1600), (70, 120, 200), TEXBLACK, root, bevel=4)
    if corners:                                          # closes the corner the stock bumper wrapped around
        from mathutils import Matrix
        for s in (-1, 1):
            box(f'corner{s}', (s * 735, 560, 1490), (60, 300, 170), TEXBLACK, root, bevel=6,
                rot=Matrix.Rotation(math.radians(s * 28), 3, 'Z'))


def fog_lamp(root, x, y, z, mat, dia=90):
    lib.cylinder(f'fogHsg{x}', (x, y, z - 30), (0, 0, 1), dia + 14, 70, mat, root)
    lib.cylinder(f'fogBowl{x}', (x, y, z), (0, 0, 1), dia - 6, 6, CHROME, root)
    lib.cylinder(f'fogLens{x}', (x, y, z + 6), (0, 0, 1), dia, 4, LENS, root)


def number_plate(root, y, z):
    box('plate', (0, y, z), (330, 165, 2), PLATE, root, bevel=1)


# SHOWA GARAGE Iron Bumper (E00900): one Ø60 steel tube at stock-bumper
# height, ends bent ~45° back to domed caps ahead of the arches, plate hung
# below centre, Ø90 fogs on stays, 3 mm aluminium skid plate, textured black.
def bumper_showa():
    root = group('frontBumper_showa_iron')
    y = 600
    path = [(-750, y, 1560), (-600, y, 1740), (600, y, 1740), (750, y, 1560)]
    tube('bar', path, 60, TEXBLACK, root, bend=130)
    for s in (-1, 1):
        sphere(f'cap{s}', (s * 750, y, 1560), 60, TEXBLACK, root)
        box(f'stay{s}', (s * 430, y - 40, 1700), (24, 80, 20), TEXBLACK, root, bevel=2)
        fog_lamp(root, s * 430, y - 90, 1712, TEXBLACK)
        box(f'plateArm{s}', (s * 120, y - 60, 1735), (16, 120, 12), TEXBLACK, root, bevel=1)
    number_plate(root, 500, 1745)
    from mathutils import Matrix
    box('skid', (0, 380, 1620), (700, 4, 260), ALU, root, bevel=1, rot=Matrix.Rotation(math.radians(-30), 3, 'X'))
    valance(root)
    return root


# KLC Heritage Traditional Bumper: straight Ø60 stainless tube ~1300 wide
# with flat caps, a shorter Ø50 tube below carrying the plate, box brackets
# with Ø90 fogs, flat black skid plate. Sold in ivory / black / polished —
# drawn in body colour.
def bumper_klc():
    root = group('frontBumper_klc_trad')
    y1, y2 = 615, 545
    tube('upper', [(-650, y1, 1745), (650, y1, 1745)], 60, PAINT, root)
    tube('lower', [(-330, y2, 1705), (330, y2, 1705)], 50, PAINT, root)
    for s in (-1, 1):
        tube(f'link{s}', [(s * 250, y2, 1705), (s * 250, y1, 1745)], 30, PAINT, root)
        box(f'fogBox{s}', (s * 340, y2 - 10, 1690), (100, 100, 90), PAINT, root, bevel=6)
        fog_lamp(root, s * 340, y2 - 10, 1738, PAINT, dia=80)
        tube(f'upright{s}', [(s * 330, 420, 1520), (s * 330, y1 - 20, 1735)], 45, PAINT, root)
    number_plate(root, 520, 1732)
    from mathutils import Matrix
    box('skid', (0, 400, 1610), (520, 4, 260), TEXBLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-30), 3, 'X'))
    valance(root)
    return root


# OUTCLASS TYPE2 winch bumper: flat-faced folded-steel box ~1500 x 250 x 200,
# ends chamfered back, centre fairlead over the plate, four square LED pods,
# shackle tabs, slotted skid apron at 45°.
def bumper_outclass():
    root = group('frontBumper_outclass_t2')
    y = 560
    # path runs through the box centre; the 200 mm deep profile puts the face at z 1750
    path = [(-780, y, 1420), (-640, y, 1650), (640, y, 1650), (780, y, 1420)]
    sweep('body', [tuple(p) for p in fillet(path, 40, steps=3)], rounded_rect(200, 220, 10, 3), TEXBLACK, root)
    box('fairleadFrame', (0, 640, 1756), (300, 100, 14), RED, root, bevel=3)
    box('fairleadSlot', (0, 640, 1764), (240, 56, 4), RUBBER, root, bevel=0)
    number_plate(root, 540, 1758)
    for x in (-520, -300, 300, 520):
        box(f'pod{x}', (x, 595, 1756), (82, 82, 12), BLACK, root, bevel=2)
        box(f'podLens{x}', (x, 595, 1763), (66, 66, 2), LENS, root, bevel=0)
    for s in (-1, 1):
        box(f'tab{s}', (s * 350, 420, 1720), (12, 110, 90), TEXBLACK, root, bevel=2)
        annulus(f'shackle{s}', (s * 350, 400, 1735), 12, 22, 24, STEEL, root, n=24)
    from mathutils import Matrix
    apron = box('apron', (0, 340, 1650), (720, 4, 300), TEXBLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-45), 3, 'X'))
    for k in range(3):
        box(f'aslot{k}', (-150 + k * 150, 350, 1662), (90, 4, 24), RUBBER, root, bevel=0,
            rot=Matrix.Rotation(math.radians(-45), 3, 'X'))
    valance(root, corners=False)
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
    grille_showa()
    grille_outclass()
    grille_klc()
    bumper_showa()
    bumper_klc()
    bumper_outclass()
    lib.export(os.path.abspath(OUT))


build()
print('exported', os.path.abspath(OUT))
