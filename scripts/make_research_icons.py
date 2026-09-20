#!/usr/bin/env python3
"""Draw the three research-interest icons of _pages/research.html.

Thin, even line work: gently bowed links, round caps, plain round nodes.
Run from the repository root; writes images/research-*.svg.
"""
import math

OUT = 'images/'
INK = '#1a1a1a'


def head(title, stroke=1.1):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
            f'role="img" aria-label="{title}">\n'
            f'  <g fill="none" stroke="{INK}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round">\n')


def link(a, b, bow=0.035, width=None):
    """A soft link: a straight line eased into a very shallow arc."""
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    cx, cy = mx - dy * bow, my + dx * bow
    w = f' stroke-width="{width}"' if width else ''
    return (f'    <path d="M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}"{w}/>')


def polyline(pts, close=True, width=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ('Z' if close else '')
    w = f' stroke-width="{width}"' if width else ''
    return f'    <path d="{d}"{w}/>'


def dots(pts, r=2.0):
    return '\n'.join(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>'
                     for x, y in pts)


def write(name, title, strokes, nodes, stroke=1.1):
    body = head(title, stroke) + '\n'.join(strokes) + '\n  </g>\n' + nodes + '\n</svg>\n'
    open(OUT + name, 'w').write(body)


# --- 1. infrastructure: one network per plane, the planes stacked ------------

def plane(cy, half_w=34, depth=9, shear=6):
    """A plane seen edge-on, as a shallow parallelogram."""
    return [(50 - half_w, cy), (50 - half_w + shear, cy - depth),
            (50 + half_w, cy - depth), (50 + half_w - shear, cy)]


def on_plane(cy, x, front):
    """Place a node on the plane: front row on its lower edge, back row higher."""
    return (x + (0 if front else 5), cy - (0 if front else 7))


planes, strokes, nodes = [24, 57, 90], [], []
for cy in planes:
    strokes.append(polyline(plane(cy), width=0.75))

top = [on_plane(24, 30, True), on_plane(24, 50, False), on_plane(24, 68, True)]
mid = [on_plane(57, 25, True), on_plane(57, 44, False), on_plane(57, 58, True),
       on_plane(57, 74, False)]
low = [on_plane(90, 22, True), on_plane(90, 34, False), on_plane(90, 46, True),
       on_plane(90, 58, False), on_plane(90, 70, True), on_plane(90, 80, False)]

for a, b in ((0, 1), (1, 2), (0, 2)):
    strokes.append(link(top[a], top[b], 0.05 if (a, b) == (0, 2) else -0.03))
for a, b in ((0, 1), (1, 2), (2, 3)):
    strokes.append(link(mid[a], mid[b], 0.04))
for a, b in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)):
    strokes.append(link(low[a], low[b], 0.05))
for a, b in ((top[0], mid[0]), (top[1], mid[1]), (top[2], mid[3])):
    strokes.append(link(a, b, 0.02))
for a, b in ((mid[0], low[0]), (mid[1], low[2]), (mid[2], low[3]), (mid[3], low[5])):
    strokes.append(link(a, b, 0.02))

nodes = dots(top, 2.3) + '\n' + dots(mid, 2.0) + '\n' + dots(low, 1.7)
write('research-infrastructure.svg', 'Networks stacked on three layers', strokes, nodes)

# --- 2. populations: individuals held together by group interactions ---------

A = [(33, 36), (52, 28), (70, 38)]          # a group of three
B = (40, 64)                                # shares one member with the group
C = (72, 70)                                # on its own


def ellipse(cx, cy, rx, ry, deg):
    return (f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
            f'transform="rotate({deg} {cx} {cy})"/>')


def inside(pt, cx, cy, rx, ry, deg):
    t = math.radians(deg)
    dx, dy = pt[0] - cx, pt[1] - cy
    x = dx * math.cos(t) + dy * math.sin(t)
    y = -dx * math.sin(t) + dy * math.cos(t)
    return math.hypot(x / rx, y / ry)


groups = [(51.5, 34, 26, 12.5, 2), (36.5, 50, 20, 11, 76), (72, 70, 10, 9, 0)]
members = [A, [A[0], B], [C]]
for g, ms in zip(groups, members):
    for m in ms:
        assert inside(m, *g) < 0.85, (m, g, inside(m, *g))   # well within the curve

strokes = [ellipse(*g) for g in groups]
nodes = dots(A + [B, C], 2.2)
write('research-populations.svg', 'Individuals bound by group interactions', strokes, nodes)

# --- 3. causal sets: a partial order growing inside a causal diamond ---------

cone = [(50, 7), (91, 50), (50, 93), (9, 50)]
elements = [(50, 84), (35, 69), (63, 67), (50, 57), (27, 52), (72, 49),
            (43, 39), (63, 31), (50, 19)]
order = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 5), (3, 6), (4, 6),
         (5, 7), (6, 8), (7, 8)]
strokes = [polyline(cone, width=0.75)]
strokes += [link(elements[a], elements[b], 0.03 if i % 2 else -0.03)
            for i, (a, b) in enumerate(order)]
write('research-causalsets.svg', 'A causal set inside a causal diamond',
      strokes, dots(elements, 2.0))

print('wrote the three research icons')
