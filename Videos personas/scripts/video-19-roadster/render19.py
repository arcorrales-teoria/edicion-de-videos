"""IMG_9043 (hook) + IMG_9044 · Tesla Roadster: "El mejor lanzamiento del año". 1.05x, voice only.
Format I (my real take full frame, one morphing card above my eyes) dressed in the Roadster launch look: black stage, Saira
(~ the squared sans of tesla.com/roadster), gold hairlines under headings, the gold ROADSTER wordmark, red tail-light progress bar.
Three full-screen beats: the flight off the ramp (with the three Roadster systems explained), two meme montages over a dark
scrim, and the ending on the flying car. Twitter clips and meme screenshots are silent. Subtitles on a dark panel (bright sky
and a cream jacket behind). HDR (HLG) only."""
import sys, os, json, math, subprocess, wave, glob
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = '/Users/acorrales/Desktop/Edición de videos/scripts'
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit19 as E; os.chdir(_cwd)

SPEED = 1.05
REF = os.path.join(HERE, 'ref'); CLIPS = os.path.join(HERE, 'clips')
SAIRA = os.path.join(HERE, 'fonts', 'Saira.ttf')
def C(r, g, b, a=1.0): return (r / 255, g / 255, b / 255, a)
BLACK, PANEL, WHITE, GREY = C(10, 10, 11), C(17, 17, 17), C(242, 242, 242), C(150, 150, 150)
GOLD, GOLDB, CHAMP, RED = C(176, 146, 98), C(217, 168, 103), C(216, 195, 154), C(228, 36, 46)

# ---------------- text (Saira: weight, width axes) ----------------
_tc = {}
def SX(txt, size, col=WHITE, wght=400, wdth=116, track=0.0, shadow=0, shadow_a=170):
    key = (txt, size, col, wght, wdth, track, shadow, shadow_a)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(SAIRA, size); f.set_variation_by_axes([wght, wdth])
    asc, desc = f.getmetrics(); sp = track * size
    widths = [f.getlength(ch) + sp for ch in txt]; tw = max(1, sum(widths) - sp)
    pad = 10 + int(size * 0.2) + shadow * 2
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    def draw(d, fill):
        x = pad
        for ch, cw in zip(txt, widths): d.text((x, pad), ch, font=f, fill=fill); x += cw
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, shadow_a))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)), (0, 4))
    draw(ImageDraw.Draw(img), tuple(int(c * 255) for c in col[:3]) + (int(col[3] * 255),))
    s, buf = fx.pil_surface(img); r = (s, buf, w, h, tw, asc); _tc[key] = r; return r
def CAPS(txt, size, col=WHITE, wght=400): return SX(txt, size, col, wght, 118, track=0.08)

# ---------------- springs ----------------
def spring(x, w=13.0, zeta=0.82):
    if x <= 0: return 0.0
    if zeta >= 1: return 1 - math.exp(-w * x) * (1 + w * x)
    wd = w * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * x) * (math.cos(wd * x) + zeta * w / wd * math.sin(wd * x))
def track(t, events, v0, **kw):
    v, prev = v0, v0
    for te, tgt in events:
        v += (tgt - prev) * spring(t - te, **kw); prev = tgt
    return v
def pop(t, t0, w=13.0, zeta=0.80): return spring(t - t0, w=w, zeta=zeta)

# ---------------- words / timing ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v19.json')))['segments'] for w in s['words']]
FIX = {18: 'el', 40: 'Por', 44: 'varios', 45: 'memes', 64: '', 83: 'superpoder de Elon.', 116: 'tiene', 118: '99%', 119: '', 120: '', 121: 'ganado.',
       160: 'viralidad.', 161: '', 162: 'Ese', 163: 'man,', 168: 'hace,', 169: 'todo', 180: 'un', 181: 'meme', 202: 'vi'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.35
TITLE_END = T(13) - 0.1                                                   # title over the hook ("Oiga, literalmente Elon…")

# ---------------- helpers ----------------
def rr(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
def soft_shadow(ctx, x, y, w, h, r, a):
    for dy, grow, al in [(20, 20, 0.07), (10, 8, 0.09), (3, 1, 0.10)]:
        rr(ctx, x - grow, y - grow + dy, w + 2 * grow, h + 2 * grow, r + grow); ctx.set_source_rgba(0, 0, 0, al * a); ctx.fill()
_img = {}
def img(name, crop=None):
    key = (name, crop)
    if key not in _img:
        im = Image.open(os.path.join(REF, name)).convert('RGBA')
        if crop: im = im.crop(crop)
        _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_surf(ctx, surf, iw, ih, x, y, w, h, alpha, lift=0.0, fit='cover'):
    if alpha <= 0.002: return
    s = max(w / iw, h / ih) if fit == 'cover' else min(w / iw, h / ih)
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + w / 2, y + h / 2 + lift); ctx.scale(s, s)
    ctx.set_source_surface(surf, -iw / 2, -ih / 2); ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha); ctx.restore()
