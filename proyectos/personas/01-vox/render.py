import ctypes.util as _u
_f = _u.find_library
_u.find_library = lambda n: '/opt/homebrew/lib/libcairo.2.dylib' if 'cairo' in n else _f(n)
import cairocffi as cairo
import numpy as np, math, subprocess, sys, os, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
SW, SH = 1440, 2560
DUR = 14.26

# ---------- palette ----------
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)
INK = hexc('1B1B1B'); PAPER = hexc('F3EDE2'); CREAM = hexc('FFFDF7')
YEL = hexc('FFD84D'); TERRA = hexc('D97757'); RED = hexc('E5484D')
TILE = ['D97757', '6A9BD1', 'E8B84A', '7FB685', 'B08CD6', 'E88F7A']

# ---------- fonts ----------
HOME = os.path.expanduser('~')
def fpath(*c):
    for p in c:
        if os.path.exists(p): return p
    raise FileNotFoundError(c)
F_SUB = fpath(HOME+'/Library/Fonts/Montserrat-ExtraBold.ttf', '/Library/Fonts/Montserrat-ExtraBold.ttf')
F_BOLD = fpath(HOME+'/Library/Fonts/Montserrat-Bold.ttf', '/Library/Fonts/Montserrat-Bold.ttf')
F_SERIF = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
F_LABEL = '/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf'
F_HAND = '/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf'
F_MONO = '/System/Library/Fonts/Menlo.ttc'

# ---------- easing ----------
def c01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def prog(t, a, d): return c01((t - a) / d)
def eo(x): x = c01(x); return 1 - (1 - x) ** 3
def eio(x): x = c01(x); return 4*x*x*x if x < .5 else 1 - (-2*x + 2) ** 3 / 2
def eback(x, s=1.9):
    x = c01(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2

# ---------- text -> cairo surfaces (cached) ----------
_cache = {}
def pil_surface(img):
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    al = a[..., 3:4] / 255.0
    bgra = np.empty(a.shape, np.uint8)
    bgra[..., 0] = (a[..., 2:3] * al)[..., 0]; bgra[..., 1] = (a[..., 1:2] * al)[..., 0]
    bgra[..., 2] = (a[..., 0:1] * al)[..., 0]; bgra[..., 3] = a[..., 3]
    bgra = np.ascontiguousarray(bgra)
    s = cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, img.width, img.height, img.width * 4)
    return s, bgra

def text(txt, font, size, color=INK, stroke=0, stroke_col=INK, shadow=False, spacing=0, idx=0):
    key = (txt, font, size, color, stroke, stroke_col, shadow, spacing, idx)
    if key in _cache: return _cache[key]
    f = ImageFont.truetype(font, size, index=idx)
    asc, desc = f.getmetrics()
    ext = max(0, -f.getbbox('ÁÉÍÓÚÑ')[1])   # room for accents above the ascender (kept symmetric so centring is unchanged)
    pad = stroke + (24 if shadow else 6) + ext
    if spacing:
        widths = [f.getlength(ch) + spacing for ch in txt]; tw = sum(widths) - spacing
    else:
        tw = f.getlength(txt)
    w, h = int(tw + 2*pad + 2), int(asc + desc + 2*pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    col = tuple(int(c*255) for c in color[:3]) + (int(color[3]*255),)
    scol = tuple(int(c*255) for c in stroke_col[:3]) + (255,)
    def draw_on(d, fill, sw):
        if spacing:
            x = pad
            for ch, cw in zip(txt, widths):
                d.text((x, pad), ch, font=f, fill=fill, stroke_width=sw, stroke_fill=scol if sw else None); x += cw
        else:
            d.text((pad, pad), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=scol if sw else None)
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw_on(ImageDraw.Draw(sh), (0, 0, 0, 150), stroke)
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        img.alpha_composite(sh, (0, 7))
    draw_on(ImageDraw.Draw(img), col, stroke)
    surf, buf = pil_surface(img)
    r = (surf, buf, w, h, tw, asc)
    _cache[key] = r
    return r

def put(ctx, t, x, y, scale=1.0, alpha=1.0, ax=0.5, ay=0.5, rot=0.0):
    surf, _, w, h, _, _ = t
    if alpha <= 0.001 or scale <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale)
    ctx.set_source_surface(surf, -w*ax, -h*ay)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha); ctx.restore()

# ---------- drawing helpers ----------
def rgba(ctx, c, a=None): ctx.set_source_rgba(c[0], c[1], c[2], c[3] if a is None else a)

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x+w-r, y+r, r, -math.pi/2, 0); ctx.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    ctx.arc(x+r, y+h-r, r, math.pi/2, math.pi); ctx.arc(x+r, y+r, r, math.pi, 1.5*math.pi)
    ctx.close_path()

def shadow(ctx, x, y, w, h, r, strength=0.22, off=10):
    for i in range(8):
        e = i * 3
        rrect(ctx, x-e/2, y-e/2+off, w+e, h+e, r+e/2)
        ctx.set_source_rgba(0, 0, 0, strength/8 * (1 - i/9)); ctx.fill()

