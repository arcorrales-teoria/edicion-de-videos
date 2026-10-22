"""IMG_9010 + IMG_9011 · Instinct — "Tu asistente personal ahora vive en WhatsApp". 1.05x, voice only (no SFX / music).
Same format as the IMG_9008 reel: me cut out in FRONT (Apple Vision masks), everything BEHIND me on Instinct's warm off-white,
one shape that morphs between states (springs on x, y, w, h, radius, colour) while its content swaps with a short fade-lift.
Instinct look: white/ink, serif headings (New York ~ their serif), sand highlight, their stick-figure logo, WhatsApp chat in its
own dark theme. Every interaction is animated (typing dots, bubbles, notifications, app links, flight route, waitlist, invite).
No camera movement. Simple subtitles. Blue progress bar. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit17 as E; os.chdir(_cwd)

SPEED = 1.05
GF = os.path.expanduser('~/Library/Fonts/')
G_REG, G_MED, G_SEMI, G_BOLD = GF + 'Geist-Regular.otf', GF + 'Geist-Medium.otf', GF + 'Geist-SemiBold.otf', GF + 'Geist-Bold.otf'
G_MONO = GF + 'GeistMono-Medium.otf'
CANVAS = (0xF6, 0xF3, 0xEF); INK = (0.07, 0.07, 0.07, 1); MUTE = (0.45, 0.45, 0.43, 1); WHITE = (1, 1, 1, 1)
BLUE = (0x2F / 255, 0x6B / 255, 0xFF / 255, 1)
REF = os.path.join(HERE, 'ref')
NY = '/System/Library/Fonts/NewYork.ttf'
SAND = (0xE6 / 255, 0xDB / 255, 0xD1 / 255, 1)
WA_BG = (0x0B / 255, 0x14 / 255, 0x1A / 255); WA_IN = (0x20 / 255, 0x2C / 255, 0x33 / 255, 1); WA_OUT = (0x00 / 255, 0x5C / 255, 0x4B / 255, 1); WA_GREEN = (0x25 / 255, 0xD3 / 255, 0x66 / 255, 1)

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

def SX(txt, size, col=INK, var='Semibold'):
    key = ('NY', txt, size, col, var)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(NY, size); f.set_variation_by_name(var)
    asc, desc = f.getmetrics(); tw = max(1, f.getlength(txt)); pad = 12 + int(size * 0.25)
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=tuple(int(c * 255) for c in col[:3]) + (255,))
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
FIX = {10: 'Instinct', 17: '', 18: 'que', 21: 'un', 22: 'agente', 96: 'Andrés,', 104: 'eso,', 142: 'dijo:', 144: 'búscame', 150: 'compró', 155: 'pero', 156: 'lo consiguió', 159: 'mandó', 185: 'hace.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.35
TITLE_END = 5.0

# ---------------- person: full frame <-> cut-out in front (the only image motion) ----------------
CUT_S = 0.62
MODE = [(TITLE_END - 0.05, 1.0), (T(165) - 0.08, 0.0), (T(177) - 0.08, 1.0)]
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
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (TITLE_END - 0.05, 'site', CX, 430, 900, 600, 44, (1, 1, 1)),
    (T(27) - 0.08, 'contact', CX, 400, 760, 170, 85, (0.07, 0.07, 0.07)),
    (T(36) - 0.08, 'hub', CX, 420, 980, 380, 56, (1, 1, 1)),
    (T(52) - 0.08, 'notifs', CX, 420, 960, 384, 48, (1, 1, 1)),
    (T(64) - 0.08, 'inbox', CX, 420, 960, 384, 44, (1, 1, 1)),
    (T(86) - 0.08, 'chat1', CX, 430, 1000, 400, 44, WA_BG),
    (T(123) - 0.08, 'flight', CX, 400, 960, 400, 48, (1, 1, 1)),
    (T(140) - 0.08, 'chat2', CX, 430, 1000, 400, 44, WA_BG),
    (T(177) - 0.08, 'g1', CX, 400, 620, 150, 75, (0.07, 0.07, 0.07)),
    (T(180) - 0.08, 'g2', CX, 400, 760, 150, 75, (0.07, 0.07, 0.07)),
    (T(186) - 0.08, 'signin', CX, 430, 900, 400, 44, (1, 1, 1)),
    (T(205) - 0.08, 'comment', CX, 400, 880, 200, 60, (1, 1, 1)),
    (T(210) - 0.08, 'invite', CX, 420, 900, 384, 48, (1, 1, 1)),
]
BAND_TOP, BAND_H, BAND_W = 46, 384, 1000
SHAPE_ON, SHAPE_OFF = STATES[0][0], DUR + 10
HIDE = (T(165) - 0.08, T(177) - 0.08)                                    # full-screen beat: the shape steps away
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

_img = {}
def img(name, crop=None):
    key = (name, crop)
    if key not in _img:
        im = Image.open(os.path.join(REF, name)).convert('RGBA')
        if crop: im = im.crop(crop)
        _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_img(ctx, name, crop, x, y, w, h, alpha, lift=0.0, fit='cover'):
    if alpha <= 0.002: return
    im, (surf, _b) = img(name, crop)
    s = max(w / im.width, h / im.height) if fit == 'cover' else min(w / im.width, h / im.height)
    ctx.save(); ctx.translate(x + w / 2, y + h / 2 + lift); ctx.scale(s, s)
    ctx.set_source_surface(surf, -im.width / 2, -im.height / 2); ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha); ctx.restore()
def logo(ctx, x, y, h, a):
    paint_img(ctx, 'logo.png', None, x - h * 0.23, y - h / 2, h * 0.46, h, a, fit='contain')

def ease_in(t, t0, d=0.35): return spring(t - t0, w=12.0, zeta=0.86)
def dots(ctx, x, y, t, a, col=(0.75, 0.78, 0.8)):
    for k in range(3):
        ph = 0.5 + 0.5 * math.sin(t * 9 - k * 0.9)
        ctx.arc(x + k * 22, y - 5 * ph, 7, 0, 2 * math.pi); ctx.set_source_rgba(col[0], col[1], col[2], a * (0.45 + 0.55 * ph)); ctx.fill()
def bubble(ctx, x, y, text_lines, a, out=False, maxw=760, t_type=None, t=0.0, size=36):
    """WhatsApp bubble; text_lines types in from t_type if given"""
    if a <= 0.002: return 0
    lines = text_lines
    if t_type is not None:
        total = sum(len(l) for l in lines); n = int(total * c01((t - t_type) / max(0.05, 0.028 * total)))
        out_l, left = [], n
        for l in lines: out_l.append(l[:max(0, left)]); left -= len(l)
        lines = out_l
    tts = [TX(l or ' ', G_REG, size, WHITE) for l in text_lines]
    w = min(maxw, max(tt[4] for tt in tts) + 44); h = 26 + len(text_lines) * (size + 12)
    bx = x - w if out else x
    rr(ctx, bx, y, w, h, 18); rgba(ctx, WA_OUT if out else WA_IN, a); ctx.fill()
    for k, l in enumerate(lines):
        if l: put(ctx, TX(l, G_REG, size, WHITE), bx + 22, y + 13 + (size + 12) * k + (size + 12) / 2, alpha=a, ax=0)
    return h

def chat_scroll(ctx, w, h, a, content_h):
    """clip below the header and scroll up if the stacked bubbles are taller than the window"""
    off = max(0.0, content_h - (h - 20))
    ctx.save(); ctx.rectangle(0, 110, w, h - 110); ctx.clip(); ctx.translate(0, -off)
def chat_header(ctx, w, a, status='en línea'):
    ctx.rectangle(0, 0, w, 110); ctx.set_source_rgba(0x20 / 255, 0x2C / 255, 0x33 / 255, a); ctx.fill()
    ctx.arc(70, 55, 34, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    ctx.rectangle(68, 36, 4, 38); ctx.set_source_rgba(0, 0, 0, a); ctx.fill()
    put(ctx, TX('Instinct', G_SEMI, 34, WHITE), 124, 42, alpha=a, ax=0)
    put(ctx, TX(status, G_REG, 24, (0.62, 0.68, 0.7, 1)), 124, 78, alpha=a, ax=0)

APPS = [('Gmail', (0.92, 0.26, 0.21)), ('Calendar', (0.26, 0.52, 0.96)), ('WhatsApp', (0.15, 0.83, 0.4)), ('Drive', (0.98, 0.74, 0.02)),
        ('Slack', (0.29, 0.08, 0.29)), ('Notion', (0.07, 0.07, 0.07))]
def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'site':
        paint_img(ctx, 'site.png', (0, 0, 1290, 1000), 0, 0, w, h, a, lift)
        k = eo(prog(t, T(10) if T(10) > st0 else st0 + 0.3, 0.5))           # "Text Instinct" CTA underline grows
    elif name == 'contact':
        ctx.arc(85, h / 2, 50, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
        logo(ctx, 85, h / 2 + 2, 74, a)
        put(ctx, SX('Instinct', 52, WHITE), 160, h / 2 - 18 + lift, alpha=a, ax=0)
        put(ctx, TX('tu asistente · en WhatsApp', G_REG, 26, (0.7, 0.7, 0.7, 1)), 162, h / 2 + 30 + lift, alpha=a, ax=0)
        k = spring(t - (T(31) - 0.05), w=12.0, zeta=0.8)                   # "como un contacto": + Añadir contacto -> check
        bx, by = w - 110, h / 2
        ctx.arc(bx, by, 44, 0, 2 * math.pi); rgba(ctx, WA_GREEN, a); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(6)
        if k < 0.5:
            ctx.move_to(bx - 16, by); ctx.line_to(bx + 16, by); ctx.move_to(bx, by - 16); ctx.line_to(bx, by + 16)
        else:
            ctx.move_to(bx - 15, by + 1); ctx.line_to(bx - 4, by + 12); ctx.line_to(bx + 16, by - 12)
        ctx.stroke()
    elif name == 'hub':
        cx, cy = w / 2, h / 2 + 6
        for j, (nm, col) in enumerate(APPS):
            ang = -math.pi / 2 + (j + 0.5) * 2 * math.pi / len(APPS); R = 1
            k = spring(t - (T(46) - 0.1 + 0.16 * j), w=12.0, zeta=0.8)
            if k <= 0.001: continue
            px, py = cx + 360 * math.cos(ang) * min(1, k), cy + 120 * math.sin(ang) * min(1, k)
            ctx.move_to(cx, cy); ctx.line_to(px, py); ctx.set_source_rgba(0, 0, 0, 0.12 * a); ctx.set_line_width(3); ctx.stroke()
            pp = c01((t - (T(46) + 0.5 + 0.16 * j)) % 1.4 / 0.7)                   # data pulse travelling to the hub
            if t > T(46) + 0.5 + 0.16 * j:
                ctx.arc(px + (cx - px) * pp, py + (cy - py) * pp, 7, 0, 2 * math.pi); ctx.set_source_rgba(col[0], col[1], col[2], a * (1 - pp)); ctx.fill()
            tw = 150; rr(ctx, px - tw / 2, py - 34, tw, 68, 34); ctx.set_source_rgba(1, 1, 1, a); ctx.fill_preserve()
            ctx.set_source_rgba(0, 0, 0, 0.10 * a); ctx.set_line_width(2); ctx.stroke()
            ctx.arc(px - tw / 2 + 30, py, 10, 0, 2 * math.pi); ctx.set_source_rgba(col[0], col[1], col[2], a); ctx.fill()
            put(ctx, TX(nm, G_MED, 26, INK), px - tw / 2 + 48, py + 1, alpha=a * c01(k * 1.5), ax=0)
        ctx.arc(cx, cy, 66, 0, 2 * math.pi); ctx.set_source_rgba(SAND[0], SAND[1], SAND[2], a); ctx.fill()
        logo(ctx, cx, cy + 2, 92, a)
    elif name == 'notifs':
        items = [(T(55) - 0.1, 'Recordatorio', 'Reunión con el equipo a las 3:00 p. m.'), (T(58) - 0.1, 'Notificación', 'Te llegó un correo importante'),
                 (T(60) - 0.1, 'Instinct', '¿Te ayudo a responderlo?')]
        for j, (t0, ttl, body) in enumerate(items):
            k = spring(t - t0, w=12.0, zeta=0.8)
            if k <= 0.001: continue
            y = 22 + j * 116 + 30 * (1 - k)
            rr(ctx, 30, y, w - 60, 104, 28); ctx.set_source_rgba(0.965, 0.955, 0.945, a * c01(k * 1.4)); ctx.fill()
            ctx.arc(96, y + 52, 30, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
            logo(ctx, 96, y + 53, 44, a * c01(k * 1.4))
            put(ctx, TX(ttl, G_SEMI, 30, INK), 146, y + 36, alpha=a * c01(k * 1.4), ax=0)
            put(ctx, TX(body, G_REG, 28, MUTE), 146, y + 74, alpha=a * c01(k * 1.4), ax=0)
            put(ctx, TX('ahora', G_REG, 24, MUTE), w - 60, y + 36, alpha=a * c01(k * 1.4), ax=1)
    elif name == 'inbox':
        put(ctx, TX('Correo', G_SEMI, 34, INK), 46, 42 + lift, alpha=a, ax=0)
        mails = [('Equipo Lab10', 'Inscripciones abiertas · cierran el viernes', True), ('Newsletter', 'Las noticias de la semana', False),
                 ('Banco', 'Tu extracto está listo', False), ('Universidad', 'Recordatorio: fecha límite de inscripción', True)]
        for j, (frm, sub, imp) in enumerate(mails):
            k = spring(t - (st0 + 0.15 + 0.1 * j), w=12.0, zeta=0.9)
            y = 82 + j * 74 + 20 * (1 - k); aa = a * c01(k * 1.4)
            hl = eo(prog(t, T(73) - 0.05, 0.4)) if imp else 0              # "importantes": the two important ones light up
            if hl > 0:
                rr(ctx, 24, y - 4, w - 48, 70, 16); ctx.set_source_rgba(SAND[0], SAND[1], SAND[2], aa * hl); ctx.fill()
            ctx.arc(54, y + 31, 8, 0, 2 * math.pi); rgba(ctx, BLUE if imp else (0.85, 0.85, 0.85, 1), aa); ctx.fill()
            put(ctx, TX(frm, G_SEMI if imp else G_MED, 28, INK), 78, y + 16, alpha=aa, ax=0)
            put(ctx, TX(sub, G_REG, 25, MUTE), 78, y + 48, alpha=aa, ax=0)
        k = eo(prog(t, T(75) - 0.05, 0.35))                                # "que no había leído" -> unread badge
        if k > 0:
            tg = TX('2 sin leer', G_SEMI, 26, WHITE); bw_ = tg[4] + 40
            rr(ctx, w - 46 - bw_, 20, bw_, 46, 23); rgba(ctx, BLUE, a * k); ctx.fill(); put(ctx, tg, w - 46 - bw_ / 2, 44, alpha=a * k)
    elif name in ('chat1', 'chat2'):
        status = 'escribiendo…' if name == 'chat1' and T(89) - 0.1 < t < T(95) - 0.1 else ('revisando tu correo…' if name == 'chat1' and t > T(110) - 0.1 else 'en línea')
        if name == 'chat2' and T(149) < t < T(156): status = 'buscando vuelos…'
        if name == 'chat1':
            ch = 140 + (76 if t >= T(95) - 0.1 else 64) + (138 if t >= T(97) - 0.1 else 0) + (124 if t >= T(105) - 0.1 else 0)
            ch_s = track(t, [(T(97) - 0.1, 140 + 76 + 138), (T(105) - 0.1, 140 + 76 + 138 + 124)], 140 + 76, w=12.0, zeta=0.9)
            chat_scroll(ctx, w, h, a, ch_s)
            y = 140
            if T(89) - 0.1 < t < T(95) - 0.1:
                rr(ctx, 30, y, 120, 64, 18); rgba(ctx, WA_IN, a); ctx.fill(); dots(ctx, 66, y + 34, t, a)
            if t >= T(95) - 0.1:
                k = spring(t - (T(95) - 0.1), w=13, zeta=0.8)
                y += bubble(ctx, 30, y + 16 * (1 - k), ['¡Hola Andrés!'], a * c01(k * 1.5)) + 14
            if t >= T(97) - 0.1:
                k = spring(t - (T(97) - 0.1), w=13, zeta=0.8)
                y += bubble(ctx, 30, y + 16 * (1 - k), ['Te recuerdo que tienes que', 'inscribirte al curso.'], a * c01(k * 1.5), t_type=T(97), t=t) + 14
            if t >= T(105) - 0.1:
                k = spring(t - (T(105) - 0.1), w=13, zeta=0.8)
                bubble(ctx, 30, y + 16 * (1 - k), ['Tienes hasta el viernes', '(fecha límite).'], a * c01(k * 1.5), t_type=T(105), t=t)
            ctx.restore(); chat_header(ctx, w, a, status)
        else:
            ch_s = track(t, [(T(149) - 0.1, 140 + 138 + 64), (T(156) - 0.1, 140 + 138 + 76 + 12), (T(160) - 0.1, 140 + 138 + 76 + 12 + 210)], 140 + 138, w=12.0, zeta=0.9)
            chat_scroll(ctx, w, h, a, ch_s)
            y = 140
            if t >= T(143) - 0.1:
                k = spring(t - (T(143) - 0.1), w=13, zeta=0.8)
                y += bubble(ctx, w - 30, y + 16 * (1 - k), ['Búscame los tiquetes más', 'baratos a San Francisco'], a * c01(k * 1.5), out=True) + 14
            if T(149) - 0.1 < t < T(156) - 0.1:
                rr(ctx, 30, y, 120, 64, 18); rgba(ctx, WA_IN, a); ctx.fill(); dots(ctx, 66, y + 34, t, a)
            if t >= T(156) - 0.1:
                k = spring(t - (T(156) - 0.1), w=13, zeta=0.8)
                y += bubble(ctx, 30, y + 16 * (1 - k), ['Listo, encontré estas opciones:'], a * c01(k * 1.5)) + 12
                rows = ['Opción 1 · 1 escala', 'Opción 2 · directo', 'Opción 3 · la más barata']
                for j, r_ in enumerate(rows):
                    kk = spring(t - (T(160) - 0.1 + 0.18 * j), w=13, zeta=0.85)
                    if kk <= 0.001: continue
                    yy = y + j * 70 + 12 * (1 - kk)
                    rr(ctx, 30, yy, 520, 58, 14); rgba(ctx, WA_IN, a * c01(kk * 1.5)); ctx.fill()
                    put(ctx, TX('✈', G_REG, 26, WHITE) if False else TX(r_, G_MED, 27, WHITE), 54, yy + 30, alpha=a * c01(kk * 1.5), ax=0)
                    if j == 2:
                        ctx.arc(520, yy + 29, 13, 0, 2 * math.pi); rgba(ctx, WA_GREEN, a * c01(kk * 1.5)); ctx.fill()
            ctx.restore()
        chat_header(ctx, w, a, status)
    elif name == 'flight':
        pass
        ax_, bx_, yb = 170, w - 170, 220
        put(ctx, SX('BOG', 84), ax_, yb + 90, alpha=a); put(ctx, SX('SFO', 84), bx_, yb + 90, alpha=a)
        put(ctx, TX('Bogotá', G_REG, 26, MUTE), ax_, yb + 150, alpha=a); put(ctx, TX('San Francisco', G_REG, 26, MUTE), bx_, yb + 150, alpha=a)
        k = eio(prog(t, T(130) - 0.1, 1.6))                                # route draws while I say "para irse a San Francisco"
        n = 60
        for i in range(int(n * k)):
            u = i / n; px = ax_ + (bx_ - ax_) * u; py = yb - math.sin(math.pi * u) * 130
            if i % 2 == 0: ctx.arc(px, py, 4, 0, 2 * math.pi); ctx.set_source_rgba(0, 0, 0, 0.35 * a); ctx.fill()
        u = k; px = ax_ + (bx_ - ax_) * u; py = yb - math.sin(math.pi * u) * 130
        ctx.arc(px, py, 14, 0, 2 * math.pi); rgba(ctx, INK, a); ctx.fill()
        kk = spring(t - (T(137) - 0.1), w=12, zeta=0.85)                    # "utilizando Instinct" stamp
        if kk > 0.001:
            tg = TX('reservado con Instinct', G_SEMI, 28, INK); bw_ = tg[4] + 90
            rr(ctx, w / 2 - bw_ / 2, h - 74, bw_, 56, 28); rgba(ctx, SAND, a * c01(kk * 1.5)); ctx.fill()
            logo(ctx, w / 2 - bw_ / 2 + 34, h - 46, 36, a * c01(kk * 1.5)); put(ctx, tg, w / 2 - bw_ / 2 + 60, h - 45, alpha=a * c01(kk * 1.5), ax=0)
    elif name in ('g1', 'g2'):
        txt = {'g1': '01 · Tu tiempo', 'g2': '02 · Lo que haces'}[name]
        put(ctx, TX(txt, G_SEMI, 52, WHITE), w / 2, h / 2 + 2 + lift * 0.6, alpha=a)
    elif name == 'signin':
        paint_img(ctx, 'signin.png', (70, 120, 900, 489), 0, 0, w, h, a, lift)
        k = spring(t - (T(197) - 0.1), w=12, zeta=0.85)                    # "lista de espera" -> pill drops in and gets clicked
        if k > 0.001:
            on = spring(t - (T(201) - 0.05), w=13, zeta=0.85)
            tg = TX('Unirme a la lista de espera', G_SEMI, 30, WHITE); tg2 = TX('Estás en la lista', G_SEMI, 30, INK)
            bw_ = 520; by_ = h - 96 + 20 * (1 - k)
            rr(ctx, w / 2 - bw_ / 2, by_, bw_, 76, 38); ctx.set_source_rgba(0.07 + 0.83 * on, 0.07 + 0.79 * on, 0.07 + 0.75 * on, a * c01(k * 1.5)); ctx.fill()
            put(ctx, tg, w / 2, by_ + 38, alpha=a * c01(k * 1.5) * (1 - c01(on * 2)))
            put(ctx, tg2, w / 2, by_ + 38, alpha=a * c01(on * 2 - 0.6))
            press = math.sin(math.pi * c01((t - T(201) + 0.12) / 0.2))
            cx_ = w / 2 + 150 + 120 * (1 - c01((t - T(197)) / 0.6)); cy_ = by_ + 50 + 60 * (1 - c01((t - T(197)) / 0.6))
            cursor(ctx, cx_, cy_, a * c01(k * 1.5), press)
    elif name == 'comment':
        n = int(len('WhatsApp') * c01((t - (T(209) - 0.15)) / 0.45))
        put(ctx, TX('Comenta', G_SEMI, 30, MUTE), 50, 50, alpha=a, ax=0)
        rr(ctx, 40, 80, w - 200, 84, 42); ctx.set_source_rgba(0.95, 0.94, 0.93, a); ctx.fill()
        txt = 'WhatsApp'[:n]
        tt = TX(txt or ' ', G_SEMI, 40, INK); put(ctx, tt, 80, 122, alpha=a, ax=0)
        if int(t * 2.4) % 2 == 0: ctx.rectangle(84 + (tt[4] if txt else 0), 100, 3, 44); rgba(ctx, BLUE, a); ctx.fill()
        sent = c01((t - (T(209) + 0.45)) / 0.15)
        ctx.arc(w - 100, 122, 42, 0, 2 * math.pi); rgba(ctx, BLUE if sent else (0.8, 0.8, 0.8, 1), a); ctx.fill()
        ctx.move_to(w - 100, 140); ctx.line_to(w - 100, 104); ctx.move_to(w - 114, 118); ctx.line_to(w - 100, 104); ctx.line_to(w - 86, 118)
        ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(5); ctx.stroke()
    elif name == 'invite':
        ctx.rectangle(0, 0, w, h); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
        logo(ctx, w / 2, 100 + lift, 120, a)
        put(ctx, SX('Tu invitación a Instinct', 50), w / 2, 222 + lift, alpha=a)
        put(ctx, TX('personalizada · para que lo uses hoy', G_REG, 28, MUTE), w / 2, 276 + lift, alpha=a)
        k = eo(prog(t, T(215) - 0.05, 0.5))
        tg = TX('Text Instinct  ›', NY, 40, INK) if False else SX('Text Instinct  ›', 40, INK, 'Regular')
        rr(ctx, w / 2 - tg[4] / 2 - 10, 336, (tg[4] + 20) * k, 28, 6); rgba(ctx, SAND, a); ctx.fill()
        put(ctx, tg, w / 2, 334, alpha=a)

def draw_shape(ctx, t):
    if t < SHAPE_ON: return
    cx, cy, w, h, r, fr, fg, fb = shape_geo(t)
    appear = spring(t - SHAPE_ON, w=11.0, zeta=0.9) * (1 - spring(t - HIDE[0], w=12.0, zeta=1.0)) + spring(t - HIDE[1], w=11.0, zeta=0.9)
    appear = c01(appear)
    if appear <= 0.01: return
    sc = 0.86 + 0.14 * appear
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
        draw_state(ctx, t, st[1], w, h, a, lift, st[0])
    ctx.restore(); ctx.restore()

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

def pair(ctx, t): pass
def follow(ctx, t): pass

# ---------------- title (over my live face) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['Tu', 'asistente'], ['personal', 'ahora'], ['vive', 'en'], ['WhatsApp']]
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

# ---------------- frame ----------------
CANVAS_F = np.array(CANVAS, np.float32) / 255
CANVAS_H = fx.srgb8_to_hlg(np.array(CANVAS, np.uint8)[None, None, :])[0, 0]
def render_frame(fr16, t, fi):
    m = mode(t)
    full = fx.resize_f(fr16, (0, 0, fx.SW, fx.SH), (W, H))               # HLG signal, full frame
    if LAYOUT == 'C':                                                     # my real room, full frame; graphics on top, above my eyes
        sdr = full.copy(); hdr = full.copy()
        arr, surf, ctx = fx.new_layer(); draw_shape(ctx, t); pair(ctx, t); follow(ctx, t)
        title(ctx, t); subtitles(ctx, t); progress(ctx, t); surf.flush(); fx.layer_over(sdr, hdr, arr)
        return sdr, hdr
    if m < 0.001:
        sdr = full.copy(); hdr = full.copy()
    else:
        sdr = np.empty((H, W, 3), np.float32); sdr[:] = CANVAS_F
        hdr = np.empty((H, W, 3), np.float32); hdr[:] = CANVAS_H
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