def paint_img(ctx, name, crop, x, y, w, h, alpha, lift=0.0, fit='cover'):
    if alpha <= 0.002: return
    im, (surf, _b) = img(name, crop); paint_surf(ctx, surf, im.width, im.height, x, y, w, h, alpha, lift, fit)
def logo(ctx, name, cx, cy, w, a):
    """wordmark / icon png with its own colours, centred"""
    if a <= 0.002: return
    im, (surf, _b) = img(name); s = w / im.width
    ctx.save(); ctx.translate(cx - w / 2, cy - im.height * s / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
_clip = {}
def clip_frame(name, t, t0):
    fs = _clip.get(name)
    if fs is None: fs = _clip[name] = sorted(glob.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, int((t - t0) * FPS)))
    key = (name, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == name and isinstance(kk[1], int)]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_clip(ctx, name, t, t0, x, y, w, h, alpha, lift=0.0):
    if alpha <= 0.002: return
    im, (surf, _b) = clip_frame(name, t, t0); paint_surf(ctx, surf, im.width, im.height, x, y, w, h, alpha, lift)
def hairline(ctx, x, y, w, a, k=1.0, col=GOLD):
    if k <= 0 or a <= 0.002: return
    ctx.rectangle(x, y, w * k, 2); rgba(ctx, col, a); ctx.fill()
def sweep(ctx, x, y, w, h, u, a):
    """light sweep across a wordmark, u 0->1"""
    if not 0 < u < 1 or a <= 0.002: return
    cx = x - 120 + (w + 240) * u
    g = cairo.LinearGradient(cx - 90, 0, cx + 90, 0)
    g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 1, 1, 0.55 * a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip(); ctx.set_source(g); ctx.paint(); ctx.restore()
def glow_line(ctx, pts, col, a, width=3):
    if len(pts) < 2 or a <= 0.002: return
    for wd, al in ((14, 0.10), (7, 0.22), (width, 1.0)):
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        rgba(ctx, col, a * al); ctx.set_line_width(wd); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
def check(ctx, x, y, s, col, a, k=1.0):
    if a <= 0.002 or k <= 0: return
    p0, p1, p2 = (x - 0.5 * s, y), (x - 0.15 * s, y + 0.35 * s), (x + 0.55 * s, y - 0.4 * s)
    L1, L2 = math.dist(p0, p1), math.dist(p1, p2); d = (L1 + L2) * k
    ctx.move_to(*p0)
    if d <= L1: ctx.line_to(p0[0] + (p1[0] - p0[0]) * d / L1, p0[1] + (p1[1] - p0[1]) * d / L1)
    else: ctx.line_to(*p1); u = (d - L1) / L2; ctx.line_to(p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u)
    rgba(ctx, col, a); ctx.set_line_width(max(3, s * 0.16)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def icon_car(ctx, x, y, s, a):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-60, 8); ctx.line_to(-56, -6); ctx.line_to(-22, -12); ctx.line_to(-2, -26); ctx.line_to(30, -24); ctx.line_to(58, -6); ctx.line_to(60, 8); ctx.close_path()
    rgba(ctx, WHITE, a); ctx.set_line_width(4); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    for wx in (-34, 36):
        ctx.arc(wx, 10, 11, 0, 2 * math.pi); rgba(ctx, BLACK, a); ctx.fill_preserve(); rgba(ctx, WHITE, a); ctx.stroke()
    ctx.restore()