def card(ctx, x, y, w, h, r=22, fill=CREAM, border=None, bw=5):
    shadow(ctx, x, y, w, h, r)
    rrect(ctx, x, y, w, h, r); rgba(ctx, fill); ctx.fill()
    if border:
        rrect(ctx, x, y, w, h, r); rgba(ctx, border); ctx.set_line_width(bw); ctx.stroke()

def jit(pts, amp, seed):
    rng = np.random.default_rng(seed)
    return [(x + rng.normal(0, amp), y + rng.normal(0, amp)) for x, y in pts]

def partial(ctx, pts, p, lw, col, alpha=1.0):
    if p <= 0 or len(pts) < 2: return
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.dist(pts[i-1], pts[i]))
    tgt = d[-1] * c01(p)
    ctx.move_to(*pts[0])
    for i in range(1, len(pts)):
        if d[i] <= tgt: ctx.line_to(*pts[i])
        else:
            seg = d[i] - d[i-1]; k = (tgt - d[i-1]) / seg if seg else 0
            ctx.line_to(pts[i-1][0] + (pts[i][0]-pts[i-1][0])*k, pts[i-1][1] + (pts[i][1]-pts[i-1][1])*k)
            break
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(lw); rgba(ctx, col, alpha); ctx.stroke()

def hand_ellipse(cx, cy, rx, ry, seed, turns=1.12, n=90):
    rng = np.random.default_rng(seed); ph = rng.uniform(0, 6)
    a0 = -2.4; pts = []
    for i in range(n):
        u = i / (n - 1); a = a0 + turns * 2 * math.pi * u
        rr = 1 + 0.035 * math.sin(3*a + ph) + 0.07 * u
        pts.append((cx + rx*rr*math.cos(a), cy + ry*rr*math.sin(a)))
    return pts

def bez(p0, c, p1, n=40):
    return [((1-u)**2*p0[0] + 2*(1-u)*u*c[0] + u*u*p1[0], (1-u)**2*p0[1] + 2*(1-u)*u*c[1] + u*u*p1[1])
            for u in np.linspace(0, 1, n)]

def hand_arrow(ctx, p0, p1, bend, p, lw, col, seed, head=34):
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy)
    c = (mx - dy/L*bend, my + dx/L*bend)
    pts = jit(bez(p0, c, p1), 1.2, seed)
    partial(ctx, pts, p / 0.8, lw, col)
    if p > 0.8:
        hp = (p - 0.8) / 0.2
        ex, ey = pts[-1]; tx, ty = pts[-1][0]-pts[-4][0], pts[-1][1]-pts[-4][1]
        ang = math.atan2(ty, tx)
        for s in (1, -1):
            a = ang + math.pi - s*0.5
            partial(ctx, [(ex, ey), (ex + head*math.cos(a), ey + head*math.sin(a))], hp, lw, col)

def highlighter(ctx, x, y, w, h, p, col=YEL, alpha=0.92, seed=3):
    if p <= 0: return
    rng = np.random.default_rng(seed)
    ww = w * eo(p)
    ctx.move_to(x + rng.uniform(-6, 4), y + rng.uniform(-4, 4))
    ctx.line_to(x + ww, y + rng.uniform(-6, 2))
    ctx.line_to(x + ww + rng.uniform(-8, 8), y + h + rng.uniform(-2, 6))
    ctx.line_to(x + rng.uniform(-4, 6), y + h + rng.uniform(-2, 4))
    ctx.close_path(); rgba(ctx, col, alpha); ctx.fill()

