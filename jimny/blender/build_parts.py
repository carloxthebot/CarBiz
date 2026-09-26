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
from lib import P, box, tube, sweep, group, material, rounded_rect, circle, fillet, annulus, sphere, text, cut, lathe, prism, slab  # noqa: E402
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
    if variant == 'basket':
        return rack_basket()
    # Front Runner Slimline II: thin tray, low T-slot rail with moulded
    # corner caps, hat-section slats flush with it, six tapered legs, one
    # curved deflector.
    return rack_frame('platform', 1345, 1560, rail=(30, 50), slats=14, slat_w=62, slat_h=18, flutes=1,
                      legs=6, deflector=True)


def rack_basket():
    """SHOWA GARAGE A-x Half Rack M (E20008), 1400 x 1250, about 130 tall
    folded, 11.4 kg: a wrinkle-black tube basket -- a rounded top hoop tied
    to the floor frame by hairpin uprights, rods fore-aft on the floor, a
    curved textured panel wrapping the front, four bracket feet (maker's
    photos, 2026-09-26)."""
    root = group('roofRack_basket')
    W, L = 1250, 1400
    top = RACK_TOP
    zc = RACK_ZC
    z0, z1 = zc - L / 2, zc + L / 2
    yf, yh = top - 12, top + 108                           # floor frame, top hoop
    fx, hx = W / 2 - 20, W / 2 - 38
    hsweep('frame', rect_loop(fx, z0 + 20, z1 - 20, yf, 130, 6), circle(13, 10), TEXBLACK, root, closed=True, crisp=False)
    hsweep('hoop', rect_loop(hx, z0 + 38, z1 - 38, yh, 150, 6), circle(13, 10), TEXBLACK, root, closed=True, crisp=False)
    n = 13
    for i in range(n):                                     # floor rods, fore-aft
        x = -fx + 50 + i * (2 * fx - 100) / (n - 1)
        lib.cylinder(f'rod{i}', (x, yf + 2, zc), (0, 0, 1), 12, L - 60, TEXBLACK, root, n=8)
    for k in range(4):                                     # cross rods under them
        z = z0 + 90 + k * (L - 180) / 3
        lib.cylinder(f'cross{k}', (0, yf - 10, z), (1, 0, 0), 18, 2 * fx, TEXBLACK, root, n=10)
    for s in (-1, 1):                                      # hairpin uprights down the sides
        for k in range(7):
            z = z0 + 150 + k * (L - 300) / 6
            tube(f'up{s}{k}', [(s * fx, yf, z), (s * fx, yf + 40, z), (s * hx, yh, z)], 14, TEXBLACK, root, bend=40)
    for k in range(5):                                     # and across the rear
        x = -hx + 160 + k * (2 * hx - 320) / 4
        tube(f'upr{k}', [(x, yf, z0 + 20), (x, yf + 40, z0 + 20), (x, yh, z0 + 38)], 14, TEXBLACK, root, bend=40)
    # the curved textured wind panel wrapping the front
    arc = bezier2((yf - 6, z1 - 14), (yf + 30, z1 + 26), (yh + 4, z1 - 34), 10)
    curved_strip('frontPanel', -(hx - 90), hx - 90, arc, 4, TEXBLACK, root)
    for s in (-1, 1):                                      # panel ends wrap round the corners
        for f in range(3):
            q = arc[3 + f * 3]
            lib.cylinder(f'panelRib{s}{f}', (s * (hx - 60), q[0], q[1]), (1, 0, 0), 10, 60, TEXBLACK, root, n=8)
    for s in (-1, 1):                                      # four bracket feet
        for k in (-1, 1):
            gutter_leg(root, f'leg{s}{k}', s, zc + k * (L / 2 - 260), fx, yf - 10, 'tower', 56)
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
    n = 6                                                    # horizontal slats across the opening (OUTCLASS's photos)
    for k in range(n):
        y = 858 - oh / 2 + 22 + k * (oh - 44) / (n - 1)
        box(f'slat{k}', (0, y, face_z(0) + 2), (ow - 14, 16, 22), TEXBLACK, root, bevel=3)
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
    for k in range(8):                                       # eight slots (KLC's photos), not seven
        x = -245 + k * 70
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
    # 1100 wide and tucked right behind the bar (whose back stays ahead of
    # 1545): at z 1500 it sat inside a 225/75R16's leading edge (1511) and
    # a steered tyre brushed its ends
    box('valance', (0, 560, 1533), (1100, 280, 20), RUBBER, root, bevel=4)
    for s in (-1, 1):                                    # chassis-rail mounts
        box(f'mount{s}', (s * 330, 540, 1600), (70, 120, 200), TEXBLACK, root, bevel=4)
    # (There used to be a 300 mm 'corner' block either side here, meant to
    # close the corner the stock bumper wrapped round. It sat at z 1490 --
    # exactly where the front tyre's leading edge is -- attached to nothing,
    # and read as a slab floating in front of the wheel. Short bumpers leave
    # that corner open on the real cars; so does this.)


def fog_lamp(root, x, y, z, mat, dia=90):
    lib.cylinder(f'fogHsg{x}', (x, y, z - 30), (0, 0, 1), dia + 14, 70, mat, root)
    lib.cylinder(f'fogBowl{x}', (x, y, z), (0, 0, 1), dia - 6, 6, CHROME, root)
    lib.cylinder(f'fogLens{x}', (x, y, z + 6), (0, 0, 1), dia, 4, LENS, root)


def number_plate(root, y, z, x=0):
    box('plate', (x, y, z), (330, 165, 2), PLATE, root, bevel=1)


def bumper_klc():
    """KLC Heritage Traditional Bumper 74 in ivory (the black one is
    bumper_tube_heritage): the colour is the product, not the car's paint.
    KLC publish no sizes; off their product shots with the 330 x 165 plate
    as the ruler (+-40 mm): a 60 mm upper tube 1380 across at y 637, a 55 mm
    lower tube 800 across 100 below it, round 88 mm fogs in flat plate boxes
    at +-400 whose brackets drop to a 710 mm skid, and the plate on tabs
    with its top level with the upper tube's top."""
    root = group('frontBumper_klc_trad')
    PAINT = material('KlcIvory', 0xe6dfcd, rough=0.5, metal=0.1)
    yu, yl, zu, zl = 637, 537, 1702, 1684
    tube('upper', [(-690, yu, zu), (690, yu, zu)], 60, PAINT, root)
    tube('lower', [(-400, yl, zl), (400, yl, zl)], 55, PAINT, root)
    for s in (-1, 1):
        lib.cylinder(f'cap{s}', (s * 691, yu, zu), (1, 0, 0), 60, 4, PAINT, root, n=24)
        tube(f'link{s}', [(s * 250, yl, zl), (s * 250, yu, zu)], 30, PAINT, root)
        box(f'fogBox{s}', (s * 400, yl, zl - 6), (104, 104, 80), PAINT, root, bevel=4)
        fog_lamp(root, s * 400, yl, zl + 40, PAINT, dia=88)
        # flat bracket from the fog box down to the skid (not a round tube)
        box(f'bracket{s}', (s * 400, (yl - 52 + 420) / 2, zl - 20), (10, yl - 52 - 420, 70), PAINT, root, bevel=1)
        box(f'plateTab{s}', (s * 110, 610, zu + 26), (24, 70, 10), PAINT, root, bevel=1)
    number_plate(root, yu + 30 - 82.5, zu + 33)
    box('skid', (0, 400, 1640), (710, 4, 240), TEXBLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-30), 3, 'X'))
    valance(root)
    return root


# OUTCLASS TYPE2 winch bumper (outclass.ocnk.net 1095; no dimensions or
# weight published): see the builder's docstring.
def bumper_outclass():
    """OUTCLASS TYPE2 winch bar, folded steel. Off three near-straight-on
    product photos with the headlamp centres (920 apart, ~3.3 mm/px) as the
    ruler: 1450 across, 200 tall (y 500-700, its top ~50 under the grille)
    and 200 deep, the outer ~120 of each end chamfered back 45 deg, the
    fairlead on the face centre, four ~100 mm square LED pods at +-370 and
    +-575, the plate hung below the bar in front of the winch bay, shackle
    tabs and a slotted skid apron at 45 deg."""
    root = group('frontBumper_outclass_t2')
    W, top, H = 1450, 700, 200
    st = front_stations(W, top, H, 200, cham=120, zf=1750)
    xloft('body', st, TEXBLACK, root, r=10)
    zf = at_x(st, 0, 4)
    box('fairleadFrame', (0, 620, zf + 6), (300, 100, 14), RED, root, bevel=3)
    box('fairleadSlot', (0, 620, zf + 14), (240, 56, 4), RUBBER, root, bevel=0)
    for x in (-575, -370, 370, 575):
        z = at_x(st, x, 4)
        box(f'pod{x}', (x, 610, z + 6), (100, 100, 12), BLACK, root, bevel=2)
        box(f'podLens{x}', (x, 610, z + 13), (82, 82, 2), LENS, root, bevel=0)
    hung_plate(root, 0, 470, zf + 4, top - H, TEXBLACK)
    for s in (-1, 1):
        box(f'tab{s}', (s * 350, 470, zf - 30), (12, 110, 90), TEXBLACK, root, bevel=2)
        annulus(f'shackle{s}', (s * 350, 440, zf - 15), 12, 22, 24, STEEL, root, n=24)
    apron = box('apron', (0, 390, 1650), (720, 4, 300), TEXBLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-45), 3, 'X'))
    for k in range(3):
        box(f'aslot{k}', (-150 + k * 150, 400, 1662), (90, 4, 24), RUBBER, root, bevel=0,
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
    dish = W / 2 - (24 if style in ('steel', 'daytona', 'moon', 'slot5', 'renkon', 'arc4', 'oz20') else 38)   # face plane, inset from the outer lip
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
    elif style == 'oz20':
        # OZ Racing Rally Racing (DAMD's 16x6J -5): twenty small rounded
        # trapezoid windows round the outer face, one every 18 degrees, about
        # 28 mm wide with 25 mm of disc between them; the rest is flat disc
        for k in range(20):
            a = 2 * math.pi * k / 20
            c = box(f'win{k}', (dish, 0.84 * R * math.sin(a), 0.84 * R * math.cos(a)), (60, 30, 44), RIM_FACE, None,
                    bevel=9, rot=Matrix.Rotation(-a, 3, 'X'))
            c.modifiers['bevel'].segments = 3
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
        n, spoke = {'stock': (5, 0.36), 'six': (6, 0.24), 'seven': (7, 0.30), 'eight': (8, 0.22), 'ten': (10, 0.17),
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
    """ARB BASE Rack (1770020), 1545 x 1285: wide flat slats across the car
    with narrow gaps, flush with a dovetail-grooved perimeter that runs round
    large cast corners (two bolts each), four tower legs, BASE RACK on the
    rear rail (maker's photos, 2026-09-26)."""
    root = rack_frame('arb', ARB_W, ARB_L, rail=(44, 45), rail_kind='dovetail', R=90, castings=True, slats=15,
                      slat_w=78, slat_h=16, flutes=2, legs=4, deflector=False)
    z0 = RACK_ZC - ARB_L / 2
    lbl = text('arbLabel', 'BASE RACK', (0, RACK_TOP - 22, z0 - 1), 22, 1, material('LabelWhite', 0xf0f0ec, rough=0.6), root)
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
    """KLC Traditional Bumper 74 in black with KC FLEX ERA 4 pods, from the
    owner's close-ups and KLC's product shots (klc-div.com
    traditionalbumperfront_2_bk; 330 x 165 plate as the ruler): a straight
    60 mm upper tube 1380 across with flat ends, a 55 mm lower tube 800
    across set back 100 below it with the square KC pods on its ends at
    +-400, the plate on two tabs with its top level with the upper tube's
    top (it hides the tube's middle), a flat 'Heritage' panel about 720
    wide below, and the silver crossmember visible between the tubes. (If
    the owner's car turns out to wear 76 mm tubes, the car wins.)"""
    root = group('frontBumper_tube_heritage')
    yu, zu = 640, 1700                                       # upper tube
    yl, zl = 540, 1666                                       # lower tube, set back
    tube('upper', [(-690, yu, zu), (690, yu, zu)], 60, TEXBLACK, root)
    tube('lower', [(-400, yl, zl), (400, yl, zl)], 55, TEXBLACK, root)
    amber = material('AmberLens', 0xe08a1e, rough=0.15, metal=0.0)
    kcred = material('KCRed', 0xa8231c, rough=0.45)
    for s in (-1, 1):
        lib.cylinder(f'capU{s}', (s * 691, yu, zu), (1, 0, 0), 62, 5, TEXBLACK, root, n=28)
        # plate tabs down the front of the upper tube, bolt heads on top
        box(f'tab{s}', (s * 120, yu - 40, zu + 30), (28, 90, 6), TEXBLACK, root, bevel=1)
        lib.cylinder(f'tabBolt{s}', (s * 120, yu + 32, zu), (0, 1, 0), 14, 8, STEEL, root, n=6)
        # KC FLEX ERA 4: square pod with a red bezel, two spots over two floods
        px, py, pz = s * 400, yl, zl + 20
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
        # chassis legs
        box(f'leg{s}', (s * 330, yu - 70, zu - 150), (60, 170, 180), TEXBLACK, root, bevel=3)
    box('plate', (0, yu + 30 - 82.5, zu + 35), (330, 165, 3), PLATE, root, bevel=1)   # top level with the tube's top
    # Heritage panel: flat plate hanging below the lower tube, slightly
    # raked, 720 wide; the laser-cut script sits low and left of centre
    panel = prism('panel', [(yl - 40, zl - 26), (yl - 210, zl - 60), (yl - 210, zl - 68), (yl - 40, zl - 34)], -360, 360, TEXBLACK, root)
    script = text('heritage', 'Heritage', (-80, yl - 150, zl - 52), 132, 70, TEXBLACK, None,
                  font='/System/Library/Fonts/Supplemental/Zapfino.ttf' if os.path.exists('/System/Library/Fonts/Supplemental/Zapfino.ttf') else None)
    cut(panel, [script])                                     # laser-cut script, open right through
    # what shows between the tubes: the galvanised crossmember and the bay
    box('crossmember', (0, 590, 1600), (1100, 60, 40), STEEL, root, bevel=4)
    box('bay', (0, 540, 1420), (860, 320, 20), RUBBER, root, bevel=4)      # inside the tyres' steering sweep
    return root


def rear_bumper_tube():
    """Owner's rear bumper: one fat straight tube low across the back with
    squared end caps, plate wings above it carrying the stock tail lamps,
    exhaust tip out the right, tow hook and shackle underneath, mesh corner
    covers where the stock bumper used to wrap round. The tube ends at
    +-718, in line with the lamp wings' outer edge, so its caps stay inside
    the flares' corners."""
    root = group('rearBumper_tube')
    y, z = 430, -1650
    tube('bar', [(-718, y, z), (718, y, z)], 76, TEXBLACK, root)
    for s in (-1, 1):
        box(f'endCap{s}', (s * 725, y, z), (14, 96, 96), TEXBLACK, root, bevel=3)
        box(f'mount{s}', (s * 330, y + 30, z + 110), (70, 100, 220), TEXBLACK, root, bevel=4)
        # wing plate behind the tail lamp, lamp framed on it
        box(f'wing{s}', (s * 513, 545, -1568), (400, 250, 8), TEXBLACK, root, bevel=3)
        box(f'wingTop{s}', (s * 513, 665, -1575), (400, 8, 30), TEXBLACK, root, bevel=2)
        for (cx, cy, sx, sy) in ((0, 76, 370, 12), (0, -76, 370, 12), (-180, 0, 12, 160), (180, 0, 12, 160)):
            box(f'lampFrame{s}{cx}{cy}', (s * 513 + cx, 518 + cy, -1596), (sx, sy, 20), TEXBLACK, root, bevel=2)
        # corner cover with a hex-mesh vent
        box(f'corner{s}', (s * 740, 520, -1545), (50, 240, 150), TEXBLACK, root, bevel=6,   # clear of a 31in tyre's back (-1440)

            rot=Matrix.Rotation(math.radians(-s * 25), 3, 'Z'))
    box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)
    box('plate', (0, 585, TAIL_Z - 6), (330, 165, 4), PLATE, root, bevel=1)
    # (no tail pipe here: the exhaust family draws it, and a second one used
    # to poke out through the bumper)
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


# ============================================================== SIDE STRIPES
# The thing that actually makes one built Jimny look unlike another is its
# side stripe, and the car has a flat painted flank between the arches to put
# one on: probed at y 750 the surface runs |x| 700-708 from z -600 to +700,
# and outboard of that the arch flares stand proud at 720-790, so a stripe set
# at |x| 710 disappears behind them exactly the way it does on the real car.
# Every stripe on this car is quoted against the flank rather than the
# ground, because that is how the reference measures them: the belt line is
# 0%, the bottom of the door is 100%, and they are 667 mm apart. Probed at
# y 750 the flank runs |x| 700-708 from z -600 to +700, with the arch flares
# standing proud at 720-790 outboard of it, so a band set at |x| 710 runs out
# under both arches the way the real one does.
#
# Across 26 documented treatments the vertical position falls into only three
# slots -- tucked under the belt (10-25%), across the door handle (20-66%),
# and down on the lower door crease (65-90%) -- so the cheapest way to make
# five styles read apart at a glance is to put each in a different one.
BELT_Y, FLANK = 1090, 667
STRIPE_X = 710
STRIPE_Z0, STRIPE_Z1 = -1020, 850   # it runs out under both arches
py = lambda pct: BELT_Y - FLANK * pct / 100


def stripe_bands(name, bands, p_top, z0=STRIPE_Z0, z1=STRIPE_Z1):
    """A stack of horizontal bands down each flank. `bands` is a list of
    (height as a percentage of the flank, hex or None for a gap that shows
    body colour), read top to bottom, starting `p_top` below the belt."""
    root = group('stripe_' + name)
    fa, ra = CAR['anchors']['frontAxleZ'], CAR['anchors']['rearAxleZ']

    def span(ylo):
        # A band low enough to cross a wheel opening stops at its edge: the
        # opening is about 430 mm round the axle (y 346), and past it there
        # is no panel to stick to -- the low bands used to run straight
        # across the rear tyre. Higher bands keep running behind the flares.
        a, b = z0, z1
        if ylo < 346 + 430:
            dz = math.sqrt(max(0.0, 430 ** 2 - (ylo - 346) ** 2)) + 15
            a, b = max(a, ra + dz), min(b, fa - dz)
        return a, b
    for s in (-1, 1):
        cut = p_top
        for i, (h, col) in enumerate(bands):
            if col is not None:
                mat = material(f'Stripe{name}{i}', col, rough=0.5, metal=0.05)
                a, b = span(py(cut + h))
                box(f'b{s}{i}', (s * STRIPE_X, (py(cut) + py(cut + h)) / 2, (a + b) / 2),
                    (6, py(cut) - py(cut + h), b - a), mat, root, bevel=0)
            cut += h
    return root


def star_prism(name, yc, zc, R, mat, root, x0=707, x1=712):
    """A five-point star lying on the flank. Built as a pentagon plus five
    point triangles rather than one ten-vertex outline, because that outline
    is concave and an n-gon face made from it triangulates through itself."""
    r = R * 0.381966
    pt = lambda rad, t: (yc + rad * math.cos(t), zc + rad * math.sin(t))
    outer = [pt(R, k * 2 * math.pi / 5) for k in range(5)]
    inner = [pt(r, math.pi / 5 + k * 2 * math.pi / 5) for k in range(5)]
    prism(f'{name}Core', inner, x0, x1, mat, root)
    for k in range(5):
        prism(f'{name}P{k}', [inner[k - 1], outer[k], inner[k]], x0, x1, mat, root)


def stripe_stencil():
    """Military-truck markings: stencilled white lettering, instead of a
    camouflage field. (It carried a white door star until the owner asked
    for it to go.)

    A camouflage decal has to argue with the paint underneath it and loses --
    on a green car it turns into a smudge at any distance, and the pattern is
    the one thing about it people recognise. White stencil marks do the
    opposite: they are the highest-contrast thing on the car and they read at
    a glance, which is how the look works on the real vehicles. The markings
    are generic -- a plain star and a serial -- rather than any actual armed
    force's insignia, which is also what the sticker sets you can buy carry.

    Probed: the door skin is painted from y 620 to 1020 across z -680 to
    +760, sitting at |x| 700-710, so a 400 mm star at (830, 250) clears the
    belt line, the flares and the door handle."""
    root = group('stripe_stencil')
    white = material('StencilWhite', 0xe7e4da, rough=0.8, metal=0.0)
    FONT = '/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf'
    # no star: the owner asked for it off (2026-09-25); the stencils stay,
    # and there are more of them. Generic markings in the military-vehicle
    # manner -- a bonnet serial, a vehicle data block on each door, tyre
    # pressure over the rear arch -- not any real unit's codes.
    ob = text('bonnetNo', 'JB 74-0419', (0, 1112, 1230), 78, 2, white, root, font=FONT)
    ob.rotation_euler = (math.radians(-90 - 4), 0, 0)      # flat on the bonnet, read from the front
    ob.location = P(0, 1112, 1230)
    for s in (-1, 1):
        # door skin is at |x| 707-709 from y 750 up (sampled at z -100); the
        # rear quarter above the arch is at |x| 697 at y 950 (z -1000)
        for i, (line, size, y, z, x) in enumerate((('MAX SPEED 90 KM/H', 30, 800, -120, 710),
                                                   ('WT 1090 KG', 30, 765, -120, 709),
                                                   ('TIRE 2.0 BAR', 30, 955, -1000, 699))):
            ob = text(f'data{s}{i}', line, (s * x, y, z), size, 2, white, root, font=FONT)
            ob.rotation_euler = (0, 0, math.radians(90 * s))
            ob.location = P(s * x, y, z)
    for s in (-1, 1):
        for i, (line, size, y, z) in enumerate((('JB-74-1970', 58, 690, -430),
                                                ('4x4', 74, 690, 640))):
            ob = text(f'mark{s}{i}', line, (s * 709, y, z), size, 3, white, root, font=FONT)
            ob.rotation_euler = (0, 0, math.radians(90 * s))
            ob.location = P(s * 709, y, z)
    return root


def stripe_retro3():
    """The stripe on nearly every sand-coloured JB74 in the Japanese feeds:
    a dark brown hairline over a wide rust band over a cream one, contiguous,
    sitting on the lower door crease."""
    return stripe_bands('retro3', [(1.5, 0x6b4423), (6.9, 0xb4703a), (2.7, 0xe0cba8)], 45.2)


def stripe_toolgear():
    """Suzuki's own ツールギア look: one deep black band pinned between the
    door's lower crease and the sill trim, with a silver hairline under it.
    The lowest and heaviest of the documented treatments, and the only one
    that deliberately leaves the whole upper door empty."""
    return stripe_bands('toolgear', [(30.8, 0x0b1315), (1.2, 0xc8ccd0)], 61)


def stripe_jaos():
    """JAOS's low twin line: a 78 mm band and a 14 mm hairline under it, with
    a 6 mm gap of body colour between, sitting lower than anything else --
    78% to 89% of the flank, below the door crease and barely above the sill.
    Drawn in the black of the two finishes JAOS offer, because the silver one
    disappears on the white car this style puts it on."""
    return stripe_bands('jaos', [(8.8, 0x393333), (0.9, None), (1.5, 0x393333)], 78)


def stripe_toy4():
    """Toy Factory's four-band set: a pale orange hairline, a graduated
    salmon-to-orange band, a solid orange band and a broad near-black one,
    crossing the door handle. The real set turns the front fender's corner on
    concentric radii; this draws the flank run, which is what reads from the
    side."""
    return stripe_bands('toy4', [(1.7, 0xf49873), (1.2, None), (5.8, 0xff8225),
                                 (1.7, None), (5.8, 0xfe7000), (1.7, None),
                                 (8.3, 0x1d2124)], 18)


# ================================================================ ROLL CAGE
def cage_wildgoose():
    """RV4 Wild Goose アウターロールケージ JM-2424, 203,500 tax incl, 25 kg.
    Main tube 38.1 x 2.3, centre crossbar 25.4 x 2.3. It mounts at the bonnet
    fixing points at the front -- which is why the side cowl and fender have
    to be cut -- and at eight points on the roof drip rail at the back.

    It is the one part in the catalogue that redraws the car's outline rather
    than hanging off it: the roof stops being a plain box and becomes a box
    inside a frame. Sized off the model: the roof crowns at y 1620 with the
    gutter at |x| 645 and runs z +170 to -1540, so the rails sit just outside
    and above that, at |x| 700 and y 1700."""
    root = group('cage_wildgoose')
    for s in (-1, 1):
        # one continuous rail: bonnet mount, up the A-pillar, over the roof,
        # down to the rear drip rail
        tube(f'rail{s}', [(s * 655, 1150, 700), (s * 690, 1420, 560), (s * 700, 1690, 330),
                          (s * 700, 1704, 60), (s * 700, 1704, -1480), (s * 686, 1600, -1616)],
             38, BLACK, root, bend=170)
        # the feet: one plate at the bonnet, four along the drip rail
        box(f'foot{s}', (s * 650, 1140, 700), (56, 12, 90), BLACK, root, bevel=3)
        for z in (-260, -740, -1180, -1560):
            box(f'drip{s}{abs(z)}', (s * 672, 1660, z), (34, 74, 52), BLACK, root, bevel=4)
            box(f'dripPad{s}{abs(z)}', (s * 656, 1622, z), (16, 12, 78), BLACK, root, bevel=2)
    # crossbars: the front hoop follows the rails over the windscreen header,
    # the rest lie flat across the roof
    tube('hoop', [(-700, 1690, 330), (-660, 1712, 250), (660, 1712, 250), (700, 1690, 330)],
         38, BLACK, root, bend=120)
    for z in (-420, -960, -1440):
        lib.cylinder(f'x{abs(z)}', (0, 1704, z), (1, 0, 0), 25, 1400, BLACK, root, n=16)
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
            # from 55 degrees up: below that, at the front arch, the rivets
            # sat on the stock bumper's corner, and with any other bumper they
            # hung in the air
            for t in range(9):
                deg = 55 + 95 * t / 8
                a = math.radians(deg)
                r = 470
                lib.cylinder(f'rivet{s}{kind}{t}', (s * (arch_half_w(kind, deg) - 3), 346 + r * math.sin(a), z + r * math.cos(a)),
                             (1, 0, 0), 15, 8, STEEL, root, n=6)
    return root


def widebody(pid, W, shape='box', mat=None, lip=None):
    """Over-fenders that go WIDER than the Sierra's own resin arches, laid over
    them. The shell is revolved round each axle but its inner face follows the
    measured arch (ARCH_HALF_W) angle by angle, so it sits on the stock flare
    all the way round instead of floating off it at the ends.

    `W` is the maker's added width per side where one is published (WALD +30,
    AERO OVER +35); the others publish none and parts.js says so. 'box' is
    the squared-off G-class section (WALD, KUHL, LB, AERO OVER), 'blister' the
    rounded rally bulge (DAMD little delta) that also swells up into the
    fender above the arch."""
    root = group(f'fender_{pid}')
    mat = mat or PAINT
    # The opening must not come in past the stock arch lip, which sits about
    # 430 mm from the axle (sampled at 30-150 degrees). These profiles were
    # drawn from 392, so on the lowered street car the lip landed on the
    # tyre; every radius below is pushed out by DR to start at the stock lip.
    DR = 38
    if shape == 'blister':
        # (r from the axle, x outward of the stock arch surface)
        prof = [(392, -36), (392, W - 6), (402, W), (440, W + 2), (488, W * 0.72), (526, W * 0.32), (552, -2), (544, -30)]
    else:
        prof = [(392, -36), (392, W - 2), (404, W + 2), (505, W + 3), (522, W - 4), (548, 6), (552, -4), (545, -30)]
    for s in (-1, 1):
        for kind, zc in (('front', CAR['anchors']['frontAxleZ']), ('rear', CAR['anchors']['rearAxleZ'])):
            bm = bmesh.new()
            rings = []
            steps = 40
            for i in range(steps + 1):
                deg = 12 + 156 * i / steps
                a = math.radians(deg)
                hw = arch_half_w(kind, min(165, max(15, deg))) - 4
                rings.append([bm.verts.new(P(s * (hw + dx), 346 + (r + DR) * math.sin(a), zc + (r + DR) * math.cos(a))) for (r, dx) in prof])
            k = len(prof)
            for r0, r1 in zip(rings, rings[1:]):
                for j in range(k):
                    bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            lib.new_object(f'{kind}{s}', bm, mat, root, smooth=True)
            if lip:                              # a black rubber edge trim along the opening
                prof2 = [(386, -30), (386, W + 1), (398, W + 1), (398, -30)]
                bm = bmesh.new()
                rings = []
                for i in range(steps + 1):
                    deg = 12 + 156 * i / steps
                    a = math.radians(deg)
                    hw = arch_half_w(kind, min(165, max(15, deg))) - 4
                    rings.append([bm.verts.new(P(s * (hw + dx), 346 + (r + DR) * math.sin(a), zc + (r + DR) * math.cos(a))) for (r, dx) in prof2])
                for r0, r1 in zip(rings, rings[1:]):
                    for j in range(4):
                        bm.faces.new((r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]))
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                lib.new_object(f'lip{kind}{s}', bm, lip, root, smooth=True)
    return root


