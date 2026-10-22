"""IMG_9108 · Idea de startup: una app que te recomiende restaurantes. No footage exists, so every idea is a drawn,
interactive motion graphic (chat with friends, the app asking your cravings, a Bogotá map with new places, trust bars, newsletter,
the pay button). House look (dark cards, Geist), warm orange accent, slow springs. Street audio cleaned with DeepFilterNet3. HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit26 as E; os.chdir(_cwd)

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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v26.json')))['segments'] for w in s['words']]
FIX = {2: 'les', 35: '¿Por', 48: 'los', 49: 'gustos', 135: 'gusto', 216: 'manes', 236: 'mande', 257: 'están en', 258: 'tendencia', 272: 'utilizaría'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(27) - 0.15                                                  # title over the question, until "Abre TikTok"

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

def R(name): return os.path.join(REF, name)
# ---------------- house look (dark cards, Geist) with a warm "food" accent; everything drawn, no stock footage ----------------
ACC = C(255, 107, 61)                                                       # warm orange
ACC2 = C(255, 196, 120)
MAP_BG, STREET = C(20, 20, 26), C(44, 44, 54)
def bubble(ctx, x, y, txt, a, me=False, size=26, maxw=420):
    if a <= 0.002: return 0
    tt = GT(txt, size, WHITE, 'Medium'); w = min(maxw, tt[4] + 40); h = size * 2.0
    x0 = x - w if me else x
    rr(ctx, x0, y, w, h, 18); rgba(ctx, ACC if me else C(44, 44, 52), a); ctx.fill(); put(ctx, tt, x0 + 20, y + h / 2 + 1, alpha=a, ax=0)
    return h
def chip(ctx, x, y, txt, a, on=0.0, size=26):
    """toggle chip: outline -> filled accent when on"""
    if a <= 0.002: return 0
    tt = GT(txt, size, WHITE, 'Medium'); w = tt[4] + 44; h = size * 1.9
    rr(ctx, x, y - h / 2, w, h, h / 2)
    if on > 0: rgba(ctx, ACC, a * on); ctx.fill_preserve()
    rgba(ctx, C(90, 90, 100) if on < 0.5 else ACC, a); ctx.set_line_width(2); ctx.stroke()
    put(ctx, tt, x + 22, y + 1, alpha=a, ax=0); return w
def pin(ctx, x, y, s, col, a, label=None):
    if a <= 0.002: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, 0); ctx.curve_to(-14, -16, -16, -26, -16, -32); ctx.arc(0, -32, 16, math.pi, 0); ctx.curve_to(16, -26, 14, -16, 0, 0); ctx.close_path()
    rgba(ctx, col, a); ctx.fill(); ctx.arc(0, -32, 6, 0, 2 * math.pi); rgba(ctx, MAP_BG, a); ctx.fill(); ctx.restore()
    if label: put(ctx, GT(label, 20, WHITE, 'Medium'), x, y - 54 * s - 12, alpha=a)
def plate(ctx, x, y, r, a, t=0.0):
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(0.95, 0.95, 0.97, a); ctx.fill()
    ctx.arc(x, y, r * 0.72, 0, 2 * math.pi); ctx.set_source_rgba(0.85, 0.85, 0.9, a); ctx.fill()
    for j, (dx, dy, rr_, col) in enumerate(((-0.2, -0.1, 0.22, ACC), (0.18, 0.05, 0.18, C(120, 190, 90)), (0.0, 0.25, 0.16, ACC2))):
        ctx.arc(x + dx * r, y + dy * r, rr_ * r, 0, 2 * math.pi); rgba(ctx, col, a); ctx.fill()
def xmark(ctx, x, y, s, a, k=1.0):
    if a <= 0.002 or k <= 0: return
    for j in range(2):
        kk = c01(k * 2 - j)
        if kk <= 0: continue
        sx, sy = (x - s / 2, y - s / 2) if j == 0 else (x + s / 2, y - s / 2)
        ex, ey = (x + s / 2, y + s / 2) if j == 0 else (x - s / 2, y + s / 2)
        ctx.move_to(sx, sy); ctx.line_to(sx + (ex - sx) * kk, sy + (ey - sy) * kk)
    rgba(ctx, BAD, a); ctx.set_line_width(max(3, s * 0.16)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(21) - 0.15, 'search', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(35) - 0.10, 'ask', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(59) - 0.10, 'city', CX, 260, 1000, 420, 26, MAP_BG[:3]),
    (T(88) - 0.10, 'trust', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(116) - 0.10, 'idea', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(151) - 0.10, 'nobody', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(166) - 0.10, 'hungry', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(192) - 0.10, 'opp', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(213) - 0.10, 'site', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(234) - 0.10, 'news', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(261) - 0.10, 'pay', CX, 260, 1000, 420, 26, CARD[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000                                   # hair from y~480, eyes ~820
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

_rng = np.random.RandomState(4)
NEWPINS = [(_rng.uniform(380, 940), _rng.uniform(110, 380)) for _ in range(12)]
HOME, USUAL = (150, 330), (300, 170)

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'search':                                                    # "abre TikTok o le pregunta a sus amigos"
        k1 = pop(t, T(27) - 0.25)
        put(ctx, GT('¿Qué es lo primero que haces?', 34, WHITE, 'SemiBold'), w / 2, h / 2, alpha=a * (1 - c01(k1 * 2)))
        x0 = 40; ph = h - 70
        rr(ctx, x0, 35, 230, ph, 22); rgba(ctx, C(8, 8, 10), a * c01(k1 * 1.5)); ctx.fill()
        scroll = ((t - st0) * 150) % 230                                     # a vertical food feed scrolling
        ctx.save(); rr(ctx, x0, 35, 230, ph, 22); ctx.clip()
        for j in range(4):
            yy = 35 + j * 230 - scroll
            plate(ctx, x0 + 115, yy + 115, 70, a * c01(k1 * 1.5), t)
            put(ctx, GT('Lo tienes que probar', 18, WHITE, 'Medium'), x0 + 115, yy + 212, alpha=a * c01(k1 * 1.5))
        ctx.restore()
        put(ctx, GT('TikTok', 26, WHITE, 'SemiBold'), x0 + 115, h - 18, alpha=a * c01(k1 * 1.5))
        put(ctx, GT('o', 34, MUTE, 'Medium'), 330, h / 2, alpha=a * c01(pop(t, T(29) - 0.1) * 1.5))
        k2 = pop(t, T(30) - 0.15)
        rr(ctx, 380, 35, w - 420, ph, 22); rgba(ctx, PANEL, a * c01(k2 * 1.5)); ctx.fill()
        put(ctx, GT('Amigos', 26, WHITE, 'SemiBold'), 410, 72, alpha=a * c01(k2 * 1.5), ax=0)
        y = 110
        for j, (tt_, txt, me) in enumerate(((T(30) - 0.1, '¿Dónde comemos hoy?', True), (T(32) - 0.1, 'Ni idea…', False), (T(34) - 0.1, '¿El de siempre?', False))):
            k = pop(t, tt_)
            if k <= 0.001: continue
            hh = bubble(ctx, (w - 70) if me else 410, y + 14 * (1 - k), txt, a * c01(k * 1.5), me)
            y += hh + 14
    elif name == 'ask':                                                     # "una aplicación que le puedas preguntar… dependiendo de tus gustos… y te recomiende"
        put(ctx, GT('¿Por qué no existe esto?', 26, MUTE), 40, 50, alpha=a, ax=0)
        rr(ctx, 40, 80, w - 80, 70, 35); rgba(ctx, PANEL, a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
        q = typed('Recomiéndame un restaurante para hoy', t, T(41) - 0.1, 28)
        put(ctx, GT(q or ' ', 28, WHITE), 76, 116, alpha=a, ax=0)
        if int(t * 2.4) % 2 == 0 and t < T(53): ctx.rectangle(80 + GT(q or ' ', 28, WHITE)[4], 98, 3, 36); rgba(ctx, ACC, a); ctx.fill()
        put(ctx, GT('Tus gustos', 22, MUTE), 40, 196, alpha=a * c01(pop(t, T(46) - 0.15) * 1.5), ax=0)
        x = 40
        for j, (lbl, tt_) in enumerate((('Italiano', T(47)), ('Cerca', T(49)), ('Para una cita', T(50)), ('Algo nuevo', T(52)))):
            k = pop(t, tt_ - 0.15)
            if k <= 0.001: break
            x += chip(ctx, x + 10 * (1 - k), 240, lbl, a * c01(k * 1.5), on=c01((t - tt_) / 0.2)) + 14
        k = pop(t, T(56) - 0.15)                                            # "te recomiende el restaurante"
        if k > 0.001:
            aa = a * c01(k * 1.5); yy = 290 + 20 * (1 - k)
            rr(ctx, 40, yy, w - 80, 100, 18); rgba(ctx, C(30, 22, 18), aa); ctx.fill_preserve(); rgba(ctx, ACC, aa); ctx.set_line_width(2); ctx.stroke()
            plate(ctx, 100, yy + 50, 34, aa)
            put(ctx, GT('Te recomiendo este', 28, WHITE, 'SemiBold'), 154, yy + 36, alpha=aa, ax=0)
            put(ctx, GT('Italiano · a 8 min · abrió esta semana', 22, MUTE), 154, yy + 70, alpha=aa, ax=0)
            put(ctx, GT('96% para ti', 26, ACC, 'SemiBold'), w - 70, yy + 50, alpha=aa, ax=1)
    elif name == 'city':                                                    # "en Bogotá todas las semanas se abren… y uno termina yendo a los mismos"
        for gx in range(0, int(w), 90): ctx.rectangle(gx, 0, 3, h); rgba(ctx, STREET, a); ctx.fill()
        for gy in range(30, int(h), 80): ctx.rectangle(0, gy, w, 3); rgba(ctx, STREET, a); ctx.fill()
        ctx.move_to(0, h * 0.8); ctx.line_to(w, h * 0.25); rgba(ctx, C(60, 60, 72), a); ctx.set_line_width(10); ctx.stroke()
        put(ctx, GT('Bogotá', 30, WHITE, 'SemiBold'), 36, 46, alpha=a, ax=0)
        same = c01((t - (T(72) - 0.1)) / 0.4)                               # new places dim when I say "uno termina yendo a los mismos"
        for j, (px, py) in enumerate(NEWPINS):
            k = pop(t, T(64) - 0.2 + 0.28 * j, w=11, zeta=0.7)
            if k <= 0.001: continue
            pin(ctx, px, py, 0.9 * k, ACC, a * (1 - 0.65 * same), 'Nuevo' if j % 3 == 0 and same < 0.5 else None)
            qk = pop(t, T(81) - 0.1 + 0.05 * j)                              # "desconoce o no sabe a dónde ir"
            if qk > 0.001: put(ctx, GT('?', 28, WHITE, 'Bold'), px + 18, py - 50, alpha=a * c01(qk * 1.5) * 0.85)
        n = sum(1 for j in range(len(NEWPINS)) if t > T(64) - 0.2 + 0.28 * j)
        if n: put(ctx, GT('Nuevos esta semana', 22, MUTE), w - 40, 40, alpha=a * (1 - same), ax=1)
        ctx.arc(*HOME, 12, 0, 2 * math.pi); rgba(ctx, ACC2, a); ctx.fill(); put(ctx, GT('Tú', 22, WHITE, 'SemiBold'), HOME[0], HOME[1] + 30, alpha=a)
        pin(ctx, USUAL[0], USUAL[1], 1.1, WHITE, a * c01(same * 2), 'El de siempre')
        if same > 0:
            u = ((t - T(72)) / 1.1) % 1                                      # going there again and again
            px = HOME[0] + (USUAL[0] - HOME[0]) * eio(u); py = HOME[1] + (USUAL[1] - 30 - HOME[1]) * eio(u)
            ctx.move_to(*HOME); ctx.line_to(USUAL[0], USUAL[1] - 30); rgba(ctx, ACC2, a * 0.5 * same); ctx.set_line_width(3); ctx.set_dash([8, 8]); ctx.stroke(); ctx.set_dash([])
            ctx.arc(px, py, 9, 0, 2 * math.pi); rgba(ctx, ACC2, a * same); ctx.fill()
    elif name == 'trust':                                                   # TikTok vs a friend
        put(ctx, GT('¿En quién confías?', 34, WHITE, 'SemiBold'), 40, 66 + lift, alpha=a, ax=0)
        for j, (lbl, val, tt_, col) in enumerate((('Un video en TikTok', 0.28, T(96) - 0.1, C(150, 150, 160)), ('Un amigo que te lo recomienda', 0.92, T(111) - 0.1, ACC))):
            k = pop(t, tt_ - 0.4); y = 150 + j * 120
            put(ctx, GT(lbl, 26, WHITE, 'Medium'), 40, y, alpha=a * c01(k * 1.5), ax=0)
            rr(ctx, 40, y + 30, w - 80, 34, 17); rgba(ctx, PANEL, a); ctx.fill()
            fill = (w - 80) * val * eio(prog(t, tt_, 1.0))
            if fill > 2: rr(ctx, 40, y + 30, fill, 34, 17); rgba(ctx, col, a); ctx.fill()
            if fill > 2: put(ctx, GT('%d%%' % int(round(100 * fill / (w - 80))), 22, WHITE, 'SemiBold'), 40 + fill - 12, y + 47, alpha=a, ax=1)
        put(ctx, GT('Confianza (ilustrativo)', 18, DIM), w - 40, h - 26, alpha=a, ax=1)
    elif name == 'idea':                                                    # the app: "dependiendo del gusto… de lo que uno quiera ese día" -> recommendation
        rr(ctx, 40, 30, 380, h - 60, 30); rgba(ctx, C(8, 8, 10), a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(2); ctx.stroke()
        put(ctx, GT('¿Qué se te antoja', 26, WHITE, 'SemiBold'), 70, 84, alpha=a, ax=0); put(ctx, GT('hoy?', 26, WHITE, 'SemiBold'), 70, 118, alpha=a, ax=0)
        moods = [('Algo nuevo', T(142) - 0.1), ('Sushi', T(135) - 0.1), ('Barato', 1e9), ('Para cita', 1e9)]
        for j, (lbl, ton) in enumerate(moods):
            k = pop(t, st0 + 0.3 + 0.12 * j)
            chip(ctx, 70 + (j % 2) * 170, 180 + (j // 2) * 64, lbl, a * c01(k * 1.5), on=c01((t - ton) / 0.2), size=22)
        put(ctx, GT('Tu app de restaurantes', 20, MUTE), 230, h - 52, alpha=a)
        k = pop(t, T(144) - 0.1)                                            # "ese día": the recommendation lands
        if k > 0.001:
            aa = a * c01(k * 1.5); x = 470 + 30 * (1 - k)
            rr(ctx, x, 60, w - x - 40, 230, 22); rgba(ctx, C(30, 22, 18), aa); ctx.fill_preserve(); rgba(ctx, ACC, aa); ctx.set_line_width(2); ctx.stroke()
            plate(ctx, x + 80, 175, 56, aa)
            put(ctx, GT('Para hoy', 22, ACC, 'SemiBold'), x + 160, 110, alpha=aa, ax=0)
            put(ctx, GT('Sushi que abrió', 30, WHITE, 'SemiBold'), x + 160, 152, alpha=aa, ax=0)
            put(ctx, GT('esta semana', 30, WHITE, 'SemiBold'), x + 160, 190, alpha=aa, ax=0)
            put(ctx, GT('a 10 min · según tus gustos', 20, MUTE), x + 160, 230, alpha=aa, ax=0)
        km = pop(t, T(149) - 0.15)                                          # "mega hit"
        if km > 0.001: gpill(ctx, 470 + (w - 510) / 2, 340, 'Sería un mega hit', a * c01(km * 1.5), 'pink', size=26, h=58, icon=False)
    elif name == 'nobody':                                                  # "aquí nadie ve TripAdvisor, nadie entra a Google a buscar restaurantes"
        put(ctx, GT('Aquí nadie busca así', 34, WHITE, 'SemiBold'), 40, 66 + lift, alpha=a, ax=0)
        for j, (txt, tt_) in enumerate((('TripAdvisor', T(157)), ('Google: restaurantes cerca', T(162)))):
            k = pop(t, tt_ - 0.4); y = 150 + j * 110
            rr(ctx, 40, y, w - 80, 76, 38); rgba(ctx, PANEL, a * c01(k * 1.5)); ctx.fill_preserve(); rgba(ctx, LINE, a * c01(k * 1.5)); ctx.set_line_width(1.5); ctx.stroke()
            ctx.arc(84, y + 38, 13, 0, 2 * math.pi); rgba(ctx, MUTE, a * c01(k * 1.5)); ctx.set_line_width(3); ctx.stroke()
            ctx.move_to(93, y + 47); ctx.line_to(104, y + 58); ctx.stroke()
            tt = GT(txt, 30, WHITE, 'Medium'); put(ctx, tt, 124, y + 39, alpha=a * c01(k * 1.5), ax=0)
            ks = eo(prog(t, tt_ + 0.25, 0.4))
            if ks > 0: ctx.rectangle(118, y + 37, (tt[4] + 14) * ks, 4); rgba(ctx, BAD, a); ctx.fill()
            xmark(ctx, w - 90, y + 38, 30, a, prog(t, tt_ + 0.4, 0.4))
    elif name == 'hungry':                                                  # "tiene hambre… quiero probar algo nuevo… nada fácil y rápido"
        cx, cy, R = 170, h / 2 + 10, 110
        ctx.arc(cx, cy, R, 0, 2 * math.pi); rgba(ctx, PANEL, a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(3); ctx.stroke()
        ang = (t - st0) * 2.2                                               # the clock keeps running
        ctx.move_to(cx, cy); ctx.line_to(cx + 0.8 * R * math.sin(ang), cy - 0.8 * R * math.cos(ang)); rgba(ctx, ACC, a); ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.move_to(cx, cy); ctx.line_to(cx + 0.5 * R * math.sin(ang / 12), cy - 0.5 * R * math.cos(ang / 12)); rgba(ctx, WHITE, a); ctx.set_line_width(6); ctx.stroke()
        put(ctx, GT('Tengo hambre', 24, ACC, 'SemiBold'), cx, cy + R + 30, alpha=a * c01(pop(t, T(169) - 0.15) * 1.5))
        k = pop(t, T(174) - 0.15)
        if k > 0.001:
            rr(ctx, 360, 50 + 14 * (1 - k), 560, 90, 45); rgba(ctx, C(44, 44, 52), a * c01(k * 1.5)); ctx.fill()
            put(ctx, GT('"Quiero probar algo nuevo"', 30, WHITE, 'Medium'), 640, 96 + 14 * (1 - k), alpha=a * c01(k * 1.5))
        for j, (lbl, tt_) in enumerate((('Fácil', T(184)), ('Rápido', T(186)))):
            kk = pop(t, tt_ - 0.2); y = 210 + j * 80
            if kk <= 0.001: continue
            rr(ctx, 380, y, 46, 46, 10); rgba(ctx, LINE, a * c01(kk * 1.5)); ctx.set_line_width(3); ctx.stroke()
            xmark(ctx, 403, y + 23, 26, a, prog(t, tt_ + 0.1, 0.35))
            put(ctx, GT(lbl, 32, WHITE, 'Medium'), 446, y + 24, alpha=a * c01(kk * 1.5), ax=0)
        kn = pop(t, T(189) - 0.15)
        if kn > 0.001: put(ctx, GT('Hoy no existe nada así', 26, MUTE), 380, 380, alpha=a * c01(kn * 1.5), ax=0)
    elif name == 'opp':                                                     # "esa es la oportunidad… lo que hay que estar construyendo"
        cx, cy = 180, h / 2
        glow = 0.6 + 0.4 * math.sin((t - st0) * 3)
        g = cairo.RadialGradient(cx, cy - 20, 10, cx, cy - 20, 150); g.add_color_stop_rgba(0, 1, 0.75, 0.4, 0.45 * a * glow); g.add_color_stop_rgba(1, 1, 0.6, 0.3, 0)
        ctx.arc(cx, cy - 20, 150, 0, 2 * math.pi); ctx.set_source(g); ctx.fill()
        ctx.arc(cx, cy - 30, 62, math.pi * 0.8, math.pi * 2.2); ctx.line_to(cx + 30, cy + 40); ctx.line_to(cx - 30, cy + 40); ctx.close_path(); rgba(ctx, ACC2, a); ctx.fill()
        for j in range(3): rr(ctx, cx - 30, cy + 48 + j * 16, 60, 10, 5); rgba(ctx, MUTE, a); ctx.fill()
        put(ctx, GT('La oportunidad', 64, WHITE, 'SemiBold'), 360, 150 + lift, alpha=a, ax=0)
        put(ctx, GT('Una app que te recomiende', 32, MUTE), 362, 220 + lift, alpha=a * eo(prog(t, st0 + 0.3, 0.5)), ax=0)
        put(ctx, GT('restaurantes a tu gusto', 32, MUTE), 362, 262 + lift, alpha=a * eo(prog(t, st0 + 0.4, 0.5)), ax=0)
        k = pop(t, T(210) - 0.15)
        if k > 0.001: gpill(ctx, 362 + 170, 340 + 10 * (1 - k), 'Constrúyela ahora', a * c01(k * 1.5), 'pink', size=26, h=58, icon=False)
    elif name == 'site':                                                    # "lo hacen muy bien, pero la página tiene que estar actualizada toda la semana"
        rr(ctx, 40, 30, w - 80, h - 60, 18); rgba(ctx, C(245, 245, 247), a); ctx.fill()
        ctx.rectangle(40, 30, w - 80, 46); rgba(ctx, C(225, 225, 230), a); ctx.fill()
        for j, col in enumerate((C(255, 95, 86), C(255, 189, 46), C(39, 201, 63))): ctx.arc(70 + j * 22, 53, 7, 0, 2 * math.pi); rgba(ctx, col, a); ctx.fill()
        put(ctx, GT('Guía de restaurantes · Bogotá', 30, C(20, 20, 24), 'SemiBold'), 80, 120 + lift, alpha=a, ax=0)
        for j in range(3):
            rr(ctx, 80 + j * 290, 160, 270, 90, 12); rgba(ctx, C(228, 228, 234), a); ctx.fill(); plate(ctx, 130 + j * 290, 205, 30, a)
            rr(ctx, 175 + j * 290, 190, 150, 12, 6); rgba(ctx, C(190, 190, 198), a); ctx.fill(); rr(ctx, 175 + j * 290, 214, 100, 10, 5); rgba(ctx, C(205, 205, 212), a); ctx.fill()
        ka = pop(t, T(226) - 0.15)                                          # "tiene que estar… actualizada toda la semana"
        days = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
        if ka > 0.001:
            put(ctx, GT('Actualizada toda la semana', 24, C(80, 80, 90), 'Medium'), 80, 290, alpha=a * c01(ka * 1.5), ax=0)
            for j, d in enumerate(days):
                on = c01((t - (T(229) - 0.2 + 0.28 * j)) / 0.2); x = 80 + j * 120
                rr(ctx, x, 320, 100, 56, 12); rgba(ctx, ACC if on > 0.5 else C(228, 228, 234), a * c01(ka * 1.5)); ctx.fill()
                put(ctx, GT(d, 26, WHITE if on > 0.5 else C(80, 80, 90), 'SemiBold'), x + 50, 349, alpha=a * c01(ka * 1.5))
    elif name == 'news':                                                    # the newsletter: top 5 new / top 5 trending
        rr(ctx, 40, 30, w - 80, h - 60, 18); rgba(ctx, PANEL, a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
        put(ctx, GT('Newsletter semanal', 22, MUTE), 76, 70, alpha=a, ax=0)
        sw = c01((t - (T(250) - 0.15)) / 0.35)                               # second list replaces the first
        for li, (title_, t0) in enumerate((('Top 5 restaurantes que abrieron en Bogotá', T(243) - 0.2), ('Top 5 restaurantes en tendencia', T(250) - 0.1))):
            la = a * ((1 - sw) if li == 0 else sw)
            if la <= 0.002: continue
            put(ctx, GT(title_, 32, WHITE, 'SemiBold'), 76, 116, alpha=la, ax=0)
            for j in range(5):
                k = pop(t, t0 + 0.2 * j); y = 160 + j * 46
                if k <= 0.001: continue
                aa = la * c01(k * 1.5)
                put(ctx, GT('%d' % (j + 1), 26, ACC, 'SemiBold'), 90, y + 18, alpha=aa)
                rr(ctx, 120 + 20 * (1 - k), y + 6, 360 - j * 30, 22, 11); rgba(ctx, C(60, 60, 70), aa); ctx.fill()
                if li == 1:                                                  # a small flame on the trending list
                    fx_, fy_ = 520 - j * 30 + 20 * (1 - k), y + 18
                    ctx.move_to(fx_, fy_ + 12); ctx.curve_to(fx_ - 12, fy_, fx_ - 2, fy_ - 6, fx_, fy_ - 16); ctx.curve_to(fx_ + 4, fy_ - 4, fx_ + 12, fy_, fx_, fy_ + 12); rgba(ctx, ACC, aa); ctx.fill()
        for j, (lbl, on) in enumerate((('Nuevos', 1 - sw), ('En tendencia', sw))):
            x = w - 360 + j * 160
            rr(ctx, x, 50, 140, 40, 20); rgba(ctx, ACC if on > 0.5 else C(44, 44, 52), a); ctx.fill()
            put(ctx, GT(lbl, 20, WHITE, 'Medium'), x + 70, 71, alpha=a)
    elif name == 'pay':                                                     # "ese sería un hit y yo pagaría por eso y lo utilizaría un montón"
        put(ctx, GT('Eso sería un hit', 44, WHITE, 'SemiBold'), 40, 76 + lift, alpha=a, ax=0)
        rr(ctx, 40, 120, 520, 250, 22); rgba(ctx, PANEL, a); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
        put(ctx, GT('Suscripción', 26, WHITE, 'SemiBold'), 76, 166, alpha=a, ax=0)
        put(ctx, GT('Recomendaciones a tu gusto, cada día', 20, MUTE), 76, 202, alpha=a, ax=0)
        tc = T(267) - 0.05; on = c01((t - tc) / 0.15)                       # "yo pagaría"
        rr(ctx, 76, 270, 448, 70, 35); rgba(ctx, OK if on > 0.5 else ACC, a); ctx.fill()
        put(ctx, GT('Suscrito' if on > 0.5 else 'Yo pagaría por esto', 28, WHITE if on <= 0.5 else C(10, 30, 14), 'SemiBold'), 300, 306, alpha=a)
        if on > 0.5: check(ctx, 410, 305, 26, C(10, 30, 14), a, eo(prog(t, tc, 0.3)))
        cx_ = track(t, [(tc - 0.8, 360)], w - 60, w=8.0, zeta=0.95); cy_ = track(t, [(tc - 0.8, 312)], h - 20, w=8.0, zeta=0.95)
        cursor(ctx, cx_, cy_, a * c01((t - tc + 1.0) / 0.3), math.sin(math.pi * c01((t - tc + 0.08) / 0.2)))
        k = pop(t, T(272) - 0.15)                                           # "lo utilizaría un montón"
        if k > 0.001:
            for j in range(5):
                kk = pop(t, T(272) - 0.15 + 0.12 * j)
                rr(ctx, 620 + j * 64, 300 - 40 * j * kk, 46, 40 + 40 * j * kk, 8); rgba(ctx, ACC, a * c01(kk * 1.5)); ctx.fill()
            put(ctx, GT('Lo usaría un montón', 26, WHITE, 'Medium'), 620, 350, alpha=a * c01(k * 1.5), ax=0)

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

# ---------------- title (over the hook), house style ----------------
LABEL = 'teoría by andrés corrales'
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.45, 0, 0, 0, 0.55 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.8 * a)
    ctx.rectangle(0, 860, W, H - 860); ctx.set_source(g); ctx.fill()
TITLE = [['Una', 'idea', 'de'], ['startup', 'que'], ['yo', 'pagaría']]
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.4 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, GT(LABEL[:n], 36, WHITE, 'Regular', shadow=6), 70, 1040, alpha=fade, ax=0)
    k = 0; t0 = 0.15 + 0.03 * len(LABEL)
    for li, line in enumerate(TITLE):
        x = 70; y = 1150 + li * 126
        for wd in line:
            tt = GT(wd, 118, ACC if wd in ('pagaría',) else WHITE, 'SemiBold', shadow=10, shadow_a=200)
            e = 1.0 if force else spring(t - (t0 + 0.09 * k), w=9.0, zeta=0.88)
            put(ctx, tt, x, y + 30 * (1 - e), alpha=c01(e * 1.3) * fade, ax=0); x += tt[4] + 26; k += 1

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
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); rgba(ctx, C(15, 14, 20), 0.9 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 1, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.rectangle(0, H - 8, W * c01(t / DUR), 8); rgba(ctx, ACC); ctx.fill()

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
