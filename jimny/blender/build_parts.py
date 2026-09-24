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
from mathutils import Matrix  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
from mathutils import Vector  # noqa: E402

CAR = json.load(open(os.path.join(HERE, 'car.json')))
OUT = os.path.join(HERE, '..', 'model', 'parts.glb')
RIMS_OUT = os.path.join(HERE, '..', 'model', 'rims.glb')

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
# A smooth dielectric goes almost white at a grazing angle, which is exactly
# how a window panel is usually seen, so this is deliberately rough and half
# transparent -- it has to read as tinted glass, not as a mirror or a lid.
GLASS = material('PrivacyGlass', 0x0a0d0f, rough=0.55, metal=0.0)


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


def flatten(obj, centre, k):
    """Squash a sphere along the car's Z (its depth) into a dome.

    lib.sphere bakes the position into the mesh, so setting obj.scale scales
    the offset too and the dome slides toward the origin -- an extinguisher
    cap ended up a metre forward of the bottle it belonged to. Scaling about
    the object origin and then putting the centre back is the fix."""
    obj.scale.y = k
    obj.location.y = P(*centre)[1] * (1 - k)
    return obj


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


def hex_edges(w, h, cell=25):
    """Flat-topped honeycomb over a w x h rectangle centred on (0, 0), each
    edge listed once. Returns [((u0, v0), (u1, v1)), ...] in mm."""
    r = cell / 2 / math.cos(math.pi / 6)              # circumradius for a cell `cell` across flats
    du, dv = 1.5 * r, cell
    edges = set()
    col = 0
    u = -w / 2 + r
    while u < w / 2 - r * 0.5:
        v = -h / 2 + (dv / 2 if col % 2 else 0) + cell / 2
        while v < h / 2 - cell * 0.45:
            for k in range(6):
                a0, a1 = math.pi / 3 * k, math.pi / 3 * (k + 1)
                p0 = (round(u + r * math.cos(a0)), round(v + r * math.sin(a0)))
                p1 = (round(u + r * math.cos(a1)), round(v + r * math.sin(a1)))
                edges.add(tuple(sorted((p0, p1))))
            v += dv
        u += du
        col += 1
    return sorted(edges)


def hex_mesh(root, mat, cx, cy, z, w, h, cell=25, bar=2.4):
    """Honeycomb in the X-Y plane at a fixed Z -- a grille face."""
    sq = [(-bar / 2, -bar / 2), (bar / 2, -bar / 2), (bar / 2, bar / 2), (-bar / 2, bar / 2)]
    for i, ((u0, v0), (u1, v1)) in enumerate(hex_edges(w, h, cell)):
        sweep(f'hx{i}', [(cx + u0, cy + v0, z), (cx + u1, cy + v1, z)], sq, mat, root, smooth=False)


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
    dish = W / 2 - (24 if style in ('steel', 'daytona', 'moon', 'slot5', 'renkon', 'arc4') else 38)   # face plane, inset from the outer lip
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
    elif style == 'renkon':
        # APIO WILDBOAR D: one ring of 16 countersunk round holes
        for k in range(16):
            a = 2 * math.pi * k / 16
            cutters.append(lib.cylinder(f'hole{k}', (dish, 0.66 * R * math.sin(a), 0.66 * R * math.cos(a)),
                                        (1, 0, 0), 52, 60, RIM_FACE, None, n=20))
    elif style == 'arc4':
        # APIO WILDBOAR SR: four long slim arc slots on the clock diagonals
        for k in range(4):
            a0 = math.pi / 4 + 2 * math.pi * k / 4
            for t in range(5):
                a = a0 - 0.30 + 0.60 * t / 4
                cutters.append(lib.cylinder(f'arc{k}{t}', (dish, 0.62 * R * math.sin(a), 0.62 * R * math.cos(a)),
                                            (1, 0, 0), 46, 60, RIM_FACE, None, n=16))
    elif style == 'dwindow':
        # MLJ XTREME-J XJ07: eight trapezoid D-windows in a deep concave
        for k in range(8):
            a = 2 * math.pi * k / 8
            c = box(f'win{k}', (dish, 0.60 * R * math.sin(a), 0.60 * R * math.cos(a)), (60, 74, 128), RIM_FACE, None,
                    bevel=22, rot=Matrix.Rotation(-a, 3, 'X'))
            c.modifiers['bevel'].segments = 4
            cutters.append(c)
    elif style == 'turbine':
        # DEAN California: 24 narrow radial stadium slots, half solid half void
        for k in range(24):
            a = 2 * math.pi * k / 24
            cutters.append(box(f'slot{k}', (dish, 0.60 * R * math.sin(a), 0.60 * R * math.cos(a)), (60, 22, 150), RIM_FACE, None,
                               bevel=10, rot=Matrix.Rotation(-a, 3, 'X')))
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
    elif style in ('slot5', 'turbine'):                        # bolt-on chrome centre plate over the nuts
        lib.cylinder('plate', (dish + 9, 0, 0), (1, 0, 0), 168, 7, NUT, root, n=44, bevel=3)
        if style == 'turbine':
            lib.cylinder('plateRope', (dish + 13, 0, 0), (1, 0, 0), 120, 6, NUT, root, n=40, bevel=2)
            lib.cylinder('plateDome', (dish + 18, 0, 0), (1, 0, 0), 82, 10, NUT, root, n=32, bevel=4)
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


def guard_can(side=RIGHT):
    """Flat 7.5 L can on a quarter-window guard (owner's photos): can forward
    with its cap on the forward top corner, a round centre boss with a latch
    bar, an octagonal raised rim, two black straps. Built per side -- the can,
    the axe and the recovery board used to be welded to one side each, which
    is not how anybody actually loads a car."""
    sfx = 'right' if side == RIGHT else 'left'
    root = group(f'guardCan_{sfx}')
    s = side
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
    return root


def guard_axe(side=RIGHT):
    """Full axe strapped to the rear end of a quarter-window guard, handle
    straight down and head up -- which is how it is carried, and how the
    owner's car wears it. The head clears the guard's top rail by about
    130 mm; the two band clamps bite onto the guard itself so the axe cannot
    read as floating alongside the car."""
    sfx = 'right' if side == RIGHT else 'left'
    root = group(f'guardAxe_{sfx}')
    s = side
    q = QUARTER
    cz = (q['z0'] + q['z1']) / 2
    face = s * 716
    ax = cz - 230                                            # rear end of the guard
    y0, y1 = q['y0'] + 10, q['y1'] + 130                     # handle butt, top of the head
    hy = y0 + (y1 - 120 - y0) / 2                            # handle butt at y0, top inside the eye
    lib.cylinder('handle', (face + s * 30, hy, ax), (0, 1, 0), 26, y1 - 120 - y0, WOOD, root, n=14)
    box('eye', (face + s * 30, y1 - 84, ax), (34, 84, 46), STEEL, root, bevel=5)
    prism('bit', [(y1 - 126, ax + 22), (y1 - 40, ax + 22), (y1 - 6, ax + 124), (y1 - 150, ax + 124)],
          face + s * 18, face + s * 42, STEEL, root)
    box('poll', (face + s * 30, y1 - 84, ax - 46), (30, 46, 42), STEEL, root, bevel=4)
    leather = material('Leather', 0xb98a55, rough=0.75)
    prism('sheath', [(y1 - 150, ax + 30), (y1 - 24, ax + 30), (y1 + 4, ax + 140), (y1 - 178, ax + 140)],
          face + s * 12, face + s * 48, leather, root)
    for yy in (y1 - 120, y1 - 60):
        lib.cylinder(f'stud{yy}', (face + s * 50, yy, ax + 104), (1, 0, 0), 14, 4,
                     material('Brass', 0xb08d3c, rough=0.4, metal=1.0), root, n=10)
    for y in (q['y0'] + 90, q['y1'] - 90):                   # band clamps onto the guard frame
        box(f'axeClamp{y}', (face + s * 16, y, ax), (48, 22, 62), BLACK, root, bevel=3)
        box(f'shackle{y}', (face + s * 30, y, ax - 52), (24, 18, 30), BLACK, root, bevel=4)
    return root


def guard_board(side=-RIGHT):
    """Perforated recovery board on a quarter-window guard: about half the
    guard's height, centred, a grid of square holes, strapped at both ends."""
    sfx = 'right' if side == RIGHT else 'left'
    root = group(f'guardBoard_{sfx}')
    s = side
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


# Body half-width along each wheel arch at r = 470 from the axle centre,
# measured off the model every 7.5 degrees. The arch is not a cylinder: it
# falls from 795 at the top to about 730 at the ends, so anything placed at
# one fixed x floats off the body near the ends.
ARCH_HALF_W = {
    'front': (728, 751, 764, 774, 780, 788, 792, 794, 794, 795, 795,
              795, 795, 795, 795, 794, 790, 785, 779, 772, 765),
    'rear': (759, 765, 770, 778, 784, 788, 791, 792, 792, 791, 787,
             788, 791, 791, 790, 788, 781, 778, 774, 767, 756),
}


def arch_half_w(kind, deg):
    """Interpolate the measured arch profile; deg runs 15..165 up the arch."""
    t = (deg - 15) / 7.5
    tbl = ARCH_HALF_W[kind]
    i = max(0, min(len(tbl) - 2, int(t)))
    return tbl[i] + (tbl[i + 1] - tbl[i]) * (t - i)


def flares():
    """Riveted look on the STOCK arches (owner's choice): a row of hex bolt
    heads following the arch. Each one sits on the measured body surface for
    its angle, not at a fixed x."""
    root = group('flares')
    for s in (-1, 1):
        for kind, z in (('front', CAR['anchors']['frontAxleZ']), ('rear', CAR['anchors']['rearAxleZ'])):
            for t in range(11):
                deg = 20 + 130 * t / 10
                a = math.radians(deg)
                r = 470
                lib.cylinder(f'rivet{s}{kind}{t}', (s * (arch_half_w(kind, deg) - 3), 346 + r * math.sin(a), z + r * math.cos(a)),
                             (1, 0, 0), 15, 8, STEEL, root, n=6)
    return root


# ============================================================ SNORKEL VARIANTS
# All on the vehicle's RIGHT (the 1.5L airbox side). The "no-drill" kits
# (Bravo, Urnieta, Supa-Sleek) replace the black fender-corner garnish at the
# A-pillar base instead of cutting the wing, so their bodies start there.
PILLAR = [(660 + 40, 1160, 630), (640 + 40, 1400, 500), (612 + 40, 1580, 410)]   # x, y, z along the pillar (right side = -x)


# Every snorkel here was drawn too tall AND with too big a head. The model's
# roof crowns at y 1620 and NONE of these clears it on the real car (a bare
# roof, no rack) -- which is also the one thing that fails a Taiwanese
# inspection, because the height on the 行照 has to match. Measured off
# URNIETA's own side photo with the duct's fore-aft width as the ruler: the
# head is about 0.7 duct-widths tall and 1.8 long, and its crown sits roughly
# 60 mm BELOW the roof. Every head here is sized and placed to that.
ROOF_Y = 1620
TUBE_TOP = 1470


def _pillar_path(side, off, top_y=1470):
    return [(side * 700, 990, 640), (side * (700 + off - 40), 1080, 640),
            (side * (660 + off), 1160, 630), (side * (640 + off), 1400, 500), (side * (612 + off), top_y, 405)]


