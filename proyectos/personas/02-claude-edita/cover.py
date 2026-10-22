import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'herramientas'))
from render import *
OUT = sys.argv[1]
SEAM = 830
src = Image.open('cover/src.png').convert('RGB')          # 2160x3840
sw, sh = src.size
# photo panel: face large, centred slightly above panel middle
ph = H - SEAM; z = 1.22
cw = sw / z; ch = cw * ph / W
fx, fy = 0.426 * sw, 0.404 * sh
x0 = min(max(fx - cw / 2, 0), sw - cw); y0 = min(max(fy - ch * 0.40, 0), sh - ch)
photo = np.asarray(src.resize((W, ph), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)))
arr = np.empty((H, W, 4), np.uint8); arr[..., 3] = 255
arr[SEAM:, :, 0] = photo[..., 2]; arr[SEAM:, :, 1] = photo[..., 1]; arr[SEAM:, :, 2] = photo[..., 0]
surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W * 4)
ctx = cairo.Context(surf)
# subtle bottom vignette on the photo
for i in range(40):
    ctx.rectangle(0, H - 260 + i * 6.5, W, 7); ctx.set_source_rgba(0, 0, 0, 0.012 * i); ctx.fill()
# paper panel
ctx.save(); ctx.rectangle(0, 0, W, SEAM); ctx.clip(); paper(ctx, 0); ctx.restore()
for i in range(12):
    ctx.rectangle(0, SEAM + i * 2, W, 2); ctx.set_source_rgba(0, 0, 0, 0.18 * (1 - i / 12)); ctx.fill()
ctx.rectangle(0, SEAM - 4, W, 8); rgba(ctx, INK); ctx.fill()

def fit(txt, font, size, maxw, col=INK, spacing=0):
    t = text(txt, font, size, col, spacing=spacing)
    return t, min(1.0, maxw / t[4])

# top chip (outside the 4:5 grid crop, visible full-screen)
lab = text('Claude Code  ·  Opus 5.5', F_BOLD, 44, CREAM); w = lab[4] + 120
ctx.save(); ctx.translate(540, 175)
shadow(ctx, -w / 2, -44, w, 88, 44); rrect(ctx, -w / 2, -44, w, 88, 44); rgba(ctx, TERRA); ctx.fill()
spark(ctx, -w / 2 + 50, 0, 22, CREAM, 7); put(ctx, lab, -w / 2 + 88, 2, ax=0)
ctx.restore()
# headline
l1, s1 = fit('CLAUDE YA EDITA', F_LABEL, 200, 980, INK, 3)
put(ctx, l1, 540, 400, scale=s1)
l2, s2 = fit('TUS VIDEOS', F_LABEL, 250, 900, INK, 4)
hw = l2[4] * s2
highlighter(ctx, 540 - hw / 2 - 28, 520, hw + 56, 205, 1.0, seed=5)
put(ctx, l2, 540, 640, scale=s2)
# stamp across the seam
ctx.save(); ctx.translate(835, SEAM + 6); ctx.rotate(-0.12)
st = text('POR TI', F_LABEL, 104, CREAM, spacing=5); sw_ = st[4] + 64
shadow(ctx, -sw_ / 2, -68, sw_, 136, 16); rrect(ctx, -sw_ / 2, -68, sw_, 136, 16); rgba(ctx, RED); ctx.fill()
rrect(ctx, -sw_ / 2 + 10, -58, sw_ - 20, 116, 10); rgba(ctx, CREAM); ctx.set_line_width(3); ctx.stroke()
put(ctx, st, 0, 6); ctx.restore()
# handwritten note + arrow near the face
note = text('este video lo editó Claude', F_HAND, 66, CREAM, stroke=0, shadow=True)
put(ctx, note, 540, 1790, rot=-0.03)
partial(ctx, jit([(300, 1840), (780, 1832)], 1.2, 4), 1.0, 6, YEL)
surf.flush()
Image.fromarray(np.ascontiguousarray(arr[..., [2, 1, 0]])).save(OUT, quality=95)
print('saved', OUT)
