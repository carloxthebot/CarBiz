"""Draw the loading screen's Jimny outline, and print the SVG for app.html.

    python3 tools/bootcar.py

Replaces the traced outline that used to come out of tools/silhouette.*. A
trace of a render carries every wobble the renderer and the tracer put in, and
a JB74 has none: it is straight lines, right angles and circles, which is the
whole look of the car. So the profile is written out here as real millimetres
off the published JB74 Sierra dimensions and converted once.

Frame: Z is millimetres rearward from the front bumper face, Y is millimetres
above the ground, and the car faces RIGHT in the finished drawing.
"""

VB_W, VB_H = 300.0, 130.0

# JB74 Sierra, published: 3550 long, 1730 tall over the roof rails, 2250
# wheelbase, 640 front overhang. The published length is measured to the
# TAILGATE SPARE, not to the body, so the body ends at 3300 and the spare is
# what reaches 3550. Everything else is read off the model at those anchors.
LEN, TALL = 3550.0, 1690.0
BODY_REAR, ROOF_REAR = 3370.0, 3310.0
AXLE_F, AXLE_R = 640.0, 2890.0
TYRE_R = 350.0                       # 195/80R15 is 683 across; the demo car is bigger
ARCH_R, ARCH_Y = 400.0, 375.0        # opening, centred just above the axle
SILL = 470.0                         # rocker, and where the arches cut into it
ARCH_DZ = (ARCH_R ** 2 - (SILL - ARCH_Y) ** 2) ** 0.5    # arch lip, along the sill
BELT, HEAD = 1180.0, 1620.0          # window sill and the roof rail's inner edge
# the tailgate spare: on the car's centreline, so in a side elevation it is a
# circle laid over the tailgate whose back half is the only part clear of the
# body. Sized and placed to clear the belt line above it and the rear arch
# below it, which is where it sits on the real car.
SPARE_Z, SPARE_Y, SPARE_R = 3260.0, 940.0, 290.0

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


body = (
    # front bumper, up the grille panel and along the bonnet. It starts where
    # the front arch ends, because on this car they meet: 640 of front
    # overhang minus a 400 opening leaves the bumper the last 250 mm.
    poly([(AXLE_F - ARCH_DZ, 400), (20, 410), (0, 500), (0, 690), (30, 720), (30, 1070),
          (85, 1110), (700, 1140), (745, 1155),
          # windscreen, roof, tailgate
          (1155, TALL), (ROOF_REAR, TALL), (BODY_REAR, 1610), (BODY_REAR, 560),
          # rear bumper, then forward along the bottom through both arches.
          # Like the front, its lower edge ends exactly on the arch lip: the
          # rear wheel on this car really is that close to the back.
          (BODY_REAR + 20, 540), (BODY_REAR + 20, 410),
          (AXLE_R + ARCH_DZ, 395)], close=False)
    + arch(AXLE_R) + arch(AXLE_F) + 'Z'
)
windows = [
    # front door: the frame's leading edge follows the A-pillar, so it leans
    # BACK going up -- about 10 degrees. Everything else is square, and the
    # rear quarter is square all round.
    poly([(1400, HEAD), (2180, HEAD), (2180, BELT), (1310, BELT)]),
    poly([(2290, HEAD), (2950, HEAD), (2950, BELT), (2290, BELT)]),
]

print('<!-- JB74 side elevation, drawn to the published dimensions by '
      'tools/bootcar.py -->')
print(f'<path class="body" pathLength="1" d="{body}"/>')
for d in windows:
    print(f'<path class="win" pathLength="1" d="{d}"/>')
for z, y, r in ((AXLE_R, TYRE_R, TYRE_R), (AXLE_F, TYRE_R, TYRE_R),
                (SPARE_Z, SPARE_Y, SPARE_R)):
    cx, cy = pt(z, y)
    print(f'<circle class="w" pathLength="1" cx="{cx}" cy="{cy}" '
          f'r="{round(r * K, 1)}"/>')
    print(f'<circle class="h" pathLength="1" cx="{cx}" cy="{cy}" '
          f'r="{round(r * 0.47 * K, 1)}"/>')
