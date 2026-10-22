"""IMG_9027 (hook) + IMG_9025 · Graza: "Marcas que tienes que seguir si trabajas en marketing · Nº 1 Graza". 1.05x, voice only.
Format I (option C): my real room full frame, one morphing shape above my eyes, graphics on top. Everything in Graza's brand:
cream #F3E7DA, olive ink #3D4230, lime #D4DF55, drizzle green #B0ED8D; tall condensed serif (New York condensed ~ their headline
serif) + typewriter mono (Courier New Bold ~ their mono); their wordmark and olive-tap icon extracted from the site screenshots.
B-roll fragments from the reference reel are cropped above/below its burned-in captions and away from the IG UI, silent.
Subtitles in a cream pill with olive border. Lime progress bar. HDR (HLG) only."""
import sys, os, json, math, subprocess, wave, glob
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit18 as E; os.chdir(_cwd)

SPEED = 1.05
REF = os.path.join(HERE, 'ref'); CLIPS = os.path.join(HERE, 'clips')
NY = '/System/Library/Fonts/NewYork.ttf'
MONO = '/System/Library/Fonts/Supplemental/Courier New Bold.ttf'
def C(r, g, b, a=1.0): return (r / 255, g / 255, b / 255, a)
CREAM, OLIVE, LIME, GREEN = C(243, 231, 218), C(61, 66, 48), C(212, 223, 85), C(176, 237, 141)
BOTTLE, MUTE, WHITE = C(38, 52, 30), C(120, 118, 104), (1, 1, 1, 1)

# ---------------- text ----------------
_tc = {}
def _surf(img, tw, asc):
    s, buf = fx.pil_surface(img); return (s, buf, img.width, img.height, tw, asc)
def CS(txt, size, col=OLIVE, var='Regular', cond=0.80, shadow=0, shadow_a=160):
    """tall condensed serif (New York squeezed horizontally) ~ Graza's headline serif"""
    key = ('CS', txt, size, col, var, cond, shadow, shadow_a)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(NY, size); f.set_variation_by_name(var)
    asc, desc = f.getmetrics(); tw = max(1, f.getlength(txt)); pad = 12 + int(size * 0.25) + shadow * 2
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad, pad + 4), txt, font=f, fill=(0, 0, 0, shadow_a))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=tuple(int(c * 255) for c in col[:3]) + (int(col[3] * 255),))
    img = img.resize((max(1, int(w * cond)), h), Image.LANCZOS)
    r = _surf(img, tw * cond, asc); _tc[key] = r; return r
def MX(txt, size, col=OLIVE, track=0.04):
    """typewriter mono ~ Graza's buttons/labels"""
    key = ('MX', txt, size, col, track)
    if key not in _tc: _tc[key] = fx.T_(txt, MONO, size, col, track=track)
    return _tc[key]

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
def pop(t, t0, w=13.0, zeta=0.78): return spring(t - t0, w=w, zeta=zeta)
def pulse(t, t0, d=0.45):
    """0 -> 1 -> 0 bump (a squeeze / a bounce)"""
    x = (t - t0) / d
    return math.sin(math.pi * x) if 0 < x < 1 else 0.0