def spark(ctx, cx, cy, r, col=TERRA, lw=14, rot=0.0, scale=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(scale, scale)
    for i in range(8):
        a = i * math.pi / 4
        ln = r if i % 2 == 0 else r * 0.78
        ctx.move_to(math.cos(a)*r*0.18, math.sin(a)*r*0.18); ctx.line_to(math.cos(a)*ln, math.sin(a)*ln)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(lw); rgba(ctx, col); ctx.stroke()
    ctx.restore()

def chat_icon(ctx, cx, cy, s=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    rrect(ctx, -60, -45, 120, 80, 20)
    ctx.move_to(-30, 34); ctx.line_to(-44, 60); ctx.line_to(-8, 34)
    rgba(ctx, INK); ctx.set_line_width(7); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    for dx in (-26, 0, 26):
        ctx.arc(dx, -5, 7, 0, 2*math.pi); rgba(ctx, INK); ctx.fill()
    ctx.restore()

def play_icon(ctx, cx, cy, s=1.0, col=INK):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    rrect(ctx, -58, -42, 116, 84, 16); rgba(ctx, col); ctx.set_line_width(7); ctx.stroke()
    ctx.move_to(-14, -20); ctx.line_to(22, 0); ctx.line_to(-14, 20); ctx.close_path(); rgba(ctx, col); ctx.fill()
    ctx.restore()

def check(ctx, cx, cy, s, p, col=CREAM, lw=8):
    pts = [(cx - 20*s, cy + 1*s), (cx - 6*s, cy + 15*s), (cx + 22*s, cy - 16*s)]
    partial(ctx, pts, p, lw, col)

# ---------- paper texture ----------
def make_paper():
    rng = np.random.default_rng(7)
    base = np.array([226, 237, 243], np.float32)  # BGR of F3EDE2
    low = rng.normal(0, 1, (24, 14)).astype(np.float32)
    low = np.asarray(Image.fromarray(((low - low.min()) / np.ptp(low) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = ((xx - W/2)/(W*0.75))**2 + ((yy - H/2)/(H*0.75))**2
    variants = []
    for k in range(3):
        g = np.random.default_rng(100 + k).normal(0, 1, (H, W)).astype(np.float32)
        img = base[None, None, :] + (low*10 + g*4.5 - vig*16)[..., None]
        arr = np.empty((H, W, 4), np.uint8)
        arr[..., :3] = np.clip(img, 0, 255); arr[..., 3] = 255
        s = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W*4)
        variants.append((s, arr))
    return variants
PAPERS = make_paper()

def paper(ctx, fi, alpha=1.0):
    s = PAPERS[(fi // 3) % 3][0]
    ctx.set_source_surface(s, 0, 0); ctx.paint_with_alpha(alpha)

# ---------- camera / face ----------
FACE_CY = 0.415
def face_frame(img, z, cx=0.5, cy=FACE_CY, size=(W, H)):
    ow, oh = size
    cw = SW / z; ch = cw * oh / ow
    x0 = min(max(cx*SW - cw/2, 0), SW - cw); y0 = min(max(cy*SH - ch/2, 0), SH - ch)
    return img.resize(size, Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))

def settle(t, t0, z, amt=0.045, d=0.3):
    return z * (1 + amt * (1 - eo(prog(t, t0, d))))

# ---------- words / subtitles ----------
WORDS = [
 (0.00, .46, '¿Sabías'), (.46, .60, 'que'), (.60, .70, 'ahora'), (.70, .84, 'con'), (.84, .96, 'la'),
 (.96, 1.12, 'nueva'), (1.12, 1.46, 'versión'), (1.46, 1.68, 'de'), (1.68, 2.28, 'Opus'),
 (2.28, 2.56, 'puedes'), (2.56, 3.20, 'literalmente'), (3.20, 3.50, 'editar'), (3.50, 3.74, 'los'),
 (3.74, 3.90, 'videos'), (3.90, 4.24, 'con'), (4.24, 4.38, 'un'), (4.38, 4.56, 'solo'), (4.56, 4.95, 'prompt?'),
 (5.46, 5.62, 'Pues'), (5.62, 6.04, 'chequea'), (6.04, 6.34, 'eso.'),
 (6.40, 6.80, 'Estoy'), (6.80, 7.32, 'haciendo'), (7.32, 7.58, 'una'), (7.58, 7.80, 'prueba'), (7.80, 8.16, 'con'),
 (8.16, 8.96, 'Opus'), (8.96, 9.44, 'y'), (9.44, 9.76, 'resulta'), (9.76, 9.82, 'que'), (9.82, 9.90, 'a'),
 (9.90, 10.14, 'partir'), (10.14, 10.32, 'de'), (10.32, 10.52, 'un'), (10.52, 10.80, 'prompt'),
 (11.00, 11.48, 'puedes'), (11.48, 11.96, 'editar'), (11.96, 12.48, 'absolutamente'), (12.48, 12.72, 'todos'),
 (12.72, 12.98, 'los'), (12.98, 13.40, 'videos.'),
]
CHUNKS_IDX = [(0, 3), (3, 7), (7, 9), (9, 11), (11, 14), (14, 18), (18, 21), (21, 23), (23, 27),
              (27, 30), (30, 35), (35, 37), (37, 39), (39, 41)]
KEY = {'Opus', 'prompt?', 'prompt', 'todos', 'absolutamente', 'literalmente'}
CHUNKS = []
for i, (a, b) in enumerate(CHUNKS_IDX):
    ws = WORDS[a:b]
    st = ws[0][0] - 0.04
    en = WORDS[CHUNKS_IDX[i+1][0]][0] - 0.04 if i + 1 < len(CHUNKS_IDX) else ws[-1][1] + 0.35
    en = min(en, ws[-1][1] + 0.45)
    CHUNKS.append((st, en, ws))

SUB_SIZE = 78
def subtitles(ctx, t, y):
    for st, en, ws in CHUNKS:
        if st <= t < en: break
    else: return
    sp = SUB_SIZE * 0.40
    parts = []
    for (a, b, w) in ws:
        active = a - 0.03 <= t < b + 0.02 or (w == ws[-1][2] and t >= a)
        col = YEL if active else CREAM
        tt = text(w, F_SUB, SUB_SIZE, col, stroke=9, stroke_col=hexc('111111'), shadow=True)
        parts.append((tt, active, w))
    total = sum(p[0][4] for p in parts) + sp * (len(parts) - 1)
    sc = min(1.0, 960 / total)
    k = eback(prog(t, st, 0.16), 2.2); cs = sc * (0.82 + 0.18 * k); al = c01((t - st) / 0.06)
    x = W/2 - total*cs/2
    for tt, active, w in parts:
        ww = tt[4] * cs
        s = cs * (1.07 if active else 1.0)
        put(ctx, tt, x + ww/2, y, scale=s, alpha=al)
        x += ww + sp*cs

# ---------- SFX timeline ----------
SFX = []
def sfx(kind, at, gain=1.0): SFX.append((kind, at, gain))

# ---------- shots ----------
def shot_face(ctx, img, z, sub_y=1390):
    fr = face_frame(img, z)
    return fr, sub_y

def draw_s1(ctx, t, fi):  # card: NUEVA VERSIÓN / Claude Opus
    t0 = 0.96
    if t < t0: return
    k = eback(prog(t, t0, 0.34), 1.6)
    cy = -220 + (265 + 220) * k
    ctx.save(); ctx.translate(540, cy); ctx.rotate(-0.035)
    card(ctx, -380, -150, 760, 300, 26)
    lab = text('NUEVA VERSIÓN', F_LABEL, 54, INK, spacing=4)
    highlighter(ctx, -lab[4]/2 - 16, -118, lab[4] + 32, 56, prog(t, t0 + 0.18, 0.28), seed=11)
    put(ctx, lab, 0, -84)
    t1 = text('Claude ', F_SERIF, 104, INK); t2 = text('Opus', F_SERIF, 104, TERRA)
    tw = t1[4] + t2[4] + 22
    put(ctx, t1, -tw/2, 44, ax=0, ay=0.5)
    ox = -tw/2 + t1[4] + 16
    put(ctx, t2, ox, 44, ax=0, ay=0.5)
    if t >= 1.62:
        pts = jit(hand_ellipse(ox + t2[4]/2 + 4, 50, t2[4]/2 + 20, 66, 5), 1.0, 5 + fi//4)
        partial(ctx, pts, eio(prog(t, 1.62, 0.42)), 7, TERRA)
    ctx.restore()

def draw_s2(ctx, t, fi):  # timeline card on "editar los videos"
    t0 = 3.14
    if t < t0: return
    k = eback(prog(t, t0, 0.3), 1.5)
    ctx.save(); ctx.translate(540, 250); ctx.scale(0.6 + 0.4*k, 0.6 + 0.4*k); ctx.rotate(0.025)
    a = c01((t - t0) / 0.1)
    ctx.push_group()
    card(ctx, -400, -135, 800, 250, 24)
    put(ctx, text('EDITANDO…', F_LABEL, 44, INK, spacing=3), -360, -92, ax=0)
    widths = [150, 90, 180, 110, 160]
    x = -360
    for i, w in enumerate(widths):
        kk = eback(prog(t, t0 + 0.08 + i*0.07, 0.22), 2.0)
        if kk > 0:
            ctx.save(); ctx.translate(x + w/2, 25); ctx.scale(1, kk)
            rrect(ctx, -w/2, -38, w, 76, 12); rgba(ctx, hexc(TILE[i])); ctx.fill()
            ctx.restore()
        x += w + 12
    ph = -360 + 740 * eio(prog(t, t0 + 0.2, 0.62))
    if t > t0 + 0.2:
        ctx.move_to(ph, -30); ctx.line_to(ph, 80); rgba(ctx, RED); ctx.set_line_width(5); ctx.stroke()
        ctx.move_to(ph - 12, -40); ctx.line_to(ph + 12, -40); ctx.line_to(ph, -26); ctx.close_path(); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

PROMPT = 'Edita este video: subtítulos, animaciones y cortes'
def wrap(txt, font, size, maxw):
    f = ImageFont.truetype(font, size); lines, cur = [], ''
    for w in txt.split(' '):
        nxt = (cur + ' ' + w).strip()
        if f.getlength(nxt) > maxw and cur: lines.append(cur); cur = w
        else: cur = nxt
    lines.append(cur); return lines
PLINES = wrap(PROMPT, F_MONO, 46, 720)

def draw_s3(ctx, t, fi):  # paper: UN SOLO PROMPT + prompt box
    paper(ctx, fi)
    # header
    hk = eo(prog(t, 3.93, 0.25))
    head = text('UN SOLO PROMPT', F_LABEL, 132, INK, spacing=3)
    highlighter(ctx, 540 - head[4]/2 - 20, 575, head[4] + 40, 92, prog(t, 4.22, 0.3), seed=21)
    put(ctx, head, 540, 610 + 30*(1-hk), alpha=hk)
    # box
    bk = eback(prog(t, 3.98, 0.3), 1.4)
    ctx.save(); ctx.translate(540, 900); ctx.scale(0.85 + 0.15*bk, 0.85 + 0.15*bk)
    ctx.push_group()
    card(ctx, -450, -160, 900, 320, 34, CREAM, INK, 6)
    n = int(len(PROMPT) * prog(t, 4.05, 0.72)); rem = n
    y = -100; cur = None
    for ln in PLINES:
        seg = ln[:max(0, rem)]
        if seg: put(ctx, text(seg, F_MONO, 46, INK), -400, y, ax=0, ay=0)
        if cur is None and (rem <= len(ln)): cur = (seg, y)
        rem -= len(ln) + 1
        y += 66
    if cur is None: cur = (PLINES[-1], y - 66)
    if n < len(PROMPT) or (fi // 8) % 2 == 0:
        cx = -400 + ImageFont.truetype(F_MONO, 46).getlength(cur[0]) + 10
        ctx.rectangle(cx, cur[1] + 12, 4, 56); rgba(ctx, TERRA); ctx.fill()
    pk = 1 - 0.18 * math.sin(math.pi * prog(t, 4.86, 0.16))
    ctx.save(); ctx.translate(370, 90); ctx.scale(pk, pk)
    ctx.arc(0, 0, 42, 0, 2*math.pi); rgba(ctx, TERRA); ctx.fill()
    ctx.move_to(0, 20); ctx.line_to(0, -18); ctx.move_to(-15, -4); ctx.line_to(0, -19); ctx.line_to(15, -4)
    rgba(ctx, CREAM); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.restore()
    rp = prog(t, 4.9, 0.35)
    if 0 < rp < 1:
        ctx.arc(370, 90, 42 + 50*eo(rp), 0, 2*math.pi); rgba(ctx, TERRA, 0.6*(1-rp)); ctx.set_line_width(5); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(c01((t - 3.98) / 0.08))
    ctx.restore()
    # handwritten note
    if t > 4.62:
        a = c01((t - 4.62) / 0.15)
        put(ctx, text('así de simple', F_HAND, 66, TERRA), 600, 1215, alpha=a, rot=-0.04)
        hand_arrow(ctx, (395, 1210), (330, 1085), 30, eio(prog(t, 4.66, 0.3)), 6, TERRA, 31 + fi//4, head=26)

def draw_s4(ctx, t, fi):  # emphasis ticks on "chequea eso"
    p = prog(t, 5.72, 0.22)
    if p <= 0: return
    for (x0, y0, x1, y1) in [(860, 600, 925, 548), (880, 685, 958, 676), (866, 768, 928, 800),
                             (220, 600, 155, 548), (200, 685, 122, 676), (214, 768, 152, 800)]:
        partial(ctx, jit([(x0, y0), (x1, y1)], 1.2, fi//4 + x0), eo(p), 9, INK)

def draw_s5(ctx, t, fi):  # REC PRUEBA EN VIVO + Opus chip
    t0 = 6.85
    if t >= t0:
        k = eback(prog(t, t0, 0.3), 2.0)
        ctx.save(); ctx.translate(320, 190); ctx.rotate(-0.03); ctx.scale(k, k)
        lab = text('PRUEBA EN VIVO', F_LABEL, 58, INK, spacing=3)
        w = lab[4] + 120
        card(ctx, -w/2, -48, w, 96, 48)
        if (fi // 12) % 2 == 0 or t < t0 + 0.4:
            ctx.arc(-w/2 + 52, 0, 15, 0, 2*math.pi); rgba(ctx, RED); ctx.fill()
        put(ctx, lab, -w/2 + 86, 4, ax=0)
        ctx.restore()
    t1 = 8.12
    if t >= t1:
        k = eback(prog(t, t1, 0.3), 2.0)
        ctx.save(); ctx.translate(690, 322); ctx.rotate(0.035); ctx.scale(k, k)
        lab = text('Claude Opus', F_BOLD, 50, CREAM)
        w = lab[4] + 130
        shadow(ctx, -w/2, -46, w, 92, 46)
        rrect(ctx, -w/2, -46, w, 92, 46); rgba(ctx, TERRA); ctx.fill()
        spark(ctx, -w/2 + 54, 0, 26, CREAM, 8, rot=t*0.8)
        put(ctx, lab, -w/2 + 96, 2, ax=0)
        ctx.restore()

SPLIT_Y = 1110
def draw_s6(ctx, t, fi):  # split: top paper diagram
    ctx.save(); ctx.rectangle(0, 0, W, SPLIT_Y); ctx.clip()
    paper(ctx, fi)
    tk = eo(prog(t, 9.0, 0.25))
    title = text('CÓMO FUNCIONA', F_LABEL, 70, INK, spacing=6)
    put(ctx, title, 540, 190 - 20*(1-tk), alpha=tk)
    partial(ctx, jit([(540 - title[4]/2, 250), (540 + title[4]/2, 244)], 1.0, 3), eio(prog(t, 9.15, 0.35)), 7, TERRA)
    nodes = [(190, 540, 9.84, 'chat', '1 prompt'), (540, 540, 10.42, 'spark', 'Opus'), (890, 540, 11.02, 'play', 'Video listo')]
    for (x, y, tn, kind, lab) in nodes:
        k = eback(prog(t, tn, 0.32), 2.0)
        if t < tn:
            ctx.save(); ctx.set_dash([14, 12]); ctx.arc(x, y, 100, 0, 2*math.pi)
            rgba(ctx, INK, 0.22); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
            continue
        ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
        ctx.arc(0, 8, 102, 0, 2*math.pi); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()
        ctx.arc(0, 0, 100, 0, 2*math.pi); rgba(ctx, TERRA if kind == 'spark' else CREAM); ctx.fill()
        ctx.arc(0, 0, 100, 0, 2*math.pi); rgba(ctx, INK); ctx.set_line_width(6); ctx.stroke()
        if kind == 'chat': chat_icon(ctx, 0, 0, 0.82)
        elif kind == 'spark': spark(ctx, 0, 0, 54, CREAM, 15, rot=(t - tn) * 0.9)
        else: play_icon(ctx, 0, 0, 0.85)
        ctx.restore()
        put(ctx, text(lab, F_SERIF, 50, INK), x, y + 160, alpha=c01((t - tn - 0.08) / 0.15))
    hand_arrow(ctx, (302, 540), (430, 540), -30, eio(prog(t, 10.14, 0.3)), 7, INK, 40 + fi//4, head=24)
    hand_arrow(ctx, (652, 540), (780, 540), -30, eio(prog(t, 10.74, 0.3)), 7, INK, 50 + fi//4, head=24)
    ck = prog(t, 11.45, 0.25)
    if ck > 0:
        s = eback(ck, 2.4)
        ctx.save(); ctx.translate(962, 468); ctx.scale(s, s)
        ctx.arc(0, 0, 40, 0, 2*math.pi); rgba(ctx, hexc('3E9B5F')); ctx.fill()
        ctx.restore()
        check(ctx, 962, 468, 1.1, prog(t, 11.5, 0.2), CREAM, 8)
    if t > 11.2:
        put(ctx, text('subtítulos + animaciones + cortes', F_HAND, 46, TERRA), 540, 900,
            alpha=c01((t - 11.2) / 0.2), rot=-0.02)
    ctx.restore()
    # seam shadow
    for i in range(10):
        ctx.rectangle(0, SPLIT_Y + i*2, W, 2); ctx.set_source_rgba(0, 0, 0, 0.16*(1 - i/10)); ctx.fill()
    ctx.rectangle(0, SPLIT_Y - 3, W, 6); rgba(ctx, INK); ctx.fill()

def draw_s7(ctx, t, fi):  # paper: TODOS los videos grid
    paper(ctx, fi)
    hk = eo(prog(t, 11.98, 0.25))
    todos = text('TODOS', F_LABEL, 170, INK, spacing=4)
    rest = text('los videos', F_SERIF, 84, INK)
    tw = todos[4] + 30 + rest[4]; x0 = 540 - tw/2
    highlighter(ctx, x0 - 18, 300, todos[4] + 36, 118, prog(t, 12.46, 0.28), seed=77)
    put(ctx, todos, x0, 372 + 30*(1-hk), ax=0, alpha=hk)
    put(ctx, rest, x0 + todos[4] + 30, 382 + 30*(1-hk), ax=0, alpha=hk)
    tw_, th_, gap = 260, 170, 40
    gx = 540 - (3*tw_ + 2*gap)/2
    for i in range(12):
        r, c = divmod(i, 3)
        x = gx + c*(tw_ + gap); y = 530 + r*(th_ + gap)
        k = eback(prog(t, 12.0 + i*0.042, 0.26), 2.2)
        if k <= 0: continue
        ctx.save(); ctx.translate(x + tw_/2, y + th_/2); ctx.scale(k, k); ctx.rotate(((i*37) % 7 - 3) * 0.008)
        shadow(ctx, -tw_/2, -th_/2, tw_, th_, 18, 0.18, 6)
        rrect(ctx, -tw_/2, -th_/2, tw_, th_, 18); rgba(ctx, hexc(TILE[i % 6])); ctx.fill()
        ctx.move_to(-18, -26); ctx.line_to(28, 0); ctx.line_to(-18, 26); ctx.close_path(); rgba(ctx, CREAM, 0.95); ctx.fill()
        put(ctx, text('0:%02d' % (15 + (i*7) % 45), F_MONO, 24, CREAM), tw_/2 - 14, th_/2 - 22, ax=1)
        cp = prog(t, 12.55 + i*0.05, 0.2)
        if cp > 0:
            s = eback(cp, 2.4)
            ctx.save(); ctx.translate(tw_/2 - 10, -th_/2 + 10); ctx.scale(s, s)
            ctx.arc(0, 0, 28, 0, 2*math.pi); rgba(ctx, INK); ctx.fill(); ctx.restore()
            check(ctx, tw_/2 - 10, -th_/2 + 10, 0.72, prog(t, 12.6 + i*0.05, 0.15), CREAM, 6)
        ctx.restore()

def draw_s8(ctx, t, fi):  # end tag
    t0 = 13.42
    if t < t0: return
    k = eback(prog(t, t0, 0.38), 1.5)
    ctx.save(); ctx.translate(540, 2150 - (2150 - 1560) * k); ctx.rotate(-0.02)
    card(ctx, -400, -120, 800, 240, 28)
    lab = text('ESTE VIDEO LO EDITÓ', F_LABEL, 50, INK, spacing=4)
    highlighter(ctx, -lab[4]/2 - 14, -92, lab[4] + 28, 52, prog(t, t0 + 0.3, 0.3), seed=91)
    put(ctx, lab, 0, -62)
    t1 = text('Opus', F_SERIF, 92, TERRA); t2 = text(' con 1 prompt', F_SERIF, 64, INK)
    tw = t1[4] + t2[4] + 70
    spark(ctx, -tw/2 + 26, 42, 26, TERRA, 9, rot=t)
    put(ctx, t1, -tw/2 + 70, 42, ax=0); put(ctx, t2, -tw/2 + 70 + t1[4], 48, ax=0)
    ctx.restore()

# shot list: (start, end, kind, fn, zoom-func)
SHOTS = [
    (0.00, 2.28, 'face', draw_s1, lambda t: settle(t, 0, 1.10 + 0.08 * eio(t / 2.28))),
    (2.28, 3.90, 'face', draw_s2, lambda t: settle(t, 2.28, 1.36 + 0.04 * eio((t - 2.28) / 1.62), 0.06)),
    (3.90, 5.30, 'paper', draw_s3, None),
    (5.30, 6.38, 'face', draw_s4, lambda t: settle(t, 5.30, 1.02 + 0.30 * eback(prog(t, 5.60, 0.2), 1.4))),
    (6.38, 8.96, 'face', draw_s5, lambda t: settle(t, 6.38, 1.16 + 0.06 * eio((t - 6.38) / 2.58))),
    (8.96, 11.96, 'split', draw_s6, None),
    (11.96, 13.40, 'paper', draw_s7, None),
    (13.40, 99.0, 'face', draw_s8, lambda t: settle(t, 13.40, 1.04 + 0.03 * eio((t - 13.4) / 0.9), 0.06)),
]
SLIDE_IN = {3.90, 11.96}

# SFX events (all subtle)
sfx('pop', 0.96, 0.8); sfx('scribble', 1.62, 0.8); sfx('pop', 1.16, 0.35)
sfx('whoosh', 2.22, 0.5); sfx('pop', 3.14, 0.6)
for i in range(5): sfx('click', 3.22 + i*0.07, 0.6)
sfx('whoosh', 3.82, 0.9)
for i in range(14): sfx('type', 4.05 + i*0.052, 0.55)
sfx('scribble', 4.22, 0.5); sfx('pop', 4.86, 0.9); sfx('swish', 5.56, 0.8)
sfx('pop', 6.85, 0.7); sfx('pop', 8.12, 0.8)
sfx('whoosh', 8.9, 0.7); sfx('pop', 9.84, 0.7); sfx('scribble', 10.14, 0.35); sfx('pop', 10.42, 0.8)
sfx('scribble', 10.74, 0.35); sfx('pop', 11.02, 0.8); sfx('tick', 11.5, 0.9)
sfx('whoosh', 11.9, 0.9)
for i in range(6): sfx('click', 12.0 + i*0.084, 0.5)
sfx('scribble', 12.46, 0.45)
for i in range(4): sfx('tick', 12.6 + i*0.15, 0.55)
sfx('whoosh', 13.34, 0.5); sfx('ding', 13.5, 0.8)

def shot_at(t):
    for s in SHOTS:
        if s[0] <= t < s[1]: return s
    return SHOTS[-1]

def render_frame(img, t, fi):
    st, en, kind, fn, zf = shot_at(t)
    arr = np.empty((H, W, 4), np.uint8)
    if kind in ('face', 'paper'):
        z = zf(t) if zf else 1.18
        prev_face = None
        if kind == 'paper':
            # during slide-in show previous face framing underneath
            prev = [s for s in SHOTS if s[1] == st][0]
            z = prev[4](t) if prev[4] else 1.18
        fr = np.asarray(face_frame(img, z))
    else:  # split: previous framing sits underneath while the paper panel drops in
        fr = np.asarray(face_frame(img, 1.22))
    if fr is not None:
        arr[..., 0] = fr[..., 2]; arr[..., 1] = fr[..., 1]; arr[..., 2] = fr[..., 0]
    else:
        arr[...] = 0
    arr[..., 3] = 255
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W*4)
    ctx = cairo.Context(surf)
    sub_y = 1395
    if kind == 'face':
        fn(ctx, t, fi)
    elif kind == 'paper':
        dx = 0
        if st in SLIDE_IN:
            dx = W * (1 - eo(prog(t, st, 0.2)))
        ctx.save(); ctx.translate(dx, 0)
        for i in range(12):
            ctx.rectangle(-24 + i*2, 0, 2, H); ctx.set_source_rgba(0, 0, 0, 0.2 * i/12); ctx.fill()
        fn(ctx, t, fi)
        ctx.restore()
        sub_y = 1640
    else:
        fp = np.asarray(face_frame(img, 1.25, cy=0.44, size=(W, H - SPLIT_Y)))
        pan = np.empty((H - SPLIT_Y, W, 4), np.uint8)
        pan[..., 0] = fp[..., 2]; pan[..., 1] = fp[..., 1]; pan[..., 2] = fp[..., 0]; pan[..., 3] = 255
        ps = cairo.ImageSurface.create_for_data(pan, cairo.FORMAT_ARGB32, W, H - SPLIT_Y, W*4)
        k = 1.0  # hard cut into split; panel contents animate in
        ctx.save(); ctx.translate(0, -SPLIT_Y * (1 - k)); fn(ctx, t, fi); ctx.restore()
        ctx.save(); ctx.set_source_surface(ps, 0, SPLIT_Y); ctx.rectangle(0, SPLIT_Y + 3, W, H); ctx.fill(); ctx.restore()
        sub_y = 1790
    subtitles(ctx, t, sub_y)
    surf.flush()
    return arr[..., [2, 1, 0]]

# ---------- audio ----------
SR = 48000
def synth(kind, rng):
    if kind == 'whoosh':
        n = int(0.42*SR); x = rng.normal(0, 1, n); u = np.linspace(0, 1, n)
        cut = 600 + 5200 * np.sin(np.pi * u) ** 2
        y = np.zeros(n); a = 0.0
        coef = 1 - np.exp(-2*np.pi*cut/SR)
        for i in range(n): a += coef[i]*(x[i] - a); y[i] = a
        y = y - np.convolve(y, np.ones(40)/40, 'same')*0.6
        env = np.sin(np.pi * u ** 0.8) ** 2
        return y * env / (np.abs(y).max() + 1e-9) * 0.11
    if kind == 'swish':
        n = int(0.22*SR); x = rng.normal(0, 1, n); u = np.linspace(0, 1, n)
        y = np.diff(np.concatenate([[0], x])); y = np.convolve(y, np.ones(6)/6, 'same')
        env = (u ** 0.5) * (1 - u) ** 2 * 4
        return y * env / (np.abs(y).max() + 1e-9) * 0.09
    if kind == 'pop':
        n = int(0.09*SR); tt = np.arange(n)/SR
        f = 380 + 700*np.exp(-tt*55); ph = 2*np.pi*np.cumsum(f)/SR
        return np.sin(ph) * np.exp(-tt*42) * 0.16
    if kind in ('click', 'type'):
        n = int((0.012 if kind == 'type' else 0.02)*SR); tt = np.arange(n)/SR
        x = rng.normal(0, 1, n); x = np.diff(np.concatenate([[0], x]))
        tone = np.sin(2*np.pi*(1800 if kind == 'type' else 1100)*tt)
        return (x*0.4 + tone) * np.exp(-tt*(420 if kind == 'type' else 260)) * (0.05 if kind == 'type' else 0.07) * rng.uniform(0.7, 1.1)
    if kind == 'scribble':
        n = int(0.42*SR); tt = np.arange(n)/SR; x = rng.normal(0, 1, n)
        y = np.convolve(x, np.ones(3)/3, 'same') - np.convolve(x, np.ones(30)/30, 'same')
        am = 0.55 + 0.45*np.sin(2*np.pi*14*tt + rng.uniform(0, 6))
        env = np.minimum(1, tt/0.03) * np.minimum(1, (tt[-1]-tt)/0.08)
        return y * am * env / (np.abs(y).max() + 1e-9) * 0.05
    if kind == 'tick':
        n = int(0.14*SR); tt = np.arange(n)/SR
        return (np.sin(2*np.pi*2100*tt) + 0.5*np.sin(2*np.pi*3150*tt)) * np.exp(-tt*38) * 0.045
    if kind == 'ding':
        n = int(1.1*SR); tt = np.arange(n)/SR
        y = sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*d) for f, a, d in [(880, 1, 4), (1320, .5, 5), (1760, .3, 7), (2640, .12, 9)])
        return y * np.minimum(1, tt/0.004) * 0.05
    raise ValueError(kind)

def build_audio():
    with wave.open(os.path.join(S, 'voice_s16.wav')) as w:
        nch = w.getnchannels(); raw = w.readframes(w.getnframes())
    v = np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, nch) / 32768
    mix = np.zeros((max(len(v), int((DUR + 1)*SR)), 2), np.float32)
    mix[:len(v)] += v
    rng = np.random.default_rng(1)
    for kind, at, g in SFX:
        y = synth(kind, rng) * g; i0 = int(at*SR)
        pan = rng.uniform(-0.25, 0.25)
        seg = mix[i0:i0 + len(y)]; n = len(seg)
        seg[:, 0] += y[:n] * (1 - pan); seg[:, 1] += y[:n] * (1 + pan)
    mix = mix[:int(DUR*SR)]
    mix = np.clip(mix, -0.98, 0.98)
    out = (mix * 32767).astype(np.int16)
    with wave.open(os.path.join(S, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())

# ---------- main ----------
def reader():
    cmd = ['ffmpeg', '-v', 'error', '-i', os.path.join(S, 'base.mp4'),
           '-vf', 'eq=contrast=1.06:saturation=1.12:gamma=0.98', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW*SH*3)
    while True:
        b = p.stdout.read(SW*SH*3)
        if len(b) < SW*SH*3: break
        yield Image.frombuffer('RGB', (SW, SH), b, 'raw', 'RGB', 0, 1)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        want = {int(round(t*FPS)): t for t in times}
        os.makedirs(os.path.join(S, 'prev'), exist_ok=True)
        for fi, img in enumerate(reader()):
            if fi in want:
                out = render_frame(img, fi / FPS, fi)
                Image.fromarray(np.ascontiguousarray(out)).save(os.path.join(S, 'prev', 'p%05.2f.jpg' % want[fi]), quality=85)
            if fi > max(want): break
        return
    build_audio()
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(S, 'out.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', os.path.join(S, 'mix.wav'),
                            '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp],
                           stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for fi, img in enumerate(reader()):
        if fi >= n: break
        enc.stdin.write(np.ascontiguousarray(render_frame(img, fi / FPS, fi)).tobytes())
        if fi % 60 == 0: print('frame', fi, '/', n, flush=True)
    enc.stdin.close(); enc.wait()
    print('done', outp)

if __name__ == '__main__':
    main()
