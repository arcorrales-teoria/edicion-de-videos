"""IMG_9094 · Ramp ("New on Ramp: Q3"), build in public: Croma and AbacatePay. 1.05x, voice only (DeepFilterNet3-cleaned).
Ramp's film plays silent inside the card the whole time I talk about Ramp, with Ramp-lime labels that explain literally what I say.
Then Croma in its own identity (black, tracked mono, node diagram Claude -> Croma -> DIAN / Supersociedades) and AbacatePay in
theirs (white, teal, green, their weekly posts). Cover = title frame in Ramp style. HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit24 as E; os.chdir(_cwd)

SPEED = 1.05
REF = os.path.join(HERE, 'ref')
GF = os.path.expanduser('~/Library/Fonts/')
G = {k: GF + 'Geist-%s.otf' % k for k in ('Light', 'Regular', 'Medium', 'SemiBold', 'Bold')}
GM = GF + 'GeistMono-Regular.otf'
def C(r, g, b, a=1.0): return (r / 255, g / 255, b / 255, a)
BG, CARD, PANEL, LINE = C(11, 10, 16), C(15, 14, 20), C(22, 21, 28), C(38, 37, 46)
WHITE, MUTE, DIM = C(255, 255, 255), C(139, 138, 150), C(90, 89, 100)
GRAD = {'purple': (C(109, 40, 217), C(167, 139, 250)), 'pink': (C(190, 24, 93), C(244, 114, 182)), 'blue': (C(37, 99, 235), C(96, 165, 250)),
        'teal': (C(14, 116, 144), C(103, 232, 249)), 'green': (C(21, 128, 61), C(74, 222, 128))}
OK = C(74, 222, 128); BAD = C(248, 113, 113)

# ---------------- text ----------------
_tc = {}
def _mk(key, f, txt, col, track, shadow, shadow_a):
    asc, desc = f.getmetrics(); sp = track * f.size
    widths = [f.getlength(ch) + sp for ch in txt]; tw = max(1, sum(widths) - sp)
    pad = 10 + int(f.size * 0.22) + shadow * 2
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
def GT(txt, size, col=WHITE, wt='Regular', track=0.0, shadow=0, shadow_a=170):
    key = ('G', txt, size, col, wt, track, shadow, shadow_a)
    return _tc[key] if key in _tc else _mk(key, ImageFont.truetype(G[wt], size), txt, col, track, shadow, shadow_a)
def MT(txt, size, col=WHITE):
    key = ('M', txt, size, col)
    return _tc[key] if key in _tc else _mk(key, ImageFont.truetype(GM, size), txt, col, 0.0, 0, 0)

# ---------------- springs (house style of video 20: slow, settled) ----------------
def spring(x, w=9.0, zeta=0.88):
    if x <= 0: return 0.0
    if zeta >= 1: return 1 - math.exp(-w * x) * (1 + w * x)
    wd = w * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * x) * (math.cos(wd * x) + zeta * w / wd * math.sin(wd * x))
def track(t, events, v0, **kw):
    v, prev = v0, v0
    for te, tgt in events:
        v += (tgt - prev) * spring(t - te, **kw); prev = tgt
    return v
def pop(t, t0, w=9.0, zeta=0.85): return spring(t - t0, w=w, zeta=zeta)

# ---------------- words / timing ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v24.json')))['segments'] for w in s['words']]
FIX = {35: '¿Ves', 41: 'manes', 44: '', 45: 'Una', 60: 'Q3', 61: '', 62: 'de todos', 73: '', 74: 'Si', 78: 'estos', 214: 'compran,', 215: 'esa', 216: 'vaina',
       244: 'Croma', 270: 'DIAN,', 276: 'Supersociedades,', 277: '', 288: 'man', 294: 'AbacatePay.', 312: 'eso.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(35) - 0.15                                                  # title over the hook, until Ramp's film comes in

# ---------------- helpers ----------------
def rr(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
def soft_shadow(ctx, x, y, w, h, r, a):
    for dy, grow, al in [(26, 26, 0.08), (12, 10, 0.10), (3, 1, 0.12)]:
        rr(ctx, x - grow, y - grow + dy, w + 2 * grow, h + 2 * grow, r + grow); ctx.set_source_rgba(0, 0, 0, al * a); ctx.fill()
_img = {}
def img(path, crop=None):
    key = (path, crop)
    if key not in _img:
        im = Image.open(path).convert('RGBA')
        if crop: im = im.crop(crop)
        _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint(ctx, path, crop, x, y, w, h, a, r=0, anchor_top=True):
    """cover-fit, anchored to the top of the screenshot (the hero is what matters)"""
    if a <= 0.002: return
    im, (surf, _b) = img(path, crop); s = max(w / im.width, h / im.height)
    ctx.save(); rr(ctx, x, y, w, h, r) if r else ctx.rectangle(x, y, w, h); ctx.clip()
    oy = y if anchor_top else y + (h - im.height * s) / 2
    ctx.translate(x + (w - im.width * s) / 2, oy); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
def panel(ctx, x, y, w, h, a, r=16, title=None):
    """React Bits window: panel, hairline border, small centred title"""
    rr(ctx, x, y, w, h, r); rgba(ctx, PANEL, a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
    if title:
        put(ctx, GT(title, 20, MUTE), x + w / 2, y + 24, alpha=a)
        ctx.rectangle(x, y + 46, w, 1); rgba(ctx, LINE, a); ctx.fill()
def gpill(ctx, cx, cy, label, a, grad='purple', size=30, h=66, icon=True, scale=1.0):
    """glossy gradient pill with an icon disc (React Bits tools)"""
    if a <= 0.002: return 0
    tt = GT(label, size, WHITE, 'Medium'); w = tt[4] + (h + 46 if icon else 64)
    c1, c2 = GRAD[grad]
    ctx.save(); ctx.translate(cx, cy); ctx.scale(scale, scale); ctx.translate(-w / 2, -h / 2)
    for k, al in ((14, 0.18), (6, 0.25)):                                     # soft coloured glow
        rr(ctx, -k, -k + 4, w + 2 * k, h + 2 * k, (h + 2 * k) / 2); rgba(ctx, c1, al * a * 0.5); ctx.fill()
    g = cairo.LinearGradient(0, 0, w, 0); g.add_color_stop_rgba(0, c1[0], c1[1], c1[2], a); g.add_color_stop_rgba(1, c2[0], c2[1], c2[2], a)
    rr(ctx, 0, 0, w, h, h / 2); ctx.set_source(g); ctx.fill()
    hl = cairo.LinearGradient(0, 0, 0, h); hl.add_color_stop_rgba(0, 1, 1, 1, 0.28 * a); hl.add_color_stop_rgba(0.55, 1, 1, 1, 0)
    rr(ctx, 0, 0, w, h, h / 2); ctx.set_source(hl); ctx.fill()
    if icon:
        ctx.arc(h / 2, h / 2, h / 2 - 8, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.18 * a); ctx.fill()
        ctx.arc(h / 2, h / 2, 7, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.9 * a); ctx.set_line_width(2.5); ctx.stroke()
        put(ctx, tt, h + 10, h / 2 + 1, alpha=a, ax=0)
    else: put(ctx, tt, w / 2, h / 2 + 1, alpha=a)
    ctx.restore(); return w * scale
def waves(ctx, x, y, w, h, t, a, n=16, col=C(167, 139, 250), amp=26):
    """React Bits background lines"""
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    for k in range(n):
        yy = y + h * (k + 0.5) / n
        ctx.move_to(x, yy)
        for i in range(1, 41):
            px = x + w * i / 40; ctx.line_to(px, yy + amp * math.sin(i / 40 * 5.5 + k * 0.35 + t * 0.6))
        rgba(ctx, col, a * (0.08 + 0.10 * math.sin(k * 0.7 + 1) ** 2)); ctx.set_line_width(1.5); ctx.stroke()
    ctx.restore()
def check(ctx, x, y, s, col, a, k=1.0):
    if a <= 0.002 or k <= 0: return
    p0, p1, p2 = (x - 0.5 * s, y), (x - 0.15 * s, y + 0.35 * s), (x + 0.55 * s, y - 0.4 * s)
    L1, L2 = math.dist(p0, p1), math.dist(p1, p2); d = (L1 + L2) * k
    ctx.move_to(*p0)
    if d <= L1: ctx.line_to(p0[0] + (p1[0] - p0[0]) * d / L1, p0[1] + (p1[1] - p0[1]) * d / L1)
    else: ctx.line_to(*p1); u = (d - L1) / L2; ctx.line_to(p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u)
    rgba(ctx, col, a); ctx.set_line_width(max(3, s * 0.16)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def cross(ctx, x, y, s, col, a):
    if a <= 0.002: return
    ctx.move_to(x - s / 2, y - s / 2); ctx.line_to(x + s / 2, y + s / 2); ctx.move_to(x + s / 2, y - s / 2); ctx.line_to(x - s / 2, y + s / 2)
    rgba(ctx, col, a); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def cursor(ctx, x, y, a, press=0.0):
    if a <= 0: return
    s = 1.0 - 0.15 * press
    ctx.save(); ctx.translate(x, y); ctx.scale(1.3 * s, 1.3 * s)
    for k in (0, 1):
        ctx.move_to(0, 0); ctx.line_to(0, 30); ctx.line_to(8, 23); ctx.line_to(13, 34); ctx.line_to(18, 32); ctx.line_to(13, 21); ctx.line_to(23, 21); ctx.close_path()
        if k == 0:
            ctx.save(); ctx.translate(1.5, 2.5); ctx.set_source_rgba(0, 0, 0, 0.3 * a); ctx.fill(); ctx.restore()
        else:
            ctx.set_source_rgba(1, 1, 1, a); ctx.fill_preserve(); ctx.set_source_rgba(0, 0, 0, a); ctx.set_line_width(1.6); ctx.stroke()
    ctx.restore()
def typed(txt, t, t0, cps=26):
    n = int(max(0, t - t0) * cps); return txt[:n]

# ---------------- identities: Ramp (lime / olive), Croma (black, tracked mono), AbacatePay (white, teal, green) ----------------
CLIPS = os.path.join(HERE, 'clips'); TILES = os.path.join(HERE, 'tiles')
LIME, OLIVE, INKR = C(227, 255, 41), C(92, 90, 16), C(28, 30, 8)
CBG, CGREY, FLAGY, FLAGB, FLAGR = C(10, 10, 10), C(150, 150, 150), C(252, 209, 22), C(0, 56, 147), C(206, 17, 38)
AWHITE, ATEAL, AGREEN, APALE = C(250, 251, 249), C(40, 70, 66), C(108, 194, 74), C(234, 246, 226)
CLAUDE = C(217, 119, 87)
_clip = {}
def clip_frame(name, k):
    import glob as _g
    fs = _clip.get(name)
    if fs is None: fs = _clip[name] = sorted(_g.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, k)); key = (name, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == name and isinstance(kk[1], int)]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_clip(ctx, name, k, x, y, w, h, a, r=0):
    if a <= 0.002: return
    im, (surf, _b) = clip_frame(name, k); s = max(w / im.width, h / im.height)
    ctx.save(); rr(ctx, x, y, w, h, r) if r else ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + (w - im.width * s) / 2, y + (h - im.height * s) / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
def tile(ctx, name, x, y, w, h, a, r=14, shadow=True):
    if a <= 0.002: return
    if shadow: soft_shadow(ctx, x, y, w, h, r, a)
    paint(ctx, os.path.join(TILES, name + '.png'), None, x, y, w, h, a, r=r)
def lchip(ctx, x, y, txt, a, fill=LIME, col=INKR, size=26, ax=0.0):
    """Ramp chip: flat lime, dark text, small radius; returns width"""
    if a <= 0.002: return 0
    tt = GT(txt, size, col, 'Medium'); w = tt[4] + 36; h = size * 1.75
    x0 = x - w * ax
    rr(ctx, x0, y - h / 2, w, h, 8); rgba(ctx, fill, a); ctx.fill(); put(ctx, tt, x0 + 18, y + 1, alpha=a, ax=0)
    return w
def arrow(ctx, x0, x1, y, col, a):
    if a <= 0.002: return
    ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.move_to(x1 - 8, y - 8); ctx.line_to(x1, y); ctx.line_to(x1 - 8, y + 8)
    rgba(ctx, col, a); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
def croma_mark(ctx, cx, cy, r, a, t=0.0):
    """Croma's ring of vertical bars"""
    if a <= 0.002: return
    ctx.arc(cx, cy, r, 0, 2 * math.pi); rgba(ctx, C(18, 18, 18), a); ctx.fill_preserve(); rgba(ctx, C(60, 60, 60), a); ctx.set_line_width(2); ctx.stroke()
    for i in range(14):
        ang = 2 * math.pi * i / 14; px = cx + 0.55 * r * math.cos(ang); py = cy + 0.55 * r * math.sin(ang)
        hh = r * (0.16 + 0.10 * (0.5 + 0.5 * math.sin(t * 3 + i)))
        ctx.rectangle(px - 1.5, py - hh / 2, 3, hh); rgba(ctx, WHITE, a); ctx.fill()
