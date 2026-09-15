# Trace a maker's straight-on tread photo into a tileable height mask.
#
#   venv/bin/python blender/trace_tread.py <photo> <out.png> [pitches] [y_lo] [y_hi]
#
# The photo runs along the circumference vertically. Only the middle band is
# used (the tyre curves away top and bottom, squashing the blocks there);
# block tops are lighter than the local mean, so a high-pass threshold gives
# blocks = white, grooves = black. The pattern's pitch is found by
# autocorrelation and an integer number of pitches is cut so the strip tiles
# around the tyre; the result is transposed so x runs along the circumference,
# which is how wheels.js reads it. Prints the pitch in pixels.
import sys
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
pitches = int(sys.argv[3]) if len(sys.argv) > 3 else 3
y_lo = int(sys.argv[4]) if len(sys.argv) > 4 else 130
y_hi = int(sys.argv[5]) if len(sys.argv) > 5 else 500
x_lo, x_hi = 22, 449

im = Image.open(src).convert('L')
g = np.asarray(im, dtype=np.float32)
lo = np.asarray(im.filter(ImageFilter.GaussianBlur(16)), dtype=np.float32)
hp = g - lo
mask = np.clip((hp + 10) / 14, 0, 1)             # soft threshold: >+4 block, <-10 groove
# closing fills sipes and the lit block flanks the photo shows as dark, leaving groove floors only
mi = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
mask = np.asarray(mi.filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float32) / 255

band = mask[y_lo:y_hi, x_lo:x_hi]
prof = band[:, band.shape[1] // 4: 3 * band.shape[1] // 4].mean(axis=1)
prof = prof - prof.mean()
ac = np.correlate(prof, prof, mode='full')[len(prof) - 1:]
ac /= ac[0]
lo_lag, hi_lag = 30, min(220, len(ac) - 1)
lag = int(np.argmax(ac[lo_lag:hi_lag]) + lo_lag)
# a staggered pattern peaks at half a pitch too; prefer the longer lag if it is nearly as strong
if 2 * lag < hi_lag and ac[2 * lag] > 0.8 * ac[lag]:
    lag *= 2
n = min(pitches, (y_hi - y_lo) // lag)
strip = band[:n * lag, :]
strip = np.ascontiguousarray(strip.T)             # x = circumference
img = Image.fromarray((strip * 255).astype(np.uint8)).resize((strip.shape[1] * 2, strip.shape[0] * 2), Image.BICUBIC)
img.save(out)
# preview: two repeats side by side, to check the seam
prev = Image.new('L', (img.width * 2, img.height))
prev.paste(img, (0, 0)); prev.paste(img, (img.width, 0))
prev.save(out.replace('.png', '.preview.png'))
print(f'{out}: pitch {lag}px, {n} pitches, mask {img.width}x{img.height}, ac={ac[lag]:.2f}')