def icon_rocket(ctx, x, y, s, a, t=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, -44); ctx.curve_to(14, -30, 14, -6, 12, 22); ctx.line_to(-12, 22); ctx.curve_to(-14, -6, -14, -30, 0, -44); ctx.close_path()
    rgba(ctx, WHITE, a); ctx.set_line_width(4); ctx.stroke()
    for sg in (-1, 1):
        ctx.move_to(12 * sg, 4); ctx.line_to(24 * sg, 26); ctx.line_to(12 * sg, 22); ctx.stroke()
    fl = 10 + 6 * math.sin(t * 22)
    ctx.move_to(-7, 26); ctx.line_to(0, 26 + fl + 10); ctx.line_to(7, 26); rgba(ctx, GOLDB, a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
def icon_chip(ctx, x, y, s, a):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rr(ctx, -26, -26, 52, 52, 6); rgba(ctx, WHITE, a); ctx.set_line_width(4); ctx.stroke()
    for k in (-14, 0, 14):
        for (x0, y0, x1, y1) in ((k, -26, k, -38), (k, 26, k, 38), (-26, k, -38, k), (26, k, 38, k)):
            ctx.move_to(x0, y0); ctx.line_to(x1, y1)
    ctx.stroke(); ctx.restore()
    put(ctx, SX('IA', 26, WHITE, 600), x, y + 1, alpha=a)

# ---------------- the morphing card (band above my eyes) ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(13) - 0.08, 'hero', CX, 260, 1000, 372, 10, BLACK[:3]),
    (T(56) - 0.08, 'radar', CX, 260, 1000, 420, 10, BLACK[:3]),
    (T(79) - 0.08, 'super', CX, 260, 1000, 382, 10, BLACK[:3]),
    (T(84) - 0.08, 'build', CX, 260, 1000, 330, 10, BLACK[:3]),
    (T(99) - 0.08, 'chart', CX, 260, 1000, 420, 10, BLACK[:3]),
    (T(122) - 0.08, 'night', CX, 260, 1000, 440, 10, BLACK[:3]),
    (T(135) - 0.08, 'levels', CX, 260, 1000, 420, 10, PANEL[:3]),
    (T(152) - 0.08, 'ring', CX, 260, 760, 420, 10, BLACK[:3]),
    (T(161) - 0.08, 'hud', CX, 260, 746, 420, 10, BLACK[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000                                 # outdoors, cap at y~250-500, eyes from y~625
SHAPE_ON = STATES[0][0]
# full-screen beats: (start, end, kind)
FS1 = (T(21) - 0.10, T(40) - 0.10)                                       # the flight, black stage
M1 = (T(40) - 0.10, T(56) - 0.12)                                         # memes over a dark scrim
M2 = (T(169) - 0.10, T(184) - 0.12)
FSE = (T(184) - 0.10, 1e9)                                                 # ending on the flying car
BEATS = [FS1, M1, M2, FSE]
def beat_a(t, b, din=0.18, dout=0.18): return c01((t - b[0]) / din) * (1 - c01((t - b[1]) / dout))
def any_beat(t): return max(beat_a(t, b) for b in BEATS)

def shape_geo(t):
    keys = []
    for k in range(8):
        ev = [(s[0], (s[2], s[3], s[4], s[5], s[6], *s[7])[k]) for s in STATES[1:]]
        v0 = (STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7])[k]
        keys.append(track(t, ev, v0, w=12.0, zeta=0.86))
    return keys
def state_alpha(t, i):
    a = STATES[i][0]; b = STATES[i + 1][0] if i + 1 < len(STATES) else 1e9
    return c01((t - a - 0.06) / 0.20) * (1 - c01((t - b) / 0.12))

MEME_THUMB = {'memes': ('i24.png', (120, 150, 1160, 930)), 'news': ('i29.png', (120, 430, 1160, 1010))}
_rng = np.random.RandomState(7)
RADAR = [(_rng.uniform(0, 2 * math.pi), _rng.choice([1, 2, 3]), _rng.uniform(0, 1)) for _ in range(70)]
def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'hero':
        paint_img(ctx, 'i30.png', (150, 330, 1950, 1000), 0, 0, w, h, a, lift)
        sweep(ctx, 40, 120, 520, 120, prog(t, T(20) - 0.15, 0.7), a)                 # light passes over ROADSTER on "Roadster"
    elif name == 'radar':
        cx, cy = w / 2, h / 2 + 14
        for k in range(3):                                                         # rings
            r = 70 + 70 * (k + 1)
            ctx.save(); ctx.translate(cx, cy); ctx.scale(2.0, 0.78); ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.restore()
            rgba(ctx, WHITE, a * 0.12); ctx.set_line_width(2); ctx.stroke()
        for ph in range(3):                                                        # pulses travelling out
            u = ((t - st0) / 1.1 + ph / 3) % 1
            ctx.save(); ctx.translate(cx, cy); ctx.scale(2.0, 0.78); ctx.arc(0, 0, 60 + 200 * u, 0, 2 * math.pi); ctx.restore()
            rgba(ctx, GOLD, a * 0.5 * (1 - u)); ctx.set_line_width(2); ctx.stroke()
        n_on = 6 + 64 * eio(prog(t, T(68) - 0.1, T(78) - T(68)))                  # "absolutamente todo el santo mundo": dots fill in
        for j, (ang, ring, ph) in enumerate(RADAR):
            if j >= n_on: break
            k = pop(t, st0 + 0.1 + 0.02 * j if j < 6 else T(68) - 0.1 + (j - 6) / 64 * (T(78) - T(68)))
            r = 70 + 70 * ring; x = cx + 2.0 * r * math.cos(ang + 0.15 * math.sin(t + ph * 6)); y = cy + 0.78 * r * math.sin(ang)
            if not (16 < y < h - 16): continue
            ctx.arc(x, y, 7 * k, 0, 2 * math.pi); rgba(ctx, GOLDB if j % 5 == 0 else WHITE, a * 0.9); ctx.fill()
        ctx.arc(cx, cy, 54, 0, 2 * math.pi); rgba(ctx, WHITE, a); ctx.fill()
        put(ctx, SX('ELON', 28, BLACK, 600, 118, track=0.06), cx, cy + 1, alpha=a)
        put(ctx, CAPS('ATENCIÓN', 24, GREY), 40, 40, alpha=a, ax=0); hairline(ctx, 40, 60, 150, a, eo(prog(t, st0 + 0.2, 0.5)))
    elif name == 'super':
        paint_img(ctx, 'i31.png', (950, 800, 2000, 1208), 440, 168, w - 440, h - 168, a, lift)      # only the car, not their English copy
        g = cairo.LinearGradient(440, 0, 610, 0); g.add_color_stop_rgba(0, BLACK[0], BLACK[1], BLACK[2], a); g.add_color_stop_rgba(1, BLACK[0], BLACK[1], BLACK[2], 0)
        ctx.rectangle(440, 168, 170, h - 168); ctx.set_source(g); ctx.fill()
        put(ctx, SX('El mayor superpoder', 66, WHITE, 400), 56, 120 + lift, alpha=a, ax=0)
        hairline(ctx, 58, 160, 560, a, eo(prog(t, st0 + 0.25, 0.6)))
        put(ctx, SX('Que todo el mundo', 34, C(200, 200, 200)), 58, 215 + lift, alpha=a * eo(prog(t, st0 + 0.35, 0.4)), ax=0)
        put(ctx, SX('hable de usted.', 34, C(200, 200, 200)), 58, 258 + lift, alpha=a * eo(prog(t, st0 + 0.45, 0.4)), ax=0)
    elif name == 'build':
        cols = [(T(90) - 0.1, 'AUTOS', icon_car), (T(91) - 0.05, 'COHETES', icon_rocket), (T(92) + 0.1, 'IA', icon_chip)]
        for j, (t0, lbl, ic) in enumerate(cols):
            k = pop(t, t0); x = 170 + j * 330
            if j: ctx.rectangle(x - 165, 60, 2, h - 120); rgba(ctx, GOLD, a * 0.8); ctx.fill()
            if k <= 0.001: continue
            aa = a * c01(k * 1.5)
            if ic is icon_rocket: ic(ctx, x, 130 + 20 * (1 - k), 1.3, aa, t)
            else: ic(ctx, x, 130 + 20 * (1 - k), 1.3, aa)
            put(ctx, CAPS(lbl, 30, WHITE), x, 245 + 10 * (1 - k), alpha=aa)
        k = pop(t, T(97) - 0.1)                                                     # "es un genio absoluto"
        put(ctx, CAPS('CONSTRUYE DE TODO', 22, GREY), w / 2, h - 28, alpha=a * c01(k * 1.5))
    elif name == 'chart':
        x0, x1, y0, y1 = 110, 950, 40, 330
        for k in range(6):
            yy = y0 + (y1 - y0) * k / 5; ctx.rectangle(x0, yy, x1 - x0, 2); rgba(ctx, WHITE, a * 0.12); ctx.fill()
        put(ctx, CAPS('QUE HABLEN DE USTED', 22, GREY), (x0 + x1) / 2, 380, alpha=a)
        ctx.save(); ctx.translate(58, (y0 + y1) / 2); ctx.rotate(-math.pi / 2); put(ctx, CAPS('VIRAL', 22, GREY), 0, 0, alpha=a); ctx.restore()
        k = eio(prog(t, st0 + 0.2, T(116) - st0 - 0.2))                             # the curve climbs while I talk
        n = 80
        gold = [(x0 + (x1 - x0) * i / n, y1 - (y1 - y0) * 1.08 * (i / n) ** 2.3) for i in range(int(n * k) + 1)]
        low = [(x0 + (x1 - x0) * i / n, y1 - (y1 - y0) * 0.16 * (i / n) ** 1.4) for i in range(int(n * k) + 1)]
        ctx.save(); ctx.rectangle(x0, y0 - 6, x1 - x0 + 10, y1 - y0 + 12); ctx.clip()
        for f_ in range(1, 12):                                                     # the fan of curves between the two (multi-mode look)
            q = f_ / 12
            pts = [(gx, ly + (gy - ly) * q) for (gx, gy), (_, ly) in zip(gold, low)]
            if len(pts) > 1:
                ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; rgba(ctx, GOLDB, a * 0.18); ctx.set_line_width(1.5); ctx.stroke()
        glow_line(ctx, low, C(210, 210, 210), a * 0.8, 2)
        glow_line(ctx, gold, GOLDB, a, 3)
        ctx.restore()
        ky = y0 + (y1 - y0) * 0.2; k2 = pop(t, T(118) - 0.1)
        if k2 > 0.001:
            ctx.rectangle(x0, ky, (x1 - x0) * eo(c01(k2)), 2); rgba(ctx, WHITE, a * 0.9); ctx.fill()
            v = int(round(99 * eo(prog(t, T(118) - 0.1, 0.55))))
            put(ctx, SX('%d%%' % v, 64, WHITE, 500), x0 + 20, ky - 40, alpha=a * c01(k2 * 1.5), ax=0)
            put(ctx, CAPS('GANADO', 24, CHAMP), x1, ky - 22, alpha=a * c01(k2 * 1.5), ax=1)
        put(ctx, CAPS('NORMAL', 20, GREY), x1, y1 - 70, alpha=a * c01((k - 0.9) * 10), ax=1)
    elif name == 'night':
        paint_img(ctx, 'i34.png', (0, 380, 2000, 1260), 0, 0, w, h, a, lift)
        put(ctx, SX('Lo más increíble', 54, WHITE, 400, shadow=6), 50, h - 92 + lift, alpha=a, ax=0)
        hairline(ctx, 52, h - 58, 420, a, eo(prog(t, st0 + 0.3, 0.6)))
    elif name == 'levels':
        rows = [(T(143) - 0.1, 'MEMES', 'memes'), (T(147) - 0.1, 'NOTICIAS', 'news'), (T(151) - 0.1, 'TODO', 'hud')]
        put(ctx, CAPS('CÓMO VOLVERSE VIRAL', 24, GREY), 40, 42, alpha=a, ax=0); hairline(ctx, 40, 62, 330, a, eo(prog(t, st0 + 0.2, 0.5)))
        for j, (t0, lbl, th) in enumerate(rows):
            k = pop(t, t0); y = 90 + j * 108
            ctx.rectangle(40, y + 100, w - 80, 1); rgba(ctx, WHITE, a * 0.12); ctx.fill()
            aa = a * (0.22 + 0.78 * c01(k * 1.5)); xo = 16 * (1 - k)              # rows wait dimmed, light up on each word
            rr(ctx, 40 + xo, y + 8, 140, 84, 6); ctx.save(); ctx.clip()
            if th == 'hud': paint_clip(ctx, 'hud', t, t0, 40 + xo, y + 8, 140, 84, aa)
            else: paint_img(ctx, MEME_THUMB[th][0], MEME_THUMB[th][1], 40 + xo, y + 8, 140, 84, aa)
            ctx.restore()
            put(ctx, SX(lbl, 46, WHITE, 500, 118, track=0.05), 220 + xo, y + 52, alpha=aa, ax=0)
            check(ctx, w - 90, y + 50, 40, GOLDB, a, eo(prog(t, t0 + 0.15, 0.3)))
    elif name == 'ring':
        cx, cy, R = w / 2, h / 2, 150
        k = eio(prog(t, st0 + 0.1, 1.1))                                           # "un 360": the ring closes
        ctx.arc(cx, cy, R, 0, 2 * math.pi); rgba(ctx, WHITE, a * 0.10); ctx.set_line_width(10); ctx.stroke()
        if k > 0:
            for wd, al in ((26, 0.10), (14, 0.22), (8, 1.0)):
                ctx.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k); rgba(ctx, GOLDB, a * al); ctx.set_line_width(wd); ctx.stroke()
        put(ctx, SX('%d°' % int(round(360 * k)), 84, WHITE, 500), cx, cy - 10, alpha=a)
        put(ctx, CAPS('VIRALIDAD', 22, GREY), cx, cy + 58, alpha=a)
    elif name == 'hud':
        paint_clip(ctx, 'hud', t, st0 + 0.06, 0, 0, w, h, a, lift)
        put(ctx, CAPS('CADA LANZAMIENTO', 22, WHITE), 30, 34, alpha=a * eo(prog(t, st0 + 0.3, 0.4)), ax=0)

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = c01(spring(t - SHAPE_ON, w=11.0, zeta=0.9)) * (1 - any_beat(t))
    if appear <= 0.01: return
    sc = 0.88 + 0.12 * appear
    f = min(1.0, BAND_H / h, BAND_W / w); cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 30 * (1 - appear)); ctx.scale(sc * f, sc * f); ctx.translate(-w / 2, -h / 2)
    soft_shadow(ctx, 0, 0, w, h, r, appear)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 12 * (1 - c01((t - st[0] - 0.06) / 0.25))
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore()
    rr(ctx, 0.5, 0.5, w - 1, h - 1, r); rgba(ctx, WHITE, 0.10 * appear); ctx.set_line_width(1.5); ctx.stroke()
    ctx.restore()

