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
from lib import P, box, tube, sweep, group, material, rounded_rect, circle, fillet, annulus, sphere, text, cut, lathe, prism  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
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
    top = ROOF_Y_MID + 62                      # tray just clears the roof crown
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
    root = group('snorkel_safari')
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
    root = group('sideStep_arb')
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
    root = group('ladder_fr')
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
    root = group(f'awning_arb_{side}')
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


def nose_z(x):
    """How far forward the body's own nose reaches at this x, in mm, fitted
    to the model: flat across the middle, then falling away fast once past
    the headlights (1775 at the centre, 1675 at 600, 1520 at 800). A bumper
    that ignores this ends up standing 100 mm in front of the wings."""
    return 1775 - 0.0013 * max(0.0, abs(x) - 350) ** 2


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
            b = box(f'bezel{k}', (x, y, z - 14), (232, 232, 30), mat, root, bevel=14)
            c = lib.cylinder(f'cutB{k}', (x, y, z), (0, 0, 1), 192, 60, mat, None, n=48)
            cut(b, [c])
    for k, (x, y) in enumerate(SIGNAL):
        annulus(f'sigBezel{k}', (x, y, face_z(x) - 9), 39, 48, 16, mat, root)


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
    ow, oh = 520, 200
    grille_panel('panel', root, TEXBLACK, (ow, oh, 858))
    lamp_bezels(root, TEXBLACK, 'square')
    n = 12                                                   # thin vertical slats across the opening (product photo)
    for k in range(n):
        x = -ow / 2 + 22 + k * (ow - 44) / (n - 1)
        box(f'slat{k}', (x, 858, face_z(0) + 2), (16, oh - 14, 22), TEXBLACK, root, bevel=3)
    text('script', 'Suzuki', (0, 862, face_z(0) + 16), 60, 3, CHROME, root,
         font='/System/Library/Fonts/Supplemental/Zapfino.ttf' if os.path.exists('/System/Library/Fonts/Supplemental/Zapfino.ttf') else None)
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
    text('suzuki', 'SUZUKI', (0, 955, face_z(0) + 9), 42, 3, material('LabelWhite', 0xf0f0ec, rough=0.6), root)
    return root


# Owner's grille (from the photos): flat black panel, seven horizontal slats
# across the full opening between squared lamp bezels, bold white SUZUKI
# lettering standing over the slats, square indicator bezels.
def grille_owner():
    root = group('grille_hbar_suzuki')
    ow, oh = 580, 215
    grille_panel('panel', root, TEXBLACK, (ow, oh, 858))
    lamp_bezels(root, TEXBLACK, 'square')
    for k in range(5):                                       # owner's KLC Nostalgic: five bars over fine mesh
        y = 858 - oh / 2 + 22 + k * 43
        box(f'slat{k}', (0, y, face_z(0) + 1), (ow - 10, 26, 22), TEXBLACK, root, bevel=4)
    for s in (-1, 1):                                        # two thin vertical dividers splitting the bars
        box(f'divider{s}', (s * 150, 858, face_z(0) + 4), (8, oh - 24, 16), TEXBLACK, root, bevel=1)
    wire_mesh(root, BLACK, 0, 858, face_z(0) - 20, ow - 10, oh - 10, pitch=9)
    box('backing', (0, 858, face_z(0) - 32), (ow, oh, 3), RUBBER, root, bevel=0)
    text('suzuki', 'SUZUKI', (0, 862, face_z(0) + 16), 56, 5, material('LabelWhite', 0xf0f0ec, rough=0.6), root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    for k, (x, y) in enumerate(SIGNAL):
        annulus(f'sigBezel{k}', (x, y, face_z(x) + 14), 39, 50, 10, TEXBLACK, root)
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
    """KLC Heritage Traditional Bumper 74 in ivory (the black one is
    bumper_tube_heritage): the colour is the product, not the car's paint."""
    root = group('frontBumper_klc_trad')
    PAINT = material('KlcIvory', 0xe6dfcd, rough=0.5, metal=0.1)
    y1, y2 = 615, 545
    tube('upper', [(-650, y1, 1690), (650, y1, 1690)], 60, PAINT, root)
    tube('lower', [(-330, y2, 1660), (330, y2, 1660)], 50, PAINT, root)
    for s in (-1, 1):
        tube(f'link{s}', [(s * 250, y2, 1660), (s * 250, y1, 1690)], 30, PAINT, root)
        box(f'fogBox{s}', (s * 340, y2 - 10, 1640), (100, 100, 90), PAINT, root, bevel=6)
        fog_lamp(root, s * 340, y2 - 10, 1688, PAINT, dia=80)
        tube(f'upright{s}', [(s * 330, 420, 1500), (s * 330, y1 - 20, 1682)], 45, PAINT, root)
    number_plate(root, 520, 1682)
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
    path = [(-700, y, 1420), (-600, y, 1650), (600, y, 1650), (700, y, 1420)]
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


# ======================================================================== RIMS
# Wheels are modelled once at 16 x 7J with the axle along X and the face at
# +X; the page scales the diameter and width to the size chosen and tints the
# face material (RimFace). Five designs: the JB74 alloy (five paired spokes),
# a JL steel wheel with eight vents, a six-spoke forged look (TE37 XT /
# Bradley V), an eight-spoke steel-look (WILDBOAR / XTREME-J) and a bolted
# beadlock ring.
RIM_R, RIM_W = 203.2, 178.0
RIM_FACE = material('RimFace', 0xc8ccd0, rough=0.35, metal=0.8)
RIM_DARK = material('RimBarrel', 0x0f1113, rough=0.7, metal=0.4)
NUT = material('LugNut', 0xd8dadd, rough=0.3, metal=1.0)


def rim(style):
    root = group(f'rim_{style}')
    R, W = RIM_R, RIM_W
    # barrel with both lips, as one revolved shell
    prof = [(R, -W / 2), (R + 14, -W / 2), (R + 14, -W / 2 + 8), (R + 2, -W / 2 + 12), (R + 2, W / 2 - 14),
            (R + 16, W / 2 - 8), (R + 16, W / 2), (R + 4, W / 2), (R - 4, W / 2 - 6), (R - 4, -W / 2 + 6), (R - 8, -W / 2 + 2)]
    lathe('barrel', prof, RIM_DARK, root)
    dish = W / 2 - (24 if style in ('steel', 'daytona', 'moon', 'slot5') else 38)   # face plane, inset from the outer lip
    face_r = R - 6
    # the face: a disc with the windows cut out, spokes are what remains
    face = lathe('face', [(0, dish - 6), (0, dish + 6), (face_r, dish + 10), (face_r, dish - 12)], RIM_FACE, root, n=96)
    cutters = []
    hub_r = 0.30 * R
    if style == 'steel':
        for k in range(8):
            a = 2 * math.pi * k / 8
            cutters.append(lib.cylinder(f'vent{k}', (dish, 0.64 * R * math.sin(a), 0.64 * R * math.cos(a)), (1, 0, 0), 46, 60, RIM_FACE, None, n=24))
    elif style == 'moon':
        pass                                                   # a moon disc: the face is left solid
    elif style == 'daytona':
        # rally steel: ten slots, each a rounded bar lying along the radius
        for k in range(10):
            a = 2 * math.pi * k / 10
            for r in (0.52 * R, 0.76 * R):
                c = box(f'slot{k}{int(r)}', (dish, r * math.sin(a), r * math.cos(a)), (60, 24, 58), RIM_FACE, None,
                        bevel=11, rot=Matrix.Rotation(-a, 3, 'X'))
                c.modifiers['bevel'].segments = 4
                cutters.append(c)
    elif style == 'slot5':
        # five wide slots lying across the face, a rounded bar each
        for k in range(5):
            a = 2 * math.pi * k / 5
            c = box(f'slot{k}', (dish, 0.60 * R * math.sin(a), 0.60 * R * math.cos(a)), (60, 40, 150), RIM_FACE, None,
                    bevel=19, rot=Matrix.Rotation(-a, 3, 'X'))
            c.modifiers['bevel'].segments = 5
            cutters.append(c)
    else:
        n, spoke = {'stock': (5, 0.36), 'six': (6, 0.24), 'eight': (8, 0.22), 'ten': (10, 0.17),
                    'watanabe': (8, 0.26), 'eightpin': (8, 0.26), 'beadlock': (8, 0.26)}[style]
        for k in range(n):
            a0 = 2 * math.pi * k / n
            half = math.pi / n - spoke / 2                      # half the angular width of a window
            r_in, r_out = hub_r + 8, face_r - 14
            poly = []
            for t in range(9):                                  # outer arc
                a = a0 - half + 2 * half * t / 8
                poly.append((r_out * math.sin(a), r_out * math.cos(a)))
            for t in range(9):                                  # inner arc, back
                a = a0 + half - 2 * half * t / 8
                poly.append((r_in * math.sin(a), r_in * math.cos(a)))
            pts = [(0, y, z) for (y, z) in poly]
            rounded = [(p.y, p.z) for p in fillet(pts + [pts[0]], 14, steps=3)]
            cutters.append(prism(f'win{k}', rounded, dish - 40, dish + 40, RIM_FACE, None))
        if style == 'stock':                                     # JB74 alloy: each spoke carries a slot
            for k in range(n):
                a = 2 * math.pi * k / n + math.pi / n
                cutters.append(box(f'slot{k}', (dish, 0.62 * R * math.sin(a), 0.62 * R * math.cos(a)), (60, 22, 56), RIM_FACE, None, bevel=0,
                                   rot=Matrix.Rotation(-a, 3, 'X')))
    cutters.append(lib.cylinder('bore', (dish, 0, 0), (1, 0, 0), 60, 60, RIM_FACE, None, n=32))
    for k in range(5):                                           # 5 x 139.7 lug holes
        a = 2 * math.pi * k / 5
        cutters.append(lib.cylinder(f'lug{k}', (dish, 69.85 * math.sin(a), 69.85 * math.cos(a)), (1, 0, 0), 30, 60, RIM_FACE, None, n=16))
    cut(face, cutters)
    for k in range(5):
        a = 2 * math.pi * k / 5
        nut = lib.cylinder(f'nut{k}', (dish + 6, 69.85 * math.sin(a), 69.85 * math.cos(a)), (1, 0, 0), 21, 20, NUT, root, n=6)
    if style == 'moon':                                        # a smooth disc laid over the whole face
        lib.cylinder('moonDisc', (dish + 24, 0, 0), (1, 0, 0), 1.52 * R, 7, RIM_FACE, root, n=64, bevel=4)
    elif style == 'slot5':                                     # removable chrome centre plate
        lib.cylinder('plate', (dish + 9, 0, 0), (1, 0, 0), 168, 7, NUT, root, n=44, bevel=3)
    elif style in ('watanabe', 'daytona'):
        pass                                                   # these run with the hub open, no cap
    else:
        lib.cylinder('cap', (dish + 3, 0, 0), (1, 0, 0), 58, 8, RIM_DARK, root, n=32)
    if style == 'eightpin':                                    # pin bolts on the face, rivets round the lip
        for k in range(8):
            a = 2 * math.pi * k / 8 + math.pi / 8
            lib.cylinder(f'pin{k}', (dish + 8, 0.74 * R * math.sin(a), 0.74 * R * math.cos(a)), (1, 0, 0), 15, 10, NUT, root, n=8)
        for k in range(28):
            a = 2 * math.pi * k / 28
            lib.cylinder(f'rivet{k}', (W / 2 - 6, (R + 8) * math.sin(a), (R + 8) * math.cos(a)), (1, 0, 0), 10, 10, NUT, root, n=6)
    if style == 'beadlock':
        annulus_x = W / 2 + 4
        ring = lathe('ring', [(R - 10, annulus_x - 4), (R + 20, annulus_x - 4), (R + 20, annulus_x + 10), (R - 10, annulus_x + 10)],
                     material('BeadlockRing', 0xb8410f, rough=0.45, metal=0.3), root)
        for k in range(24):
            a = 2 * math.pi * k / 24
            lib.cylinder(f'bolt{k}', (annulus_x + 12, (R + 5) * math.sin(a), (R + 5) * math.cos(a)), (1, 0, 0), 9, 8, NUT, root, n=6)
    return root


# ============================================================ OWNER'S CAR PARTS
# Modelled from the owner's photos of their black JB74 (parking-garage set):
# ARB BASE Rack with two round spots, tube front bumper with LED pods, tube
# rear bumper keeping the stock tail lamps, hoop-type tube ladder with a
# fire extinguisher, WLM guard carrying a flat fuel can and an axe, and
# riveted pocket-style flares.
ARB_W, ARB_L = 1285, 1545
RACK_TOP = ROOF_Y_MID + 62
RACK_ZC = (ROOF_Z_FRONT + ROOF_Z_REAR) / 2 - 20
WOOD = material('AxeHandle', 0xa07a4a, rough=0.7)
RED_LABEL = material('LabelRed', 0xb3261e, rough=0.5)


def roof_rack_arb():
    root = group('roofRack_arb')
    W, L, top = ARB_W, ARB_L, RACK_TOP
    deck = top - 45
    z0, z1 = RACK_ZC - L / 2, RACK_ZC + L / 2
    for s in (-1, 1):                                    # dovetail side rails
        sweep(f'rail{s}', [(s * (W / 2 - 22), deck + 22, z0), (s * (W / 2 - 22), deck + 22, z1)], rounded_rect(44, 45, 4), BLACK, root)
        for k in range(int((L - 60) // 38)):
            box(f'slot{s}{k}', (s * W / 2, deck + 22, z0 + 40 + k * 38), (2, 12, 20), TEXBLACK, root, bevel=0)
    for zz in (z0, z1):                                  # end rails
        sweep(f'end{zz}', [(-W / 2 + 44, deck + 22, zz + (22 if zz == z0 else -22)), (W / 2 - 44, deck + 22, zz + (22 if zz == z0 else -22))],
              rounded_rect(45, 44, 4), BLACK, root)
    n = 15                                               # planks across the car
    pitch = (L - 120) / (n - 1)
    for i in range(n):
        z = z0 + 60 + i * pitch
        box(f'plank{i}', (0, top - 8, z), (W - 88, 14, 78), BLACK, root, bevel=2)
        box(f'gap{i}', (0, top - 2, z + 44), (W - 88, 2, 10), TEXBLACK, root, bevel=0)
    for s in (-1, 1):                                    # six gutter legs
        for k in range(3):
            z = z0 + 170 + k * (L - 340) / 2
            yg = ROOF_Y_EDGE - 6
            leg = [(s * (GUTTER_X + 18), yg - 25, z), (s * (GUTTER_X + 18), yg + 40, z), (s * (W / 2 - 22), deck, z)]
            sweep(f'leg{s}{k}', [tuple(p) for p in fillet(leg, 30)], rounded_rect(64, 22, 5), BLACK, root)
            box(f'pad{s}{k}', (s * (GUTTER_X + 5), yg + 3, z), (40, 8, 64), RUBBER, root, bevel=2)
    box('deflector', (0, top - 50, z1 + 60), (W - 60, 80, 3), BLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-58), 3, 'X'))
    lbl = text('arbLabel', 'BASE RACK', (0, deck + 22, z0 - 24), 22, 1, material('LabelWhite', 0xf0f0ec, rough=0.6), root)
    lbl.rotation_euler = (0, 0, math.pi)                    # faces the rear, so it reads from behind
    return root


def roof_lights():
    root = group('roofLights')
    z = RACK_ZC + ARB_L / 2 + 10
    for s in (-1, 1):
        x, y = s * (ARB_W / 2 - 130), RACK_TOP + 105
        lib.cylinder(f'hsg{s}', (x, y, z - 40), (0, 0, 1), 180, 90, BLACK, root, n=40)
        annulus(f'bezel{s}', (x, y, z + 8), 78, 92, 12, BLACK, root, n=40)
        lib.cylinder(f'bowl{s}', (x, y, z + 2), (0, 0, 1), 156, 6, CHROME, root, n=40)
        lib.cylinder(f'lens{s}', (x, y, z + 6), (0, 0, 1), 160, 3, LENS, root, n=40)
        box(f'stem{s}', (x, y - 100, z - 40), (30, 110, 26), BLACK, root, bevel=3)
        box(f'foot{s}', (x, RACK_TOP - 44, z - 40), (70, 12, 70), BLACK, root, bevel=2)
        for k in (-1, 1):
            box(f'ear{s}{k}', (x + k * 96, y - 10, z - 40), (8, 60, 40), BLACK, root, bevel=2)
    return root


def bumper_tube_heritage():
    """KLC Traditional Bumper 74 with KC FLEX ERA 4 pods, from the owner's
    close-ups: a straight 76 mm upper tube with flat ends and two plate
    tabs under its middle; a shorter 76 mm lower tube set back with the
    square KC pods on its ends; a big flat "Heritage" panel below; the
    silver crossmember visible between the tubes."""
    root = group('frontBumper_tube_heritage')
    yu, zu = 640, 1694                                       # upper tube
    yl, zl = 520, 1652                                       # lower tube, set back
    tube('upper', [(-676, yu, zu), (676, yu, zu)], 76, TEXBLACK, root)
    tube('lower', [(-450, yl, zl), (450, yl, zl)], 76, TEXBLACK, root)
    for s in (-1, 1):
        lib.cylinder(f'capU{s}', (s * 678, yu, zu), (1, 0, 0), 78, 6, TEXBLACK, root, n=28)
        lib.cylinder(f'capL{s}', (s * 452, yl, zl), (1, 0, 0), 78, 6, TEXBLACK, root, n=28)
        # plate tabs under the upper tube, with their bolt heads on top
        box(f'tab{s}', (s * 120, yu - 55, zu + 6), (28, 60, 6), TEXBLACK, root, bevel=1)
        lib.cylinder(f'tabBolt{s}', (s * 120, yu + 40, zu), (0, 1, 0), 14, 8, STEEL, root, n=6)
        # KC FLEX ERA 4: square pod with a red bezel, two spots over two floods
        px, py, pz = s * 520, yl, zl + 20
        amber = material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0)
        kcred = material('KCRed', 0xa8231c, rough=0.45)
        body = box(f'pod{s}', (px, py, pz), (104, 104, 62), BLACK, root, bevel=22)
        body.modifiers['bevel'].segments = 5
        ring = box(f'podBezel{s}', (px, py, pz + 30), (100, 100, 12), kcred, root, bevel=24)
        ring.modifiers['bevel'].segments = 5
        face = box(f'podFace{s}', (px, py, pz + 33), (78, 78, 6), BLACK, root, bevel=12)
        face.modifiers['bevel'].segments = 4
        for (dx, dy, m) in ((-19, 19, amber), (19, 19, amber), (-19, -19, LENS), (19, -19, LENS)):
            lib.cylinder(f'cup{s}{dx}{dy}', (px + dx, py + dy, pz + 33), (0, 0, 1), 34, 8, CHROME, root, n=20)
            lib.cylinder(f'led{s}{dx}{dy}', (px + dx, py + dy, pz + 37), (0, 0, 1), 28, 3, m, root, n=20)
        box(f'podMount{s}', (px - s * 58, py, zl), (48, 26, 26), TEXBLACK, root, bevel=3)
        # chassis legs and tow hooks
        box(f'leg{s}', (s * 330, yu - 70, zu - 150), (60, 170, 180), TEXBLACK, root, bevel=3)
    box('plate', (0, yu - 125, zu + 32), (330, 165, 3), PLATE, root, bevel=1)   # demo plate on the tabs
    # Heritage panel: big flat plate hanging below the lower tube, slightly raked
    # the plate spans the whole span between the KC pods and hangs well below
    # the lower tube, raked back; the script sits low and left of centre
    panel = prism('panel', [(yl - 58, zl - 30), (yl - 252, zl - 66), (yl - 252, zl - 74), (yl - 58, zl - 38)], -524, 524, TEXBLACK, root)
    script = text('heritage', 'Heritage', (-120, yl - 176, zl - 60), 168, 70, TEXBLACK, None,
                  font='/System/Library/Fonts/Supplemental/Zapfino.ttf' if os.path.exists('/System/Library/Fonts/Supplemental/Zapfino.ttf') else None)
    cut(panel, [script])                                     # laser-cut script, open right through
    # what shows between the tubes: the galvanised crossmember and the bay
    box('crossmember', (0, 575, 1600), (1100, 70, 40), STEEL, root, bevel=4)
    box('bay', (0, 540, 1420), (1050, 320, 20), RUBBER, root, bevel=4)
    return root


