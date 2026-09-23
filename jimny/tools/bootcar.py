"""Draw the loading screen's Jimny face, and print the SVG for app.html.

    python3 tools/bootcar.py

It draws the GRILLE, nothing else. Two goes at a side elevation both read as
the wrong car -- a profile is nearly all proportion, and proportion is the bit
that goes wrong. The grille is the opposite: a JB74 is recognised by it and by
the two round lamps sitting in it, which is a rectangle, five slots and two
circles, and none of it depends on getting a length right. The bumper under it
carries no recognition and only made the drawing smaller, so it is left off.

Every landmark is MEASURED off model/jimny-hq.glb, by raycasting its nose on a
20 mm grid and sorting the hits by material: LampLens for the lamps, the black
trim for the grille panel, body paint for everything around it.

Frame: X is millimetres across the car (+ to the right as drawn), Y is
millimetres above the ground.
"""

VB_W, VB_H = 300.0, 58.0

# Measured off a head-on render of the model, with the camera's own
# projection used to turn pixels back into millimetres:
#   grille panel     |x| 648, y 771-983
#   head lamps       r 100 at (+-453, 877)
#   indicators       55 x 66 at (+-596, 917), just outboard of the lamps
#   five slots       88 wide on a 60 rib, y 789-961, filling x +-340
GRILLE_X, GRILLE_TOP, GRILLE_BOT = 648.0, 983.0, 771.0
LAMP_X, LAMP_Y, LAMP_R = 453.0, 877.0, 100.0
IND_X0, IND_X1, IND_TOP, IND_BOT = 568.0, 624.0, 950.0, 884.0
SLOT_W, SLOT_GAP, SLOTS = 88.0, 60.0, 5
SLOT_TOP, SLOT_BOT = 961.0, 789.0

K = min((VB_W - 16) / (2 * GRILLE_X), (VB_H - 10) / (GRILLE_TOP - GRILLE_BOT))
CX = VB_W / 2
GROUND = VB_H - (VB_H - (GRILLE_TOP - GRILLE_BOT) * K) / 2 + GRILLE_BOT * K


def pt(x, y):
    return round(CX + x * K, 1), round(GROUND - y * K, 1)


def poly(pts, close=True):
    d = 'M%s %s' % pt(*pts[0]) + ''.join('L%s %s' % pt(*p) for p in pts[1:])
    return d + ('Z' if close else '')


def rect(x0, x1, y0, y1):
    return poly([(x0, y1), (x1, y1), (x1, y0), (x0, y0)])


slot_span = SLOTS * SLOT_W + (SLOTS - 1) * SLOT_GAP
slots = [rect(x, x + SLOT_W, SLOT_BOT, SLOT_TOP)
         for x in (-slot_span / 2 + i * (SLOT_W + SLOT_GAP) for i in range(SLOTS))]

print('<!-- JB74 grille, measured off model/jimny-hq.glb by tools/bootcar.py -->')
print(f'<path class="body" pathLength="1" d="{rect(-GRILLE_X, GRILLE_X, GRILLE_BOT, GRILLE_TOP)}"/>')
for d in slots:
    print(f'<path class="win" pathLength="1" d="{d}"/>')
for s in (-1, 1):
    print(f'<path class="win" pathLength="1" '
          f'd="{rect(s * IND_X0, s * IND_X1, IND_BOT, IND_TOP)}"/>')
for s in (-1, 1):
    cx, cy = pt(s * LAMP_X, LAMP_Y)
    print(f'<circle class="w" pathLength="1" cx="{cx}" cy="{cy}" r="{round(LAMP_R * K, 1)}"/>')
    print(f'<circle class="h" pathLength="1" cx="{cx}" cy="{cy}" r="{round(LAMP_R * 0.52 * K, 1)}"/>')