# ---------------- full-screen beats ----------------
FEATS = [('ic_aero.png', ['AERO', 'ACTIVA'], 0.0), ('ic_thrust.png', ['PROPULSORES', 'DE GAS FRÍO'], 0.18), ('ic_fan.png', ['SUCCIÓN', 'MULTIMODO'], 0.36)]
MEMES1 = ['i26.png', 'i24.png', 'i23.png', 'i27.png']
MEMES2 = ['i25.png', 'i28.png', 'i29.png']
def meme_stack(ctx, t, beat, names):
    a = beat_a(t, beat)
    if a <= 0.002: return
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, 0.78 * a); ctx.fill()
    n = len(names); span = beat[1] - beat[0] - 0.25
    for j, nm in enumerate(names):
        t0 = beat[0] + 0.05 + span * j / n
        k = pop(t, t0, w=12, zeta=0.78)
        if k <= 0.001: continue
        im, (surf, _b) = img(nm); s = min(860 / im.width, 1000 / im.height); cw, ch = im.width * s, im.height * s
        newer = sum(1 for jj in range(j + 1, n) if t >= beat[0] + 0.05 + span * jj / n)
        rot = (-0.045, 0.035, -0.025, 0.04)[j % 4]; dx = (-18, 22, -10, 14)[j % 4]
        ctx.save(); ctx.translate(W / 2 + dx, 760 + 260 * (1 - k)); ctx.rotate(rot * k); ctx.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
        soft_shadow(ctx, -cw / 2, -ch / 2, cw, ch, 22, a)
        rr(ctx, -cw / 2, -ch / 2, cw, ch, 22); ctx.save(); ctx.clip()
        ctx.translate(-cw / 2, -ch / 2); ctx.scale(s, s); ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint_with_alpha(a * c01(k * 1.6)); ctx.restore()
        if newer: rr(ctx, -cw / 2, -ch / 2, cw, ch, 22); ctx.set_source_rgba(0, 0, 0, 0.45 * a * min(1, newer)); ctx.fill()
        ctx.restore()