def rear_bumper_tube():
    """Owner's rear bumper: one fat straight tube low across the back with
    squared end caps, plate wings above it carrying the stock tail lamps,
    exhaust tip out the right, tow hook and shackle underneath, mesh corner
    covers where the stock bumper used to wrap round."""
    root = group('rearBumper_tube')
    y, z = 430, -1650
    tube('bar', [(-745, y, z), (745, y, z)], 76, TEXBLACK, root)
    for s in (-1, 1):
        box(f'endCap{s}', (s * 752, y, z), (14, 96, 96), TEXBLACK, root, bevel=3)
        box(f'mount{s}', (s * 330, y + 30, z + 110), (70, 100, 220), TEXBLACK, root, bevel=4)
        # wing plate behind the tail lamp, lamp framed on it
        box(f'wing{s}', (s * 513, 545, -1568), (400, 250, 8), TEXBLACK, root, bevel=3)
        box(f'wingTop{s}', (s * 513, 665, -1575), (400, 8, 30), TEXBLACK, root, bevel=2)
        for (cx, cy, sx, sy) in ((0, 76, 370, 12), (0, -76, 370, 12), (-180, 0, 12, 160), (180, 0, 12, 160)):
            box(f'lampFrame{s}{cx}{cy}', (s * 513 + cx, 518 + cy, -1596), (sx, sy, 20), TEXBLACK, root, bevel=2)
        # corner cover with a hex-mesh vent
        box(f'corner{s}', (s * 740, 520, -1470), (50, 240, 180), TEXBLACK, root, bevel=6,
            rot=Matrix.Rotation(math.radians(-s * 25), 3, 'Z'))
    box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)
    box('plate', (0, 585, TAIL_Z - 6), (330, 165, 4), PLATE, root, bevel=1)
    ex = RIGHT * 400
    lib.cylinder('exhaust', (ex, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    lib.cylinder('exhaustIn', (ex + RIGHT * 38, 334, -1738), (RIGHT * 0.4, -0.06, -1), 50, 8, RUBBER, root, n=24)
    box('towHook', (RIGHT * 300, 365, -1600), (70, 26, 120), RED, root, bevel=5)
    annulus('shackle', (-RIGHT * 330, 360, -1630), 16, 28, 26, RED, root, n=24)
    box('shackleTab', (-RIGHT * 330, 385, -1600), (12, 60, 80), TEXBLACK, root, bevel=2)
    return root


def ladder_tube():
    """Hoop-type tube ladder on the hinge side; the rails climb the tailgate,
    bend forward over the roof edge and hook onto the rack's rear rail, as on
    the owner's car. Fire extinguisher clamped to the outer rail."""
    root = group('ladder_tube')
    s = RIGHT
    zf = TAIL_Z - 95
    xi, xo = s * 430, s * 610
    y0 = 600
    rack_rail_z = RACK_ZC - ARB_L / 2 + 40
    rack_y = RACK_TOP - 45 + 22
    for x in (xi, xo):
        rail = [(x, y0, zf), (x, 1420, zf), (x, 1580, TAIL_Z - 40), (x, rack_y + 30, rack_rail_z + 60), (x, rack_y, rack_rail_z + 60)]
        tube(f'rail{x}', rail, 32, BLACK, root, bend=110)
        box(f'hook{x}', (x, rack_y - 4, rack_rail_z + 30), (40, 20, 70), BLACK, root, bevel=3)
    tube('top', [(xi, rack_y + 30, rack_rail_z + 60), (xo, rack_y + 30, rack_rail_z + 60)], 32, BLACK, root)
    tube('bottom', [(xi, y0, zf), (xo, y0, zf)], 32, BLACK, root)
    for k in range(2):
        y = 850 + k * 300
        tube(f'rung{k}', [(xi, y, zf), (xo, y, zf)], 26, BLACK, root)
    for y in (650, 1300):
        for x in (xi, xo):
            box(f'standoff{x}{y}', (x, y, (TAIL_Z + zf) / 2), (34, 34, abs(TAIL_Z - zf)), BLACK, root, bevel=3)
    ex, ey, ez = (xi + xo) / 2, 1010, zf - 75                # on the ladder face, between the rails
    lib.cylinder('extBody', (ex, ey, ez), (0, 1, 0), 88, 380, RUBBER, root, n=28)
    lib.cylinder('extBand', (ex, ey + 40, ez), (0, 1, 0), 90, 90, RED_LABEL, root, n=28)
    lib.cylinder('extNeck', (ex, ey + 205, ez), (0, 1, 0), 40, 30, CHROME, root, n=16)
    box('extLever', (ex, ey + 235, ez + 10), (30, 20, 90), BLACK, root, bevel=3)
    for y in (ey - 110, ey + 110):
        box(f'clamp{y}', (ex, y, (ez + zf) / 2), (abs(xo - xi) + 30, 24, abs(ez - zf) + 20), BLACK, root, bevel=3)
    return root


def decals():
    """Owner's door lettering: MODEL:3BA-JB74W with two lines of small print,
    and the WLM mark on each guard. Thin white text standing 1 mm proud."""
    root = group('decals')
    white = material('LabelWhite', 0xf0f0ec, rough=0.6)
    for s in (-1, 1):
        for i, (line, size, dy) in enumerate((('MODEL:3BA-JB74W', 26, 0), ('PART TIME 4-WHEEL DRIVE', 11, -30), ('5-SPEED MANUAL', 11, -46))):
            ob = text(f'door{s}{i}', line, (s * 707, 1030 + dy, 300), size, 1, white, root)
            ob.rotation_euler = (0, 0, math.radians(90 * s))
            ob.location = P(s * 707, 1030 + dy, 300)
    return root


def guard_can():
    """Flat 7.5 L can and an axe on the RIGHT window guard (owner's photos):
    can forward with its cap on the forward top corner, a round centre boss
    with a latch bar, an octagonal raised rim; axe at the rear end, head up,
    blade forward under a tan leather sheath, two black band clamps."""
    root = group('guardCan')
    s = RIGHT
    q = QUARTER
    cz, cy = (q['z0'] + q['z1']) / 2, (q['y0'] + q['y1']) / 2 + 20
    face = s * 716
    czc = cz + 120                                           # can centre (forward half)
    can = box('can', (face + s * 50, cy - 10, czc), (100, 340, 440), TEXBLACK, root, bevel=26)
    can.modifiers['bevel'].segments = 4
    rim = [(cy + 120, czc - 210), (cy + 160, czc - 120), (cy + 160, czc + 120), (cy + 120, czc + 210),
           (cy - 150, czc + 210), (cy - 180, czc + 120), (cy - 180, czc - 120), (cy - 150, czc - 210)]
    prism('canRim', rim, face + s * 96, face + s * 106, TEXBLACK, root)
    box('canField', (face + s * 100, cy - 15, czc), (4, 250, 330), TEXBLACK, root, bevel=2)
    lib.cylinder('boss', (face + s * 106, cy - 20, czc), (1, 0, 0), 200, 8, TEXBLACK, root, n=32)
    box('latch', (face + s * 112, cy - 20, czc + 20), (10, 24, 110), BLACK, root, bevel=3)
    box('handleSlot', (face + s * 100, cy + 130, czc), (6, 26, 120), RUBBER, root, bevel=1)
    lib.cylinder('cap', (face + s * 40, cy + 140, czc + 235), (0, 0, 1), 64, 40, TEXBLACK, root, n=20)
    box('label', (face + s * 101, cy - 130, czc - 40), (2, 40, 110), material('LabelGrey', 0x8a8d90, rough=0.6), root, bevel=0.5)
    for z in (czc - 180, czc + 160):
        box(f'strap{z}', (face + s * 55, cy - 10, z), (114, 36, 24), BLACK, root, bevel=3)
    # axe at the rear end of the guard
    ax = cz - 250
    lib.cylinder('handle', (face + s * 30, cy - 10, ax), (0, 1, 0), 26, 480, WOOD, root, n=14)
    box('eye', (face + s * 30, cy + 240, ax), (34, 70, 44), STEEL, root, bevel=5)
    prism('bit', [(cy + 205, ax + 22), (cy + 275, ax + 22), (cy + 300, ax + 120), (cy + 180, ax + 120)], face + s * 18, face + s * 42, STEEL, root)
    box('poll', (face + s * 30, cy + 240, ax - 42), (30, 44, 40), STEEL, root, bevel=4)
    leather = material('Leather', 0xb98a55, rough=0.75)
    prism('sheath', [(cy + 170, ax + 30), (cy + 285, ax + 30), (cy + 310, ax + 135), (cy + 150, ax + 135)], face + s * 12, face + s * 48, leather, root)
    for zz in (ax + 70, ax + 115):
        lib.cylinder(f'stud{zz}', (face + s * 50, cy + 280, zz), (1, 0, 0), 14, 4, material('Brass', 0xb08d3c, rough=0.4, metal=1.0), root, n=10)
    for y in (cy - 170, cy + 110):                           # black band clamps with a shackle on the outside
        box(f'axeClamp{y}', (face + s * 20, y, ax), (44, 20, 60), BLACK, root, bevel=3)
        box(f'shackle{y}', (face + s * 26, y, ax - 50), (24, 18, 30), BLACK, root, bevel=4)
    return root


def guard_board():
    """Perforated recovery board on the LEFT window guard: about half the
    guard's height, centred, a grid of square holes, strapped at both ends."""
    root = group('guardBoard')
    s = -RIGHT
    q = QUARTER
    cz, cy = (q['z0'] + q['z1']) / 2, (q['y0'] + q['y1']) / 2 + 20
    face = s * 716
    board = box('board', (face + s * 18, cy - 10, cz), (30, 240, 700), BLACK, root, bevel=10)
    board.modifiers['bevel'].segments = 3
    for i in range(10):
        for j in range(3):
            box(f'hole{i}{j}', (face + s * 34, cy - 10 - 70 + j * 70, cz - 315 + i * 70), (4, 36, 36), RUBBER, root, bevel=0)
    for z in (cz - 250, cz + 250):
        box(f'strap{z}', (face + s * 20, cy - 10, z), (40, 250, 24), STEEL, root, bevel=3)
    return root


def shovel():
    """Black folding shovel along the rack's right rail, blade to the rear:
    D-grip, tube shaft with a collar, folding hinge, dished blade."""
    root = group('shovel')
    s = RIGHT
    x = s * (ARB_W / 2 - 40)
    y = RACK_TOP + 40
    zc = RACK_ZC - 250
    lib.cylinder('shaft', (x, y, zc + 320), (0, 0, 1), 28, 640, BLACK, root, n=14)
    tube('dgrip', [(x, y, zc + 640), (x, y + 60, zc + 690), (x, y + 60, zc + 760), (x, y, zc + 800), (x, y, zc + 640)], 22, BLACK, root, bend=30)
    lib.cylinder('collar', (x, y, zc + 10), (0, 0, 1), 40, 50, STEEL, root, n=14)
    box('hinge', (x, y, zc - 20), (44, 30, 40), STEEL, root, bevel=4)
    lib.cylinder('hingePin', (x, y, zc - 20), (1, 0, 0), 14, 56, STEEL, root, n=8)
    pouch = box('pouch', (x, y - 4, zc - 190), (230, 44, 340), CANVAS, root, bevel=22)
    pouch.modifiers['bevel'].segments = 4
    box('pouchFlap', (x, y + 20, zc - 60), (120, 6, 90), WEBBING, root, bevel=2)
    box('pouchStrap', (x, y - 4, zc - 190), (240, 46, 30), WEBBING, root, bevel=2)
    for z in (zc + 120, zc + 520):
        box(f'clamp{z}', (x, y - 30, z), (46, 34, 34), BLACK, root, bevel=4)
        box(f'clampFoot{z}', (x, y - 52, z), (60, 10, 50), BLACK, root, bevel=2)
    return root


def revolve_arc(name, profile, centre_y, centre_z, a0, a1, mat, parent, side=1, steps=28):
    """Revolve a closed (r, x) profile around the wheel axle between angles
    a0..a1 (degrees, 0 = forward, 90 = up). Ends are capped."""
    bm = bmesh.new()
    rings = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        rings.append([bm.verts.new(P(side * x, centre_y + r * math.sin(a), centre_z + r * math.cos(a))) for (r, x) in profile])
    k = len(profile)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return lib.new_object(name, bm, mat, parent, smooth=True)


def flares():
    """Pocket-style riveted look on the STOCK arches (owner's choice): six
    square black pockets along each arch's outer face, a silver hex bolt
    head in each; the stock shells stay, rendered matte."""
    root = group('flares')
    for s in (-1, 1):
        for z in (CAR['anchors']['frontAxleZ'], CAR['anchors']['rearAxleZ']):
            for t in range(11):
                a = math.radians(18 + 144 * t / 10)
                r, x = 478, 786
                lib.cylinder(f'rivet{s}{z}{t}', (s * x, 346 + r * math.sin(a), z + r * math.cos(a)), (1, 0, 0), 15, 7, STEEL, root, n=6)
    return root


# ============================================================ SNORKEL VARIANTS
# All on the vehicle's RIGHT (the 1.5L airbox side). The "no-drill" kits
# (Bravo, Urnieta, Supa-Sleek) replace the black fender-corner garnish at the
# A-pillar base instead of cutting the wing, so their bodies start there.
PILLAR = [(660 + 40, 1160, 630), (640 + 40, 1400, 500), (612 + 40, 1580, 410)]   # x, y, z along the pillar (right side = -x)


def _pillar_path(side, off, top_y=1600):
    return [(side * 700, 990, 640), (side * (700 + off - 40), 1080, 640),
            (side * (660 + off), 1160, 630), (side * (640 + off), 1400, 500), (side * (612 + off), top_y, 405)]


def snorkel_bravo(side=RIGHT):
    """Bravo Snorkel SSJN: squared textured body hugging the pillar from a base
    plate on the fender corner; 3.5in elbow head turned outward with a mesh
    intake on its side face."""
    root = group('snorkel_bravo')
    off = 44
    pts = fillet(_pillar_path(side, off, 1590), 90, steps=8)
    sweep('body', [tuple(p) for p in pts], rounded_rect(96, 80, 18, 4), TEXBLACK, root)
    box('basePlate', (side * 712, 1000, 620), (60, 40, 170), TEXBLACK, root, bevel=6)
    hx, hz = side * (612 + off), 405
    tube('neck', [(hx, 1585, hz), (hx, 1640, hz)], 89, TEXBLACK, root)
    # elbow head: turns forward, flat cap, mesh intake facing the nose
    head = tube('elbow', [(hx, 1630, hz), (hx, 1690, hz), (hx, 1700, hz + 60)], 89, TEXBLACK, root, bend=45)
    box('cap', (hx, 1700, hz + 62), (100, 100, 30), TEXBLACK, root, bevel=8)
    for k in range(5):
        box(f'grille{k}', (hx, 1668 + k * 16, hz + 80), (76, 6, 4), RUBBER, root, bevel=0)
    for (y, z, x) in ((1260, 575, 655), (1500, 445, 625)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_urnieta(side=RIGHT):
    """URNIETA Salado: rectangular ABS body from the fender corner, round
    collar, then a rectangular head with forward louvres and slotted sides."""
    root = group('snorkel_urnieta')
    off = 42
    pts = fillet(_pillar_path(side, off, 1570), 80, steps=8)
    sweep('body', [tuple(p) for p in pts], rounded_rect(90, 70, 10, 3), TEXBLACK, root)
    box('basePlate', (side * 712, 1000, 620), (60, 40, 170), TEXBLACK, root, bevel=6)
    hx, hz = side * (612 + off), 405
    lib.cylinder('collar', (hx, 1590, hz), (0, 1, 0), 96, 40, TEXBLACK, root)
    box('head', (hx, 1670, hz), (140, 110, 120), TEXBLACK, root, bevel=10)
    for k in range(5):
        box(f'louvre{k}', (hx, 1632 + k * 19, hz + 62), (118, 6, 6), RUBBER, root, bevel=0)
    for k in range(6):
        box(f'slot{k}', (hx + side * 72, 1670, hz - 45 + k * 18), (4, 80, 6), RUBBER, root, bevel=0)
    box('lid', (hx, 1728, hz), (146, 8, 126), TEXBLACK, root, bevel=3)
    for (y, z, x) in ((1260, 575, 655), (1500, 445, 625)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_precleaner(side=RIGHT):
    """Safari-type body with a cyclonic pre-cleaner bowl instead of the ram."""
    root = group('snorkel_precleaner')
    off = 40
    wing_y = top_y(side * 700, 660)
    path = [(side * 705, wing_y - 60, 660), (side * 705, wing_y + 80, 660), (side * (660 + off), 1160, 630),
            (side * (640 + off), 1400, 500), (side * (612 + off), 1560, 410), (side * (612 + off), 1600, 405)]
    pts = fillet(path, 110, steps=10)
    sweep('body', [tuple(p) for p in pts], rounded_rect(95, 75, 30, 5), TEXBLACK, root)
    box('wingSeal', (side * 705, wing_y + 6, 660), (140, 10, 140), RUBBER, root, bevel=4)
    hx, hz = side * (612 + off), 405
    lib.cylinder('stem', (hx, 1625, hz), (0, 1, 0), 89, 50, TEXBLACK, root)
    lib.cylinder('bowl', (hx, 1690, hz), (0, 1, 0), 180, 80, material('ClearBowl', 0xd9dde2, rough=0.1, metal=0.0), root, n=32)
    lib.cylinder('bowlBase', (hx, 1652, hz), (0, 1, 0), 150, 12, TEXBLACK, root, n=32)
    lib.cylinder('bowlTop', (hx, 1734, hz), (0, 1, 0), 184, 10, TEXBLACK, root, n=32)
    lib.cylinder('lid', (hx, 1760, hz), (0, 1, 0), 150, 42, TEXBLACK, root, n=32)
    sphere('knob', (hx, 1786, hz), 40, TEXBLACK, root)
    for (y, z, x) in ((1260, 575, 655), (1500, 445, 625)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_sleek(side=RIGHT):
    """Mega Jimny Supa-Sleek: 2in tube tight to the pillar from a flat
    fender-corner cover, small rear-facing scoop at the top."""
    root = group('snorkel_sleek')
    off = 30
    pts = fillet(_pillar_path(side, off, 1585), 70, steps=8)
    tube('body', [tuple(p) for p in pts], 51, TEXBLACK, root, bend=70)
    box('cover', (side * 712, 1000, 620), (50, 34, 180), TEXBLACK, root, bevel=8)
    hx, hz = side * (612 + off), 405
    box('scoop', (hx, 1605, hz - 30), (70, 60, 110), TEXBLACK, root, bevel=8,
        rot=Matrix.Rotation(math.radians(-35 * side), 3, 'X'))
    box('scoopMouth', (hx, 1620, hz - 85), (54, 40, 4), RUBBER, root, bevel=2)
    for (y, z, x) in ((1300, 555, 650),):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 16, 30), STEEL, root, bevel=2)
    return root


# ==================================================================== MIRRORS
# Both replace the stock door mirrors (hidden by the page). Mounted on the
# door's mirror triangle like the stock unit (front top corner of the door).
MIR_X, MIR_Y, MIR_Z = 705, 1165, 445        # door skin at the mirror triangle


def mirrors_urnieta():
    """URNIETA Salado: squarish 200 x 150 head inside a round-tube loop arm
    (~411 tall x 237 out) fixed top and bottom to the door."""
    root = group('mirrors_urnieta')
    for s in (-1, 1):
        x0 = s * MIR_X
        loop = [(x0, 1330, 485), (s * (MIR_X + 200), 1330, 485), (s * (MIR_X + 200), 1000, 485), (x0, 1000, 485)]
        tube(f'arm{s}', loop, 20, BLACK, root, bend=60)
        for y in (1330, 1000):
            box(f'base{s}{y}', (s * (MIR_X + 4), y, 482), (10, 50, 70), BLACK, root, bevel=3)
        # head faces the rear: wide across the car, thin front-to-back
        head = box(f'head{s}', (s * (MIR_X + 120), MIR_Y, 452), (200, 150, 34), BLACK, root, bevel=16)
        head.modifiers['bevel'].segments = 4
        box(f'glass{s}', (s * (MIR_X + 120), MIR_Y, 433), (186, 136, 2), CHROME, root, bevel=0)
        box(f'stem{s}', (s * (MIR_X + 160), MIR_Y, 470), (24, 24, 30), BLACK, root, bevel=3)
    return root


def mirrors_damd():
    """DAMD Truck Mirror, measured off the owner's photos: tall 150 x 250 head
    with big radii hanging inside a U of 20 mm tube; the top arm leaves a
    flat plate bracket at the door's top front corner, the vertical run passes
    behind the head's outer third, the bottom arm returns to a hinge block on
    a plate at the cowl beside the door hinge."""
    root = group('mirrors_damd')
    for s in (-1, 1):
        xd = s * MIR_X
        xo = s * (MIR_X + 175)                     # vertical tube
        loop = [(xd + s * 6, 1315, 505), (xo, 1315, 490), (xo, 1000, 490), (xd + s * 6, 1000, 505)]
        tube(f'arm{s}', loop, 20, BLACK, root, bend=55)
        # top bracket: plate against the pillar with a clamp on the tube
        box(f'topPlate{s}', (s * (MIR_X - 2), 1300, 525), (6, 70, 110), BLACK, root, bevel=1)
        box(f'topClamp{s}', (s * (MIR_X + 22), 1315, 505), (44, 30, 30), BLACK, root, bevel=4)
        # bottom: hinge block on a plate at the cowl
        box(f'botPlate{s}', (s * (MIR_X - 6), 985, 540), (70, 6, 110), BLACK, root, bevel=1)
        lib.cylinder(f'hinge{s}', (s * (MIR_X + 14), 1005, 505), (0, 1, 0), 34, 60, BLACK, root, n=16)
        box(f'botClamp{s}', (s * (MIR_X + 30), 1000, 505), (40, 26, 26), BLACK, root, bevel=3)
        # head: 150 x 250 x 50 shell, corner radius ~30, glass in the rear face
        # head faces the rear (glass plane across the car); the vertical tube runs just ahead of it
        head = box(f'head{s}', (s * (MIR_X + 112), 1160, 452), (190, 258, 58), BLACK, root, bevel=32)
        head.modifiers['bevel'].segments = 6
        box(f'glass{s}', (s * (MIR_X + 112), 1160, 422), (166, 232, 2), CHROME, root, bevel=0)
        box(f'glassRim{s}', (s * (MIR_X + 112), 1160, 424), (176, 242, 2), RUBBER, root, bevel=0)
        # pivot from the vertical tube to the head's front face
        box(f'pivot{s}', (s * (MIR_X + 160), 1165, 486), (36, 40, 20), BLACK, root, bevel=3)
    return root


def pillar_pods(sides=(-1, 1), suffix=''):
    """Two small round pods stacked on one bracket at the cowl beside the
    A-pillar base (owner's car): amber above, white below, facing forward."""
    root = group('pillarPods' + suffix)
    amber = material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0)
    for s in sides:
        x, z = s * 688, 600
        box(f'bracket{s}', (s * 674, 1150, z - 25), (8, 130, 60), BLACK, root, bevel=1)
        box(f'foot{s}', (s * 690, 1084, z - 25), (40, 6, 60), BLACK, root, bevel=1)
        for (y, dia, lens) in ((1205, 70, amber), (1140, 58, LENS)):
            lib.cylinder(f'hsg{s}{y}', (x, y, z - 26), (0, 0, 1), dia, 52, BLACK, root, n=24)
            annulus(f'bezel{s}{y}', (x, y, z + 1), dia / 2 - 8, dia / 2 + 1, 6, BLACK, root, n=24)
            lib.cylinder(f'lens{s}{y}', (x, y, z), (0, 0, 1), dia - 16, 3, lens, root, n=24)
            box(f'ear{s}{y}', (s * 680, y, z - 26), (14, 16, 26), BLACK, root, bevel=2)
    return root



# ============================================================ MORE VARIANTS
# Generic builders so each catalogue entry only supplies dimensions.
def rack_platform(pid, W, L, slat_dir='across', slats=None, rail=(50, 45), legs=6, deflector=True, mesh=False, top=None):
    """Flat aluminium platform on gutter legs. slat_dir 'across' (Front Runner,
    ARB) or 'along' (Yakima LockNLoad, Rhino Pioneer)."""
    root = group(f'roofRack_{pid}')
    top = top or RACK_TOP
    deck = top - rail[1]
    z0, z1 = RACK_ZC - L / 2, RACK_ZC + L / 2
    for s in (-1, 1):
        sweep(f'rail{s}', [(s * (W / 2 - rail[0] / 2), deck + rail[1] / 2, z0), (s * (W / 2 - rail[0] / 2), deck + rail[1] / 2, z1)],
              rounded_rect(rail[0], rail[1], 4), BLACK, root)
        box(f'railSlot{s}', (s * W / 2, deck + rail[1] / 2, RACK_ZC), (2, 10, L - 20), TEXBLACK, root, bevel=0)
    for zz, k in ((z0, 1), (z1, -1)):
        sweep(f'end{zz}', [(-W / 2 + rail[0], deck + rail[1] / 2, zz + k * rail[0] / 2), (W / 2 - rail[0], deck + rail[1] / 2, zz + k * rail[0] / 2)],
              rounded_rect(rail[1], rail[0], 4), BLACK, root)
    if slat_dir == 'across':
        n = slats or int((L - 60) // 110)
        pitch = (L - 60 - 80) / (n - 1)
        for i in range(n):
            z = z0 + 70 + i * pitch
            box(f'slat{i}', (0, top - 8, z), (W - 2 * rail[0], 15, 62), BLACK, root, bevel=2)
            box(f'slot{i}', (0, top, z), (W - 2 * rail[0] - 20, 1.5, 9), TEXBLACK, root, bevel=0)
    else:
        n = slats or int((W - 2 * rail[0]) // 75)
        pitch = (W - 2 * rail[0] - 60) / (n - 1)
        for i in range(n):
            x = -W / 2 + rail[0] + 30 + i * pitch
            box(f'slat{i}', (x, top - 8, RACK_ZC), (58, 15, L - 2 * rail[0] - 10), BLACK, root, bevel=2)
            box(f'slot{i}', (x, top, RACK_ZC), (9, 1.5, L - 2 * rail[0] - 30), TEXBLACK, root, bevel=0)
    if mesh:                                             # horizontal mesh floor under the slats
        mw, ml = W - 2 * rail[0], L - 2 * rail[0]
        for i in range(int(mw // 40) + 1):
            box(f'mfx{i}', (-mw / 2 + i * 40, top - 20, RACK_ZC), (3, 3, ml), BLACK, root, bevel=0)
        for j in range(int(ml // 40) + 1):
            box(f'mfz{j}', (0, top - 20, RACK_ZC - ml / 2 + j * 40), (mw, 3, 3), BLACK, root, bevel=0)
    per = legs // 2
    for s in (-1, 1):
        for k in range(per):
            z = z0 + 170 + k * (L - 340) / max(1, per - 1)
            yg = ROOF_Y_EDGE - 6
            leg = [(s * (GUTTER_X + 18), yg - 25, z), (s * (GUTTER_X + 18), yg + 40, z), (s * (W / 2 - rail[0] / 2), deck, z)]
            sweep(f'leg{s}{k}', [tuple(p) for p in fillet(leg, 30)], rounded_rect(64, 22, 5), BLACK, root)
            box(f'pad{s}{k}', (s * (GUTTER_X + 5), yg + 3, z), (40, 8, 64), RUBBER, root, bevel=2)
    if deflector:
        box('deflector', (0, top - 50, z1 + 60), (W - 60, 80, 3), BLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-58), 3, 'X'))
    return root


def awning_case(pid, side, L, W, H, mat, hard=True, hinge=False):
    """Roll-out awning on the rack's side rail: soft PVC bag (rounded) or
    aluminium hard case (crisp). `hinge` adds the 270-degree pivot housing at
    the rear end (batwing types)."""
    root = group(f'awning_{pid}_{side}')
    s = -RIGHT if side == 'left' else RIGHT
    rack_top = RACK_TOP
    # every case is centred on the roof, so it overhangs the same amount front
    # and rear -- never trailing a long tail off the back
    x, y, zc = s * (ARB_W / 2 + W / 2 - 30), rack_top + 40 - H / 2, RACK_ZC
    prof = rounded_rect(W, H, 8 if hard else min(W, H) * 0.4, 6)
    sweep('bag', [(x, y, zc - L / 2 + 20), (x, y, zc + L / 2 - 20)], prof, mat, root)
    for k in (-1, 1):
        z = zc + k * (L / 2 - 10)
        sweep(f'cap{k}', [(x, y, z - 18), (x, y, z + 18)], rounded_rect(W + 6, H + 6, 10 if hard else min(W, H) * 0.42, 6), BLACK, root)
    if not hard:
        for k in (-1, 1):
            box(f'strap{k}', (x, y, zc + k * 600), (W + 4, H + 4, 40), WEBBING, root, bevel=10)
        box('zip', (x + s * W / 2, y - 30, zc), (3, 8, L - 120), WEBBING, root, bevel=0)
    for k in (-1, 1):
        z = zc + k * min(600, L * 0.3)
        box(f'bracketH{k}', (s * (ARB_W / 2 + W / 2 - 30), y + H / 2 + 4, z), (W - 10, 8, 50), BLACK, root, bevel=2)
        box(f'bracketV{k}', (s * (ARB_W / 2 - 4), y + H / 4, z), (8, H / 2 + 20, 50), BLACK, root, bevel=2)
    if hinge:                                            # 270 types: pivot plate at the rear end, flush with the bag
        box('hinge', (x, y - 4, zc - L / 2 - 22), (W + 10, H + 8, 40), BLACK, root, bevel=6)
        lib.cylinder('pivot', (x, y - H / 2 - 30, zc - L / 2 - 22), (0, 1, 0), 36, 50, BLACK, root)
    return root


def side_step(pid, kind, tube_d=50, length=None, standoff=70, drop=40, pads=(), mat=None, plate_w=180, upturn=0):
    """kind: 'tube' (round tube, optional step pads), 'slider' (chassis-mounted
    bar with support tubes), 'plate' (flat step on brackets), 'armour' (sill
    guard hugging the sill face, no step), 'short' (small step under the door
    only). pads = [(width, length, z offset from centre), ...]."""
    root = group(f'sideStep_{pid}')
    mat = mat or TEXBLACK
    zf, zr = FRONT_ARCH_Z - 40, REAR_ARCH_Z + 40
    L = length or (zf - zr - 80)
    zc = (zf + zr) / 2
    y = SILL_Y - drop
    x = BODY_X + standoff
    for s in (-1, 1):
        if kind == 'plate':
            box(f'plate{s}', (s * (x - 10), y, zc), (plate_w, 30, L), mat, root, bevel=6)
            for i in range(int(L // 90)):
                box(f'hole{s}{i}', (s * (x - 10), y + 16, zc - L / 2 + 45 + i * 90), (plate_w - 70, 2, 30), RUBBER, root, bevel=0)
            for k, z in enumerate((zc - L * 0.35, zc, zc + L * 0.35)):
                box(f'brk{s}{k}', (s * (x - 110), y - 8, z), (200, 30, 60), mat, root, bevel=3)
        elif kind == 'armour':
            # plate wrapping the sill: vertical face plus a flat top lip
            box(f'face{s}', (s * (BODY_X + standoff / 2), SILL_Y + 40, zc), (standoff, 185, L), mat, root, bevel=8)
            box(f'top{s}', (s * (BODY_X + standoff / 2), SILL_Y + 133, zc), (standoff + 10, 6, L), mat, root, bevel=1)
            for i in range(int(L // 110)):
                lib.cylinder(f'bolt{s}{i}', (s * (BODY_X + standoff + 2), SILL_Y + 95, zc - L / 2 + 55 + i * 110), (1, 0, 0), 12, 5, STEEL, root, n=6)
        elif kind == 'short':
            # one small step under the door on a tube frame
            w, l = pads[0][0], pads[0][1]
            zd = zc + 120                                      # under the door
            box(f'tread{s}', (s * (x - 10), y, zd), (w, 10, l), ALU_CHEQ, root, bevel=2)
            for i in range(int(l // 40)):
                box(f'treadSlot{s}{i}', (s * (x - 10), y + 6, zd - l / 2 + 20 + i * 40), (w - 24, 2, 14), RUBBER, root, bevel=0)
            tube(f'frame{s}', [(s * (x - 10 - w / 2), y - 8, zd - l / 2), (s * (x - 10 + w / 2), y - 8, zd - l / 2), (s * (x - 10 + w / 2), y - 8, zd + l / 2), (s * (x - 10 - w / 2), y - 8, zd + l / 2)], tube_d, mat, root, bend=40)
            for k, z in enumerate((zd - l * 0.3, zd + l * 0.3)):
                box(f'brk{s}{k}', (s * (x - 90), y - 5, z), (160, 30, 50), mat, root, bevel=3)
        elif kind == 'slider':
            rail = [(s * (x - 60), y + 10, zf + 10), (s * x, y, zf - 90), (s * x, y, zr + 90), (s * (x - 60), y + 10, zr - 10)]
            tube(f'main{s}', rail, tube_d, mat, root, bend=110)
            for k, z in enumerate((zf - 170, zc, zr + 170)):
                tube(f'support{s}{k}', [(s * (x - 20), y, z), (s * 470, y + 30, z)], tube_d * 0.8, mat, root)
                box(f'bracket{s}{k}', (s * 455, y + 50, z), (70, 110, 90), mat, root, bevel=4)
        else:
            if upturn:                                   # ends curl up and in towards the sill (JST)
                rail = [(s * (x - 75), y + upturn, zf + 40), (s * (x - 20), y + upturn * 0.3, zf - 20), (s * x, y, zf - 120),
                        (s * x, y, zr + 120), (s * (x - 20), y + upturn * 0.3, zr + 20), (s * (x - 75), y + upturn, zr - 40)]
            else:
                rail = [(s * (x - 40), y, zf + 20), (s * x, y, zf - 60), (s * x, y, zr + 60), (s * (x - 40), y, zr - 20)]
            tube(f'main{s}', rail, tube_d, mat, root, bend=100)
            for k, z in enumerate((zc - L * 0.32, zc + L * 0.32)):
                box(f'brk{s}{k}', (s * (x - 80), y + 10, z), (160, 40, 60), mat, root, bevel=3)
        if kind in ('tube', 'slider'):
            for j, (pw, pl, zo) in enumerate(pads):
                box(f'pad{s}{j}', (s * (x - 10), y + tube_d / 2 + 2, zc + zo), (pw, 6, pl), ALU_CHEQ, root, bevel=1)
                for i in range(int(pl // 60)):
                    box(f'padSlot{s}{j}{i}', (s * (x - 10), y + tube_d / 2 + 6, zc + zo - pl / 2 + 30 + i * 60), (pw - 30, 2, 18), RUBBER, root, bevel=0)
    return root


# ===================================================== GENERIC FRONT / REAR / GRILLE
GUNMETAL = material('Gunmetal', 0x3a3d42, rough=0.45, metal=0.7)


def front_bar(pid, kind, W=1400, H=250, D=160, y=560, tube_d=60, hoop=False, fogs=False, skid=True, winch=False, mat=None, corners=True,
              hooks=False, bash=False, hump=False, badge=None, slot=False, bolts=False, fog_stalk=False, mesh_off=0):
    """kind: 'plate' (folded steel bar), 'box' (square tube), 'double' (two
    tubes), 'short' (short plate between the wheels), 'abs' (OEM-shaped short
    resin bumper with a mesh opening).

    The flags are what tells one product from another in a photo: red tow
    hooks (Armando), a bright skid plate under the face (Beyond, JAOS, MRK),
    a raised centre section (JAOS cowl), an air slot under the plate (KLC),
    exposed bolt heads (TOC), and fog lamps either recessed in the face or
    hung on brackets off the ends."""
    root = group(f'frontBumper_{pid}')
    mat = mat or TEXBLACK
    zf = 1745
    if kind in ('plate', 'short', 'abs'):
        # follow the nose: flat across the middle, wrapping back at the ends
        stand = 12 if kind != 'abs' else 4
        n = 13
        xs = [-W / 2 + W * i / (n - 1) for i in range(n)]
        path = [(x, y, min(zf, nose_z(x) + stand) - D / 2) for x in xs]
        sweep('body', [tuple(p) for p in fillet(path, 30, steps=3)], rounded_rect(D, H, 8 if kind != 'abs' else 30, 4), mat, root)
        if kind == 'abs':
            mw, mh = W * 0.45, H * 0.45
            wire_mesh(root, BLACK, mesh_off, y - 10, zf - 6, mw, mh, pitch=14)
            box('meshFrame', (mesh_off, y - 10, zf - 12), (mw + 20, mh + 20, 4), RUBBER, root, bevel=0)
    elif kind == 'box':
        xs = [-W / 2 + W * i / 8 for i in range(9)]
        sweep('body', [(x, y, min(zf - 40, nose_z(x) - 28)) for x in xs], rounded_rect(80, 80, 6, 3), mat, root)
    elif kind == 'double':
        xs = [-W / 2 + W * i / 8 for i in range(9)]
        for k, yy in enumerate((y + 45, y - 45)):
            tube(f'bar{k}', [(x, yy, min(zf - 30, nose_z(x) - 20)) for x in xs], tube_d, mat, root, bend=100)
        for s in (-1, 1):
            tube(f'link{s}', [(s * 300, y - 45, zf - 30), (s * 300, y + 45, zf - 30)], 30, mat, root)
    if hoop:
        tube('hoop', [(-400, y + H / 2 - 20, zf - 60), (-400, y + H / 2 + 140, zf - 60), (400, y + H / 2 + 140, zf - 60), (400, y + H / 2 - 20, zf - 60)], 48, mat, root, bend=110)
    if fogs:
        for s in (-1, 1):
            fog_lamp(root, s * 430, y - 20, zf + 4, mat, dia=90)
    if fog_stalk:                                            # fogs on brackets off the bar's ends
        for s in (-1, 1):
            box(f'fogArm{s}', (s * (W / 2 - 40), y + H / 2 - 10, zf - 30), (20, 90, 40), mat, root, bevel=2)
            fog_lamp(root, s * (W / 2 - 40), y + H / 2 + 50, zf - 10, mat, dia=110)
    if hump:                                                 # raised centre section of a moulded cowl
        box('hump', (0, y + H / 2 - 40, zf - D / 2 - 10), (W * 0.40, 110, D * 0.85), mat, root, bevel=26)
    if slot:                                                 # air slot across the face under the plate
        box('slot', (0, y - H / 2 + 50, zf - 2), (W * 0.46, 30, 12), RUBBER, root, bevel=3)
    if bolts:                                                # exposed hex heads across the flat of the face
        for k in range(9):
            bx = -440 + k * 110
            lib.cylinder(f'bolt{k}', (bx, y + H / 2 - 40, min(zf, nose_z(bx) + 12) + 2), (0, 0, 1), 18, 8, STEEL, root, n=6)
    if hooks:
        for s in (-1, 1):
            box(f'hook{s}', (s * 270, y - H / 2 + 20, zf - 10), (16, 120, 64), RED, root, bevel=5)
    if bash:                                                 # bright skid plate hung under the face
        box('bash', (0, y - H / 2 - 34, zf - 100), (min(760, W - 420), 6, 250), ALU, root, bevel=2,
            rot=Matrix.Rotation(math.radians(-28), 3, 'X'))
    if badge:
        text('badge', badge, (0, y - H / 2 + 108, zf + 4), 42, 3, material('LabelWhite', 0xf0f0ec, rough=0.6), root)
    if winch:
        box('fairleadFrame', (0, y + 30, zf + 6), (280, 100, 14), RED, root, bevel=3)
        box('fairleadSlot', (0, y + 30, zf + 14), (220, 56, 4), RUBBER, root, bevel=0)
    number_plate(root, y - (20 if winch else 0) - (60 if winch else 0), zf + 8)
    if skid:
        box('skid', (0, y - H / 2 - 40, zf - 120), (min(700, W - 500), 4, 240), mat, root, bevel=1, rot=Matrix.Rotation(math.radians(-30), 3, 'X'))
    valance(root, corners=corners and W < 1450)
    return root


# ======================================================= DAMD FULL BODY KITS
# Panel sets that restyle the whole front end. All three of these keep the
# stock round headlights, so only the grille panel and the bumpers change.
# Measured off DAMD's own product photography (damd.co.jp).
DAMD_GREEN = material('DamdGreen', 0x123b26, rough=0.5)
CHROME_TRIM = material('ChromeTrim', 0xd8dce0, rough=0.12, metal=1.0)
AMBER = material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0)
IVORY = material('RootsIvory', 0xe8e2d2, rough=0.5, metal=0.1)


def grille_damd_little_d():
    """little D.: a black box frame standing proud of the panel carrying six
    thick horizontal ribs over mesh, a green oval badge low on one side, and
    two small round lamps stacked outboard of each headlight -- the Defender
    signature."""
    root = group('grille_damd_little_d')
    mat, ow, oh = TEXBLACK, 560, 200
    grille_panel('panel', root, mat, (ow, oh, 858))
    lamp_bezels(root, mat, 'square')
    z = face_z(0)
    box('frame', (0, 858, z + 8), (ow + 44, oh + 44, 24), mat, root, bevel=8)
    wire_mesh(root, BLACK, 0, 858, z - 8, ow - 10, oh - 10, pitch=9)
    for k in range(6):
        y = 858 - oh / 2 + 20 + k * (oh - 40) / 5
        box(f'rib{k}', (0, y, z + 22), (ow - 14, 18, 14), mat, root, bevel=3)
    badge = box('badge', (RIGHT * 168, 858 - oh / 2 + 30, z + 24), (104, 50, 5), DAMD_GREEN, root, bevel=24)
    badge.modifiers['bevel'].segments = 6
    for s in (-1, 1):                                        # stacked auxiliary lamps
        for k, (yy, m) in enumerate(((914, AMBER), (842, LENS))):
            lib.cylinder(f'auxHsg{s}{k}', (s * 616, yy, face_z(616) + 6), (0, 0, 1), 74, 40, mat, root, n=22)
            lib.cylinder(f'auxLens{s}{k}', (s * 616, yy, face_z(616) + 26), (0, 0, 1), 62, 5, m, root, n=22)
    return root


def grille_damd_little_g_trad():
    """little G. TRADITIONAL: the whole panel is a matte black louvre field
    of twelve thin horizontal slats, broken in the middle by a round matte
    badge disc. The headlight bays are thick black carriers."""
    root = group('grille_damd_little_g_trad')
    mat, ow, oh = TEXBLACK, 600, 215
    grille_panel('panel', root, mat, (ow, oh, 858))
    lamp_bezels(root, mat, 'square')
    z = face_z(0)
    for k in range(12):
        y = 858 - oh / 2 + 12 + k * (oh - 24) / 11
        box(f'louvre{k}', (0, y, z + 6), (ow - 16, 10, 18), mat, root, bevel=2)
    box('backing', (0, 858, z - 10), (ow, oh, 3), RUBBER, root, bevel=0)
    lib.cylinder('badge', (0, 858, z + 14), (0, 0, 1), 118, 6, mat, root, n=36, bevel=0.5)
    annulus('badgeRing', (0, 858, z + 18), 84, 98, 3, BLACK, root)
    return root


def grille_damd_roots():
    """JIMNY the ROOTS.: a body-colour panel with one wide opening split
    into five cells by four upright ribs, chrome SUZUKI lettering above it,
    and a small round amber marker outboard of each headlight."""
    root = group('grille_damd_roots')
    ow, oh = 600, 170
    grille_panel('panel', root, PAINT, (ow, oh, 848))
    lamp_bezels(root, PAINT, 'round')
    z = face_z(0)
    wire_mesh(root, BLACK, 0, 848, z - 16, ow - 10, oh - 10, pitch=9)
    box('backing', (0, 848, z - 28), (ow, oh, 3), RUBBER, root, bevel=0)
    for k in range(4):
        x = -ow / 2 + (k + 1) * ow / 5
        box(f'rib{k}', (x, 848, z + 2), (22, oh - 6, 20), PAINT, root, bevel=4)
    box('frameTop', (0, 848 + oh / 2 + 8, z + 2), (ow + 16, 22, 20), PAINT, root, bevel=4)
    box('frameBot', (0, 848 - oh / 2 - 8, z + 2), (ow + 16, 22, 20), PAINT, root, bevel=4)
    text('suzuki', 'SUZUKI', (0, 848 + oh / 2 + 44, z + 12), 54, 6, CHROME_TRIM, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    for s in (-1, 1):
        lib.cylinder(f'mk{s}', (s * 612, 906, face_z(612) + 8), (0, 0, 1), 52, 24, PAINT, root, n=20)
        lib.cylinder(f'mkLens{s}', (s * 612, 906, face_z(612) + 22), (0, 0, 1), 42, 4, AMBER, root, n=20)
    return root


def bumper_damd_little_d():
    """little D. front, measured off DAMD's straight-on product shot: 1653
    wide and flush with the wings, a 134 mm flat central face carrying the
    stock round fogs at +-507 and a 734 x 72 mesh slot, square end blocks
    212 wide wrapping back to the wing corners, and a gunmetal skid plate
    with pressed teardrop dimples. Coarse matte black on the top platform and
    the central face, gunmetal on the end blocks and the skid plate."""
    root = group('frontBumper_damd_little_d')
    gun = material('DamdGunmetal', 0x4a4d52, rough=0.5, metal=0.6)
    W, ytop, H = 1570, 720, 134
    y, zf = ytop - H / 2, 1772
    inner = W / 2 - 212                                      # where the end blocks start
    # flat central face
    box('face', (0, y, zf - 60), (inner * 2, H, 120), TEXBLACK, root, bevel=5)
    box('deck', (0, ytop + 16, zf - 70), (inner * 2, 34, 140), TEXBLACK, root, bevel=5)
    # mesh slot across the middle
    box('slotFrame', (0, 644, zf - 2), (734, 72, 14), TEXBLACK, root, bevel=3)
    wire_mesh(root, BLACK, 0, 644, zf - 14, 720, 60, pitch=11)
    for k in (-1, 0, 1):
        box(f'slotRib{k}', (k * 180, 644, zf - 4), (14, 64, 12), TEXBLACK, root, bevel=2)
    for s in (-1, 1):
        fog_lamp(root, s * 507, 658, zf + 2, TEXBLACK, dia=94)
        # square end block, wrapped back onto the wing corner
        ex = s * (inner + 106)
        ez = min(zf, nose_z(abs(ex)) + 30)
        box(f'endBlock{s}', (ex, y, ez - 60), (212, H, 130), gun, root, bevel=6)
        box(f'endDeck{s}', (ex, ytop + 16, ez - 70), (212, 34, 150), TEXBLACK, root, bevel=5)
        box(f'endSide{s}', (s * (W / 2 - 6), y, ez - 110), (14, H, 200), gun, root, bevel=5)
    box('plate', (0, 586, zf + 6), (330, 165, 3), PLATE, root, bevel=1)
    skid = box('skid', (0, 492, zf - 70), (1118, 198, 8), gun, root, bevel=4,
               rot=Matrix.Rotation(math.radians(-24), 3, 'X'))
    for k in range(8):                                       # shallow pressed teardrops
        sx = -490 + k * 140
        lib.cylinder(f'dimple{k}', (sx, 470, zf - 33), (0, 0.42, 1), 38, 4, gun, root, n=18)
    for s in (-1, 1):
        lib.cylinder(f'boss{s}', (s * 210, 540, zf - 11), (0, 0.42, 1), 34, 6, gun, root, n=18)
    valance(root, corners=False)
    return root


def rear_damd_little_d():
    """little D. rear, measured off DAMD's straight-on shot: two layers --
    an upper beam 1656 wide swelling into 486 mm end blocks, and a separate
    lower beam set back and 47 mm below it. The stock lamps go entirely; the
    kit's own domed round lamps take over, three a side plus a flat
    reflector, all wired into the original harness. Coarse matte black."""
    root = group('rearBumper_damd_little_d_rear')
    amber = material('AmberLens', 0xe08a1e, rough=0.15)
    red = material('TailRed', 0xc0161a, rough=0.18)
    W, ytop, HB = 1572, 640, 133
    zc, D = -1640, 140
    zf = zc - D / 2
    ymid = ytop - HB / 2
    box('upper', (0, ymid, zc), (W - 972, HB, D - 30), TEXBLACK, root, bevel=6)
    box('deck', (0, ytop + 16, zc + 10), (W, 34, D), TEXBLACK, root, bevel=5)
    box('lower', (0, 417, zc + 26), (1378, 86, D - 40), TEXBLACK, root, bevel=6)
    for s in (-1, 1):
        ex = s * (W / 2 - 243)
        box(f'endBlock{s}', (ex, ymid, zc - 6), (486, HB, D), TEXBLACK, root, bevel=8)
        box(f'endSide{s}', (s * (W / 2 - 6), ymid, zc + 40), (14, HB, 170), TEXBLACK, root, bevel=5)
        box(f'rubber{s}', (s * (W / 2 - 4), ymid, zf + 14), (20, HB - 20, 10), RUBBER, root, bevel=3)
        # corner gusset that carries the reverse lamp and the flap bracket
        prism(f'gusset{s}', [(507, zf + 6), (507, zf + 120), (398, zf + 120)], s * (W / 2 - 60), s * (W / 2 - 20), TEXBLACK, root)
        # the kit's own lamps: domed lenses, amber over red on a shallow
        # diagonal, clear reverse out on the gusset, flat reflector below
        for (dx, yy, dia, mat_, dome) in ((703, 573, 64, amber, True), (613, 546, 64, red, True),
                                          (757, 471, 64, LENS, True), (453, 430, 57, red, False)):
            lib.cylinder(f'lampCan{s}{dx}', (s * dx, yy, zf + 10), (0, 0, 1), dia + 12, 28, TEXBLACK, root, n=22)
            lib.cylinder(f'lampRim{s}{dx}', (s * dx, yy, zf - 6), (0, 0, 1), dia + 6, 6, CHROME, root, n=22)
            lib.cylinder(f'lampLens{s}{dx}', (s * dx, yy, zf - 10), (0, 0, 1), dia, 12 if dome else 4, mat_, root, n=22)
            if dome:                                         # the lenses are domed, not flat
                d = lib.sphere(f'lampDome{s}{dx}', (s * dx, yy, zf - 6), dia, mat_, root)
                d.scale.y = 0.34
        box(f'mount{s}', (s * 330, ymid + 30, zc + 110), (70, 100, 220), TEXBLACK, root, bevel=4)
    box('plateStep', (0, 520, zc - 30), (420, 190, 60), TEXBLACK, root, bevel=5)
    box('plate', (RIGHT * 60, 520, zf + 34), (330, 165, 3), PLATE, root, bevel=1)
    for s in (-1, 1):
        lib.cylinder(f'plateLamp{s}', (RIGHT * 60 + s * 120, 612, zf + 40), (0, 0, 1), 26, 16, CHROME, root, n=14)
    lib.cylinder('exhaust', (RIGHT * 400, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    return root


def bumper_damd_little_g_trad():
    """little G. TRADITIONAL front: a flat steel beam with a band of close
    vertical ribbing across its face, a chrome-framed amber SQUARE fog lamp
    standing on the top edge at each end, and the plate hung off centre."""
    root = group('frontBumper_damd_little_g_trad')
    y, zf, W, H, D = 585, 1745, 1520, 170, 140
    xs = [-W / 2 + W * i / 12 for i in range(13)]
    sweep('body', [(x, y, min(zf, nose_z(x) + 12) - D / 2) for x in xs], rounded_rect(D, H, 8, 4), TEXBLACK, root)
    for s in (-1, 1):
        box(f'endCap{s}', (s * (W / 2 + 4), y, nose_z(W / 2) + 12 - D / 2), (10, H + 8, D + 8), TEXBLACK, root, bevel=3)
        # Koito square fog on a chrome base, sitting on top of the beam
        box(f'fogBase{s}', (s * 430, y + H / 2 + 16, zf - 44), (36, 34, 36), CHROME_TRIM, root, bevel=3)
        box(f'fogHsg{s}', (s * 430, y + H / 2 + 70, zf - 36), (171, 92, 62), CHROME_TRIM, root, bevel=8)
        box(f'fogLens{s}', (s * 430, y + H / 2 + 70, zf - 4), (141, 75, 5), AMBER, root, bevel=4)
        lib.cylinder(f'fogLogo{s}', (s * 430, y + H / 2 + 70, zf - 1), (0, 0, 1), 34, 3, CHROME_TRIM, root, n=20)
    for k in range(21):                                      # washboard ribbing across the face
        bx = -450 + k * 45
        box(f'ribV{k}', (bx, y + 20, min(zf, nose_z(bx) + 12) + 2), (12, H - 70, 10), TEXBLACK, root, bevel=2)
    wire_mesh(root, BLACK, 0, y - 55, zf - 2, 300, 44, pitch=11)
    box('plate', (RIGHT * 420, y - 6, zf + 10), (330, 165, 3), PLATE, root, bevel=1)
    valance(root, corners=False)
    return root


def rear_damd_little_g_trad():
    """DAMD little G. TRADITIONAL rear bar, from the fitting instructions and
    product shots: 1650 mm across, matte black on every exposed face and
    piano black in the recesses, carrying the kit's own truck-style lamp each
    side (DAMD part E-476). The lens is 215 x 68 and reads, outboard to
    inboard: amber indicator, a plain red reflector, a red stop/tail, then a
    slightly proud clear reverse. Plate centred, its top 130 below the bar."""
    root = group('rearBumper_damd_little_g_trad_rear')
    piano = material('PianoBlack', 0x141416, rough=0.12, metal=0.25)
    W, ytop, H, D, z = 1568, 640, 230, 150, -1650
    y, zf = ytop - H / 2, z - 150 / 2
    sweep('body', [(-W / 2, y, z), (W / 2, y, z)], rounded_rect(D, H, 10, 4), TEXBLACK, root)
    box('ripple', (0, ytop - 26, zf + 4), (W - 120, 44, 10), piano, root, bevel=3)
    for s in (-1, 1):
        box(f'endCap{s}', (s * (W / 2 + 4), y, z), (10, H + 6, D + 6), TEXBLACK, root, bevel=4)
        ly = ytop - 105
        box(f'recess{s}', (s * 540, ly, zf + 4), (345, 107, 12), piano, root, bevel=4)
        box(f'bezel{s}', (s * 540, ly, zf - 3), (280, 100, 10), TEXBLACK, root, bevel=5)
        box(f'lens{s}', (s * 540, ly, zf - 9), (215, 68, 6), TEXBLACK, root, bevel=2)
        segs = ((617.5, 60, material('AmberLens', 0xe08a1e, rough=0.15)),
                (562.8, 49, material('TailRed', 0xc0161a, rough=0.18)),
                (513.2, 49, material('TailRed', 0xc0161a, rough=0.18)),
                (460.5, 56, LENS))
        for k, (dx, w, m) in enumerate(segs):
            lib.cylinder(f'seg{s}{k}', (s * dx, ly, zf - 12 - (2 if k == 3 else 0)), (0, 0, 1),
                         min(w - 4, 58), 4, m, root, n=22)
        for (bx, by) in ((647, 0), (540, 44), (540, -44)):    # the lens screws
            lib.cylinder(f'screw{s}{bx}{by}', (s * bx, ly + by, zf - 13), (0, 0, 1), 9, 4, STEEL, root, n=6)
        box(f'mount{s}', (s * 330, y + 30, z + 110), (70, 100, 220), TEXBLACK, root, bevel=4)
    box('plateStep', (0, ytop - 176, zf + 6), (400, 200, 10), piano, root, bevel=3)
    box('plate', (0, ytop - 212, zf - 3), (330, 165, 3), PLATE, root, bevel=1)
    lib.cylinder('exhaust', (RIGHT * 400, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    return root


def bumper_damd_roots():
    """JIMNY the ROOTS. front: two layers -- an ivory pressed-steel beam
    with a row of small slots along it, over a black lower valance carrying
    the plate in the centre and a small chrome round fog each side."""
    root = group('frontBumper_damd_roots')
    y, zf, W, H, D = 640, 1745, 1560, 120, 110
    xs = [-W / 2 + W * i / 12 for i in range(13)]
    sweep('beam', [(x, y, min(zf, nose_z(x) + 10) - D / 2) for x in xs], rounded_rect(D, H, 8, 3), IVORY, root)
    for s in (-1, 1):
        box(f'endCap{s}', (s * (W / 2 + 4), y, nose_z(W / 2) + 10 - D / 2), (10, H + 8, D + 8), IVORY, root, bevel=3)
    for k in range(17):                                      # pressed slots along the beam
        bx = -560 + k * 70
        box(f'slot{k}', (bx, y, min(zf, nose_z(bx) + 10) + 2), (34, 22, 10), RUBBER, root, bevel=2)
    box('valanceBox', (0, y - 165, zf - 96), (1380, 210, 130), TEXBLACK, root, bevel=10)
    box('plate', (0, y - 165, zf - 28), (330, 165, 3), PLATE, root, bevel=1)
    for s in (-1, 1):
        fog_lamp(root, s * 420, y - 165, min(zf, nose_z(420)) - 30, CHROME_TRIM, dia=86)
    return root


def rear_bar(pid, kind, W=1450, H=200, D=120, y=440, tube_d=60, lamps='wings', steps=False, mat=None):
    """kind: 'tube' or 'plate'; lamps: 'wings' (plate housings keeping the
    stock lamps), 'round' (four small round lamps in the bar), 'housing'
    (recessed boxes), 'none'."""
    root = group(f'rearBumper_{pid}')
    mat = mat or TEXBLACK
    z = -1650
    if lamps == 'klc':
        z = -1640                                            # just proud of the lamps
    if kind == 'tube':
        tube('bar', [(-W / 2, y, z), (W / 2, y, z)], tube_d, mat, root)
        if lamps != 'klc':                                   # the KLC bar is a bare round tube, no end blocks
            for s in (-1, 1):
                box(f'endCap{s}', (s * (W / 2 + 5), y, z), (12, tube_d + 20, tube_d + 20), mat, root, bevel=3)
    else:
        path = [(-W / 2 - 60, y, z + 150), (-W / 2, y, z), (W / 2, y, z), (W / 2 + 60, y, z + 150)]
        sweep('body', [tuple(p) for p in fillet(path, 40, steps=3)], rounded_rect(D, H, 10, 3), mat, root)
    for s in (-1, 1):
        box(f'mount{s}', (s * 330, y + 30, z + 110), (70, 100, 220), mat, root, bevel=4)
        if lamps == 'wings':
            box(f'wing{s}', (s * 513, 545, -1568), (400, 250, 8), mat, root, bevel=3)
            for (cx, cy, sx, sy) in ((0, 76, 370, 12), (0, -76, 370, 12), (-180, 0, 12, 160), (180, 0, 12, 160)):
                box(f'lampFrame{s}{cx}{cy}', (s * 513 + cx, 518 + cy, -1596), (sx, sy, 20), mat, root, bevel=2)
        elif lamps == 'klc':
            # tube runs along the body's lower edge; the stock lamps sit in
            # housings hung from the tube, faces set back from the tube
            # steel boxes on the tube's ends, tops level with the tube, holding the stock lamps;
            # a red tow hook drops from each box's inner bottom corner
            # the car's own tail lamps stay; the bar only carries a hook each side
            box(f'hook{s}', (s * 330, y - 150, -1560), (14, 110, 50), RED, root, bevel=4, rot=Matrix.Rotation(s * 0.25, 3, 'Z'))
        elif lamps == 'housing':
            box(f'lampBox{s}', (s * 513, 518, -1560), (380, 170, 90), mat, root, bevel=4)
        elif lamps == 'round':
            for k, xx in enumerate((s * 470, s * 580)):
                lib.cylinder(f'lampHsg{s}{k}', (xx, y, z - 8), (0, 0, 1), 78, 40, BLACK, root, n=24)
                lib.cylinder(f'lampLens{s}{k}', (xx, y, z - 30), (0, 0, 1), 66, 4, material('TailRed', 0xc0161a, rough=0.2), root, n=24)
        if steps:
            box(f'step{s}', (s * (W / 2 - 120), y + H / 2 + 4, z + 20), (240, 6, 160), ALU_CHEQ, root, bevel=1)
    if lamps == 'klc':                                       # plate on two tabs right under the tube
        for s in (-1, 1):
            box(f'plateTab{s}', (s * 110, y - tube_d / 2 - 10, z - 6), (24, 40, 6), mat, root, bevel=1)
        box('plate', (0, y - tube_d / 2 - 100, z - tube_d / 2 + 2), (330, 165, 3), PLATE, root, bevel=1)
    else:
        box('plate', (0, 585, TAIL_Z - 6), (330, 165, 4), PLATE, root, bevel=1)
    if lamps != 'klc':                                       # the KLC tube stays open underneath, as fitted
        box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)
        for s in (-1, 1):
            box(f'corner{s}', (s * 740, 520, -1470), (50, 240, 180), mat, root, bevel=6, rot=Matrix.Rotation(math.radians(-s * 25), 3, 'Z'))
    else:
        lib.cylinder('exhaust', (RIGHT * 400, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    return root


def grille_generic(pid, h_slats=0, v_slots=0, hex_cells=False, wire=True, label=None, text_mat=None, bezel='round',
                   marker=0, mat=None, ow=580, oh=215, slat_h=30, ribs=False, letters_over=True):
    """Stock-outline panel with a centre opening filled per product."""
    root = group(f'grille_{pid}')
    mat = mat or TEXBLACK
    grille_panel('panel', root, mat, (ow, oh, 858))
    lamp_bezels(root, mat, bezel)
    z = face_z(0)
    if h_slats:
        pitch = oh / (h_slats + 0.2)
        for k in range(h_slats):
            y = 858 - oh / 2 + pitch * 0.6 + k * pitch
            box(f'slat{k}', (0, y, z + 1), (ow - 10, min(slat_h, pitch * 0.62), 22), mat, root, bevel=4)
    if v_slots:
        pitch = ow / (v_slots + 0.5)
        for k in range(v_slots + 1):
            x = -ow / 2 + pitch * 0.25 + k * pitch
            box(f'post{k}', (x, 858, z + 1), (min(24, pitch * 0.35), oh - 8, 22), mat, root, bevel=4)
    if hex_cells:
        hex_mesh(root, BLACK, 0, 858, z - 16, ow - 20, oh - 20)
    elif wire:
        wire_mesh(root, STEEL if text_mat is None else BLACK, 0, 858, z - 20, ow - 10, oh - 10, pitch=9)
    box('backing', (0, 858, z - 32), (ow, oh, 3), RUBBER, root, bevel=0)
    if ribs:
        for s in (-1, 1):
            for k in range(3):
                box(f'rib{s}{k}', (s * 460, 866 + (k - 1) * 45, z + 8), (230, 8, 8), mat, root, bevel=2)
    for k in range(marker):
        xx = (-1 if k % 2 == 0 else 1) * (ow / 2 - 60 - (k // 2) * 90)
        lib.cylinder(f'marker{k}', (xx, 858 + oh / 2 + 24, z + 6), (0, 0, 1), 46, 20, BLACK, root, n=20)
        lib.cylinder(f'markerLens{k}', (xx, 858 + oh / 2 + 24, z + 17), (0, 0, 1), 38, 3, material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0), root, n=20)
    if label:
        text('suzuki', label, (0, 862, z + 16), 56, 5, text_mat or material('LabelWhite', 0xf0f0ec, rough=0.6), root,
             font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    return root


# ============================================================ KLC NOSTALGIC
def bumper_klc_nostalgic():
    """KLC Heritage Nostalgic front: smooth pressed-steel box bar wrapped
    round the corners, painted, over a black lower valance with two round
    fogs, horizontal slots and the number plate."""
    root = group('frontBumper_klc_nostalgic')
    y, zf = 640, 1745
    W, H, D = 1470, 150, 120
    path = [(-W / 2, y, zf - D / 2 - 160), (-W / 2 + 140, y, zf - D / 2), (W / 2 - 140, y, zf - D / 2), (W / 2, y, zf - D / 2 - 160)]
    sweep('bar', [tuple(p) for p in fillet(path, 60, steps=4)], rounded_rect(D, H, 34, 5), PAINT, root)
    box('valance', (0, 470, zf - 90), (1020, 170, 110), TEXBLACK, root, bevel=14)
    for k in range(3):
        box(f'slot{k}', (0, 440 + k * 30, zf - 33), (330, 12, 6), RUBBER, root, bevel=0)
    for s in (-1, 1):
        fog_lamp(root, s * 400, 470, zf - 34, TEXBLACK, dia=90)
    box('plate', (0, 480, zf - 28), (330, 165, 3), PLATE, root, bevel=1)
    box('bay', (0, 560, 1400), (1050, 300, 20), RUBBER, root, bevel=4)
    return root


def rear_bumper_klc_nostalgic():
    """KLC Heritage Nostalgic rear: painted box bar with wrapped ends, a black
    rubber strip along the top, rectangular three-colour lamps set into the
    ends, the number plate hung under the middle. Stock lamps are hidden by
    the bumper it replaces, so this one carries its own."""
    root = group('rearBumper_klc_nostalgic_rear')
    y, z = 470, -1650
    W, H, D = 1520, 180, 130
    path = [(-W / 2, y, z + 200), (-W / 2 + 150, y, z), (W / 2 - 150, y, z), (W / 2, y, z + 200)]
    sweep('bar', [tuple(p) for p in fillet(path, 60, steps=4)], rounded_rect(D, H, 30, 5), PAINT, root)
    box('rubber', (0, y + H / 2 - 4, z - 4), (W - 320, 10, D - 20), RUBBER, root, bevel=3)
    red = material('TailRed', 0xc0161a, rough=0.2)
    amber = material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0)
    for s in (-1, 1):
        cx = s * 520
        box(f'lampHsg{s}', (cx, y + 5, z - D / 2 - 2), (270, 110, 8), BLACK, root, bevel=2)
        for (dx, w, m) in ((-95 * s, 70, amber), (0 * s, 100, red), (95 * s, 70, LENS)):
            box(f'lamp{s}{dx}', (cx + dx, y + 5, z - D / 2 - 8), (w - 6, 96, 6), m, root, bevel=1)
        box(f'mount{s}', (s * 330, y + 30, z + 110), (70, 100, 220), TEXBLACK, root, bevel=4)
        box(f'corner{s}', (s * 740, 520, -1470), (50, 240, 180), TEXBLACK, root, bevel=6, rot=Matrix.Rotation(math.radians(-s * 25), 3, 'Z'))
    box('plate', (0, y - 20, z - D / 2 - 8), (330, 165, 3), PLATE, root, bevel=1)
    box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)
    return root


def side_skirt():
    """SHOWA GARAGE AES sill cover: matte panel under the doors between the
    arches, a soft crease along its top, wrapping under the sill."""
    root = group('sideSkirt')
    zf, zr = FRONT_ARCH_Z - 60, REAR_ARCH_Z + 60
    L = zf - zr
    for s in (-1, 1):
        panel = box(f'panel{s}', (s * (BODY_X + 8), SILL_Y + 30, (zf + zr) / 2), (26, 150, L), TEXBLACK, root, bevel=10)
        panel.modifiers['bevel'].segments = 3
        box(f'crease{s}', (s * (BODY_X + 22), SILL_Y + 95, (zf + zr) / 2), (4, 6, L - 40), BLACK, root, bevel=1)
        box(f'under{s}', (s * (BODY_X - 30), SILL_Y - 40, (zf + zr) / 2), (90, 12, L), TEXBLACK, root, bevel=3)
    return root


def ladder_jst():
    """JST tailgate ladder, standard width: a closed oval hoop of 25 mm tube,
    270 mm inside, four rungs, two tabs bolting it to the hinge side of the
    tailgate about 60 mm off the skin."""
    root = group('ladder_jst')
    s = RIGHT
    zf = TAIL_Z - 62
    xi, xo = s * 330, s * 625
    y0, y1 = 640, 1560
    r = abs(xo - xi) / 2
    loop = [(xi, y0 + 60, zf), (xi, y1, zf), (xo, y1, zf), (xo, y0, zf), (xi, y0, zf), (xi, y0 + 120, zf)]
    tube('hoop', loop, 32, BLACK, root, bend=70)
    for k in range(4):
        y = y0 + 170 + k * 215
        tube(f'rung{k}', [(xi, y, zf), (xo, y, zf)], 26, BLACK, root)
    for y in (y0 + 260, y1 - 260):
        box(f'tab{y}', (xi + s * 20, y, (TAIL_Z + zf) / 2), (60, 70, abs(TAIL_Z - zf)), BLACK, root, bevel=4)
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
    grille_owner()
    bumper_showa()
    bumper_klc()
    bumper_outclass()
    for st in ('stock', 'steel', 'six', 'eight', 'ten', 'beadlock', 'moon', 'daytona', 'slot5', 'watanabe', 'eightpin'):
        rim(st)
    roof_rack_arb()
    roof_lights()
    bumper_tube_heritage()
    rear_bumper_tube()
    ladder_tube()
    ladder_jst()
    guard_can()
    guard_board()
    shovel()
    flares()
    decals()
    side_skirt()
    snorkel_bravo()
    snorkel_urnieta()
    snorkel_precleaner()
    snorkel_sleek()
    mirrors_urnieta()
    mirrors_damd()
    pillar_pods()
    pillar_pods(sides=(-RIGHT,), suffix='_left')
    # catalogue variants (dimensions from parts.js research; see notes there)
    # roof racks (research 2026-09-16: ARB/Yakima TW, Front Runner, Rhino, JAOS, IPF, APIO, SHOWA, TW generic)
    rack_platform('yakima', 1370, 1520, slat_dir='across', slats=7, legs=4, deflector=False)
    rack_platform('fr34', 1345, 1156, slat_dir='across', slats=6, legs=4, deflector=True)
    rack_platform('pioneer', 1339, 1453, slat_dir='along', slats=5, legs=4, deflector=False)
    rack_platform('jaos', 1250, 1400, slat_dir='across', slats=6, rail=(32, 32), legs=6, deflector=True)
    rack_platform('ipf', 1250, 1400, slat_dir='across', slats=7, rail=(40, 39), legs=4, deflector=False)
    rack_platform('apio', 1270, 1420, slat_dir='across', slats=8, rail=(28, 60), legs=6, deflector=True)
    rack_platform('showa_foot', 1250, 1500, slat_dir='across', slats=9, rail=(40, 40), legs=6, deflector=False)
    rack_platform('tw_generic', 1260, 1600, slat_dir='across', slats=9, legs=6, deflector=True)
    # awnings (closed bag L x W x H; hard = aluminium case; hinge = 270/180 pivot at the rear end)
    for side in ('left', 'right'):
        awning_case('arb_touring_2', side, 2200, 130, 130, PVC)
        awning_case('arb_touring_25', side, 2700, 130, 130, PVC)
        awning_case('arb_alu', side, 2650, 150, 110, BLACK, hard=True)
        awning_case('yakima_s', side, 2100, 150, 150, PVC)
        awning_case('yakima_l', side, 2600, 150, 150, PVC)
        awning_case('yakima_270', side, 2286, 216, 254, PVC, hinge=True)
        awning_case('yakima_270s', side, 1850, 200, 200, PVC, hinge=True)
        awning_case('yakima_180', side, 2260, 229, 178, PVC, hinge=True)
        awning_case('rhino_compact', side, 2000, 180, 160, PVC, hinge=True)
        awning_case('rhino_270', side, 2500, 180, 160, PVC, hinge=True)
        awning_case('darche_270', side, 2550, 170, 170, PVC, hinge=True)
        awning_case('darche_slim', side, 2550, 130, 130, PVC)
        awning_case('ikamper', side, 2630, 180, 184, BLACK, hard=True, hinge=True)
        awning_case('allblack_270', side, 2100, 180, 180, PVC, hinge=True)
    # side steps (research 2026-09-16: TW mrk.com.tw, JP makers)
    side_step('wlm', 'tube', tube_d=50, pads=[(130, 900, 0)], drop=30)
    side_step('jst', 'tube', tube_d=50, standoff=55, drop=20, upturn=110)
    side_step('tjm', 'slider', tube_d=51, pads=[(110, 200, -350), (110, 200, 0), (110, 200, 350)])
    side_step('outclass', 'tube', tube_d=45, pads=[(150, 900, 0)], drop=30)
    side_step('apio_guard', 'armour', standoff=45)
    side_step('jaos', 'tube', tube_d=76, pads=[(110, 300, 60)])
    side_step('taniguchi_bar', 'tube', tube_d=42, pads=[(145, 550, 80)])
    side_step('taniguchi_short', 'short', tube_d=32, pads=[(145, 550, 0)])
    side_step('showa', 'tube', tube_d=48)
    side_step('wildgoose_fold', 'short', tube_d=20, pads=[(160, 510, 0)])
    side_step('wildgoose_guard', 'armour', standoff=55)
    side_step('customwagon', 'tube', tube_d=48, pads=[(140, 420, 60)])
    side_step('spieler', 'plate', plate_w=150)
    side_step('ironman', 'slider', tube_d=51)
    side_step('hamer', 'slider', tube_d=60, pads=[(120, 260, -300), (120, 260, 300)])
    # front bumpers (TW/JP research 2026-09-16)
    front_bar('armando', 'plate', W=1500, H=300, D=170, y=530, hoop=True, fogs=True, hooks=True, skid=False)
    front_bar('urnieta_1970', 'short', W=1300, H=160, D=120, y=560)
    front_bar('beyond_liberte', 'plate', W=1400, H=230, D=150, fog_stalk=True, bash=True, skid=False)
    front_bar('maverick', 'short', W=1300, H=200, D=140, y=540, fogs=True, skid=False)
    front_bar('mrk_abs', 'abs', W=1520, H=250, D=170, y=540, skid=False, corners=False, hump=True, bash=True, mesh_off=RIGHT * 330, fogs=True)
    front_bar('wmd_winch', 'short', W=1100, H=230, D=170, y=560, hoop=True, winch=True)
    front_bar('jaos_cowl', 'abs', W=1470, H=280, D=180, y=540, skid=False, corners=False, hump=True, bash=True, badge='JAOS', mesh_off=0)
    front_bar('taniguchi_square', 'box', W=1400, y=600, skid=False)
    front_bar('taniguchi_double', 'double', W=1400, y=590, tube_d=48, skid=False)
    bumper_klc_nostalgic()
    rear_bumper_klc_nostalgic()
    front_bar('klc_short', 'abs', W=1500, H=230, D=170, y=540, fogs=True, skid=False, corners=False, slot=True, badge='KLC')
    front_bar('toc_extreme', 'plate', W=1470, H=260, D=180, y=530, fogs=True, corners=False, bolts=True, skid=False)
    # DAMD full body kits (damd.co.jp, 2026-09): panel sets that keep the
    # stock round headlights, so only the grille and the bumpers change
    grille_damd_little_d()
    grille_damd_little_g_trad()
    grille_damd_roots()
    bumper_damd_little_d()
    bumper_damd_little_g_trad()
    bumper_damd_roots()
    rear_damd_little_d()
    rear_damd_little_g_trad()
    rear_bar('damd_roots_rear', 'plate', W=1360, H=150, D=120, y=520, lamps='round', mat=IVORY)
    # rear bumpers
    rear_bar('klc_heritage_rear', 'tube', W=1380, tube_d=76, y=648, lamps='klc')
    rear_bar('urnieta_1970_rear', 'plate', W=1370, H=140, D=110, y=470, lamps='round')
    rear_bar('beyond_rear', 'plate', W=1360, H=160, D=120, y=460, lamps='wings')
    rear_bar('jaos_rear_cowl', 'plate', W=1330, H=230, D=150, y=500, lamps='round')
    rear_bar('wildgoose_crawler_rear', 'tube', W=1330, tube_d=76, lamps='housing')
    rear_bar('wildgoose_box_rear', 'plate', W=1410, H=100, D=100, y=450, lamps='housing')
    rear_bar('showa_iron_rear', 'tube', W=1450, tube_d=60, lamps='wings')
    rear_bar('taniguchi_rear_pipe', 'tube', W=1420, tube_d=60, lamps='none')
    rear_bar('apio_tactical_rear', 'plate', W=1290, H=280, D=200, y=520, lamps='housing')
    rear_bar('outclass_rear_abs', 'plate', W=1310, H=220, D=170, y=500, lamps='round')
    rear_bar('hamer_mx208', 'plate', W=1270, H=300, D=220, y=520, lamps='housing', steps=True)
    # grilles
    grille_generic('taishan_retro', v_slots=11)
    grille_generic('klc_ja', wire=True, marker=4, bezel='round', h_slats=1, slat_h=18)
    grille_generic('klc_nanaketsu', v_slots=7, bezel='square')
    grille_generic('klc_forty', wire=True, label='SUZUKI', bezel='round')
    grille_generic('urnieta_1970', wire=True, ow=600, oh=220, bezel='square')
    grille_generic('mrk_angry', v_slots=7, bezel='square', wire=False)
    grille_generic('apio_sj', v_slots=9, mat=GUNMETAL)
    grille_generic('apio_marker', h_slats=4, marker=4)
    grille_generic('taniguchi_washer', wire=True)
    grille_generic('kpro_folksy', h_slats=6, mat=material('WhiteGel', 0xeeeee8, rough=0.35), wire=False)
    grille_generic('prostaff_minig', v_slots=9, bezel='square')
    grille_generic('sixsense_explosion', h_slats=7, slat_h=12, label='SUZUKI', bezel='square', mat=PAINT)
    lib.export(os.path.abspath(OUT))


build()
print('exported', os.path.abspath(OUT))