# =================================================================== FACE SWAP
# The stock face, sampled off the model (blender/car.json, front raycast):
# the round headlamps centre at about x +-550, y 855; the grille panel and
# lamp surrounds sit at z 1615-1666 between y 750 and 960; the bonnet's
# leading edge is at y 1000, z 1600-1635; the stock bumper's face is at
# z 1740-1770 between y 400 and 650. A face kit hides all three (bumper,
# grille, headlamps -- see rig.js stockHeadlamps) and replaces them.
BRON_SILVER = material('BronSilver', 0xb4b8bb, rough=0.32, metal=0.65)
# clear outer lens: the chrome bowl and projectors have to read through it
LAMP_GLASS = material('LampGlass', 0xd8e0e6, rough=0.04, metal=0.0, alpha=0.25)


def _rrect(w, h, r, n=6):
    """Rounded rectangle as (x, y) points, centred on 0."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def face_bron55():
    """GARAGE ILL BRON55 (JB74W 1-4, LED-headlamp cars), the two-tone painted
    finish shown on the maker's demonstration car: grille frame and bumper
    beam in the body colour, centre module and lower edge silver.

    GARAGE ILL publish no drawings, so every size here is read off their own
    photographs against a 330 mm Japanese number plate and the 1645 mm arch
    width (docs/jb74-face-swap.json, +-10 %): grille 1330 x 220 with R40
    corners, lamps about 175 across at 1090 centres, set INTO the grille; a
    190 x 18 light bar through each lamp's centre; BRON55 lettering about
    600 wide on a black band at lamp-centre height; three rows of staggered
    48 x 20 capsule holes above the band and three below. Bumper about 1600
    wide and 375 tall starting 50 below the grille: a 65 mm body-colour beam
    with square ends, a 940 mm silver trapezoid module with two tow-hook
    recesses and a honeycomb intake, a silver lower edge with one crease and
    four notches, and a 300 x 85 black pocket at each outer end."""
    root = group('face_bron55')
    yc, zf = 860, 1672                      # grille centre height, grille face
    W, H, LX, LR = 1330, 220, 545, 88       # grille size, lamp centre x, lamp radius

    # grille frame: a ring round the honeycomb, with two round lamp openings
    frame = slab('frame', [(x, y + yc) for (x, y) in _rrect(W, H, 40)], zf - 62, zf, PAINT, root, smooth=False)
    cutters = [box('frameHole', (0, yc, zf - 20), (2 * (LX - LR) - 20, H - 44, 120), PAINT, None, bevel=0)]
    for s in (-1, 1):
        cutters.append(lib.cylinder(f'lampHole{s}', (s * LX, yc, zf), (0, 0, 1), 2 * LR + 8, 140, PAINT, None, n=40))
    cut(frame, cutters)
    # side returns carrying the amber corner markers, back to the fender
    for s in (-1, 1):
        box(f'return{s}', (s * (W / 2 - 14), yc, zf - 90), (28, H - 40, 120), PAINT, root, bevel=6)
        box(f'marker{s}', (s * (W / 2 + 1), yc, zf - 70), (4, 50, 12), AMBER, root, bevel=1)
    box('backing', (0, yc, zf - 70), (W - 60, H - 30, 10), RUBBER, root, bevel=0)

    # honeycomb plate: 3 staggered rows above the letter band, 3 below
    pw = 2 * (LX - LR) - 40
    plate = box('mesh', (0, yc, zf - 18), (pw, H - 44, 10), TEXBLACK, root, bevel=0)
    holes = []
    for row, y in enumerate((yc + 37, yc + 63, yc + 89, yc - 37, yc - 63, yc - 89)):
        off = 30 if row % 2 else 0
        for k in range(-7, 8):
            x = k * 60 + off
            if abs(x) + 30 > pw / 2 - 8:
                continue
            c = box(f'h{row}{k}', (x, y, zf - 18), (48, 20, 40), TEXBLACK, None, bevel=9.5)
            c.modifiers['bevel'].segments = 3
            holes.append(c)
    cut(plate, holes)

    # letter band at lamp-centre height, with three slits either side of the name
    box('band', (0, yc, zf - 8), (pw + 20, 40, 12), TEXBLACK, root, bevel=2)
    for s in (-1, 1):
        for k in range(3):
            box(f'slit{s}{k}', (s * (330 + k * 14), yc, zf - 1), (5, 28, 2), RUBBER, root, bevel=0)
    t = text('name', 'BRON55', (0, yc - 2, zf - 2), 44, 5, UNT_TEXT, root)
    t.scale = (2.35, 1.0, 1.0)             # super-extended face: ~600 mm for six characters

    # the lamps: chrome base, lens with a white halo ring, the bar through the centre
    for s in (-1, 1):
        x = s * LX
        lib.cylinder(f'bowl{s}', (x, yc, zf - 40), (0, 0, 1), 2 * LR, 50, CHROME_TRIM, root, n=40)
        annulus(f'halo{s}', (x, yc, zf - 12), LR - 16, LR - 6, 6, LENS, root)
        lib.cylinder(f'proj{s}a', (x, yc + 30, zf - 12), (0, 0, 1), 52, 8, CHROME, root, n=24)
        lib.cylinder(f'proj{s}b', (x, yc - 30, zf - 12), (0, 0, 1), 52, 8, CHROME, root, n=24)
        lib.cylinder(f'lens{s}', (x, yc, zf - 6), (0, 0, 1), 2 * LR - 4, 4, LAMP_GLASS, root, n=40)
        box(f'drl{s}', (x - s * 38, yc, zf + 2), (190, 18, 8), LENS, root, bevel=3)

    # ---- bumper
    top, bot = yc - H / 2 - 50, yc - H / 2 - 50 - 375       # 700 .. 325
    zb = 1790                                                 # beam face
    box('beam', (0, top - 32, zb - 70), (1600, 65, 140), PAINT, root, bevel=5)
    for s in (-1, 1):                                         # square ends wrapping back to the arch
        box(f'beamEnd{s}', (s * 776, top - 32, zb - 190), (48, 65, 250), PAINT, root, bevel=5)
    box('body', (0, (top - 65 + bot) / 2 + 20, zb - 120), (1560, top - 65 - bot - 40, 150), PAINT, root, bevel=5)
    # silver trapezoid module, proud of the beam
    mod = [(-470, top - 66), (470, top - 66), (420, bot + 86), (-420, bot + 86)]
    slab('module', mod, zb - 60, zb + 22, BRON_SILVER, root)
    for s in (-1, 1):
        box(f'hookPocket{s}', (s * 335, bot + 215, zb + 20), (90, 140, 10), TEXBLACK, root, bevel=4)
        tube(f'hook{s}', [(s * 335, bot + 245, zb + 24), (s * 335, bot + 245, zb + 60), (s * 335, bot + 190, zb + 60),
                          (s * 335, bot + 190, zb + 24)], 16, CHROME_TRIM, root, bend=20)
    box('intake', (0, bot + 230, zb + 22), (370, 95, 6), TEXBLACK, root, bevel=3)
    for k in range(-5, 6):                                    # the honeycomb, as a lattice of bars
        box(f'hc{k}', (k * 32, bot + 230, zb + 26), (4, 90, 4), BLACK, root, bevel=0)
    # silver lower edge with one crease and four notches
    box('lower', (0, bot + 43, zb - 40), (1480, 86, 120), BRON_SILVER, root, bevel=5)
    box('crease', (0, bot + 58, zb + 20), (1440, 3, 4), BLACK, root, bevel=0)
    for k in (-3, -1, 1, 3):
        box(f'notch{k}', (k * 150, bot + 18, zb + 20), (60, 22, 6), TEXBLACK, root, bevel=2)
    for s in (-1, 1):                                         # empty fog pockets at the outer ends
        box(f'pocket{s}', (s * 640, top - 130, zb - 44), (300, 85, 8), TEXBLACK, root, bevel=4)
    return root


# ================================================================ EURO RALLY
# DAMD little delta and the roof spoilers. Every size is read off the makers'
# own photographs (docs/jb74-rally-geometry.json: +-8 % for large shapes,
# +-15 % for small ones, +-25 % fore-aft); the DAMD demo car sits on 2-inch
# lowering springs, so its heights were put back to stock ride height.
DELTA_RED = material('DeltaRedEdge', 0xa3161a, rough=0.35)
KOITO_YELLOW = material('KoitoYellow', 0xe8b41c, rough=0.1)
STRIPE_CREAM = material('StripeCream', 0xe9e2cc, rough=0.5)
STRIPE_GREEN = material('StripeGreen', 0x1f3a2c, rough=0.5)
TAIL_RED = material('TailRed', 0xc0161a, rough=0.18)


def face_damd_delta():
    """DAMD little delta front: the four-round-lamp grille (173,800 yen) and
    the little 5./delta front bumper (92,400 yen) together. Four lamps in one
    row at lamp-centre height 855: an outer pair about 145 across at x +-575
    and a clearly smaller inner pair about 105 at x +-430. Between them a
    Lancia-style chrome frame about 730 x 160 -- a centre post opening into a
    V at the top -- over two openings with a red inner edge and black diamond
    mesh; the black grille panel behind is about 1340 x 180. Square clear LED
    indicator bars, 145 x 25, sit under the lamps at y 740. The bumper is all
    body colour, about 1480 across the face and 370 tall (y 340-710) at
    z 1740: top beam, a row of five slots, a rib, a recessed band carrying
    the plate and two square yellow Koito fogs (155 x 92 at x +-460, y 460),
    then a small lip."""
    root = group('face_damd_delta')
    yc, zf = 855, 1668
    box('panel', (0, yc, zf - 20), (1340, 180, 40), TEXBLACK, root, bevel=8)
    box('panelBack', (0, yc, zf - 60), (1300, 170, 30), RUBBER, root, bevel=0)
    for s in (-1, 1):
        for x, d in ((575, 145), (430, 105)):
            X = s * x
            lib.cylinder(f'bezel{s}{x}', (X, yc, zf + 2), (0, 0, 1), d + 18, 12, CHROME_TRIM, root, n=40)
            lib.cylinder(f'bowl{s}{x}', (X, yc, zf + 4), (0, 0, 1), d, 10, CHROME, root, n=40)
            lib.cylinder(f'bulb{s}{x}', (X, yc, zf + 10), (0, 0, 1), d * 0.3, 8, LENS, root, n=20)
            lib.cylinder(f'lens{s}{x}', (X, yc, zf + 12), (0, 0, 1), d - 4, 4, LAMP_GLASS, root, n=40)
        box(f'indicator{s}', (s * 502, 740, zf - 6), (145, 25, 10), LENS, root, bevel=3)
    # the chrome frame and the two openings it holds
    frame = slab('frame', [(x, y + yc) for (x, y) in _rrect(730, 160, 20)], zf - 4, zf + 10, CHROME_TRIM, root)
    cut(frame, [box('frameHole', (0, yc, zf), (702, 132, 40), CHROME_TRIM, None, bevel=10)])
    for s in (-1, 1):
        box(f'opening{s}', (s * 180, yc, zf - 2), (336, 132, 6), DELTA_RED, root, bevel=4)
        box(f'mesh{s}', (s * 180, yc, zf + 1), (320, 118, 3), BLACK, root, bevel=2)
        for k in range(-9, 10):                                 # diamond mesh, as crossed bars
            for sgn in (-1, 1):
                box(f'dia{s}{k}{sgn}', (s * 180 + k * 17, yc, zf + 3), (3, 130, 3), BLACK, root, bevel=0,
                    rot=Matrix.Rotation(math.radians(38 * sgn), 3, 'Y'))
    # Lancia post: a vertical bar opening into a V at the top
    tube('post', [(0, yc - 70, zf + 8), (0, yc + 30, zf + 8)], 16, CHROME_TRIM, root)
    for s in (-1, 1):
        tube(f'vee{s}', [(0, yc + 30, zf + 8), (s * 60, yc + 72, zf + 8)], 14, CHROME_TRIM, root)

    # ---- bumper, all body colour
    zb = 1740
    box('beam', (0, 680, zb - 60), (1480, 60, 120), PAINT, root, bevel=8)
    for s in (-1, 1):
        box(f'end{s}', (s * 760, 530, zb - 130), (50, 350, 160), PAINT, root, bevel=8)   # back edge at 1530, ahead of the tyre
    box('body', (0, 520, zb - 90), (1480, 300, 120), PAINT, root, bevel=8)
    for k in range(-2, 3):                                      # the row of five slots
        box(f'slot{k}', (k * 150, 615, zb - 28), (110, 26, 8), TEXBLACK, root, bevel=5)
    box('rib', (0, 570, zb - 24), (1440, 16, 10), PAINT, root, bevel=3)
    box('band', (0, 470, zb - 34), (1400, 130, 6), TEXBLACK, root, bevel=4)
    box('plate', (0, 470, zb - 28), (330, 110, 3), PLATE, root, bevel=1)
    for s in (-1, 1):
        box(f'fogBody{s}', (s * 460, 460, zb - 26), (163, 100, 14), BLACK, root, bevel=4)
        box(f'fog{s}', (s * 460, 460, zb - 18), (147, 84, 4), KOITO_YELLOW, root, bevel=3)
        box(f'fogRim{s}', (s * 460, 460, zb - 20), (155, 92, 3), CHROME, root, bevel=2)
    box('lip', (0, 355, zb - 50), (1380, 30, 110), PAINT, root, bevel=6)
    return root


def rear_damd_delta():
    """little 5./delta rear bumper (74,800 yen). DAMD publish no sizes;
    everything is off their straight-on shot (plate 330 = 130 px, 2.54 mm/px,
    heights anchored to the tailgate's bottom edge): a full-width body-colour
    bumper about 1590 across wrapping round onto the flare corners, 225 tall
    (y 645-420), with a grey lip 65 tall set back under both outer thirds;
    raised outer blocks about 480 wide (to +-310) ribbed with seven
    horizontal grooves, carrying DB's square tail lamps (about 228 x 60 at
    +-590, y 530); the plate centred in a recess across the colour/grey
    break."""
    root = group('rearBumper_damd_delta_rear')
    grey = material('DeltaGrey', 0x6b6e70, rough=0.6)
    W, ytop = 1590, REAR_TOP
    zf = REAR_FACE
    xloft('beam', rear_stations(W, ytop, 225, 140, wrap=120), PAINT, root, r=10)
    for s in (-1, 1):
        a, b = (265, W / 2) if s > 0 else (-W / 2, -265)
        xloft(f'lip{s}', rear_stations(W, 422, 67, 110, face=zf + 25, wrap=120, x0=a, x1=b), grey, root, r=6)
        a, b = (310, W / 2) if s > 0 else (-W / 2, -310)
        blk = rear_stations(W, ytop - 4, 215, 60, face=zf - 15, wrap=120, x0=a, x1=b)
        xloft(f'block{s}', blk, PAINT, root, r=8)
        for k in range(7):                                   # the grooves across the block
            box(f'groove{s}{k}', (s * 505, 440 + k * 30, zf - 16), (370, 5, 3), RUBBER, root, bevel=0.5)
        box(f'lampCase{s}', (s * 590, 530, zf - 19), (240, 72, 8), BLACK, root, bevel=4)
        box(f'lampRed{s}', (s * (590 + 38), 530, zf - 24), (148, 60, 3), TAILRED, root, bevel=3)
        box(f'lampAmb{s}', (s * (590 - 76), 530, zf - 24), (70, 60, 3), AMBER, root, bevel=3)
    box('plateRecess', (0, 458, zf - 1), (400, 200, 4), BLACK, root, bevel=4)
    box('plate', (0, 458, zf - 4.5), (330, 165, 3), PLATE, root, bevel=1)
    rear_mounts(root, ytop - 60)
    rear_valance(root)
    return root


def spoiler_damd_wing():
    """DAMD little delta FRP rear wing (63,800 yen): span about 1230, chord
    about 250 at about 30 degrees, leading edge about 20 above the roof and
    the trailing edge flush with the roof's rear end (z -1540) about 155 up;
    small end plates, black steel stays at x +-565 clamped to the gutters."""
    root = group('spoiler_damd_wing')
    ang = math.radians(30)
    zt, yt = -1540, 1623 + 155
    zl, yl = zt + 250 * math.cos(ang), yt - 250 * math.sin(ang)
    zm, ym = (zt + zl) / 2, (yt + yl) / 2
    box('blade', (0, ym, zm), (1230, 14, 250), PAINT, root, bevel=5, rot=Matrix.Rotation(-ang, 3, 'X'))
    for s in (-1, 1):
        box(f'plate{s}', (s * 612, ym + 10, zm), (6, 90, 280), PAINT, root, bevel=2)
        tube(f'stay{s}', [(s * 565, 1600, zm + 70), (s * 565, ym - 10, zm)], 22, BLACK, root)
        box(f'clamp{s}', (s * 600, 1590, zm + 70), (70, 30, 50), BLACK, root, bevel=3)
    return root


def spoiler_rowen():
    """ROWEN Roof Spoiler Electronics TYPE3 (1K002R30): a short ducktail on the
    roof's rear edge, not a raised wing -- about 1250 wide, 200 long, rising
    about 45 above the roof, with a black lens about 905 wide on its rear
    slope carrying a thin red stop-lamp strip."""
    root = group('spoiler_rowen')
    prof = [(1618, -1330), (1630, -1330), (1668, -1470), (1664, -1560), (1600, -1560), (1606, -1450)]
    prism('duck', prof, -625, 625, PAINT, root, smooth=False)
    box('lens', (0, 1640, -1562), (905, 34, 6), GLASS, root, bevel=3)
    box('stop', (0, 1640, -1566), (880, 6, 3), TAIL_RED, root, bevel=0)
    return root


def _centre_y(z):
    """Height of the body's centreline (x 0), from the raycast grid."""
    pts = sorted([p for p in CAR['top'] if p[0] == 0 and p[3].startswith('Body')], key=lambda p: p[2])
    for a, b in zip(pts, pts[1:]):
        if a[2] <= z <= b[2]:
            t = (z - a[2]) / (b[2] - a[2])
            return a[1] + (b[1] - a[1]) * t
    return pts[0][1] if z < pts[0][2] else pts[-1][1]


