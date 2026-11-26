"""Paint the teapot body's glaze: a few scarlet brush-painted tendrils on white porcelain.

usage: python3 -I tools/tendrils.py WIDTH OUT.tif

Stems rise from the foot, lean a little around the body and thin to a point, with an occasional
side shoot; each stroke swells and thins like a loaded brush, and no stroke crosses another. The
design is vector strokes from a fixed seed, so it rasterizes sharp at any
WIDTH; the height is WIDTH / 4, matching the body's cylindrical map (s around the body, seam at the
handle; t from the rim at 0 to the foot at 1). Strokes wrap in s, so the seam is invisible.
"""

import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PORCELAIN = np.array([247, 246, 241], dtype=np.float32) / 255
SCARLET = np.array([168, 22, 30], dtype=np.float32) / 255
SUPERSAMPLE = 2


def smooth_noise(rng, n, octaves=3):
    phases = [(rng.uniform(1, 3) * 2 ** o, rng.uniform(0, 2 * math.pi), 0.5 ** o) for o in range(octaves)]
    return [sum(a * math.sin(f * math.pi * i / n + p) for f, p, a in phases) for i in range(n + 1)]


def brush_path(rng, x, y, heading, length, bend, aspect, steps=220, curl=0.0):
    wobble = smooth_noise(rng, steps)
    points = []
    for i in range(steps + 1):
        f = i / steps
        points.append((x, y))
        a = heading + bend * f * f + curl * f ** 4 + 0.06 * wobble[i]
        step = length / steps
        x += math.cos(a) * step / aspect
        y += math.sin(a) * step
    return points


def brush_outline(rng, centre, width, aspect, swell=0.35):
    pressure = smooth_noise(rng, len(centre) - 1, octaves=2)
    left, right = [], []
    n = len(centre)
    for i, (x, y) in enumerate(centre):
        xa, ya = centre[max(i - 1, 0)]
        xb, yb = centre[min(i + 1, n - 1)]
        dx, dy = (xb - xa) * aspect, yb - ya
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        f = i / (n - 1)
        body = math.sin(math.pi * min(1.0, 0.15 + f) ** 0.8) ** 0.6 * (1 - f) ** 0.7
        w = width * max(0.0, body * (1 + swell * 0.25 * pressure[i]))
        skew = 0.25 * width * pressure[i] * body
        left.append((x + nx * (w + skew) / aspect, y + ny * (w + skew)))
        right.append((x - nx * (w - skew) / aspect, y - ny * (w - skew)))
    return left + right[::-1]


def clear_of(path, others, margin, aspect, skip=0):
    for x, y in path[skip::4]:
        for ox, oy in others:
            for wrap in (-1.0, 0.0, 1.0):
                if math.hypot((x - ox + wrap) * aspect, y - oy) < margin:
                    return False
    return True


def strokes(rng, aspect):
    shapes = []
    placed = []
    count = 9
    for k in range(count):
        width = rng.uniform(0.03, 0.042)
        for _ in range(60):
            s0 = (k + rng.uniform(-0.25, 0.25)) / count
            side = rng.choice((-1, 1))
            stem = brush_path(rng, s0, rng.uniform(0.97, 1.02), -math.pi / 2 + side * rng.uniform(0.1, 0.3),
                              rng.uniform(0.7, 0.92), side * rng.uniform(0.2, 0.5), aspect,
                              curl=side * rng.uniform(1.4, 2.4))
            if clear_of(stem, placed, 3.5 * width, aspect):
                break
        else:
            continue
        shapes.append((brush_outline(rng, stem, width, aspect), rng.uniform(0.82, 0.95)))
        own = list(stem[::4])
        for _ in range(rng.randint(1, 2)):
            for _ in range(30):
                j = rng.randrange(len(stem) // 4, int(len(stem) * 0.7))
                x, y = stem[j]
                xa, ya = stem[j - 2]
                xb, yb = stem[j + 2]
                along = math.atan2(yb - ya, (xb - xa) * aspect)
                side = rng.choice((-1, 1))
                shoot = brush_path(rng, x, y, along + side * rng.uniform(0.5, 0.9), rng.uniform(0.14, 0.26),
                                   side * rng.uniform(0.6, 1.2), aspect, steps=120,
                                   curl=side * rng.uniform(2.0, 3.5))
                if clear_of(shoot, placed, 2.5 * width, aspect) and clear_of(shoot, own, 1.6 * width, aspect, skip=55):
                    shapes.append((brush_outline(rng, shoot, width * 0.6, aspect), rng.uniform(0.75, 0.9)))
                    own += shoot[::4]
                    break
        placed += own
    return shapes


def main():
    width = int(sys.argv[1])
    out = sys.argv[2]
    height = width // 4
    aspect = width / height
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    rng = random.Random(1975)
    ink = np.zeros((big_h, big_w), dtype=np.float32)
    for shape, density in strokes(rng, aspect):
        for offset in (-1.0, 0.0, 1.0):
            pts = [((x + offset) * big_w, y * big_h) for x, y in shape]
            x0 = max(int(min(p[0] for p in pts)) - 4, 0)
            x1 = min(int(max(p[0] for p in pts)) + 5, big_w)
            y0 = max(int(min(p[1] for p in pts)) - 4, 0)
            y1 = min(int(max(p[1] for p in pts)) + 5, big_h)
            if x1 <= x0 or y1 <= y0:
                continue
            mask = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 0.6))
            a = np.asarray(mask, dtype=np.float32) / 255 * density
            region = ink[y0:y1, x0:x1]
            ink[y0:y1, x0:x1] = np.maximum(region, a)
    colour = PORCELAIN[None, None, :] * (1 - ink[..., None]) + SCARLET[None, None, :] * ink[..., None]
    image = Image.fromarray((np.clip(colour, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    image = image.resize((width, height), Image.LANCZOS)
    image.save(out, compression="tiff_lzw")


if __name__ == "__main__":
    main()