# ---------------- words / timing ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v18.json')))['segments'] for w in s['words']]
FIX = {24: 'mercadeo.', 26: 'uno:', 27: 'Graza.', 28: '¿Qué', 105: '', 152: 'eso,', 153: 'los', 154: 'manes', 155: 'de', 156: 'Graza,',
       157: 'lo', 158: 'que', 159: 'dijeron:', 185: 'utilizan:', 189: 'oliva?'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.35
TITLE_END = T(25) - 0.1                                                  # title rides the whole hook, leaves at "Número uno"

# ---------------- drawing helpers ----------------
def rr(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
def soft_shadow(ctx, x, y, w, h, r, a):
    for dy, grow, al in [(18, 18, 0.05), (10, 8, 0.06), (3, 1, 0.07)]:
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
def mark(ctx, name, cx, cy, w, col, a, reveal=1.0):
    """brand mark (alpha png) tinted in a brand colour, centred; reveal wipes it up from the baseline"""
    if a <= 0.002: return
    im, (surf, _b) = img(name); s = w / im.width; h = im.height * s
    ctx.save()
    if reveal < 1: ctx.rectangle(cx - w / 2 - 4, cy + h / 2 - h * reveal, w + 8, h * reveal + 4); ctx.clip()
    ctx.translate(cx - w / 2, cy - h / 2 + (1 - reveal) * h * 0.35); ctx.scale(s, s)
    rgba(ctx, col, a); ctx.mask_surface(surf, 0, 0); ctx.restore()

_clip = {}
def clip_frame(name, t, t0):
    fs = _clip.get(name)
    if fs is None: fs = _clip[name] = sorted(glob.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, int((t - t0) * FPS)))
    key = (name, k)
    if key not in _img:
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
        old = [kk for kk in _img if isinstance(kk[1], int) and kk[0] == name and kk != key]
        for kk in old: _img.pop(kk)
    return _img[key]
def paint_clip(ctx, name, t, t0, x, y, w, h, alpha, lift=0.0):
    if alpha <= 0.002: return
    im, (surf, _b) = clip_frame(name, t, t0); paint_surf(ctx, surf, im.width, im.height, x, y, w, h, alpha, lift)

def pill(ctx, cx, cy, txt_t, a, fill=LIME, border=OLIVE, padx=34, h=None, bw=3):
    if a <= 0.002: return 0
    w = txt_t[4] + 2 * padx; h = h or (txt_t[3] * 0.62)
    rr(ctx, cx - w / 2, cy - h / 2, w, h, h / 2); rgba(ctx, fill, a); ctx.fill_preserve()
    if bw: rgba(ctx, border, a); ctx.set_line_width(bw); ctx.stroke()
    else: ctx.new_path()
    put(ctx, txt_t, cx, cy + 1, alpha=a); return w
def check(ctx, x, y, s, col, a, k=1.0):
    if a <= 0.002 or k <= 0: return
    pts = [(x - 0.5 * s, y), (x - 0.15 * s, y + 0.35 * s), (x + 0.55 * s, y - 0.4 * s)]
    ctx.move_to(*pts[0]); L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); d = (L1 + L2) * k
    if d <= L1: ctx.line_to(pts[0][0] + (pts[1][0] - pts[0][0]) * d / L1, pts[0][1] + (pts[1][1] - pts[0][1]) * d / L1)
    else: ctx.line_to(*pts[1]); u = (d - L1) / L2; ctx.line_to(pts[1][0] + (pts[2][0] - pts[1][0]) * u, pts[1][1] + (pts[2][1] - pts[1][1]) * u)
    rgba(ctx, col, a); ctx.set_line_width(max(3, s * 0.18)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
def asterisk(ctx, x, y, r, col, a, rot=0.0):
    for k in range(4):
        ang = rot + k * math.pi / 4
        ctx.move_to(x - r * math.cos(ang), y - r * math.sin(ang)); ctx.line_to(x + r * math.cos(ang), y + r * math.sin(ang))
    rgba(ctx, col, a); ctx.set_line_width(max(2, r * 0.32)); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
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

def graza_bottle(ctx, x, y, s, a, squish=0.0, label=LIME, cap=LIME, rot=0.0):
    """Graza squeeze bottle, origin = bottom centre, ~360*s tall. squish: 0..1 squeezes the body"""
    if a <= 0.002: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (1 + 0.16 * squish), s * (1 - 0.07 * squish))
    bw, bh = 128, 236
    rr(ctx, -bw / 2, -bh, bw, bh, 26); rgba(ctx, BOTTLE, a); ctx.fill()                               # body
    ctx.move_to(-bw / 2, -bh + 30); ctx.curve_to(-bw / 2, -bh - 34, -30, -bh - 40, -28, -bh - 58)    # shoulders
    ctx.line_to(28, -bh - 58); ctx.curve_to(30, -bh - 40, bw / 2, -bh - 34, bw / 2, -bh + 30); ctx.close_path(); rgba(ctx, BOTTLE, a); ctx.fill()
    rr(ctx, -31, -bh - 92, 62, 38, 6); rgba(ctx, cap, a); ctx.fill()                                  # cap
    ctx.move_to(-14, -bh - 90); ctx.line_to(-4, -bh - 136); ctx.line_to(4, -bh - 136); ctx.line_to(14, -bh - 90); ctx.close_path(); rgba(ctx, cap, a); ctx.fill()
    ctx.rectangle(-bw / 2, -bh * 0.70, bw, bh * 0.58); rgba(ctx, label, a); ctx.fill()                # label
    mark(ctx, 'wordmark.png', 0, -bh * 0.70 + bh * 0.58 - 26, bw * 0.84, OLIVE, a)
    mark(ctx, 'olive.png', 0, -bh * 0.48, 54, OLIVE, a)
    ctx.rectangle(bw * 0.18, -bh + 18, 10, bh * 0.22); ctx.set_source_rgba(1, 1, 1, 0.18 * a); ctx.fill()  # glint
    ctx.restore()