def stripe_damd_center():
    """The band down the centre of DAMD's red demo car: cream 25 + dark
    green 35 + cream 25, 85 mm with no gaps, over the bonnet and the roof (it
    skips the glass and the tailgate). DAMD say it is on the demo car only
    and is not part of the kit, so it is a cut-vinyl job."""
    root = group('stripe_damd_center')
    runs = [(1590, 790), (390, -1430)]                 # bonnet, roof (glass in between)
    for i, (z0, z1) in enumerate(runs):
        n = max(2, int(abs(z0 - z1) / 40))
        for x0, x1, mat in ((-42.5, -17.5, STRIPE_CREAM), (-17.5, 17.5, STRIPE_GREEN), (17.5, 42.5, STRIPE_CREAM)):
            bm = bmesh.new()
            vs = []
            for k in range(n + 1):
                z = z0 + (z1 - z0) * k / n
                y = _centre_y(z) + 2.0
                vs.append((bm.verts.new(P(x0, y, z)), bm.verts.new(P(x1, y, z))))
            for (a, b), (c, d) in zip(vs, vs[1:]):
                bm.faces.new((a, b, d, c))
            lib.new_object(f'band{i}{int(x0)}', bm, mat, root, smooth=True)
    return root


# ============================================================ ARB BASE RACK KIT
# Accessories that clip into the BASE Rack's dovetail rails
# (docs/jb74-arb-rack-accessories.json). ARB publish part numbers and prices
# but almost no dimensions, so the shapes follow their product photographs
# and the common sizes of what they hold: a NATO 20 L jerry can is
# 470 x 350 x 165, a MAXTRAX board 1160 x 330 x 60, a 48-inch Hi-Lift about
# 1220 long. Everything sits on the tray top of roofRack_arb.
MAXTRAX_ORANGE = material('MaxtraxOrange', 0xd96a1c, rough=0.7)
JACK_RED = material('HiLiftRed', 0xa8201a, rough=0.45, metal=0.3)
CAN_GREEN = material('JerryCanGreen', 0x3e4a33, rough=0.5, metal=0.3)


def _arb_frame():
    z0, z1 = RACK_ZC - ARB_L / 2, RACK_ZC + ARB_L / 2
    return ARB_W, z0, z1, RACK_TOP


def arb_deflector():
    """BASE Rack Deflector 17950020: one press-formed aluminium sheet the full
    tray width, curling up at the front edge, clipped under the front rail."""
    root = group('arbAcc_deflector')
    W, z0, z1, top = _arb_frame()
    box('deflector', (0, top - 50, z1 + 60), (W - 60, 80, 3), BLACK, root, bevel=1, rot=Matrix.Rotation(math.radians(-58), 3, 'X'))
    for s in (-1, 1):
        box(f'bracket{s}', (s * (W / 2 - 40), top - 45, z1 + 20), (6, 60, 90), BLACK, root, bevel=1)
    return root


def _rail_corner(name, at, root):
    box(name, at, (44, 44, 44), BLACK, root, bevel=10)


def arb_rail_front():
    """Front 3/4 guard rail 1780040: a low tube fence -- 25 mm tube about
    130 mm above the tray, cast corners -- round the front three quarters,
    open at the back."""
    root = group('arbAcc_railFront')
    W, z0, z1, top = _arb_frame()
    y = top + 130
    zb = z1 - 0.75 * ARB_L
    x = W / 2 - 25
    tube('rail', [(-x, y, zb), (-x, y, z1 - 25), (x, y, z1 - 25), (x, y, zb)], 25, BLACK, root, bend=60)
    for s in (-1, 1):
        for z in (zb, zb + (z1 - zb) / 2, z1 - 25):
            tube(f'post{s}{int(z)}', [(s * x, top, z), (s * x, y, z)], 25, BLACK, root)
            box(f'foot{s}{int(z)}', (s * x, top + 6, z), (40, 12, 60), BLACK, root, bevel=3)
    for x2 in (-W / 4, W / 4):
        tube(f'fpost{int(x2)}', [(x2, top, z1 - 25), (x2, y, z1 - 25)], 25, BLACK, root)
    return root


def arb_rail_side():
    """Side (trade) rail 1780110, one each side: a single straight 25 mm tube
    the full length, on cast feet in the side dovetail."""
    root = group('arbAcc_railSide')
    W, z0, z1, top = _arb_frame()
    y = top + 130
    for s in (-1, 1):
        x = s * (W / 2 - 12)
        lib.cylinder(f'rail{s}', (x, y, (z0 + z1) / 2), (0, 0, 1), 25, ARB_L - 60, BLACK, root, n=14)
        for k in range(4):
            z = z0 + 40 + k * (ARB_L - 80) / 3
            tube(f'post{s}{k}', [(x, top, z), (x, y, z)], 25, BLACK, root)
            box(f'foot{s}{k}', (x, top + 6, z), (40, 12, 60), BLACK, root, bevel=3)
    return root


def _jerry_can(name, centre, root, mat):
    """A NATO 20 L can lying on its side: 470 long (along x), 350 wide, 165 thick."""
    cx, cy, cz = centre
    b = box(name, (cx, cy, cz), (470, 165, 350), mat, root, bevel=18)
    for k in (-1, 1):                                        # the pressed X in each face
        box(f'{name}rib{k}', (cx, cy + 84, cz), (400, 4, 20), mat, root, bevel=2,
            rot=Matrix.Rotation(math.radians(38 * k), 3, 'Z'))       # lies in the top face
    for dz in (-100, 0, 100):                                # three handles along the top edge
        box(f'{name}h{dz}', (cx - 250, cy, cz + dz), (30, 40, 60), mat, root, bevel=6)
    lib.cylinder(f'{name}spout', (cx - 250, cy, cz + 150), (1, 0, 0), 40, 40, mat, root, n=12)
    return b


def arb_jerry():
    """Double horizontal jerry can holder 1780350: a base plate across the
    rear of the tray, two cans lying side by side, a ratchet strap over each."""
    root = group('arbAcc_jerry')
    W, z0, z1, top = _arb_frame()
    zc = z0 + 220
    box('plate', (0, top + 4, zc), (1000, 8, 380), BLACK, root, bevel=2)
    for i, x in enumerate((-250, 250)):
        _jerry_can(f'can{i}', (x, top + 8 + 83, zc), root, CAN_GREEN)
        box(f'strap{i}', (x, top + 8 + 168, zc), (40, 4, 360), WEBBING, root, bevel=1)
        for s in (-1, 1):
            box(f'strapSide{i}{s}', (x, top + 90, zc + s * 178), (40, 170, 4), WEBBING, root, bevel=1)
    return root


def arb_gas():
    """Gas bottle holder 1780250: a 9 kg-class bottle (about 300 across and
    550 long) lying across the front of the tray between stainless clamps."""
    root = group('arbAcc_gas')
    W, z0, z1, top = _arb_frame()
    zc = z1 - 260
    box('plate', (0, top + 4, zc), (640, 8, 280), BLACK, root, bevel=2)
    lib.cylinder('bottle', (0, top + 160, zc), (1, 0, 0), 300, 520, material('GasGrey', 0xbfc3c6, rough=0.4, metal=0.3), root, n=28, bevel=40)
    lib.cylinder('valve', (290, top + 160, zc), (1, 0, 0), 60, 60, STEEL, root, n=12)
    for s in (-1, 1):
        box(f'clamp{s}', (s * 240, top + 90, zc), (20, 150, 300), STEEL, root, bevel=4)
    box('strap', (0, top + 312, zc), (40, 4, 300), WEBBING, root, bevel=1)
    return root