def stage(ctx, t):
    """black Tesla stage for the flight and the ending"""
    for beat, clip, c0 in ((FS1, 'fly', FS1[0]), (FSE, 'end', FSE[0])):
        a = beat_a(t, beat)
        if a <= 0.002: continue
        ctx.rectangle(0, 0, W, H); rgba(ctx, BLACK, a); ctx.fill()
        vy = 360
        paint_clip(ctx, clip, t, c0, 0, vy, W, 608, a)
        g = cairo.LinearGradient(0, vy, 0, vy + 608)                               # feather the clip into the stage
        for u, al in ((0, 1), (0.10, 0), (0.90, 0), (1, 1)): g.add_color_stop_rgba(u, BLACK[0], BLACK[1], BLACK[2], al * a)
        ctx.rectangle(0, vy, W, 608); ctx.set_source(g); ctx.fill()
        logo(ctx, 'tesla.png', W / 2, 150, 210, a * eo(prog(t, beat[0] + 0.1, 0.4)))
        logo(ctx, 'roadster.png', W / 2, 250, 620, a * eo(prog(t, beat[0] + 0.2, 0.4)))
        sweep(ctx, W / 2 - 320, 220, 640, 60, prog(t, beat[0] + 0.45, 0.8), a)
        if beat is FS1:
            for j, (ic, lines, d) in enumerate(FEATS):
                t0 = T(27) - 0.1 + d                                               # "casi que puede volar"
                k = pop(t, t0); x = 200 + j * 340
                if j: ctx.rectangle(x - 170, 1040, 2, 190); rgba(ctx, GOLD, a * 0.9 * c01(k * 1.5)); ctx.fill()
                if k <= 0.001: continue
                hi = 1.0 if j == 1 else 0.55                                       # the thrusters are what make it "fly"
                logo(ctx, ic, x, 1090 + 16 * (1 - k), 70 if j != 1 else 34, a * c01(k * 1.5) * hi)
                for li, ln in enumerate(lines):
                    put(ctx, CAPS(ln, 26, WHITE), x, 1170 + li * 36 + 10 * (1 - k), alpha=a * c01(k * 1.5) * hi)
                if j == 1: hairline(ctx, x - 110, 1238, 220, a, eo(prog(t, t0 + 0.4, 0.5)), GOLDB)
        else:
            k = pop(t, T(196) - 0.1)                                                # "de los mejores lanzamientos"
            if k > 0.001:
                tt = CAPS('EL MEJOR LANZAMIENTO DEL AÑO', 34, WHITE, 500); bw = tt[4] + 90; by = 1120 + 20 * (1 - k)
                rr(ctx, W / 2 - bw / 2, by - 44, bw, 88, 4); rgba(ctx, PANEL, a * c01(k * 1.5)); ctx.fill_preserve()
                rgba(ctx, GOLD, a * c01(k * 1.5)); ctx.set_line_width(2); ctx.stroke()
                put(ctx, tt, W / 2, by + 1, alpha=a * c01(k * 1.5))

