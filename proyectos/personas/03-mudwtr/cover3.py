import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas'))
from render import *
OUT = sys.argv[1]
# ---- background: deep purple + sunburst + grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = 540, 1000
ang = np.arctan2(yy - cy, xx - cx); rad = np.hypot(xx - cx, yy - cy)
rays = (np.sin(ang * 14) > 0).astype(np.float32)
base = np.array([0x2A, 0x16, 0x47], np.float32); ray = np.array([0x3D, 0x1F, 0x63], np.float32)
glow = np.clip(1 - rad / 1300, 0, 1)[..., None]
img = base + (ray - base) * rays[..., None] * 0.9 + np.array([90, 40, 70], np.float32) * glow ** 2 * 0.5
img += np.random.default_rng(1).normal(0, 4, (H, W, 1))
img = np.clip(img, 0, 255).astype(np.uint8)
arr = np.empty((H, W, 4), np.uint8); arr[..., 3] = 255
arr[..., 0] = img[..., 2]; arr[..., 1] = img[..., 1]; arr[..., 2] = img[..., 0]
surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W * 4); ctx = cairo.Context(surf)
# ---- title (behind the person)
def line(txt, y, size, col, spacing=4, maxw=1000):
    t = text(txt, F_LABEL, size, col, spacing=spacing); s = min(1.0, maxw / t[4]); put(ctx, t, 540, y, scale=s); return t[4] * s
line('LAS MEJORES', 360, 120, CREAM, 8)
line('CAMPAÑAS DE', 530, 200, CREAM, 5)
w = line('MARKETING', 735, 240, YEL, 6)
surf.flush()
# ---- person cut-out
src = Image.open('cover/full/a.jpg').convert('RGB'); sw, sh = src.size
m = Image.open('cover/fullm/a.png').convert('L').resize((sw, sh), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
s = 0.40; head_top_src = 0.165 * sh; dy = 700 - head_top_src * s; dx = 540 - 0.5 * sw * s
pw, ph = int(sw * s), int(sh * s)
ps = np.asarray(src.resize((pw, ph), Image.LANCZOS), np.float32); pm = np.asarray(m.resize((pw, ph), Image.BILINEAR), np.float32) / 255
pm = np.clip((pm - 0.1) / 0.8, 0, 1)
fx = np.clip(np.minimum(np.arange(pw), pw - 1 - np.arange(pw)) / 110.0, 0, 1) ** 1.5   # fade the cut frame edges
pm = (pm * fx[None, :])[..., None]
x0, y0 = int(dx), int(dy)
xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + pw), min(H, y0 + ph)
reg = arr[ya:yb, xa:xb, :3].astype(np.float32)
pp = ps[ya - y0:yb - y0, xa - x0:xb - x0][..., ::-1]; mm = pm[ya - y0:yb - y0, xa - x0:xb - x0]
# soft rim shadow behind the person for separation
arr[ya:yb, xa:xb, :3] = (pp * mm + reg * (1 - mm)).astype(np.uint8)
surf.mark_dirty()
# ---- top chip (outside the 4:5 grid crop)
lab = text('Caso real: MUD\\WTR', F_BOLD, 46, CREAM); cw = lab[4] + 70
ctx.save(); ctx.translate(540, 175); shadow(ctx, -cw / 2, -45, cw, 90, 45)
rrect(ctx, -cw / 2, -45, cw, 90, 45); rgba(ctx, TERRA); ctx.fill(); put(ctx, lab, 0, 2); ctx.restore()
# ---- phone with the game
g = Image.open('cover/game.png').convert('RGBA'); gw, gh = 250, 502
gs, gb = pil_surface(g.resize((gw, gh), Image.LANCZOS))
ctx.save(); ctx.translate(175, 1490); ctx.rotate(-0.12)
shadow(ctx, -gw / 2 - 14, -gh / 2 - 14, gw + 28, gh + 28, 44, 0.45, 16)
rrect(ctx, -gw / 2 - 14, -gh / 2 - 14, gw + 28, gh + 28, 44); rgba(ctx, INK); ctx.fill()
ctx.save(); rrect(ctx, -gw / 2, -gh / 2, gw, gh, 32); ctx.clip(); ctx.set_source_surface(gs, -gw / 2, -gh / 2); ctx.paint(); ctx.restore()
ctx.restore()
# ---- 2026 stamp
tt = text('2026', F_LABEL, 160, INK, spacing=6); sw_ = tt[4] + 70
ctx.save(); ctx.translate(885, 1400); ctx.rotate(0.1)
shadow(ctx, -sw_ / 2, -95, sw_, 190, 22, 0.35, 12); rrect(ctx, -sw_ / 2, -95, sw_, 190, 22); rgba(ctx, YEL); ctx.fill()
rrect(ctx, -sw_ / 2 + 12, -83, sw_ - 24, 166, 14); rgba(ctx, INK); ctx.set_line_width(4); ctx.stroke()
put(ctx, tt, 0, 12); ctx.restore()
# ---- bottom note
note = text('un juego que regala descuentos', F_HAND, 62, CREAM, shadow=True)
put(ctx, note, 540, 1800, rot=-0.03)
surf.flush()
Image.fromarray(np.ascontiguousarray(arr[..., [2, 1, 0]])).save(OUT, quality=95)
print('saved', OUT)