def plain_bottle(ctx, x, y, s, a, oil=C(214, 166, 52), lab=C(250, 248, 240)):
    """the 'traditional' olive oil bottle: clear glass, gold oil, black cap, plain label"""
    if a <= 0.002: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    bw, bh = 92, 190
    rr(ctx, -bw / 2, -bh, bw, bh, 12); ctx.set_source_rgba(0.86, 0.88, 0.86, 0.55 * a); ctx.fill()
    rr(ctx, -bw / 2 + 6, -bh + 30, bw - 12, bh - 36, 8); rgba(ctx, oil, a); ctx.fill()
    ctx.move_to(-bw / 2, -bh + 14); ctx.curve_to(-bw / 2, -bh - 30, -16, -bh - 40, -16, -bh - 70); ctx.line_to(16, -bh - 70)
    ctx.curve_to(16, -bh - 40, bw / 2, -bh - 30, bw / 2, -bh + 14); ctx.close_path(); ctx.set_source_rgba(0.86, 0.88, 0.86, 0.55 * a); ctx.fill()
    rr(ctx, -19, -bh - 100, 38, 34, 4); ctx.set_source_rgba(0.12, 0.12, 0.12, a); ctx.fill()
    ctx.rectangle(-bw / 2 + 6, -bh * 0.62, bw - 12, bh * 0.34); rgba(ctx, lab, a); ctx.fill()
    for k in range(3):
        ctx.rectangle(-bw / 2 + 18, -bh * 0.62 + 16 + k * 16, bw - 36 - k * 14, 6); ctx.set_source_rgba(0.55, 0.53, 0.48, a); ctx.fill()
    ctx.rectangle(bw * 0.22, -bh + 10, 7, bh * 0.5); ctx.set_source_rgba(1, 1, 1, 0.35 * a); ctx.fill()
    ctx.restore()

