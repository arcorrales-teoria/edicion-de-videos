"""IMG_9123 + IMG_9124 + IMG_9125 · Casey Neistat. Cut to the bone (147 s -> 64 s). Edited in the format of his Nike film "Make It Count":
black cards and full-screen black beats with his footage (silent, hard cuts), white Helvetica Bold caps quotes top-left with credit
bottom-right, a red strike / red thread as the only accent; his best videos (thumbnails) placed mid-video. HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = '/Users/acorrales/Desktop/Edición de videos/scripts'
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit28 as E; os.chdir(_cwd)

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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v28.json')))['segments'] for w in s['words']]
FIX = {15: 'usted', 16: '', 41: '', 67: '', 68: 'Pero', 89: 'nunca', 90: 'pierdes', 92: 'hilo,', 93: 'así', 115: 'dejo', 119: 'Hard', 139: 'esto es', 190: 'rígido,', 212: 'se', 222: 'historia,'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(7) - 0.15                                                   # title over the hook question

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
# ---------------- Casey Neistat "Make It Count" look: black, white Helvetica Bold caps, credit bottom-right, silent footage ----------------
HN = '/System/Library/Fonts/HelveticaNeue.ttc'
CLIPS = os.path.join(HERE, 'clips')
RED = C(255, 0, 0)
def HB(txt, size, col=WHITE, idx=1, shadow=0, shadow_a=180, track=0.0):
    key = ('HB', txt, size, col, idx, shadow, shadow_a, track)
    if key in _tc: return _tc[key]
    return _mk(key, ImageFont.truetype(HN, size, index=idx), txt, col, track, shadow, shadow_a)
_cl = {}
def clip_img(name, k):
    import glob as _g
    fs = _cl.get(name)
    if fs is None: fs = _cl[name] = sorted(_g.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, k)); key = ('CL', name, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == 'CL' and kk[1] == name]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_clip(ctx, name, t, t0, x, y, w, h, a, rate=1.0):
    if a <= 0.002: return
    im, (surf, _b) = clip_img(name, int(max(0, t - t0) * 30 * rate)); s = max(w / im.width, h / im.height)
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + (w - im.width * s) / 2, y + (h - im.height * s) / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
def montage(ctx, t, seq, x, y, w, h, a):
    """hard cuts like his edit: seq = [(start, clip)]"""
    cur = None
    for t0, nm in seq:
        if t >= t0: cur = (t0, nm)
    if cur: paint_clip(ctx, cur[1], t, cur[0], x, y, w, h, a)
def quote(ctx, lines, x, y, size, a, credit=None, cx=None, cy=None, k=1.0):
    """his on-screen quotes: stacked caps, tight leading, top-left; credit bottom-right"""
    for i, ln in enumerate(lines):
        put(ctx, HB(ln, size, WHITE, 1, shadow=6, shadow_a=150), x, y + i * size * 0.92 + 14 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
    if credit and cx is not None: put(ctx, HB(credit, int(size * 0.5), WHITE, 1, shadow=4), cx, cy, alpha=a * c01(k * 1.5), ax=1)
def strike(ctx, x, y, wd, a, k):
    if k <= 0 or a <= 0.002: return
    ctx.rectangle(x, y - 3, wd * k, 7); rgba(ctx, RED, a); ctx.fill()

CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill) black cards, small radius, like his title cards
    (T(7) - 0.15, 'courses', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(27) - 0.10, 'casey', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(35) - 0.10, 'simple', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(67) - 0.10, 'thread', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(102) - 0.10, 'videos', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(142) - 0.10, 'friend', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(166) - 0.10, 'where', CX, 240, 1000, 400, 8, (0, 0, 0)),
    (T(189) - 0.35, 'feel', CX, 240, 1000, 400, 8, (0, 0, 0)),
]
BAND_TOP, BAND_H, BAND_W = 40, 400, 1000                                   # hair from y~370, eyes ~800
SHAPE_ON = STATES[0][0]
FS1 = (T(48) - 0.10, T(67) - 0.10)                                        # "toma el concepto… narrativa visual hermosa": his montage, full screen
FS2 = (T(131) - 0.10, T(142) - 0.10)                                      # "un comercial que hizo con Nike, increíble, es un genio"
FS3 = (T(215) - 0.10, 1e9)                                                # ending: "…que uno se la quisiera echar a un amigo"
BEATS = [FS1, FS2, FS3]
LIST_BEAT = (1e9, 1e9)
def beat_a(t, b, din=0.06, dout=0.06): return c01((t - b[0]) / din) * (1 - c01((t - b[1]) / dout))   # hard cuts
def any_beat(t): return max(beat_a(t, b) for b in BEATS)
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
YT = ['yt48.png', 'yt46.png', 'yt47.png', 'yt49.png', 'yt50.png', 'yt51.png', 'yt52.png']

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'courses':                                                   # "no tiene que pagar cursos en la universidad… siga a los mejores"
        k0 = pop(t, st0 + 0.05)
        put(ctx, HB('¿APRENDER STORYTELLING?', 30, WHITE, 1), 50, 36 + 8 * (1 - k0), alpha=a * c01(k0 * 1.5) * (1 - c01((t - (T(11) - 0.3)) / 0.3)), ax=0)
        for j, (txt, t0) in enumerate((('CURSOS DE STORYTELLING', T(11) - 0.15), ('LA UNIVERSIDAD', T(14) - 0.15))):
            k = pop(t, t0); tt = HB(txt, 52, WHITE)
            put(ctx, tt, 50, 90 + j * 76 + 10 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
            strike(ctx, 50, 92 + j * 76, tt[4] + 4, a, eo(prog(t, t0 + 0.4, 0.35)))
        k = pop(t, T(19) - 0.15)
        if k > 0.001:
            for i, ln in enumerate(('SIGUE A LOS QUE MEJOR LO HACEN.',)):
                put(ctx, HB(ln, 46, WHITE), 50, 300 + 12 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
    elif name == 'casey':                                                   # "Casey Neistat, el mejor storyteller que tiene YouTube"
        paint(ctx, os.path.join(REF, 'casey2.png'), None, w - 330, 0, 330, h, a, anchor_top=False)
        k = pop(t, T(29) - 0.15)
        quote(ctx, ['CASEY', 'NEISTAT'], 50, 110, 96, a, k=pop(t, st0 + 0.1))
        if k > 0.001: put(ctx, HB('EL MEJOR STORYTELLER DE YOUTUBE', 30, WHITE, 1), 52, 330 + 8 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
    elif name == 'simple':                                                  # "¿por qué es el mejor? porque lo hace muy simple"
        paint_clip(ctx, 'm_car', t, st0, 0, 0, w, h, a)
        ctx.rectangle(0, 0, w, h); ctx.set_source_rgba(0, 0, 0, 0.25 * a); ctx.fill()
        k1 = pop(t, st0 + 0.1); k2 = pop(t, T(46) - 0.15)
        quote(ctx, ['¿POR QUÉ ES EL MEJOR?'], 40, 70, 48, a, k=k1)
        if k2 > 0.001: quote(ctx, ['LO HACE', 'MUY SIMPLE.'], 40, 190, 82, a, k=k2)
    elif name == 'thread':                                                  # "desde el comienzo hasta el final… nunca pierdes el hilo, dure 5, 10 o 15 minutos"
        sw = c01((t - (T(89) - 0.2)) / 0.25)
        quote(ctx, ['DE PRINCIPIO', 'A FIN.'], 50, 90, 74, a * (1 - sw), k=pop(t, st0 + 0.1))
        quote(ctx, ['NUNCA PIERDES', 'EL HILO.'], 50, 90, 74, a * sw, k=pop(t, T(89) - 0.2))
        x0, x1, y = 60, w - 60, 300
        ctx.rectangle(x0, y, x1 - x0, 4); ctx.set_source_rgba(1, 1, 1, 0.25 * a); ctx.fill()
        p = eio(prog(t, T(77) - 0.1, T(101) - T(77) + 0.4))                   # the thread runs from beginning to end
        ctx.rectangle(x0, y, (x1 - x0) * p, 4); rgba(ctx, RED, a); ctx.fill()
        ctx.arc(x0 + (x1 - x0) * p, y + 2, 11, 0, 2 * math.pi); rgba(ctx, RED, a); ctx.fill()
        put(ctx, HB('COMIENZO', 22, WHITE, 1), x0, y + 40, alpha=a, ax=0); put(ctx, HB('FINAL', 22, WHITE, 1), x1, y + 40, alpha=a, ax=1)
        for j, (lbl, i0) in enumerate((('5 MIN', 97), ('10 MIN', 98), ('15 MIN', 100))):
            k = pop(t, T(i0) - 0.1); xx = x0 + (x1 - x0) * (0.33 + 0.25 * j)
            if k > 0.001:
                ctx.rectangle(xx - 2, y - 16, 4, 36); rgba(ctx, WHITE, a * c01(k * 1.5)); ctx.fill()
                put(ctx, HB(lbl, 26, WHITE, 1), xx, y - 40 - 8 * (1 - k), alpha=a * c01(k * 1.5))
    elif name == 'videos':                                                  # "de los mejores videos que tiene Casey… Do Hard Things… decirle no a MrBeast"
        tw, th = 300, 172
        for j, nm in enumerate(YT[:6]):
            k = pop(t, st0 + 0.2 + 0.18 * j); col, row = j % 3, j // 3
            x = 30 + col * (tw + 20); y = 26 + row * (th + 24)
            focus = 'yt48.png' if T(118) - 0.2 <= t < T(121) else ('yt46.png' if t >= T(121) else None)
            dim = 1.0 if focus in (None, nm) else 0.35
            if k <= 0.001: continue
            sc = 1.0 + (0.06 if focus == nm else 0)
            ctx.save(); ctx.translate(x + tw / 2, y + th / 2 + 14 * (1 - k)); ctx.scale(sc, sc); ctx.translate(-tw / 2, -th / 2)
            paint(ctx, os.path.join(REF, nm), (0, 0, 10000, 10000) if False else None, 0, 0, tw, th, a * c01(k * 1.5) * dim, anchor_top=True)
            if focus == nm: ctx.rectangle(-2, -2, tw + 4, th + 4); rgba(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
            ctx.restore()
        put(ctx, HB('SUS MEJORES VIDEOS', 24, WHITE, 1), w - 30, h - 22, alpha=a, ax=1)
    elif name == 'friend':                                                  # "es una historia, como si un amigo te echara un cuento"
        montage(ctx, t, [(st0, 'm_talk'), (T(149) - 0.1, 'm_car')], 0, 0, w, h, a)
        ctx.rectangle(0, 0, w, h); ctx.set_source_rgba(0, 0, 0, 0.25 * a); ctx.fill()
        quote(ctx, ['COMO UN AMIGO', 'CONTÁNDOTE', 'UNA HISTORIA.'], 40, 70, 64, a, 'CASEY NEISTAT', w - 30, h - 30, k=pop(t, T(146) - 0.15))
        k = pop(t, T(165) - 0.15)                                            # "esa es la clave"
        if k > 0.001:
            tt = HB('ESA ES LA CLAVE', 30, WHITE, 1); pw = tt[4] + 40
            ctx.rectangle(40, h - 74, pw, 50); rgba(ctx, RED, a * c01(k * 1.5)); ctx.fill(); put(ctx, tt, 60, h - 48, alpha=a * c01(k * 1.5), ax=0)
    elif name == 'where':                                                   # empresa, negocio, redes sociales
        put(ctx, HB('APLICA EL STORYTELLING EN TU', 36, WHITE, 1), 50, 60 + lift, alpha=a, ax=0)
        for j, (lbl, i0) in enumerate((('EMPRESA', 177), ('NEGOCIO', 180), ('REDES SOCIALES', 184))):
            k = pop(t, T(i0) - 0.2)
            if k > 0.001: put(ctx, HB(lbl, 82, WHITE, 1), 50, 150 + j * 82 + 12 * (1 - k), alpha=a * c01(k * 1.5), ax=0)
    elif name == 'feel':                                                    # no rígido, no una lección (como yo ahora), que se sienta genuino
        for j, (lbl, i0) in enumerate((('RÍGIDO', 190), ('UNA LECCIÓN', 198))):
            k = pop(t, T(i0) - 0.2); tt = HB(lbl, 66, WHITE, 1); y = 90 + j * 86
            if k <= 0.001: continue
            put(ctx, tt, 50, y + 10 * (1 - k), alpha=a * c01(k * 1.5) * 0.85, ax=0)
            strike(ctx, 50, y + 2, tt[4] + 4, a, eo(prog(t, T(i0) + 0.25, 0.35)))
        kj = pop(t, T(205) - 0.15)
        if kj > 0.001: put(ctx, HB('(COMO YO AHORA MISMO)', 24, WHITE, 2), 54, 236 + 8 * (1 - kj), alpha=a * c01(kj * 1.5) * 0.8, ax=0)
        kg = pop(t, T(214) - 0.2)
        if kg > 0.001: quote(ctx, ['GENUINO.'], 50, 330, 82, a, k=kg)

def stage(ctx, t):
    """full-screen beats in his format: black, 16:9 footage with hard cuts, quote above, credit below"""
    seqs = {0: [(FS1[0], 'm_door'), (T(53) - 0.1, 'm_run'), (T(57) - 0.1, 'm_pyr'), (T(60) - 0.1, 'm_cliff'), (T(63) - 0.1, 'm_hand'), (T(65) - 0.1, 'm_pyr2')],
            1: [(FS2[0], 'm_box'), (T(136) - 0.1, 'm_win'), (T(139) - 0.1, 'm_end')],
            2: [(FS3[0], 'm_pyr2'), (T(222) - 0.1, 'm_run'), (T(228) - 0.1, 'm_hand'), (T(234) - 0.1, 'm_talk')]}
    for i, b in enumerate(BEATS):
        a = beat_a(t, b)
        if a <= 0.002: continue
        ctx.rectangle(0, 0, W, H); rgba(ctx, (0, 0, 0, 1), a); ctx.fill()
        vy = 640; vh = 608
        montage(ctx, t, seqs[i], 0, vy, W, vh, a)
        if i == 0:
            quote(ctx, ['UNA IDEA SIMPLE.', 'UNA NARRATIVA', 'VISUAL HERMOSA.'], 60, 300, 74, a, k=pop(t, b[0] + 0.1))
        elif i == 1:
            quote(ctx, ['NIKE LE PIDIÓ', 'UN COMERCIAL.'], 60, 360, 74, a, k=pop(t, b[0] + 0.1))
            put(ctx, HB('"MAKE IT COUNT" · CASEY NEISTAT', 28, WHITE, 1), W - 60, vy + vh + 60, alpha=a, ax=1)
        else:
            quote(ctx, ['UNA HISTORIA', 'TAN BUENA QUE', 'SE LA CONTARÍAS', 'A UN AMIGO.'], 60, 250, 70, a, k=pop(t, b[0] + 0.1))
            put(ctx, HB('#MAKEITCOUNT', 30, WHITE, 1), W - 60, vy + vh + 60, alpha=a * c01((t - T(234)) / 0.3), ax=1)

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = c01(spring(t - SHAPE_ON, w=9.0, zeta=0.92)) * (1 - any_beat(t))
    if appear <= 0.01: return
    f = min(1.0, BAND_H / h, BAND_W / w); cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 30 * (1 - appear)); ctx.scale(f, f); ctx.translate(-w / 2, -h / 2)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 12 * (1 - eo(c01((t - st[0] - 0.1) / 0.5)))
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore(); ctx.restore()

# ---------------- title (over the hook), his caps style ----------------
LABEL = 'teoría by andrés corrales'
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 860, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.45, 0, 0, 0, 0.55 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.8 * a)
    ctx.rectangle(0, 860, W, H - 860); ctx.set_source(g); ctx.fill()
TITLE = ['EL MEJOR', 'STORYTELLER', 'DE YOUTUBE.']
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.3 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, HB(LABEL[:n], 34, WHITE, 0, shadow=6), 66, 1050, alpha=fade, ax=0)
    for li, line in enumerate(TITLE):
        e = 1.0 if force else spring(t - (0.4 + 0.1 * li), w=10.0, zeta=0.9)
        put(ctx, HB(line, 128, WHITE, 1, shadow=10, shadow_a=200), 60, 1160 + li * 118 + 24 * (1 - e), alpha=c01(e * 1.4) * fade, ax=0)

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
    """his text style: white Helvetica Bold caps, soft shadow, no box"""
    if t < TITLE_END: return
    for st, en, line in CHUNKS:
        if st <= t < en: break
    else: return
    e = c01((t - st) / 0.08)
    tt = HB(line.upper(), 60, WHITE, 1, shadow=8, shadow_a=200); sc = min(1.0, 960 / tt[4])
    y = 1450
    put(ctx, tt, W / 2, y, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    ctx.rectangle(0, H - 8, W * c01(t / DUR), 8); rgba(ctx, RED); ctx.fill()

# ---------------- frame ----------------
def render_frame(fr16, t, fi):
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))
    sdr = full.copy(); hdr = full.copy()
    arr, surf, ctx = fx.new_layer()
    draw_shape(ctx, t); stage(ctx, t); title(ctx, t); subtitles(ctx, t); progress(ctx, t)
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
