"""IMG_9008 + IMG_9009 · "2 personas que tienes que seguir si estás en marketing" (Héctor Serrano, Matt Swulinski). 1.05x, voice only.
Look: Dribbble / Apple-keynote UI motion. Me cut out in FRONT (Apple Vision person masks), everything else BEHIND me on a warm light
canvas. One white shape that morphs (springs on x, y, w, h, radius, colour) between states while its content swaps with a short
fade-lift: profile card -> Wispr Flow site -> tweets -> Matt card -> 0→100 counter -> morphing pill -> LinkedIn card.
No camera movement: the only motion of my image is the spring between full frame and the cut-out size. Simple subtitles,
blue progress bar. Springs are closed-form (pure functions of time). HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit16 as E; os.chdir(_cwd)

SPEED = 1.05
GF = os.path.expanduser('~/Library/Fonts/')
G_REG, G_MED, G_SEMI, G_BOLD = GF + 'Geist-Regular.otf', GF + 'Geist-Medium.otf', GF + 'Geist-SemiBold.otf', GF + 'Geist-Bold.otf'
G_MONO = GF + 'GeistMono-Medium.otf'
CANVAS = (0xEE, 0xEC, 0xE8); INK = (0.07, 0.07, 0.07, 1); MUTE = (0.45, 0.45, 0.43, 1); WHITE = (1, 1, 1, 1)
BLUE = (0x2F / 255, 0x6B / 255, 0xFF / 255, 1)
REF = os.path.join(HERE, 'ref')

# ---------------- text (Geist) ----------------
_tc = {}
def TX(txt, font, size, col=INK, shadow=0, shadow_a=150):
    key = (txt, font, size, col, shadow, shadow_a)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(font, size)
    asc, desc = f.getmetrics(); tw = max(1, f.getlength(txt)); pad = 12 + int(size * 0.25) + shadow * 2
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad, pad + 3), txt, font=f, fill=(0, 0, 0, shadow_a))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=tuple(int(c * 255) for c in col[:3]) + (int(col[3] * 255),))
    s, buf = fx.pil_surface(img); r = (s, buf, w, h, tw, asc); _tc[key] = r; return r

# ---------------- springs (closed form, pure functions of time) ----------------
def spring(x, w=13.0, zeta=0.82):
    """unit step response, slight overshoot at most"""
    if x <= 0: return 0.0
    if zeta >= 1: return 1 - math.exp(-w * x) * (1 + w * x)
    wd = w * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * w * x) * (math.cos(wd * x) + zeta * w / wd * math.sin(wd * x))
def track(t, events, v0, **kw):
    """value that changes target many times = sum of one spring per change"""
    v, prev = v0, v0
    for te, tgt in events:
        v += (tgt - prev) * spring(t - te, **kw); prev = tgt
    return v

# ---------------- words / timing ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {11: 'marketing', 14: 'compañía,', 18: 'de verdad', 44: 'Héctor', 45: 'Serrano,', 53: 'Wispr Flow,', 57: 'voice-to-text', 58: '', 59: '',
       71: 'man', 86: 'Wispr Flow.', 90: '', 91: 'Matt', 92: 'Swulinski,', 106: 'programas', 109: '', 110: 'UGC,', 114: 'de',
       137: 'en todo, en', 138: 'cómo', 147: 'marketing,', 166: 'para', 177: 'manes,'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.35
TITLE_END = 5.0

# ---------------- person: full frame <-> cut-out in front (the only image motion) ----------------
CUT_S = 0.72 if os.environ.get('LAYOUT') == 'B' else 0.62
MODE = [(TITLE_END - 0.05, 1.0), (T(148) - 0.08, 0.0), (T(172) - 0.08, 1.0)]
LAYOUT = os.environ.get('LAYOUT', 'C')
def mode(t):
    if LAYOUT in ('A', 'C'): return 0.0
    return c01(track(t, MODE, 0.0, w=10.0, zeta=1.0))

_mcache = {}
def mask(fi):
    if fi in _mcache: return _mcache[fi]
    p = os.path.join(HERE, 'masks', '%05d.png' % fi)
    m = np.asarray(Image.open(p).convert('L').resize((W, H), Image.BILINEAR)).astype(np.float32) / 255 if os.path.exists(p) else None
    if len(_mcache) > 6: _mcache.pop(next(iter(_mcache)))
    _mcache[fi] = m; return m
def smooth_mask(fi):
    ms = [m for m in (mask(fi - 1), mask(fi), mask(fi + 1)) if m is not None]
    d = 2
    while not ms and d < 30:                                              # Vision gave no mask for this frame: borrow the nearest
        ms = [m for m in (mask(fi - d), mask(fi + d)) if m is not None]; d += 1
    if not ms: return None
    m = sum(ms) / len(ms)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255
    return np.clip((m - 0.08) / 0.84, 0, 1)

# ---------------- canvas & cards ----------------
def rr(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()

_img = {}
def img(name, crop=None):
    key = (name, crop)
    if key not in _img:
        im = Image.open(os.path.join(REF, name)).convert('RGB')
        if crop: im = im.crop(crop)
        _img[key] = (im, fx.pil_surface(im.convert('RGBA')))
    return _img[key]

def paint_img(ctx, name, crop, x, y, w, h, alpha, lift=0.0):
    """cover-fit the image into (x, y, w, h)"""
    if alpha <= 0.002: return
    im, (surf, _b) = img(name, crop)
    s = max(w / im.width, h / im.height)
    ctx.save(); ctx.translate(x + w / 2, y + h / 2 + lift); ctx.scale(s, s)
    ctx.set_source_surface(surf, -im.width / 2, -im.height / 2); ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha); ctx.restore()

def soft_shadow(ctx, x, y, w, h, r, a):
    for k, (dy, grow, al) in enumerate([(18, 18, 0.05), (10, 8, 0.06), (3, 1, 0.07)]):
        rr(ctx, x - grow, y - grow + dy, w + 2 * grow, h + 2 * grow, r + grow); ctx.set_source_rgba(0, 0, 0, al * a); ctx.fill()

# ---------------- the morphing shape ----------------
HECTOR = ('hector.png', None); WF = ('wf2.png', (300, 0, 3324, 1828)); MATT = ('matt.png', None); LINKEDIN = ('cap3.png', (20, 0, 1272, 496))
TW1 = ('cap2.png', None); TW2 = ('cap1.png', None)
CX = W / 2
STATES = [  # (start time, name, x-centre, y-centre, w, h, radius, fill (r,g,b))
    (T(43) - 0.08, 'hector', CX, 440, 900, 655, 44, (1, 1, 1)),
    (T(56) - 0.08, 'wf', CX, 430, 900, 545, 44, (1, 1, 1)),
    (T(72) - 0.08, 'tweets', CX, 440, 820, 666, 40, (1, 1, 1)),
    (T(87) - 0.08, 'matt', CX, 400, 920, 483, 44, (0.04, 0.04, 0.06)),
    (T(94) - 0.08, 'counter', CX, 420, 700, 360, 56, (1, 1, 1)),
    (T(103) - 0.08, 'pill', CX, 430, 720, 140, 70, (0.07, 0.07, 0.07)),
    (T(106) - 0.08, 'pill2', CX, 430, 860, 140, 70, (0.07, 0.07, 0.07)),
    (T(111) - 0.08, 'pill3', CX, 430, 300, 140, 70, (0.07, 0.07, 0.07)),
    (T(114) - 0.08, 'linkedin', CX, 420, 940, 371, 40, (1, 1, 1)),
]
BAND_TOP, BAND_H, BAND_W = 46, 384, 1000
SHAPE_ON, SHAPE_OFF = STATES[0][0], T(119) - 0.08
def shape_geo(t):
    keys = []
    for k in range(8):
        ev = [(s[0], (s[2], s[3], s[4], s[5], s[6], *s[7])[k]) for s in STATES[1:]]
        v0 = (STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7])[k]
        keys.append(track(t, ev, v0, w=12.0, zeta=0.86))
    return keys
def state_alpha(t, i):
    """content of state i: quick fade-in after its start, fade-out when the next one starts"""
    a = STATES[i][0]; b = STATES[i + 1][0] if i + 1 < len(STATES) else SHAPE_OFF
    return c01((t - a - 0.06) / 0.20) * (1 - c01((t - b) / 0.12))

def draw_shape(ctx, t):
    if t < SHAPE_ON or t > SHAPE_OFF + 0.45: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = spring(t - SHAPE_ON, w=11.0, zeta=0.9) * (1 - spring(t - SHAPE_OFF, w=12.0, zeta=1.0))
    sc = 0.86 + 0.14 * appear
    if appear <= 0.01: return
    f = min(1.0, BAND_H / h, BAND_W / w) if LAYOUT == 'C' else 1.0     # option C: stay above my eyes
    if LAYOUT == 'C': cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 40 * (1 - appear)); ctx.scale(sc * f, sc * f); ctx.translate(-w / 2, -h / 2)
    soft_shadow(ctx, 0, 0, w, h, r, appear)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 14 * (1 - c01((t - st[0] - 0.06) / 0.25))
        name = st[1]
        if name == 'hector':
            paint_img(ctx, *HECTOR, 0, 0, w, h, a, lift)
            k = eo(prog(t, T(50) - 0.05, 0.45))                          # "el segundo empleado": highlight the bio line
            if k > 0:
                s_ = w / 1232; hy = 640 * s_; hx0 = 36 * s_
                rr(ctx, hx0, hy, (430 * s_) * k, 50 * s_, 12); ctx.set_source_rgba(BLUE[0], BLUE[1], BLUE[2], 0.22 * a); ctx.fill()
                rr(ctx, hx0, hy, (430 * s_) * k, 50 * s_, 12); rgba(ctx, BLUE, a); ctx.set_line_width(3); ctx.stroke()
        elif name == 'wf': paint_img(ctx, *WF, 0, 0, w, h, a, lift)
        elif name == 'matt': paint_img(ctx, *MATT, 0, 0, w, h, a, lift)
        elif name == 'linkedin':
            paint_img(ctx, *LINKEDIN, 0, 0, w, h, a, lift)
            k = eo(prog(t, T(116) - 0.05, 0.45))                         # "un montón de empresas": underline the companies line
            if k > 0:
                s_ = w / 1252; rr(ctx, 30 * s_, 415 * s_, 770 * s_ * k, 40 * s_, 10)
                ctx.set_source_rgba(BLUE[0], BLUE[1], BLUE[2], 0.22 * a); ctx.fill()
        elif name == 'tweets':
            ctx.rectangle(0, 0, w, h); ctx.set_source_rgba(0, 0, 0, a); ctx.fill()
            paint_img(ctx, *TW1, 0, 0, w, h, a, lift)
        elif name == 'counter':
            k = eio(prog(t, T(94) + 0.2, T(102) + 0.25 - T(94) - 0.2))           # counts while I say 'creció un montón de empresas de cero a cien'
            n = int(round(100 * k))
            put(ctx, TX('EMPRESAS', G_MONO, 26, MUTE), w / 2, 70 + lift, alpha=a)
            put(ctx, TX('0 → %d' % n, G_BOLD, 150, INK), w / 2, h / 2 + 10 + lift, alpha=a)
            put(ctx, TX('de cero a cien', G_MED, 34, MUTE), w / 2, h - 62 + lift, alpha=a)
        elif name.startswith('pill'):
            txt = {'pill': 'Partnership programs', 'pill2': 'Programas de creadores UGC', 'pill3': 'Ads'}[name]
            put(ctx, TX(txt, G_SEMI, 50, WHITE), w / 2, h / 2 + 2 + lift * 0.6, alpha=a)
    ctx.restore(); ctx.restore()
    # the second tweet slides in behind-left of the first while in the 'tweets' state
    a = state_alpha(t, 2) * appear
    if a > 0.002:
        k = spring(t - T(76), w=11.0, zeta=0.86)
        if k > 0.001:
            ww, hh = 340, 342; x0 = 700 + 30 * (1 - k); y0 = 250 + 40 * (1 - k)
            ctx.save(); ctx.translate(x0 + ww / 2, y0 + hh / 2); ctx.rotate(math.radians(4 * k)); ctx.translate(-ww / 2, -hh / 2)
            soft_shadow(ctx, 0, 0, ww, hh, 30, a * k)
            rr(ctx, 0, 0, ww, hh, 30); ctx.set_source_rgba(0, 0, 0, a * k); ctx.fill()
            rr(ctx, 0, 0, ww, hh, 30); ctx.save(); ctx.clip(); paint_img(ctx, *TW2, 0, 0, ww, hh, a * k); ctx.restore()
            ctx.restore()

# ---------------- the two people (S1 and S4) ----------------
AV = {'h': ('hector.png', (53, 215, 323, 485)), 'm': ('matt.png', (745, 100, 1205, 560))}
PEOPLE = [('h', 'Héctor Serrano', 'Marketing hire #2 · Wispr Flow'), ('m', 'Matt Swulinski', 'Head of Growth · Viktor')]
PAIR_SPANS = [(T(15) - 0.05, T(43) - 0.1), (T(119) - 0.05, T(148) - 0.1)]
def avatar(ctx, key, cx, cy, d, a):
    im, (surf, _b) = img(*AV[key]); s = d / im.width
    soft_shadow(ctx, cx - d / 2, cy - d / 2, d, d, d / 2, a)
    ctx.save(); ctx.arc(cx, cy, d / 2, 0, 2 * math.pi); ctx.clip(); ctx.translate(cx - d / 2, cy - d / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
    ctx.arc(cx, cy, d / 2, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(6); ctx.stroke()

LABELS = [(T(43) - 0.05, T(87) - 0.1, '01', 'Héctor Serrano'), (T(87) - 0.05, T(119) - 0.1, '02', 'Matt Swulinski')]
def section_label(ctx, t):
    """small '01 · name' tag that rides the bottom-left corner of the band"""
    for a0, b0, num, name in LABELS:
        if a0 <= t < b0 + 0.3: break
    else: return
    k = spring(t - a0 - 0.15, w=12.0, zeta=0.85) * (1 - spring(t - b0, w=12.0, zeta=1.0))
    if k <= 0.01: return
    t1 = TX(num, G_MONO, 28, WHITE); t2 = TX(name, G_SEMI, 32, INK)
    w_ = t1[4] + t2[4] + 96; h_ = 64; x0 = 60 - 20 * (1 - k); y0 = BAND_TOP + BAND_H + 10 + 14 * (1 - k)
    soft_shadow(ctx, x0, y0, w_, h_, h_ / 2, k)
    rr(ctx, x0, y0, w_, h_, h_ / 2); ctx.set_source_rgba(1, 1, 1, k); ctx.fill()
    rr(ctx, x0 + 8, y0 + 8, t1[4] + 34, h_ - 16, (h_ - 16) / 2); rgba(ctx, BLUE, k); ctx.fill()
    put(ctx, t1, x0 + 8 + (t1[4] + 34) / 2, y0 + h_ / 2 + 1, alpha=k)
    put(ctx, t2, x0 + t1[4] + 58, y0 + h_ / 2 + 1, alpha=k, ax=0)

def pair(ctx, t):
    for a0, b0 in PAIR_SPANS:
        if a0 <= t < b0 + 0.4: break
    else: return
    out = spring(t - b0, w=12.0, zeta=1.0)
    for j, (key, name, sub) in enumerate(PEOPLE):
        k = spring(t - a0 - 0.12 * j, w=11.0, zeta=0.8) * (1 - out)
        if k <= 0.01: continue
        cx = 300 + 480 * j; cy = 170 + 40 * (1 - k)
        avatar(ctx, key, cx, cy, 210 * (0.85 + 0.15 * k), c01(k * 1.3))
        put(ctx, TX(name, G_SEMI, 42, WHITE, shadow=6), cx, cy + 150, alpha=c01(k * 1.3))
        put(ctx, TX(sub, G_MED, 27, WHITE, shadow=6), cx, cy + 196, alpha=c01(k * 1.3))
    k = spring(t - a0 - 0.3, w=10.0, zeta=1.0) * (1 - out)                  # step chip
    if k > 0.01:
        pass

# ---------------- follow list (end) ----------------
FOLLOW_ON = T(172) - 0.05
CLICKS = [T(176) - 0.05, T(178) - 0.05]
ROWS = [('h', 'Héctor Serrano', '@hectorserrranoo · X'), ('m', 'Matt Swulinski', 'Matt Swulinski · LinkedIn')]
PW, PX, PY, ROWH = 900, (W - 900) / 2, 46, 150
def btn_geo(t, j):
    on = spring(t - CLICKS[j] - 0.06, w=13.0, zeta=0.8)
    return 210 + 50 * on, on                                               # "Seguir" -> "Siguiendo" grows
def cursor(ctx, x, y, a, press=0.0):
    if a <= 0: return
    s = 1.0 - 0.15 * press
    ctx.save(); ctx.translate(x, y); ctx.scale(1.3 * s, 1.3 * s)
    ctx.move_to(0, 0); ctx.line_to(0, 30); ctx.line_to(8, 23); ctx.line_to(13, 34); ctx.line_to(18, 32); ctx.line_to(13, 21); ctx.line_to(23, 21); ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.25 * a); ctx.save(); ctx.translate(1.5, 2.5); ctx.fill_preserve(); ctx.restore(); ctx.new_path()
    ctx.move_to(0, 0); ctx.line_to(0, 30); ctx.line_to(8, 23); ctx.line_to(13, 34); ctx.line_to(18, 32); ctx.line_to(13, 21); ctx.line_to(23, 21); ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, a); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
def follow(ctx, t):
    if t < FOLLOW_ON: return
    k = spring(t - FOLLOW_ON, w=11.0, zeta=0.86); a = c01(k * 1.4)
    h = 60 + ROWH * 2; y0 = PY + 40 * (1 - k)
    ctx.save(); ctx.translate(W / 2, y0 + h / 2); s = 0.9 + 0.1 * k; ctx.scale(s, s); ctx.translate(-PW / 2, -h / 2)
    soft_shadow(ctx, 0, 0, PW, h, 44, a); rr(ctx, 0, 0, PW, h, 44); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    for j, (key, name, sub) in enumerate(ROWS):
        ry = 30 + j * ROWH + ROWH / 2
        if j == 0:
            ctx.rectangle(40, 30 + ROWH, PW - 80, 1.5); ctx.set_source_rgba(0, 0, 0, 0.08 * a); ctx.fill()
        avatar(ctx, key, 110, ry, 104, a)
        put(ctx, TX(name, G_SEMI, 40, INK), 190, ry - 20, alpha=a, ax=0)
        put(ctx, TX(sub, G_REG, 27, MUTE), 190, ry + 24, alpha=a, ax=0)
        bw, on = btn_geo(t, j); bh = 76; bx = PW - 44 - bw; by = ry - bh / 2
        fill = 1 - on                                                     # black -> white
        rr(ctx, bx, by, bw, bh, bh / 2); ctx.set_source_rgba(0.07 + 0.93 * on, 0.07 + 0.93 * on, 0.07 + 0.93 * on, a); ctx.fill()
        if on > 0.01:
            rr(ctx, bx, by, bw, bh, bh / 2); ctx.set_source_rgba(0, 0, 0, 0.18 * a * on); ctx.set_line_width(2); ctx.stroke()
        put(ctx, TX('Seguir', G_SEMI, 32, WHITE), bx + bw / 2, ry + 1, alpha=a * (1 - c01(on * 2)))
        put(ctx, TX('Siguiendo', G_SEMI, 32, INK), bx + bw / 2, ry + 1, alpha=a * c01(on * 2 - 0.6))
    ctx.restore()
    # cursor: glides in, clicks row 1, then row 2 (positions in frame coords)
    s = 0.9 + 0.1 * k; ox, oy = W / 2 - PW / 2 * s, y0 + h / 2 - h / 2 * s
    def btn_xy(j):
        bw, _ = btn_geo(CLICKS[j], j); return ox + (PW - 44 - 105) * s, oy + (30 + j * ROWH + ROWH / 2) * s
    p0 = (W - 120, PY + h + 160); p1 = btn_xy(0); p2 = btn_xy(1)
    m1 = eio(prog(t, FOLLOW_ON + 0.25, CLICKS[0] - FOLLOW_ON - 0.3)); m2 = eio(prog(t, CLICKS[0] + 0.2, CLICKS[1] - CLICKS[0] - 0.25))
    x = p0[0] + (p1[0] - p0[0]) * m1 + (p2[0] - p1[0]) * m2; y = p0[1] + (p1[1] - p0[1]) * m1 + (p2[1] - p1[1]) * m2
    press = max(math.sin(math.pi * c01((t - CLICKS[0] + 0.06) / 0.16)), math.sin(math.pi * c01((t - CLICKS[1] + 0.06) / 0.16)))
    cursor(ctx, x, y, a * c01((t - FOLLOW_ON - 0.2) / 0.2), press)
    kk = spring(t - (T(179) - 0.05), w=10.0, zeta=1.0)
    if kk > 0.01: put(ctx, TX('Links en la descripción', G_MED, 32, MUTE), W / 2, y0 + h + 60 + 14 * (1 - kk), alpha=kk)

# ---------------- title (over my live face) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['2', 'personas', 'que'], ['tienes', 'que', 'seguir'], ['si', 'estás', 'en'], ['marketing']]
def title(ctx, t):
    if t >= TITLE_END: return
    fade = 1 - c01((t - (TITLE_END - 0.35)) / 0.35)
    n = min(len(LABEL), int(max(0, t - 0.1) / 0.025))
    if n > 0:
        txt = LABEL[:n] if n < len(LABEL) else (LABEL if int(t * 2.2) % 2 == 0 else LABEL[:-1])
        put(ctx, TX(txt, G_MED, 38, WHITE, shadow=6), 70, 1060, alpha=fade, ax=0)
    t0 = 0.1 + 0.025 * len(LABEL); k = 0
    for li, line in enumerate(TITLE):
        x = 70; y = 1160 + li * 112
        for wd in line:
            tt = TX(wd, G_BOLD, 100, WHITE, shadow=10, shadow_a=170)
            e = spring(t - (t0 + 0.07 * k), w=12.0, zeta=0.86)
            put(ctx, tt, x, y + 30 * (1 - e), alpha=c01(e * 1.4) * fade, ax=0)
            x += tt[4] + 26; k += 1

# ---------------- subtitles (simple) ----------------
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
    tt = TX(line, G_SEMI, 58, WHITE, shadow=8, shadow_a=190); sc = min(1.0, 960 / tt[4])
    pa = c01((mode(t) - 0.5) * 2)                                         # on the light canvas: soft dark plate so white text always reads
    if pa > 0:
        pw_, ph_ = tt[4] * sc + 56, 88 * sc; rr(ctx, W / 2 - pw_ / 2, 1450 + 8 * (1 - e) - ph_ / 2 - 2, pw_, ph_, ph_ / 2)
        ctx.set_source_rgba(0, 0, 0, 0.55 * e * pa); ctx.fill()
    put(ctx, tt, W / 2, 1450 + 8 * (1 - e), scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 10, W, 10); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.fill()
    ctx.rectangle(0, H - 10, W * c01(t / DUR), 10); rgba(ctx, BLUE); ctx.fill()

_bd = {}
def backdrop(t):
    """full-bleed blurred version of whatever the shape is showing (or of my own shot when nothing is shown)"""
    key = None
    for i, st in enumerate(STATES):
        b = STATES[i + 1][0] if i + 1 < len(STATES) else SHAPE_OFF
        if st[0] <= t < b: key = st[1]
    srcs = {'hector': HECTOR, 'wf': WF, 'tweets': TW1, 'matt': MATT, 'linkedin': LINKEDIN, 'counter': MATT, 'pill': MATT, 'pill2': MATT, 'pill3': MATT}
    if key is None: key = 'hector' if t < STATES[0][0] else 'matt'
    nm, cr = srcs[key]
    if (nm, cr) not in _bd:
        im = Image.open(os.path.join(REF, nm)).convert('RGB')
        if cr: im = im.crop(cr)
        s_ = max(W / im.width, H / im.height); im = im.resize((int(im.width * s_) + 1, int(im.height * s_) + 1), Image.LANCZOS)
        x0, y0 = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(40))
        a = np.asarray(im).astype(np.float32) * 0.78; _bd[(nm, cr)] = a.astype(np.uint8)
    return _bd[(nm, cr)]

# ---------------- frame ----------------
CANVAS_F = np.array(CANVAS, np.float32) / 255
CANVAS_H = fx.srgb8_to_hlg(np.array(CANVAS, np.uint8)[None, None, :])[0, 0]
def render_frame(fr16, t, fi):
    m = mode(t)
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))               # HLG signal, full frame
    if LAYOUT in ('A', 'C'):
        sdr = full.copy(); hdr = full.copy()
        arr, surf, ctx = fx.new_layer(); draw_shape(ctx, t); section_label(ctx, t); pair(ctx, t); follow(ctx, t); surf.flush()
        if LAYOUT == 'C':
            fx.layer_over(sdr, hdr, arr)
        else:                                                              # A: graphics between my room and me
            mk = smooth_mask(fi); s2, h2 = sdr.copy(), hdr.copy(); fx.layer_over(s2, h2, arr)
            a_ = (mk if mk is not None else np.zeros((H, W), np.float32))[..., None]
            sdr = full * a_ + s2 * (1 - a_); hdr = full * a_ + h2 * (1 - a_)
        arr, surf, ctx = fx.new_layer(); title(ctx, t); subtitles(ctx, t); progress(ctx, t); surf.flush(); fx.layer_over(sdr, hdr, arr)
        return sdr, hdr
    if m < 0.001:
        sdr = full.copy(); hdr = full.copy()
    else:
        sdr = np.empty((H, W, 3), np.float32); sdr[:] = CANVAS_F
        hdr = np.empty((H, W, 3), np.float32); hdr[:] = CANVAS_H
        if LAYOUT == 'B':
            bg = backdrop(t)
            if bg is not None: sdr[:] = bg.astype(np.float32) / 255; hdr[:] = fx.srgb8_to_hlg(bg)
        arr, surf, ctx = fx.new_layer()                                  # content BEHIND me
        draw_shape(ctx, t); pair(ctx, t); follow(ctx, t)
        surf.flush(); fx.layer_over(sdr, hdr, arr)
        s = 1 - (1 - CUT_S) * m; pw, ph = int(round(W * s)), int(round(H * s)); x0, y0 = (W - pw) // 2, H - ph
        mk = smooth_mask(fi)
        if mk is None: mk = np.ones((H, W), np.float32)
        person = full if (pw, ph) == (W, H) else fx.resize_f(full, (0, 0, W, H), (pw, ph))
        mks = mk if (pw, ph) == (W, H) else np.asarray(Image.fromarray(mk).resize((pw, ph), Image.BILINEAR))
        # my shoulders/arms leave the frame at the sides: without this the cut-out shows a hard vertical edge (a "box" of my
        # room). Feather the person into the canvas near the left/right edges and the bottom corners of the shrunken shot.
        xs = np.arange(pw, dtype=np.float32); F = 0.20 * pw
        rx = np.clip(np.minimum(xs, pw - 1 - xs) / F, 0, 1); rx = rx * rx * (3 - 2 * rx)
        ys = np.arange(ph, dtype=np.float32); ry = 1 - 0.0 * ys                                  # bottom edge is the frame edge: keep
        ramp = (ry[:, None] * rx[None, :]) ** m
        mm = mks * ramp
        alpha = (mm + (1 - mm) * (1 - m))[..., None]                     # background of my shot fades as it shrinks
        for img_ in (sdr, hdr):
            reg = img_[y0:y0 + ph, x0:x0 + pw]
            img_[y0:y0 + ph, x0:x0 + pw] = person * alpha + reg * (1 - alpha)
    arr, surf, ctx = fx.new_layer()                                      # front layer
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
    eh, es = fx.encoders(sys.argv[2], sys.argv[3], os.path.join(HERE, 'mix.wav'))
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t, fi)
        eh.stdin.write(np.ascontiguousarray(fx.to16(hdr)).tobytes()); es.stdin.write(np.ascontiguousarray(fx.to8(sdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    for e_ in (eh, es): e_.stdin.close()
    for e_ in (eh, es): e_.wait()
    print('done', sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