def arb_boards():
    """Recovery board mount 1780310: two MAXTRAX (1160 x 330 x 60) stacked flat
    along the left side of the tray, held by four dovetail pins."""
    root = group('arbAcc_boards')
    W, z0, z1, top = _arb_frame()
    x, zc = W / 2 - 200, RACK_ZC + 150
    for i in range(2):
        y = top + 8 + 30 + i * 62
        b = box(f'board{i}', (x, y, zc), (330, 58, 1160), MAXTRAX_ORANGE, root, bevel=12)
        for k in range(-5, 6):                               # the moulded cleats
            box(f'cleat{i}{k}', (x, y + 30, zc + k * 95), (280, 6, 26), MAXTRAX_ORANGE, root, bevel=2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            box(f'pin{sx}{sz}', (x + sx * 150, top + 70, zc + sz * 520), (30, 150, 30), BLACK, root, bevel=4)
    return root


def arb_jack():
    """Premium Hi-Lift jack holder 1780280: a 48-inch farm jack lying fore and
    aft on the right half of the tray, clamped at the top and the foot."""
    root = group('arbAcc_jack')
    W, z0, z1, top = _arb_frame()
    x, zc, y = RIGHT * 430, RACK_ZC + 120, top + 50
    box('bar', (x, y, zc), (50, 30, 1220), JACK_RED, root, bevel=3)
    for k in range(30):                                      # the climbing holes
        box(f'hole{k}', (x, y + 16, zc - 560 + k * 38), (18, 3, 12), BLACK, root, bevel=0)
    box('mech', (x, y + 10, zc + 250), (120, 80, 200), JACK_RED, root, bevel=8)
    lib.cylinder('handle', (x - 20, y + 45, zc + 60), (0, 0, 1), 28, 900, BLACK, root, n=12)
    box('foot', (x, y - 5, zc - 620), (150, 40, 90), BLACK, root, bevel=6)
    box('top', (x, y, zc + 620), (80, 40, 40), BLACK, root, bevel=6)
    for z in (zc - 450, zc + 450):
        box(f'clamp{z}', (x, y - 10, z), (110, 70, 60), BLACK, root, bevel=6)
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
# ============================================================ RACK & AWNING KIT
# Shared pieces for every roof rack and awning bag. A photo review of all 17
# racks and 14 awnings against the makers' own pages (2026-09-26) found the
# same faults everywhere: rails were plain rounded bars with a 2 mm strip
# stuck on as the "T-slot", slats were boxes, a leg was one bent strap, the
# deflector a flat sheet tilted 58 degrees, and a fabric bag was a crisp black
# beam. What makes the real ones read as bought parts, and what these helpers
# draw: an extruded rail whose slot is a recess (a shadow line), a perimeter
# that turns its corners (cast corner or rounded extrusion), hat-section slats
# with a recessed slot and fluting, a foot on a rubber pad with a clamp plate
# and bolt heads under a tapered tower, a curved pressed deflector, and a soft
# pinched bag with welted seams, a zip, and webbing straps with buckles.

def sharp(ob, angle=35):
    """Smooth shading that still keeps the extrusion's corners crisp."""
    m = ob.modifiers.new('split', 'EDGE_SPLIT')
    m.split_angle = math.radians(angle)
    return ob


def hsweep(name, pts, prof, mat, parent=None, closed=False, caps=True, scale=None, crisp=True):
    """Sweep an (out, up) profile along a HORIZONTAL car-frame path. 'out' is
    to the left of the direction of travel (up x tangent), so a rectangle run
    +Z along the +X side, then -X across the front, has 'out' pointing
    outward the whole way round. `scale(i) -> k` shrinks ring i about the
    path (for a pinched fabric bag)."""
    n = len(pts)
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        a = pts[i - 1] if closed else pts[max(i - 1, 0)]
        b = pts[(i + 1) % n] if closed else pts[min(i + 1, n - 1)]
        tx, tz = b[0] - a[0], b[2] - a[2]
        ln = math.hypot(tx, tz) or 1.0
        lx, lz = tz / ln, -tx / ln
        k = scale(i) if scale else 1.0
        rings.append([bm.verts.new(P(p[0] + lx * u * k, p[1] + v * k, p[2] + lz * u * k)) for (u, v) in prof])
    m = len(prof)
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for r0, r1 in pairs:
        for j in range(m):
            bm.faces.new((r0[j], r0[(j + 1) % m], r1[(j + 1) % m], r1[j]))
    if caps and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = lib.new_object(name, bm, mat, parent, smooth=True)
    return sharp(ob) if crisp else ob


def rail_prof(w, h, kind='tslot'):
    """Side-rail extrusion, (out, up) about its centre. 'tslot' has a T-slot
    recessed into the outboard face, 'dovetail' (ARB) a dovetail groove,
    'round' (Yakima) a fat rounded aero face, 'plate' (APIO) a tall thin
    plate."""
    c = min(3.0, w * 0.08)
    if kind == 'round':
        return rounded_rect(w, h, min(w, h) * 0.42, 5)
    if kind == 'plate':
        return rounded_rect(w, h, 3, 2)
    o = min(5.0, h * 0.12)                      # slot opening half-height
    d = min(10.0, w * 0.28)                     # slot depth
    if kind == 'dovetail':
        slot = [(w / 2, -o), (w / 2 - d, -o - 4), (w / 2 - d, o + 4), (w / 2, o)]
    else:
        slot = [(w / 2, -o), (w / 2 - 3, -o), (w / 2 - 3, -o - 4), (w / 2 - d, -o - 4),
                (w / 2 - d, o + 4), (w / 2 - 3, o + 4), (w / 2 - 3, o), (w / 2, o)]
    return ([(-w / 2 + c, -h / 2), (w / 2 - c, -h / 2), (w / 2, -h / 2 + c)] + slot +
            [(w / 2, h / 2 - c), (w / 2 - c, h / 2), (-w / 2 + c, h / 2), (-w / 2, h / 2 - c), (-w / 2, -h / 2 + c)])


def slat_prof(sw, sh, flutes=0, slot=True):
    """Hat-section slat, (across, up) with its top at up = 0: tapered sides,
    a recessed T-slot down the middle and `flutes` shallow grooves either
    side of it."""
    top = []
    fl = [sw * (0.18 + 0.2 * k) for k in range(flutes)]
    for f in reversed(fl):                                  # right-hand flutes, outside in
        top += [(f + 2.5, 0), (f, -1.8), (f - 2.5, 0)]
    if slot:
        top += [(4, 0), (4, -3), (7.5, -3), (7.5, -min(10, sh - 4)), (-7.5, -min(10, sh - 4)), (-7.5, -3), (-4, -3), (-4, 0)]
    for f in fl:                                            # left-hand, inside out
        top += [(-f + 2.5, 0), (-f, -1.8), (-f - 2.5, 0)]
    return ([(-sw / 2 + 4, -sh), (sw / 2 - 4, -sh), (sw / 2, -3), (sw / 2 - 2, 0)] + top +
            [(-sw / 2 + 2, 0), (-sw / 2, -3)])


def rect_loop(xh, z0, z1, y, R, steps=6):
    """Rounded-rectangle centre line, closed, run so hsweep's 'out' faces out."""
    zm = (z0 + z1) / 2
    pts = [(xh, y, zm), (xh, y, z1), (-xh, y, z1), (-xh, y, z0), (xh, y, z0), (xh, y, zm)]
    return [tuple(p) for p in fillet(pts, R, steps)][:-1]


def corner_arcs(xh, z0, z1, y, R, run=60, steps=6):
    """The four corners of rect_loop, each with `run` mm of straight either side."""
    out = []
    corners = [((xh, y, z1), (0, 0, 1), (-1, 0, 0)), ((-xh, y, z1), (-1, 0, 0), (0, 0, -1)),
               ((-xh, y, z0), (0, 0, -1), (1, 0, 0)), ((xh, y, z0), (1, 0, 0), (0, 0, 1))]
    for c, di, do in corners:
        c = Vector(c)
        a = c - Vector(di) * (R + run)
        b = c + Vector(do) * (R + run)
        out.append([tuple(p) for p in fillet([a, c, b], R, steps)])
    return out


def curved_strip(name, x0, x1, arc, t, mat, parent=None):
    """A pressed sheet across the car: `arc` is its section as (y, z) points,
    `t` its thickness, built from quads only (a crescent-shaped n-gon cap
    triangulates through itself)."""
    bm = bmesh.new()
    n = len(arc)
    rows = []
    for i, (y, z) in enumerate(arc):
        (ya, za), (yb, zb) = arc[max(i - 1, 0)], arc[min(i + 1, n - 1)]
        dy, dz = yb - ya, zb - za
        ln = math.hypot(dy, dz) or 1.0
        ny, nz = -dz / ln, dy / ln                          # normal in the section plane
        rows.append([bm.verts.new(P(x, y + ny * o, z + nz * o)) for x in (x0, x1) for o in (0, -t)])
    for r0, r1 in zip(rows, rows[1:]):                      # r = [x0 out, x0 in, x1 out, x1 in]
        bm.faces.new((r0[0], r0[2], r1[2], r1[0]))
        bm.faces.new((r0[1], r1[1], r1[3], r0[3]))
        bm.faces.new((r0[0], r1[0], r1[1], r0[1]))
        bm.faces.new((r0[2], r0[3], r1[3], r1[2]))
    for r in (rows[0], rows[-1]):
        bm.faces.new((r[0], r[1], r[3], r[2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return sharp(lib.new_object(name, bm, mat, parent, smooth=True), 40)


def bezier2(a, c, b, n=10):
    return [tuple(a[k] * (1 - u) ** 2 + c[k] * 2 * u * (1 - u) + b[k] * u * u for k in range(len(a)))
            for u in (i / n for i in range(n + 1))]


def bolt(name, centre, axis, parent, dia=13, length=6, mat=None):
    """Hex bolt head."""
    return lib.cylinder(name, centre, axis, dia, length, mat or STEEL, parent, n=6)


def gutter_leg(root, name, s, z, rail_x, deck, kind='tower', depth=64):
    """One gutter mount: rubber pad on the gutter, foot casting, clamp plate
    hooked under the gutter lip with its bolt, and the upright to the rail.
    The gutter lip is at |x| 644 at y 1550 (sampled), so the clamp stands
    just outboard of that; the roof side is at |x| 599 by y 1600, so nothing
    inboard of |x| 612 comes below y 1595."""
    gy = ROOF_Y_EDGE
    box(f'{name}pad', (s * (GUTTER_X + 8), gy - 3, z), (44, 8, depth + 6), RUBBER, root, bevel=2)
    box(f'{name}foot', (s * (GUTTER_X + 22), gy + 6, z), (50, 12, depth + 10), BLACK, root, bevel=3)
    box(f'{name}clamp', (s * 652, gy - 12, z), (6, 44, depth - 14), BLACK, root, bevel=1.5)
    box(f'{name}hook', (s * 650, gy - 32, z), (12, 5, depth - 14), BLACK, root, bevel=1)
    bolt(f'{name}clampBolt', (s * 658, gy - 8, z), (1, 0, 0), root, dia=14, length=7)
    xi, xo = rail_x - 26, max(rail_x + 22, GUTTER_X + 44)
    if kind == 'plate3':                                   # Rhino: one plate along the car, three holes
        th = 7
        slab(f'{name}tower', [(s * (GUTTER_X + 6), gy + 12), (s * (GUTTER_X + 34), gy + 12),
                              (s * (rail_x + 10), deck), (s * (rail_x - 14), deck)], z - 90, z + 90, BLACK, root)
        xm = (GUTTER_X + 20 + rail_x - 2) / 2
        box(f'{name}plate', (s * (xm + 10), (gy + 12 + deck) / 2 + 2, z), (th, deck - gy - 8, 200), BLACK, root, bevel=2)
        for k in (-1, 0, 1):
            lib.cylinder(f'{name}hole{k}', (s * (xm + 10), (gy + 12 + deck) / 2 + 4, z + k * 58), (1, 0, 0),
                         30 if k else 36, th + 1.2, RUBBER, root, n=16)
    elif kind == 'sleg':                                   # IPF: curved arm down to a knob clamp
        arm = [(s * rail_x, deck, z), (s * (rail_x + 18), deck - 18, z), (s * (GUTTER_X + 30), gy + 22, z),
               (s * (GUTTER_X + 24), gy + 10, z)]
        sweep(f'{name}tower', [tuple(p) for p in fillet(arm, 20)], rounded_rect(14, 40, 4), BLACK, root)
        lib.cylinder(f'{name}knob', (s * 668, gy - 8, z), (1, 0, 0), 30, 18, TEXBLACK, root, n=8)
    else:                                                  # tapered cast tower
        t = slab(f'{name}tower', [(s * (GUTTER_X + 2), gy + 12), (s * (GUTTER_X + 40), gy + 12),
                                  (s * xo, deck + 2), (s * xi, deck + 2)],
                 z - depth / 2, z + depth / 2, BLACK, root)
        mod = t.modifiers.new('bevel', 'BEVEL'); mod.width = 4 * lib.MM; mod.segments = 2
        bolt(f'{name}footBolt', (s * (GUTTER_X + 22), gy + 13, z + depth / 2 - 10), (0, 1, 0), root, dia=12, length=5)
    for k in (-1, 1):                                      # bolts into the rail's slot
        bolt(f'{name}railBolt{k}', (s * (rail_x + 1), deck - 3, z + k * depth * 0.3), (0, 1, 0), root, dia=11, length=5)


def deflector_curve(root, W, top, zf, drop=62, reach=95, holes=0, inset=40):
    """Curved pressed wind deflector across the front, on a bracket each end.
    Its lowest edge stays above the roof's front (y 1599 at z 300, 1577 at
    z 400 on the centre line)."""
    arc = bezier2((top - 4, zf), (top - 4, zf + reach * 0.75), (top - drop, zf + reach), 10)
    xh = W / 2 - inset
    curved_strip('deflector', -xh, xh, arc, 3, BLACK, root)
    for s in (-1, 1):
        # a gusset plate under the sheet's end, following its curve
        under = [(y - 3, z) for (y, z) in arc[:8]]
        prism(f'deflBracket{s}', [(top - 6, zf - 34)] + under + [(top - drop * 0.8, zf - 34)],
              s * (xh - 4), s * (xh + 2), BLACK, root)
        bolt(f'deflBolt{s}', (s * (xh + 4), top - 22, zf - 18), (1, 0, 0), root, dia=11, length=5)
    for k in range(holes):                                 # APIO: four round holes in the front plate
        y, z = arc[5]
        lib.cylinder(f'deflHole{k}', (-xh * 0.6 + k * xh * 0.4, y + 1, z + 1), (0, 0.8, 0.6), 34, 4.5, RUBBER, root, n=16)


def rack_frame(pid, W, L, top=None, rail=(50, 45), rail_kind='tslot', R=None, castings=None,
               slat_dir='across', slats=14, slat_w=62, slat_h=18, flutes=1, bars='slat', legs=6,
               leg_kind='tower', deflector=True, defl_drop=62, fairing=False, defl_holes=0,
               side_bars=0, tube_frame=0, spine=False, backbone=False, eyebolts=0, label=None,
               badge=None, leg_depth=64):
    """Platform on gutter legs, the construction every rack here shares:
    extruded perimeter with rounded corners (castings optional), slats flush
    with its top, gutter legs, optional deflector. Returns the root."""
    root = group(f'roofRack_{pid}')
    top = top or RACK_TOP
    rw, rh = rail
    deck = top - rh
    zc = RACK_ZC
    z0, z1 = zc - L / 2, zc + L / 2
    xh = W / 2 - rw / 2
    R = R if R is not None else rw / 2 + 10
    loop = rect_loop(xh, z0 + rw / 2, z1 - rw / 2, top - rh / 2, R)
    hsweep('rail', loop, rail_prof(rw, rh, rail_kind), BLACK, root, closed=True)
    if castings:                                            # cast corners over the extrusion
        cw, ch = castings if isinstance(castings, tuple) else (rw + 8, rh + 6)
        for i, arcp in enumerate(corner_arcs(xh, z0 + rw / 2, z1 - rw / 2, top - rh / 2 + 1.5, R, run=45)):
            hsweep(f'corner{i}', arcp, rounded_rect(cw, ch, min(10, ch * 0.3), 3), BLACK, root)
            for k, f in enumerate((0.3, 0.7)):
                q = arcp[int(len(arcp) * f)]
                bolt(f'cornerBolt{i}{k}', (q[0] * 0.995, top + 2.5, q[2] - math.copysign(4, q[2] - zc)), (0, 1, 0), root, dia=10, length=4)
    else:                                                   # plastic end caps at the corners
        for i, arcp in enumerate(corner_arcs(xh, z0 + rw / 2, z1 - rw / 2, top - rh / 2, R, run=8)):
            hsweep(f'corner{i}', arcp, rounded_rect(rw + 3, rh + 3, 4, 2), TEXBLACK, root)
    # slats, tucked 6 mm into the rails either end
    inner = W / 2 - rw + 6
    if slat_dir == 'across':
        pitch = (L - 2 * rw - slat_w - 20) / max(1, slats - 1)
        for i in range(slats):
            z = z0 + rw + 10 + slat_w / 2 + i * pitch
            if bars == 'aero':
                hsweep(f'slat{i}', [(-inner, top - 4, z), (inner, top - 4, z)],
                       [(u, v - 4) for (u, v) in rounded_rect(slat_w, slat_h, slat_h * 0.45, 4)], BLACK, root, caps=False)
                box(f'slot{i}', (0, top - 3.2, z), (2 * inner - 60, 1.5, 8), TEXBLACK, root, bevel=0)
            else:
                hsweep(f'slat{i}', [(-inner, top, z), (inner, top, z)], slat_prof(slat_w, slat_h, flutes), BLACK, root, caps=False)
    else:
        span = W - 2 * rw
        pitch = (span - slat_w - 40) / max(1, slats - 1)
        zin = L / 2 - rw + 6
        for i in range(slats):
            x = -span / 2 + 20 + slat_w / 2 + i * pitch
            hsweep(f'slat{i}', [(x, top, zc - zin), (x, top, zc + zin)], slat_prof(slat_w, slat_h, flutes), BLACK, root, caps=False)
    if backbone:                                           # Rhino: two cross members under the slats
        for k in (-1, 1):
            hsweep(f'backbone{k}', [(-inner, top - slat_h - 12, zc + k * L * 0.22), (inner, top - slat_h - 12, zc + k * L * 0.22)],
                   rail_prof(40, 24), BLACK, root, caps=True)
    if spine:                                              # URNIETA: a fore-aft spine down the middle
        hsweep('spine', [(0, top - 2, z0 + rw), (0, top - 2, z1 - rw)], slat_prof(52, 24, 1), BLACK, root, caps=False)
    for k in range(eyebolts):                              # tie-down eye bolts on the slats
        for s in (-1, 1):
            z = z0 + L * (0.2 + 0.6 * k / max(1, eyebolts - 1))
            ex = s * (W / 2 - rw - 110)
            sweep(f'eye{s}{k}', [tuple(p) for p in fillet([(ex - 12, top + 1, z), (ex - 12, top + 22, z), (ex + 12, top + 22, z), (ex + 12, top + 1, z)], 11, 4)],
                  circle(3, 6), STEEL, root)
    # gutter legs
    per = legs // 2
    for s in (-1, 1):
        for k in range(per):
            z = z0 + 170 + k * (L - 340) / max(1, per - 1)
            z = min(max(z, ROOF_Z_REAR + 90), ROOF_Z_FRONT - 150)
            gutter_leg(root, f'leg{s}{k}', s, z, xh, deck, leg_kind, leg_depth)
    if deflector:
        deflector_curve(root, W, top, z1 - 4, defl_drop, holes=defl_holes)
    if fairing:                                            # Yakima: short fairing under the front rail
        arc = bezier2((top - rh + 4, z1 - 10), (top - rh - 10, z1 + 20), (top - rh - 34, z1 + 10), 6)
        curved_strip('fairing', -xh + 30, xh - 30, arc, 3, BLACK, root)
    if side_bars:                                          # JAOS side bars: two sections a side on posts
        for s in (-1, 1):
            for seg in (-1, 1):
                za, zb = zc + seg * 40, zc + seg * (L / 2 - 90)
                za, zb = min(za, zb), max(za, zb)
                hsweep(f'sideBar{s}{seg}', [(s * xh, top + side_bars, za), (s * xh, top + side_bars, zb)],
                       rounded_rect(26, 22, 6, 3), BLACK, root)
                for zz in (za + 40, zb - 40):
                    lib.cylinder(f'sidePost{s}{seg}{zz:.0f}', (s * xh, top + side_bars / 2, zz), (0, 1, 0), 20, side_bars, BLACK, root, n=12)
                for zz in (za, zb):
                    box(f'sideCap{s}{seg}{zz:.0f}', (s * xh, top + side_bars, zz), (30, 26, 12), TEXBLACK, root, bevel=4)
    if tube_frame:                                         # URNIETA: low round-tube frame round the edge
        tl = rect_loop(xh - 10, z0 + rw, z1 - rw, top + tube_frame, 110, 6)
        hsweep('tubeFrame', tl, circle(16, 12), BLACK, root, closed=True, crisp=False)
        for s in (-1, 1):
            for k in range(4):
                zz = z0 + 150 + k * (L - 300) / 3
                lib.cylinder(f'tubePost{s}{k}', (s * (xh - 10), top + tube_frame / 2, zz), (0, 1, 0), 20, tube_frame, BLACK, root, n=10)
    if badge:                                              # maker's badge plate on the front rail
        box('badge', (0, top - rh / 2, z1 + 1.5), (140, rh * 0.5, 3), badge, root, bevel=0.5)
        for k in (-1, 1):
            bolt(f'badgeBolt{k}', (k * 60, top - rh / 2, z1 + 3.5), (0, 0, 1), root, dia=8, length=3)
    return root


# Per-product look, from the photo review (docs in the review JSON). Only
# construction details live here -- overall sizes stay in the build() calls,
# which carry the published figures.
RACK_STYLE = {
    # Rhino Pioneer: fore-aft slats on two Backbone cross members, legs are
    # plates with three lightening holes. No mesh floor in any photo.
    'pioneer': dict(R=40, slat_w=86, slat_h=20, flutes=2, leg_kind='plate3', backbone=True),
    # JAOS: square frame under big moulded corner covers (39 mm over a 32 mm
    # frame), ribbed tower clamps, short side bars in two sections a side.
    'jaos': dict(rail_kind='tslot', R=18, castings=(46, 39), slat_w=50, slat_h=20, leg_depth=72),
    # IPF EXR-01: flat (38.8 mm), small square corner caps, fat fluted slats,
    # S-legs with a knob clamp, eye bolts. There is no raised hoop.
    'ipf': dict(R=22, slat_w=80, slat_h=26, flutes=2, leg_kind='sleg', eyebolts=2),
    # APIO: tall thin plate rails, four slats, angled front plate with holes.
    'apio': dict(rail_kind='plate', R=16, slat_w=70, slat_h=22, flutes=0, defl_holes=4, defl_drop=50),
    # SHOWA A-x: many fluted slats, big round corner castings, emblem plate.
    'showa_foot': dict(R=70, castings=True, slat_w=70, slat_h=20, flutes=2),
    # Taiwan generic: twin-channel slats, big moulded round corners, eye bolts.
    'tw_generic': dict(R=110, castings=True, slat_w=90, slat_h=22, flutes=2, eyebolts=3),
    # Yakima LockNLoad: fat rounded perimeter, aero crossbars, front fairing.
    'yakima': dict(rail_kind='round', R=140, bars='aero', slat_w=70, slat_h=22, fairing=True),
    'fr34': dict(slat_w=62, slat_h=18, flutes=1),
    # URNIETA SALADO: 50 mm channels, centre spine, low tube frame, deep
    # stamped deflector.
    'urnieta_salado': dict(slat_w=50, slat_h=24, flutes=0, spine=True, tube_frame=36, defl_drop=100),
    'urnieta_salado_half': dict(slat_w=50, slat_h=24, flutes=0, spine=True, tube_frame=36, defl_drop=100),
}


def rack_platform(pid, W, L, slat_dir='across', slats=None, rail=(50, 45), legs=6, deflector=True, top=None, **kw):
    """Flat platform on gutter legs; the construction is rack_frame(), the
    per-product details RACK_STYLE."""
    style = dict(RACK_STYLE.get(pid, {}))
    style.update(kw)
    n = slats or (int((L - 60) // 110) if slat_dir == 'across' else int((W - 2 * rail[0]) // 75))
    root = rack_frame(pid, W, L, top=top, rail=rail, slat_dir=slat_dir, slats=n, legs=legs, deflector=deflector, **style)
    top = top or RACK_TOP
    if pid == 'apio':                                      # slot holes along the plate rails
        for s in (-1, 1):
            for k in range(14):
                z = RACK_ZC - L / 2 + 120 + k * (L - 240) / 13
                box(f'railHole{s}{k}', (s * (W / 2 + 0.6), top - rail[1] / 2, z), (1.5, 12, 34), RUBBER, root, bevel=0)
    if pid == 'showa_foot':
        box('emblem', (0, top - rail[1] / 2, RACK_ZC + L / 2 + 1.5), (170, 22, 3), material('LabelWhite', 0xf0f0ec, rough=0.6), root, bevel=0.5)
    return root


def squircle(w, h, n=24, p=4.0):
    """Soft box section: what a stuffed PVC bag looks like end-on."""
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        c, s_ = math.cos(a), math.sin(a)
        out.append((math.copysign(abs(c) ** (2 / p), c) * w / 2, math.copysign(abs(s_) ** (2 / p), s_) * h / 2))
    return out


AWNING_LABEL = {'arb': ('LabelRed', 0xb3261e), 'yakima': ('LabelWhite', 0xf0f0ec), 'rhino': ('LabelWhite', 0xf0f0ec),
                'darche': ('LabelWhite', 0xf0f0ec), 'allblack': ('LabelOrange', 0xd8641e), 'ikamper': ('LabelWhite', 0xf0f0ec)}


def awning_case(pid, side, L, W, H, mat, hard=None, hinge=False):
    """Roll-out awning on the rack's side rail. Soft types are a PVC bag:
    squircle section pinched where the straps pull it in, welted seams top
    and bottom, a zip along the lower outboard edge with its pull, webbing
    straps with buckles, moulded end caps. Hard types (ARB alu, iKamper) are
    a grooved extrusion with a lid line, end castings and latches. `hinge`
    adds the 270/180 pivot at the REAR end: a cast housing over the bag's
    end, the pivot on top of it bolted to the rack, and the folded arms'
    knuckles showing out of its end."""
    root = group(f'awning_{pid}_{side}')
    s = -RIGHT if side == 'left' else RIGHT
    if hard is None:                                       # every PVC entry is a bag; the default used to
        hard = mat is not PVC                              # be True, so all fourteen were drawn as hard cases
    # every case is centred on the roof, so it overhangs the same amount front
    # and rear -- never trailing a long tail off the back
    # hung OUTBOARD of the rack's side rail (it used to sit 30 mm inside it),
    # and never lower than just above the gutter, or a tall bag runs into
    # the roof side and over the top of the door glass. The 5 mm over the old
    # 1595 floor is for the straps, which wrap the bag.
    x, y, zc = s * (ARB_W / 2 + W / 2 + 5), max(RACK_TOP + 40 - H / 2, 1600 + H / 2), RACK_ZC
    za, zb = zc - L / 2 + 30, zc + L / 2 - 30             # the bag between its end caps
    yt = y + H / 2
    lab = next((v for k, v in AWNING_LABEL.items() if pid.startswith(k)), None)
    lab = material(*lab, rough=0.6) if lab else None
    if hard:
        # extrusion: chamfered box with two grooves down the outboard face,
        # one along the top, and the lid split line at the top outboard edge
        w2, h2 = W / 2, H / 2
        prof = [(-w2 + 6, -h2), (w2 - 6, -h2), (w2, -h2 + 6), (w2, -h2 * 0.35), (w2 - 3, -h2 * 0.35 + 3), (w2, -h2 * 0.35 + 6),
                (w2, h2 * 0.3), (w2 - 3, h2 * 0.3 + 3), (w2, h2 * 0.3 + 6), (w2, h2 - 10), (w2 - 5, h2 - 7), (w2 - 10, h2),
                (w2 * 0.2 + 3, h2), (w2 * 0.2, h2 - 3), (w2 * 0.2 - 3, h2), (-w2 + 6, h2), (-w2, h2 - 6), (-w2, -h2 + 6)]
        prof = [(u * s, v) for (u, v) in prof]
        hsweep('bag', [(x, y, za), (x, y, zb)], prof, mat, root, caps=False)
        for k, z in enumerate((za, zb)):                   # end castings
            d = -1 if k == 0 else 1
            hsweep(f'cap{k}', [(x, y, z - d * 6), (x, y, z + d * 30)], rounded_rect(W + 10, H + 10, 14, 4), TEXBLACK, root)
            box(f'capFace{k}', (x, y, z + d * 31), (W - 20, H - 20, 3), BLACK, root, bevel=1)
        for k in range(3):                                 # latches under the lid
            z = zc + (k - 1) * L * 0.3
            box(f'latch{k}', (x + s * (W / 2 + 2), y + H * 0.1, z), (5, 30, 44), STEEL, root, bevel=1.5)
        lib.cylinder('lidHinge', (x - s * W * 0.1, yt + 1, zc), (0, 0, 1), 8, L - 120, TEXBLACK, root, n=8)
        if lab:
            box('label', (x + s * (W / 2 + 0.8), y - H * 0.1, zb - 220), (1.5, 18, 170), lab, root, bevel=0)
    else:
        sec = squircle(W, H)
        straps = [zc + k * L * 0.3 for k in (-1, 1)] if L < 2300 else [zc + k * L * 0.33 for k in (-1, 0, 1)]
        n = 36
        path = [(x, y, za + (zb - za) * i / (n - 1)) for i in range(n)]

        def pinch(i):
            z = path[i][2]
            return 1 - 0.07 * sum(math.exp(-((z - zs) / 70) ** 2) for zs in straps) - 0.03 * math.exp(-((z - za) / 40) ** 2) \
                - 0.03 * math.exp(-((z - zb) / 40) ** 2)
        hsweep('bag', path, sec, mat, root, scale=pinch, crisp=False)
        # welted seams along the four long edges
        for k, a in enumerate((40, 140, 220, 320)):
            r = math.radians(a)
            u = math.copysign(abs(math.cos(r)) ** 0.5, math.cos(r)) * (W / 2 + 1)
            v = math.copysign(abs(math.sin(r)) ** 0.5, math.sin(r)) * (H / 2 + 1)
            lib.cylinder(f'seam{k}', (x + s * u, y + v, zc), (0, 0, 1), 6, zb - za - 40, mat, root, n=6)
        # zip down the lower outboard edge, with its pull near the front
        r = math.radians(-22)
        zu, zv = (abs(math.cos(r)) ** 0.5) * (W / 2 + 1.5), -(abs(math.sin(r)) ** 0.5) * (H / 2 + 1.5)
        lib.cylinder('zip', (x + s * zu, y + zv, zc), (0, 0, 1), 8, zb - za - 80, TEXBLACK, root, n=6)
        box('zipPull', (x + s * (zu + 4), y + zv - 10, zb - 90), (4, 26, 12), STEEL, root, bevel=1.5)
        # webbing straps round the bag, buckle on the outboard face
        for j, zs in enumerate(straps):
            k = 0.93
            ring = [(x + u * k * 1.02 + math.copysign(3, u), y + v * k * 1.02 + math.copysign(3, v), zs) for (u, v) in squircle(W, H, 20)]
            ring = ring[15:] + ring[:15]                       # start underneath, where the seam hides
            sweep(f'strap{j}', ring + [ring[0]], [(-19, -1.6), (19, -1.6), (19, 1.6), (-19, 1.6)], WEBBING, root, caps=False)
            bx = x + s * (W / 2 * k + 7)
            box(f'buckle{j}', (bx, y + H * 0.05, zs), (7, 34, 46), TEXBLACK, root, bevel=2)
            box(f'buckleBar{j}', (bx + s * 3.5, y + H * 0.05 + 8, zs), (2, 5, 40), STEEL, root, bevel=0.5)
        # moulded end caps: a skirt over the bag and a chamfered face
        for k, z in enumerate((za, zb)):
            d = -1 if k == 0 else 1
            st = [(x, y, z - d * 20), (x, y, z + d * 6), (x, y, z + d * 26), (x, y, z + d * 34)]
            ks = (1.0, 1.08, 1.08, 0.94)
            hsweep(f'cap{k}', st, [(u * 1.0, v) for (u, v) in squircle(W, H, 20)], BLACK, root, scale=lambda i: ks[i])
        if lab:
            box('label', (x + s * (W / 2 * 0.99 + 1), y + H * 0.12, zb - 260), (1.5, min(24, H * 0.18), 190), lab, root, bevel=0)
    # L-brackets: a plate bolted to the rack rail's outer face, a flat arm
    # over the bag's top, a gusset between them
    for k in (-1, 1):
        z = zc + k * min(600, L * 0.3)
        xr = s * (ARB_W / 2 + 3)
        yb = RACK_TOP - 36
        box(f'bracketV{k}', (xr, (yb + yt + 8) / 2, z), (6, yt + 8 - yb, 50), BLACK, root, bevel=1.5)
        box(f'bracketH{k}', (s * (ARB_W / 2 + W * 0.45), yt + 3, z), (W * 0.9, 6, 50), BLACK, root, bevel=1.5)
        slab(f'gusset{k}', [(xr, yt), (xr + s * 40, yt), (xr, yt - 40)], z - 3, z + 3, BLACK, root)
        for b in (-1, 1):
            bolt(f'bracketBolt{k}{b}', (xr + s * 3.5, yb + 12, z + b * 14), (1, 0, 0), root, dia=12, length=5)
            bolt(f'bagBolt{k}{b}', (s * (ARB_W / 2 + W * 0.55), yt + 6.5, z + b * 14), (0, 1, 0), root, dia=11, length=4)
    if hinge:
        zr = zc - L / 2 + 10                               # hinge at the rear end
        hsg = box('hinge', (x, y + 5, zr + 20), (W + 24, H + 18, 80), TEXBLACK, root, bevel=14)
        hsg.modifiers['bevel'].segments = 3
        for k in range(4):                                 # folded arms' knuckles out of its end
            yy = y - H / 2 + 30 + k * (H - 50) / 3
            box(f'knuckle{k}', (x + s * W * 0.18, yy, zr - 26), (W * 0.42, min(26, H / 5), 24), BLACK, root, bevel=4)
            bolt(f'knucklePin{k}', (x + s * (W * 0.18 + W * 0.21 + 2), yy, zr - 26), (1, 0, 0), root, dia=10, length=4)
        py = y + 5 + (H + 18) / 2
        lib.cylinder('pivot', (x - s * W * 0.1, py + 14, zr + 20), (0, 1, 0), 64, 28, BLACK, root, n=20)
        bolt('pivotBolt', (x - s * W * 0.1, py + 30, zr + 20), (0, 1, 0), root, dia=24, length=6)
        box('pivotArm', (s * (ARB_W / 2 + W * 0.2), py + 6, zr + 20), (W * 0.6 + 40, 8, 70), BLACK, root, bevel=2)
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


# Where the bars sit. A photo review of all 35 bars (2026-09-26) found the
# same faults over and over, and these numbers are its fixes.
#
# Front: the grille panel runs y 750-960 and the stock bumper's top edge was
# 736. Every real bar tucks its top up under the grille (y 720-745); ours
# stopped at 640-680 and left a strip of bare body showing under it.
FRONT_TOP = 730
# Rear: the stock bumper's face is at z -1605 at the lamps and -1543 in the
# plate recess, and its bottom edge at the tailgate is y 645. The tailgate
# spare hangs from z -1589 rearward; its underside is at y 547 (33in) to 585
# (stock size) in the middle, 575-617 at |x| 200 and 630+ at |x| 300 (probed
# through the page). The bars used to stand at -1650..-1745 -- 100-140 mm
# proud of the stock line -- and low, under the spare; brought up to the
# tailgate's edge where the real ones are, they would have trapped it (the
# spare swings out with the side-hinged tailgate). So a rear bar's face
# stands at -1565, flush with the stock line: the spare's tread overhangs it,
# as it does in every maker photo. Anything behind z -1585 stays under the
# spare's underside.
REAR_FACE = -1565
REAR_TOP = 645
# where a relocated plate goes on the tailgate (the bars that need
# 'ナンバー移動'): vehicle-left of the spare, clear of its rim
TG_PLATE = (450, 780)
TAILRED = material('TailRed', 0xc0161a, rough=0.18)


def xloft(name, stations, mat, parent=None, r=8, n=3, smooth=True):
    """A bar built from cross-sections standing across the car. Each station
    is (x, ytop, ybot, z0, z1) and gets a rounded rectangle in the Y-Z plane.
    Unlike sweep() nothing turns with the path, so a bar can get shallower,
    shorter or step back toward its ends without its section twisting."""
    bm = bmesh.new()
    rings = []
    for (x, yt, yb, z0, z1) in stations:
        w, h = z1 - z0, yt - yb
        rr = max(0.5, min(r, w / 2 - 0.5, h / 2 - 0.5))
        zc, yc = (z0 + z1) / 2, (yt + yb) / 2
        rings.append([bm.verts.new(P(x, yc + v, zc + u)) for (u, v) in rounded_rect(w, h, rr, n)])
    k = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(k):
            bm.faces.new((r0[j], r0[(j + 1) % k], r1[(j + 1) % k], r1[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return lib.new_object(name, bm, mat, parent, smooth=smooth)


def at_x(st, x, k):
    """Field k of a station list (1 ytop, 2 ybot, 3 z0, 4 z1) at x."""
    for a, b in zip(st, st[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / ((b[0] - a[0]) or 1)
            return a[k] + (b[k] - a[k]) * t
    return st[0][k] if x < st[0][0] else st[-1][k]


def _span_xs(x0, x1, extra=(), n=24):
    xs = {round(x0 + (x1 - x0) * i / n, 2) for i in range(n + 1)}
    xs.update(round(e, 2) for e in extra if x0 <= e <= x1)
    return sorted(xs)


def front_stations(W, ytop, H, D, stand=12, cham=120, dmin=40, rise=0, drop=0, zf=1745, x0=None, x1=None, notch=None):
    """Stations for a front bar that follows the nose (flat across the middle,
    falling away past the headlights) and wraps back at its ends instead of
    stopping square -- 13 of the 35 bars had square-cut ends the real ones
    don't. Over the last `cham` mm the face swings back at 45 degrees and the
    section thins to `dmin`, so the tip finishes just ahead of the wing
    corner. `rise` lifts the lower edge over that run (ends that sweep up),
    `drop` lowers it (end wings taller than the middle), and
    `notch=(half_width, depth)` cuts the lower edge up in the middle.
    Outboard of |x| 520 the back never comes behind z 1545: a 31in tyre's
    leading edge is at 1532 (axle 1139) and a steered one swings in to 520."""
    x0 = -W / 2 if x0 is None else x0
    x1 = W / 2 if x1 is None else x1
    extra = []
    for s in (-1, 1):
        extra += [s * (W / 2 - cham * f) for f in (0, 0.25, 0.5, 0.75, 1.0)]
        if drop:
            extra += [s * (W / 2 - cham - 60)]
        if notch:
            extra += [s * notch[0], s * (notch[0] + 14)]
    out = []
    for x in _span_xs(x0, x1, extra):
        a = abs(x)
        t = max(0.0, a - (W / 2 - cham))
        face = min(zf, nose_z(x) + stand) - t
        back = face - D
        if a > 520:
            back = max(back, 1545)
        face = max(face, back + dmin)
        yb = ytop - H + (rise * t / cham if cham else 0)
        if drop:
            yb -= drop * min(1.0, max(0.0, (a - (W / 2 - cham - 60)) / 60))
        if notch and a <= notch[0] + 7:
            yb += notch[1]
        out.append((x, ytop, yb, back, face))
    return out


def rear_stations(W, ytop, H, D, face=REAR_FACE, wrap=110, dmin=40, rise=0, drop=0, x0=None, x1=None, extra=()):
    """Stations for a rear bar: the face at `face` (a number, or a function of
    x), the ends wrapping FORWARD round the body corners over the last `wrap`
    mm at 45 degrees instead of stopping square. Outboard of |x| 470 nothing
    comes forward of z -1470, which keeps the bar behind the rear tyres (a
    33in tyre's back is at -1466)."""
    x0 = -W / 2 if x0 is None else x0
    x1 = W / 2 if x1 is None else x1
    ex = list(extra)
    for s in (-1, 1):
        ex += [s * (W / 2 - wrap * f) for f in (0, 0.25, 0.5, 0.75, 1.0)]
    out = []
    for x in _span_xs(x0, x1, ex):
        a = abs(x)
        t = max(0.0, a - (W / 2 - wrap))
        f = (face(x) if callable(face) else face) + t
        fwd = f + D
        if a > 470:
            fwd = min(fwd, -1470)
        f = min(f, fwd - dmin)
        k = t / wrap if wrap else 0
        out.append((x, ytop + drop * k, ytop - H + rise * k - drop * k, f, fwd))
    return out


def hung_plate(root, x, y, z, bar_bottom, mat, rear=False):
    """A plate hung off a bar's lower edge on two flat tabs, which is how
    most of these bars carry it (DAMD, OUTCLASS, TOC, Maverick, WMD...)."""
    number_plate(root, y, z, x)
    top = y + 82.5
    lo, hi = top - 40, bar_bottom + 20
    if hi > lo:
        for s in (-1, 1):
            box(f'plateTab{s}', (x + s * 110, (lo + hi) / 2, z + (5 if rear else -5)), (24, hi - lo, 6), mat, root, bevel=1)


def tailgate_plate(root):
    """The plate moved onto the tailgate beside the spare, on a flat bracket
    -- where it goes when a bar has no place for it."""
    x, y = TG_PLATE
    box('plateBracket', (x, y, TAIL_Z - 3), (300, 120, 6), TEXBLACK, root, bevel=1)
    box('plate', (x, y, TAIL_Z - 7.5), (330, 165, 3), PLATE, root, bevel=1)


def frame_walls(name, poly, t, z0, z1, mat, root, back=None):
    """An open box: the walls of a convex (x, y) outline, `t` thick, from z0
    to z1, plus a back plate at `back` if given -- a lamp box that shows what
    is inside it."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    for i, (a, b) in enumerate(zip(poly, poly[1:] + poly[:1])):
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey) or 1
        nx, ny = -ey / L, ex / L
        if nx * (cx - a[0]) + ny * (cy - a[1]) < 0:
            nx, ny = -nx, -ny
        quad = [a, b, (b[0] + nx * t, b[1] + ny * t), (a[0] + nx * t, a[1] + ny * t)]
        slab(f'{name}Wall{i}', quad, z0, z1, mat, root)
    if back is not None:
        slab(f'{name}Back', poly, back - 3, back + 3, mat, root)


def lamp_strip(root, tag, x, y, z, w, h, segs, rear=True):
    """A flat combination lamp: black bezel, lens split across its width into
    (share, material) segments, amber / red / clear as the maker's is."""
    sgn = -1 if rear else 1
    box(f'lampBezel{tag}', (x, y, z + sgn * 2), (w + 16, h + 16, 6), BLACK, root, bevel=3)
    total = sum(s for s, _ in segs)
    u = x - w / 2
    for k, (share, m) in enumerate(segs):
        sw = w * share / total
        box(f'lampSeg{tag}{k}', (u + sw / 2, y, z + sgn * 6), (sw - 3, h, 3), m, root, bevel=1)
        u += sw


def round_lamp(root, tag, x, y, z, dia, lens, dome=True, rear=True):
    sgn = -1 if rear else 1
    lib.cylinder(f'lampCan{tag}', (x, y, z - sgn * 12), (0, 0, 1), dia + 12, 30, TEXBLACK, root, n=22)
    lib.cylinder(f'lampRim{tag}', (x, y, z + sgn * 3), (0, 0, 1), dia + 6, 6, CHROME, root, n=22)
    lib.cylinder(f'lampLens{tag}', (x, y, z + sgn * 6), (0, 0, 1), dia, 4, lens, root, n=22)
    if dome:                                                 # the lenses are domed, not flat
        flatten(lib.sphere(f'lampDome{tag}', (x, y, z + sgn * 6), dia, lens, root), (x, y, z + sgn * 6), 0.3)


def rear_mounts(root, y, z=REAR_FACE, mat=None, x=330):
    for s in (-1, 1):
        box(f'mount{s}', (s * x, y, z + 110), (70, 100, 200), mat or TEXBLACK, root, bevel=4)


def rear_valance(root):
    # closes the gap to the body the stock bumper used to cover
    box('valance', (0, 520, -1430), (1300, 200, 20), RUBBER, root, bevel=4)


def fog_pocket(root, tag, x, y, z, dia, mat=None, w=None, h=None):
    """A stock round fog set into the bar's face in a dark pocket."""
    box(f'fogPocket{tag}', (x, y, z - 2), (w or dia + 36, h or dia + 26, 8), BLACK, root, bevel=6)
    fog_lamp(root, x, y, z - 2, mat or TEXBLACK, dia=dia)


# --------------------------------------------------------------- front bars
def bumper_armando():
    """ARMANDO steel front bar (MRK ID=1542). No maker figures: measured off
    the straight-on photo at 1.29 mm/px (headlamp centres 920 apart; the plate
    agrees). Two tiers -- a 105 mm upper bar whose top meets the grille, with
    a light-bar slot, over a lower tier set back 40 that carries the plate and
    two square LED cubes at +-470 -- 1580 across with the ends chamfered round
    to the arches; a flat trapezoid guard of 60 mm box standing only 60 mm
    above the bar (950 across its feet, 750 across the top); red recovery
    hooks under the face at +-330 and a stepped black plate under the middle."""
    root = group('frontBumper_armando')
    W, top = 1580, FRONT_TOP + 15
    up = front_stations(W, top, 105, 200, cham=130)
    xloft('upper', up, TEXBLACK, root)
    lo = front_stations(W - 120, top - 105, 215, 160, zf=1705, cham=110, rise=30)
    xloft('lower', lo, TEXBLACK, root)
    zf, zl = at_x(up, 0, 4), at_x(lo, 0, 4)
    box('lightSlot', (0, top - 52, zf + 1), (720, 34, 8), RUBBER, root, bevel=3)
    box('lightLens', (0, top - 52, zf + 4), (690, 18, 3), LENS, root, bevel=1)
    g = [(-475, top + 6, 1716), (-375, top + 60, 1716), (375, top + 60, 1716), (475, top + 6, 1716)]
    sweep('guard', [tuple(p) for p in fillet(g, 30, steps=3)], rounded_rect(60, 60, 6, 3), TEXBLACK, root)
    for s in (-1, 1):
        x = s * 470
        z = at_x(lo, x, 4)
        box(f'fogPocket{s}', (x, 610, z - 2), (104, 100, 12), BLACK, root, bevel=6)
        box(f'fogCube{s}', (x, 610, z + 4), (80, 80, 20), BLACK, root, bevel=5)
        box(f'fogLens{s}', (x, 610, z + 15), (64, 64, 3), LENS, root, bevel=2)
        box(f'hook{s}', (s * 330, 400, z - 40), (16, 90, 60), RED, root, bevel=5)
    number_plate(root, 470, zl + 3)
    box('skidStep', (0, 408, zl - 40), (760, 34, 80), TEXBLACK, root, bevel=4)
    box('skid', (0, 360, zl - 110), (700, 6, 150), TEXBLACK, root, bevel=2, rot=Matrix.Rotation(math.radians(-30), 3, 'X'))
    valance(root)
    return root


def bumper_beyond_liberte():
    """Beyond Liberte front bar, a JB64/JB74 common part (MRK ID=2114 and
    Beyond's own kit shots). Beyond publish no dimensions: sized off the
    straight-on night shot at 1.28 mm/px, where the headlamp spacing and the
    330 plate agree. One ~62 mm round tube about 1080 across with flat end
    caps, ending near the headlamps' outer edge; two flat-bar uprights at
    +-350 dropping to a big flat skid plate, a thin cross bar between them,
    round fogs in square stays hung under the tube just outboard of the
    uprights, and the plate standing on the tube's face.

    One node carries all three catalogue finishes: the page swaps
    PowderBlack/TextureBlack for mirror or ivory, so every piece that takes
    the finish (skid included) is TEXBLACK and nothing else is."""
    root = group('frontBumper_beyond_liberte')
    d, y, zt = 62, 675, 1735
    tube('tube', [(-540, y, zt), (540, y, zt)], d, TEXBLACK, root)
    for s in (-1, 1):
        lib.cylinder(f'cap{s}', (s * 541, y, zt), (1, 0, 0), d, 4, TEXBLACK, root, n=24)
        box(f'upright{s}', (s * 350, 590, zt - 6), (12, 136, 50), TEXBLACK, root, bevel=1)
        fx, fy = s * 440, 585
        for (cx, cy, sx, sy) in ((0, 58, 128, 8), (0, -58, 128, 8), (-60, 0, 8, 124), (60, 0, 8, 124)):
            box(f'fogStay{s}{cx}{cy}', (fx + cx, fy + cy, zt + 2), (sx, sy, 30), TEXBLACK, root, bevel=1)
        fog_lamp(root, fx, fy, zt + 12, TEXBLACK, dia=90)
        box(f'plateTab{s}', (s * 110, 640, zt + d / 2 - 3), (24, 90, 8), TEXBLACK, root, bevel=1)
    lib.cylinder('crossBar', (0, 590, zt - 6), (1, 0, 0), 27, 700, TEXBLACK, root, n=16)
    number_plate(root, 620, zt + d / 2 + 3)
    # flat skid, raked: top edge (y 530) forward under the uprights, bottom
    # edge (y 390) 80 mm further back
    box('skid', (0, 460, zt - 40), (840, 6, 161), TEXBLACK, root, bevel=2, rot=Matrix.Rotation(math.radians(-60), 3, 'X'))
    valance(root)
    return root


def bumper_maverick():
    """Maverick DF0001 short steel bar (i-pickup.com.tw; no dimensions
    published). Off the straight-on photo at 1.25 mm/px (headlamp spacing):
    1580 across, 200 tall with its top under the grille, the ends running out
    to the arches and kicking back, their wings 50 mm deeper than the middle;
    four slot vents across the upper face, 75 mm round fogs near the ends at
    +-545, and the plate NOT on the bar but on a separate winch-mount carrier
    under the middle, with red D-shackles either side."""
    root = group('frontBumper_maverick')
    W, top = 1580, FRONT_TOP + 15
    st = front_stations(W, top, 200, 170, cham=140, drop=50)
    xloft('body', st, TEXBLACK, root)
    zf = at_x(st, 0, 4)
    for k, vx in enumerate((-330, -110, 110, 330)):
        box(f'vent{k}', (vx, top - 42, zf + 1), (170, 22, 8), RUBBER, root, bevel=3)
    for s in (-1, 1):
        fog_pocket(root, s, s * 545, 600, at_x(st, s * 545, 4), 75)
        annulus(f'shackle{s}', (s * 330, 520, zf - 30), 14, 26, 22, RED, root, n=24)
        box(f'shackleTab{s}', (s * 330, 548, zf - 40), (12, 40, 60), TEXBLACK, root, bevel=2)
    box('carrier', (0, 470, zf - 70), (440, 200, 120), TEXBLACK, root, bevel=6)
    number_plate(root, 470, zf - 8)
    valance(root)
    return root


def bumper_mrk_abs():
    """MRK short ABS bumper JMY-FB-L (MRK ID=1948; no dimensions published).
    From the fitted 3/4 and the part-only shots: a slim OEM-shaped bar, 190
    tall (twice the stock fog) with its top right under the grille trim,
    1560 across; the END blocks stand 20 mm proud and carry the stock round
    fogs at +-500, the middle is recessed with a centred hex mesh about 780 x
    100, and a flat black steel plate hangs raked under the middle."""
    root = group('frontBumper_mrk_abs')
    W, top, H = 1560, FRONT_TOP + 5, 190
    st = front_stations(W, top, H, 170, stand=4, cham=120)
    xloft('body', st, TEXBLACK, root, r=24)
    zf = at_x(st, 0, 4)
    for s in (-1, 1):
        a, b = (420, W / 2) if s > 0 else (-W / 2, -420)
        blk = front_stations(W, top + 3, H + 6, 70, stand=24, zf=1765, cham=120, x0=a, x1=b)
        xloft(f'endBlock{s}', blk, TEXBLACK, root, r=20)
        fog_pocket(root, s, s * 500, 640, at_x(blk, s * 500, 4), 90)
    box('meshBack', (0, 640, zf + 1), (800, 116, 4), RUBBER, root, bevel=2)
    hex_mesh(root, BLACK, 0, 640, zf + 4, 780, 100, cell=22, bar=2.4)
    number_plate(root, 610, zf + 8)
    box('skid', (0, top - H - 40, zf - 80), (700, 6, 170), BLACK, root, bevel=2, rot=Matrix.Rotation(math.radians(-35), 3, 'X'))
    valance(root)
    return root


def bumper_wmd_winch():
    """WMD-style short winch bar (Ruten listing 22105872751291; the listing
    text gives nothing, so everything is off its small fitted photos with the
    headlamp spacing as the ruler, ~3.2 mm/px -- low confidence). A thin
    folded face plate only 140 tall, its top under the grille, five round
    lightening holes along its lower edge; the winch sits exposed in an
    open-top bay behind it with a small roller fairlead at the top centre and
    a cover plate over the top; no hoop on any photo. The plate hangs below
    the bar, with red D-ring mounts either side."""
    root = group('frontBumper_wmd_winch')
    W, top, H = 1200, FRONT_TOP + 5, 140
    st = front_stations(W, top, H, 34, cham=80, dmin=20)
    xloft('face', st, TEXBLACK, root, r=4)
    zf = at_x(st, 0, 4)
    bot = top - H
    box('floor', (0, bot + 5, (zf + 1560) / 2), (W - 160, 10, zf - 1560), TEXBLACK, root, bevel=2)
    for s in (-1, 1):
        box(f'bayWall{s}', (s * 300, bot + 70, 1640), (8, 130, 150), TEXBLACK, root, bevel=2)
        annulus(f'dring{s}', (s * 300, bot - 22, zf - 30), 14, 25, 20, RED, root, n=24)
        box(f'dringTab{s}', (s * 300, bot - 4, zf - 40), (12, 36, 50), TEXBLACK, root, bevel=2)
    for k in range(5):                                       # lightening holes
        hx = -400 + k * 200
        lib.cylinder(f'hole{k}', (hx, bot + 30, at_x(st, hx, 4) + 1), (0, 0, 1), 46, 4, RUBBER, root, n=20)
    lib.cylinder('winchDrum', (0, 672, 1672), (1, 0, 0), 100, 380, BLACK, root, n=22)
    lib.cylinder('winchMotor', (-265, 672, 1672), (1, 0, 0), 112, 150, BLACK, root, n=22)
    box('winchGear', (265, 672, 1672), (130, 120, 120), BLACK, root, bevel=8)
    box('cover', (0, top + 3, zf - 70), (560, 6, 110), TEXBLACK, root, bevel=2)
    box('fairlead', (0, top - 34, zf + 5), (250, 60, 12), STEEL, root, bevel=6)
    box('fairleadSlot', (0, top - 34, zf + 10), (170, 22, 4), RUBBER, root, bevel=4)
    hung_plate(root, 0, 520, zf + 4, bot, TEXBLACK)
    valance(root)
    return root


def bumper_jaos_cowl():
    """JAOS Front Sport Cowl B040518. JAOS publish 5.05 kg, overall length
    +10 mm and 'within the overall width'; the face is measured off their
    straight-on studio shot at 1.37 mm/px (headlamp spacing; the plate
    agrees): 240 tall with its top under the grille, full width to the
    arches with the lower corners cut up, a recessed dark trapezoid opening
    about 630 x 110 behind the plate between angled ribs, the stock round
    fogs kept in angular pockets at +-590, and a nearly upright silver skid
    about 690 wide under the middle carrying the JAOS lettering."""
    root = group('frontBumper_jaos_cowl')
    W, top, H = 1560, FRONT_TOP - 10, 240
    st = front_stations(W, top, H, 180, stand=10, cham=130, rise=70)
    xloft('body', st, TEXBLACK, root, r=28)
    zf = at_x(st, 0, 4)
    box('opening', (0, 600, zf + 1), (630, 110, 4), BLACK, root, bevel=8)
    for s in (-1, 1):
        box(f'rib{s}', (s * 360, 600, zf + 3), (16, 140, 8), TEXBLACK, root, bevel=3,
            rot=Matrix.Rotation(math.radians(s * 25), 3, 'Y'))
        x = s * 590
        z = at_x(st, x, 4)
        box(f'fogPocket{s}', (x, 575, z - 2), (160, 110, 10), BLACK, root, bevel=8,
            rot=Matrix.Rotation(math.radians(-s * 12), 3, 'Y'))
        fog_lamp(root, x, 575, z - 4, TEXBLACK, dia=90)
    number_plate(root, 565, zf + 5)
    bash = top - H - 36
    box('bash', (0, bash, zf - 25), (690, 80, 6), ALU, root, bevel=2, rot=Matrix.Rotation(math.radians(10), 3, 'X'))
    text('badge', 'JAOS', (0, bash, zf - 19), 40, 3, TEXBLACK, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    valance(root)
    return root


def bumper_klc_short():
    """KLC Heritage Front Short Bumper 74 (klc-div.com; KLC publish no
    sizes). Off their 3/4 shots with the plate and headlamp glass as rulers:
    a slim OEM-shaped ABS bar 185 tall (twice the stock fog), its top under
    the grille trim in every photo, 1580 across with OEM-shaped end blocks
    standing a little proud and carrying the stock fogs at +-560; a fine
    silver mesh opening across the middle, a dark panel under it, and the
    plate offset 150 to the car's left, half hanging off the lower edge.
    (The 'KLC' in the photos is their demo plate, not on the bumper.)"""
    root = group('frontBumper_klc_short')
    W, top, H = 1580, FRONT_TOP + 3, 185
    st = front_stations(W, top, H, 170, stand=4, cham=120)
    xloft('body', st, TEXBLACK, root, r=24)
    zf = at_x(st, 0, 4)
    for s in (-1, 1):
        a, b = (470, W / 2) if s > 0 else (-W / 2, -470)
        blk = front_stations(W, top + 2, H + 4, 70, stand=16, zf=1757, cham=120, x0=a, x1=b)
        xloft(f'endBlock{s}', blk, TEXBLACK, root, r=20)
        fog_pocket(root, s, s * 560, 640, at_x(blk, s * 560, 4), 90)
    box('meshBack', (0, 650, zf + 1), (730, 116, 4), RUBBER, root, bevel=2)
    wire_mesh(root, ALU, 0, 650, zf + 4, 700, 96, pitch=10, bar=1.8)
    hung_plate(root, -RIGHT * 150, 560, zf + 6, top - H, TEXBLACK)
    box('lowerPanel', (0, top - H - 30, zf - 60), (720, 6, 150), TEXBLACK, root, bevel=2, rot=Matrix.Rotation(math.radians(-40), 3, 'X'))
    valance(root)
    return root


def bumper_toc_extreme():
    """TOC BODYWORKS Extreme Bumper 74, FRP (tocbw.thebase.in; no dimensions
    published). Off the straight-on photo with the headlamp centres (920) and
    the flare width (1645) as rulers: 210 tall with its top tight under the
    grille, block ends that run right up to the fronts of the over-fenders,
    a row of nine 40 mm round holes across the upper face, the stock fogs in
    small rectangular pockets at +-575, the middle 700 of the lower edge
    notched up 60 for an LED bar (not included), and the plate hung below
    the middle (TOC hang it on their skid plate, also not included)."""
    root = group('frontBumper_toc_extreme')
    W, top, H = 1560, FRONT_TOP, 210
    st = front_stations(W, top, H, 200, cham=70, notch=(350, 60))
    xloft('body', st, TEXBLACK, root)
    zf = at_x(st, 0, 4)
    for k in range(9):
        hx = -440 + k * 110
        lib.cylinder(f'hole{k}', (hx, 660, at_x(st, hx, 4) + 1), (0, 0, 1), 40, 4, RUBBER, root, n=20)
    for s in (-1, 1):
        fog_pocket(root, s, s * 575, 590, at_x(st, s * 575, 4), 70, w=130, h=90)
    hung_plate(root, 0, 470, zf - 6, top - H + 60, TEXBLACK)
    valance(root)
    return root


def bumper_taniguchi_square():
    """TANIGUCHI square front bar (ors-taniguchi.co.jp: 2 mm sheet, about
    3 kg, stock fogs relocatable, bolts to TANIGUCHI's own skid plate stays
    and cannot be fitted without it). A short folded-plate bar, not a tube:
    off one 3/4 photo with the plate and headlamp spacing as rulers, 145
    tall, 130 deep, only as wide as the headlamps' outer edges (1230), its
    last 100 mm chamfered back, the stock round fogs recessed at +-400; the
    silver skid plate it needs is drawn under it."""
    root = group('frontBumper_taniguchi_square')
    W, top, H = 1230, 690, 145
    st = front_stations(W, top, H, 130, cham=100)
    xloft('body', st, TEXBLACK, root, r=5)
    zf = at_x(st, 0, 4)
    for s in (-1, 1):
        fog_pocket(root, s, s * 400, 615, at_x(st, s * 400, 4), 70)
    number_plate(root, 615, zf + 4)
    box('skid', (0, 500, zf - 70), (760, 6, 200), ALU, root, bevel=2, rot=Matrix.Rotation(math.radians(-40), 3, 'X'))
    valance(root)
    return root


def bumper_taniguchi_double():
    """TANIGUCHI double-tube front bar (ors-taniguchi.co.jp: 'the middle is a
    double tube, the sides are boxes that take the stock fog lamps', tube
    48.6 x 2.3, about 9 kg). Off the maker's 3/4 photo (plate = 330): the two
    tubes run only between the frame rails (+-450), at y 660 and 570; each
    side is a square box about 300 x 145 x 130, its top level with the upper
    tube, its outer end chamfered back toward the wing, a stock round fog in
    its face at +-600. The plate stands on tabs in front of the tubes."""
    root = group('frontBumper_taniguchi_double')
    W, d, yu, yl = 1470, 48.6, 660, 570
    top = yu + d / 2
    zt = 1745 - d / 2 - 6
    tube('upper', [(-450, yu, zt), (450, yu, zt)], d, TEXBLACK, root)
    tube('lower', [(-450, yl, zt), (450, yl, zt)], d, TEXBLACK, root)
    for s in (-1, 1):
        tube(f'link{s}', [(s * 300, yl, zt), (s * 300, yu, zt)], 30, TEXBLACK, root)
        a, b = (435, W / 2) if s > 0 else (-W / 2, -435)
        st = front_stations(W, top, 145, 130, cham=110, x0=a, x1=b)
        xloft(f'endBox{s}', st, TEXBLACK, root, r=5)
        fog_pocket(root, s, s * 600, 600, at_x(st, s * 600, 4), 70)
        box(f'plateTab{s}', (s * 110, 615, zt + d / 2), (24, 110, 8), TEXBLACK, root, bevel=1)
    number_plate(root, 615, zt + d / 2 + 5)
    valance(root)
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
    """JIMNY the ROOTS.: a body-colour panel whose opening is three rows of
    horizontal slots, chrome SUZUKI lettering on the band between the top two,
    and a small round amber marker outboard of each headlight."""
    root = group('grille_damd_roots')
    ow, oh = 600, 170
    grille_panel('panel', root, PAINT, (ow, oh, 848))
    lamp_bezels(root, PAINT, 'round')
    z = face_z(0)
    wire_mesh(root, BLACK, 0, 848, z - 16, ow - 10, oh - 10, pitch=9)
    box('backing', (0, 848, z - 28), (ow, oh, 3), RUBBER, root, bevel=0)
    # three rows of horizontal slots (DAMD's photos), the chrome SUZUKI
    # letters sitting on the wide band between the first and second rows
    box('frameTop', (0, 848 + oh / 2 + 8, z + 2), (ow + 16, 22, 20), PAINT, root, bevel=4)
    box('frameBot', (0, 848 - oh / 2 - 8, z + 2), (ow + 16, 22, 20), PAINT, root, bevel=4)
    box('bandLetters', (0, 848 + oh / 6, z + 2), (ow - 6, 44, 20), PAINT, root, bevel=4)
    box('bandLow', (0, 848 - oh / 6 - 6, z + 2), (ow - 6, 18, 20), PAINT, root, bevel=4)
    text('suzuki', 'SUZUKI', (0, 848 + oh / 6, z + 14), 38, 5, CHROME_TRIM, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    for s in (-1, 1):
        lib.cylinder(f'mk{s}', (s * 612, 906, face_z(612) + 8), (0, 0, 1), 52, 24, PAINT, root, n=20)
        lib.cylinder(f'mkLens{s}', (s * 612, 906, face_z(612) + 22), (0, 0, 1), 42, 4, AMBER, root, n=20)
    return root


def bumper_damd_little_d():
    """little D. front, measured off DAMD's straight-on product shot with the
    headlamp (180) as the ruler, the grille's lower edge (y 735) checking it:
    1510 across, a 170 mm flat central face (y 544-714) under a 16 mm top
    deck that ends at the grille (730), carrying the stock round fogs at
    +-473 and a 734 x 72 mesh slot; gunmetal end blocks about 180 wide in
    front view whose backs are chamfered 45 deg round to the wing corners;
    the plate hung off the face's lower edge over the top half of a 976 x
    175 gunmetal skid with pressed teardrop dimples. Coarse matte black on
    the deck and the central face."""
    root = group('frontBumper_damd_little_d')
    gun = material('DamdGunmetal', 0x4a4d52, rough=0.5, metal=0.6)
    W, ytop, H = 1510, 714, 170
    y, zf = ytop - H / 2, 1772
    inner = W / 2 - 180                                      # where the end blocks start
    box('face', (0, y, zf - 60), (inner * 2, H, 120), TEXBLACK, root, bevel=5)
    box('deck', (0, ytop + 8, zf - 70), (inner * 2, 16, 140), TEXBLACK, root, bevel=4)
    box('slotFrame', (0, 640, zf - 2), (734, 72, 14), TEXBLACK, root, bevel=3)
    wire_mesh(root, BLACK, 0, 640, zf - 14, 720, 60, pitch=11)
    for k in (-1, 0, 1):
        box(f'slotRib{k}', (k * 180, 640, zf - 4), (14, 64, 12), TEXBLACK, root, bevel=2)
    for s in (-1, 1):
        fog_lamp(root, s * 473, 645, zf + 2, TEXBLACK, dia=90)
        a, b = (inner - 2, W / 2) if s > 0 else (-W / 2, -inner + 2)
        es = front_stations(W, ytop + 16, H + 16, 130, stand=60, cham=160, zf=zf, x0=a, x1=b)
        xloft(f'endBlock{s}', es, gun, root, r=6)
    number_plate(root, 482, zf + 6)
    # skid, raked 62 deg: its top edge meets the face's lower edge at the front
    skid = box('skid', (0, 457, zf - 66), (976, 8, 198), gun, root, bevel=4,
               rot=Matrix.Rotation(math.radians(-62), 3, 'X'))
    for k in range(7):                                       # shallow pressed teardrops, below the plate
        sx = -420 + k * 140
        lib.cylinder(f'dimple{k}', (sx, 420, zf - 79), (0, -0.469, 0.883), 38, 4, gun, root, n=18)
    valance(root, corners=False)
    return root


def rear_damd_little_d():
    """little D. rear, measured off DAMD's straight-on shot (74littleD_REAR,
    plate 330 = 130 px; DAMD quote 1656 full width, about 1615 straight on):
    an upper beam 180 tall right under the tailgate swelling into end blocks
    about 490 wide that wrap forward round the corners, and a lower beam only
    1040 wide (between the mud flaps), 86 tall, set back directly under it.
    The stock lamps go; the kit's own domed round lamps take over, three a
    side plus a flat reflector, all wired into the original harness. The
    plate sits on a step in the middle (DAMD's own shot shows it moved to
    the tailgate, a separate kit). Coarse matte black."""
    root = group('rearBumper_damd_little_d_rear')
    amber = material('AmberLens', 0xe08a1e, rough=0.15)
    red = TAILRED
    W, ytop, HB = 1615, REAR_TOP, 180
    zf = REAR_FACE
    inner = W / 2 - 490
    xloft('upper', rear_stations(W, ytop, HB, 110, face=zf + 12, x0=-inner - 2, x1=inner + 2), TEXBLACK, root, r=6)
    blocks = {}
    for s in (-1, 1):
        a, b = (inner, W / 2) if s > 0 else (-W / 2, -inner)
        blocks[s] = rear_stations(W, ytop, HB, 140, wrap=140, x0=a, x1=b)
        xloft(f'endBlock{s}', blocks[s], TEXBLACK, root, r=8)
    xloft('lower', rear_stations(1040, ytop - HB, 86, 100, face=zf + 30, wrap=0), TEXBLACK, root, r=6)
    for s in (-1, 1):
        # the kit's own lamps: domed lenses, amber over red on a shallow
        # diagonal, clear reverse out at the corner, flat reflector below
        k = W / 1656.0                                       # the quoted x's are for DAMD's 1656 bar
        for (dx, yy, dia, mat_, dome) in ((703 * k, 573, 64, amber, True), (613 * k, 546, 64, red, True),
                                          (757 * k, 492, 58, LENS, True), (453 * k, 430, 57, red, False)):
            z = at_x(blocks[s], s * dx, 3) if dx > inner else zf + 30
            round_lamp(root, f'{s}{int(dx)}', s * dx, yy, z, dia, mat_, dome=dome)
        box(f'rubber{s}', (s * (W / 2 - 60), ytop - HB / 2, at_x(blocks[s], s * (W / 2 - 60), 3) - 3), (40, HB - 30, 6), RUBBER, root, bevel=2)
    rear_mounts(root, ytop - 60)
    box('plateStep', (0, 520, zf + 12 - 4), (420, 190, 8), TEXBLACK, root, bevel=4)
    box('plate', (RIGHT * 60, 520, zf + 12 - 9.5), (330, 165, 3), PLATE, root, bevel=1)
    for s in (-1, 1):
        lib.cylinder(f'plateLamp{s}', (RIGHT * 60 + s * 120, 612, zf + 12 - 12), (0, 0, 1), 26, 8, CHROME, root, n=14)
    rear_valance(root)
    return root


def bumper_damd_little_g_trad():
    """little G. TRADITIONAL front, off DAMD's fitted front photo with the
    headlamp (180) as the ruler, +-30 mm; DAMD publish no sizes. A flat steel
    beam 1600 across -- almost to the arches, its ends wrapping back -- 215
    tall with its top under the grille, a band of close vertical ribbing
    across the upper face, a chrome-framed amber Koito SQUARE fog set into
    the upper face at each end (+-538), a mesh slot in the middle below the
    ribbing, and the plate hung off-centre from the lower edge."""
    root = group('frontBumper_damd_little_g_trad')
    W, ytop, H, D = 1600, 713, 215, 140
    st = front_stations(W, ytop, H, D, cham=130)
    xloft('body', st, TEXBLACK, root)
    for s in (-1, 1):
        x = s * 538
        z = at_x(st, x, 4)
        box(f'fogHsg{s}', (x, 668, z - 6), (160, 90, 30), CHROME_TRIM, root, bevel=8)
        box(f'fogLens{s}', (x, 668, z + 10), (134, 70, 5), AMBER, root, bevel=4)
        lib.cylinder(f'fogLogo{s}', (x, 668, z + 13), (0, 0, 1), 30, 3, CHROME_TRIM, root, n=20)
    for k in range(19):                                      # washboard ribbing across the face
        bx = -405 + k * 45
        box(f'ribV{k}', (bx, 650, at_x(st, bx, 4) + 2), (12, 90, 10), TEXBLACK, root, bevel=2)
    zf = at_x(st, 0, 4)
    box('meshBack', (0, 575, zf + 1), (340, 74, 4), RUBBER, root, bevel=2)
    wire_mesh(root, BLACK, 0, 575, zf + 4, 326, 62, pitch=11)
    number_plate(root, 466, at_x(st, RIGHT * 425, 4) + 5, RIGHT * 425)
    valance(root, corners=False)
    return root


def rear_damd_little_g_trad():
    """DAMD little G. TRADITIONAL rear bar, from the fitting instructions and
    DAMD's straight-on shot (74-TRA-REAR-2, plate = 139 px): 1650 mm along
    the wrap, about 1570 straight on, 225 tall right under the tailgate, its
    ends wrapping forward onto the flare corners (black side returns in
    DAMD's shot); matte black on every exposed face and piano black in the
    recesses, carrying the kit's own truck-style lamp each side (DAMD part
    E-476) at +-526, 102 below the top. The lens is 215 x 68 and reads,
    outboard to inboard: amber indicator, a plain red reflector, a red
    stop/tail, then a slightly proud clear reverse. Plate centred, its top
    118 below the bar's, hanging below the bar."""
    root = group('rearBumper_damd_little_g_trad_rear')
    piano = material('PianoBlack', 0x141416, rough=0.12, metal=0.25)
    W, ytop, H = 1570, REAR_TOP, 225
    zf = REAR_FACE
    st = rear_stations(W, ytop, H, 150, wrap=130)
    xloft('body', st, TEXBLACK, root, r=10)
    box('ripple', (0, ytop - 26, zf - 3), (W - 300, 44, 6), piano, root, bevel=3)
    for s in (-1, 1):
        ly, lx = ytop - 102, 526
        box(f'recess{s}', (s * lx, ly, zf - 3), (345, 107, 6), piano, root, bevel=4)
        box(f'bezel{s}', (s * lx, ly, zf - 8), (280, 100, 6), TEXBLACK, root, bevel=5)
        box(f'lens{s}', (s * lx, ly, zf - 12), (215, 68, 4), TEXBLACK, root, bevel=2)
        segs = ((77.5, 60, AMBER), (22.8, 49, TAILRED), (-26.8, 49, TAILRED), (-79.5, 56, LENS))
        for k, (dx, w, m) in enumerate(segs):
            lib.cylinder(f'seg{s}{k}', (s * (lx + dx), ly, zf - 15 - (2 if k == 3 else 0)), (0, 0, 1),
                         min(w - 4, 58), 4, m, root, n=22)
        for (bx, by) in ((lx + 107, 0), (lx, 44), (lx, -44)):  # the lens screws
            lib.cylinder(f'screw{s}{bx}{by}', (s * bx, ly + by, zf - 16), (0, 0, 1), 9, 4, STEEL, root, n=6)
    rear_mounts(root, ytop - 80)
    py = ytop - 118 - 82.5
    box('plateStep', (0, py, zf - 3), (400, 200, 6), piano, root, bevel=3)
    box('plate', (0, py, zf - 7.5), (330, 165, 3), PLATE, root, bevel=1)
    rear_valance(root)
    return root


def bumper_damd_roots():
    """JIMNY the ROOTS. front, off DAMD's straight-on shot with the plate
    (330) as the ruler, +-25 mm: two layers -- an ivory pressed-steel beam
    1400 across and 142 tall under the grille, its ends wrapping back along
    the wings and tapering to a point with the lower edge rising, pierced by
    two rows of three long slots in the middle; over a black lower valance
    about 1015 wide that narrows downward, carrying the plate in the centre
    and a 100 mm chrome round fog each side at +-432."""
    root = group('frontBumper_damd_roots')
    W, ytop, H, D = 1400, 716, 142, 110
    st = front_stations(W, ytop, H, D, stand=10, cham=170, rise=70, dmin=24)
    xloft('beam', st, IVORY, root, r=8)
    for yy in (665, 625):                                    # two rows of long pressed slots
        for (cx, w) in ((-262, 200), (0, 300), (262, 200)):
            box(f'slot{yy}{cx}', (cx, yy, at_x(st, cx, 4) + 1), (w, 25, 8), RUBBER, root, bevel=4)
    zv = at_x(st, 0, 4) - 30                                 # valance face, set back
    slab('valance', [(-507, 573), (507, 573), (450, 366), (-450, 366)], zv - 100, zv, TEXBLACK, root)
    number_plate(root, 508, zv + 2)
    for s in (-1, 1):
        fog_lamp(root, s * 432, 503, zv + 4, CHROME_TRIM, dia=100)
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
    """SALADO front bumper (UN-JIMNY-FB-001), drawn 1426 x 670 (42.8 kg);
    every size below is measured off that drawing with 1426 as the scale
    (+-15 mm): a 155 mm winch bar 1426 across with its ends wrapped back, a
    grille guard loop 1395 wide of 42 mm tube whose lower run sits right on
    the bar and whose top is 295 above the bar face, two inner uprights at
    +-352, a recessed 277 x 128 light pocket at each end (+-573) holding a
    small square mesh-guarded lamp, and a 705 wide winch box hanging 210
    below the bar with a hawse fairlead and a bolted skid. The fitted height
    is not drawn; the bar's top (678) puts the guard's lower run against
    the grille's bottom edge, as on the 1970 bar from the same maker."""
    root = group('frontBumper_urnieta_salado')
    W, y, zf, D, H = 1426, 600, 1768, 168, 155
    top, bot = y + H / 2, y - H / 2
    st = front_stations(W, top, H, D, stand=16, cham=110, zf=zf)
    xloft('body', st, TEXBLACK, root, r=16)
    for s in (-1, 1):
        px = s * 573
        pz = at_x(st, px, 4)
        box(f'pocket{s}', (px, y, pz - 2), (277, 128, 8), BLACK, root, bevel=9)
        box(f'lampBody{s}', (px, y, pz + 4), (112, 94, 16), BLACK, root, bevel=6)
        box(f'lens{s}', (px, y, pz + 12), (100, 82, 3), LENS, root, bevel=3)
        wire_mesh(root, TEXBLACK, px, y, pz + 16, 100, 82, pitch=12, bar=3)
        box(f'postFoot{s}', (s * 352, top + 12, 1732), (62, 24, 62), TEXBLACK, root, bevel=4)
    # the grille guard: a closed loop in front of the grille, its legs just
    # outboard of the headlamps and swept back toward the wing; only the two
    # inner uprights run down onto the bar
    gx, gtop, gbot, hz, hzl = 676, 952, top + 21, 1734, 1650
    loop = [(0, gbot, hz), (420, gbot, hz), (gx, gbot, hzl), (gx, gtop, hzl), (420, gtop, hz),
            (-420, gtop, hz), (-gx, gtop, hzl), (-gx, gbot, hzl), (-420, gbot, hz), (0, gbot, hz)]
    tube('guard', loop, 42, TEXBLACK, root, bend=92)
    for s in (-1, 1):
        px2 = s * 352
        tube(f'upright{s}', [(px2, top + 10, hz + 16), (px2, gtop + 4, hz + 16)], 42, TEXBLACK, root)
        for yy in (gtop - 14, gbot + 14):
            box(f'clamp{s}{yy}', (px2, yy, hz + 8), (54, 40, 44), TEXBLACK, root, bevel=5)
    text('salado', 'Salado', (-290, bot + 24, zf + 2), 40, 4, UNT_TEXT, root)
    text('unt', 'URNIETA', (290, top - 26, zf + 2), 24, 3, UNT_TEXT, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    for k in range(6):                                       # bolt heads along the top
        lib.cylinder(f'wbolt{k}', (-250 + k * 100, top + 2, zf - 40), (0, 1, 0), 15, 8, STEEL, root, n=6)
    number_plate(root, y - 4, zf + 6)
    # winch box hanging 210 below the bar, fairlead and skid
    wy = bot - 105
    box('winchBox', (0, wy, zf - 120), (705, 210, 200), TEXBLACK, root, bevel=6)
    box('fairlead', (0, wy + 10, zf - 14), (240, 70, 16), STEEL, root, bevel=14)
    box('hawse', (0, wy + 10, zf - 8), (150, 32, 10), RUBBER, root, bevel=8)
    for s in (-1, 1):
        box(f'ledBar{s}', (s * 250, wy + 64, zf - 16), (150, 34, 20), BLACK, root, bevel=5)
        box(f'ledLens{s}', (s * 250, wy + 64, zf - 5), (128, 18, 4), LENS, root, bevel=2)
        box(f'shackle{s}', (s * 250, wy - 50, zf - 14), (44, 82, 40), STEEL, root, bevel=8)
    box('skid', (0, wy - 120, zf - 150), (760, 8, 260), STEEL, root, bevel=3,
        rot=Matrix.Rotation(math.radians(-26), 3, 'X'))
    valance(root, corners=False)
    return root


def rear_urnieta_salado():
    """SALADO rear bumper (UN-JIMNY-FB-002), 16.4 kg. The drawing's 1816 is
    the developed length and its 216 includes the plate panel; scaling it by
    its own 216 mark gives about 1600 straight on and a 150 mm face, and the
    fitted photo agrees (bar about body width, top at the tailgate's bottom
    edge). The ends wrap forward onto the flare corners as 165 mm blocks; a
    230 x 90 lamp frame each side at +-560, 84 below the top; a PIAA
    rectangular lamp inboard on the vehicle-left side only and the URNIETA
    oval badge on the vehicle-right; the Salado script on the left lamp's
    top frame; a 455 x 165 plate panel hanging 65 below the bar. No steps --
    the drawing and the photos show mounting brackets there."""
    root = group('rearBumper_urnieta_salado_rear')
    W, ytop, H = 1600, REAR_TOP, 150
    zf = REAR_FACE
    st = rear_stations(W, ytop, H, 150, wrap=120, drop=15)
    xloft('body', st, TEXBLACK, root, r=14)
    ly = ytop - 84
    for s in (-1, 1):
        x = s * 560
        box(f'window{s}', (x, ly, zf - 3), (230, 90, 6), BLACK, root, bevel=8)
        box(f'lens{s}', (x, ly, zf - 7), (200, 56, 4), TAILRED, root, bevel=4)
    xl = -RIGHT                                              # vehicle left
    box('aux', (xl * 367, ly, zf - 3), (150, 60, 6), BLACK, root, bevel=5)
    box('auxLens', (xl * 367, ly, zf - 7), (130, 40, 3), LENS, root, bevel=3)
    box('badge', (RIGHT * 363, ly, zf - 3), (130, 34, 5), UNT_TEXT, root, bevel=14)
    sc = text('salado', 'Salado', (xl * 560, ly + 56, zf - 3), 24, 3, UNT_TEXT, root)
    sc.rotation_euler = (0, 0, math.pi)                      # reads from behind
    box('platePanel', (0, ytop - 216 + 82.5, zf - 4), (455, 165, 8), TEXBLACK, root, bevel=5)
    box('plate', (0, ytop - 216 + 82.5, zf - 9.5), (330, 165, 3), PLATE, root, bevel=1)
    rear_mounts(root, ytop - 60)
    rear_valance(root)
    return root


def bumper_urnieta_1970():
    """1970 front bumper (UN-JIMNY-FB-027), drawn 1547 x 331, 21 kg: a slim
    beam 1547 across -- flush with the arches -- whose ends sweep back into
    winged corners with three vent slots each, a louvred centre panel 935
    wide carrying URNIETA and a 1970 SERIES badge, a lamp bracket each side
    at +-382, and a flat lower panel about 770 x 220 with two tow shackles at
    +-330 and the plate on it. W and the 331 overall are the drawing's; the
    rest is off the straight-on product photo scaled by 1547 (+-20 mm), and
    the fitted height off the fitted photo (headlamp 180 as the ruler): the
    beam's top meets the grille's bottom edge."""
    root = group('frontBumper_urnieta_1970')
    W, y, zf, D, H = 1547, 650, 1762, 118, 125
    top, bot = y + H / 2, y - H / 2
    st = front_stations(W, top, H, D, stand=10, cham=150, drop=20, zf=zf)
    xloft('body', st, TEXBLACK, root, r=12)
    box('centre', (0, y, zf - 6), (935, H - 20, 20), TEXBLACK, root, bevel=5)
    for k in range(6):                                       # louvres across the centre panel
        box(f'louvre{k}', (0, y - 34 + k * 14, zf + 6), (220, 6, 9), TEXBLACK, root, bevel=1)
    box('badge1970', (200, y - 4, zf + 10), (150, 70, 8), TEXBLACK, root, bevel=6)
    text('n1970', '1970', (200, y + 4, zf + 15), 38, 4, UNT_TEXT, root,
         font='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    box('unt', (-200, y + 2, zf + 12), (104, 22, 6), UNT_TEXT, root, bevel=1)
    for s in (-1, 1):
        box(f'lampBrk{s}', (s * 382, y + 2, zf + 8), (145, 55, 12), TEXBLACK, root, bevel=4)
        box(f'piaa{s}', (s * 382, y + 2, zf + 15), (118, 32, 8), BLACK, root, bevel=3)
        box(f'piaaLens{s}', (s * 382, y + 2, zf + 19), (100, 22, 4), LENS, root, bevel=2)
        for k in range(3):                                   # vent slots in the winged end
            vx = s * (W / 2 - 100)
            box(f'vent{s}{k}', (vx, y - 20 + k * 26, at_x(st, vx, 4) + 1), (70, 12, 8), RUBBER, root, bevel=2)
        box(f'shackle{s}', (s * 330, bot - 150, zf - 22), (54, 92, 46), STEEL, root, bevel=8)
        lib.cylinder(f'shacklePin{s}', (s * 330, bot - 134, zf - 22), (1, 0, 0), 20, 66, STEEL, root, n=12)
    box('lowerPanel', (0, bot - 110, zf - 40), (770, 220, 14), TEXBLACK, root, bevel=4)
    box('plate', (0, 497, zf - 31.5), (330, 165, 3), PLATE, root, bevel=1)
    valance(root, corners=False)
    return root


def rear_urnieta_1970():
    """1970 rear bumper (UN-JIMNY-FB-028), drawn 1617 x 265, 8.4 kg; the 265
    includes the plate bracket. Off the MRK product photos (ID=2219) with the
    plate as the ruler: about 1600 straight on, a 150 mm face whose top
    reaches the tailgate's bottom edge (no separate top rail), ends wrapped
    forward, and the line's signature round lamps -- 62 mm lenses in 76 mm
    bezels, AMBER outboard, red inboard -- then inboard of them a PIAA
    rectangular lamp on the vehicle-left and a louvred vent carrying the
    URNIETA badge on the vehicle-right. The plate hangs on a bracket below
    the bar. Mud flaps, not steps, under the ends."""
    root = group('rearBumper_urnieta_1970_rear')
    W, ytop, H = 1600, REAR_TOP, 150
    zf = REAR_FACE
    st = rear_stations(W, ytop, H, 128, wrap=100)
    xloft('body', st, TEXBLACK, root, r=14)
    y = ytop - H / 2
    for s in (-1, 1):
        for k, (dx, m) in enumerate(((W / 2 - 110, AMBER), (W / 2 - 230, TAILRED))):
            round_lamp(root, f'{s}{k}', s * dx, y + 6, at_x(st, s * dx, 3), 62, m)
    xl = -RIGHT                                              # vehicle left
    box('piaa', (xl * 420, y + 6, zf - 3), (160, 55, 6), BLACK, root, bevel=4)
    box('piaaLens', (xl * 420, y + 6, zf - 7), (140, 36, 3), LENS, root, bevel=3)
    box('vent', (RIGHT * 420, y + 6, zf - 3), (160, 60, 6), BLACK, root, bevel=4)
    for k in range(4):
        box(f'louvre{k}', (RIGHT * 420, y - 15 + k * 12, zf - 7), (150, 4, 3), TEXBLACK, root, bevel=0.5)
    box('badgeText', (RIGHT * 420, y + 6, zf - 9), (110, 18, 3), UNT_TEXT, root, bevel=1)
    hung_plate(root, 0, 440, zf - 3, ytop - H, TEXBLACK, rear=True)
    rear_mounts(root, ytop - 60)
    rear_valance(root)
    return root


def side_bar_urnieta_salado():
    """SALADO Side Bar Kit (UN-JIMNY-FB-009), drawn 1270 x 460 for the three
    door. From the fitted photos it is a big single tube along the sill whose
    ends sweep up toward the body, with a long grippy step strip bonded along
    its top (URNIETA printed on it, a Salado badge near the rear) and tubular
    arms back to the chassis -- not a chequer-plate step."""
    root = group('sideStep_urnieta_salado')
    z0, z1, ty = -555, 640, 330      # the front kick-up clears a 225/75R16 (its back edge z 767)
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
    # between the arches: the front one opens at z 700 (and a 31in tyre's
    # back is at 746), the rear at -610 -- the drawn 833 put the front tail
    # 48 mm into the tyre
    z0, z1, ty = -560, 680, 338
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
        # 20 mm higher than first drawn: at deck - 34 the bar's underside
        # (1607) ran 15 mm into the roof's crown (1622)
        sweep(f'bar{zz}', [(-660, deck - 14, zz), (660, deck - 14, zz)], rounded_rect(70, 26, 6), BLACK, root)
        for s in (-1, 1):
            # TERZO foot: pad, clamp and tower (was a plain box)
            gutter_leg(root, f'foot{s}{zz}', s, zz, 636, deck - 27, 'tower', 52)
            box(f'barCap{s}{zz}', (s * 662, deck - 14, zz), (8, 30, 74), TEXBLACK, root, bevel=3)
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


def rear_damd_roots():
    """JIMNY the ROOTS. rear bumper + extension (DAMD publish no sizes; off
    their straight-on photo, plate 330 = 137 px): a slim ivory beam 1460
    across and 125 tall right up under the tailgate, ends cut square with
    black corner pieces behind them, two small round lamps a side (amber
    outboard at +-630, red at +-525), and a black extension panel 1085 x 140
    set back under the beam carrying the plate and a small red reflector
    each side -- the extension is half of what the catalogue entry sells."""
    root = group('rearBumper_damd_roots_rear')
    W, top, H = 1460, REAR_TOP, 125
    zf = REAR_FACE
    st = rear_stations(W, top, H, 110, wrap=0)
    xloft('beam', st, IVORY, root, r=8)
    for s in (-1, 1):
        box(f'corner{s}', (s * (W / 2 - 12), top - 70, -1522), (60, 150, 96), TEXBLACK, root, bevel=6)
        round_lamp(root, f'{s}a', s * 630, top - H / 2, zf, 55, AMBER)
        round_lamp(root, f'{s}r', s * 525, top - H / 2, zf, 55, TAILRED)
        box(f'reflector{s}', (s * 450, 440, zf + 21), (70, 24, 4), TAILRED, root, bevel=1)
    box('extension', (0, 435, zf + 25 + 30), (1085, 140, 60), TEXBLACK, root, bevel=5)
    number_plate(root, 440, zf + 23.5)
    rear_mounts(root, top - 60)
    rear_valance(root)
    return root


def rear_klc_heritage():
    """KLC Heritage Traditional rear bar (klc-div.com traditionalbumperrear_2_bk;
    KLC publish no sizes or tube diameter). Off KLC's straight-on close-up
    with the plate as the ruler (0.817 mm/px): the ends are closed trapezoid
    boxes about 425 x 170 that enclose the car's own tail lamps (outer edge
    +-720), and one fat round tube, about 90, runs only between them with its
    top level with theirs; the plate hangs on two tabs under the tube and a
    flat strap runs down from each box to the chassis. The tube stands 35 mm
    forward of the boxes' rims: level with them its top (y 620) would sit
    inside the tailgate spare's underside."""
    root = group('rearBumper_klc_heritage_rear')
    d, yt, top = 90, 575, 620
    zt = -1580 + d / 2
    tube('bar', [(-305, yt, zt), (305, yt, zt)], d, TEXBLACK, root)
    for s in (-1, 1):
        poly = [(305, top), (720, top), (720, 540), (650, 452), (305, 452)]
        poly = [(s * x, y) for (x, y) in poly]
        frame_walls(f'lampBox{s}', poly, 8, -1614, -1546, TEXBLACK, root, back=-1546)
        box(f'strap{s}', (s * 420, 400, -1556), (50, 110, 8), TEXBLACK, root, bevel=1)
        box(f'mount{s}', (s * 250, yt, zt + 100), (70, 90, 150), TEXBLACK, root, bevel=4)
        box(f'plateTab{s}', (s * 110, yt - d / 2 - 30, zt - d / 2 + 14), (24, 80, 24), TEXBLACK, root, bevel=1)
    number_plate(root, yt - d / 2 - 12 - 82.5, zt - d / 2 + 0.5)
    return root


def rear_beyond():
    """Beyond Liberte rear bar (MRK ID=2112; Beyond publish no sizes): off
    MRK's photos with the plate as the ruler. One 60 mm round tube about
    1500 across that dips 115 mm through the middle on 45-degree bends to
    carry the plate on two tabs below it, and an open square box hung under
    each outer run holding a truck combination lamp (amber / red / clear):
    the bar brings its own lamps. The dip keeps the tube under the spare, so
    it can stand 35 mm behind the stock line as the real one does.
    One node for all three finishes -- TEXBLACK is what the page swaps."""
    root = group('rearBumper_beyond_rear')
    d, yo, yc, z = 60, 605, 490, -1600
    tube('bar', [(-750, yo, z), (-345, yo, z), (-230, yc, z), (230, yc, z), (345, yo, z), (750, yo, z)],
         d, TEXBLACK, root, bend=90)
    for s in (-1, 1):
        lib.cylinder(f'cap{s}', (s * 751, yo, z), (1, 0, 0), d, 4, TEXBLACK, root, n=24)
        x = s * 610
        poly = [(x - 140, 575), (x + 140, 575), (x + 140, 465), (x - 140, 465)]
        frame_walls(f'lampBox{s}', poly, 6, -1630, -1510, TEXBLACK, root, back=-1575)
        lamp_strip(root, s, x, 520, -1590, 250, 90, [(1, AMBER), (1.2, TAILRED), (0.8, LENS)][::-s])
        box(f'mount{s}', (s * 420, yo, z + 120), (70, 70, 200), TEXBLACK, root, bevel=4)
        box(f'plateTab{s}', (s * 110, 440, z - d / 2 + 6), (24, 70, 12), TEXBLACK, root, bevel=1)
    number_plate(root, 370, z - d / 2 - 1)
    rear_valance(root)
    return root


def rear_jaos_cowl():
    """JAOS Rear Sport Cowl B042518. JAOS publish: overall length 15 mm
    shorter than stock, lower edge 29 mm lower (so y 370), plate height
    unchanged, 4.65 kg. Width, pods and lamps off JAOS's photos with the
    plate as the ruler: two boxy end pods about 450 x 270 wrapping forward to
    the arches, a lower 150 mm centre beam set back 70 between them, two 80
    mm round LED lamps a side in a black recess and a small square reverse
    lamp inboard; the plate stays where the stock one was (centre y 460)."""
    root = group('rearBumper_jaos_rear_cowl')
    W, top, bot = 1600, 640, 370
    zp = -1605 + 15                                          # 15 mm shorter than the stock face
    for s in (-1, 1):
        a, b = (350, W / 2) if s > 0 else (-W / 2, -350)
        st = rear_stations(W, top, top - bot, 120, face=zp, wrap=150, x0=a, x1=b)
        xloft(f'pod{s}', st, TEXBLACK, root, r=24)
        box(f'recess{s}', (s * 515, 505, zp - 2), (260, 110, 6), BLACK, root, bevel=10)
        round_lamp(root, f'{s}o', s * 570, 505, zp - 4, 80, TAILRED, dome=False)
        round_lamp(root, f'{s}i', s * 460, 505, zp - 4, 80, TAILRED, dome=False)
        box(f'revBezel{s}', (s * 395, 505, zp - 2), (70, 70, 6), BLACK, root, bevel=4)
        box(f'reverse{s}', (s * 395, 505, zp - 6), (55, 55, 3), LENS, root, bevel=2)
    zc = zp + 70
    xloft('centre', rear_stations(W, bot + 150, 150, 110, face=zc, wrap=0, x0=-360, x1=360), TEXBLACK, root, r=20)
    number_plate(root, 460, zc - 2.5)
    rear_mounts(root, 560, zc)
    return root


def rear_wildgoose_crawler():
    """WILD GOOSE crawler rear bar JM-1103 (rv4wildgoose.com: W1330 x H200 x
    D225, 76.3 x 1.6 pipe, 6 mm brackets, 4.5 mm lamp frames with the lens
    set 10 mm in, 9.3 kg, departure angle 55 deg; the plate has to move).
    One straight 76.3 tube just under the body edge (centre y 530, off the
    straight-on photo), an open lamp box about 260 x 105 sitting on each end
    of it, a 6 mm plate bracket with a 50 mm tow hole under each end. The
    plate goes to the tailgate; the lamps are bought separately."""
    root = group('rearBumper_wildgoose_crawler_rear')
    d, y, W = 76.3, 530, 1330
    zt = -1570 + d / 2
    tube('bar', [(-W / 2, y, zt), (W / 2, y, zt)], d, TEXBLACK, root)
    for s in (-1, 1):
        lib.cylinder(f'cap{s}', (s * (W / 2 + 1), y, zt), (1, 0, 0), d, 4, TEXBLACK, root, n=24)
        x = s * 535
        poly = [(x - 130, 652), (x + 130, 652), (x + 130, 548), (x - 130, 548)]
        frame_walls(f'lampBox{s}', poly, 4.5, -1586, -1480, TEXBLACK, root, back=-1560)
        lamp_strip(root, s, x, 600, -1570, 236, 82, [(1, AMBER), (1.2, TAILRED), (0.8, LENS)][::-s])
        box(f'bracket{s}', (s * 330, y - 70, zt + 10), (6, 110, 130), TEXBLACK, root, bevel=1)
        lib.cylinder(f'towHole{s}', (s * 330, y - 92, zt + 10), (1, 0, 0), 50, 8, RUBBER, root, n=20)
        box(f'mount{s}', (s * 250, y, zt + 100), (70, 90, 150), TEXBLACK, root, bevel=4)
    tailgate_plate(root)
    rear_valance(root)
    return root


def rear_wildgoose_box():
    """WILD GOOSE box rear bar JM-1101 (rv4wildgoose.com: beam 1410 x 100 x
    100, 3.2 mm plate, 9 mm brackets, 13.2 kg, departure angle 60 deg; the
    plate has to move). One straight square beam with its top at the body's
    edge (y 640, off the fitted photo), ends cut square, and the
    combination lamps set into its face at the extreme ends (lens about 270
    x 85). The plate goes to the tailgate."""
    root = group('rearBumper_wildgoose_box_rear')
    W, y = 1410, 590
    st = rear_stations(W, y + 50, 100, 100, face=-1570, wrap=0)
    xloft('beam', st, TEXBLACK, root, r=4)
    for s in (-1, 1):
        box(f'endCap{s}', (s * (W / 2 + 3), y, -1520), (6, 100, 100), TEXBLACK, root, bevel=1)
        lamp_strip(root, s, s * 555, y, -1570, 270, 78, [(1, AMBER), (1.2, TAILRED), (0.8, LENS)][::-s])
    rear_mounts(root, y, -1570)
    tailgate_plate(root)
    rear_valance(root)
    return root


def rear_showa_iron():
    """SHOWA GARAGE iron rear bar (showa-garage.shop 000000000843: main pipe
    60, lamp pipe 42). Off the straight-on JB74 photo (plate 330, ~2.65 mm/px):
    about 1420 across, the tube just under the body's edge (centre y 585),
    passing through the sides of two small open lamp frames about 200 x 105
    at +-610 with a small tail lamp inside each and a reflector strip under
    it. The plate goes onto the tailgate beside the spare."""
    root = group('rearBumper_showa_iron_rear')
    d, y = 60, 585
    zt = -1570 + d / 2
    tube('bar', [(-705, y, zt), (705, y, zt)], d, TEXBLACK, root)
    for s in (-1, 1):
        x = s * 610
        poly = [(x - 100, 637), (x + 100, 637), (x + 100, 533), (x - 100, 533)]
        frame_walls(f'lampFrame{s}', poly, 8, -1610, -1472, TEXBLACK, root)
        # the lamp sits on the tube's rear face, inside the frame
        box(f'lamp{s}', (x, y, -1578), (120, 52, 18), BLACK, root, bevel=4)
        box(f'lampLens{s}', (x, y, -1588), (104, 38, 4), TAILRED, root, bevel=2)
        box(f'reflector{s}', (x, 518, -1598), (160, 16, 4), TAILRED, root, bevel=1)
        lib.cylinder(f'cap{s}', (s * 706, y, zt), (1, 0, 0), d, 4, TEXBLACK, root, n=24)
    rear_mounts(root, y, -1570)
    tailgate_plate(root)
    rear_valance(root)
    return root


def rear_taniguchi_pipe():
    """TANIGUCHI off-road rear pipe bar (ors-taniguchi.co.jp: pipe 48.6 x
    2.3, both ends bent, tail-lamp frames on top of the pipe, plate must be
    moved; their small tail lamp's lens is 214 x 65). Off the 3/4 photo: about
    1420 across, pipe centre y 525 (~130 under the body edge), its last 50 mm
    bent forward about 55 deg round the corners (as far as the rear tyres
    allow), a lamp frame about 235 x 80 on top of each end at +-580, and a
    slotted steel panel between the frames closing the gap to the body."""
    root = group('rearBumper_taniguchi_rear_pipe')
    d, y = 48.6, 525
    zt = -1582 + d / 2
    tube('bar', [(-710, y, -1492), (-660, y, zt), (660, y, zt), (710, y, -1492)], d, TEXBLACK, root, bend=60)
    for s in (-1, 1):
        x = s * 580
        box(f'lampFrame{s}', (x, 595, zt), (235, 80, 90), TEXBLACK, root, bevel=3)
        lamp_strip(root, s, x, 595, zt - 45, 214, 65, [(1, AMBER), (1.4, TAILRED), (0.7, LENS)][::-s])
    box('panel', (0, 596, -1562), (924, 88, 6), TEXBLACK, root, bevel=1)
    for k in range(9):
        box(f'slot{k}', (-360 + k * 90, 596, -1566), (50, 14, 3), RUBBER, root, bevel=1)
    rear_mounts(root, y, zt - d / 2)
    tailgate_plate(root)
    rear_valance(root)
    return root


def rear_apio_tactical():
    """APIO Tactical rear bumper 3032-71, ABS, JB74 only (apio.jp; the
    1660 x 280 x 460 on the page is the shipping box -- no body size is
    published). Off the straight-on photo with the flare width 1645 as the
    ruler: about 1600 across and 170 tall under the tailgate, wrapping round
    the corners with a flap down behind each rear wheel; three 70 mm round
    lamps a side in the upper band (amber, red tail, red reflector, outboard
    to inboard), a clear round reverse lamp each side lower down, a recessed
    lower middle with a step lip. The plate goes onto the tailgate."""
    root = group('rearBumper_apio_tactical_rear')
    W, top = 1600, 620
    st = rear_stations(W, top, 100, 140, wrap=130)
    xloft('upper', st, TEXBLACK, root, r=16)
    zf = REAR_FACE
    for s in (-1, 1):
        a, b = (400, W / 2) if s > 0 else (-W / 2, -400)
        xloft(f'lower{s}', rear_stations(W, top - 100, 70, 140, wrap=130, x0=a, x1=b), TEXBLACK, root, r=12)
        for k, (dx, m, dome) in enumerate(((675, AMBER, True), (585, TAILRED, True), (490, TAILRED, False))):
            round_lamp(root, f'{s}{k}', s * dx, 560, at_x(st, s * dx, 3), 70, m, dome=dome)
        round_lamp(root, f'{s}rev', s * 450, 482, zf, 56, LENS)
        box(f'flap{s}', (s * 740, 380, -1500), (90, 170, 8), RUBBER, root, bevel=2)
    xloft('lowerMid', rear_stations(W, top - 100, 70, 110, face=zf + 30, wrap=0, x0=-400, x1=400), TEXBLACK, root, r=10)
    box('stepLip', (0, 456, zf + 10), (800, 14, 60), TEXBLACK, root, bevel=3)
    rear_mounts(root, 560)
    tailgate_plate(root)
    rear_valance(root)
    return root


def rear_outclass_abs():
    """OUTCLASS TYPE2 ABS rear bumper (outclass.ocnk.net 1094: ABS, the lower
    edge 'shaped slim', small universal tail lamps as an option). Off the
    straight-on photo (plate 330, ~3.4 mm/px): about 1450 across and 190
    tall, wrapping forward round the corners with the lower edge chamfered
    up, one small rectangular combination lamp (about 205 x 75) recessed in
    each end of the upper face -- the bar covers where the stock lamps were --
    and the plate on a bracket straddling the lower edge."""
    root = group('rearBumper_outclass_rear_abs')
    W, top = 1450, 600
    st = rear_stations(W, top, 190, 150, wrap=130, rise=50)
    xloft('body', st, TEXBLACK, root, r=24)
    zf = REAR_FACE
    for s in (-1, 1):
        box(f'lampRecess{s}', (s * 525, 555, zf - 1), (230, 96, 4), BLACK, root, bevel=8)
        lamp_strip(root, s, s * 525, 555, zf - 2, 205, 70, [(1, AMBER), (1.5, TAILRED), (0.8, LENS)][::-s])
    box('plateBracket', (0, 426, zf - 2), (260, 110, 6), TEXBLACK, root, bevel=2)
    number_plate(root, 420, zf - 6.5)
    rear_mounts(root, 520)
    rear_valance(root)
    return root


def rear_hamer_mx208():
    """HAMER MX208 (hamer4x4.com: 4 mm steel, 1830 x 650 x 340 overall, 50
    kg, keeps the car's own signal and reverse lamps). 1830 is measured along
    the wrap; straight on it is about 1600 (flare width as the ruler). The
    ends wrap forward to the flares with the stock tail lamps (x 346-680, y
    476-603) set in deep pockets cut through the face; the middle drops as a
    tapered panel to a receiver hitch at y 330; the corners' tops are the
    steps. The plate goes onto the tailgate, as in Hamer's photos. The outer
    faces stand at -1620 so the stock lenses (-1609) sit inside their
    pockets; the middle comes forward to the stock line, clear of the spare."""
    root = group('rearBumper_hamer_mx208')
    W, top, bot = 1600, 630, 390

    def face(x):
        return -1620 + max(0.0, min(1.0, (345 - abs(x)) / 40)) * 55

    kw = dict(face=face, wrap=150, extra=(-345, -305, 305, 345))
    xloft('middle', rear_stations(W, top, top - bot, 150, x0=-345, x1=345, **kw), TEXBLACK, root, r=10)
    for s in (-1, 1):
        a, b = (345, 690) if s > 0 else (-690, -345)
        xloft(f'below{s}', rear_stations(W, 472, 472 - bot, 150, x0=a, x1=b, **kw), TEXBLACK, root, r=6)
        xloft(f'above{s}', rear_stations(W, top, top - 608, 150, x0=a, x1=b, **kw), TEXBLACK, root, r=4)
        a, b = (690, W / 2) if s > 0 else (-W / 2, -690)
        xloft(f'end{s}', rear_stations(W, top, top - bot, 150, x0=a, x1=b, **kw), TEXBLACK, root, r=10)
        box(f'pocketBack{s}', (s * 515, 540, -1547), (345, 136, 6), BLACK, root, bevel=2)
    zc = face(0)
    slab('hitchPanel', [(-210, bot + 6), (210, bot + 6), (110, 330), (-110, 330)], zc, zc + 90, TEXBLACK, root)
    box('receiver', (0, 345, zc + 60), (66, 66, 160), TEXBLACK, root, bevel=3)
    box('receiverMouth', (0, 345, zc - 21), (46, 46, 4), RUBBER, root, bevel=1)
    rear_mounts(root, 520, zc)
    tailgate_plate(root)
    rear_valance(root)
    return root


def grille_generic(pid, h_slats=0, v_slots=0, hex_cells=False, wire=True, label=None, text_mat=None, bezel='round',
                   marker=0, mat=None, ow=580, oh=215, slat_h=30, ribs=False, letters_over=True,
                   frame_mat=None, bezel_mat=None, mesh_mat=None):
    """Stock-outline panel with a centre opening filled per product.

    `mat` is the slats and posts; `frame_mat` the panel round the opening
    and `bezel_mat` the lamp rings, which on a painted grille are body colour
    or white (docs/jb74-grille-finishes.json); `mesh_mat` the mesh behind,
    silver aluminium on KLC's painted faces and black on everyone else's."""
    root = group(f'grille_{pid}')
    mat = mat or TEXBLACK
    frame_mat = frame_mat or mat
    grille_panel('panel', root, frame_mat, (ow, oh, 858))
    lamp_bezels(root, bezel_mat or frame_mat, bezel)
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
        wire_mesh(root, mesh_mat or BLACK, 0, 858, z - 20, ow - 10, oh - 10, pitch=9)
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
            # the legs drop in front of the bumper and turn back through the
            # lower aperture (y 550-600, recessed to z 1668 at |x| 300-400) to
            # a plate on the chassis rail -- the first version stopped them
            # in mid-air in front of the bumper face
            leg = [(s * 540, y, zf + 46), (s * 540, 620, zf + 20), (s * 400, 590, zf - 10), (s * 400, 580, 1640)]
            tube(f'leg{s}', [tuple(p) for p in fillet(leg, 50)], 63, STEEL, root)
            box(f'plate{s}', (s * 400, 580, 1620), (110, 110, 12), STEEL, root, bevel=3)
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
        zc = zf - (6 if pid == 'lower' else 94)              # the Bushranger sits BEHIND the lower mesh
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
        #
        # Everything but the tips lives UNDER the floor, inboard of the rocker
        # (the body side is at |x| 705 and the sill bottom at y 350): the
        # first version hung the canister at |x| 790, outside the car, with
        # the tips firing straight back into the tyre tread. Now the tips turn
        # out sideways at the rocker line and end 130 mm ahead of the tyre.
        zc = -110
        cx, cy = s * 520, 265
        if muffler:
            ml, md = muffler
            lib.cylinder('canister', (cx, cy, zc), (0, 0, 1), md, ml, EXH_STEEL, root, n=26)
            for k in range(9):                               # perforated heat shield
                lib.cylinder(f'perf{k}', (cx, cy + md / 2 - 4, zc - ml / 2 + 40 + k * (ml - 80) / 8),
                             (0, 1, 0), 16, 8, BLACK, root, n=8)
            for zz in (zc - ml / 2 - 10, zc + ml / 2 + 10):
                box(f'strap{zz}', (cx, cy, zz), (md + 16, md + 16, 16), BLACK, root, bevel=4)
                box(f'hanger{zz}', (cx, cy + md / 2 + 30, zz), (24, 70, 16), BLACK, root, bevel=3)
        z_tail = zc - (muffler[0] / 2 if muffler else 200)
        for k in range(tips):
            zt = -560 - k * (tip_d + 14)
            # a short pipe out of the canister's tail, then the tip turned out at the rocker
            tube(f'tail{k}', [(cx, cy, z_tail - 20), (cx, cy, zt), (s * 640, cy, zt)], tip_d - 16, pipe, root, bend=60)
            tip_at(f'tip{k}', s * 715, zt, cy, ax=(s, 0, 0))
        lib.cylinder('run', (cx, cy + 10, zc + 420), (0, 0, 1), tip_d - 16, 500, pipe, root, n=16)
        return root

    if layout == 'through':
        # TANIGUCHI Compe R: the bullet turns out through the bumper corner,
        # high enough to stay out of a water crossing.
        # The mouth has to be OUTSIDE the corner skin (|x| about 750 there);
        # the first version buried the whole bullet and tip inside it.
        yy = 560 - EXH_LIFT
        x = side * 600
        lib.cylinder('bullet', (x, yy, BUMPER_Z + 130), (1, 0, 0), tip_d + 60, 220, EXH_STEEL, root, n=24)
        tip_at('tip', side * 775, BUMPER_Z + 130, yy, ax=(side, 0, 0))
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


# ============================================================ NUMBER PLATES
PLATE_INK = material('PlateInk', 0x15171a, rough=0.5)
PLATE_RIM = material('PlateRim', 0x2a2d31, rough=0.45, metal=0.3)


def decorate_plates():
    """Every bumper carries a plate, and a blank white slab was the most
    toy-like thing on the car. After everything is built, each plate gets a
    raised black border, embossed characters in the Taiwanese small-car
    format (three letters, a dash, four digits) and two chrome screws. The
    registration is made up; a rear plate's lettering faces backwards."""
    plates = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.split('.')[0] == 'plate'
              and o.data.materials and o.data.materials[0] == PLATE]
    for i, pl in enumerate(plates):
        bpy.context.view_layer.update()
        mw = pl.matrix_world
        cs = [mw @ Vector(c) for c in pl.bound_box]
        bx0, bx1 = min(c.x for c in cs), max(c.x for c in cs)
        by0, by1 = min(c.y for c in cs), max(c.y for c in cs)
        bz0, bz1 = min(c.z for c in cs), max(c.z for c in cs)
        # back to the car frame (mm): x = bx, y = bz, z = -by
        x, y = (bx0 + bx1) / 2 / lib.MM, (bz0 + bz1) / 2 / lib.MM
        w, h = (bx1 - bx0) / lib.MM, (bz1 - bz0) / lib.MM
        front = (-(by0 + by1) / 2) > 0
        zf = (-by0 / lib.MM) if front else (-by1 / lib.MM)       # the face that shows
        sgn = 1 if front else -1
        root = pl.parent
        t = 3
        for k, (cx, cy, sx, sy) in enumerate(((0, h / 2 - 5, w - 6, 6), (0, -h / 2 + 5, w - 6, 6),
                                              (-w / 2 + 5, 0, 6, h - 6), (w / 2 - 5, 0, 6, h - 6))):
            box(f'plateRim{i}_{k}', (x + cx, y + cy, zf + sgn * t / 2), (sx, sy, t), PLATE_RIM, root, bevel=0.5)
        ob = text(f'plateNo{i}', 'JMN-7474', (x, y - h * 0.04, zf + sgn * 1.5), h * 0.42, 2, PLATE_INK, root,
                  font='/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf')
        ob.scale = (min(1.0, (w * 0.84) / max(1.0, ob.dimensions.x / lib.MM)), 1, 1) if ob.dimensions.x else (1, 1, 1)
        if not front:
            ob.rotation_euler = (0, 0, math.pi)
        for k, dx in enumerate((-w * 0.36, w * 0.36)):
            lib.cylinder(f'plateBolt{i}_{k}', (x + dx, y + h * 0.36, zf + sgn * 2), (0, 0, 1), 12, 4, CHROME, root, n=10)


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
    bumper_klc()
    bumper_outclass()
    for st in ('stock', 'steel', 'six', 'eight', 'ten', 'beadlock', 'moon', 'daytona', 'slot5', 'watanabe', 'eightpin',
               'renkon', 'arc4', 'dwindow', 'turbine', 'seven', 'oz20'):
        rim(st)
    roof_rack_arb()
    arb_deflector()
    arb_rail_front()
    arb_rail_side()
    arb_jerry()
    arb_gas()
    arb_boards()
    arb_jack()
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
    widebody('wald_bison', 30, 'box')
    widebody('kuhl_blocker', 30, 'box')
    widebody('lb_gmini', 35, 'box', lip=RUBBER)
    widebody('aero_over', 35, 'box')
    widebody('damd_delta', 40, 'blister')
    face_bron55()
    face_damd_delta()
    rear_damd_delta()
    spoiler_damd_wing()
    spoiler_rowen()
    stripe_damd_center()
    decals()
    cage_wildgoose()
    stripe_retro3()
    stripe_toolgear()
    stripe_jaos()
    stripe_toy4()
    stripe_stencil()
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
    rack_platform('yakima', 1370, 1520, slat_dir='across', slats=6, rail=(60, 40), legs=4, deflector=False)
    # same 110 mm slat pitch as the full-length Slimline II
    rack_platform('fr34', 1345, 1156, slat_dir='across', slats=10, rail=(30, 50), legs=4, deflector=True)
    rack_platform('pioneer', 1339, 1453, slat_dir='along', slats=5, rail=(56, 52), legs=4, deflector=False)
    rack_platform('jaos', 1250, 1400, slat_dir='across', slats=6, rail=(32, 32), legs=6, deflector=False, side_bars=96)
    # flat: IPF publish 38.8 mm for the rack body; no hoop in any photo
    rack_platform('ipf', 1250, 1400, slat_dir='across', slats=7, rail=(40, 39), legs=6, deflector=False)
    rack_platform('apio', 1270, 1420, slat_dir='across', slats=4, rail=(28, 60), legs=6, deflector=True)
    rack_platform('showa_foot', 1250, 1500, slat_dir='across', slats=12, rail=(40, 40), legs=6, deflector=False)
    rack_wood('half')
    rack_wood('full')
    rack_platform('tw_generic', 1260, 1600, slat_dir='across', slats=7, legs=6, deflector=True)
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
    side_step('taniguchi_bar', 'tube', tube_d=42, pads=[(145, 550, 80)])
    side_step('taniguchi_short', 'short', tube_d=32, pads=[(145, 550, 0)])
    side_step('showa', 'tube', tube_d=48)
    side_step('wildgoose_fold', 'short', tube_d=20, pads=[(160, 510, 0)])
    side_step('wildgoose_guard', 'armour', standoff=55)
    side_step('customwagon', 'tube', tube_d=48, pads=[(140, 420, 60)])
    side_step('spieler', 'plate', plate_w=150)
    side_step('ironman', 'slider', tube_d=51)
    side_step('hamer', 'slider', tube_d=60, pads=[(120, 260, -300), (120, 260, 300)])
    # front bumpers (TW/JP research 2026-09-16; proportions per the photo review 2026-09-26)
    bumper_armando()
    bumper_beyond_liberte()
    bumper_maverick()
    bumper_mrk_abs()
    bumper_wmd_winch()
    bumper_jaos_cowl()
    bumper_taniguchi_square()
    bumper_taniguchi_double()
    bumper_klc_short()
    bumper_toc_extreme()
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
    # Rear bars reach up to the tailgate's edge like the real ones; the
    # tailgate spare's underside is at y 547-585 in the middle, so anything
    # above that stands forward of it (see REAR_FACE) and the spare swings
    # clear when the tailgate opens.
    rear_damd_roots()
    # rear bumpers
    rear_klc_heritage()
    rear_beyond()
    rear_jaos_cowl()
    rear_wildgoose_crawler()
    rear_wildgoose_box()
    rear_showa_iron()
    rear_taniguchi_pipe()
    rear_apio_tactical()
    rear_outclass_abs()
    rear_hamer_mx208()
    # grilles
    grille_generic('taishan_retro', v_slots=11)
    # finishes per docs/jb74-grille-finishes.json: the makers' own demo cars
    grille_generic('klc_ja', wire=True, marker=4, bezel='round', h_slats=1, slat_h=18, mat=GUNMETAL, mesh_mat=STEEL)
    grille_generic('klc_nanaketsu', v_slots=7, bezel='square', mesh_mat=STEEL)
    grille_generic('klc_forty', wire=True, label='SUZUKI', bezel='round', frame_mat=PAINT,
                   bezel_mat=material('GrilleWhite', 0xefefea, rough=0.4), mesh_mat=STEEL)
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
    grille_generic('apio_sj', v_slots=7, mat=GUNMETAL)        # seven slots
    grille_generic('apio_marker', h_slats=4, marker=4)
    grille_generic('taniguchi_washer', wire=True, mat=GUNMETAL)
    grille_generic('kpro_folksy', h_slats=6, wire=False)      # the white is gelcoat primer; the maker shows it black
    grille_generic('prostaff_minig', v_slots=9, bezel='square', mat=PAINT)
    grille_generic('sixsense_explosion', h_slats=7, slat_h=12, label='SUZUKI', text_mat=CHROME_TRIM, bezel='square', mat=PAINT)
    decorate_plates()
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
