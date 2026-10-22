"""IMG_9042 · "La red social que te da una ventaja 10x" (Twitter / X). 1.05x, voice only. Built on the Roadster model (video 19)
with the user's note: visuals stay longer, slower entrances/exits, one card per idea (each holds >= 3 s).
Key visual = the David Haz "Texture Lab" post: an off-white frame holding either a halftone-dotted texture with huge thin type
(like his "14°") or a faithful dark X interface (trends, feed, who-to-follow, sidebar logo). X blue progress bar.
Subtitles on a dark pill (bright sky / cream jacket behind). HDR (HLG) only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = '/Users/acorrales/Desktop/Edición de videos/scripts'
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit20 as E; os.chdir(_cwd)

SPEED = 1.05
REF = os.path.join(HERE, 'ref')
GF = os.path.expanduser('~/Library/Fonts/')
G = {k: GF + 'Geist-%s.otf' % k for k in ('Thin', 'ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold', 'Bold')}
SF = '/System/Library/Fonts/SFNS.ttf'
def C(r, g, b, a=1.0): return (r / 255, g / 255, b / 255, a)
CREAM, PAPER, INK, WHITE = C(238, 235, 229), C(246, 244, 240), C(17, 17, 17), C(255, 255, 255)
XBLK, XGREY, XLINE, XBLUE = C(0, 0, 0), C(113, 118, 123), C(47, 51, 54), C(29, 155, 240)

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
    """Geist: the key visual's thin, quiet type"""
    key = ('G', txt, size, col, wt, track, shadow, shadow_a)
    return _tc[key] if key in _tc else _mk(key, ImageFont.truetype(G[wt], size), txt, col, track, shadow, shadow_a)
def XT(txt, size, col=WHITE, wght=400):
    """SF Pro ~ X's Chirp for the X interface"""
    key = ('X', txt, size, col, wght)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(SF, size); f.set_variation_by_axes([100, min(96, max(17, size)), 400, wght])
    return _mk(key, f, txt, col, 0.0, 0, 0)