# ---------------- title (over the hook) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['El', 'mejor'], ['lanzamiento'], ['del', 'año']]
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.45, 0, 0, 0, 0.55 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.8 * a)
    ctx.rectangle(0, 860, W, H - 860); ctx.set_source(g); ctx.fill()
def title(ctx, t):
    if t >= TITLE_END + 0.3: return
    fade = 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    scrim(ctx, fade * c01(t / 0.2))
    n = min(len(LABEL), int(max(0, t - 0.1) / 0.025))
    if n > 0:
        txt = LABEL[:n] if n < len(LABEL) else (LABEL if int(t * 2.2) % 2 == 0 else LABEL[:-1])
        put(ctx, SX(txt, 36, WHITE, 400, 112, shadow=6), 70, 1060, alpha=fade, ax=0)
    t0 = 0.1 + 0.025 * len(LABEL); k = 0
    for li, line in enumerate(TITLE):
        x = 70; y = 1170 + li * 128
        for wd in line:
            tt = SX(wd, 124, CHAMP if wd == 'año' else WHITE, 500, 112, shadow=10, shadow_a=200)
            e = spring(t - (t0 + 0.07 * k), w=12.0, zeta=0.86)
            put(ctx, tt, x, y + 30 * (1 - e), alpha=c01(e * 1.4) * fade, ax=0)
            x += tt[4] + 28; k += 1
    hairline(ctx, 72, 1170 + 2 * 128 + 82, 520, fade, eo(prog(t, t0 + 0.6, 0.6)), GOLDB)

