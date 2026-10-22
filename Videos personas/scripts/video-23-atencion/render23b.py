"""IMG_9088 · Darshita Patankar ("DESIGN IS DEAD") and why attention is everything. v2 (20 oct 2026): the user
rejected the pink look ("déjalo normal") and asked for much more of her film: it now plays almost the whole time inside a neutral card. 1.05x, voice only (DeepFilterNet3-cleaned).
Identity taken from her film: plum-black and hot pink, glossy pink 3D script (Pacifico, extruded, rim + gradient face), glowing serif
(New York) for text and subtitles, 4-point glints. Her film's own shots are cropped above its burned-in subtitles and play silent
inside the card. Literal explanations only (no orbit / radar metaphors: rejected 20 oct 2026). HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = '/Users/acorrales/Desktop/Edición de videos/scripts'
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit23 as E; os.chdir(_cwd)

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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v23.json')))['segments'] for w in s['words']]
FIX = {0: 'Vea,', 27: '', 43: 'oe,', 75: 'la IA', 82: '', 89: 'pelada', 131: 'está', 132: 'en', 150: 'mucho', 151: 'ruido',
       173: 'A esa', 174: 'pelada le', 175: 'están', 187: '¿Y', 188: 'por qué', 203: 'mundo?', 210: '', 211: '', 212: 'y se', 213: 'fue',
       226: '¿Que', 228: 'pena?', 229: 'No,'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(17) - 0.1                                                   # title over the hook line, until "Twitter"

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
# ---------------- neutral house look (like videos 20-22): near-black card, Geist, white chips ----------------
FILM = os.path.join(HERE, 'film')
ACC = C(96, 165, 250)
# her film plays (silent) inside the card almost all the time: (output start, segment dir)
SEGS_OUT = [(T(17) - 0.15, 's01b'), (T(43) - 0.15, 's02'), (T(53) - 0.1, 's03'), (T(68) - 0.1, 's04'), (T(88) - 0.1, 's05'),
            (T(98) - 0.1, 's06'), (T(110) - 0.1, 's07'), (T(116) - 0.1, 's08'), (T(141) - 0.1, 's09'), (T(153) - 0.1, 's10'),
            (T(173) - 0.1, 's11'), (T(187) - 0.1, 's12'), (T(218) - 0.1, 's13'), (T(229) - 0.3, 's14')]
_fl = {}
def film_frame(seg, k):
    import glob as _g
    fs = _fl.get(seg)
    if fs is None: fs = _fl[seg] = sorted(_g.glob(os.path.join(FILM, seg, '*.jpg')))
    k = min(len(fs) - 1, max(0, k)); key = ('F', seg, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == 'F' and kk[1] == seg]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_film(ctx, t, x, y, w, h, a):
    for j, (t0, seg) in enumerate(SEGS_OUT):
        t1 = SEGS_OUT[j + 1][0] if j + 1 < len(SEGS_OUT) else 1e9
        fa = (c01((t - t0) / 0.25) if j else 1.0) * (1 - c01((t - t1) / 0.25))
        if fa <= 0.002 or t < t0 - 0.01: continue
        im, (surf, _b) = film_frame(seg, int((t - t0) * 30)); s = max(w / im.width, h / im.height)
        ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip(); ctx.translate(x + (w - im.width * s) / 2, y + (h - im.height * s) / 2); ctx.scale(s, s)
        ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a * fa); ctx.restore()
def wchip(ctx, x, y, txt, a, size=24, dark=False):
    if a <= 0.002: return 0
    tt = GT(txt, size, WHITE if dark else C(15, 15, 18), 'Medium'); w = tt[4] + 36; h = size * 1.8
    rr(ctx, x, y - h / 2, w, h, h / 2); rgba(ctx, C(30, 30, 36) if dark else WHITE, a); ctx.fill(); put(ctx, tt, x + 18, y + 1, alpha=a, ax=0)
    return w
def arrow(ctx, x0, x1, y, a):
    if a <= 0.002: return
    ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.move_to(x1 - 8, y - 8); ctx.line_to(x1, y); ctx.line_to(x1 - 8, y + 8)
    rgba(ctx, WHITE, a); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
STRIP = [  # (start, end, label, [(t, chip)]) explains, literally, what I am saying over her film
    (T(17) - 0.1, T(43) - 0.2, 'Darshita Patankar, diseñadora', [(T(23) - 0.15, 'Se volvió viral en X')]),
    (T(43) - 0.2, T(53) - 0.2, 'Su película para conseguir trabajo', [(T(48) - 0.15, 'Con la mejor empresa del mundo')]),
    (T(53) - 0.2, T(68) - 0.2, '"Design is Dead"', [(T(62) - 0.15, 'Su respuesta: el diseño no está muerto')]),
    (T(68) - 0.2, T(88) - 0.2, 'Lo que todos decían', [(T(75) - 0.15, 'La IA mató el diseño')]),
    (T(88) - 0.2, T(110) - 0.2, 'Un launch video de sí misma', [(T(105) - 0.15, 'Con sus proyectos reales')]),
    (T(110) - 0.2, T(116) - 0.2, 'Mega hit', [(T(114) - 0.15, '4,9 M de vistas en X')]),
    (T(116) - 0.2, T(141) - 0.2, 'No se trata de copiar su video', [(T(133) - 0.15, 'Lo esencial: lograr atención')]),
    (T(141) - 0.2, T(170) - 0.2, 'Si quieres lograr algo', [(T(150) - 0.15, 'Haz ruido'), (T(160) - 0.15, 'Atrae gente'), (T(163) - 0.15, 'Atrae miradas'), (T(165) - 0.1, 'Todo sucede')]),
    (T(170) - 0.2, T(173) - 0.2, 'Lo más importante, ahora mismo', []),
    (T(173) - 0.2, T(187) - 0.2, 'Le llueven propuestas', [(T(183) - 0.15, 'De las mejores empresas')]),
    (T(187) - 0.2, T(218) - 0.2, '¿Por qué no lo estás haciendo tú?', [(T(214) - 0.15, 'Ella lo hizo y se volvió viral')]),
    (T(218) - 0.2, 1e9, '¿Por pena?', [(T(229) - 0.15, 'No se puede.')]),
]
QUOTES = [('q_ankur.png', T(176) - 0.2), ('q_aleks.png', T(181) - 0.2)]

CX = W / 2
STATES = [(T(17) - 0.15, 'film', CX, 260, 1000, 425, 22, (0.06, 0.06, 0.07))]
BAND_TOP, BAND_H, BAND_W = 46, 430, 1000
SHAPE_ON = STATES[0][0]
LIST_BEAT = (1e9, 1e9)
def beat_a(t, b, din=0.35, dout=0.35): return c01((t - b[0]) / din) * (1 - c01((t - b[1]) / dout))
def shape_geo(t): return [STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7]]
def state_alpha(t, i): return c01((t - STATES[0][0] - 0.10) / 0.35)

def draw_state(ctx, t, name, w, h, a, lift, st0):
    paint_film(ctx, t, 0, 0, w, h, a)
    for (t0, t1, label, chips) in STRIP:
        sa = a * c01((t - t0) / 0.35) * (1 - c01((t - t1) / 0.3))
        if sa <= 0.002: continue
        g = cairo.LinearGradient(0, h - 170, 0, h); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.5, 0, 0, 0, 0.72 * sa); g.add_color_stop_rgba(1, 0, 0, 0, 0.85 * sa)
        ctx.rectangle(0, h - 170, w, 170); ctx.set_source(g); ctx.fill()
        put(ctx, GT(label, 32, WHITE, 'SemiBold'), 34, h - 100, alpha=sa, ax=0)
        x = 34; seq = len(chips) > 2
        for j, (tc, txt) in enumerate(chips):                                 # fixed logical order; each chip lands when I say it
            k = pop(t, tc); cw = GT(txt, 24, WHITE, 'Medium')[4] + 36
            if k > 0.001:
                if seq and j: arrow(ctx, x - 28, x - 8, h - 44, sa * c01(k * 1.5))
                wchip(ctx, x + 10 * (1 - k), h - 44, txt, sa * c01(k * 1.5))
            x += cw + (40 if seq else 16)
    for j, (nm, t0) in enumerate(QUOTES):                                     # what people answered her (real posts)
        k = pop(t, t0); out = 1 - c01((t - (T(187) - 0.2)) / 0.3)
        if k <= 0.001 or out <= 0: continue
        aa = a * c01(k * 1.5) * out; x = w - 470 + 30 * (1 - k); y = 24 + j * 150
        soft_shadow(ctx, x, y, 440, 136, 12, aa); paint(ctx, R(nm), None, x, y, 440, 136, aa, r=12)

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
TITLE = [['Atención', 'es'], ['lo', 'único', 'que'], ['necesitas']]
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.4 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, GT(LABEL[:n], 36, WHITE, 'Regular', shadow=6), 70, 1050, alpha=fade, ax=0)
    k = 0; t0 = 0.15 + 0.03 * len(LABEL)
    for li, line in enumerate(TITLE):
        x = 70; y = 1160 + li * 124
        for wd in line:
            tt = GT(wd, 118, ACC if wd == 'Atención' else WHITE, 'SemiBold', shadow=10, shadow_a=200)
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
            Image.fromarray(fx.to8(sdr)).save(os.path.join(HERE, 'prev2', 'p%05.2f.jpg' % t), quality=85)
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
