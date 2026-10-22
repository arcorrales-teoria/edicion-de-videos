"""IMG_9115 + IMG_9116 · Whop. Whole edit in Whop's look (user request): charcoal cards, Whop orange, white type, their own film
(silent, cover-fit), their flyer clip, founders and billboard photos; subtitles white with the spoken word in Whop orange. Literal labels
over the footage; drawn cards only where there is no footage (bots pipeline, US$200M counter, Shopify vs Whop, growth engine). HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit27 as E; os.chdir(_cwd)

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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v27.json')))['segments'] for w in s['words']]
FIX = {152: 'imaginan,', 157: 'pelaos', 166: 'tiene', 167: '', 270: 'influencers,', 336: 'Whop.', 362: 'en', 363: 'ellos', 364: 'inmediatamente.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(13) - 0.15                                                  # title over the hook, until "Montaron una página"

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
# ---------------- Whop look: charcoal cards, Whop orange (#FE6243), white type, their own film and photos ----------------
WO = C(254, 98, 67); CHAR = C(20, 18, 18); CHAR2 = C(34, 31, 30)
CLIPS = os.path.join(HERE, 'clips')
_cl = {}
def clip_img(name, k):
    import glob as _g
    fs = _cl.get(name)
    if fs is None: fs = _cl[name] = sorted(_g.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, k)); key = ('CL', name, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == 'CL' and kk[1] == name]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key], len(fs)
def paint_clip(ctx, name, t, t0, x, y, w, h, a, rate=1.0, r=0):
    if a <= 0.002: return
    (im, (surf, _b)), n = clip_img(name, int(max(0, t - t0) * 30 * rate)); s = max(w / im.width, h / im.height)
    ctx.save(); rr(ctx, x, y, w, h, r) if r else ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + (w - im.width * s) / 2, y + (h - im.height * s) / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
def paint_seq(ctx, t, seq, x, y, w, h, a):
    """seq = [(start, clip, rate)] crossfading"""
    for j, (t0, nm, rate) in enumerate(seq):
        t1 = seq[j + 1][0] if j + 1 < len(seq) else 1e9
        fa = (c01((t - t0) / 0.3) if j else 1.0) * (1 - c01((t - t1) / 0.3))
        if fa > 0.002 and t >= t0 - 0.01: paint_clip(ctx, nm, t, t0, x, y, w, h, a * fa, rate)
def ochip(ctx, x, y, txt, a, size=26, filled=True):
    """Whop chip: orange fill, white text (or outline)"""
    if a <= 0.002: return 0
    tt = GT(txt, size, WHITE, 'SemiBold'); w = tt[4] + 40; h = size * 1.85
    rr(ctx, x, y - h / 2, w, h, h / 2)
    if filled: rgba(ctx, WO, a); ctx.fill()
    else: rgba(ctx, WO, a); ctx.set_line_width(2.5); ctx.stroke()
    put(ctx, tt, x + 20, y + 1, alpha=a, ax=0); return w
def strip(ctx, t, w, h, a, label, chips, t0, t1, arrows=False):
    sa = a * c01((t - t0) / 0.35) * (1 - c01((t - t1) / 0.3))
    if sa <= 0.002: return
    g = cairo.LinearGradient(0, h - 170, 0, h); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.5, 0, 0, 0, 0.72 * sa); g.add_color_stop_rgba(1, 0, 0, 0, 0.86 * sa)
    ctx.rectangle(0, h - 170, w, 170); ctx.set_source(g); ctx.fill()
    put(ctx, GT(label, 32, WHITE, 'SemiBold'), 34, h - 100, alpha=sa, ax=0)
    x = 34
    for j, (tc, txt) in enumerate(chips):
        k = pop(t, tc); cw = GT(txt, 24, WHITE, 'SemiBold')[4] + 40
        if k > 0.001:
            if arrows and j:
                ctx.move_to(x - 30, h - 44); ctx.line_to(x - 10, h - 44); ctx.move_to(x - 18, h - 52); ctx.line_to(x - 10, h - 44); ctx.line_to(x - 18, h - 36)
                rgba(ctx, WHITE, sa * c01(k * 1.5)); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            ochip(ctx, x + 10 * (1 - k), h - 44, txt, sa * c01(k * 1.5), size=24)
        x += cw + (40 if arrows else 14)
def photo(ctx, name, x, y, w, h, a, zoom_t=0.0):
    if a <= 0.002: return
    z = 1.0 + 0.04 * c01(zoom_t / 6.0)
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(z, z); ctx.translate(-(x + w / 2), -(y + h / 2))
    paint(ctx, os.path.join(REF, name), None, x, y, w, h, a, anchor_top=False); ctx.restore()

CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (0.35, 'founders', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(13) - 0.10, 'bots', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(31) - 0.10, 'raise', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(52) - 0.10, 'logo', CX, 260, 1000, 420, 22, (1, 1, 1)),
    (T(58) - 0.10, 'what', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(85) - 0.10, 'started', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(103) - 0.10, 'shopify', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(150) - 0.10, 'genios', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(175) - 0.10, 'partners', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(223) - 0.10, 'engine', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(242) - 0.10, 'jake', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(252) - 0.10, 'influ', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(289) - 0.10, 'marketing', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(305) - 0.10, 'market', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(337) - 0.10, 'pay', CX, 260, 1000, 420, 22, CHAR[:3]),
    (T(347) - 0.10, 'end', CX, 260, 1000, 420, 22, (1, 1, 1)),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000                                   # hair from y~400, eyes ~690
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

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'founders':
        photo(ctx, 'w04.png', 0, 0, w, h, a, t - st0)
        strip(ctx, t, w, h, a, 'Los fundadores de Whop', [(T(6) - 0.1, 'Revendían sneakers'), (T(11) - 0.1, 'en Facebook')], st0, 1e9)
    elif name == 'bots':                                                    # their first site: buy sneakers with bots, resell on Facebook
        put(ctx, GT('Su primera página', 26, MUTE), 40, 50, alpha=a, ax=0)
        nodes = [(T(17) - 0.15, 'Lanzamiento', 'de sneakers'), (T(25) - 0.15, 'Bots que', 'los compran'), (T(28) - 0.15, 'Reventa', 'en Facebook')]
        for j, (tt_, l1, l2) in enumerate(nodes):
            k = pop(t, tt_); x = 60 + j * 320
            if k <= 0.001: continue
            aa = a * c01(k * 1.5); yy = 130 + 20 * (1 - k)
            rr(ctx, x, yy, 260, 200, 20); rgba(ctx, CHAR2, aa); ctx.fill_preserve(); rgba(ctx, WO if j == 2 else LINE, aa); ctx.set_line_width(2); ctx.stroke()
            put(ctx, GT('%02d' % (j + 1), 24, WO, 'SemiBold'), x + 24, yy + 36, alpha=aa, ax=0)
            put(ctx, GT(l1, 32, WHITE, 'SemiBold'), x + 24, yy + 112, alpha=aa, ax=0)
            put(ctx, GT(l2, 32, WHITE, 'SemiBold'), x + 24, yy + 152, alpha=aa, ax=0)
            if j:
                ka = eo(prog(t, tt_, 0.4)); ctx.move_to(x - 54, yy + 100); ctx.line_to(x - 54 + 40 * ka, yy + 100)
                rgba(ctx, WO, aa); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    elif name == 'raise':                                                   # "acaban de levantar 200 millones… Sequoia"
        put(ctx, GT('Acaban de levantar', 30, MUTE), w / 2, 90 + lift, alpha=a)
        v = 200 * eio(prog(t, T(36) - 0.2, 1.2))
        put(ctx, GT('US$%dM' % int(round(v)), 170, WO, 'SemiBold'), w / 2, 220, alpha=a)
        k = pop(t, T(43) - 0.15)
        if k > 0.001:
            tt = GT('Liderado por Sequoia' if t > T(51) - 0.2 else 'Liderado por el mejor fondo', 28, WHITE, 'SemiBold'); pw = tt[4] + 50
            rr(ctx, w / 2 - pw / 2, 330 + 12 * (1 - k) - 28, pw, 56, 28); rgba(ctx, CHAR2, a * c01(k * 1.5)); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
            put(ctx, tt, w / 2, 331 + 12 * (1 - k), alpha=a * c01(k * 1.5))
    elif name == 'logo':
        paint(ctx, os.path.join(REF, 'w02.png'), None, 140, 60 + lift, w - 280, h - 120, a, anchor_top=False)
    elif name == 'what':                                                    # what Whop is: their own film + literal chips
        paint_seq(ctx, t, [(st0, 'prod', 1.0), (T(66) - 0.25, 'any', 1.0)], 0, 0, w, h, a)   # 'cualquier tipo de negocio': their film's examples
        strip(ctx, t, w, h, a, 'Whop te permite', [(T(67) - 0.15, 'Cualquier negocio'), (T(72) - 0.15, 'Conectado a tu red'), (T(76) - 0.15, 'Recibir pagos'), (T(79) - 0.15, 'Todo en un lugar')], st0, 1e9)
    elif name == 'started':
        put(ctx, GT('Empezó para', 44, WHITE, 'SemiBold'), 40, 80 + lift, alpha=a, ax=0)
        items = [(T(90), 'Coaches'), (T(92), 'Cursos'), (T(98), 'Comunidades'), (T(102), 'Trading')]
        for j, (tt_, lbl) in enumerate(items):
            k = pop(t, tt_ - 0.2); x = 40 + (j % 2) * 470; y = 170 + (j // 2) * 120
            if k <= 0.001: continue
            aa = a * c01(k * 1.5)
            rr(ctx, x, y + 14 * (1 - k), 450, 100, 18); rgba(ctx, CHAR2, aa); ctx.fill()
            ctx.rectangle(x, y + 14 * (1 - k), 8, 100); rgba(ctx, WO, aa); ctx.fill()
            put(ctx, GT(lbl, 40, WHITE, 'SemiBold'), x + 36, y + 50 + 14 * (1 - k), alpha=aa, ax=0)
    elif name == 'shopify':                                                 # Shopify vs Whop: "everything market para cualquier mercado"
        k0 = pop(t, st0 + 0.1)
        put(ctx, GT('La plataforma global', 30, MUTE), w / 2, 50, alpha=a * c01(k0 * 1.5))
        kv = pop(t, T(120) - 0.2)
        for j, (nm, col) in enumerate((('Shopify', C(150, 150, 150)), ('Whop', WO))):
            x = 40 + j * 480
            if kv <= 0.001: continue
            aa = a * c01(kv * 1.5)
            rr(ctx, x, 86, 440, 300, 20); rgba(ctx, CHAR2, aa); ctx.fill_preserve(); rgba(ctx, col if j else LINE, aa); ctx.set_line_width(2); ctx.stroke()
            put(ctx, GT(nm, 44, col if j else WHITE, 'SemiBold'), x + 30, 140, alpha=aa, ax=0)
        if kv > 0.001: put(ctx, GT('vs', 28, MUTE, 'Medium'), w / 2, 140, alpha=a * c01(kv * 1.5))
        ks = pop(t, T(130) - 0.15)                                          # "únicamente para… venta de productos"
        if ks > 0.001:
            put(ctx, GT('Solo venta de', 30, WHITE, 'Medium'), 70, 220, alpha=a * c01(ks * 1.5), ax=0)
            put(ctx, GT('productos', 30, WHITE, 'Medium'), 70, 260, alpha=a * c01(ks * 1.5), ax=0)
        kw = pop(t, T(144) - 0.15)                                          # "everything market para cualquier mercado"
        if kw > 0.001: put(ctx, GT('Everything market', 30, WHITE, 'Medium'), 550, 210, alpha=a * c01(kw * 1.5), ax=0)
        for j, lbl in enumerate(('Cursos', 'Comunidades', 'Software', 'Productos')):
            kk = pop(t, T(147) - 0.15 + 0.15 * j)
            if kk > 0.001: ochip(ctx, 550 + (j % 2) * 190, 266 + (j // 2) * 58, lbl, a * c01(kk * 1.5), size=22)
    elif name == 'genios':
        photo(ctx, 'w03.png', 0, 0, w, h, a, t - st0)
        strip(ctx, t, w, h, a, 'Unos genios', [(T(168) - 0.15, 'El mayor tiene 25 años'), (T(172) - 0.15, 'Crearon un monstruo')], st0, 1e9)
    elif name == 'partners':                                                # their partner strategy + the real flyer
        paint_seq(ctx, t, [(st0, 'flyer', 0.45)], 30, 30, 214, 360, a)
        rr(ctx, 30, 30, 214, 360, 16); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
        put(ctx, GT('Su estrategia', 34, WHITE, 'SemiBold'), 290, 70 + lift, alpha=a, ax=0)
        items = [(T(192), 'Vendedores'), (T(194), 'Coaches'), (T(196), 'Influencers'), (T(201), 'Traders')]
        for j, (tt_, lbl) in enumerate(items):
            k = pop(t, tt_ - 0.2)
            if k > 0.001: ochip(ctx, 290 + (j % 2) * 230 + 10 * (1 - k), 140 + (j // 2) * 64, lbl, a * c01(k * 1.5), size=24, filled=False)
        k2 = pop(t, T(211) - 0.15)                                          # "los metieron a todos a su plataforma"
        if k2 > 0.001:
            ctx.move_to(420, 240); ctx.line_to(420, 240 + 46 * eo(c01(k2))); rgba(ctx, WO, a); ctx.set_line_width(4); ctx.stroke()
            put(ctx, GT('Todos dentro de Whop', 28, WHITE, 'Medium'), 290, 315, alpha=a * c01(k2 * 1.5), ax=0)
        k3 = pop(t, T(220) - 0.15)
        if k3 > 0.001: ochip(ctx, 290, 366 + 8 * (1 - k3), 'Casi socios', a * c01(k3 * 1.5), size=26)
    elif name == 'engine':                                                  # growth engine with the same influencers
        put(ctx, GT('Motor de crecimiento', 34, WHITE, 'SemiBold'), 40, 66 + lift, alpha=a, ax=0)
        x0, x1, y0, y1 = 60, w - 60, 120, h - 50
        ctx.rectangle(x0, y1, x1 - x0, 2); rgba(ctx, LINE, a); ctx.fill()
        k = eio(prog(t, st0 + 0.3, T(241) - st0)); n = 60
        pts = [(x0 + (x1 - x0) * i / n, y1 - (y1 - y0) * ((i / n) ** 2.6)) for i in range(int(n * k) + 1)]
        if len(pts) > 1:
            for wd, al in ((14, 0.12), (7, 0.25), (4, 1.0)):
                ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; rgba(ctx, WO, a * al); ctx.set_line_width(wd); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        for j in range(5):                                                   # influencers feeding the curve
            kk = pop(t, T(231) - 0.2 + 0.2 * j)
            if kk <= 0.001: continue
            u = 0.3 + 0.14 * j; px = x0 + (x1 - x0) * u; py = y1 - (y1 - y0) * (u ** 2.6)
            if u <= k + 0.01:
                ctx.arc(px, py, 12 * kk, 0, 2 * math.pi); rgba(ctx, WHITE, a); ctx.fill()
        if pop(t, T(231) - 0.2) > 0.001: put(ctx, GT('Influencers', 22, MUTE), x0 + (x1 - x0) * 0.3, y1 + 26, alpha=a)
        ke = pop(t, T(238) - 0.15)
        if ke > 0.001: ochip(ctx, w - 360, 110 + 8 * (1 - ke), 'Explotó la plataforma', a * c01(ke * 1.5), size=24)
    elif name == 'jake':                                                    # "hace un año metieron a Jake Paul como inversionista"
        put(ctx, GT('Hace un año', 28, MUTE), w / 2, 110 + lift, alpha=a)
        k = pop(t, T(247) - 0.15)
        put(ctx, GT('Jake Paul', 110, WHITE, 'SemiBold'), w / 2, 220 + 14 * (1 - k), alpha=a * c01(k * 1.5))
        k2 = pop(t, T(250) - 0.15)
        if k2 > 0.001:
            tt = GT('Inversionista', 30, WHITE, 'SemiBold'); pw = tt[4] + 50
            rr(ctx, w / 2 - pw / 2, 300, pw, 56, 28); rgba(ctx, WO, a * c01(k2 * 1.5)); ctx.fill(); put(ctx, tt, w / 2, 329, alpha=a * c01(k2 * 1.5))
    elif name == 'influ':                                                   # how they grow: partnerships with influencers
        paint_seq(ctx, t, [(st0, 'creators', 1.0), (T(265) - 0.2, 'speed', 1.0), (T(270) - 0.2, 'celebrate', 1.0), (T(278) - 0.2, 'social', 1.0)], 0, 0, w, h, a)
        strip(ctx, t, w, h, a, 'Así crecen: con influencers', [(T(268) - 0.15, 'Partnerships'), (T(278) - 0.15, 'Más conexión'), (T(287) - 0.15, 'Llegan a más personas')], T(261) - 0.2, 1e9, arrows=True)
    elif name == 'marketing':                                                # their billboards: "súper dopamínico"
        seq = [('w06.png', st0), ('w07.png', T(300) - 0.2), ('w05.png', T(303) - 0.2)]
        for j, (nm, t0) in enumerate(seq):
            t1 = seq[j + 1][1] if j + 1 < len(seq) else 1e9
            fa = (c01((t - t0) / 0.35) if j else 1.0) * (1 - c01((t - t1) / 0.35))
            if fa > 0.002 and t >= t0 - 0.01: photo(ctx, nm, 0, 0, w, h, a * fa, t - t0)
        strip(ctx, t, w, h, a, 'Su marketing', [(T(299) - 0.15, 'Súper dopamínico'), (T(302) - 0.15, 'Interesante'), (T(304) - 0.15, 'Chévere')], st0, 1e9)
    elif name == 'market':                                                  # new features daily, the new marketplace, not Shopify: Whop
        paint_seq(ctx, t, [(st0, 'easy_n', 1.0), (T(316) - 0.2, 'humans', 1.0), (T(327) - 0.2, 'logo_n', 0.5)], 0, 0, w, h, a)   # 'todo el mundo va a estar construyendo'
        strip(ctx, t, w, h, a, 'Nuevos features todos los días', [], st0, T(316) - 0.2)
        strip(ctx, t, w, h, a, 'El nuevo marketplace', [(T(320) - 0.15, 'Todo el mundo va a construir aquí')], T(316) - 0.2, T(327) - 0.2)
        ks = pop(t, T(332) - 0.15)
        if ks > 0.001:
            g = cairo.LinearGradient(0, h - 170, 0, h); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.85 * a); ctx.rectangle(0, h - 170, w, 170); ctx.set_source(g); ctx.fill()
            tt = GT('Shopify', 40, C(170, 170, 170), 'SemiBold'); put(ctx, tt, 40, h - 56, alpha=a * c01(ks * 1.5), ax=0)
            kx = eo(prog(t, T(332) + 0.1, 0.35)); ctx.rectangle(34, h - 58, (tt[4] + 12) * kx, 4); rgba(ctx, BAD, a); ctx.fill()
            kw = pop(t, T(336) - 0.15)
            if kw > 0.001: ochip(ctx, 80 + tt[4], h - 56, 'Whop', a * c01(kw * 1.5), size=30)
    elif name == 'pay':
        paint_seq(ctx, t, [(st0, 'pay1', 1.0), (T(341) - 0.2, 'pay2_n', 1.0)], 0, 0, w, h, a)
        strip(ctx, t, w, h, a, 'Todo en Whop', [(T(338) - 0.15, 'Pagos'), (T(342) - 0.15, 'Todo integrado'), (T(346) - 0.15, 'Una maravilla')], st0, 1e9)
    elif name == 'end':
        paint(ctx, os.path.join(REF, 'w02.png'), None, 200, 30 + lift, w - 400, 230, a, anchor_top=False)
        for j, (tt_, txt) in enumerate(((T(351) - 0.15, 'Yo la seguiría sí o sí'), (T(361) - 0.15, 'Y si pudiera, invertiría'))):
            k = pop(t, tt_)
            if k > 0.001:
                tt = GT(txt, 30, WHITE, 'SemiBold'); pw = tt[4] + 50; y = 300 + j * 0
                x = w / 2 - pw / 2 + (-260 if j == 0 else 260) * (1 if pop(t, T(361) - 0.15) > 0.001 else 0) if False else (w / 2 - pw / 2)
                if j == 0 and pop(t, T(361) - 0.15) > 0.001: continue
                rr(ctx, x, 300 + 12 * (1 - k), pw, 60, 30); rgba(ctx, WO, a * c01(k * 1.5)); ctx.fill(); put(ctx, tt, w / 2, 331 + 12 * (1 - k), alpha=a * c01(k * 1.5))

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
TITLE = [['De', 'revender'], ['sneakers', 'a'], ['US$200M']]
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.4 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, GT(LABEL[:n], 36, WHITE, 'Regular', shadow=6), 70, 1040, alpha=fade, ax=0)
    k = 0; t0 = 0.15 + 0.03 * len(LABEL)
    for li, line in enumerate(TITLE):
        x = 70; y = 1150 + li * 130
        for wd in line:
            tt = GT(wd, 124, WO if wd == 'US$200M' else WHITE, 'SemiBold', shadow=10, shadow_a=200)
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
    global CHUNK_WORDS
    CHUNK_WORDS = ch
    out = []
    for j, c in enumerate(ch):
        st = c[0][0] - 0.03; en = ch[j + 1][0][0] - 0.03 if j + 1 < len(ch) else c[-1][1] + 0.5
        out.append((st, min(en, c[-1][1] + 0.6), ' '.join(x[2] for x in c)))
    return out
CHUNKS = build_chunks()
def subtitles(ctx, t):
    """white subtitles; the word being said lights up in Whop orange"""
    if t < TITLE_END: return
    for ci, (st, en, line) in enumerate(CHUNKS):
        if st <= t < en: break
    else: return
    e = c01((t - st) / 0.12)
    words = CHUNK_WORDS[ci]
    parts = [GT(wd, 56, WHITE, 'SemiBold') for (_, _, wd) in words]
    sp = 16; tw = sum(p[4] for p in parts) + sp * (len(parts) - 1); sc = min(1.0, 920 / tw)
    pw_, ph_ = (tw + 64) * sc, 92 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); ctx.set_source_rgba(0.08, 0.07, 0.07, 0.85 * e); ctx.fill()
    x = W / 2 - tw * sc / 2
    for (ws, we_, wd), p in zip(words, parts):
        on = ws - 0.03 <= t < we_ + 0.05
        put(ctx, GT(wd, 56, WO if on else WHITE, 'SemiBold'), x, y + 1, scale=sc, alpha=e, ax=0); x += (p[4] + sp) * sc

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.rectangle(0, H - 8, W * c01(t / DUR), 8); rgba(ctx, WO); ctx.fill()

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
