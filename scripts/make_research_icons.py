#!/usr/bin/env python3
"""Draw the three research-interest icons in the ink style of images/profile.png.

Each icon is an SVG on a 100x100 viewBox: wobbly, slightly uneven strokes and
round ink blobs for the nodes, so the drawings look like the tree of the logo.
Run from the repository root; writes images/research-*.svg.
"""
import math
import random

OUT = 'images/'
W = 100.0

# --- a steady but not quite straight hand -----------------------------------

def noise(seed, freq=1.0):
    """Smooth 1-D noise in [-1, 1], as a sum of a few sines."""
    rng = random.Random(seed)
    waves = [(rng.uniform(0.6, 1.0) / (i + 1), rng.uniform(0.7, 1.6) * freq * (i + 1),
              rng.uniform(0, 2 * math.pi)) for i in range(3)]
    norm = sum(a for a, _, _ in waves)
    return lambda t: sum(a * math.sin(f * t + p) for a, f, p in waves) / norm


def resample(pts, step=1.2):
    """Densify a polyline, with rounded corners."""
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append(pts[-1])
    if len(out) > 4:                      # light smoothing, to round the joints
        sm = [out[0]]
        for i in range(1, len(out) - 1):
            sm.append(((out[i - 1][0] + 2 * out[i][0] + out[i + 1][0]) / 4,
                       (out[i - 1][1] + 2 * out[i][1] + out[i + 1][1]) / 4))
        sm.append(out[-1])
        out = sm
    return out


def stroke(pts, seed, width=1.5, wobble=0.5, closed=False, taper=0.75):
    """An ink stroke along pts, returned as a filled SVG path."""
    if closed:
        pts = list(pts) + [pts[0]]
    p = resample(pts)
    n = len(p)
    off = noise(seed, 2.2)
    thick = noise(seed + 977, 1.7)
    length = sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(n - 1))
    left, right, s = [], [], 0.0
    for i in range(n):
        a = p[max(i - 1, 0)]
        b = p[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        if i:
            s += math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1])
        u = s / (length or 1.0)
        x = p[i][0] + nx * off(u * 6) * wobble
        y = p[i][1] + ny * off(u * 6) * wobble
        w = width / 2 * (0.82 + 0.22 * thick(u * 5))
        if not closed:                    # the pen presses less at both ends
            e = min(s, length - s) / (taper * width) if width else 1
            w *= min(1.0, 0.45 + 0.55 * min(1.0, e))
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    path = left + right[::-1]
    d = 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in path) + 'Z'
    return f'  <path d="{d}"/>'


def blob(cx, cy, r, seed):
    """A node: a small, not quite round ink dot."""
    n = noise(seed, 1.0)
    pts = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        rr = r * (1 + 0.16 * n(a * 1.6))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'
    return f'  <path d="{d}"/>'


def svg(parts, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
            f'role="img" aria-label="{title}">\n'
            f'  <style>path{{fill:#1a1a1a;fill-rule:evenodd}}</style>\n'
            + '\n'.join(parts) + '\n</svg>\n')


def link(a, b, seed, width=1.4, wobble=0.45):
    return stroke([a, b], seed, width, wobble)


# --- 1. infrastructure: a network of networks, transmission down to consumers

top = [(30, 19), (52, 13), (73, 22)]
mid = [(25, 50), (38, 55), (51, 48), (64, 55), (77, 51)]
parts = []
for i, (a, b) in enumerate([(top[0], top[1]), (top[1], top[2]), (top[0], top[2])]):
    parts.append(link(a, b, 10 + i, 1.5))
for i, (a, b) in enumerate([(top[0], mid[0]), (top[1], mid[2]), (top[2], mid[4])]):
    parts.append(link(a, b, 20 + i, 1.3))
for i in range(len(mid) - 1):
    parts.append(link(mid[i], mid[i + 1], 30 + i, 1.4))
leaves = []
for i, (mx, my) in enumerate(mid):
    for j, dx in enumerate((-7.5, 0.5, 8)):
        if (i + j) % 3 == 1 and i not in (0, 4):
            continue
        lx, ly = mx + dx * 1.25, my + 24 + (j % 2) * 5
        parts.append(link((mx, my), (lx, ly), 40 + 3 * i + j, 1.0, 0.35))
        leaves.append((lx, ly))
for i, (x, y) in enumerate(top):
    parts.append(blob(x, y, 3.2, 60 + i))
for i, (x, y) in enumerate(mid):
    parts.append(blob(x, y, 2.5, 70 + i))
for i, (x, y) in enumerate(leaves):
    parts.append(blob(x, y, 1.6, 80 + i))
open(OUT + 'research-infrastructure.svg', 'w').write(
    svg(parts, 'A layered infrastructure network'))

# --- 2. populations: individuals bound by group (higher-order) interactions

def ellipse(cx, cy, rx, ry, rot, seed, width=1.35):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return stroke(pts, seed, width, 0.45, closed=True)

dots = [(32, 38), (53, 29), (70, 41),        # a group of three
        (40, 65),                           # shares one member with it
        (71, 72)]                           # on its own
parts = [
    ellipse(52, 35, 29, 14, -0.10, 110),
    ellipse(35, 51, 13, 21, 0.32, 111),
    ellipse(71, 72, 11, 9, 0.00, 112),
]
for i, (x, y) in enumerate(dots):
    parts.append(blob(x, y, 2.6, 120 + i))
open(OUT + 'research-populations.svg', 'w').write(
    svg(parts, 'Individuals bound by group interactions'))

# --- 3. causal sets: a partial order growing inside a causal diamond

cone = [(50, 7), (91, 50), (50, 93), (9, 50)]
parts = [stroke(cone, 130, 1.0, 0.5, closed=True)]
elements = [(50, 84), (35, 69), (63, 67), (50, 57), (27, 52), (72, 49),
            (43, 39), (63, 31), (50, 19)]
order = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 5), (3, 6), (4, 6),
         (5, 7), (6, 8), (7, 8)]
for i, (a, b) in enumerate(order):
    parts.append(link(elements[a], elements[b], 140 + i, 1.3))
for i, (x, y) in enumerate(elements):
    parts.append(blob(x, y, 2.6, 160 + i))
open(OUT + 'research-causalsets.svg', 'w').write(
    svg(parts, 'A causal set inside a causal diamond'))

print('wrote research-infrastructure.svg, research-populations.svg, research-causalsets.svg')
