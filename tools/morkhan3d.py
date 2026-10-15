"""Renders a spinning 'CGI' Morkhan head, the way a 2000 fan page would have had one made in a
shareware 3D program: chrome-ish shading, glowing eyes, purple lights, 16 frames, dithered GIF.

    python3 tools/morkhan3d.py

Writes users/Kanykei5093/morkhan.gif (96x100) and morkhan_krug.gif (48x48).
A small sphere-tracing renderer over signed distance functions, in numpy.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "users", "Kanykei5093")


def length(v):
    return np.sqrt((v * v).sum(-1))


def sd_ellipsoid(p, c, r):
    q = (p - c) / r
    k0 = length(q)
    k1 = length(q / r)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sd_capsule(p, a, b, ra, rb):
    """Tapered capsule from a (radius ra) to b (radius rb)."""
    pa, ba = p - a, b - a
    h = np.clip((pa * ba).sum(-1) / (ba * ba).sum(), 0, 1)
    return length(pa - ba * h[..., None]) - (ra + (rb - ra) * h)


def sd_sphere(p, c, r):
    return length(p - c) - r


def sd_torus_x(p, c, R, r):
    """Torus lying in the y-z plane (a nose ring seen from the front)."""
    q = p - c
    xy = np.stack([np.sqrt(q[..., 1] ** 2 + q[..., 2] ** 2) - R, q[..., 0]], -1)
    return length(xy) - r


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


V = lambda *a: np.array(a, dtype=float)


def scene(p):
    """Returns (distance, material id): 0 head, 1 horn, 2 eye, 3 ring."""
    head = sd_ellipsoid(p, V(0, 0.05, 0), V(0.52, 0.62, 0.5))
    snout = sd_ellipsoid(p, V(0, -0.5, 0.22), V(0.34, 0.3, 0.34))
    brow = sd_ellipsoid(p, V(0, 0.3, 0.18), V(0.5, 0.18, 0.32))
    d_head = smin(smin(head, snout, 0.2), brow, 0.12)
    for s in (-1, 1):
        ear = sd_ellipsoid(p, V(0.58 * s, 0.22, -0.05), V(0.22, 0.09, 0.08))
        d_head = smin(d_head, ear, 0.06)
    horn = 1e9
    for s in (-1, 1):                                   # each horn: three tapered segments curving up
        pts = [V(0.36 * s, 0.42, 0.02), V(0.75 * s, 0.55, 0.0), V(1.0 * s, 0.85, 0.05), V(0.98 * s, 1.18, 0.12)]
        rads = [0.13, 0.1, 0.065, 0.02]
        for i in range(3):
            horn = np.minimum(horn, sd_capsule(p, pts[i], pts[i + 1], rads[i], rads[i + 1]))
    eye = np.minimum(sd_sphere(p, V(-0.21, 0.12, 0.39), 0.095), sd_sphere(p, V(0.21, 0.12, 0.39), 0.095))
    ring = sd_torus_x(p, V(0, -0.72, 0.42), 0.11, 0.025)
    d = d_head
    mat = np.zeros(d.shape, int)
    for i, dd in ((1, horn), (2, eye), (3, ring)):
        m = dd < d
        d = np.where(m, dd, d)
        mat = np.where(m, i, mat)
    return d, mat


def normal(p):
    e = 1e-3
    n = np.stack([scene(p + V(e, 0, 0))[0] - scene(p - V(e, 0, 0))[0],
                  scene(p + V(0, e, 0))[0] - scene(p - V(0, e, 0))[0],
                  scene(p + V(0, 0, e))[0] - scene(p - V(0, 0, e))[0]], -1)
    return n / np.maximum(length(n)[..., None], 1e-9)


def render(w, h, angle, ss=2):
    W, H = w * ss, h * ss
    y, x = np.mgrid[0:H, 0:W]
    u = (x + 0.5) / W * 2 - 1
    v = 1 - (y + 0.5) / H * 2
    u = u * W / H
    ro = V(0, 0.22, 3.0)
    rd = np.stack([u * 0.62, v * 0.62 + 0.0, -np.ones_like(u)], -1)
    rd /= length(rd)[..., None]
    ca, sa = math.cos(angle), math.sin(angle)               # rotate the object = rotate the camera around it
    R = np.array([[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]])
    ro_r = ro @ R.T
    rd_r = rd @ R.T
    t = np.full(u.shape, 2.0)
    hit = np.zeros(u.shape, bool)
    live = np.ones(u.shape, bool)
    ro_f, rd_f = np.broadcast_to(ro_r, rd_r.shape), rd_r
    for _ in range(70):                                     # march only the rays still travelling
        idx = np.nonzero(live)
        if not idx[0].size:
            break
        p = ro_f[idx] + rd_f[idx] * t[idx][:, None]
        d, _m = scene(p)
        got = d < 1e-3
        hit[idx[0][got], idx[1][got]] = True
        t[idx] += np.where(got, 0, d * 0.9)
        live[idx] = ~got & (t[idx] < 6)
    p = ro_r + rd_r * t[..., None]
    _, mat = scene(p)
    n = normal(p)
    lights = [(V(-0.6, 0.8, 0.6) @ R.T, V(0.95, 0.85, 1.0), 1.0),     # key, cool white
              (V(0.9, 0.1, -0.4) @ R.T, V(0.9, 0.2, 1.0), 0.9),       # violet rim
              (V(0.0, -1.0, 0.3) @ R.T, V(1.0, 0.1, 0.4), 0.35)]      # magenta from below
    base = {0: V(0.22, 0.08, 0.32), 1: V(0.92, 0.86, 0.72), 2: V(1.0, 0.1, 0.15), 3: V(1.0, 0.8, 0.3)}
    spec_k = {0: 0.9, 1: 0.5, 2: 0.0, 3: 1.0}
    col = np.zeros(u.shape + (3,))
    for m, b in base.items():
        sel = hit & (mat == m)
        if not sel.any():
            continue
        nn = n[sel]
        vv = -rd_r[sel]
        c = np.tile(b * 0.12, (nn.shape[0], 1))
        for L, lc, li in lights:
            L = L / np.linalg.norm(L)
            diff = np.clip((nn * L).sum(-1), 0, 1)
            hv = L + vv
            hv /= length(hv)[..., None]
            spec = np.clip((nn * hv).sum(-1), 0, 1) ** 40
            c += (b * diff[:, None] + spec_k[m] * spec[:, None]) * lc * li
        # fake chrome: reflect a purple sky over a black floor
        refl = nn * 2 * (nn * vv).sum(-1)[:, None] - vv
        sky = np.clip(refl[:, 1], 0, 1)[:, None]
        if m in (0, 3):
            c += (sky * V(0.5, 0.25, 0.9) + (1 - sky) * V(0.02, 0.0, 0.05)) * (0.45 if m == 0 else 0.6)
        if m == 2:
            c = np.tile(V(1.0, 0.05, 0.08), (nn.shape[0], 1))   # glowing red, unlit
        col[sel] = c
    img = np.clip(col, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    return im


def stars(w, h, seed=7):
    rnd = np.random.default_rng(seed)
    pts = rnd.integers(0, [w, h], size=(w * h // 120, 2))
    return pts


def save(frames, path, ms=90):
    pal_src = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        pal_src.paste(f, (0, i * f.height))
    pal = pal_src.quantize(48, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, disposal=1)


def main():
    n = 16
    big, small = [], []
    sp = stars(96, 100)
    for k in range(n):
        a = 2 * math.pi * k / n
        f = render(96, 100, a)
        d = ImageDraw.Draw(f)
        for i, (x, y) in enumerate(sp):                    # twinkling dots behind, black elsewhere
            if f.getpixel((int(x), int(y))) == (0, 0, 0) and (i + k) % 3:
                d.point((int(x), int(y)), fill=(120, 60, 200))
        big.append(f)
        s = render(48, 48, a, ss=3)
        ring = Image.new("RGB", (48, 48), (0, 0, 0))       # 'krug' = circle: a violet ring behind the head
        ImageDraw.Draw(ring).ellipse((1, 1, 46, 46), outline=(140, 60, 230), width=2)
        mask = s.convert("L").point(lambda v: 255 if v > 6 else 0)
        ring.paste(s, (0, 0), mask)
        small.append(ring)
    save(big, os.path.join(OUT, "morkhan.gif"))
    save(small, os.path.join(OUT, "morkhan_krug.gif"))
    print("ok")


if __name__ == "__main__":
    main()