# ---------------- springs (slower than the Roadster: the user asked for more time) ----------------
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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v20.json')))['segments'] for w in s['words']]
FIX = {18: '', 63: 'X', 64: "pa'", 129: 'dejo'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.45
TITLE_END = T(17) - 0.1                                                   # title rides the whole hook question

# ---------------- helpers ----------------
def rr(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
def soft_shadow(ctx, x, y, w, h, r, a):
    for dy, grow, al in [(26, 26, 0.06), (12, 10, 0.08), (3, 1, 0.10)]:
        rr(ctx, x - grow, y - grow + dy, w + 2 * grow, h + 2 * grow, r + grow); ctx.set_source_rgba(0, 0, 0, al * a); ctx.fill()
_img = {}
def img(name, crop=None):
    key = (name, crop)
    if key not in _img:
        im = Image.open(os.path.join(REF, name)).convert('RGBA')
        if crop: im = im.crop(crop)
        _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint(ctx, name, crop, x, y, w, h, a, ox=0.0, oy=0.0, s=None):
    """draw an image into (x,y,w,h); cover-fit unless a scale s is given; ox/oy pan in image pixels"""
    if a <= 0.002: return
    im, (surf, _b) = img(name, crop)
    s = s or max(w / im.width, h / im.height)
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + w / 2, y + h / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, -im.width / 2 - ox, -im.height / 2 - oy); ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(a); ctx.restore()

def halftone(name, w, h, seed, stops, spacing=9):
    """'Texture Lab' look: a soft colour field rendered as a dot screen (dot size follows brightness)"""
    p = os.path.join(REF, name)
    if os.path.exists(p): return
    rng = np.random.RandomState(seed)
    def octave(n): return np.asarray(Image.fromarray((rng.rand(n, int(n * w / h) + 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    f = np.clip(0.62 * octave(3) + 0.28 * octave(7) + 0.10 * octave(16), 0, 1)
    yy = np.linspace(0, 1, h)[:, None]; f = np.clip(0.75 * f + 0.25 * (1 - yy), 0, 1)              # light from the top, like a sky
    st = np.array([s[0] for s in stops]); cols = np.array([s[1] for s in stops], np.float32)
    col = np.stack([np.interp(f, st, cols[:, c]) for c in range(3)], -1)
    S = 3; big = Image.new('L', (w * S, h * S), 0); d = ImageDraw.Draw(big)
    for cy in range(spacing // 2, h, spacing):
        for cx in range(spacing // 2 + (spacing // 2 if (cy // spacing) % 2 else 0), w, spacing):
            lum = col[min(h - 1, cy), min(w - 1, cx)].mean() / 255
            r = spacing * 0.5 * (0.35 + 0.75 * lum) * S
            d.ellipse((cx * S - r, cy * S - r, cx * S + r, cy * S + r), fill=255)
    m = np.asarray(big.resize((w, h), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    out = col * (0.30 + 0.70 * m)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(p)
halftone('tex_sage.png', 1300, 700, 3, [(0, (22, 44, 44)), (0.45, (74, 112, 104)), (0.75, (150, 172, 150)), (1, (226, 222, 204))])
halftone('tex_blue.png', 1300, 700, 11, [(0, (6, 16, 30)), (0.5, (18, 74, 120)), (0.8, (60, 150, 210)), (1, (210, 230, 240))])
halftone('tex_av1.png', 200, 200, 21, [(0, (40, 30, 60)), (1, (220, 160, 120))], 7)
halftone('tex_av2.png', 200, 200, 22, [(0, (20, 50, 40)), (1, (170, 220, 150))], 7)
halftone('tex_av3.png', 200, 200, 23, [(0, (20, 30, 60)), (1, (140, 190, 240))], 7)

def xlogo(ctx, cx, cy, size, a, fg=WHITE, bg=XBLK):
    """vector X mark: hollow heavy backslash + thin slash broken at it"""
    if a <= 0.002: return
    s = size
    ctx.save(); ctx.translate(cx - s / 2, cy - s / 2); ctx.scale(s, s)
    ctx.move_to(0.86, 0.0); ctx.line_to(0.95, 0.0); ctx.line_to(0.14, 1.0); ctx.line_to(0.05, 1.0); ctx.close_path(); rgba(ctx, fg, a); ctx.fill()
    outer = [(0.0, 0.0), (0.31, 0.0), (1.0, 1.0), (0.69, 1.0)]
    ctx.move_to(-0.04, -0.03)
    for p in [(0.33, -0.03), (1.05, 1.03), (0.67, 1.03)]: ctx.line_to(*p)
    ctx.close_path(); rgba(ctx, bg, a); ctx.fill()
    ctx.move_to(*outer[0]); [ctx.line_to(*p) for p in outer[1:]]; ctx.close_path()
    inner = [(0.10, 0.07), (0.24, 0.07), (0.90, 0.93), (0.76, 0.93)]
    ctx.move_to(*inner[0]); [ctx.line_to(*p) for p in inner[1:]]; ctx.close_path()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); rgba(ctx, fg, a); ctx.fill(); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.restore()
def check(ctx, x, y, s, col, a, k=1.0):
    if a <= 0.002 or k <= 0: return
    p0, p1, p2 = (x - 0.5 * s, y), (x - 0.15 * s, y + 0.35 * s), (x + 0.55 * s, y - 0.4 * s)
    L1, L2 = math.dist(p0, p1), math.dist(p1, p2); d = (L1 + L2) * k
    ctx.move_to(*p0)
    if d <= L1: ctx.line_to(p0[0] + (p1[0] - p0[0]) * d / L1, p0[1] + (p1[1] - p0[1]) * d / L1)
    else: ctx.line_to(*p1); u = (d - L1) / L2; ctx.line_to(p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u)
    rgba(ctx, col, a); ctx.set_line_width(max(3, s * 0.16)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
def cursor(ctx, x, y, a, press=0.0):
    if a <= 0: return
    s = 1.0 - 0.15 * press
    ctx.save(); ctx.translate(x, y); ctx.scale(1.3 * s, 1.3 * s)
    for k in (0, 1):
        ctx.move_to(0, 0); ctx.line_to(0, 30); ctx.line_to(8, 23); ctx.line_to(13, 34); ctx.line_to(18, 32); ctx.line_to(13, 21); ctx.line_to(23, 21); ctx.close_path()
        if k == 0:
            ctx.save(); ctx.translate(1.5, 2.5); ctx.set_source_rgba(0, 0, 0, 0.25 * a); ctx.fill(); ctx.restore()
        else:
            ctx.set_source_rgba(0, 0, 0, a); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
def inner(ctx, w, h, col, a, P=16, R=22):
    rr(ctx, P, P, w - 2 * P, h - 2 * P, R); rgba(ctx, col, a); ctx.fill()

# ---------------- the morphing card (band above my eyes) ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(6) - 0.10, 'context', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(37) - 0.10, 'trends', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(57) - 0.10, 'x10', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(82) - 0.10, 'feed', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(98) - 0.10, 'world', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(111) - 0.10, 'ahead', CX, 260, 1000, 420, 34, CREAM[:3]),
    (T(127) - 0.10, 'list', CX, 260, 1000, 420, 34, CREAM[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000                                 # cap at y~120-480, eyes from y~600
SHAPE_ON = STATES[0][0]
def shape_geo(t):
    keys = []
    for k in range(8):
        ev = [(s[0], (s[2], s[3], s[4], s[5], s[6], *s[7])[k]) for s in STATES[1:]]
        v0 = (STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7])[k]
        keys.append(track(t, ev, v0, w=9.0, zeta=0.9))
    return keys
def state_alpha(t, i):
    a = STATES[i][0]; b = STATES[i + 1][0] if i + 1 < len(STATES) else 1e9
    return c01((t - a - 0.10) / 0.35) * (1 - c01((t - b) / 0.30))      # slower crossfade than v19

TRENDS = [(T(39) - 0.15, 'Tecnología · Tendencia', 'Lo que hacen las mejores empresas'), (T(48) - 0.15, 'Negocios · Tendencia', 'Growth y marketing'),
          (T(52) - 0.15, 'Tendencia en Colombia', 'Ventas'), (T(56) - 0.15, 'Para ti · Tendencia', 'Playbooks')]
LIST = [('tex_av1.png', 'Fundadores', 'Construyen en público'), ('tex_av2.png', 'Growth y marketing', 'Experimentos que sí funcionan'),
        ('tex_av3.png', 'Ventas', 'Playbooks probados')]
_rng = np.random.RandomState(5)
PARTS = [(_rng.uniform(0, 2 * math.pi), _rng.uniform(0.7, 1.25), _rng.uniform(0, 0.9), _rng.choice([0, 1, 2])) for _ in range(150)]

def draw_state(ctx, t, name, w, h, a, lift, st0):
    P = 16; iw, ih = w - 2 * P, h - 2 * P
    if name == 'context':
        ctx.save(); rr(ctx, P, P, iw, ih, 22); ctx.clip()
        paint(ctx, 'tex_sage.png', None, P, P, iw, ih, a, ox=40 * math.sin((t - st0) * 0.25), oy=10)
        ctx.restore()
        put(ctx, GT('En contexto', 30, WHITE, 'Regular'), 52, 64, alpha=a, ax=0)
        put(ctx, GT('Ahora mismo, en el mundo', 22, C(255, 255, 255, 0.8), 'Light'), 52, 98, alpha=a, ax=0)
        put(ctx, GT('Contexto', 150, WHITE, 'ExtraLight'), 46, 220 + lift, alpha=a, ax=0)
        k1 = pop(t, T(22) - 0.15); k2 = pop(t, T(31) - 0.15)                     # "noticias" (struck) · "tecnología" (chosen)
        strike = eo(prog(t, T(27) - 0.1, 0.5))
        for j, (lbl, k) in enumerate((('Noticias', k1), ('Tecnología', k2))):
            if k <= 0.001: continue
            tt = GT(lbl, 32, WHITE if j == 1 else C(255, 255, 255, 0.75), 'Medium'); pw = tt[4] + (96 if j == 1 else 60)
            x = 52 + j * 290; y = 330 + 16 * (1 - k); aa = a * c01(k * 1.4) * ((1 - 0.45 * strike) if j == 0 else 1)
            rr(ctx, x, y - 30, pw, 60, 30)
            if j == 1: rgba(ctx, XBLUE, aa); ctx.fill()
            else: ctx.set_source_rgba(1, 1, 1, 0.16 * aa); ctx.fill()
            put(ctx, tt, x + 30, y + 1, alpha=aa, ax=0)
            if j == 0 and strike > 0: ctx.rectangle(x + 22, y - 1, (tt[4] + 16) * strike, 3); ctx.set_source_rgba(1, 1, 1, aa); ctx.fill()
            if j == 1: check(ctx, x + pw - 36, y, 24, WHITE, aa, eo(prog(t, T(31) + 0.1, 0.4)))
        put(ctx, GT('10:00', 18, C(255, 255, 255, 0.7), 'Regular'), w - 250, 340, alpha=a)                 # quiet data row, like the key visual
        put(ctx, GT('12:00', 18, C(255, 255, 255, 0.7), 'Regular'), w - 160, 340, alpha=a)
        put(ctx, GT('14:00', 18, C(255, 255, 255, 0.7), 'Regular'), w - 70, 340, alpha=a)
        for j, v in enumerate(('IA', 'Startups', 'Growth')):
            put(ctx, GT(v, 20, WHITE, 'Medium'), w - 250 + 90 * j, 366, alpha=a)
    elif name == 'trends':
        inner(ctx, w, h, XBLK, a)
        put(ctx, XT('Qué está pasando', 42, WHITE, 800), 52, 60 + lift, alpha=a, ax=0)
        for j, (t0, cat, item) in enumerate(TRENDS):
            k = pop(t, t0); y = 92 + j * 74
            if k <= 0.001: continue
            aa = a * c01(k * 1.4); dx = 24 * (1 - k)
            put(ctx, XT(cat, 21, XGREY, 400), 52 + dx, y + 14, alpha=aa, ax=0)
            put(ctx, XT(item, 34, WHITE, 700), 52 + dx, y + 48, alpha=aa, ax=0)
            for d in range(3): ctx.arc(w - 80 + d * 10, y + 16, 2.6, 0, 2 * math.pi); rgba(ctx, XGREY, aa); ctx.fill()
            hl = c01((t - t0 - 0.2) / 0.3) * (1 - c01((t - t0 - 1.6) / 0.6))       # the row just named lights up, then settles
            if hl > 0: rr(ctx, 32, y - 6, w - 64, 70, 12); ctx.set_source_rgba(1, 1, 1, 0.06 * hl * aa); ctx.fill()
    elif name == 'x10':
        split = spring(t - (T(67) - 0.15), w=8.0, zeta=0.92)                       # "Estar en Twitter te da…": X panel slides left
        lw = (w - 2 * P) * (1 - split) + 300 * split
        rr(ctx, P, P, lw, h - 2 * P, 22); rgba(ctx, XBLK, a); ctx.fill()
        cx = P + lw / 2
        kx = pop(t, T(63) - 0.12)                                                  # "o X": the word becomes the mark
        tw_ = XT('Twitter', 120, WHITE, 800)
        put(ctx, tw_, cx, h / 2 - 6 - 30 * kx, scale=1 - 0.25 * kx, alpha=a * (1 - c01(kx * 1.6)) * c01((t - st0 - 0.1) / 0.4))
        xlogo(ctx, cx, h / 2 - 12 + 30 * (1 - kx), 150 * (0.7 + 0.3 * kx) * (1 - 0.25 * split), a * c01(kx * 1.5))
        put(ctx, GT("pa' los amigos", 26, XGREY, 'Regular'), cx, h / 2 + 100, alpha=a * c01(kx * 1.5) * eo(prog(t, T(64), 0.4)) * (1 - split))
        if split > 0.01:
            rx = P + lw + 16; rwid = w - P - rx
            ctx.save(); rr(ctx, rx, P, rwid, h - 2 * P, 22); ctx.clip()
            paint(ctx, 'tex_blue.png', None, rx, P, rwid, h - 2 * P, a * c01(split * 1.3), ox=30 * math.sin((t - st0) * 0.22))
            ctx.restore()
            v = 1 + 9 * eio(prog(t, T(76) - 0.45, 0.9))                             # counts 1x -> 10x on "10x"
            put(ctx, GT('%dx' % int(round(v)), 210, WHITE, 'Thin'), rx + 36, 190, alpha=a * c01((split - 0.3) * 2), ax=0)
            put(ctx, GT('Ventaja', 26, WHITE, 'Regular'), rx + 40, 66, alpha=a * c01((split - 0.4) * 2), ax=0)
            put(ctx, GT('sobre todo el mundo', 20, C(255, 255, 255, 0.75), 'Light'), rx + 40, 96, alpha=a * c01((split - 0.5) * 2), ax=0)
            ka = pop(t, T(79) - 0.1)                                                # "a todo el mundo": small comparison row
            for j, (lbl, val) in enumerate((('Tú, en X', '10x'), ('El resto', '1x'))):
                put(ctx, GT(lbl, 18, C(255, 255, 255, 0.7), 'Regular'), rx + rwid - 230 + 120 * j, 330, alpha=a * c01(ka * 1.5))
                put(ctx, GT(val, 24, WHITE, 'Medium'), rx + rwid - 230 + 120 * j, 358, alpha=a * c01(ka * 1.5))
    elif name == 'feed':
        inner(ctx, w, h, XBLK, a)
        ctx.save(); rr(ctx, P, P, w - 2 * P, h - 2 * P, 22); ctx.clip()
        sc = (w - 2 * P) / 1155
        scroll = 700 * eio(prog(t, st0 + 0.5, T(98) - st0 - 0.4))               # the feed scrolls slowly while I talk
        paint(ctx, 'i38.png', (25, 330, 1180, 1797), P, P + 70, w - 2 * P, h - 2 * P - 70, a, oy=scroll - 120, s=sc)
        ctx.rectangle(P, P, w - 2 * P, 70); rgba(ctx, C(0, 0, 0, 0.92), a); ctx.fill()
        put(ctx, XT('Para ti', 26, WHITE, 700), 220, P + 36, alpha=a); put(ctx, XT('Siguiendo', 26, XGREY, 500), 560, P + 36, alpha=a)
        rr(ctx, 178, P + 62, 84, 5, 2.5); rgba(ctx, XBLUE, a); ctx.fill()
        ctx.rectangle(P, P + 69, w - 2 * P, 1); rgba(ctx, XLINE, a); ctx.fill()
        ctx.restore()
        k = pop(t, T(96) - 0.15)                                                    # "publicando todo": new posts pill
        if k > 0.001:
            tt = XT('↑  Nuevos posts', 24, WHITE, 700); pw = tt[4] + 50; y = P + 110 - 20 * (1 - k)
            rr(ctx, w / 2 - pw / 2, y - 24, pw, 48, 24); rgba(ctx, XBLUE, a * c01(k * 1.5)); ctx.fill()
            put(ctx, tt, w / 2, y + 1, alpha=a * c01(k * 1.5))
    elif name == 'world':
        inner(ctx, w, h, XBLK, a)
        ctx.save(); rr(ctx, P, P, w - 2 * P, h - 2 * P, 22); ctx.clip()
        paint(ctx, 'tex_blue.png', None, P, P, w - 2 * P, h - 2 * P, a * 0.28)
        cx, cy = w / 2, h / 2
        for ang, rad, d0, kind in PARTS:                                           # everything flows into X
            u = eio(c01((t - (st0 + 0.2 + d0 * 1.2)) / 1.6))
            r0 = rad * 560
            x = cx + math.cos(ang) * r0 * (1 - u); y = cy + math.sin(ang) * r0 * 0.55 * (1 - u)
            al = a * (0.25 + 0.75 * c01((t - st0 - 0.1) / 0.5)) * (1 - c01((u - 0.85) / 0.15))
            if al <= 0.01: continue
            col = (XBLUE, WHITE, C(150, 172, 150))[kind]
            ctx.arc(x, y, 4 if kind else 5, 0, 2 * math.pi); rgba(ctx, col, al); ctx.fill()
        ctx.restore()
        pul = math.sin(math.pi * c01((t - (T(109) - 0.1)) / 0.5))                  # "se concentra ahí"
        ctx.arc(w / 2, h / 2, 86 + 14 * pul, 0, 2 * math.pi); rgba(ctx, WHITE, a); ctx.fill()
        xlogo(ctx, w / 2, h / 2, 82, a, fg=XBLK, bg=WHITE)
        put(ctx, GT('Todo pasa aquí', 22, C(255, 255, 255, 0.85), 'Regular'), 52, 64, alpha=a, ax=0)
    elif name == 'ahead':
        inner(ctx, w, h, PAPER, a)
        x0, x1, y0, y1 = 70, w - 90, 70, h - 80
        for k in range(5):
            yy = y0 + (y1 - y0) * k / 4; ctx.rectangle(x0, yy, x1 - x0, 1); rgba(ctx, INK, a * 0.08); ctx.fill()
        put(ctx, GT('Por delante del mundo', 24, INK, 'Regular'), x0, 46, alpha=a, ax=0)
        put(ctx, GT('tiempo', 18, C(17, 17, 17, 0.5), 'Regular'), x1, y1 + 30, alpha=a, ax=1)
        k = eio(prog(t, st0 + 0.3, 2.6)); n = 60
        def line(f, col, wd):
            pts = [(x0 + (x1 - x0) * i / n, y1 - (y1 - y0) * f(i / n)) for i in range(int(n * k) + 1)]
            if len(pts) < 2: return pts
            ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]
            rgba(ctx, col, a); ctx.set_line_width(wd); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke(); return pts
        lw = line(lambda u: 0.22 * u, C(17, 17, 17, 0.45), 3)
        lx = line(lambda u: 0.08 * u + 0.86 * u ** 1.8, XBLUE, 5)
        if lx and len(lx) > 1:
            ex, ey = lx[-1]; ctx.arc(ex, ey, 9, 0, 2 * math.pi); rgba(ctx, XBLUE, a); ctx.fill()
            put(ctx, GT('Tú, en X', 22, XBLUE, 'Medium'), ex - 16, ey - 28, alpha=a * c01((k - 0.6) * 3), ax=1)
        if lw and len(lw) > 1:
            put(ctx, GT('El mundo', 22, C(17, 17, 17, 0.6), 'Regular'), lw[-1][0] - 10, lw[-1][1] + 26, alpha=a * c01((k - 0.6) * 3), ax=1)
        kb = pop(t, T(122) - 0.15)                                                 # "tiene que estar en Twitter": the X badge lands on the lead
        if kb > 0.001 and lx:
            ex, ey = lx[-1]; bx, by = min(ex + 50, w - 60), max(ey, 70)
            ctx.arc(bx, by, 30 * (0.6 + 0.4 * kb), 0, 2 * math.pi); rgba(ctx, XBLK, a * c01(kb * 1.5)); ctx.fill()
            xlogo(ctx, bx, by, 30 * (0.6 + 0.4 * kb), a * c01(kb * 1.5))
    elif name == 'list':
        inner(ctx, w, h, XBLK, a)
        put(ctx, XT('A quién seguir', 36, WHITE, 800), 52, 70 + lift, alpha=a, ax=0)
        ka = pop(t, T(142) - 0.15)                                                 # "solo tiran alfa"
        if ka > 0.001:
            tt = XT('solo alfa', 22, XBLK, 700); pw = tt[4] + 40; x = 52 + XT('A quién seguir', 36, WHITE, 800)[4] + 24
            rr(ctx, x, 70 - 20, pw, 40, 20); rgba(ctx, WHITE, a * c01(ka * 1.5)); ctx.fill(); put(ctx, tt, x + 20, 71, alpha=a * c01(ka * 1.5), ax=0)
        clicks = [T(138) - 0.1 + 0.45 * j for j in range(3)]
        for j, (av, nm, sub) in enumerate(LIST):
            k = pop(t, st0 + 0.25 + 0.25 * j); y = 106 + j * 86
            if k <= 0.001: continue
            aa = a * c01(k * 1.4); dy = 18 * (1 - k)
            ctx.save(); ctx.arc(84, y + 36 + dy, 30, 0, 2 * math.pi); ctx.clip(); paint(ctx, av, None, 54, y + 6 + dy, 60, 60, aa); ctx.restore()
            put(ctx, XT(nm, 32, WHITE, 700), 132, y + 20 + dy, alpha=aa, ax=0)
            put(ctx, XT(sub, 24, XGREY, 400), 132, y + 54 + dy, alpha=aa, ax=0)
            on = c01((t - clicks[j]) / 0.12)
            lbl = XT('Siguiendo' if on else 'Seguir', 24, WHITE if on else XBLK, 700); bw = 170
            rr(ctx, w - 70 - bw, y + 14 + dy, bw, 46, 23)
            if on: rgba(ctx, XBLK, aa); ctx.fill_preserve(); rgba(ctx, XLINE, aa); ctx.set_line_width(2); ctx.stroke()
            else: rgba(ctx, C(239, 243, 244), aa); ctx.fill()
            put(ctx, lbl, w - 70 - bw / 2, y + 37 + dy, alpha=aa)
        if t > clicks[0] - 0.6:                                                     # one cursor clicks the three
            tg = [(c - 0.35, (w - 155, 106 + j * 86 + 44)) for j, c in enumerate(clicks)]
            cx_ = track(t, [(a_, p[0]) for a_, p in tg], w - 40, w=8.0, zeta=0.95); cy_ = track(t, [(a_, p[1]) for a_, p in tg], h - 20, w=8.0, zeta=0.95)
            press = max(math.sin(math.pi * c01((t - c + 0.08) / 0.2)) for c in clicks)
            cursor(ctx, cx_, cy_, a * c01((t - clicks[0] + 0.6) / 0.3), press)
        put(ctx, XT('La lista completa, en la descripción', 25, XBLUE, 600), 52, h - 44, alpha=a * eo(prog(t, T(139), 0.5)), ax=0)

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = c01(spring(t - SHAPE_ON, w=8.0, zeta=0.92))
    if appear <= 0.01: return
    sc = 0.9 + 0.1 * appear
    f = min(1.0, BAND_H / h, BAND_W / w); cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 36 * (1 - appear)); ctx.scale(sc * f, sc * f); ctx.translate(-w / 2, -h / 2)
    soft_shadow(ctx, 0, 0, w, h, r, appear)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 16 * (1 - eo(c01((t - st[0] - 0.1) / 0.6)))
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore()
    rr(ctx, 0.5, 0.5, w - 1, h - 1, r); ctx.set_source_rgba(0, 0, 0, 0.08 * appear); ctx.set_line_width(1.5); ctx.stroke()
    ctx.restore()

# ---------------- title (over the hook) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['La', 'red', 'social'], ['que', 'te', 'da', 'una'], ['ventaja', '10x']]
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
        put(ctx, GT(txt, 36, WHITE, 'Regular', shadow=6), 70, 1060, alpha=fade, ax=0)
    t0 = 0.15 + 0.03 * len(LABEL); k = 0
    for li, line in enumerate(TITLE):
        x = 70; y = 1170 + li * 124
        for wd in line:
            tt = GT(wd, 118, XBLUE if wd == '10x' else WHITE, 'Medium', shadow=10, shadow_a=200)
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
    tt = GT(line, 56, WHITE, 'Medium'); sc = min(1.0, 920 / tt[4])
    pw_, ph_ = (tt[4] + 64) * sc, 92 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); rgba(ctx, C(15, 15, 15), 0.88 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 1, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.rectangle(0, H - 8, W * c01(t / DUR), 8); rgba(ctx, XBLUE); ctx.fill()

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
