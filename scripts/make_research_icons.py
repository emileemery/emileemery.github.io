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

def plane(cy, half_w=34, depth=9, shear=6):
    """A plane seen edge-on, as a shallow parallelogram."""
    return [(50 - half_w, cy), (50 - half_w + shear, cy - depth),
            (50 + half_w, cy - depth), (50 + half_w - shear, cy)]


mesh = [(22, 33), (40, 23), (60, 23), (77, 33), (49, 33)]
mesh_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (1, 4)]
root = (54, 72)
forks = [(41, 79), (68, 79)]
leaves = [(30, 87), (47, 87), (59, 87), (78, 87)]
tree_edges = [(root, forks[0]), (root, forks[1]),
              (forks[0], leaves[0]), (forks[0], leaves[1]),
              (forks[1], leaves[2]), (forks[1], leaves[3])]

strokes = [polyline(plane(33, depth=12), width=0.75),
           polyline(plane(87, depth=15), width=0.75)]
for i, (a, b) in enumerate(mesh_edges):
    strokes.append(link(mesh[a], mesh[b], 0.05 if i % 2 else -0.04))
for a, b in ((mesh[0], forks[0]), (mesh[4], root), (mesh[3], forks[1])):
    strokes.append(link(a, b, 0.02))      # the meshed layer feeds the tree
for i, (a, b) in enumerate(tree_edges):
    strokes.append(link(a, b, 0.03 if i % 2 else -0.03))

nodes = dots(mesh, 2.3) + '\n' + dots([root] + forks, 2.0) + '\n' + dots(leaves, 1.7)
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
