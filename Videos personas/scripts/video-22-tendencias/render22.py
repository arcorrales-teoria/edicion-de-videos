"""IMG_9070 (hook) + IMG_9069 · "Cómo ir 2 años por delante en Latinoamérica". 1.05x, voice only (DeepFilterNet3-cleaned).
Same system as video 21: React Bits look (near-black cards, glossy gradient pills, thin line backgrounds), slow springs, one card per idea.
Visual thread: a two-lane timeline (EE. UU. / LATAM) where trend curves are drawn, delayed, copied and pulled ahead. HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = '/Users/acorrales/Desktop/Edición de videos/scripts'
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit22 as E; os.chdir(_cwd)

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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v22.json')))['segments'] for w in s['words']]
FIX = {7: '', 10: 'qué', 17: 'cópielo', 102: '¿Cuándo', 128: 'ahora,', 129: 'con', 130: 'el', 131: 'tema', 132: 'de las', 145: '2021,', 146: '2022,',
       155: '', 158: 'cogió', 163: 'eso,', 164: '', 171: 'Pueden', 238: 'que', 239: 'es', 240: 'tendencia.', 261: 'está', 274: ''}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(32) - 0.1                                                   # title holds the hook until "y esa es la forma…"

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

# ---------------- the morphing card (band above my eyes) ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(14) - 0.10, 'copy', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(42) - 0.10, 'delay', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(64) - 0.10, 'ai', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(102) - 0.10, 'when', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(124) - 0.10, 'example', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(185) - 0.10, 'now', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(224) - 0.10, 'next', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(255) - 0.10, 'ahead', CX, 260, 1000, 420, 26, CARD[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000
SHAPE_ON = STATES[0][0]
LIST_BEAT = (1e9, 1e9)                                                   # no full-screen beat in this video
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

US, LA = GRAD['blue'], GRAD['green']
# ---------------- the two-lane timeline ----------------
Y0, Y1 = 2020, 2029
def lanes(ctx, a, t, x0=170, x1=960, top=78, lane_h=106, gap=22, years=True, labels=True, k_in=1.0):
    """two lanes (EE. UU. above, LATAM below) on a shared year axis; returns a mapper year -> x and the lane baselines"""
    for j, (lbl, g) in enumerate((('EE. UU.', US), ('LATAM', LA))):
        y = top + j * (lane_h + gap)
        rr(ctx, x0 - 120, y, x1 - x0 + 120, lane_h, 14); rgba(ctx, PANEL, a * k_in); ctx.fill_preserve(); rgba(ctx, LINE, a * k_in); ctx.set_line_width(1.5); ctx.stroke()
        if labels:
            ctx.arc(x0 - 96, y + lane_h / 2, 7, 0, 2 * math.pi); rgba(ctx, g[1], a * k_in); ctx.fill()
            put(ctx, GT(lbl, 28, WHITE, 'SemiBold'), x0 - 80, y + lane_h / 2 + 1, alpha=a * k_in, ax=0)
    X = lambda yr: x0 + 20 + (x1 - x0 - 40) * (yr - Y0) / (Y1 - Y0)
    if years:
        ya = top + 2 * lane_h + gap + 24
        for yr in range(Y0 + 1, Y1):
            put(ctx, MT(str(yr), 19, MUTE), X(yr), ya, alpha=a * k_in)
    base = [top + lane_h - 10, top + lane_h + gap + lane_h - 10]
    return X, base, lane_h
def curve(ctx, X, base, lane_h, c, s, col, a, k=1.0, label=None, width=4, glow=True, dim=1.0):
    """a trend: bell-shaped hype curve centred on year c, drawn left->right up to fraction k"""
    if k <= 0 or a <= 0.002: return None
    n = 60; pts = []
    for i in range(int(n * k) + 1):
        yr = c - 2.2 * s + 4.4 * s * i / n
        pts.append((X(yr), base - (lane_h - 30) * math.exp(-((yr - c) / s) ** 2)))
    if len(pts) < 2: return None
    for wd, al in (((14, 0.12), (7, 0.25), (width, 1.0)) if glow else ((width, 1.0),)):
        ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]
        rgba(ctx, col, a * al * dim); ctx.set_line_width(wd); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    if label and k > 0.6:
        px, py = X(c), base - (lane_h - 30)
        put(ctx, GT(label, 25, col, 'SemiBold'), px, py - 16, alpha=a * c01((k - 0.6) * 3) * dim)
    return pts
def bracket(ctx, xa, xb, y, txt, a, k=1.0, col=C(167, 139, 250)):
    if k <= 0.001 or a <= 0.002: return
    xm = xa + (xb - xa) * k
    ctx.move_to(xa, y - 8); ctx.line_to(xa, y); ctx.line_to(xm, y)
    if k > 0.98: ctx.line_to(xb, y - 8)
    rgba(ctx, col, a); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    put(ctx, GT(txt, 25, col, 'SemiBold'), (xa + xb) / 2, y + 22, alpha=a * c01((k - 0.5) * 2))
def arrow_down(ctx, x, y0, y1, a, k, col):
    if k <= 0: return
    ye = y0 + (y1 - y0) * k
    ctx.move_to(x, y0); ctx.line_to(x, ye); rgba(ctx, col, a); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    if k > 0.95:
        ctx.move_to(x - 12, ye - 12); ctx.line_to(x, ye); ctx.line_to(x + 12, ye - 12); ctx.stroke()

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'copy':                                                          # hook: see the US -> copy -> 2 years ahead
        waves(ctx, 0, 0, w, h, t, a, col=C(96, 165, 250))
        k1 = pop(t, st0 + 0.15)
        gpill(ctx, w / 2, 96 + 16 * (1 - k1), 'Lo que pasa en EE. UU.', a * c01(k1 * 1.5), 'blue', size=28, h=62)
        kc = eio(prog(t, T(17) - 0.2, 0.8))                                     # "cópielo exactamente igual"
        arrow_down(ctx, w / 2, 140, 230, a, kc, C(167, 139, 250))
        if kc > 0.3: put(ctx, GT('copiar', 22, C(167, 139, 250), 'Medium'), w / 2 + 24, 186, alpha=a * c01((kc - 0.3) * 3), ax=0)
        k2 = pop(t, T(17) + 0.4)
        gpill(ctx, w / 2, 280 + 16 * (1 - k2), 'Latinoamérica', a * c01(k2 * 1.5), 'green', size=28, h=62)
        k3 = pop(t, T(25) - 0.15)                                               # "dos años delante de todo el mundo"
        if k3 > 0.001:
            tt = GT('+2 años por delante', 26, WHITE, 'SemiBold'); pw = tt[4] + 50
            rr(ctx, w / 2 - pw / 2, 344 + 10 * (1 - k3), pw, 50, 25); rgba(ctx, C(167, 139, 250), a * 0.22 * c01(k3 * 1.5)); ctx.fill()
            put(ctx, tt, w / 2, 369 + 10 * (1 - k3), alpha=a * c01(k3 * 1.5))
    elif name == 'delay':                                                       # the US trend shows up in LATAM 2-3 years later
        X, base, lh = lanes(ctx, a, t)
        put(ctx, GT('Históricamente', 24, MUTE), 30, 42, alpha=a, ax=0)
        curve(ctx, X, base[0], lh, 2021.5, 0.9, US[1], a, eio(prog(t, st0 + 0.3, 1.4)), 'tendencia')
        kd = eio(prog(t, T(49) - 0.15, 1.4))                                    # "un delay de dos a tres años"
        curve(ctx, X, base[1], lh, 2024.0, 0.9, LA[1], a, kd, 'la misma, tarde')
        bracket(ctx, X(2021.5), X(2024.0), 78 + 2 * lh + 22 + 50, '2 a 3 años de delay', a, eo(prog(t, T(51) - 0.1, 0.6)))
    elif name == 'ai':                                                          # everything arrives late, except AI
        put(ctx, GT('¿Cuándo llega a Latinoamérica?', 24, MUTE), 40, 50, alpha=a, ax=0)
        rows = [(st0 + 0.2, 'Inteligencia artificial', 'Al mismo tiempo', OK, 'purple'), (T(80) - 0.15, 'Todo lo demás', '2 años después', C(250, 204, 21), 'blue')]
        for j, (t0, lbl, val, col, g_) in enumerate(rows):
            k = pop(t, t0)
            if k <= 0.001: continue
            y = 96 + j * 150; aa = a * c01(k * 1.5)
            hl = 1.0 if j == 0 and t > T(99) - 0.1 else 0.0                     # "a no ser que sean temas de AI"
            rr(ctx, 40, y + 14 * (1 - k), w - 80, 126, 18); rgba(ctx, PANEL, aa); ctx.fill_preserve()
            rgba(ctx, C(167, 139, 250) if hl else LINE, aa); ctx.set_line_width(2 if hl else 1.5); ctx.stroke()
            gpill(ctx, 60 + 150, y + 63 + 14 * (1 - k), lbl if j else 'IA', aa, g_, size=26, h=56)
            if j == 0: put(ctx, GT(lbl, 22, MUTE), 340, y + 64 + 14 * (1 - k), alpha=aa, ax=0)
            put(ctx, GT(val, 30, col, 'SemiBold'), w - 70, y + 63 + 14 * (1 - k), alpha=aa, ax=1)
    elif name == 'when':                                                        # "dos años después o el año que viene"
        waves(ctx, 0, 0, w, h, t, a)
        put(ctx, GT('¿Cuándo las vemos aquí?', 26, MUTE), w / 2, 70 + lift, alpha=a)
        yrs = [('Hoy en EE. UU.', st0 + 0.3, 'blue'), ('El año que viene', T(119) - 0.1, 'teal'), ('Dos años después', T(116) - 0.1, 'green')]
        for j, (lbl, t0, g_) in enumerate(yrs):
            k = pop(t, t0)
            if k <= 0.001: continue
            x = 180 + j * 320
            gpill(ctx, x, 210 + 16 * (1 - k), lbl, a * c01(k * 1.5), g_, size=22, h=52, icon=False)
            if j: put(ctx, GT('+%d' % j, 44, WHITE, 'SemiBold'), x, 300, alpha=a * c01(k * 1.5))
        ctx.rectangle(180, 252, 640 * eio(prog(t, st0 + 0.4, 2.2)), 2); rgba(ctx, LINE, a); ctx.fill()
    elif name == 'example':                                                     # the "formaciones" wave in the US, 2021-2022
        X, base, lh = lanes(ctx, a, t)
        put(ctx, GT('Ejemplo: las formaciones', 24, MUTE), 30, 42, alpha=a, ax=0)
        curve(ctx, X, base[0], lh, 2021.5, 0.9, US[1], a, eio(prog(t, st0 + 0.3, 2.0)), 'formaciones')
        for yr, i0 in ((2021, 145), (2022, 146)):                                # "2021, 2022"
            k = pop(t, T(i0) - 0.1)
            if k > 0.001: rr(ctx, X(yr) - 34, 78 + 2 * 106 + 22 + 9, 68, 30, 15); rgba(ctx, US[1], a * 0.25 * c01(k * 1.5)); ctx.fill()
        for j, (nm, i0, g_) in enumerate((('Alex Hormozi', 148, 'blue'), ('Iman Gadzhi', 169, 'purple'))):
            k = pop(t, T(i0) - 0.15)
            if k <= 0.001: continue
            x = X(2025.4) + 10; y = 118 + j * 58
            gpill(ctx, x + 20 * (1 - k), y, nm, a * c01(k * 1.5), g_, size=22, h=46)
        kb = pop(t, T(181) - 0.1)                                               # "el man montó bien su vaina"
        if kb > 0.001: check(ctx, X(2025.4) + 130, 118 + 58 + 40, 24, OK, a * c01(kb * 1.5), eo(prog(t, T(181), 0.4)))
    elif name == 'now':                                                         # the same wave, now in LATAM: a 2-year lag
        X, base, lh = lanes(ctx, a, t)
        put(ctx, GT('Lo que ves hoy en Latam', 24, MUTE), 30, 42, alpha=a, ax=0)
        curve(ctx, X, base[0], lh, 2021.5, 0.9, US[1], a, 1.0, 'formaciones', dim=0.55)
        curve(ctx, X, base[1], lh, 2024.6, 0.9, LA[1], a, eio(prog(t, T(203) - 0.2, 1.6)), 'cursos')
        bracket(ctx, X(2021.5), X(2024.6), 78 + 2 * 106 + 22 + 50, 'rezago de 2 años', a, eo(prog(t, T(213) - 0.1, 0.7)))
    elif name == 'next':                                                        # the US moved on: copy the new thing
        X, base, lh = lanes(ctx, a, t)
        put(ctx, GT('Lo nuevo en EE. UU.', 24, MUTE), 30, 42, alpha=a, ax=0)
        fade = 1 - 0.75 * eo(prog(t, T(229) - 0.1, 0.6))                         # "dejó de ser tendencia"
        curve(ctx, X, base[0], lh, 2021.5, 0.9, US[1], a, 1.0, None, dim=0.55 * fade)
        curve(ctx, X, base[1], lh, 2024.6, 0.9, LA[1], a, 1.0, None, dim=0.4 * fade)
        curve(ctx, X, base[0], lh, 2025.6, 0.8, C(167, 139, 250), a, eio(prog(t, T(234) - 0.2, 1.4)), 'lo nuevo')
        kc = eio(prog(t, T(246) - 0.15, 0.7))                                   # "lo copia exactamente igual"
        arrow_down(ctx, X(2026.4), base[0] + 8, base[1] - 70, a, kc, C(167, 139, 250))
        if kc > 0.5: put(ctx, GT('copiar', 20, C(167, 139, 250), 'Medium'), X(2026.4) + 18, (base[0] + base[1]) / 2 - 20, alpha=a * c01((kc - 0.5) * 2), ax=0)
    elif name == 'ahead':                                                       # bring it to LATAM first: years ahead, the reference, the market
        X, base, lh = lanes(ctx, a, t, x1=760)
        put(ctx, GT('Tú, en Latam', 24, MUTE), 30, 42, alpha=a, ax=0)
        curve(ctx, X, base[0], lh, 2025.6, 0.8, C(167, 139, 250), a, 1.0, 'lo nuevo', dim=0.6)
        curve(ctx, X, base[1], lh, 2025.9, 0.75, LA[1], a, eio(prog(t, st0 + 0.3, 1.4)), 'tú, primero')
        curve(ctx, X, base[1], lh, 2027.9, 0.75, C(150, 150, 160), a, eio(prog(t, T(268) - 0.2, 1.0)), None, dim=0.6, glow=False, width=3)
        bracket(ctx, X(2025.9), X(2027.9), 78 + 2 * 106 + 22 + 50, '1 a 2 años por delante', a, eo(prog(t, T(262) - 0.1, 0.7)), OK)
        km = eio(prog(t, T(288) - 0.15, 1.2))                                   # "capturar todo ese mercado"
        cx, cy, R = 880, 140, 56
        if km > 0:
            ctx.arc(cx, cy, R, 0, 2 * math.pi); rgba(ctx, LINE, a); ctx.set_line_width(14); ctx.stroke()
            ctx.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * km); rgba(ctx, LA[1], a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            put(ctx, GT('mercado', 22, WHITE, 'Medium'), cx, cy + 1, alpha=a)
        k = pop(t, T(280) - 0.15)                                               # "se va a volver la referencia"
        if k > 0.001: gpill(ctx, cx, 262 + 12 * (1 - k), 'La referencia', a * c01(k * 1.5), 'green', size=19, h=42)
        kt = pop(t, T(292) - 0.15)                                              # "esa es la teoría de hoy"
        if kt > 0.001: gpill(ctx, cx, 322 + 10 * (1 - kt), 'La teoría de hoy', a * c01(kt * 1.5), 'purple', size=19, h=40, icon=False)

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

# ---------------- title (over the hook) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['Cómo', 'ir', '2', 'años'], ['por', 'delante', 'en'], ['Latinoamérica']]
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.45, 0, 0, 0, 0.55 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.8 * a)
    ctx.rectangle(0, 860, W, H - 860); ctx.set_source(g); ctx.fill()
def title(ctx, t):
    if t >= TITLE_END + 0.4: return
    fade = 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * c01(t / 0.3))
    n = min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0:
        txt = LABEL[:n] if n < len(LABEL) else (LABEL if int(t * 2.2) % 2 == 0 else LABEL[:-1])
        put(ctx, GT(txt, 36, WHITE, 'Regular', shadow=6), 70, 1040, alpha=fade, ax=0)
    t0 = 0.15 + 0.03 * len(LABEL); k = 0
    for li, line in enumerate(TITLE):
        x = 70; y = 1140 + li * 118
        for wd in line:
            tt = GT(wd, 112, C(167, 139, 250) if wd in ('2', 'años') else WHITE, 'SemiBold', shadow=10, shadow_a=200)
            e = spring(t - (t0 + 0.09 * k), w=9.0, zeta=0.88)
            put(ctx, tt, x, y + 30 * (1 - e), alpha=c01(e * 1.3) * fade, ax=0)
            x += tt[4] + 26; k += 1

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
    y0 = 1450 + (1700 - 1450) * beat_a(t, LIST_BEAT)                         # drops below the list while it is on screen
    tt = GT(line, 56, WHITE, 'Medium'); sc = min(1.0, 920 / tt[4])
    pw_, ph_ = (tt[4] + 64) * sc, 92 * sc; y = y0 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); rgba(ctx, C(15, 14, 20), 0.9 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 1, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    x1 = W * c01(t / DUR)
    if x1 > 1:
        g = cairo.LinearGradient(0, 0, W, 0); g.add_color_stop_rgba(0, *GRAD['purple'][0][:3], 1); g.add_color_stop_rgba(1, *GRAD['blue'][1][:3], 1)
        ctx.rectangle(0, H - 8, x1, 8); ctx.set_source(g); ctx.fill()

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
