"""Draw the loading screen's Jimny face, and print the SVG for app.html.

    python3 tools/bootcar.py

It draws the FRONT, not the side. Two goes at a side elevation both read as
the wrong car -- a profile is nearly all proportion, and proportion is the bit
that goes wrong. The face is the opposite: a JB74 is recognised by the grille
and the two round lamps, which are a rectangle, five slots and two circles,
and none of it depends on getting a length right.

Every landmark is MEASURED off model/jimny-hq.glb, by raycasting its nose on a
20 mm grid and sorting the hits by material: LampLens for the lamps, the black
trim for the grille panel, body paint for everything around it.

Frame: X is millimetres across the car (+ to the right as drawn), Y is
millimetres above the ground.
"""

VB_W, VB_H = 300.0, 130.0

# Measured off a head-on render of the model, with the camera's own
# projection used to turn pixels back into millimetres:
#   face             |x| 675 at y 1035 (bonnet shut line), 711 across the bumper
#   grille panel     |x| 648, y 771-983
#   head lamps       r 100 at (+-453, 877)
#   indicators       55 x 66 at (+-596, 917), just outboard of the lamps
#   five slots       88 wide on a 60 rib, y 789-961, filling x +-340
#   paint band       y 722-771, between the grille and the bumper
#   bumper           y 413-722; its recess |x| 380, y 519-652
#   fog lamps        r 49 at (+-590, 585)
FACE_X, FACE_HIP = 675.0, 711.0
FACE_TOP, FACE_BOT = 1035.0, 410.0
GRILLE_X, GRILLE_TOP, GRILLE_BOT = 648.0, 983.0, 771.0
LAMP_X, LAMP_Y, LAMP_R = 453.0, 877.0, 100.0
IND_X0, IND_X1, IND_TOP, IND_BOT = 568.0, 624.0, 950.0, 884.0
FOG_X, FOG_Y, FOG_R = 590.0, 585.0, 49.0
BUMPER_TOP, BAND_TOP = 722.0, 771.0
RECESS_X, RECESS_TOP, RECESS_BOT = 380.0, 652.0, 519.0
SLOT_W, SLOT_GAP, SLOTS = 88.0, 60.0, 5
SLOT_TOP, SLOT_BOT = 961.0, 789.0

K = min((VB_W - 24) / (2 * FACE_HIP), (VB_H - 8) / (FACE_TOP - FACE_BOT))
CX = VB_W / 2
GROUND = VB_H - (VB_H - (FACE_TOP - FACE_BOT) * K) / 2 + FACE_BOT * K


def pt(x, y):
    return round(CX + x * K, 1), round(GROUND - y * K, 1)


def poly(pts, close=True):
    d = 'M%s %s' % pt(*pts[0]) + ''.join('L%s %s' % pt(*p) for p in pts[1:])
    return d + ('Z' if close else '')


def rect(x0, x1, y0, y1):
    return poly([(x0, y1), (x1, y1), (x1, y0), (x0, y0)])


face = poly([(-FACE_X, FACE_TOP), (FACE_X, FACE_TOP), (FACE_HIP, 940),
             (FACE_HIP, 500), (FACE_X - 15, FACE_BOT), (-FACE_X + 15, FACE_BOT),
             (-FACE_HIP, 500), (-FACE_HIP, 940)])

slot_span = SLOTS * SLOT_W + (SLOTS - 1) * SLOT_GAP
slots = [rect(x, x + SLOT_W, SLOT_BOT, SLOT_TOP)
         for x in (-slot_span / 2 + i * (SLOT_W + SLOT_GAP) for i in range(SLOTS))]

print('<!-- JB74 face, measured off model/jimny-hq.glb by tools/bootcar.py -->')
print(f'<path class="body" pathLength="1" d="{face}"/>')
print(f'<path class="body" pathLength="1" d="{rect(-GRILLE_X, GRILLE_X, GRILLE_BOT, GRILLE_TOP)}"/>')
# the painted band that separates the grille from the bumper
print(f'<path class="win" pathLength="1" d="'
      f'{poly([(-FACE_HIP, BAND_TOP), (FACE_HIP, BAND_TOP)], close=False)}"/>')
print(f'<path class="win" pathLength="1" d="'
      f'{poly([(-FACE_HIP, BUMPER_TOP), (FACE_HIP, BUMPER_TOP)], close=False)}"/>')
for d in slots:
    print(f'<path class="win" pathLength="1" d="{d}"/>')
for s in (-1, 1):
    print(f'<path class="win" pathLength="1" '
          f'd="{rect(s * IND_X0, s * IND_X1, IND_BOT, IND_TOP)}"/>')
for s in (-1, 1):
    cx, cy = pt(s * LAMP_X, LAMP_Y)
    print(f'<circle class="w" pathLength="1" cx="{cx}" cy="{cy}" r="{round(LAMP_R * K, 1)}"/>')
    print(f'<circle class="h" pathLength="1" cx="{cx}" cy="{cy}" r="{round(LAMP_R * 0.52 * K, 1)}"/>')
for s in (-1, 1):
    cx, cy = pt(s * FOG_X, FOG_Y)
    print(f'<circle class="h" pathLength="1" cx="{cx}" cy="{cy}" r="{round(FOG_R * K, 1)}"/>')
# the bumper's own recess, which is what fills the lower half on the real car
print(f'<path class="win" pathLength="1" d="'
      f'{rect(-RECESS_X, RECESS_X, RECESS_BOT, RECESS_TOP)}"/>')
