"""Build the site favicons from the tree drawing in images/profile.png."""
import numpy as np
from PIL import Image

SRC = 'images/profile.png'
OUT = 'images/'

# --- binary mask, cropped to the ink with a small margin, padded to a square
a = np.array(Image.open(SRC).convert('L'))
ink = a < 128
ys, xs = np.where(ink)
x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
crop = ink[y0:y1, x0:x1]
h, w = crop.shape
side = int(max(h, w) * 1.06)          # ~3% margin on the long side
sq = np.zeros((side, side), bool)
oy, ox = (side - h) // 2, (side - w) // 2
sq[oy:oy + h, ox:ox + w] = crop

# --- vector contours: follow the pixel cracks, one closed loop per component
def contours(mask):
    H, W = mask.shape
    p = np.zeros((H + 2, W + 2), bool)
    p[1:-1, 1:-1] = mask
    edges = {}
    def add(ax, ay, bx, by):
        edges.setdefault((ax, ay), []).append((bx, by))
    yy, xx = np.where(p)
    for y, x in zip(yy, xx):
        if not p[y - 1, x]: add(x, y, x + 1, y)
        if not p[y, x + 1]: add(x + 1, y, x + 1, y + 1)
        if not p[y + 1, x]: add(x + 1, y + 1, x, y + 1)
        if not p[y, x - 1]: add(x, y + 1, x, y)
    loops = []
    while edges:
        start = next(iter(edges))
        loop, cur = [start], start
        while True:
            nxt = edges[cur].pop()
            if not edges[cur]:
                del edges[cur]
            if nxt == start:
                break
            loop.append(nxt)
            cur = nxt
            if cur not in edges:      # broken chain, give up on this loop
                break
        if len(loop) > 8:
            loops.append([(x - 1, y - 1) for x, y in loop])
    return loops

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    p = np.asarray(pts, float)
    keep = np.zeros(len(p), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(p) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        seg = p[j] - p[i]
        n = np.hypot(*seg)
        d = (np.abs(np.cross(seg, p[i + 1:j] - p[i])) / n if n else
             np.hypot(*(p[i + 1:j] - p[i]).T))
        k = int(np.argmax(d))
        if d[k] > eps:
            k += i + 1
            keep[k] = True
            stack += [(i, k), (k, j)]
    return [tuple(q) for q in p[keep]]

def svg(mask, size):
    s = mask.shape[0]
    paths = []
    for loop in contours(mask):
        pts = rdp(loop + [loop[0]], 1.0)
        if len(pts) < 4:
            continue
        d = 'M' + ' '.join(f'{x * size / s:.1f},{y * size / s:.1f}' for x, y in pts) + 'Z'
        paths.append(d)
    body = '\n  '.join(f'<path d="{d}"/>' for d in paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">\n'
            f'  <style>path{{fill:#1a1a1a;fill-rule:evenodd}}'
            f'@media(prefers-color-scheme:dark){{path{{fill:#f2f2f2}}}}</style>\n'
            f'  {body}\n</svg>\n')

open(OUT + 'favicon.svg', 'w').write(svg(sq, 64))

# --- raster icons; thicken the strokes so they survive the small sizes
def thicken(mask, r):
    m = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                m |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return m

def largest_component(mask):
    """The tree alone: the floating dots are separate components."""
    from collections import deque
    H, W = mask.shape
    seen = np.zeros_like(mask)
    best = None
    for sy, sx in zip(*np.where(mask)):
        if seen[sy, sx]:
            continue
        comp = np.zeros_like(mask)
        q = deque([(sy, sx)])
        seen[sy, sx] = True
        while q:
            y, x = q.popleft()
            comp[y, x] = True
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if best is None or comp.sum() > best.sum():
            best = comp
    return best

TREE = largest_component(sq)

def png(size, grow, dots=True, gain=1.0):
    base = sq if dots else TREE
    m = thicken(base, grow) if grow else base
    big = Image.fromarray(np.where(m, 0, 255).astype('uint8'), 'L')
    alpha = (big.point(lambda v: 255 - v)
                .resize((size, size), Image.LANCZOS)
                .point(lambda v: min(255, int(v * gain))))
    img = Image.new('RGBA', (size, size), (26, 26, 26, 0))
    img.putalpha(alpha)
    return img

png(512, 0).save(OUT + 'favicon-512x512.png')
png(192, 2).save(OUT + 'favicon-192x192.png')
png(180, 2).save(OUT + 'apple-touch-icon-180x180.png')
png(32, 8).save(OUT + 'favicon-32x32.png')
import subprocess, tempfile, os
tmp = tempfile.mkdtemp()
frames = []
for size, grow, dots, gain in ((48, 5, True, 1.0), (32, 8, True, 1.0), (16, 10, False, 1.8)):
    f = os.path.join(tmp, f'{size}.png')
    png(size, grow, dots, gain).save(f)
    frames.append(f)
subprocess.run(['convert', *frames, OUT + 'favicon.ico'], check=True)
print('contours:', len(contours(sq)), 'svg bytes:', len(open(OUT + 'favicon.svg').read()))