def snorkel_bravo(side=RIGHT):
    """Bravo Snorkel SSJN (Girona, Spain).

    Corrected 2026-09-22 from Bravo's own manual: the body is NOT square and
    the head does NOT face sideways. The top is round, Bravo publish it as
    89 mm, and the intake is a forward-facing elbow clamped on a band so the
    owner can rotate it. The fender IS drilled and cut -- the "no
    modification" line is a reseller's, not Bravo's."""
    root = group('snorkel_bravo')
    off = 44
    pts = fillet(_pillar_path(side, off, TUBE_TOP), 90, steps=8)
    sweep('body', [tuple(p) for p in pts], rounded_rect(92, 74, 30, 5), TEXBLACK, root)
    box('basePlate', (side * 712, 1000, 620), (60, 40, 170), TEXBLACK, root, bevel=6)
    hx, hz = side * (612 + off), 405
    lib.cylinder('collar', (hx, 1458, hz), (0, 1, 0), 98, 26, TEXBLACK, root, n=24)
    lib.cylinder('band', (hx, 1478, hz), (0, 1, 0), 96, 18, BLACK, root, n=24)
    box('bandLug', (hx + side * 50, 1478, hz), (22, 24, 30), BLACK, root, bevel=3)
    # forward-facing elbow: up out of the band, over, and out toward the nose
    tube('elbow', [(hx, 1474, hz), (hx, 1510, hz), (hx, 1521, hz + 54), (hx, 1521, hz + 98)],
         84, TEXBLACK, root, bend=38)
    box('mouth', (hx, 1521, hz + 112), (88, 88, 14), TEXBLACK, root, bevel=8)
    for k in range(6):                                      # grille bars across the mouth
        box(f'grille{k}', (hx, 1488 + k * 13, hz + 118), (72, 6, 5), RUBBER, root, bevel=0)
    for (y, z, x) in ((1260, 575, 655), (1380, 512, 646)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_urnieta(side=RIGHT, head='drum'):
    """URNIETA SALADO snorkel kit (0702021), drawing UN-JIMNY-FB-006: 1048
    long x 675 tall, 2.3 kg, JB74 only.

    The kit ships TWO heads on one collar -- URNIETA call them Standard and
    Pre-Cleaner -- so the kit is drawn twice, once per head:

      'drum'  a round drum with louvres right round it
      'ram'   a square box cantilevered forward off the collar, its barred
              mouth facing the nose, UNT badge on the outboard face. This is
              what the Taiwanese sellers' photos show; URNIETA's own page
              names the two heads without describing either shape.
    """
    root = group('snorkel_urnieta' + ('_ram' if head == 'ram' else ''))
    off = 42
    pts = fillet(_pillar_path(side, off, 1452), 80, steps=8)
    # the duct is a flattened moulding hugging the pillar, 104 fore-aft -- that
    # width is the ruler everything above it is measured against
    sweep('body', [tuple(p) for p in pts], rounded_rect(88, 104, 26, 4), TEXBLACK, root)
    box('basePlate', (side * 712, 1000, 620), (60, 40, 170), TEXBLACK, root, bevel=6)
    hx, hz = side * (612 + off), 405
    lib.cylinder('collar', (hx, 1466, hz), (0, 1, 0), 96, 34, TEXBLACK, root, n=24)
    if head == 'ram':
        # a short stepped neck off the collar, then a slim box reaching forward
        # over the windscreen pillar; the mouth is barred rather than meshed
        box('neck', (hx, 1496, hz + 4), (104, 38, 100), TEXBLACK, root, bevel=8)
        box('head', (hx, 1524, hz + 70), (128, 76, 196), TEXBLACK, root, bevel=18)
        box('mouth', (hx, 1524, hz + 168), (112, 62, 12), BLACK, root, bevel=6)
        for k in range(3):                                  # bars across the mouth
            box(f'bar{k}', (hx, 1506 + k * 18, hz + 174), (98, 9, 6), TEXBLACK, root, bevel=2)
        box('badge', (side * (612 + off + 66), 1524, hz + 70),
            (5, 26, 74), material('LabelWhite', 0xf0f0ec, rough=0.6), root, bevel=2)
        lib.cylinder('bandScrew', (hx, 1468, hz + 48), (0, 0, 1), 14, 24, STEEL, root, n=10)
    else:
        lib.cylinder('drum', (hx, 1500, hz), (0, 1, 0), 136, 72, TEXBLACK, root, n=28)
        for k in range(5):                                  # louvres all the way round
            lib.cylinder(f'louvre{k}', (hx, 1472 + k * 14, hz), (0, 1, 0), 144, 7, RUBBER, root, n=28)
        lib.cylinder('lid', (hx, 1542, hz), (0, 1, 0), 142, 10, TEXBLACK, root, n=28)
        lib.cylinder('knob', (hx, 1552, hz), (0, 1, 0), 34, 10, TEXBLACK, root, n=16)
    for (y, z, x) in ((1260, 575, 655), (1370, 520, 648)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_ironman(side=RIGHT):
    """Ironman 4x4 ISNORKEL070 -- what our 'safari' slot was always drawing.
    Safari has never made a JB74 part. Forward-facing ram head with a hex
    mesh face, on a band clamp so it rotates."""
    root = group('snorkel_ironman')
    off = 42
    pts = fillet(_pillar_path(side, off, 1470), 95, steps=8)
    sweep('body', [tuple(p) for p in pts], rounded_rect(98, 96, 34, 5), TEXBLACK, root)
    box('basePlate', (side * 712, 1000, 620), (62, 40, 176), TEXBLACK, root, bevel=6)
    hx, hz = side * (612 + off), 405
    lib.cylinder('band', (hx, 1480, hz), (0, 1, 0), 102, 20, BLACK, root, n=24)
    tube('ram', [(hx, 1476, hz), (hx, 1516, hz), (hx, 1532, hz + 58), (hx, 1532, hz + 106)],
         90, TEXBLACK, root, bend=42)
    box('face', (hx, 1532, hz + 120), (96, 96, 16), TEXBLACK, root, bevel=10)
    hex_mesh(root, BLACK, hx, 1532, hz + 126, 72, 72)
    for (y, z, x) in ((1260, 575, 655), (1380, 512, 646)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_precleaner(side=RIGHT):
    """Safari-type body with a cyclonic pre-cleaner bowl instead of the ram."""
    root = group('snorkel_precleaner')
    off = 40
    wing_y = top_y(side * 700, 660)
    path = [(side * 705, wing_y - 60, 660), (side * 705, wing_y + 80, 660), (side * (660 + off), 1160, 630),
            (side * (640 + off), 1320, 510), (side * (612 + off), 1355, 415), (side * (612 + off), 1380, 405)]
    pts = fillet(path, 110, steps=10)
    sweep('body', [tuple(p) for p in pts], rounded_rect(95, 75, 30, 5), TEXBLACK, root)
    box('wingSeal', (side * 705, wing_y + 6, 660), (140, 10, 140), RUBBER, root, bevel=4)
    hx, hz = side * (612 + off), 405
    lib.cylinder('stem', (hx, 1402, hz), (0, 1, 0), 89, 48, TEXBLACK, root)
    # smoked polycarbonate, not the white it used to be
    lib.cylinder('bowl', (hx, 1462, hz), (0, 1, 0), 160, 72, material('ClearBowl', 0x9aa3a9, rough=0.28, metal=0.0), root, n=32)
    lib.cylinder('bowlBase', (hx, 1432, hz), (0, 1, 0), 134, 12, TEXBLACK, root, n=32)
    lib.cylinder('bowlTop', (hx, 1502, hz), (0, 1, 0), 164, 10, TEXBLACK, root, n=32)
    lib.cylinder('lid', (hx, 1522, hz), (0, 1, 0), 134, 32, TEXBLACK, root, n=32)
    sphere('knob', (hx, 1542, hz), 28, TEXBLACK, root)
    for (y, z, x) in ((1260, 575, 655), (1300, 548, 652)):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 18, 36), STEEL, root, bevel=2)
    return root


def snorkel_sleek(side=RIGHT):
    """Mega Jimny Supa-Sleek V4.

    Corrected 2026-09-22: the 2 in stainless tube is not visible at all --
    it runs inside a black moulding against the pillar -- and the intake is
    a louvred panel at the top of the A-pillar facing OUTWARD, not a scoop
    facing back. From the far side of the car you barely see it, which is
    the whole point of the product."""
    root = group('snorkel_sleek')
    off = 26
    pts = fillet(_pillar_path(side, off, 1500), 70, steps=8)
    sweep('cowl', [tuple(p) for p in pts], rounded_rect(72, 46, 16, 4), TEXBLACK, root)
    box('cover', (side * 712, 1000, 620), (46, 32, 180), TEXBLACK, root, bevel=8)
    hx, hz = side * (612 + off), 405
    box('vent', (hx + side * 10, 1480, hz), (30, 140, 92), TEXBLACK, root, bevel=8)
    for k in range(5):                                      # outward-facing louvres
        box(f'louvre{k}', (hx + side * 26, 1428 + k * 22, hz), (5, 13, 72), RUBBER, root, bevel=0)
    for (y, z, x) in ((1300, 555, 650),):
        box(f'bracket{y}', (side * (x + off / 2), y, z), (off + 10, 16, 30), STEEL, root, bevel=2)
    return root


# ==================================================================== MIRRORS
# Both replace the stock door mirrors (hidden by the page). Mounted on the
# door's mirror triangle like the stock unit (front top corner of the door).
MIR_X, MIR_Y, MIR_Z = 705, 1165, 445        # door skin at the mirror triangle


def mirrors_urnieta():
    """URNIETA SALADO Side Mirror Kit (0702022), off the factory drawing
    UN-JIMNY-FB-014: 411 tall x 237 across. One continuous 16 mm tube leaves
    a vertical pivot barrel at the door's upper front corner, turns down,
    runs behind the head at 57% of its width, then turns back in to a second
    barrel on the stock mirror triangle -- a C opening toward the body, with
    the 152 x 235 head slung from it on a four-bolt saddle plate. Black only.
    Dimensions other than the 411 and 237 are read off the drawing."""
    root = group('mirrors_urnieta')
    ytop, ybot = 1317, 994                                   # the two pivot barrels, 323 apart
    hy, hx_out = 1170, 237                                   # head centre height, outer face
    for s in (-1, 1):
        xt = s * (MIR_X + 172)                               # vertical tube, 57% across the head
        # door-mounted feet: a wedge bracket up at the window frame, the stock
        # mirror triangle below, and the trim panel that covers the gap
        box(f'trim{s}', (s * (MIR_X - 3), (ytop + ybot) / 2, 512), (6, ytop - ybot + 60, 58), BLACK, root, bevel=3)
        box(f'wedge{s}', (s * (MIR_X + 6), ytop + 18, 508), (22, 74, 62), BLACK, root, bevel=4)
        box(f'foot{s}', (s * (MIR_X + 6), ybot - 16, 516), (22, 66, 74), BLACK, root, bevel=4)
        for yy in (ytop, ybot):
            lib.cylinder(f'pivot{s}{yy}', (s * (MIR_X + 40), yy, 506), (0, 1, 0), 36, 32, BLACK, root, n=18)
            lib.cylinder(f'collar{s}{yy}', (s * (MIR_X + 78), yy, 506), (1, 0, 0), 26, 34, BLACK, root, n=16)
            lib.cylinder(f'pinch{s}{yy}', (s * (MIR_X + 92), yy + 14, 506), (0, 1, 0), 11, 16, STEEL, root, n=6)
        tube(f'arm{s}', [(s * (MIR_X + 60), ytop, 506), (xt, ytop, 506), (xt, ybot, 506), (s * (MIR_X + 60), ybot, 506)],
             16, BLACK, root, bend=36)
        # head: upright rounded rectangle, glass looking back down the car
        head = box(f'head{s}', (s * (MIR_X + 161), hy, 470), (152, 235, 62), BLACK, root, bevel=39)
        head.modifiers['bevel'].segments = 6
        box(f'plateau{s}', (s * (MIR_X + 168), hy, 504), (100, 126, 16), BLACK, root, bevel=22)
        box(f'glass{s}', (s * (MIR_X + 161), hy, 438), (123, 208, 3), CHROME, root, bevel=0)
        box(f'glassRim{s}', (s * (MIR_X + 161), hy, 440), (136, 221, 3), RUBBER, root, bevel=0)
        box(f'saddle{s}', (xt, hy, 518), (70, 66, 14), BLACK, root, bevel=4)
        for (dx, dy) in ((-25, -20), (-25, 20), (25, -20), (25, 20)):
            lib.cylinder(f'saddleBolt{s}{dx}{dy}', (xt + dx, hy + dy, 528), (0, 0, 1), 11, 8, STEEL, root, n=6)
        box(f'badge{s}', (s * (MIR_X + 95), hy, 498), (16, 78, 5), material('LabelWhite', 0xf0f0ec, rough=0.6), root, bevel=2)
        box(f'boss{s}', (s * (MIR_X + hx_out - 6), hy - 60, 486), (10, 34, 26), BLACK, root, bevel=3)
    return root


def mirrors_damd():
    """DAMD Truck Mirror, measured off the owner's photos: tall 150 x 250 head
    with big radii hanging inside a U of 20 mm tube; the top arm clamps onto
    the DOOR's window frame, the vertical run passes behind the head's outer
    third, the bottom arm returns to a hinge block on a plate at the cowl
    beside the door hinge.

    The top bracket sits on the frame, not in mid-air beside it. Probed on
    this model, right side: the painted band between the windscreen glass and
    the door glass runs |x| 645-658 over z 410-510 at y 1300-1340, and the
    door's half of it -- the bit a clamp may grip -- is the rear half, around
    z 430-470. The old bracket was at |x| 703 over z 470-580, which is the
    door SKIN's width carried up to window height, so it floated about 50 mm
    outboard of the frame and lay across the windscreen."""
    root = group('mirrors_damd')
    FRAME_X, FRAME_Z = 656, 448                    # door window frame, outer face
    for s in (-1, 1):
        xd = s * MIR_X
        xo = s * (MIR_X + 175)                     # vertical tube
        loop = [(s * (FRAME_X + 16), 1315, FRAME_Z), (xo, 1315, 490), (xo, 1000, 490), (xd + s * 6, 1000, 505)]
        tube(f'arm{s}', loop, 20, BLACK, root, bend=55)
        # top bracket: a pad lying on the frame (its inner half buried in the
        # paint, so it reads as clamped rather than floating), and the clamp
        # that grips the tube where the tube meets it
        box(f'topPlate{s}', (s * (FRAME_X + 3), 1312, FRAME_Z), (8, 88, 76), BLACK, root, bevel=3)
        box(f'topClamp{s}', (s * (FRAME_X + 30), 1315, FRAME_Z), (44, 34, 34), BLACK, root, bevel=4)
        for dy in (-13, 13):                       # the pinch bolts through the clamp
            lib.cylinder(f'topBolt{s}{dy}', (s * (FRAME_X + 50), 1315 + dy, FRAME_Z), (s, 0, 0),
                         9, 14, STEEL, root, n=8)
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
def rack_platform(pid, W, L, slat_dir='across', slats=None, rail=(50, 45), legs=6, deflector=True, mesh=False, top=None,
                  hoop=0, round_bars=False):
    """Flat aluminium platform on gutter legs. slat_dir 'across' (Front Runner,
    ARB) or 'along' (Yakima LockNLoad, Rhino Pioneer). `hoop` adds a tube
    perimeter standing that many mm above the deck (IPF, JAOS), `round_bars`
    swaps the flat slats for round crossbars (Yakima LockNLoad) and `mesh`
    lays a grid floor under them (APIO, Rhino Pioneer)."""
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
            if round_bars:
                tube(f'bar{i}', [(-W / 2 + rail[0], top - 4, z), (W / 2 - rail[0], top - 4, z)], 42, BLACK, root)
                continue
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
    if hoop:                                             # tube perimeter standing proud of the deck
        hy = top + hoop
        loop = [(-W / 2 + rail[0], hy, z0 + rail[0]), (-W / 2 + rail[0], hy, z1 - rail[0]),
                (W / 2 - rail[0], hy, z1 - rail[0]), (W / 2 - rail[0], hy, z0 + rail[0]),
                (-W / 2 + rail[0], hy, z0 + rail[0])]
        tube('hoop', loop, 34, BLACK, root, bend=70)
        for s2 in (-1, 1):
            for k in range(3):
                zz = z0 + 120 + k * (L - 240) / 2
                box(f'stanchion{s2}{k}', (s2 * (W / 2 - rail[0]), top + hoop / 2, zz), (26, hoop, 26), BLACK, root, bevel=3)
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
    W, ytop, H = 1496, 720, 134
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
    W, ytop, HB = 1462, 640, 133
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
        k = W / 1656.0                                       # the quoted x's are for DAMD's 1656 bar
        for (dx, yy, dia, mat_, dome) in ((703 * k, 573, 64, amber, True), (613 * k, 546, 64, red, True),
                                          (757 * k, 471, 64, LENS, True), (453 * k, 430, 57, red, False)):
            lib.cylinder(f'lampCan{s}{int(dx)}', (s * dx, yy, zf + 10), (0, 0, 1), dia + 12, 28, TEXBLACK, root, n=22)
            lib.cylinder(f'lampRim{s}{int(dx)}', (s * dx, yy, zf - 6), (0, 0, 1), dia + 6, 6, CHROME, root, n=22)
            lib.cylinder(f'lampLens{s}{int(dx)}', (s * dx, yy, zf - 10), (0, 0, 1), dia, 12 if dome else 4, mat_, root, n=22)
            if dome:                                         # the lenses are domed, not flat
                d = flatten(lib.sphere(f'lampDome{s}{int(dx)}', (s * dx, yy, zf - 6), dia, mat_, root), (s * dx, yy, zf - 6), 0.34)
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
    y, zf, W, H, D = 585, 1745, 1428, 170, 140
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
    W, ytop, H, D, z = 1492, 640, 230, 150, -1650
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
    y, zf, W, H, D = 640, 1745, 1444, 120, 110
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


# ===================================================== URNIETA (SALADO / 1970)
# Chinese brand (STARK, Dongguan; 歐尼塔), JB74/JC74 only. Every dimension
# below is off the factory drawings on urnieta.com -- the grilles are both
# 1337 x 241 with a 592 x 126 centre opening, and the bumpers carry their own
# drawing numbers. Widths are pulled in so the bars stay inside the tyre line.
UNT_TEXT = material('LabelWhite', 0xf0f0ec, rough=0.6)


def _urnieta_grille(pid, kind):
    """Shared outline for both grilles (UN-JIMNY-FB-004 and -026): the stock
    panel with a 592 x 126 recessed centre, filled with horizontal louvres
    for SALADO and fine mesh for 1970, URNIETA lettering across the middle."""
    root = group(f'grille_{pid}')
    ow, oh, cy = 592, 126, 852
    grille_panel('panel', root, TEXBLACK, (ow, oh, cy))
    lamp_bezels(root, TEXBLACK, 'square')
    z = face_z(0)
    box('surround', (0, cy, z + 4), (ow + 34, oh + 34, 18), TEXBLACK, root, bevel=8)
    if kind == 'louvre':
        for k in range(7):
            y = cy - oh / 2 + 12 + k * (oh - 24) / 6
            box(f'louvre{k}', (0, y, z - 2), (ow - 18, 9, 16), TEXBLACK, root, bevel=2)
        for k in range(5):                                   # small upright ticks between the bars
            box(f'tick{k}', (-200 + k * 100, cy, z + 2), (7, oh - 26, 12), TEXBLACK, root, bevel=1)
        lib.cylinder('badge', (168, cy - 40, z + 16), (0, 0, 1), 46, 5, CHROME, root, n=22)
    else:
        wire_mesh(root, BLACK, 0, cy, z - 10, ow - 16, oh - 16, pitch=7, bar=1.4)
        box('unt', (-224, cy, z + 16), (56, 30, 5), UNT_TEXT, root, bevel=1)
    box('backing', (0, cy, z - 26), (ow, oh, 3), RUBBER, root, bevel=0)
    text('urnieta', 'URNIETA', (0, cy - 4, z + 16), 62, 6, UNT_TEXT, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    return root


def grille_urnieta_salado():
    return _urnieta_grille('urnieta_salado', 'louvre')


def grille_urnieta_1970():
    return _urnieta_grille('urnieta_1970', 'mesh')


def bumper_urnieta_salado():
    """SALADO front bumper (UN-JIMNY-FB-001), drawn 1426 x 670: a deep winch
    bar with a U-shaped bull bar on two uprights, a recessed light pocket at
    each end behind a mesh guard, an exposed winch plate with a hawse
    fairlead, and a bolted skid plate under it. 42.8 kg of steel and alloy."""
    root = group('frontBumper_urnieta_salado')
    W, y, zf = 1300, 566, 1768
    D, H = 168, 150
    xs = [-W / 2 + W * i / 12 for i in range(13)]
    sweep('body', [(x, y, min(zf, nose_z(x) + 16) - D / 2) for x in xs], rounded_rect(D, H, 16, 4), TEXBLACK, root)
    for s in (-1, 1):
        ez = min(zf, nose_z(W / 2) + 16)
        box(f'endCap{s}', (s * (W / 2 + 4), y, ez - D / 2), (10, H + 6, D + 6), TEXBLACK, root, bevel=5)
        # light pocket: a recessed rectangle behind a mesh stone guard
        px = s * 480
        pz = min(zf, nose_z(480) + 16)
        box(f'pocket{s}', (px, y + 6, pz - 12), (262, 92, 24), BLACK, root, bevel=9)
        box(f'lens{s}', (px, y + 6, pz - 2), (228, 64, 6), LENS, root, bevel=4)
        wire_mesh(root, TEXBLACK, px, y + 6, pz + 4, 224, 62, pitch=12, bar=3)
        # upright from the bar up to the hoop
        box(f'postFoot{s}', (s * 340, y + 46, 1732), (62, 24, 62), TEXBLACK, root, bevel=4)
    # the grille guard: a closed rounded-rectangle loop sitting in front of
    # the grille only, its legs inboard of the headlights so the lamps stay
    # clear. The loop does not reach the ground -- only two inner uprights
    # run past it and down onto the bumper.
    gx, gtop, gbot, hz = 640, 976, 716, 1734
    tube('guard', [(-gx, gbot, hz), (-gx, gtop, hz), (gx, gtop, hz), (gx, gbot, hz), (-gx, gbot, hz)],
         46, TEXBLACK, root, bend=92)
    for s in (-1, 1):
        px2 = s * 340
        tube(f'upright{s}', [(px2, y + 58, hz + 16), (px2, gtop + 4, hz + 16)], 42, TEXBLACK, root)
        for yy in (gtop - 14, gbot + 14):
            box(f'clamp{s}{yy}', (px2, yy, hz + 8), (54, 40, 44), TEXBLACK, root, bevel=5)
    hy = gtop
    text('salado', 'Salado', (-430, y - 128, zf + 2), 42, 4, UNT_TEXT, root)
    text('unt', 'URNIETA', (452, gbot + 24, hz + 24), 22, 3, UNT_TEXT, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    # winch plate, fairlead and skid
    box('plate', (0, y - 6, zf + 6), (330, 165, 3), PLATE, root, bevel=1)
    box('winchBox', (0, y - 158, zf - 120), (640, 176, 210), TEXBLACK, root, bevel=6)
    lib.cylinder('winchDrum', (0, y - 150, zf - 40), (1, 0, 0), 120, 420, BLACK, root, n=22)
    for s in (-1, 1):
        lib.cylinder(f'winchEnd{s}', (s * 220, y - 150, zf - 40), (1, 0, 0), 150, 70, TEXBLACK, root, n=22)
        box(f'ledBar{s}', (s * 300, y - H / 2 - 24, zf - 14), (180, 40, 34), BLACK, root, bevel=5)
        box(f'ledLens{s}', (s * 300, y - H / 2 - 24, zf + 4), (154, 22, 5), LENS, root, bevel=2)
        box(f'shackle{s}', (s * 250, y - 250, zf - 70), (44, 82, 40), STEEL, root, bevel=8)
    box('winchPlate', (0, y - 150, zf - 96), (620, 190, 14), STEEL, root, bevel=3)
    box('fairlead', (0, y - 246, zf - 30), (240, 70, 16), STEEL, root, bevel=14)
    box('hawse', (0, y - 246, zf - 24), (150, 32, 10), RUBBER, root, bevel=8)
    for k in range(6):
        lib.cylinder(f'wbolt{k}', (-250 + k * 100, y + 66, zf - 8), (0, 0, 1), 15, 8, STEEL, root, n=6)
    box('skid', (0, y - 258, zf - 150), (760, 8, 280), STEEL, root, bevel=3,
        rot=Matrix.Rotation(math.radians(-26), 3, 'X'))
    valance(root, corners=False)
    return root


def rear_urnieta_salado():
    """SALADO rear bumper (UN-JIMNY-FB-002), drawn 216 tall: a half-height bar
    whose ends wrap back round the corners, a lit window each side (one badged
    Salado, one URNIETA), a flat plate panel in the middle and a step pad
    under each side. 16.4 kg."""
    root = group('rearBumper_urnieta_salado_rear')
    W, ytop, H, D, z = 1414, 620, 216, 150, -1648
    y, zf = ytop - H / 2, z - 150 / 2
    path = [(-W / 2, y, z + 150), (-W / 2 + 150, y, z), (W / 2 - 150, y, z), (W / 2, y, z + 150)]
    sweep('body', [tuple(p) for p in fillet(path, 40, steps=3)], rounded_rect(D, H, 14, 4), TEXBLACK, root)
    for s in (-1, 1):
        box(f'window{s}', (s * 520, y + 14, zf + 6), (300, 96, 16), BLACK, root, bevel=8)
        box(f'lens{s}', (s * 520, y + 14, zf - 4), (268, 66, 6), material('TailRed', 0xc0161a, rough=0.2), root, bevel=4)
        box(f'badge{s}', (s * 520, y - 54, zf - 2), (190, 26, 5), UNT_TEXT, root, bevel=1)
        box(f'aux{s}', (s * 300, y + 14, zf + 2), (150, 84, 10), BLACK, root, bevel=6)
        # step pad slung under the bar on two brackets
        box(f'step{s}', (s * 470, y - H / 2 - 30, z + 10), (300, 12, 190), ALU_CHEQ, root, bevel=2)
        for k in (-1, 1):
            box(f'stepArm{s}{k}', (s * 470 + k * 110, y - H / 2 - 16, z + 10), (16, 40, 150), TEXBLACK, root, bevel=2)
        box(f'endPlug{s}', (s * (W / 2 - 24), y, z + 118), (14, 40, 26), BLACK, root, bevel=6)
    box('platePanel', (0, y - 24, zf + 8), (430, 190, 16), TEXBLACK, root, bevel=5)
    box('plate', (0, y - 24, zf - 1), (330, 165, 3), PLATE, root, bevel=1)   # sits ON the panel, not 1.5 mm off it
    lib.cylinder('exhaust', (RIGHT * 400, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    return root


def bumper_urnieta_1970():
    """1970 front bumper (UN-JIMNY-FB-027), drawn 1547 x 331: a slim beam
    whose ends sweep back into winged corners with three vent slots each, a
    louvred centre panel carrying URNIETA and a 1970 SERIES badge with a lamp
    bracket either side, and a flat lower panel with two tow shackles. 21 kg,
    plastic body on a full metal skid."""
    root = group('frontBumper_urnieta_1970')
    W, y, zf, D, H = 1434, 626, 1762, 118, 102
    xs = [-W / 2 + W * i / 12 for i in range(13)]
    sweep('body', [(x, y, min(zf, nose_z(x) + 10) - D / 2) for x in xs], rounded_rect(D, H, 12, 4), TEXBLACK, root)
    box('centre', (0, y, zf - 6), (840, 86, 20), TEXBLACK, root, bevel=5)
    for k in range(6):                                       # louvres across the centre panel
        box(f'louvre{k}', (0, y - 32 + k * 13, zf + 6), (560, 6, 9), TEXBLACK, root, bevel=1)
    box('badge1970', (272, y - 4, zf + 10), (168, 74, 8), TEXBLACK, root, bevel=6)
    text('n1970', '1970', (272, y + 4, zf + 15), 40, 4, UNT_TEXT, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    box('unt', (-232, y + 2, zf + 12), (104, 22, 6), UNT_TEXT, root, bevel=1)
    for s in (-1, 1):
        box(f'lampBrk{s}', (s * 470, y + 2, zf + 8), (190, 62, 12), TEXBLACK, root, bevel=4)
        box(f'piaa{s}', (s * 470, y + 2, zf + 15), (150, 34, 8), BLACK, root, bevel=3)
        box(f'piaaLens{s}', (s * 470, y + 2, zf + 19), (128, 22, 4), LENS, root, bevel=2)
        ez = min(zf, nose_z(W / 2 - 90) + 10)
        box(f'wing{s}', (s * (W / 2 - 90), y + 16, ez - 60), (180, 120, 150), TEXBLACK, root, bevel=16)
        for k in range(3):                                   # vent slots in the wing
            box(f'vent{s}{k}', (s * (W / 2 - 150), y - 8 + k * 26, ez + 4), (80, 12, 10), RUBBER, root, bevel=2)
        box(f'shackle{s}', (s * 220, y - 128, zf - 22), (54, 92, 46), STEEL, root, bevel=8)
        lib.cylinder(f'shacklePin{s}', (s * 220, y - 112, zf - 22), (1, 0, 0), 20, 66, STEEL, root, n=12)
    box('lowerPanel', (0, y - 140, zf - 40), (1020, 210, 14), TEXBLACK, root, bevel=4)
    box('plate', (0, y - 150, zf - 30), (330, 165, 3), PLATE, root, bevel=1)
    valance(root, corners=False)
    return root


def rear_urnieta_1970():
    """1970 rear bumper (UN-JIMNY-FB-028), drawn 1617 x 265: half height,
    ends wrapped back, and the line's signature -- two round lamps a side
    (the product page calls them GT-R inspired) beside a rectangular recess,
    with a lit URNIETA badge panel on the right and the plate in the middle."""
    root = group('rearBumper_urnieta_1970_rear')
    red = material('TailRed', 0xc0161a, rough=0.18)
    W, ytop, H, D, z = 1421, 606, 205, 128, -1648
    y, zf = ytop - H / 2, z - 140 / 2
    path = [(-W / 2, y, z + 140), (-W / 2 + 140, y, z), (W / 2 - 140, y, z), (W / 2, y, z + 140)]
    sweep('body', [tuple(p) for p in fillet(path, 36, steps=3)], rounded_rect(D, H, 14, 4), TEXBLACK, root)
    box('rail', (0, ytop + 16, z + 40), (1180, 34, 120), TEXBLACK, root, bevel=4)
    for s in (-1, 1):
        for k, dx in enumerate((618, 512)):                  # the two round lamps
            lib.cylinder(f'lampCan{s}{k}', (s * dx, y + 6, zf + 16), (0, 0, 1), 92, 34, TEXBLACK, root, n=24)
            lib.cylinder(f'lampRim{s}{k}', (s * dx, y + 6, zf - 2), (0, 0, 1), 88, 10, CHROME, root, n=24)
            lib.cylinder(f'lampLens{s}{k}', (s * dx, y + 6, zf - 10), (0, 0, 1), 76, 10, red, root, n=24)
            d = flatten(lib.sphere(f'lampDome{s}{k}', (s * dx, y + 6, zf - 14), 76, red, root), (s * dx, y + 6, zf - 14), 0.34)
        box(f'recess{s}', (s * 372, y + 6, zf + 8), (150, 84, 14), BLACK, root, bevel=6)
        box(f'step{s}', (s * 470, y - H / 2 - 24, z + 10), (250, 12, 170), ALU_CHEQ, root, bevel=2)
        box(f'endPlug{s}', (s * (W / 2 - 22), y, z + 112), (14, 36, 24), BLACK, root, bevel=6)
    box('badgePanel', (RIGHT * 250, y + 6, zf + 4), (200, 60, 10), BLACK, root, bevel=4)
    box('badgeText', (RIGHT * 250, y + 6, zf - 2), (150, 22, 4), UNT_TEXT, root, bevel=1)
    box('platePanel', (0, y - 16, zf + 8), (430, 190, 16), TEXBLACK, root, bevel=5)
    box('plate', (0, y - 16, zf - 3), (330, 165, 3), PLATE, root, bevel=1)
    lib.cylinder('exhaust', (RIGHT * 400, 340, -1640), (RIGHT * 0.4, -0.06, -1), 62, 210, CHROME, root, n=24)
    return root


def side_bar_urnieta_salado():
    """SALADO Side Bar Kit (UN-JIMNY-FB-009), drawn 1270 x 460 for the three
    door. From the fitted photos it is a big single tube along the sill whose
    ends sweep up toward the body, with a long grippy step strip bonded along
    its top (URNIETA printed on it, a Salado badge near the rear) and tubular
    arms back to the chassis -- not a chequer-plate step."""
    root = group('sideStep_urnieta_salado')
    z0, z1, ty = -555, 690, 330
    for s in (-1, 1):
        xo = s * 796
        tube(f'bar{s}', [(s * 700, ty + 84, z0 - 58), (xo, ty, z0 + 50), (xo, ty, z1 - 50), (s * 700, ty + 84, z1 + 58)],
             94, TEXBLACK, root, bend=140)
        # the step strip sits on top of the tube, slightly inboard
        box(f'strip{s}', (xo - s * 4, ty + 50, (z0 + z1) / 2), (76, 14, z1 - z0 - 210), RUBBER, root, bevel=5)
        for k in range(22):                                  # grip ribs moulded into it
            zz = z0 + 130 + k * (z1 - z0 - 260) / 21
            box(f'grip{s}{k}', (xo - s * 4, ty + 56, zz), (68, 6, 16), RUBBER, root, bevel=2)
        box(f'label{s}', (xo - s * 4, ty + 58, (z0 + z1) / 2 - 190), (60, 6, 130), UNT_TEXT, root, bevel=1)
        box(f'badge{s}', (xo, ty - 16, z1 - 130), (10, 40, 150), UNT_TEXT, root, bevel=2)
        for k, zz in enumerate((z0 + 200, z1 - 200)):        # tubular arms into the chassis
            tube(f'arm{s}{k}', [(xo, ty - 10, zz), (s * 540, ty - 40, zz), (s * 430, ty - 46, zz)], 52, TEXBLACK, root, bend=90)
            box(f'armPlate{s}{k}', (s * 418, ty - 46, zz), (14, 120, 84), TEXBLACK, root, bevel=3)
        tube(f'stay{s}', [(xo, ty - 6, z0 + 320), (s * 520, ty - 56, z0 + 150)], 44, TEXBLACK, root, bend=70)
    return root


def side_skirt_urnieta_1970():
    """1970 Side Skirt Kit (UN-JIMNY-FB-030), drawn 1433 x 176: a one-piece
    moulding along the sill with a long raised rib, three bolt heads along
    its top edge and a kicked-up tail at each end. 4.6 kg the pair."""
    root = group('sideStep_urnieta_1970')
    z0, z1, ty = -600, 833, 338
    for s in (-1, 1):
        body = box(f'skirt{s}', (s * 762, ty, (z0 + z1) / 2), (46, 176, z1 - z0), TEXBLACK, root, bevel=12)
        body.modifiers['bevel'].segments = 3
        box(f'rib{s}', (s * 786, ty - 18, (z0 + z1) / 2), (16, 34, z1 - z0 - 180), TEXBLACK, root, bevel=8)
        box(f'ribLip{s}', (s * 790, ty - 18, (z0 + z1) / 2), (8, 12, z1 - z0 - 220), BLACK, root, bevel=4)
        for k, zz in enumerate((z0 + 250, (z0 + z1) / 2, z1 - 250)):
            lib.cylinder(f'bolt{s}{k}', (s * 784, ty + 62, zz), (1, 0, 0), 22, 10, TEXBLACK, root, n=8)
        for k, zz in enumerate((z0 + 40, z1 - 40)):          # the ends kick up to meet the arches
            box(f'tail{s}{k}', (s * 756, ty + 46, zz), (44, 130, 96), TEXBLACK, root, bevel=14)
        box(f'tab{s}', (s * 736, ty + 70, z1 - 150), (30, 46, 120), TEXBLACK, root, bevel=3)
    return root


# The bonnet's own surface, measured off the model every 100 mm of z, so an
# overlay panel can follow it instead of floating.
BONNET_Y = ((900, 1131), (1000, 1118), (1100, 1111), (1200, 1100), (1300, 1094),
            (1400, 1084), (1500, 1072), (1600, 1058))


def bonnet_y(z):
    for (z0, y0), (z1, y1) in zip(BONNET_Y, BONNET_Y[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return y0 + (y1 - y0) * max(0.0, min(1.0, t))
    return BONNET_Y[-1][1]


def _urnieta_hood(pid, vent_z, vent_w, slots, corner_vent):
    """Both URNIETA bonnets are drawn 1408 x 882 (UN-JIMNY-FB-003, -025). On
    the car the panel reads as stock apart from the intake, which is a WIDE
    and nearly FLUSH louvre set into the bonnet -- about 43% of the bonnet's
    width on the SALADO, smaller and further forward on the 1970 -- so that
    is what is modelled, on the bonnet's own measured surface."""
    root = group(f'hood_{pid}')
    vy = bonnet_y(vent_z)
    box('surround', (0, vy + 12, vent_z), (vent_w, 26, 150), PAINT, root, bevel=12)
    box('well', (0, vy + 19, vent_z), (vent_w - 44, 14, 118), BLACK, root, bevel=6)
    for k in range(slots):                                   # long openings, split by a centre rib
        dx = (k - (slots - 1) / 2) * (vent_w - 70) / max(1, slots)
        box(f'slot{k}', (dx, vy + 24, vent_z), ((vent_w - 110) / slots, 10, 96), BLACK, root, bevel=4)
        for j in range(4):                                   # cross fins inside each opening
            box(f'fin{k}{j}', (dx, vy + 27, vent_z - 36 + j * 24), ((vent_w - 118) / slots, 5, 8), TEXBLACK, root, bevel=1)
    box('rib', (0, vy + 25, vent_z), (16, 12, 126), PAINT, root, bevel=4)
    box('lip', (0, vy + 18, vent_z - 74), (vent_w - 20, 22, 18), PAINT, root, bevel=8)
    if corner_vent:
        cz, cx = 1452, RIGHT * 468
        box('cvent', (cx, bonnet_y(cz) + 6, cz), (206, 20, 104), TEXBLACK, root, bevel=8)
        for k in range(5):
            box(f'cfin{k}', (cx, bonnet_y(cz) + 13, cz - 38 + k * 19), (168, 6, 8), BLACK, root, bevel=1)
    return root


def hood_urnieta_salado():
    return _urnieta_hood('urnieta_salado', 986, 610, 2, False)


def hood_urnieta_1970():
    return _urnieta_hood('urnieta_1970', 1180, 430, 3, True)


def _urnieta_spare_dish(root, mat=None):
    """URNIETA's covers sit on the WHEEL FACE inside the tyre -- about 0.62
    of the tyre's diameter in the fitted photos -- not over the whole wheel
    the way the stock hard cover does."""
    cx, cy = SPARE['x'], SPARE['y']
    R = 0.31 * SPARE['dia']
    zf = SPARE_FACE_Z + 36
    mat = mat or TEXBLACK
    # built from discs along the car's Z: lathe() revolves about X (it is the
    # rim builder's helper) and would lay the cover on its side
    lib.cylinder('back', (cx, cy, zf + 40), (0, 0, 1), 2 * (R - 20), 80, mat, root, n=64)
    lib.cylinder('rim', (cx, cy, zf + 2), (0, 0, 1), 2 * (R + 6), 22, mat, root, n=64)
    lib.cylinder('face', (cx, cy, zf - 10), (0, 0, 1), 2 * (R - 18), 16, mat, root, n=64)
    return cx, cy, R, zf


def spare_urnieta_salado():
    """SALADO Extended Spare Tire Cover (0702003), 3.4 kg: a round hard cover
    whose lower half folds down into a work table, with a latch knob at the
    top and the seam running across below the lettering."""
    root = group('spareCover_urnieta_salado')
    cx, cy, R, zf = _urnieta_spare_dish(root)
    box('seam', (cx, cy - 40, zf - 20), (2 * R - 60, 8, 6), BLACK, root, bevel=2)
    lib.cylinder('knob', (cx, cy + R - 44, zf - 22), (0, 0, 1), 44, 16, TEXBLACK, root, n=20)
    lib.cylinder('knobFace', (cx, cy + R - 44, zf - 30), (0, 0, 1), 30, 5, STEEL, root, n=20)
    for s in (-1, 1):
        box(f'hinge{s}', (cx + s * (R - 70), cy - 44, zf - 20), (40, 22, 8), STEEL, root, bevel=2)
    t = text('unt', 'URNIETA', (cx, cy - 14, zf - 22), 46, 5, UNT_TEXT, root,
             font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    t.rotation_euler[2] = math.pi                            # it faces the rear
    return root


def spare_urnieta_1970():
    """1970 Spare Tire Cover (0703002), 3.4 kg: the same round cover carrying
    a MOLLE field that also takes the matching pouch."""
    root = group('spareCover_urnieta_1970')
    cx, cy, R, zf = _urnieta_spare_dish(root)
    box('panel', (cx, cy - 6, zf - 22), (2 * R - 110, 2 * R - 150, 10), TEXBLACK, root, bevel=14)
    for r in range(3):
        yy = cy + 46 - r * 50
        box(f'row{r}', (cx, yy, zf - 28), (2 * R - 170, 20, 7), WEBBING, root, bevel=2)
        for c in range(4):
            box(f'loop{r}{c}', (cx - 84 + c * 56, yy, zf - 32), (9, 20, 5), WEBBING, root, bevel=1)
    t = text('unt', 'URNIETA', (cx, cy + R - 56, zf - 24), 34, 5, UNT_TEXT, root,
             font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    t.rotation_euler[2] = math.pi
    return root


def gullwing_urnieta_1970():
    """URNIETA 1970 Gullwing Window Kit (0703009), 6.35 kg, ABS + aluminium-
    magnesium + glass, black. It REPLACES the rear quarter glass rather than
    sitting over it: the original pane comes out, a fixed surround goes into
    the aperture, and the opening pane hangs inside THAT on a top hinge with
    two gas struts. No cutting, no drilling.

    Redrawn twice, 2026-09-24. The first version was an 800 x 540 slab laid on
    the flank -- the aperture (QUARTER, sampled off the model) is only 600 x
    360, so it overhung the glass on every edge. The second filled the whole
    aperture, which is still wrong: the part that MOVES is not the aperture,
    it is what is left inside the fixed surround, so it comes out about 520 x
    280 -- a good deal smaller than the window it sits in. The page hides the
    stock pane behind it (cfg.hideQuarterGlass).
    """
    root = group('gullwing')
    q = QUARTER
    cz, cy = (q['z0'] + q['z1']) / 2, (q['y0'] + q['y1']) / 2
    XB = 702                                                 # the glass surface, |x|
    BAR = 36                                                 # the fixed surround's width
    OW, OH = q['z1'] - q['z0'] + 20, q['y1'] - q['y0'] + 20  # surround, outer
    IW, IH = OW - 2 * BAR, OH - 2 * BAR                      # the hole left in it
    PW, PH, PT = IW + 26, IH + 26, 20                        # the pane that moves
    HINGE_Y = cy + IH / 2 + 6
    TH = math.radians(36)                                    # how far it is propped open
    sin, cos = math.sin(TH), math.cos(TH)
    for s in (-1, 1):
        # the fixed surround, flush in the aperture
        for (dy, dz, sy, sz) in ((IH / 2 + BAR / 2, 0, BAR, OW), (-IH / 2 - BAR / 2, 0, BAR, OW),
                                 (0, IW / 2 + BAR / 2, IH, BAR), (0, -IW / 2 - BAR / 2, IH, BAR)):
            box(f'surround{s}{dy}{dz}', (s * XB, cy + dy, cz + dz), (18, sy, sz), TEXBLACK, root, bevel=5)
        # the pane, swung up about the hinge at the top of the hole
        rot = Matrix.Rotation(-s * TH, 3, 'Y')
        px, py = XB + 4 + (PH / 2) * sin, HINGE_Y - (PH / 2) * cos
        box(f'frame{s}', (s * px, py, cz), (PT, PH, PW), TEXBLACK, root, bevel=7, rot=rot)
        gx, gy = px + 7 * cos, py + 7 * sin
        box(f'glass{s}', (s * gx, gy, cz), (6, PH - 58, PW - 58), GLASS, root, bevel=0, rot=rot)
        # hinges on the surround's top bar
        for k in (-1, 1):
            box(f'hinge{s}{k}', (s * (XB + 6), HINGE_Y + 10, cz + k * (IW / 2 - 60)),
                (26, 22, 62), TEXBLACK, root, bevel=4)
        # gas struts: foot on the surround's bottom bar, head partway up the pane
        for k in (-1, 1):
            z = cz + k * (IW / 2 - 90)
            fx, fy = XB + 6, cy - IH / 2 - 4
            hx_, hy = XB + 4 + 92 * sin, HINGE_Y - 92 * cos   # 92 mm down the pane
            dx, dy = hx_ - fx, hy - fy
            L = math.hypot(dx, dy)
            lib.cylinder(f'strut{s}{k}', (s * (fx + dx / 2), fy + dy / 2, z),
                         (s * dx, dy, 0), 16, L, STEEL, root, n=12)
            box(f'strutFoot{s}{k}', (s * fx, fy, z), (22, 22, 22), TEXBLACK, root, bevel=3)
    return root


RACK_WOOD = material('RackWood', 0xb07a3e, rough=0.55)


def rack_wood(size='half'):
    """DAMD trip basket roof rack, HALF size (TB-HR1): 1350 x 600 x 160 mm,
    13.5 kg. A black steel WIRE basket -- longitudinal rods over three cross
    rods -- inside a rounded tube frame on short stanchions, with the wood
    where it actually is on the product: a curved Accoya panel wrapping the
    leading edge (carrying the oval trip basket badge) and a small block on
    each side. It sits at the FRONT of the roof on TERZO cross bars, not on
    gutter legs."""
    root = group('roofRack_wood' if size == 'half' else f'roofRack_wood_{size}')
    # Corrected 2026-09-21 (docs/jb74-fitment.json): DAMD's half size takes
    # 400 mm off the WIDTH, not the length. Both are 1350 mm front to back and
    # both run the length of the roof with the wood leading edge up at the
    # windscreen header; the half leaves ~600 mm of bare cross bar beside it,
    # which is what DAMD's own copy means by room for skis and boards.
    H, L = 160, 1350
    W = 600 if size == 'half' else 1000                      # TB-HR1 / TB-RR1
    xc = 350 if size == 'half' else 0                        # the half sits over to one side
    # Fore-aft position measured 2026-09-22 off DAMD's own two fitted side
    # views (docs/jb74-fitment.json): the wooden nose lands 218-325 mm behind
    # the windscreen header and the tail 218-317 mm ahead of the rear roof
    # edge -- essentially centred, over the front door, not up at the screen.
    z1 = ROOF_Z_FRONT - 270
    z0 = z1 - L
    zc = (z0 + z1) / 2
    deck = RACK_TOP - 30
    top = deck + H
    # two TERZO cross bars with gutter feet
    for zz in (zc - 395, zc + 395):                          # TERZO bars, 790 apart (measured)
        sweep(f'bar{zz}', [(-660, deck - 34, zz), (660, deck - 34, zz)], rounded_rect(70, 26, 6), BLACK, root)
        for s in (-1, 1):
            box(f'foot{s}{zz}', (s * (GUTTER_X + 10), ROOF_Y_EDGE + 16, zz), (60, 74, 52), BLACK, root, bevel=6)
    xl, xr = xc - W / 2, xc + W / 2                          # the basket's own left and right
    # wire floor: rods along the car over cross rods
    n_rod = max(9, int(W / 48))
    for i in range(n_rod):
        x = xl + 40 + i * (W - 80) / (n_rod - 1)
        lib.cylinder(f'rod{i}', (x, deck, zc), (0, 0, 1), 11, L - 60, BLACK, root, n=8)
    for k in range(5):
        zz = z0 + 40 + k * (L - 80) / 4
        lib.cylinder(f'cross{k}', (xc, deck - 10, zz), (1, 0, 0), 14, W - 60, BLACK, root, n=8)
    # rounded tube frame round the rim, on short stanchions
    loop = [(xl + 26, top, z0 + 26), (xl + 26, top, z1 - 26), (xr - 26, top, z1 - 26),
            (xr - 26, top, z0 + 26), (xl + 26, top, z0 + 26)]
    tube('rail', loop, 26, BLACK, root, bend=72)
    for s, xx in ((-1, xl + 26), (1, xr - 26)):
        for k in range(9):
            zz = z0 + 60 + k * (L - 120) / 8
            lib.cylinder(f'post{s}{k}', (xx, (deck + top) / 2, zz), (0, 1, 0), 12, H, BLACK, root, n=8)
    n_wall = max(5, int(W / 95))
    for k in range(n_wall):                                  # rear wall uprights
        x = xl + 60 + k * (W - 120) / (n_wall - 1)
        lib.cylinder(f'wall{k}', (x, (deck + top) / 2, z0 + 26), (0, 1, 0), 12, H, BLACK, root, n=8)
    # The wood, measured 2026-09-22 off DAMD's own fitted side views and their
    # parts list (docs/jb74-fitment.json). Three pieces of timber in the whole
    # kit: one front plate and two side plates. It is NOT a curved wrap and
    # NOT a slab standing upright -- it is a flat board raked back about 19
    # degrees like a wind fairing, with fully half-round ends, its top edge
    # tucked under the rim tube. The installer sets the angle on the clamps,
    # which is why DAMD's own two demo cars measure 15 and 23 degrees.
    rake = math.radians(19)
    ph, pt = 120, 15                                         # plate height and thickness
    yT, zT = top, z1 - 10                                    # top edge, level with the rim tube

    def face(down, out):
        """A point on the plate's face: `down` mm from its top edge, `out` mm
        along its outward normal."""
        return (yT - down * math.cos(rake) + out * math.sin(rake),
                zT + down * math.sin(rake) + out * math.cos(rake))

    pw = W - 20                                              # 980 on the full size, 580 on the half
    prof = [face(0, 0), face(ph, 0), face(ph, -pt), face(0, -pt)]
    prism('frontPlate', prof, xc - (pw - ph) / 2, xc + (pw - ph) / 2, RACK_WOOD, root)
    for xe in (xc - (pw - ph) / 2, xc + (pw - ph) / 2):      # half-round ends, radius = half the height
        (ya, za), (yb, zb) = face(ph / 2, 0), face(ph / 2, -pt)
        lib.cylinder(f'plateEnd{xe:.0f}', ((xe), (ya + yb) / 2, (za + zb) / 2), (1, 0, 0), ph, pt, RACK_WOOD, root, n=20)
    # knob bolts: three across the full size, two across the half, 70% down
    knobs = (0.15, 0.5, 0.85) if size != 'half' else (0.25, 0.75)
    for k, f in enumerate(knobs):
        yk, zk = face(ph * 0.7, 8)
        lib.cylinder(f'knob{k}', (xc - pw / 2 + f * pw, yk, zk), (math.sin(rake), 0, math.cos(rake)), 26, 22, STEEL, root, n=12)
    # the engraved stadium badge sits off to one side of the front plate
    (yb0, zb0), (yb1, zb1) = face(ph * 0.24 - 12, 1.5), face(ph * 0.24 + 13, 1.5)
    prism('badge', [(yb0, zb0), (yb1, zb1), face(ph * 0.24 + 13, 0)[::1], face(ph * 0.24 - 12, 0)[::1]],
          xc - pw / 2 + 80, xc - pw / 2 + 195, TEXBLACK, root)
    # side plates: flat boards on the OUTSIDE of each wall, mid-length
    for xx in (xl - 9, xr + 9):
        box(f'sidePlate{xx:.0f}', (xx, top - 62, z1 - 650), (16, 115, 185), RACK_WOOD, root, bevel=8)
        box(f'sideBadge{xx:.0f}', (xx + (9 if xx > xc else -9), top - 62, z1 - 650), (4, 22, 100), TEXBLACK, root, bevel=2)
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
            # the car's own tail lamps stay; the bar only carries a hook each
            # side. The hook has to bite into the tube -- hung 150 mm below it
            # with nothing between, it read as a red tag floating in mid-air.
            box(f'hook{s}', (s * 330, y - 72, z), (14, 116, 54), RED, root, bevel=4, rot=Matrix.Rotation(s * 0.25, 3, 'Z'))
        elif lamps == 'housing':
            box(f'lampBox{s}', (s * 513, 518, -1560), (380, 170, 90), mat, root, bevel=4)
        elif lamps == 'round':
            # sit them on the bar's rear FACE, and space them off its end, so
            # they neither sink into the bar nor drift as the bar changes width
            zr = z - (D if kind == 'plate' else tube_d) / 2
            for k, xx in enumerate((s * (W / 2 - 70), s * (W / 2 - 180))):
                lib.cylinder(f'lampHsg{s}{k}', (xx, y, zr + 18), (0, 0, 1), 78, 44, BLACK, root, n=24)
                lib.cylinder(f'lampRim{s}{k}', (xx, y, zr - 4), (0, 0, 1), 74, 6, CHROME, root, n=24)
                lib.cylinder(f'lampLens{s}{k}', (xx, y, zr - 9), (0, 0, 1), 66, 6, material('TailRed', 0xc0161a, rough=0.2), root, n=24)
                d = flatten(lib.sphere(f'lampDome{s}{k}', (xx, y, zr - 8), 66, material('TailRed', 0xc0161a, rough=0.2), root), (xx, y, zr - 8), 0.3)
        if steps:
            box(f'step{s}', (s * (W / 2 - 120), y + H / 2 + 4, z + 20), (240, 6, 160), ALU_CHEQ, root, bevel=1)
    if lamps == 'klc':
        # Plate on two tabs right under the tube. Every dimension here is
        # measured off the tube's own underside and rear face so the tabs
        # always bite into the tube and the plate always sits against the
        # tabs -- the old absolute offsets left visible daylight between all
        # three once the bar's diameter changed.
        ty, tz = y - tube_d / 2, z - tube_d / 2
        for s in (-1, 1):
            box(f'plateTab{s}', (s * 110, ty - 38, tz - 12), (24, 96, 34), mat, root, bevel=1)
        box('plate', (0, ty - 92, tz - 27), (330, 165, 3), PLATE, root, bevel=1)
    else:
        box('plate', (0, 585, TAIL_Z - 6), (330, 165, 4), PLATE, root, bevel=1)
    if lamps != 'klc':                                       # the KLC tube stays open underneath, as fitted
        box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)
        for s in (-1, 1):
            box(f'corner{s}', (s * min(740, W / 2 - 30), 520, -1470), (50, 240, 180), mat, root, bevel=6, rot=Matrix.Rotation(math.radians(-s * 25), 3, 'Z'))
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
    # Re-measured 2026-09-21 against MRK's straight-on photo, scaled on the
    # 1645 mm body width: the tube is 34 mm (not 25) and the published 270 mm
    # is the OUTER width, so the tube centres are 236 mm apart. Four rungs at
    # 195 mm, overall 1005 mm tall, and the hoop's rounded top stops under the
    # gutter -- it does not hook over the roof.
    xo = s * 600
    xi = xo - s * 236
    y0, y1 = 620, 1625
    loop = [(xi, y0 + 70, zf), (xi, y1, zf), (xo, y1, zf), (xo, y0, zf), (xi, y0, zf), (xi, y0 + 140, zf)]
    tube('hoop', loop, 34, BLACK, root, bend=88)
    for k in range(4):
        y = y0 + 150 + k * 195
        tube(f'rung{k}', [(xi, y, zf), (xo, y, zf)], 26, BLACK, root)
    for y in (y0 + 250, y1 - 250):                           # two plates onto the factory tailgate hinges
        box(f'tab{y}', (xi + s * 20, y, (TAIL_Z + zf) / 2), (60, 84, abs(TAIL_Z - zf)), BLACK, root, bevel=4)
    return root



# =================================================================== LIGHTING
# Sizes from docs/jb74-lighting.json (maker spec sheets). The STEDI bars are
# the ones people actually put on a Jimny roof; the amber is a clip-on filter
# on the ST3K/ST4K and a bonded yellow lens on the ST1K, so the ST1K reads
# yellow even switched off.
AMBER = material('AmberLens', 0xe08a1e, rough=0.15)
STEDI_YELLOW = material('StediYellow', 0xe8b823, rough=0.14)
KC_YELLOW = material('KCYellow', 0xe0aa18, rough=0.45)


def light_bar_gen(pid, L, hh, dd, segs, rows=1, lens_mat=None):
    """Roof-height light bar on A-pillar brackets, sized from the maker's own
    spec sheet: L x hh x dd in mm and `segs` emitters across. Two rows means
    a double-stack bar (ST4K)."""
    root = group(f'lightBar_{pid}')
    lens_mat = lens_mat or LENS
    y, z = ROOF_Y_EDGE + 70, ROOF_Z_FRONT + 90
    sweep('housing', [(-L / 2, y, z), (L / 2, y, z)], rounded_rect(hh, dd, min(12, hh / 4), 4), BLACK, root)
    box('bezel', (0, y, z + dd / 2 - 6), (L - 24, hh - 12, 4), BLACK, root, bevel=1)
    box('lens', (0, y, z + dd / 2 - 3), (L - 44, hh - 22, 2), lens_mat, root, bevel=0.5)
    n = max(2, segs // rows)
    cup = max(10, min(46, (L - 80) / n - 5))
    for row in range(rows):
        ry = y + (0 if rows == 1 else (row * 2 - 1) * hh / 4.2)
        for k in range(n):
            xk = -L / 2 + 42 + k * (L - 84) / (n - 1)
            lib.cylinder(f'cup{row}{k}', (xk, ry, z + dd / 2 - 9), (0, 0, 1), cup, 6, CHROME, root, n=10)
    for k in range(24):                                      # heat-sink fins down the back
        box(f'fin{k}', (-L / 2 + 30 + k * (L - 60) / 23, y, z - dd / 2 - 4), (5, hh - 6, 12), BLACK, root, bevel=0)
    for s in (-1, 1):
        arm = [(s * 610, ROOF_Y_EDGE - 150, ROOF_Z_FRONT + 40), (s * 620, ROOF_Y_EDGE - 20, ROOF_Z_FRONT + 60),
               (s * (L / 2 + 15), y, z)]
        sweep(f'bracket{s}', [tuple(p) for p in fillet(arm, 40)], rounded_rect(50, 8, 2), BLACK, root)
        box(f'endCap{s}', (s * (L / 2 + 6), y, z), (12, hh + 12, dd + 8), BLACK, root, bevel=3)
    return root


def roof_lights_kc():
    """KC HiLiTES Pro6 six-light gravity bar (91307): 994 x 154 x 85 overall,
    six 152.4 mm lamps at a 156.6 mm pitch, each wearing the black-and-yellow
    KC cover that gives the bar its face. Sits on the rack's front rail."""
    root = group('roofLights_kc_pro6')
    z = RACK_ZC + ARB_L / 2 + 10
    y = RACK_TOP + 120
    pitch = 156.6
    sweep('bar', [(-470, y - 96, z - 34), (470, y - 96, z - 34)], rounded_rect(58, 46, 8, 3), BLACK, root)
    for s in (-1, 1):
        box(f'foot{s}', (s * 400, RACK_TOP - 30, z - 34), (70, 130, 66), BLACK, root, bevel=4)
    for k in range(6):
        x = (k - 2.5) * pitch
        lib.cylinder(f'can{k}', (x, y, z - 36), (0, 0, 1), 150, 76, BLACK, root, n=28)
        annulus(f'bezel{k}', (x, y, z + 6), 66, 78, 12, BLACK, root, n=28)
        lib.cylinder(f'bowl{k}', (x, y, z + 1), (0, 0, 1), 132, 5, CHROME, root, n=28)
        lib.cylinder(f'lens{k}', (x, y, z + 5), (0, 0, 1), 132, 3, LENS, root, n=28)
        lib.cylinder(f'cover{k}', (x, y, z + 12), (0, 0, 1), 156, 6, KC_YELLOW, root, n=28)
        # the cover's face IS the KC logo -- black letters over a smile
        # curve. A straight bar across the middle reads as a road sign.
        text(f'kc{k}', 'KC', (x, y + 6, z + 16), 52, 4, BLACK, root,
             font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
        for j in range(9):
            t = j / 8
            sx = (t - 0.5) * 104
            sy = y - 30 - 22 * math.sin(math.pi * t)
            box(f'smile{k}{j}', (x + sx, sy, z + 16), (16, 11, 3), BLACK, root, bevel=1)
        box(f'stem{k}', (x, y - 84, z - 36), (26, 64, 22), BLACK, root, bevel=3)
    return root


def grille_light(pid):
    """Lighting that lives at the nose rather than on the roof.

    'rally'      STEDI Rally Bar (ST-11-JMN-001): a 63 mm stainless tube
                 across the front of the grille on two legs, carrying an
                 ST1K 21.5 in yellow bar. STEDI's only Jimny nose product --
                 they make no behind-the-grille bracket for this car.
    'lower'      ST1K 21.5 in (546 x 38 x 80) sitting in the lower bumper
                 aperture, the common DIY answer.
    'bushranger' Bushranger NHBGS450LB, 717 mm single row of 21, mounted
                 BEHIND the lower grille with the splash tray trimmed."""
    root = group(f'grilleLight_{pid}')
    zf = nose_z(0)
    if pid == 'rally':
        y = 690
        tube('hoop', [(-560, y, zf + 46), (560, y, zf + 46)], 63, STEEL, root)
        for s in (-1, 1):
            leg = [(s * 540, y, zf + 46), (s * 540, 480, zf + 30), (s * 540, 430, zf - 30)]
            tube(f'leg{s}', [tuple(p) for p in fillet(leg, 60)], 63, STEEL, root)
            box(f'plate{s}', (s * 540, 415, zf - 40), (90, 40, 90), STEEL, root, bevel=4)
        L, hh, dd, n = 546, 38, 80, 20
        y2 = y + 70
        sweep('housing', [(-L / 2, y2, zf + 40), (L / 2, y2, zf + 40)], rounded_rect(hh, dd, 8, 3), BLACK, root)
        box('lens', (0, y2, zf + 40 + dd / 2 - 3), (L - 40, hh - 16, 2), STEDI_YELLOW, root, bevel=0.5)
        for k in range(n):
            xk = -L / 2 + 34 + k * (L - 68) / (n - 1)
            lib.cylinder(f'cup{k}', (xk, y2, zf + 40 + dd / 2 - 8), (0, 0, 1), 22, 6, CHROME, root, n=10)
        for s in (-1, 1):
            box(f'clamp{s}', (s * (L / 2 - 30), y2 - 40, zf + 44), (30, 80, 30), BLACK, root, bevel=3)
    else:
        L, hh, dd, n, lens = ((546, 38, 80, 20, STEDI_YELLOW) if pid == 'lower'
                              else (717, 62, 78, 21, LENS))
        y = 520 if pid == 'lower' else 470
        zc = zf - (6 if pid == 'lower' else 34)              # the Bushranger sits behind the grille
        sweep('housing', [(-L / 2, y, zc), (L / 2, y, zc)], rounded_rect(hh, dd, 8, 3), BLACK, root)
        box('lens', (0, y, zc + dd / 2 - 3), (L - 40, hh - 18, 2), lens, root, bevel=0.5)
        for k in range(n):
            xk = -L / 2 + 34 + k * (L - 68) / (n - 1)
            lib.cylinder(f'cup{k}', (xk, y, zc + dd / 2 - 8), (0, 0, 1), min(30, (L - 68) / n - 4), 6, CHROME, root, n=10)
        for s in (-1, 1):
            box(f'brk{s}', (s * (L / 2 - 20), y - 50, zc - 10), (24, 110, 40), BLACK, root, bevel=3)
    return root


# ================================================================== EXHAUSTS
# docs/jb74-exhaust.json. The tail pipe used to be drawn by one rear bumper,
# which meant every other bumper silently deleted the car's exhaust. It is a
# product family of its own now.
#
# Heights in that file are ground clearances in world mm; parts hang off BODY,
# which already carries the 60 mm the model lifts the shell by, so subtract it.
EXH_LIFT = 60
TI_BLUE = material('TitaniumBlue', 0x3d5a7a, rough=0.28, metal=1.0)
EXH_STEEL = material('ExhaustSteel', 0xc9ced2, rough=0.18, metal=1.0)
# Measured off the model 2026-09-22: the rearmost full-width low body panel
# (the stock rear bumper) ends at z = -1609. The -1735 assumed before put
# every tail pipe 126 mm too far back, which is what made them look like they
# were hanging off the car.
BUMPER_Z = -1612          # rear face of the stock rear bumper
TIP_L = 110               # length of a tail-pipe tip, off the owner's photo


def exhaust(pid, layout='rear', tip_d=76, tips=1, side=RIGHT, tip_y=330, protrude=35,
            cut=0.0, tip_mat=None, muffler=None, muffler_z=-1250, muffler_dy=0, roll=False):
    """One tail-pipe system. `layout` picks the silhouette:
       'rear'    drum behind the axle, tip out under the bumper
       'corner'  a tip under each rear bumper corner
       'side'    silencer under the left rocker, tips out ahead of the wheel
       'through' the tip turns outboard through the bumper corner, high up
       'cover'   a slip-over sleeve on the stock pipe, nothing else changes
    """
    root = group(f'exhaust_{pid}')
    tip_mat = tip_mat or EXH_STEEL
    y = tip_y - EXH_LIFT
    pipe = material('ExhaustPipe', 0x6e7276, rough=0.45, metal=0.9)

    def tip_at(name, x, zz, yy, ax=(0, 0, -1)):
        """`zz` is where the tip's MOUTH is; the body runs forward from there,
        so a published protrusion lands where it should."""
        zc = zz - ax[2] * TIP_L / 2
        xc = x - ax[0] * TIP_L / 2
        lib.cylinder(name, (xc, yy, zc), ax, tip_d, TIP_L, tip_mat, root, n=24)
        lib.cylinder(name + 'Mouth', (x - ax[0] * 6, yy, zz - ax[2] * 6), ax, tip_d - 10, 14,
                     material('ExhaustBore', 0x141414, rough=0.9), root, n=24)
        if roll:
            annulus(name + 'Roll', (x - ax[0] * 8, yy, zz - ax[2] * 8), tip_d / 2 - 3, tip_d / 2 + 5, 12,
                    tip_mat, root, n=24)
        return (xc - ax[0] * TIP_L / 2, zc - ax[2] * TIP_L / 2)   # forward end, to join a pipe to

    if layout == 'cover':
        fx, fz = tip_at('tipR', side * 430, BUMPER_Z - protrude, y)
        lib.cylinder('stub', (fx, y, fz + 90), (0, 0, -1), tip_d - 22, 220, pipe, root, n=18)
        return root

    if layout == 'side':
        # HKS TrailMaster and the Kakimoto DS: everything happens under the
        # left rocker, ahead of the rear wheel; the rear bumper is untouched.
        s = -RIGHT
        # HKS's own demo-car photo puts the tips 150-250 mm ahead of the rear
        # tyre's leading edge. On a 744 mm tyre on the -1047 axle that edge is
        # at z = -675, so the tips finish near -475 and the canister sits
        # forward of them, under the door.
        zc = -110
        if muffler:
            ml, md = muffler
            lib.cylinder('canister', (s * 790, y + 30, zc), (0, 0, 1), md, ml, EXH_STEEL, root, n=26)
            for k in range(9):                               # perforated heat shield
                lib.cylinder(f'perf{k}', (s * 790, y + 30 + md / 2 - 4, zc - ml / 2 + 40 + k * (ml - 80) / 8),
                             (0, 1, 0), 16, 8, BLACK, root, n=8)
            for zz in (zc - ml / 2 - 10, zc + ml / 2 + 10):
                box(f'strap{zz}', (s * 790, y + 30, zz), (md + 16, md + 16, 16), BLACK, root, bevel=4)
        for k in range(tips):
            xx = s * (790 + (k - (tips - 1) / 2) * (tip_d + 12))
            tip_at(f'tip{k}', xx, zc - (muffler[0] / 2 if muffler else 200) - 150, y + 30)
        lib.cylinder('run', (s * 760, y + 50, zc + 420), (0, 0, 1), tip_d - 16, 500, pipe, root, n=16)
        return root

    if layout == 'through':
        # TANIGUCHI Compe R: the bullet turns out through the bumper corner,
        # high enough to stay out of a water crossing.
        yy = 560 - EXH_LIFT
        x = side * 620
        lib.cylinder('bullet', (x - side * 60, yy, BUMPER_Z + 130), (1, 0, 0), tip_d + 60, 300, EXH_STEEL, root, n=24)
        tip_at('tip', x + side * 50, BUMPER_Z + 130, yy, ax=(side, 0, 0))
        lib.cylinder('down', (side * 500, yy - 140, BUMPER_Z + 200), (0, 1, 0), tip_d - 12, 260, pipe, root, n=16)
        return root

    if muffler:
        ml, md = muffler
        if layout == 'corner':
            box('resonator', (0, y + 20, muffler_z), (ml, md, md * 0.8), EXH_STEEL, root, bevel=18)
        elif pid.startswith('apio_yoshimura'):
            # a motorcycle cannon lying across the car, which is the whole
            # point of this system
            lib.cylinder('cannon', (side * 60, y + 26, muffler_z), (1, 0, 0), md, ml, tip_mat, root, n=28)
            annulus('cannonEndL', (side * 60 - ml / 2, y + 26, muffler_z), md / 2 - 8, md / 2 + 2, 14, EXH_STEEL, root, n=28)
            box('logo', (side * 60, y + 26 + md / 2 - 4, muffler_z), (200, 6, 40), BLACK, root, bevel=2)
            for zz in (muffler_z - 70, muffler_z + 70):
                box(f'hanger{zz}', (side * 60 - ml / 2 + 40, y + 26 + md / 2 + 20, zz), (60, 50, 14), BLACK, root, bevel=3)
        else:
            # muffler_dy tucks the drum up over the axle, where a compact one
            # actually lives and where it stops showing in a side view
            lib.cylinder('drum', (0, y + 20 + muffler_dy, muffler_z), (0, 0, 1), md, ml, EXH_STEEL, root, n=26)
        lib.cylinder('inlet', (0, y + 30 + muffler_dy, muffler_z + ml / 2 + 180), (0, 0, 1), tip_d - 22, 360, pipe, root, n=16)

    if layout == 'quad':
        # URNIETA SALADO: one central silencer splitting two ways, two tips a
        # side at 279 and 368 mm off centre -- 89 mm apart, so each pair reads
        # as one bonded unit inside a squared shroud. The tips clamp to the
        # tail section and hang below the bumper; nothing is cut.
        for xx in (-368, -279, 279, 368):
            tip_at(f'tip{xx}', xx, BUMPER_Z - protrude, y)
        for sd in (-1, 1):
            box(f'shroud{sd}', (sd * 323.5, y, BUMPER_Z + 54), (210, tip_d + 34, 130), BLACK, root, bevel=12)
            lib.cylinder(f'feed{sd}', (sd * 200, y + 26, muffler_z - 150), (sd * 0.62, -0.16, -1), tip_d - 26, 520, pipe, root, n=16)
        return root
    if layout == 'corner':
        for s in (-1, 1):
            fx, fz = tip_at(f'tip{s}', s * 540, BUMPER_Z - protrude, y)
            tube(f'link{s}', [(0, y + 20, muffler_z - muffler[0] / 2 if muffler else muffler_z),
                              (s * 300, y + 8, (muffler_z + fz) / 2), (fx, y, fz + 30)],
                 tip_d - 22, pipe, root, bend=200)
    else:
        for k in range(tips):
            xx = side * 430 + (k - (tips - 1) / 2) * (tip_d + 14)
            fx, fz = tip_at(f'tip{k}', xx, BUMPER_Z - protrude, y)
            # A tip with nothing joining it to the silencer reads as a chrome
            # can floating under the car -- this is that pipe.
            if muffler:
                z0 = muffler_z - muffler[0] / 2
                tube(f'tail{k}', [(0, y + 20 + muffler_dy, z0),
                                  (xx * 0.7, y + 8 + muffler_dy * 0.35, (z0 + fz) / 2),
                                  (fx, y, fz + 30)], tip_d - 22, pipe, root, bend=220)
    return root


# ============================================================ FIRE EXTINGUISHER
# 1 kg dry-powder bottle, 80 mm across and about 280 mm tall plus the head.
# There is no maker-supplied ladder mount for a JB74 -- the owner's car wears
# a pair of band clamps on the ladder rail, which is what this draws. The two
# guard positions strap to the MOLLE panel instead.
def extinguisher(where):
    """1 kg bottle in a two-band quick-release. Black body with a red label,
    which is what the owner's car carries -- a fire-engine-red bottle was
    wrong. On the ladder it sits BETWEEN the rails on the rear face, the way
    it is actually strapped, not hung off the outside of the hoop."""
    root = group(f'extinguisher_{where}')
    body = material('ExtinguisherBlack', 0x17181a, rough=0.42)
    red = material('ExtinguisherLabel', 0xb2211c, rough=0.5)
    if where == 'ladder':
        s = RIGHT
        x, y, z = s * 482, 1030, TAIL_Z - 62 - 54            # centred in the hoop, proud of the rungs
    else:
        s = RIGHT if where == 'right' else -RIGHT
        q = QUARTER
        x = s * 716 + s * 54
        y = (q['y0'] + q['y1']) / 2 + 10
        z = (q['z0'] + q['z1']) / 2 + 215
    lib.cylinder('bottle', (x, y, z), (0, 1, 0), 82, 270, body, root, n=22)
    flatten(lib.sphere('domeTop', (x, y + 135, z), 82, body, root), (x, y + 135, z), 0.45)
    flatten(lib.sphere('domeBase', (x, y - 135, z), 82, body, root), (x, y - 135, z), 0.35)
    # the owner's bottle is black with a big red maker's logo low down and a
    # white instruction panel above it
    box('label', (x, y - 46, z - 32), (76, 128, 20), red, root, bevel=5)
    box('labelText', (x, y + 74, z - 32), (72, 44, 18), material('LabelWhite', 0xf0f0ec, rough=0.6), root, bevel=4)
    lib.cylinder('neck', (x, y + 168, z), (0, 1, 0), 34, 70, STEEL, root, n=14)
    box('head', (x, y + 212, z), (56, 40, 76), BLACK, root, bevel=6)
    box('lever', (x, y + 238, z + 6), (40, 12, 96), STEEL, root, bevel=3)
    lib.cylinder('gauge', (x, y + 206, z - 46), (0, 0, 1), 44, 18, STEEL, root, n=14)
    tube('hose', [(x + s * 24, y + 200, z - 30), (x + s * 46, y + 110, z - 44),
                  (x + s * 26, y + 10, z - 40)], 16, RUBBER, root, bend=34)
    for yy in (y - 92, y + 92):                              # two band clamps round the bottle
        lib.cylinder(f'band{yy}', (x, yy, z), (0, 1, 0), 96, 26, BLACK, root, n=22)
        box(f'bandFoot{yy}', (x, yy, z + 46), (44, 30, 40), BLACK, root, bevel=3)
    return root




# ============================================================ URNIETA SALADO
# docs/urnieta-salado.json. Every dimension here is measured off URNIETA's own
# scale drawings (UN-JIMNY-FB-010/012/013), not estimated from photographs.
def ladder_urnieta():
    """SALADO rear ladder (0702026), drawing UN-JIMNY-FB-013: 1015 x 390 over
    the accessory post, a closed loop of 34 mm tube with four 28 mm rungs at
    158/378/603/862 above its foot.

    Redrawn 2026-09-22. The first attempt built the two rails, the top bow and
    the foot bow as four separate pieces and ran the accessory post the whole
    height of the ladder: above the S-bend the frame steps 91 mm inboard and
    the post did not, so it crossed the rail and floated. It is one continuous
    loop per side now, the bend is short enough to read as a step rather than
    a lean, and the post is bracketed to the lower section where the drawing's
    390 mm width comes from."""
    root = group('ladder_urnieta')
    s = RIGHT
    zf = TAIL_Z - 58
    y0 = 545                                                 # foot of the ladder
    y1 = y0 + 1015
    half = 254 / 2
    xlo, xup = s * 560, s * (560 - 91)                       # lower run outboard, upper run inboard
    yb0, yb1 = y0 + 640, y0 + 800                            # the S-bend, kept short

    # one closed loop: up one side, over the top, down the other
    def side(k):
        return [(xlo + k * s * half, y0 + 40, zf), (xlo + k * s * half, yb0, zf),
                (xup + k * s * half, yb1, zf), (xup + k * s * half, y1 - 40, zf)]
    loop = ([(xlo - s * half, y0 + 90, zf)] + side(-1)[1:] +
            [(xup - s * half, y1, zf), (xup + s * half, y1, zf)] +
            list(reversed(side(1))) + [(xlo + s * half, y0, zf), (xlo - s * half, y0, zf),
                                       (xlo - s * half, y0 + 90, zf)])
    tube('loop', loop, 34, BLACK, root, bend=58)
    for k, dy in enumerate((158, 378, 603, 862)):
        xc = xlo if dy < 620 else xup
        tube(f'rung{k}', [(xc - s * half, y0 + dy, zf), (xc + s * half, y0 + dy, zf)], 28, BLACK, root)
    box('gripPad', (xlo, y0 + 158, zf - 16), (188, 34, 22), RUBBER, root, bevel=6)

    # accessory post: outboard of the LOWER section only, which is where the
    # drawing's 390 mm overall width comes from. Flag socket on top.
    xp = xlo + s * (half + 34)
    lib.cylinder('post', (xp, y0 + 400, zf), (0, 1, 0), 30, 520, BLACK, root, n=14)
    for dy in (y0 + 180, y0 + 600):
        box(f'postArm{dy}', (xlo + s * (half + 17), dy, zf), (40, 26, 26), BLACK, root, bevel=3)
    lib.cylinder('flagSocket', (xp, y0 + 690, zf), (0, 1, 0), 38, 80, STEEL, root, n=14)
    lib.cylinder('aerial', (xp, y0 + 900, zf), (0, 1, 0), 10, 340, STEEL, root, n=8)

    # the top wraps forward over the tailgate's upper edge; the bottom clamps
    # the lower hinge. Neither reaches the roof.
    for k in (-1, 1):
        tube(f'hook{k}', [(xup + k * s * half, y1 - 6, zf), (xup + k * s * half, y1 + 18, zf + 34),
                          (xup + k * s * half, y1 + 6, zf + 78)], 30, BLACK, root, bend=22)
        box(f'foot{k}', (xlo + k * s * half, y0 + 60, (TAIL_Z + zf) / 2), (56, 110, abs(TAIL_Z - zf)), BLACK, root, bevel=4)
        box(f'plate{k}', (xlo + k * s * half, y0 + 60, TAIL_Z - 8), (76, 130, 10), BLACK, root, bevel=4)
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
    for st in ('stock', 'steel', 'six', 'eight', 'ten', 'beadlock', 'moon', 'daytona', 'slot5', 'watanabe', 'eightpin',
               'renkon', 'arc4', 'dwindow', 'turbine'):
        rim(st)
    roof_rack_arb()
    roof_lights()
    bumper_tube_heritage()
    rear_bumper_tube()
    ladder_tube()
    ladder_jst()
    for sd in (RIGHT, -RIGHT):
        guard_can(sd)
        guard_axe(sd)
        guard_board(sd)
    shovel()
    # lighting (docs/jb74-lighting.json)
    light_bar_gen('stedi_st3k', 1300, 51, 55, 50, lens_mat=AMBER)
    light_bar_gen('stedi_st4k', 1320, 110, 105, 100, rows=2, lens_mat=AMBER)
    light_bar_gen('stedi_st1k', 546, 38, 80, 20, lens_mat=STEDI_YELLOW)
    light_bar_gen('stedi_st2k', 1016, 60, 70, 16, lens_mat=AMBER)
    roof_lights_kc()
    for gl in ('rally', 'lower', 'bushranger'):
        grille_light(gl)
    # exhausts (docs/jb74-exhaust.json)
    exhaust('stock', tip_d=48, protrude=0, muffler=(360, 120), muffler_z=-1240)
    exhaust('tw_tip', layout='cover', tip_d=76, protrude=60, roll=True)
    exhaust('fujitsubo_ak', tip_d=70, tip_y=330, protrude=35, muffler=(350, 120))
    exhaust('monster_sp_x', tip_d=76, tip_y=330, protrude=45, muffler=(400, 100), roll=True)
    exhaust('jaos_zs', tip_d=101, tip_y=330, protrude=40, muffler=(400, 130), roll=True)
    exhaust('kakimoto_kr_lr', layout='corner', tip_d=96, tip_y=345, protrude=30, muffler=(420, 150))
    exhaust('apio_yoshimura_ti', tip_d=68, tip_y=333, protrude=30, tip_mat=TI_BLUE,
            muffler=(550, 115), muffler_z=-1560, roll=True)
    exhaust('taniguchi_compe_r', layout='through', tip_d=75, tip_mat=TI_BLUE)
    exhaust('hks_trailmaster', layout='side', tip_d=75, tips=2, tip_y=300, tip_mat=TI_BLUE,
            muffler=(450, 100))
    # HKS LEGAL K-1: right side, straight out the back under the bumper, one
    # 74.7 tip. The drum is small (4.0 kg) and sits up over the rear axle, so
    # from the side the tip is all you see.
    exhaust('hks_legal', tip_d=75, tip_y=325, protrude=45, muffler=(250, 150),
            muffler_z=-1060, muffler_dy=150, roll=True)
    exhaust('hks_legal_ti', tip_d=75, tip_y=325, protrude=45, tip_mat=TI_BLUE,
            muffler=(250, 150), muffler_z=-1060, muffler_dy=150, roll=True)
    exhaust('urnieta_salado', layout='quad', tip_d=80, tip_y=330, protrude=40,
            muffler=(500, 150), muffler_z=-1180, roll=True)
    for wh in ('ladder', 'left', 'right'):
        extinguisher(wh)
    # URNIETA SALADO (docs/urnieta-salado.json)
    ladder_urnieta()
    # 1890 x 1366 is dimensioned on drawing UN-JIMNY-FB-012; it overhangs this
    # model's 1825 mm roof slightly at both ends, which is what the fitted
    # photos show. The half-roof SKU is not dimensioned anywhere -- 1100 is a
    # guess from the product photos and is flagged as such in parts.js.
    rack_platform('urnieta_salado', 1366, 1890, slat_dir='across', slats=7, rail=(52, 48), legs=6, deflector=True)
    rack_platform('urnieta_salado_half', 1366, 1100, slat_dir='across', slats=5, rail=(52, 48), legs=4, deflector=True)
    flares()
    decals()
    side_skirt()
    snorkel_bravo()
    snorkel_ironman()
    snorkel_urnieta()
    snorkel_urnieta(head='ram')
    snorkel_precleaner()
    snorkel_sleek()
    mirrors_urnieta()
    mirrors_damd()
    pillar_pods()
    pillar_pods(sides=(-RIGHT,), suffix='_left')
    # catalogue variants (dimensions from parts.js research; see notes there)
    # roof racks (research 2026-09-16: ARB/Yakima TW, Front Runner, Rhino, JAOS, IPF, APIO, SHOWA, TW generic)
    rack_platform('yakima', 1370, 1520, slat_dir='across', slats=6, legs=4, deflector=False, round_bars=True)
    rack_platform('fr34', 1345, 1156, slat_dir='across', slats=6, legs=4, deflector=True)
    rack_platform('pioneer', 1339, 1453, slat_dir='along', slats=4, rail=(56, 52), legs=4, deflector=False, mesh=True)
    rack_platform('jaos', 1250, 1400, slat_dir='across', slats=6, rail=(32, 32), legs=6, deflector=False, hoop=96)
    rack_platform('ipf', 1250, 1400, slat_dir='across', slats=7, rail=(40, 39), legs=4, deflector=False, hoop=140)
    rack_platform('apio', 1270, 1420, slat_dir='across', slats=4, rail=(28, 60), legs=6, deflector=True, mesh=True)
    rack_platform('showa_foot', 1250, 1500, slat_dir='across', slats=12, rail=(40, 40), legs=6, deflector=False)
    rack_wood('half')
    rack_wood('full')
    rack_platform('tw_generic', 1260, 1600, slat_dir='across', slats=7, legs=6, deflector=True, hoop=70)
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
    front_bar('beyond_liberte', 'plate', W=1400, H=230, D=150, fog_stalk=True, bash=True, skid=False)
    front_bar('maverick', 'short', W=1300, H=200, D=140, y=540, fogs=True, skid=False)
    front_bar('mrk_abs', 'abs', W=1520, H=250, D=170, y=540, skid=False, corners=False, hump=True, bash=True, mesh_off=RIGHT * 330, fogs=True)
    front_bar('wmd_winch', 'short', W=1100, H=230, D=170, y=560, hoop=True, winch=True)
    front_bar('jaos_cowl', 'abs', W=1470, H=280, D=180, y=540, skid=False, corners=False, hump=True, bash=True, badge='JAOS', mesh_off=0)
    front_bar('taniguchi_square', 'box', W=1400, y=600, skid=False)
    front_bar('taniguchi_double', 'double', W=1400, y=590, tube_d=48, skid=False)
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
    rear_bar('damd_roots_rear', 'plate', W=1230, H=150, D=120, y=520, lamps='round', mat=IVORY)
    # rear bumpers
    rear_bar('klc_heritage_rear', 'tube', W=1380, tube_d=76, y=648, lamps='klc')
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
    grille_urnieta_salado()
    side_bar_urnieta_salado()
    hood_urnieta_salado()
    hood_urnieta_1970()
    spare_urnieta_salado()
    spare_urnieta_1970()
    gullwing_urnieta_1970()
    side_skirt_urnieta_1970()
    grille_urnieta_1970()
    bumper_urnieta_salado()
    rear_urnieta_salado()
    bumper_urnieta_1970()
    rear_urnieta_1970()
    grille_generic('mrk_angry', v_slots=7, bezel='square', wire=False)
    grille_generic('apio_sj', v_slots=9, mat=GUNMETAL)
    grille_generic('apio_marker', h_slats=4, marker=4)
    grille_generic('taniguchi_washer', wire=True)
    grille_generic('kpro_folksy', h_slats=6, mat=material('WhiteGel', 0xeeeee8, rough=0.35), wire=False)
    grille_generic('prostaff_minig', v_slots=9, bezel='square')
    grille_generic('sixsense_explosion', h_slats=7, slat_h=12, label='SUZUKI', bezel='square', mat=PAINT)
    # Two files, because they are needed at different moments: the car cannot
    # be drawn at all without its wheels, but nothing needs an awning until
    # somebody picks one. Splitting them takes about 1.5 MB off what has to
    # arrive before the first frame.
    roots = [o for o in bpy.data.objects if o.parent is None and o.type == 'EMPTY']
    rims = [o for o in roots if o.name.startswith('rim_')]
    rest = [o for o in roots if not o.name.startswith('rim_')]
    lib.export(os.path.abspath(RIMS_OUT), only=rims)
    lib.export(os.path.abspath(OUT), only=rest)
    print(f'exported {len(rims)} rims and {len(rest)} parts')


build()
print('exported', os.path.abspath(OUT))
