#!/usr/bin/env python3
"""Photo ruler: turn pixel coordinates into millimetres.

Pick four corners of something in the photo whose real size is known and
lies in one plane -- a JDM number plate is 330 x 165 mm and is in almost
every owner photo -- and this solves the homography that maps that plane
to millimetres. Anything ON THAT SAME PLANE can then be measured; parts
standing proud of it are measured with systematic error, so pick a
reference plane close to the part you care about.

    python3 ruler.py photo.jpg \
        --ref 742,812 1160,806 1164,908 738,914 --size 330x165 \
        --measure 470,690 1420,690 \
        --rectify out.png

Corners are given clockwise from the reference's top-left. --measure takes
pairs of points and prints the distance between each pair in mm.
No OpenCV: the DLT is eight linear equations, numpy solves it directly.
"""
import argparse
import sys

import numpy as np


def homography(src, dst):
    """Solve H with src (pixels) -> dst (mm), four point pairs, DLT."""
    rows = []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    b = np.array([c for p in dst for c in p], dtype=float)
    h = np.linalg.solve(np.array(rows, dtype=float), b)
    return np.append(h, 1.0).reshape(3, 3)


def apply(H, pts):
    p = np.hstack([np.asarray(pts, dtype=float), np.ones((len(pts), 1))])
    q = p @ H.T
    return q[:, :2] / q[:, 2:3]


def point(s):
    x, y = s.split(',')
    return (float(x), float(y))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image', nargs='?')
    ap.add_argument('--ref', nargs=4, type=point, required=True,
                    help='four corners of the reference rectangle, clockwise from top-left')
    ap.add_argument('--size', default='330x165', help='reference size in mm, WxH (default: a JDM plate)')
    ap.add_argument('--measure', nargs='+', type=point, default=[],
                    help='pairs of points; the distance of each pair is printed in mm')
    ap.add_argument('--at', nargs='+', type=point, default=[],
                    help='single points; their mm coordinates on the reference plane are printed')
    ap.add_argument('--rectify', help='write a top-down view of the plane to this PNG')
    ap.add_argument('--scale', type=float, default=1.0, help='px per mm in the rectified image')
    a = ap.parse_args()

    W, H_mm = (float(v) for v in a.size.lower().split('x'))
    dst = [(0, 0), (W, 0), (W, H_mm), (0, H_mm)]
    H = homography(a.ref, dst)

    # the reference's own diagonals come back exact by construction, so report
    # the scale at its centre instead: how many mm one pixel covers there
    c = np.mean(a.ref, axis=0)
    d = apply(H, [c, (c[0] + 10, c[1]), (c[0], c[1] + 10)])
    print(f'scale at reference centre: {np.linalg.norm(d[1] - d[0]) / 10:.3f} mm/px across, '
          f'{np.linalg.norm(d[2] - d[0]) / 10:.3f} mm/px down')

    if a.at:
        for p, q in zip(a.at, apply(H, a.at)):
            print(f'  point {p[0]:.0f},{p[1]:.0f} -> {q[0]:8.1f} {q[1]:8.1f} mm')
    if a.measure:
        if len(a.measure) % 2:
            sys.exit('--measure takes pairs of points')
        q = apply(H, a.measure)
        for i in range(0, len(q), 2):
            d = q[i + 1] - q[i]
            print(f'  {a.measure[i]} -> {a.measure[i + 1]}: {np.linalg.norm(d):8.1f} mm '
                  f'(dx {d[0]:.1f}, dy {d[1]:.1f})')

    if a.rectify:
        from PIL import Image
        img = np.asarray(Image.open(a.image).convert('RGB'))
        ow, oh = int(W * a.scale), int(H_mm * a.scale)
        ys, xs = np.mgrid[0:oh, 0:ow]
        mm = np.stack([xs.ravel() / a.scale, ys.ravel() / a.scale], axis=1)
        src = apply(np.linalg.inv(H), mm).round().astype(int)
        ok = ((src[:, 0] >= 0) & (src[:, 0] < img.shape[1]) &
              (src[:, 1] >= 0) & (src[:, 1] < img.shape[0]))
        out = np.zeros((oh * ow, 3), dtype=np.uint8)
        out[ok] = img[src[ok, 1], src[ok, 0]]
        Image.fromarray(out.reshape(oh, ow, 3)).save(a.rectify)
        print(f'rectified plane -> {a.rectify} ({ow} x {oh} px at {a.scale} px/mm)')


if __name__ == '__main__':
    main()
