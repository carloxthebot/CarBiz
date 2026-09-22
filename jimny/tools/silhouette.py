"""Turn the masks from tools/silhouette.mjs into the loading screen's SVG.

Walks the outer boundary of the body mask, simplifies it, does the same for
each window opening, and prints paths in a 300 x 130 viewBox with the wheels
as circles. Paste the result into app.html's #bootcar.

    node tools/silhouette.mjs && python3 tools/silhouette.py
"""
import json
import os
import sys

from PIL import Image

sys.setrecursionlimit(60000)
SRC = os.environ.get('OUT', '/private/tmp/claude-501/-Users-carlox-Personal/'
                            'bae455ed-b844-4d8b-bf32-ff71834ff136/scratchpad')
VB_W, VB_H = 300.0, 130.0
PAD = 4.0


def mask(path, thr=110, x_max=1030):
    im = Image.open(path).convert('L')
    w, h = im.size
    px = im.load()
    return {(x, y) for y in range(h) for x in range(min(w, x_max)) if px[x, y] > thr}


def denoise(pts):
    """Morphological open: drops hairline features (the radio antenna) that
    would otherwise become a spike on the roof."""
    k = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    eroded = {p for p in pts if all((p[0] + dx, p[1] + dy) in pts for dx, dy in k)}
    out = set()
    for p in eroded:
        for dx, dy in k:
            out.add((p[0] + dx, p[1] + dy))
    return out


def blobs(pts):
    """Split a point set into 4-connected components, largest first."""
    seen, out = set(), []
    for p in pts:
        if p in seen:
            continue
        stack, comp = [p], []
        seen.add(p)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in pts and q not in seen:
                    seen.add(q)
                    stack.append(q)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def contour(pts):
    """Order the boundary pixels into one loop. Greedy nearest-neighbour: for a
    clean silhouette every step is to a touching pixel, so this traces the
    outline without the backtracking bookkeeping a Moore walk needs."""
    s = set(pts)
    edge = {p for p in s if not all((p[0] + dx, p[1] + dy) in s
                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    if not edge:
        return list(s)
    grid = {}
    for p in edge:
        grid.setdefault((p[0] >> 3, p[1] >> 3), []).append(p)
    start = min(edge, key=lambda p: (p[1], p[0]))
    out, cur = [start], start
    edge.discard(start)
    while edge:
        best, bd = None, 1e9
        cx, cy = cur[0] >> 3, cur[1] >> 3
        for gx in range(cx - 1, cx + 2):
            for gy in range(cy - 1, cy + 2):
                for q in grid.get((gx, gy), ()):
                    if q not in edge:
                        continue
                    d = (q[0] - cur[0]) ** 2 + (q[1] - cur[1]) ** 2
                    if d < bd:
                        best, bd = q, d
        if best is None or bd > 32:
            break
        edge.discard(best)
        out.append(best)
        cur = best
    return out


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    worst, at = 0.0, 0
    for i, (x, y) in enumerate(pts[1:-1], 1):
        d = abs(dy * (x - x0) - dx * (y - y0)) / n
        if d > worst:
            worst, at = d, i
    if worst <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:at + 1], eps)[:-1] + rdp(pts[at:], eps)


def main():
    body = mask(f'{SRC}/sil_body.png')
    glass = mask(f'{SRC}/sil_glass.png')
    if not body:
        sys.exit('no body mask -- run tools/silhouette.mjs first')
    car = blobs(denoise(body))[0]
    xs = [p[0] for p in car]
    ys = [p[1] for p in car]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = min((VB_W - 2 * PAD) / (x1 - x0), (VB_H - 2 * PAD) / (y1 - y0))
    ox = (VB_W - (x1 - x0) * k) / 2
    oy = (VB_H - (y1 - y0) * k) / 2

    def to_vb(p):                                   # mirrored so the car faces right
        return (round(VB_W - (ox + (p[0] - x0) * k), 1), round(oy + (p[1] - y0) * k, 1))

    def path(pts, eps):
        v = [to_vb(p) for p in rdp(contour(pts), eps)]
        d = f'M{v[0][0]} {v[0][1]}' + ''.join(f'L{x} {y}' for x, y in v[1:]) + 'Z'
        return d, len(v)

    d_body, n = path(car, 2.2)
    print(f'<!-- body outline, {n} points, traced from model/jimny-hq.glb -->')
    print(f'<path class="body" pathLength="1" d="{d_body}"/>')
    for i, g in enumerate(blobs(denoise(glass))):
        if len(g) < 900:                            # skip slivers: wiper, mirror glass
            continue
        # the side windows are square openings with rounded corners; traced at
        # a fine tolerance they come out wobbly, which does not read as glass
        d_g, n = path(g, 5.5)
        print(f'<path class="win" pathLength="1" d="{d_g}"/>   <!-- window {i}, {n} pts -->')
    # road wheels only: the tailgate spare reads as a bubble in a side outline
    ws = json.load(open(f'{SRC}/sil_wheels.json'))
    ground = max(w['y'] for w in ws)
    for w in ws:
        if w['y'] < ground - 8:
            continue
        cx, cy = to_vb((w['x'], w['y']))
        print(f'<circle class="w" pathLength="1" cx="{cx}" cy="{cy}" r="{round(w["r"] * k, 1)}"/>')


main()
