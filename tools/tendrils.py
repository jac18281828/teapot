"""Paint the teapot body's glaze: scarlet hand-painted tendrils on white porcelain.

usage: python3 -I tools/tendrils.py WIDTH OUT.tif

The design is vector strokes from a fixed seed, so it rasterizes sharp at any WIDTH; the height is
WIDTH / 4, matching the body's cylindrical map (s around the body, seam at the handle; t from the
rim at the top to the foot at the bottom). Strokes wrap in s, so the seam is invisible.
"""

import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

PORCELAIN = (247, 246, 241)
SCARLET = (176, 18, 26)
SUPERSAMPLE = 2


def vine_path(rng, phase, base, amp):
    k1 = rng.choice((2, 3))
    k2 = k1 * 2 + rng.choice((1, 3))
    a2 = amp * rng.uniform(0.15, 0.3)
    p2 = rng.uniform(0, 2 * math.pi)
    points = []
    for i in range(1601):
        s = i / 1600
        t = base + amp * math.sin(2 * math.pi * k1 * s + phase) + a2 * math.sin(2 * math.pi * k2 * s + p2)
        points.append((s, t))
    return points


def tapered_outline(centre, w0, w1, aspect):
    left, right = [], []
    n = len(centre)
    for i, (x, y) in enumerate(centre):
        xa, ya = centre[max(i - 1, 0)]
        xb, yb = centre[min(i + 1, n - 1)]
        dx, dy = (xb - xa) * aspect, yb - ya
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        f = i / (n - 1)
        w = (w0 + (w1 - w0) * f) * (0.85 + 0.15 * math.sin(f * 9.0))
        left.append((x + nx * w / aspect, y + ny * w))
        right.append((x - nx * w / aspect, y - ny * w))
    return left + right[::-1]


def curl(rng, x, y, heading, size, turns, aspect):
    direction = rng.choice((-1, 1))
    points = []
    steps = 140
    for i in range(steps + 1):
        f = i / steps
        a = heading + direction * turns * 2 * math.pi * f
        r = size * (1 - f) ** 1.4
        points.append((x, y))
        x += math.cos(a) * r * 0.005 / aspect
        y += math.sin(a) * r * 0.005
    return points


def leaf(x, y, heading, length, width, aspect):
    points = []
    for i in range(41):
        f = i / 40
        along = length * f
        half = width * math.sin(math.pi * f) ** 1.3
        points.append((along, half))
    outline = points + [(a, -h) for a, h in reversed(points)]
    c, s = math.cos(heading), math.sin(heading)
    return [(x + (a * c - h * s) / aspect, y + (a * s + h * c)) for a, h in outline]


def strokes(rng, aspect):
    shapes = []
    for base, amp, w in ((0.30, 0.07, 0.0030), (0.52, 0.09, 0.0036), (0.74, 0.06, 0.0027)):
        path = vine_path(rng, rng.uniform(0, 2 * math.pi), base, amp)
        for k in range(0, len(path) - 1, 200):
            segment = path[k:k + 201]
            shapes.append(tapered_outline(segment, w, w * 0.9, aspect))
        for _ in range(rng.randint(24, 32)):
            i = rng.randrange(5, len(path) - 5)
            x, y = path[i]
            xa, ya = path[i - 3]
            xb, yb = path[i + 3]
            heading = math.atan2(yb - ya, (xb - xa) * aspect) + rng.choice((-1, 1)) * rng.uniform(0.6, 1.3)
            size = rng.uniform(0.6, 1.1)
            tendril = curl(rng, x, y, heading, size, rng.uniform(1.2, 2.2), aspect)
            shapes.append(tapered_outline(tendril, w * 0.6, 0.0002, aspect))
            for _ in range(rng.randint(0, 2)):
                j = rng.randrange(10, len(tendril) // 2)
                lx, ly = tendril[j]
                shapes.append(leaf(lx, ly, heading + rng.uniform(-1.8, 1.8), rng.uniform(0.04, 0.07),
                                   rng.uniform(0.005, 0.008), aspect))
    return shapes


def main():
    width = int(sys.argv[1])
    out = sys.argv[2]
    height = width // 4
    aspect = width / height
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    image = Image.new("RGB", (big_w, big_h), PORCELAIN)
    draw = ImageDraw.Draw(image)
    rng = random.Random(1975)
    for shape in strokes(rng, aspect):
        for offset in (-1.0, 0.0, 1.0):
            draw.polygon([((x + offset) * big_w, y * big_h) for x, y in shape], fill=SCARLET)
    image = image.filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 0.35))
    image = image.resize((width, height), Image.LANCZOS)
    image.save(out, compression="tiff_lzw")


if __name__ == "__main__":
    main()