# ---------------- subtitles (dark panel, Saira) ----------------
def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) + 1 for x in cur)
        if len(cur) >= 4 or chars >= 22 or w[2][-1] in '.,?:' or nxt is None or nxt[0] - w[1] > 0.35:
            ch.append(cur); cur = []
    out = []
    for j, c in enumerate(ch):
        st = c[0][0] - 0.03; en = ch[j + 1][0][0] - 0.03 if j + 1 < len(ch) else c[-1][1] + 0.4
        out.append((st, min(en, c[-1][1] + 0.5), ' '.join(x[2] for x in c)))
    return out
CHUNKS = build_chunks()
def subtitles(ctx, t):
    if t < TITLE_END: return
    for st, en, line in CHUNKS:
        if st <= t < en: break
    else: return
    e = c01((t - st) / 0.12)
    tt = SX(line, 56, WHITE, 500, 112); sc = min(1.0, 920 / tt[4])
    pw_, ph_ = (tt[4] + 60) * sc, 90 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, 6); rgba(ctx, PANEL, 0.88 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 1, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.35); ctx.fill()
    x1 = W * c01(t / DUR)
    for hh, al in ((22, 0.12), (12, 0.25), (6, 1.0)):                                # red tail-light line with a soft glow
        ctx.rectangle(0, H - 4 - hh / 2, x1, hh); rgba(ctx, RED, al); ctx.fill()

