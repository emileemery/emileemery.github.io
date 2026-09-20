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


def write(name, title, strokes, nodes, stroke=1.1, wash=None):
    fill = ''
    if wash:                              # a barely tinted background shape
        pts, colour = wash
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'
        fill = f'    <path d="{d}" fill="{colour}" stroke="none"/>\n'
    body = (head(title, stroke) + fill + '\n'.join(strokes)
            + '\n  </g>\n' + nodes + '\n</svg>\n')
    open(OUT + name, 'w').write(body)


# --- 1. infrastructure: a meshed network feeding a branching one -----------

PLANE_W, PLANE_SHEAR = 46, 12


def plane(cy, depth):
    """A plane seen edge-on, as a wide parallelogram."""
    return [(50 - PLANE_W, cy), (50 - PLANE_W + PLANE_SHEAR, cy - depth),
            (50 + PLANE_W, cy - depth), (50 + PLANE_W - PLANE_SHEAR, cy)]


def on(cy, depth, u, v, margin=0.07):
    """A point at (u, v) in the plane's own frame, kept clear of its edges."""
    assert margin <= u <= 1 - margin and margin <= v <= 1 - margin, (u, v)
    return (50 - PLANE_W + (2 * PLANE_W - PLANE_SHEAR) * u + PLANE_SHEAR * v,
            cy - depth * v)


TOP, TOP_D = 36, 28
LOW, LOW_D = 96, 32

mesh = [on(TOP, TOP_D, u, v) for u, v in
        ((0.14, 0.24), (0.33, 0.74), (0.63, 0.80), (0.86, 0.38), (0.49, 0.18))]
mesh_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 4)]

# the lower network branches out in every direction over its own plane
tree_uv = {
    'root': (0.45, 0.80), 'a': (0.28, 0.66), 'b': (0.67, 0.71), 'c': (0.62, 0.46),
    'a1': (0.13, 0.75), 'a2': (0.25, 0.41), 'a3': (0.10, 0.27),
    'b1': (0.88, 0.57), 'c1': (0.39, 0.17), 'c2': (0.76, 0.24),
}
tree = {k: on(LOW, LOW_D, *uv) for k, uv in tree_uv.items()}
tree_edges = [('root', 'a'), ('root', 'b'), ('root', 'c'), ('a', 'a1'),
              ('a', 'a2'), ('a2', 'a3'), ('b', 'b1'), ('c', 'c1'), ('c', 'c2')]
leaves = ('a1', 'a3', 'b1', 'c1', 'c2')

strokes = [polyline(plane(TOP, TOP_D), width=0.75),
           polyline(plane(LOW, LOW_D), width=0.75)]
for a, b in mesh_edges:                   # straight lines: this drawing is built
    strokes.append(link(mesh[a], mesh[b], 0))          # of planes, not of curves
for a, b in ((mesh[0], tree['a']), (mesh[4], tree['c']),
             (mesh[2], tree['root']), (mesh[3], tree['b'])):
    strokes.append(link(a, b, 0))         # the meshed layer feeds the branching one
for a, b in tree_edges:
    strokes.append(link(tree[a], tree[b], 0))

nodes = (dots(mesh, 2.3) + '\n'
         + dots([tree[k] for k in tree if k not in leaves], 2.0) + '\n'
         + dots([tree[k] for k in leaves], 1.7))
write('research-infrastructure.svg', 'A meshed network above a branching one',
      strokes, nodes)

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
      strokes, dots(elements, 2.0), wash=(cone, '#f2f2f2'))

print('wrote the three research icons')
