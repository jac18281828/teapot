"""Paint the teapot body's glaze: a few scarlet brush-painted tendrils on white porcelain.

usage: python3 -I tools/tendrils.py WIDTH OUT.tif

A composed handful of stems rise from the foot around the body's front, FRONT: a tall one pulled
well up, others pulled less far, the farther ones paler and finer so they sit behind. Each
stroke swells and thins like a loaded brush, with a side shoot here and there. The design is
vector strokes, so it rasterizes sharp at any WIDTH; the height is WIDTH / 4, matching the body's cylindrical map (s around the body, seam at the
handle; t from the rim at 0 to the foot at 1). Strokes wrap in s, so the seam is invisible.
"""

import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PORCELAIN = np.array([247, 246, 241], dtype=np.float32) / 255
SCARLET = np.array([118, 10, 16], dtype=np.float32) / 255
WASH = np.array([160, 28, 30], dtype=np.float32) / 255
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


def brush_outline(rng, centre, width, aspect, swell=0.9):
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
        body = (1 - f) ** 0.9 * (1 + 0.35 * math.exp(-f * 12))
        w = width * max(0.0, body * (1 + swell * 0.3 * pressure[i]))
        skew = 0.25 * width * pressure[i] * body
        left.append((x + nx * (w + skew) / aspect, y + ny * (w + skew)))
        right.append((x - nx * (w - skew) / aspect, y - ny * (w - skew)))
    return left + right[::-1]


FRONT = 0.25

COMPOSITION = (
    (FRONT - 0.035, 0.86, 0.32, 2.0, 0.024, 0.0, ((0.42, -1),)),
    (FRONT + 0.05, 0.58, -0.22, -1.8, 0.017, 0.65, ()),
    (FRONT - 0.17, 0.34, -0.30, -2.3, 0.014, 0.35, ()),
    (FRONT - 0.085, 0.55, -0.30, -2.0, 0.018, 0.1, ((0.5, 1),)),
    (FRONT + 0.115, 0.30, 0.30, 2.2, 0.013, 0.4, ()),
    (FRONT + 0.15, 0.48, 0.38, 2.2, 0.019, 0.15, ((0.5, 1),)),
    (FRONT + 0.40, 0.72, 0.28, 1.9, 0.021, 0.2, ((0.45, -1),)),
    (FRONT + 0.58, 0.40, -0.35, -2.1, 0.015, 0.55, ()),
)


def strokes(rng, aspect):
    shapes = []
    for s0, length, lean, curl, width, depth, shoots in COMPOSITION:
        stem = brush_path(rng, s0, 1.0, -math.pi / 2 + lean * 0.4, length, lean, aspect, curl=curl)
        shapes.append((brush_outline(rng, stem, width, aspect), depth))
        for at, side in shoots:
            j = int(len(stem) * at)
            x, y = stem[j]
            xa, ya = stem[j - 2]
            xb, yb = stem[j + 2]
            along = math.atan2(yb - ya, (xb - xa) * aspect)
            shoot = brush_path(rng, x, y, along + side * 0.75, length * 0.3, side * 0.9, aspect, steps=120,
                               curl=side * 2.6)
            shapes.append((brush_outline(rng, shoot, width * 0.6, aspect), depth))
    return sorted(shapes, key=lambda shape: -shape[1])


def main():
    width = int(sys.argv[1])
    out = sys.argv[2]
    height = width // 4
    aspect = width / height
    big_w, big_h = width * SUPERSAMPLE, height * SUPERSAMPLE
    rng = random.Random(1975)
    load = np.asarray(Image.effect_noise((big_w // 64 + 1, big_h // 64 + 1), 60).resize((big_w, big_h), Image.BICUBIC),
                      dtype=np.float32) / 255
    paint = WASH[None, None, :] + (SCARLET - WASH)[None, None, :] * np.clip(0.35 + load, 0, 1)[..., None]
    colour = np.broadcast_to(PORCELAIN, (big_h, big_w, 3)).copy()
    for shape, depth in strokes(rng, aspect):
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
            mask = mask.filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 0.9))
            a = (np.asarray(mask, dtype=np.float32) / 255 * (0.95 - 0.4 * depth))[..., None]
            ink = paint[y0:y1, x0:x1] * (1 - 0.55 * depth) + PORCELAIN * 0.55 * depth
            colour[y0:y1, x0:x1] = colour[y0:y1, x0:x1] * (1 - a) + ink * a
    image = Image.fromarray((np.clip(colour, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    image = image.resize((width, height), Image.LANCZOS)
    image.save(out, compression="tiff_lzw")


if __name__ == "__main__":
    main()