# ---------------- frame ----------------
def render_frame(fr16, t, fi):
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))
    sdr = full.copy(); hdr = full.copy()
    arr, surf, ctx = fx.new_layer()
    draw_shape(ctx, t); stage(ctx, t); meme_stack(ctx, t, M1, MEMES1); meme_stack(ctx, t, M2, MEMES2)
    title(ctx, t); subtitles(ctx, t); progress(ctx, t)
    surf.flush(); fx.layer_over(sdr, hdr, arr)
    return sdr, hdr

def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    readers = {k: fx.hlg_reader(E.SRCS[k]) for k in E.SRCS}; cur = {k: (-1, None) for k in E.SRCS}
    for fi in want:
        t = fi / FPS
        te = min(t * SPEED, E.TOTAL - 0.001)
        s, st = E.src_of(te)
        if t * SPEED > E.TOTAL: st += t * SPEED - E.TOTAL
        k = int(round(st * FPS))
        while cur[s][0] < k:
            try: cur[s] = next(readers[s])
            except StopIteration: break
        fr = np.frombuffer(cur[s][1], np.uint16).reshape(fx.SH, fx.SW, 3).astype(np.float32) / 65535
        yield fi, t, fr

def build_audio():
    SR = 48000
    with wave.open(os.path.join(HERE, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(DUR * SR); m = np.zeros((n, 2), np.float32); m[:min(n, len(v))] = v[:n]
    with wave.open(os.path.join(HERE, 'mix.wav'), 'wb') as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())

def hdr_encoder(out_hdr, audio_wav):
    common = ['-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)]
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb48le', '-color_range', 'pc', '-i', '-', '-i', audio_wav,
                            '-vf', 'scale=out_color_matrix=bt2020:in_range=pc:out_range=tv:flags=bicubic+accurate_rnd,format=yuv420p10le',
                            '-c:v', 'libx265', '-crf', '17', '-preset', 'medium', '-tag:v', 'hvc1',
                            '-x265-params', 'colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error',
                            '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_hdr], stdin=subprocess.PIPE)

def main():
    mode_ = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode_ == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(HERE, 'prev'), exist_ok=True)
        for fi, t, fr in frames(times):
            sdr, hdr = render_frame(fr, t, fi)
            Image.fromarray(fx.to8(sdr)).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    eh = hdr_encoder(sys.argv[2], os.path.join(HERE, 'mix.wav'))          # HDR only
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t, fi)
        eh.stdin.write(np.ascontiguousarray(fx.to16(hdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    eh.stdin.close(); eh.wait()
    print('done', sys.argv[2])

if __name__ == '__main__':
    main()
