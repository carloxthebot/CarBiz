"""Draw the loading screen's Jimny outline, and print the SVG for app.html.

    python3 tools/bootcar.py

A JB74 is straight lines, right angles and circles, so the profile is written
out here rather than traced: a trace of a render carries every wobble the
renderer and the tracer put in, and the car has none.

Every landmark below is MEASURED off model/jimny-hq.glb, by raycasting the
side of it on a 20 mm grid the way blender/probe.mjs does. Writing them from
the published brochure figures instead is what produced the first version, and
it came out with a 2155 mm roof on a car whose roof is 1680 -- a three-door
Jimny drawn with five-door proportions.

Frame: Z is millimetres rearward from the front bumper face, Y is millimetres
above the ground, and the car faces RIGHT in the finished drawing.
"""

VB_W, VB_H = 300.0, 130.0

# Measured, near side of the model, Z shifted so the bumper face is 0:
#   bumper face      Z 0,      y 380-690
#   grille panel     Z 120,    y 700-1030
#   bonnet           y 1055 at Z 200, rising to 1150 at Z 1030
#   windscreen       (1090, 1160) up to the roof, about 35 deg off vertical
#   roof             y 1615, Z 1480 to 3190
#   tailgate         (3190, 1615) down to (3310, 620) -- nearly upright
#   rear bumper      Z 3310-3360, y 410-620
#   glass            sill y 1090, top y 1475
#   door window      Z 1560-2210;   rear quarter Z 2430-3030
#   axles            Z 620 and 2806 (wheelbase 2186)
#   tailgate spare   y 590-1280, reaching Z 3520
LEN, TALL = 3520.0, 1630.0
AXLE_F, AXLE_R = 620.0, 2806.0
TYRE_R = 347.0                       # the model's stock tyre is 693 across
ARCH_R, ARCH_Y = 410.0, 370.0        # opening, centred just above the axle
SILL = 420.0                         # rocker, and where the arches cut into it
ARCH_DZ = (ARCH_R ** 2 - (SILL - ARCH_Y) ** 2) ** 0.5    # arch lip, along the sill
BELT, HEAD = 1090.0, 1490.0          # window sill and the top of the glass
ROOF_REAR, TAIL_FOOT = 3190.0, 3310.0
# The spare is on the tailgate with its axis pointing back down the car, so a
# SIDE elevation sees it EDGE ON: a band as tall as the tyre and as wide as
# the tyre is thick, its corners rounded by the tread shoulders. Drawn as a
# wheel face -- which is the view from behind, not from the side -- it reads
# as a wheel stuck on the flank.
SPARE_Z0, SPARE_Z1 = 3210.0, LEN
SPARE_Y0, SPARE_Y1 = 1280.0, 590.0
SPARE_RAD = 60.0

K = min((VB_W - 24) / LEN, (VB_H - 8) / TALL)
NOSE = VB_W - (VB_W - LEN * K) / 2
GROUND = VB_H - (VB_H - TALL * K) / 2


def pt(z, y):
    return round(NOSE - z * K, 1), round(GROUND - y * K, 1)


def poly(pts, close=True):
    d = 'M%s %s' % pt(*pts[0]) + ''.join('L%s %s' % pt(*p) for p in pts[1:])
    return d + ('Z' if close else '')


def arch(z_centre):
    """The wheel opening, from its rear lip up over the top to its front lip.
    Drawn travelling forward along the sill, so on screen it runs left to
    right over the top: clockwise, sweep-flag 1, and under a half turn."""
    r = round(ARCH_R * K, 1)
    x, y = pt(z_centre - ARCH_DZ, SILL)
    return 'L%s %s' % pt(z_centre + ARCH_DZ, SILL) + f'A{r} {r} 0 0 1 {x} {y}'


def spare():
    """The tailgate spare, edge on: a rounded band behind the tailgate."""
    r = round(SPARE_RAD * K, 1)
    a = f'A{r} {r} 0 0 1 '
    (xr, yt), (xl, yb) = pt(SPARE_Z0, SPARE_Y0), pt(SPARE_Z1, SPARE_Y1)
    return (f'M{round(xl + r, 1)} {yt}L{round(xr - r, 1)} {yt}'
            + a + f'{xr} {round(yt + r, 1)}'
            + f'L{xr} {round(yb - r, 1)}' + a + f'{round(xr - r, 1)} {yb}'
            + f'L{round(xl + r, 1)} {yb}' + a + f'{xl} {round(yb - r, 1)}'
            + f'L{xl} {round(yt + r, 1)}' + a + f'{round(xl + r, 1)} {yt}Z')


body = (
    # front bumper, up the grille panel and along the bonnet
    poly([(AXLE_F - ARCH_DZ, 400), (30, 385), (0, 430), (0, 690), (120, 710), (120, 1030),
          (200, 1055), (1030, 1150), (1090, 1165),
          # windscreen, roof, tailgate
          (1440, 1595), (1520, TALL - 15), (ROOF_REAR, TALL - 15),
          (TAIL_FOOT, 620),
          # rear bumper, then forward along the bottom through both arches
          (3360, 600), (3360, 420), (AXLE_R + ARCH_DZ, 395)], close=False)
    + arch(AXLE_R) + arch(AXLE_F) + 'Z'
)
windows = [
    # the door window's leading edge follows the A-pillar, so it leans back
    # going up; everything else is square, and the rear quarter is square all
    # round -- which is what the car actually looks like
    poly([(1610, HEAD), (2210, HEAD), (2210, BELT), (1560, BELT)]),
    poly([(2430, HEAD), (3030, HEAD), (3030, BELT), (2430, BELT)]),
]

print('<!-- JB74 side elevation, measured off model/jimny-hq.glb by '
      'tools/bootcar.py -->')
print(f'<path class="body" pathLength="1" d="{body}"/>')
for d in windows:
    print(f'<path class="win" pathLength="1" d="{d}"/>')
print(f'<path class="w" pathLength="1" d="{spare()}"/>')
for z in (AXLE_R, AXLE_F):
    cx, cy = pt(z, TYRE_R)
    print(f'<circle class="w" pathLength="1" cx="{cx}" cy="{cy}" '
          f'r="{round(TYRE_R * K, 1)}"/>')
    print(f'<circle class="h" pathLength="1" cx="{cx}" cy="{cy}" '
          f'r="{round(TYRE_R * 0.47 * K, 1)}"/>')