# ---------------- the morphing shape ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(25) - 0.08, 'num', CX, 260, 430, 150, 75, OLIVE[:3]),
    (T(27) - 0.08, 'wordmark', CX, 260, 1000, 400, 40, CREAM[:3]),
    (T(33) - 0.08, 'bottles', CX, 260, 1000, 384, 36, CREAM[:3]),
    (T(45) - 0.08, 'sq', CX, 260, 548, 440, 36, OLIVE[:3]),
    (T(55) - 0.08, 'photo', CX, 260, 656, 440, 36, OLIVE[:3]),
    (T(68) - 0.08, 'squeeze', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(86) - 0.08, 'andrew', CX, 260, 616, 440, 36, OLIVE[:3]),
    (T(92) - 0.08, 'idea', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(104) - 0.08, 'traits', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(115) - 0.08, 'same', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(160) - 0.08, 'quiz', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(178) - 0.08, 'glass', CX, 260, 830, 440, 36, GREEN[:3]),
    (T(190) - 0.08, 'ext', CX, 260, 1000, 440, 40, OLIVE[:3]),
    (T(203) - 0.08, 'usa', CX, 260, 1000, 440, 40, GREEN[:3]),
    (T(217) - 0.08, 'shelf', CX, 260, 1000, 440, 40, CREAM[:3]),
    (T(257) - 0.08, 'value', CX, 260, 1000, 440, 40, CREAM[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 440, 1000                                 # my eyes sit at y~650-700 in both takes
SHAPE_ON, SHAPE_OFF = STATES[0][0], DUR + 10
def shape_geo(t):
    keys = []
    for k in range(8):
        ev = [(s[0], (s[2], s[3], s[4], s[5], s[6], *s[7])[k]) for s in STATES[1:]]
        v0 = (STATES[0][2], STATES[0][3], STATES[0][4], STATES[0][5], STATES[0][6], *STATES[0][7])[k]
        keys.append(track(t, ev, v0, w=12.0, zeta=0.86))
    return keys
def state_alpha(t, i):
    a = STATES[i][0]; b = STATES[i + 1][0] if i + 1 < len(STATES) else SHAPE_OFF
    return c01((t - a - 0.06) / 0.20) * (1 - c01((t - b) / 0.12))

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'num':
        ctx.arc(80, h / 2, 52, 0, 2 * math.pi); rgba(ctx, LIME, a); ctx.fill()
        mark(ctx, 'olive.png', 80, h / 2 + 2, 66, OLIVE, a)
        put(ctx, CS('Nº 1', 96, CREAM, 'Medium'), 160, h / 2 + 2 + lift, alpha=a, ax=0)
    elif name == 'wordmark':
        k = eo(prog(t, st0 + 0.08, 0.55))
        mark(ctx, 'wordmark.png', w / 2, 168 + lift, 820, OLIVE, a, reveal=k)
        put(ctx, CS('Olive oil the way it should be.', 50, OLIVE), w / 2, 330 + lift, alpha=a * eo(prog(t, st0 + 0.45, 0.4)))
    elif name == 'bottles':
        paint_img(ctx, 'cap6.png', (0, 60, 2778, 1130), 0, 0, w, h, a, lift)
    elif name == 'sq':
        paint_clip(ctx, 'sq', t, st0 + 0.06, 0, 0, w, h, a, lift)
    elif name == 'photo':
        paint_img(ctx, 'cap7.png', None, 0, 0, w, h, a, lift)
        k = pop(t, T(64) - 0.06)                                               # "ve, eso es chévere" sticker
        if k > 0.001:
            ctx.save(); ctx.translate(200, h - 70); ctx.rotate(-0.08); ctx.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
            pill(ctx, 0, 0, MX('¡ESO ES CHÉVERE!', 34), a * c01(k * 1.6), h=72); ctx.restore()
    elif name == 'squeeze':
        sq = 0.85 * pulse(t, T(73) - 0.08, 0.5) + pulse(t, T(79) - 0.06, 0.55)    # "squish" / "apretar"
        sway = 0.06 * math.sin((t - st0) * 2.2)
        bx, by = 300, 26
        graza_bottle(ctx, bx, by, 0.80, a, squish=sq, rot=math.pi + sway)        # upside down, nozzle pointing at the plate
        nx, ny = bx + math.sin(sway) * 300 * 0.8, by + 300 * 0.80 * math.cos(sway) + 8
        rgba(ctx, OLIVE, a * 0.9); ctx.save(); ctx.scale(1, 0.22); ctx.arc(bx, (h - 34) / 0.22, 120, 0, 2 * math.pi); ctx.restore()
        ctx.set_line_width(4); ctx.stroke()
        for t0 in (T(79) + 0.05, T(80) - 0.1, T(81), T(82), T(84)):               # drops when I say "donde sale el aceite"
            u = (t - t0) / 0.42
            if 0 < u < 1:
                dy = ny + (h - 40 - ny) * u * u
                ctx.save(); ctx.translate(nx, dy); ctx.scale(1, 1.25)
                ctx.arc(0, 0, 11, 0, 2 * math.pi); rgba(ctx, C(196, 170, 40), a); ctx.fill(); ctx.restore()
        pud = eo(prog(t, T(79) + 0.4, 0.8))
        if pud > 0:
            ctx.save(); ctx.scale(1, 0.22); ctx.arc(bx, (h - 34) / 0.22, 70 * pud, 0, 2 * math.pi); ctx.restore(); rgba(ctx, C(196, 170, 40), a * 0.9); ctx.fill()
        k = pop(t, T(73) - 0.06)
        put(ctx, MX('*SQUISH*', 30, MUTE), bx + 150, 120 - 10 * k, alpha=a * c01(k * 1.5) * (1 - c01((t - T(79)) / 0.2)))
        k2 = pop(t, T(79) - 0.04)
        put(ctx, MX('*SQUEEZE*', 30, MUTE), bx + 150, 120 - 10 * k2, alpha=a * c01(k2 * 1.5))
        put(ctx, MX('*DRIP*', 26, MUTE), bx + 110, h - 110, alpha=a * c01((t - T(80)) / 0.2))
        put(ctx, CS('Se aprieta', 92, OLIVE, 'Regular'), 590, 170 + lift, alpha=a, ax=0)
        put(ctx, CS('como un shampoo.', 60, OLIVE, 'Regular'), 592, 262 + lift, alpha=a * eo(prog(t, st0 + 0.35, 0.4)), ax=0)
    elif name == 'pizza':
        paint_clip(ctx, 'pizza', t, st0 + 0.06, 0, 0, w, h, a, lift)
    elif name == 'andrew':
        paint_img(ctx, 'dsc.jpg', (300, 40, 1660, 1010), 0, 0, w, h, a, lift)
        k = pop(t, T(87) + 0.05)
        pill(ctx, w / 2, h - 52 + 14 * (1 - k), MX('ANDREW BENIN · FUNDADOR', 26), a * c01(k * 1.6), h=60)
    elif name == 'idea':
        tw_, th_ = 440, 314; tx, ty = 40, 36
        rr(ctx, tx, ty, tw_, th_, 26); ctx.save(); ctx.clip(); paint_clip(ctx, 'soap', t, st0 + 0.06, tx, ty, tw_, th_, a, lift); ctx.restore()
        put(ctx, MX('SHAMPOO', 30, OLIVE), tx + tw_ / 2, ty + th_ + 40, alpha=a)
        k = eio(prog(t, T(98) - 0.1, 0.5))                                     # "exprimía el shampoo" -> arrow draws -> the squeeze bottle
        if k > 0:
            ctx.move_to(520, h / 2 - 22); ctx.line_to(520 + 110 * k, h / 2 - 22); rgba(ctx, OLIVE, a); ctx.set_line_width(6); ctx.stroke()
            if k > 0.95:
                ctx.move_to(612, h / 2 - 42); ctx.line_to(634, h / 2 - 22); ctx.line_to(612, h / 2 - 2); ctx.stroke()
        kb = pop(t, T(99) - 0.05)
        sq = pulse(t, T(100) - 0.02, 0.5)
        if kb > 0.001:
            graza_bottle(ctx, 810, 340 + 30 * (1 - kb), 0.86 * (0.7 + 0.3 * kb), a * c01(kb * 1.5), squish=sq)
            put(ctx, MX('ACEITE DE OLIVA', 30, OLIVE), 810, ty + th_ + 40, alpha=a * c01(kb * 1.5))
    elif name in ('traits', 'quiz'):
        mark(ctx, 'wordmark.png', 210, 74 + lift, 230, OLIVE, a)
        if name == 'traits':
            put(ctx, CS('Una marca', 100, OLIVE), 210, 200 + lift, alpha=a)
            put(ctx, CS('que da ganas', 64, OLIVE), 210, 300 + lift, alpha=a * eo(prog(t, st0 + 0.3, 0.4)))
            put(ctx, CS('de comprar.', 64, OLIVE), 210, 362 + lift, alpha=a * eo(prog(t, st0 + 0.4, 0.4)))
            items = [(T(109) - 0.08, 'ASPIRACIONAL'), (T(110) - 0.08, 'BONITA'), (T(113) - 0.08, 'CON ESENCIA')]
            clicks = [None, None, None]
        else:
            put(ctx, CS('¿Y si le', 100, OLIVE), 210, 200 + lift, alpha=a)
            put(ctx, CS('metemos…?', 100, OLIVE), 210, 300 + lift, alpha=a * eo(prog(t, st0 + 0.25, 0.4)))
            items = [(T(167) - 0.1, 'TASTE'), (T(171) - 0.1, 'BRAND'), (T(176) - 0.1, 'NARRATIVA')]
            clicks = [it[0] + 0.32 for it in items]
        for j, (t0, label) in enumerate(items):
            k = pop(t, t0)
            if k <= 0.001: continue
            px, py, pw, ph = 470, 52 + j * 116, 480, 92
            on = c01((t - clicks[j]) / 0.12) if clicks[j] else 0
            yy = py + 26 * (1 - k)
            rr(ctx, px, yy, pw, ph, ph / 2)
            fill = tuple(LIME[i] + (OLIVE[i] - LIME[i]) * on for i in range(3)) + (1,)
            rgba(ctx, fill, a * c01(k * 1.6)); ctx.fill_preserve(); rgba(ctx, OLIVE, a * c01(k * 1.6)); ctx.set_line_width(3); ctx.stroke()
            put(ctx, MX(label, 36, OLIVE), px + pw / 2, yy + ph / 2 + 1, alpha=a * c01(k * 1.6) * (1 - on))
            put(ctx, MX(label, 36, CREAM), px + pw / 2, yy + ph / 2 + 1, alpha=a * on)
            if on: check(ctx, px + pw - 50, yy + ph / 2, 30, LIME, a, k=eo(prog(t, clicks[j], 0.25)))
        if name == 'quiz':                                                    # cursor travels pill to pill and clicks each
            if t > items[0][0] + 0.1:
                tgt = [(it[0] + 0.1, (470 + 380, 52 + j * 116 + 60)) for j, it in enumerate(items)]
                cx_ = track(t, [(a_, p[0]) for a_, p in tgt], 980, w=11.0, zeta=0.9)
                cy_ = track(t, [(a_, p[1]) for a_, p in tgt], 470, w=11.0, zeta=0.9)
                press = max(math.sin(math.pi * c01((t - c + 0.1) / 0.2)) for c in clicks)
                cursor(ctx, cx_, cy_, a * c01((t - items[0][0] - 0.1) / 0.2), press)
    elif name == 'same':
        n = 7; xs = [95 + j * 135 for j in range(n)]
        bounce = pulse(t, T(140) - 0.06, 0.4) + pulse(t, T(141) - 0.04, 0.4)   # "todas son iguales": all hop together
        swap = pop(t, T(152) - 0.1, zeta=0.7)                                   # "y eso, los manes de Graza…": one becomes Graza
        for j, x in enumerate(xs):
            k = pop(t, st0 + 0.1 + 0.07 * j)
            if k <= 0.001: continue
            dim = 1 - 0.6 * swap if j != 3 else 1
            if j == 3 and swap > 0.02:
                graza_bottle(ctx, x, 372, 0.78 * (0.6 + 0.4 * swap), a * c01(swap * 2), squish=pulse(t, T(156) - 0.05, 0.4))
                plain_bottle(ctx, x, 372 - 20 * bounce, 1.0, a * (1 - c01(swap * 2)))
            else:
                plain_bottle(ctx, x, 372 + 40 * (1 - k) - 20 * bounce, 1.0, a * c01(k * 1.5) * dim)
        ctx.rectangle(30, 374, w - 60, 6); rgba(ctx, OLIVE, a * 0.85); ctx.fill()
        caps = [(T(116) - 0.06, 'MARCAS TRADICIONALES'), (T(140) - 0.06, 'TODAS IGUALES'), (T(143) - 0.06, 'MISMA BOTELLA DE VIDRIO'),
                (T(147) - 0.06, 'MISMO COLOR'), (T(149) - 0.06, 'ABSOLUTAMENTE TODO'), (T(152) - 0.1, 'GRAZA')]
        cur = [c for c in caps if t >= c[0]]
        if cur:
            t0, lbl = cur[-1]; k = pop(t, t0)
            pill(ctx, w / 2, 412, MX(lbl, 26, OLIVE if lbl != 'GRAZA' else CREAM), a * c01(k * 1.6),
                 fill=CREAM if lbl != 'GRAZA' else OLIVE, h=46)
    elif name == 'glass':
        paint_img(ctx, 'cap4.png', (0, 60, 2538, 1290), 0, 0, w, h, a, lift)
    elif name == 'ext':
        ts = [st0 + 0.08, T(194) - 0.08, T(199) - 0.08]                         # papas · mayonesa · martini, one per beat
        for j, (nm, t0) in enumerate(zip(('chips', 'mayo', 'can'), ts)):
            k = pop(t, t0)
            if k <= 0.001: continue
            x0, y0, tw_, th_ = 34 + j * 320, 30, 292, 380
            s = 0.85 + 0.15 * k
            ctx.save(); ctx.translate(x0 + tw_ / 2, y0 + th_ / 2 + 30 * (1 - k)); ctx.scale(s, s); ctx.translate(-tw_ / 2, -th_ / 2)
            rr(ctx, 0, 0, tw_, th_, 24); ctx.save(); ctx.clip(); paint_clip(ctx, nm, t, t0, 0, 0, tw_, th_, a * c01(k * 1.5)); ctx.restore()
            ctx.restore()
    elif name == 'usa':
        k = pop(t, st0 + 0.1)
        asterisk(ctx, w / 2 - 250, 92, 14, OLIVE, a, rot=t * 1.2); asterisk(ctx, w / 2 + 250, 92, 14, OLIVE, a, rot=-t * 1.2)
        put(ctx, MX('CONSUMER BRAND', 34, OLIVE), w / 2, 92, alpha=a * c01(k * 1.6))
        put(ctx, CS('De los más grandes', 112, OLIVE), w / 2, 220 + lift, alpha=a)
        k2 = pop(t, T(215) - 0.08)
        put(ctx, CS('de Estados Unidos.', 80, OLIVE), w / 2, 330 + 18 * (1 - k2), alpha=a * c01(k2 * 1.6))
    elif name == 'shelf':
        rows = [(214, C(190, 186, 176), C(160, 156, 146), 'can'), (408, C(205, 198, 186), C(176, 170, 158), 'box')]
        hero = (0, 4)
        diff = pop(t, T(255) - 0.06, zeta=0.7)                                  # "¿qué pasa si yo lo haría diferente?"
        hop = pulse(t, T(248) - 0.04, 0.35) + pulse(t, T(249) - 0.02, 0.35)     # "todo igual": everything hops in sync
        for r_, (by, body, band, kind) in enumerate(rows):
            ctx.rectangle(30, by, w - 60, 8); rgba(ctx, OLIVE, a * 0.85); ctx.fill()
            for j in range(9):
                x = 70 + j * 107
                k = pop(t, st0 + 0.1 + 0.05 * j + 0.2 * r_)
                if k <= 0.001: continue
                is_hero = (r_, j) == hero
                dim = 1 - 0.5 * diff if not is_hero else 1
                sc = 1 + (0.22 * diff if is_hero else 0)
                bh_ = 118 if kind == 'can' else 104; bw_ = 62 if kind == 'can' else 78
                ctx.save(); ctx.translate(x, by - 16 * hop + 30 * (1 - k)); ctx.scale(sc, sc)
                col = tuple(body[i] + (LIME[i] - body[i]) * (diff if is_hero else 0) for i in range(3)) + (1,)
                bcol0 = tuple(band[i] + (OLIVE[i] - band[i]) * (diff if is_hero else 0) for i in range(3)) + (1,)
                rr(ctx, -bw_ / 2, -bh_, bw_, bh_, 12 if kind == 'can' else 6); rgba(ctx, col, a * c01(k * 1.5) * dim); ctx.fill()
                if kind == 'can': rr(ctx, -bw_ / 2 + 8, -bh_ - 10, bw_ - 16, 12, 4); rgba(ctx, bcol0, a * c01(k * 1.5) * dim); ctx.fill()
                bcol = tuple(band[i] + (OLIVE[i] - band[i]) * (diff if is_hero else 0) for i in range(3)) + (1,)
                ctx.rectangle(-bw_ / 2, -bh_ * 0.62, bw_, bh_ * 0.26); rgba(ctx, bcol, a * c01(k * 1.5) * dim); ctx.fill()
                if is_hero and diff > 0.02: mark(ctx, 'olive.png', 0, -bh_ * 0.49, 26, LIME, a * diff)
                ctx.restore()
        k = pop(t, T(237) - 0.06)
        put(ctx, MX('VITRINA DEL SUPERMERCADO', 24, MUTE), 40, 26, alpha=a * c01(k * 1.6), ax=0)
        k = pop(t, T(245) - 0.06)
        put(ctx, MX('¿POR QUÉ TODO ES IGUAL?', 24, OLIVE), w - 40, 26, alpha=a * c01(k * 1.6) * (1 - diff), ax=1)
        put(ctx, MX('¿Y SI LO HAGO DIFERENTE?', 24, OLIVE), w - 40, 26, alpha=a * c01(diff * 1.6), ax=1)
    elif name == 'value':
        mark(ctx, 'olive.png', w / 2, 92 + lift, 96, OLIVE, a)
        put(ctx, CS('La verdadera oportunidad:', 66, OLIVE), w / 2, 196 + lift, alpha=a * eo(prog(t, st0 + 0.15, 0.4)))
        tt = CS('crear valor.', 140, OLIVE, 'Medium')
        k = eio(prog(t, T(266) - 0.05, 0.55))
        if k > 0:
            rr(ctx, w / 2 - tt[4] / 2 - 14, 268, (tt[4] + 28) * k, 104, 18); rgba(ctx, LIME, a); ctx.fill()
        put(ctx, tt, w / 2, 316 + lift, alpha=a * eo(prog(t, T(265) - 0.1, 0.35)))

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = c01(spring(t - SHAPE_ON, w=11.0, zeta=0.9))
    if appear <= 0.01: return
    sc = 0.86 + 0.14 * appear
    f = min(1.0, BAND_H / h, BAND_W / w)                                 # always above my eyes
    cy = BAND_TOP + h * f / 2
    ctx.save(); ctx.translate(cx, cy + 40 * (1 - appear)); ctx.scale(sc * f, sc * f); ctx.translate(-w / 2, -h / 2)
    soft_shadow(ctx, 0, 0, w, h, r, appear)
    rr(ctx, 0, 0, w, h, r); ctx.set_source_rgba(fr, fg, fb, appear); ctx.fill()
    rr(ctx, 0, 0, w, h, r); ctx.save(); ctx.clip()
    for i, st in enumerate(STATES):
        a = state_alpha(t, i) * appear
        if a <= 0.002: continue
        lift = 14 * (1 - c01((t - st[0] - 0.06) / 0.25))
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore(); ctx.restore()

# ---------------- title (over my live face, during the hook) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['Marcas', 'que', 'tienes'], ['que', 'seguir', 'si'], ['trabajas', 'en'], ['marketing']]
def title(ctx, t):
    if t >= TITLE_END: return
    fade = 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    n = min(len(LABEL), int(max(0, t - 0.1) / 0.025))
    if n > 0:
        txt = LABEL[:n] if n < len(LABEL) else (LABEL if int(t * 2.2) % 2 == 0 else LABEL[:-1])
        put(ctx, fx.T_(txt, MONO, 38, CREAM, shadow=6, shadow_a=200), 70, 1050, alpha=fade, ax=0)
    t0 = 0.1 + 0.025 * len(LABEL); k = 0
    for li, line in enumerate(TITLE):
        x = 70; y = 1160 + li * 122
        for wd in line:
            col = LIME if wd == 'marketing' else CREAM
            tt = CS(wd, 136, col, 'Medium', cond=0.82, shadow=10, shadow_a=190)
            e = spring(t - (t0 + 0.07 * k), w=12.0, zeta=0.86)
            put(ctx, tt, x, y + 30 * (1 - e), alpha=c01(e * 1.4) * fade, ax=0)
            x += tt[4] + 22; k += 1

# ---------------- subtitles (simple, Graza pill) ----------------
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
    tt = CS(line, 64, OLIVE, 'Medium', cond=0.84)
    sc = min(1.0, 900 / tt[4]); pw_, ph_ = (tt[4] + 64) * sc, 92 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); rgba(ctx, CREAM, 0.97 * e); ctx.fill_preserve()
    rgba(ctx, OLIVE, e); ctx.set_line_width(3); ctx.stroke()
    put(ctx, tt, W / 2, y + 2, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 10, W, 10); rgba(ctx, CREAM, 0.30); ctx.fill()
    ctx.rectangle(0, H - 10, W * c01(t / DUR), 10); rgba(ctx, LIME); ctx.fill()

# ---------------- frame ----------------
def render_frame(fr16, t, fi):
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))               # HLG signal, full frame, no camera movement
    sdr = full.copy(); hdr = full.copy()
    arr, surf, ctx = fx.new_layer(); draw_shape(ctx, t)
    title(ctx, t); subtitles(ctx, t); progress(ctx, t); surf.flush(); fx.layer_over(sdr, hdr, arr)
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
    eh = hdr_encoder(sys.argv[2], os.path.join(HERE, 'mix.wav'))          # HDR only (house rule since 13 oct 2026)
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t, fi)
        eh.stdin.write(np.ascontiguousarray(fx.to16(hdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    eh.stdin.close(); eh.wait()
    print('done', sys.argv[2])

if __name__ == '__main__':
    main()