def flag_dot(ctx, cx, cy, r, a):
    ctx.save(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.clip()
    ctx.rectangle(cx - r, cy - r, 2 * r, r); rgba(ctx, FLAGY, a); ctx.fill()
    ctx.rectangle(cx - r, cy, 2 * r, r / 2); rgba(ctx, FLAGB, a); ctx.fill()
    ctx.rectangle(cx - r, cy + r / 2, 2 * r, r / 2); rgba(ctx, FLAGR, a); ctx.fill(); ctx.restore()
def cpill(ctx, cx, cy, txt, a, light=False, flag=False, claude=False, size=26):
    """Croma node pill"""
    if a <= 0.002: return
    tt = GT(txt, size, INKR if light else WHITE, 'Regular'); extra = 44 if (flag or claude) else 0
    w = tt[4] + 56 + extra; h = size * 2.1
    rr(ctx, cx - w / 2, cy - h / 2, w, h, h / 2)
    rgba(ctx, WHITE if light else C(26, 26, 26), a); ctx.fill_preserve(); rgba(ctx, C(70, 70, 70) if not light else C(220, 220, 220), a); ctx.set_line_width(1.5); ctx.stroke()
    x0 = cx - w / 2 + 28
    if flag: flag_dot(ctx, x0 + 14, cy, 14, a); x0 += extra
    if claude:
        for i in range(8):
            ang = i * math.pi / 8; ctx.move_to(x0 + 14 - 12 * math.cos(ang), cy - 12 * math.sin(ang)); ctx.line_to(x0 + 14 + 12 * math.cos(ang), cy + 12 * math.sin(ang))
        rgba(ctx, CLAUDE, a); ctx.set_line_width(3); ctx.stroke(); x0 += extra
    put(ctx, tt, x0, cy + 1, alpha=a, ax=0)
def tracked(txt, size, col, track=0.35): return GT(txt, size, col, 'Medium', track=track)

# ---------------- the morphing card ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(35) - 0.15, 'ramp', CX, 300, 1000, 562, 18, INKR[:3]),
    (T(228) - 0.10, 'croma', CX, 300, 1000, 562, 18, CBG[:3]),
    (T(262) - 0.10, 'nodes', CX, 300, 1000, 562, 18, CBG[:3]),
    (T(281) - 0.10, 'abacate', CX, 300, 1000, 562, 18, AWHITE[:3]),
    (T(300) - 0.10, 'abacate2', CX, 300, 1000, 562, 18, APALE[:3]),
    (T(313) - 0.10, 'end', CX, 300, 1000, 562, 18, LIME[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 574, 1000                                  # my hair starts at y~510, eyes ~830
SHAPE_ON = STATES[0][0]
LIST_BEAT = (1e9, 1e9)
def beat_a(t, b, din=0.35, dout=0.35): return c01((t - b[0]) / din) * (1 - c01((t - b[1]) / dout))
def shape_geo(t):
    keys = []
    for k in range(8):
        ev = [(s[0], (s[2], s[3], s[4], s[5], s[6], *s[7])[k]) for s in STATES[1:]]
        v0 = (STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7])[k]
        keys.append(track(t, ev, v0, w=9.0, zeta=0.9))
    return keys
def state_alpha(t, i):
    a = STATES[i][0]; b = STATES[i + 1][0] if i + 1 < len(STATES) else 1e9
    return c01((t - a - 0.10) / 0.35) * (1 - c01((t - b) / 0.30))

RAMP_T0 = T(35) - 0.15                                                     # their film plays, silent, the whole time I talk about Ramp
STRIP = [  # (start, end, label, [(t, chip)])
    (T(56) - 0.15, T(73) - 0.2, 'Repasaron todo lo que lanzaron en el Q3', [(T(67) - 0.15, 'Hasta los features más pequeños')]),
    (T(73) - 0.2, T(98) - 0.2, 'No es el gran feature', [(T(91) - 0.15, 'Ramp ya es un buen producto')]),
    (T(98) - 0.2, T(160) - 0.2, 'Lo que logra', [(T(107) - 0.15, 'Conocen la marca'), (T(113) - 0.15, 'Lo usan'), (T(145) - 0.15, 'Lo compran'), (T(152) - 0.15, 'Lo venden adentro')]),
    (T(160) - 0.2, T(183) - 0.2, 'La mejor forma de conseguir', [(T(170) - 0.15, 'Usuarios'), (T(172) - 0.15, 'Clientes'), (T(175) - 0.15, 'Go to market')]),
    (T(183) - 0.2, 1e9, 'Construir en público', [(T(190) - 0.15, 'Que todos vean lo que haces'), (T(220) - 0.15, 'Bola de nieve')]),
]
CROMA_TILES = ['i43_01', 'i44_00', 'i45_02']
ABA_WALL = ['i41_01', 'i42_01', 'i41_02', 'i42_02', 'i41_12', 'i42_11', 'i42_00', 'i42_10', 'i42_12']

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'ramp':
        paint_clip(ctx, 'ramp', int((t - RAMP_T0) * 30), 0, 0, w, h, a)
        for (t0, t1, label, chips) in STRIP:
            sa = a * c01((t - t0) / 0.35) * (1 - c01((t - t1) / 0.3))
            if sa <= 0.002: continue
            g = cairo.LinearGradient(0, h - 170, 0, h); g.add_color_stop_rgba(0, 0.11, 0.12, 0.03, 0); g.add_color_stop_rgba(0.45, 0.11, 0.12, 0.03, 0.88 * sa); g.add_color_stop_rgba(1, 0.11, 0.12, 0.03, 0.95 * sa)
            ctx.rectangle(0, h - 170, w, 170); ctx.set_source(g); ctx.fill()
            put(ctx, GT(label, 30, LIME, 'Medium'), 36, h - 102, alpha=sa, ax=0)
            x = 36; seq = len(chips) > 2
            for j, (tc, txt) in enumerate(chips):
                k = pop(t, tc)
                if k <= 0.001: continue
                if seq and j: arrow(ctx, x - 26, x - 8, h - 46, LIME, sa * c01(k * 1.5))
                cw = lchip(ctx, x + 10 * (1 - k), h - 46, txt, sa * c01(k * 1.5), size=24)
                x += cw + (40 if seq else 16)
    elif name == 'croma':
        put(ctx, tracked('CROMA', 30, C(200, 200, 200), 0.5), 40, 48, alpha=a, ax=0)
        put(ctx, MT('USECROMA.COM', 18, CGREY), w - 40, 48, alpha=a, ax=1)
        q = 1 - c01((t - (T(244) - 0.2)) / 0.3)
        put(ctx, GT('¿Quién más lo hace', 54, WHITE, 'Regular'), w / 2, h / 2 - 40 + lift, alpha=a * q)
        put(ctx, GT('en Latinoamérica?', 54, CGREY, 'Regular'), w / 2, h / 2 + 30 + lift, alpha=a * q)
        k = pop(t, T(244) - 0.15)                                           # "Croma lo hace todo el tiempo"
        if k > 0.001:
            put(ctx, GT('Croma lo comunica todo', 40, WHITE, 'Regular'), 40, 112 + 12 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
            for j, nm in enumerate(CROMA_TILES):
                kj = pop(t, T(250) - 0.15 + 0.35 * j)                       # "sacan nuevas conexiones"
                if kj <= 0.001: continue
                tile(ctx, nm, 40 + j * 312, 160 + 30 * (1 - kj), 296, 370, a * c01(kj * 1.5))
    elif name == 'nodes':                                                   # "así sea la conexión más mínima con la DIAN / Supersociedades"
        put(ctx, tracked('CROMA', 30, C(200, 200, 200), 0.5), 40, 48, alpha=a, ax=0)
        put(ctx, GT('Así sea la conexión más pequeña', 40, WHITE, 'Regular'), 40, 112 + lift, alpha=a, ax=0)
        cx = w / 2
        cpill(ctx, cx, 200, 'Claude', a, claude=True)
        ctx.move_to(cx, 228); ctx.line_to(cx, 262); rgba(ctx, C(80, 80, 80), a); ctx.set_line_width(2); ctx.stroke()
        croma_mark(ctx, cx, 312, 50, a, t)
        for j, (tt_, txt, x) in enumerate(((T(268) - 0.15, 'DIAN', cx - 230), (T(275) - 0.15, 'Supersociedades', cx + 200))):
            k = pop(t, tt_)
            if k <= 0.001: continue
            ctx.move_to(cx, 362); ctx.curve_to(cx, 400, x, 400, x, 440 - 14 * (1 - k)); rgba(ctx, C(80, 80, 80), a * c01(k * 1.5)); ctx.set_line_width(2); ctx.stroke()
            cpill(ctx, x, 470 - 14 * (1 - k), txt, a * c01(k * 1.5), light=True, flag=True)
        k3 = pop(t, T(278) - 0.15)                                          # "lo están haciendo" (they post it)
        if k3 > 0.001: put(ctx, MT('LO PUBLICAN IGUAL', 18, CGREY), w - 40, h - 30, alpha=a * c01(k3 * 1.5), ax=1)
    elif name == 'abacate':
        put(ctx, GT('¿Y en Brasil?', 34, ATEAL, 'Medium'), 40, 52 + lift, alpha=a * (1 - c01((t - T(294)) / 0.3)), ax=0)
        k = pop(t, T(294) - 0.15)                                           # "se llama AbacatePay"
        if k > 0.001:
            ctx.arc(70, 66, 22, 0, 2 * math.pi); rgba(ctx, AGREEN, a * c01(k * 1.5)); ctx.fill()
            ctx.arc(74, 70, 9, 0, 2 * math.pi); rgba(ctx, C(110, 70, 40), a * c01(k * 1.5)); ctx.fill()
            put(ctx, GT('Abacate', 50, ATEAL, 'Bold', track=-0.03), 104, 66, alpha=a * c01(k * 1.5), ax=0)
            put(ctx, GT('Pay', 50, AGREEN, 'Bold', track=-0.03), 104 + GT('Abacate', 50, ATEAL, 'Bold', track=-0.03)[4] + 6, 66, alpha=a * c01(k * 1.5), ax=0)
        kf = pop(t, T(296) - 0.15)                                          # "features todas las semanas"
        if kf > 0.001:
            put(ctx, GT('Features', 70, ATEAL, 'Bold', track=-0.03), 40, 160 + 10 * (1 - kf), alpha=a * c01(kf * 1.5), ax=0)
            put(ctx, GT('todas las semanas', 70, AGREEN, 'Bold', track=-0.03), 40 + GT('Features', 70, ATEAL, 'Bold', track=-0.03)[4] + 18, 160 + 10 * (1 - kf), alpha=a * c01(kf * 1.5), ax=0)
        if k > 0.001:                                                       # their posts start passing as soon as I name them
            off = 40 * (t - T(294))
            ctx.save(); ctx.rectangle(0, 210, w, h - 210); ctx.clip()
            for j, nm in enumerate(ABA_WALL):
                kj = pop(t, T(294) - 0.1 + 0.18 * j)
                if kj <= 0.001: continue
                tile(ctx, nm, 40 + j * 240 - off, 236 + 26 * (1 - kj), 224, 290, a * c01(kj * 1.5), r=12)
            ctx.restore()
    elif name == 'abacate2':                                                # "así sea lo más mínimo: ya puedes pagar con esto, puedes integrar esto"
        put(ctx, GT('Así sea lo más pequeño', 48, ATEAL, 'Bold', track=-0.02), 40, 62 + lift, alpha=a, ax=0)
        for j, (nm, tt_, txt) in enumerate((('i41_10', T(305) - 0.15, 'Ya puedes pagar con tarjeta'), ('i41_11', T(310) - 0.15, 'Ya lo puedes integrar a tu IA'))):
            k = pop(t, tt_)
            if k <= 0.001: continue
            x = 60 + j * 470
            tile(ctx, nm, x, 120 + 24 * (1 - k), 300, 400, a * c01(k * 1.5))
            lchip(ctx, x + 150, 500 + 24 * (1 - k), txt, a * c01(k * 1.5), fill=AGREEN, col=WHITE, size=22, ax=0.5)
    elif name == 'end':                                                     # "eso es lo que hace que tu producto se vuelva viral y que ganes usuarios"
        for r_ in range(5):                                                  # Ramp-style repeated word, faint
            off = (t - st0) * 40 * (1 if r_ % 2 else -1)
            put(ctx, GT('feature  feature  feature  feature  feature', 64, C(28, 30, 8, 0.055), 'Medium'), -200 + off, 60 + r_ * 110, alpha=a, ax=0)
        put(ctx, GT('Comunica', 96, INKR, 'Medium', track=-0.02), w / 2, 190 + lift, alpha=a)
        put(ctx, GT('cada feature.', 96, INKR, 'Medium', track=-0.02), w / 2, 300 + lift, alpha=a * eo(prog(t, st0 + 0.25, 0.5)))
        for j, (tt_, txt) in enumerate(((T(324) - 0.15, 'Tu producto se vuelve viral'), (T(327) - 0.15, 'Ganas usuarios'))):
            k = pop(t, tt_)
            if k > 0.001: lchip(ctx, w / 2 + (-230 if j == 0 else 230), 440 + 14 * (1 - k), txt, a * c01(k * 1.5), fill=INKR, col=LIME, size=28, ax=0.5)

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = c01(spring(t - SHAPE_ON, w=8.0, zeta=0.92)) * (1 - beat_a(t, LIST_BEAT))
    if appear <= 0.01: return
    sc = 0.9 + 0.1 * appear
    f = min(1.0, BAND_H / h, BAND_W / w); cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 36 * (1 - appear)); ctx.scale(sc * f, sc * f); ctx.translate(-w / 2, -h / 2)
    soft_shadow(ctx, 0, 0, w, h, r, appear)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, 0.97 * appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 16 * (1 - eo(c01((t - st[0] - 0.1) / 0.6)))
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore()
    rr(ctx, 0.5, 0.5, w - 1, h - 1, r); rgba(ctx, LINE, appear); ctx.set_line_width(1.5); ctx.stroke()
    ctx.restore()

# ---------------- title (over the hook), Ramp style ----------------
LABEL = 'teoría by andrés corrales'
TITLE = [('Así consigue', False), ('clientes', False), ('Ramp', True)]
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0.06, 0.06, 0.02, 0); g.add_color_stop_rgba(0.45, 0.06, 0.06, 0.02, 0.55 * a); g.add_color_stop_rgba(1, 0.06, 0.06, 0.02, 0.8 * a)
    ctx.rectangle(0, 860, W, H - 860); ctx.set_source(g); ctx.fill()
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.4 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, GT(LABEL[:n], 34, WHITE, 'Regular', shadow=6), 70, 1050, alpha=fade, ax=0)
    for li, (line, lime) in enumerate(TITLE):
        e = 1.0 if force else spring(t - (0.5 + 0.12 * li), w=9.0, zeta=0.88)
        y = 1160 + li * 132 + 26 * (1 - e); aa = c01(e * 1.3) * fade
        if lime:
            tt = GT(line, 124, INKR, 'SemiBold', track=-0.02); wb = (tt[4] + 50) * (c01(e * 1.2) if not force else 1)
            rr(ctx, 56, y - 70, wb, 140, 10); rgba(ctx, LIME, aa); ctx.fill(); put(ctx, tt, 80, y + 2, alpha=aa, ax=0)
        else: put(ctx, GT(line, 124, WHITE, 'SemiBold', track=-0.02, shadow=10, shadow_a=200), 70, y, alpha=aa, ax=0)

# ---------------- subtitles (dark pill) ----------------
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
        st = c[0][0] - 0.03; en = ch[j + 1][0][0] - 0.03 if j + 1 < len(ch) else c[-1][1] + 0.5
        out.append((st, min(en, c[-1][1] + 0.6), ' '.join(x[2] for x in c)))
    return out
CHUNKS = build_chunks()
def subtitles(ctx, t):
    if t < TITLE_END: return
    for st, en, line in CHUNKS:
        if st <= t < en: break
    else: return
    e = c01((t - st) / 0.12)
    tt = GT(line, 56, WHITE, 'Medium'); sc = min(1.0, 920 / tt[4])
    pw_, ph_ = (tt[4] + 64) * sc, 92 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, 12); ctx.set_source_rgba(0.11, 0.12, 0.03, 0.88 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 1, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.rectangle(0, H - 8, W * c01(t / DUR), 8); rgba(ctx, LIME); ctx.fill()

# ---------------- frame ----------------
def render_frame(fr16, t, fi):
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))
    sdr = full.copy(); hdr = full.copy()
    arr, surf, ctx = fx.new_layer()
    draw_shape(ctx, t); title(ctx, t); subtitles(ctx, t); progress(ctx, t)
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
