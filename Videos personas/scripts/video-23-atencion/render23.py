"""IMG_9088 · Darshita Patankar ("DESIGN IS DEAD") and why attention is everything. 1.05x, voice only (DeepFilterNet3-cleaned).
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

# ---------------- Darshita's identity: plum-black, hot pink, glossy script, glowing serif, sparkles ----------------
NY = '/System/Library/Fonts/NewYork.ttf'
SCRIPT = os.path.join(HERE, 'fonts', 'Pacifico.ttf')
CLIPS = os.path.join(HERE, 'clips')
PLUM, HOT, BLUSH, ROSE = C(16, 5, 11), C(255, 46, 147), C(255, 214, 236), C(255, 140, 198)
def SER(txt, size, col=BLUSH, var='Medium', glow=True):
    """her subtitle serif (New York) with a soft pink glow"""
    key = ('S', txt, size, col, var, glow)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(NY, size); f.set_variation_by_name(var)
    asc, desc = f.getmetrics(); tw = max(1, f.getlength(txt)); pad = 14 + int(size * 0.35)
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if glow:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad, pad), txt, font=f, fill=(255, 46, 147, 200))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(max(4, size * 0.16))))
        d = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(d).text((pad, pad + 2), txt, font=f, fill=(40, 0, 20, 160))
        img.alpha_composite(d.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=tuple(int(c * 255) for c in col[:3]) + (255,))
    s, buf = fx.pil_surface(img); r = (s, buf, w, h, tw, asc); _tc[key] = r; return r
def GLOSS(txt, size):
    """glossy pink 3D script like her 'Design is Dead' lettering: deep magenta extrude, hot pink rim, pale pink gradient face, highlight"""
    key = ('GL', txt, size)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(SCRIPT, size)
    l, tp, rgt, bt = f.getbbox(txt); tw, th = rgt - l, bt - tp
    pad = int(size * 0.45); depth = max(4, int(size * 0.09)); sw = max(2, int(size * 0.05))
    w, h = int(tw + 2 * pad + depth), int(th + 2 * pad + depth)
    org = (pad - l, pad - tp)
    def mask(off=(0, 0), stroke=0):
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).text((org[0] + off[0], org[1] + off[1]), txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255); return m
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow = Image.new('RGBA', (w, h), (255, 46, 147, 0)); glow.putalpha(mask(stroke=sw).filter(ImageFilter.GaussianBlur(size * 0.12)).point(lambda v: int(v * 0.75)))
    out.alpha_composite(glow)
    for i in range(depth, 0, -1):                                              # extrude
        layer = Image.new('RGBA', (w, h), (110, 6, 58, 255)); layer.putalpha(mask((int(i * 0.7), i), stroke=sw)); out.alpha_composite(layer)
    rim = Image.new('RGBA', (w, h), (255, 46, 147, 255)); rim.putalpha(mask(stroke=sw)); out.alpha_composite(rim)
    grad = np.zeros((h, w, 4), np.uint8); yy = np.linspace(0, 1, h)[:, None]
    top, bot = np.array([255, 244, 250]), np.array([255, 150, 205])
    grad[..., :3] = (top[None, None, :] * (1 - yy[..., None]) + bot[None, None, :] * yy[..., None]).astype(np.uint8)
    face = Image.fromarray(grad); face.putalpha(mask()); out.alpha_composite(face)
    hl = Image.new('RGBA', (w, h), (255, 255, 255, 0)); hm = mask((0, -max(1, size // 40))).point(lambda v: int(v * 0.35)); hl.putalpha(Image.fromarray((np.asarray(hm) * (np.linspace(1, 0, h)[:, None] ** 3)).astype(np.uint8)))
    out.alpha_composite(hl)
    s, buf = fx.pil_surface(out); r = (s, buf, w, h, tw + depth, 0); _tc[key] = r; return r
def sparkle(ctx, x, y, r, a, t=0.0, ph=0.0):
    """her 4-point glint"""
    k = 0.65 + 0.35 * math.sin(t * 3.2 + ph)
    if a * k <= 0.01: return
    g = cairo.RadialGradient(x, y, 0, x, y, r * 1.6 * k); g.add_color_stop_rgba(0, 1, 0.85, 0.95, 0.55 * a * k); g.add_color_stop_rgba(1, 1, 0.4, 0.75, 0)
    ctx.arc(x, y, r * 1.6 * k, 0, 2 * math.pi); ctx.set_source(g); ctx.fill()
    for (dx, dy) in ((1, 0), (0, 1)):
        L = r * 2.2 * k; wd = r * 0.16 * k
        ctx.move_to(x - dx * L, y - dy * L); ctx.line_to(x + dy * wd, y + dx * wd); ctx.line_to(x + dx * L, y + dy * L); ctx.line_to(x - dy * wd, y - dx * wd); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.95 * a * k); ctx.fill()
def stage_bg(ctx, w, h, a, t):
    """plum-black with a pink bloom from below and a few glints"""
    g = cairo.RadialGradient(w / 2, h * 1.15, 10, w / 2, h * 1.15, w * 0.75)
    g.add_color_stop_rgba(0, 1, 0.18, 0.58, 0.35 * a); g.add_color_stop_rgba(1, 1, 0.18, 0.58, 0)
    ctx.rectangle(0, 0, w, h); ctx.set_source(g); ctx.fill()
    for j, (px, py, r) in enumerate(((0.08, 0.2, 9), (0.93, 0.18, 11), (0.88, 0.82, 7), (0.12, 0.8, 6), (0.5, 0.08, 5))):
        sparkle(ctx, px * w, py * h, r, a, t, j * 1.7)
_clip = {}
def clip_frame(name, t, t0):
    import glob as _g
    fs = _clip.get(name)
    if fs is None: fs = _clip[name] = sorted(_g.glob(os.path.join(CLIPS, name, '*.jpg')))
    k = min(len(fs) - 1, max(0, int((t - t0) * FPS)))
    key = (name, k)
    if key not in _img:
        for kk in [kk for kk in _img if kk[0] == name and isinstance(kk[1], int)]: _img.pop(kk)
        im = Image.open(fs[k]).convert('RGBA'); _img[key] = (im, fx.pil_surface(im))
    return _img[key]
def paint_clip(ctx, name, t, t0, x, y, w, h, a, r=0):
    if a <= 0.002: return
    im, (surf, _b) = clip_frame(name, t, t0); s = max(w / im.width, h / im.height)
    ctx.save(); rr(ctx, x, y, w, h, r) if r else ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.translate(x + (w - im.width * s) / 2, y + (h - im.height * s) / 2); ctx.scale(s, s)
    ctx.set_source_surface(surf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()
def R(name): return os.path.join(REF, name)
def chip(ctx, cx, cy, txt, a, size=24):
    """small pink chip with serif text"""
    if a <= 0.002: return
    tt = SER(txt, size, WHITE, 'Semibold', glow=False); w = tt[4] + 40; h = size * 1.9
    rr(ctx, cx - w / 2, cy - h / 2, w, h, h / 2); rgba(ctx, HOT, a * 0.92); ctx.fill()
    put(ctx, tt, cx, cy + 1, alpha=a)

# ---------------- the morphing card (band above my eyes) ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(17) - 0.10, 'tweet', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(40) - 0.10, 'call', CX, 260, 1000, 330, 24, PLUM[:3]),
    (T(53) - 0.10, 'notdead', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(66) - 0.10, 'dead', CX, 260, 1000, 330, 24, PLUM[:3]),
    (T(87) - 0.10, 'launch', CX, 260, 1000, 330, 24, PLUM[:3]),
    (T(103) - 0.15, 'projects', CX, 260, 1000, 330, 24, PLUM[:3]),
    (T(116) - 0.10, 'copy', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(146) - 0.10, 'noise', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(173) - 0.10, 'offers', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(187) - 0.10, 'why', CX, 260, 1000, 420, 24, PLUM[:3]),
    (T(204) - 0.10, 'viral', CX, 260, 1000, 330, 24, PLUM[:3]),
    (T(218) - 0.10, 'end', CX, 260, 1000, 420, 24, PLUM[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000
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
    if name == 'tweet':                                                        # her post: text + still, then "viral"
        stage_bg(ctx, w, h, a, t)
        paint(ctx, R('t_text.png'), None, 26, 26, 430, h - 52, a, r=16)
        paint(ctx, R('t_photo.png'), None, 480, 40, 494, 292, a * eo(prog(t, st0 + 0.3, 0.5)), r=16, anchor_top=False)
        k = pop(t, T(23) - 0.15)                                               # "se volvió viral"
        if k > 0.001:
            gl = GLOSS('Viral', 64); put(ctx, gl, 727, 372 + 10 * (1 - k), scale=0.7 + 0.3 * k, alpha=a * c01(k * 1.5))
    elif name == 'call':                                                        # "quiero camellar con la mejor empresa del mundo"
        paint_clip(ctx, 'call', t, st0, 0, 0, w, h, a)
        put(ctx, SER('Su película, para conseguir trabajo', 26, BLUSH, 'Medium'), 30, 40, alpha=a * eo(prog(t, st0 + 0.4, 0.5)), ax=0)
    elif name == 'notdead':                                                     # her lettering, our sentence: design is NOT dead
        stage_bg(ctx, w, h, a, t)
        k1 = pop(t, st0 + 0.15)
        put(ctx, GLOSS('Design is', 92), w / 2 - 120, 130 + 16 * (1 - k1), alpha=a * c01(k1 * 1.4))
        put(ctx, GLOSS('Dead', 108), w / 2 + 150, 268 + 16 * (1 - k1), alpha=a * c01(k1 * 1.4))
        kn = pop(t, T(63) - 0.12, w=11, zeta=0.6)                               # "no está muerto": NOT lands with a bounce
        if kn > 0.001:
            ctx.save(); ctx.translate(w / 2 - 120, 268); ctx.rotate(-0.12); ctx.scale(0.4 + 0.6 * kn, 0.4 + 0.6 * kn)
            put(ctx, GLOSS('not', 108), 0, 0, alpha=a * c01(kn * 1.5)); ctx.restore()
        put(ctx, SER('El diseño no está muerto.', 28, BLUSH), w / 2, h - 40, alpha=a * eo(prog(t, T(63), 0.5)))
    elif name == 'dead':                                                        # what everyone said: her "Design is Dead" card, then the AI headline
        sw = T(78) - 0.35
        paint_clip(ctx, 'dead', t, st0, 0, 0, w, h, a * (1 - c01((t - sw) / 0.4)))
        paint_clip(ctx, 'news', t, sw, 0, 0, w, h, a * c01((t - sw) / 0.4))
        put(ctx, SER('Lo que todo el mundo decía', 26, BLUSH), 30, 40, alpha=a * eo(prog(t, st0 + 0.4, 0.5)), ax=0)
    elif name == 'launch':                                                      # "un launch video… de ella misma"
        paint_clip(ctx, 'hi', t, st0, 0, 0, w, h, a)
        k = pop(t, T(96) - 0.15)
        if k > 0.001: chip(ctx, w - 190, h - 46 + 8 * (1 - k), 'Su propio launch video', a * c01(k * 1.5), 24)
    elif name == 'projects':                                                    # "de los proyectos que ella ha hecho" + "mega hit"
        seq = [('type', st0), ('welcome', st0 + 1.2), ('game', st0 + 2.4)]
        for j, (nm, t0) in enumerate(seq):
            nxt = seq[j + 1][1] if j + 1 < len(seq) else 1e9
            fa = c01((t - t0) / 0.4) * (1 - c01((t - nxt) / 0.4)) if j else (1 - c01((t - nxt) / 0.4))
            paint_clip(ctx, nm, t, t0, 0, 0, w, h, a * fa)
        k = pop(t, T(112) - 0.15)                                              # "mega hit"
        if k > 0.001:
            ctx.rectangle(0, 0, w, h); ctx.set_source_rgba(0.06, 0.0, 0.03, 0.45 * a * c01(k * 1.5)); ctx.fill()
            put(ctx, GLOSS('Mega hit', 110), w / 2, h / 2 - 20 + 14 * (1 - k), scale=0.8 + 0.2 * k, alpha=a * c01(k * 1.5))
            put(ctx, SER('4,9 M de vistas en X', 28, BLUSH), w / 2, h - 52, alpha=a * c01(k * 1.5))
    elif name == 'copy':                                                        # "no es que uno tenga que hacer lo que hizo ella, pero… lo esencial"
        stage_bg(ctx, w, h, a, t)
        put(ctx, SER('No se trata de copiar su video.', 40, BLUSH), w / 2, 130 + lift, alpha=a)
        k = pop(t, T(133) - 0.15)                                              # "la vaina esencial"
        if k > 0.001:
            put(ctx, SER('Lo esencial:', 34, ROSE, 'Regular'), w / 2, 220, alpha=a * c01(k * 1.5))
            put(ctx, GLOSS('lograr atención', 84), w / 2, 312 + 12 * (1 - k), alpha=a * c01(pop(t, T(144) - 0.15) * 1.5))
    elif name == 'noise':                                                       # literal chain: ruido -> gente -> miradas -> todo sucede
        stage_bg(ctx, w, h, a, t)
        put(ctx, SER('Si quieres lograr algo:', 30, ROSE, 'Regular'), w / 2, 56 + lift, alpha=a)
        k0 = pop(t, T(150) - 0.15)                                             # "hacer mucho ruido"
        put(ctx, GLOSS('haz ruido', 96), w / 2, 140 + 14 * (1 - k0), alpha=a * c01(k0 * 1.5))
        steps = [(T(160) - 0.15, 'atrae gente', 190), (T(163) - 0.15, 'atrae miradas', 500), (T(155) - 0.2, 'todo sucede', 810)]
        ks = [pop(t, t0) for t0, _, _ in steps]
        for j, ((t0, lbl, x), k) in enumerate(zip(steps, ks)):
            if k <= 0.001: continue
            chip(ctx, x, 300 + 10 * (1 - k), lbl, a * c01(k * 1.5), 28)
            if j < 2 and ks[j + 1] > 0.001:
                aa = a * c01(min(k, ks[j + 1]) * 1.5); ax0 = x + 130; ax1 = x + 180
                ctx.move_to(ax0, 300); ctx.line_to(ax1, 300); ctx.move_to(ax1 - 10, 290); ctx.line_to(ax1, 300); ctx.line_to(ax1 - 10, 310)
                rgba(ctx, HOT, aa); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
        ki = pop(t, T(170) - 0.15)                                             # "lo más importante ahora mismo"
        if ki > 0.001: put(ctx, SER('Lo más importante, ahora mismo.', 26, BLUSH), w / 2, h - 34, alpha=a * c01(ki * 1.5))
    elif name == 'offers':                                                      # offers raining: "Hiring? My DMs are open." + what people said
        stage_bg(ctx, w, h, a, t)
        paint(ctx, R('t_text.png'), (0, 1000, 1170, 1085), 30, 40, 440, 34, a, r=8, anchor_top=False)
        put(ctx, SER('Le llueven propuestas', 34, BLUSH, 'Semibold'), 250, 190 + lift, alpha=a)
        put(ctx, SER('de las mejores empresas', 28, ROSE, 'Regular'), 250, 236 + lift, alpha=a)
        for j, (img_, t0) in enumerate((('q_ankur.png', T(179) - 0.2), ('q_aleks.png', T(183) - 0.15))):
            k = pop(t, t0)
            if k <= 0.001: continue
            x = 510 + j * 20; y = 34 + j * 186 + 30 * (1 - k)
            ctx.save(); ctx.translate(x + 225, y + 84); ctx.rotate((-0.025, 0.02)[j]); ctx.translate(-225, -84)
            soft_shadow(ctx, 0, 0, 450, 168, 14, a * c01(k * 1.5))
            paint(ctx, R(img_), None, 0, 0, 450, 168, a * c01(k * 1.5), r=14); ctx.restore()
    elif name == 'why':
        stage_bg(ctx, w, h, a, t)
        put(ctx, SER('¿Por qué no estás haciendo', 40, BLUSH), w / 2, 110 + lift, alpha=a)
        put(ctx, SER('todo lo posible para lograr la', 40, BLUSH), w / 2, 170 + lift, alpha=a * eo(prog(t, st0 + 0.3, 0.5)))
        k = pop(t, T(199) - 0.2)
        put(ctx, GLOSS('atención?', 100), w / 2, 290 + 14 * (1 - k), alpha=a * c01(k * 1.5))
    elif name == 'viral':                                                       # "ella lo hizo y se fue mega viral"
        paint_clip(ctx, 'bed', t, st0, 0, 0, w, h, a)
        k = pop(t, T(212) - 0.15)
        if k > 0.001:
            ctx.rectangle(0, h - 92, w, 92); ctx.set_source_rgba(0.06, 0, 0.03, 0.55 * a * c01(k * 1.5)); ctx.fill()
            paint(ctx, R('t_stats.png'), (0, 60, 1170, 190), w / 2 - 330, h - 82, 660, 74, a * c01(k * 1.5), anchor_top=False)
    elif name == 'end':                                                         # "¿que por pena? no, no se puede"
        stage_bg(ctx, w, h, a, t)
        put(ctx, SER('¿Y tú por qué no lo haces?', 40, BLUSH), w / 2, 100 + lift, alpha=a)
        k1 = pop(t, T(226) - 0.15)
        put(ctx, SER('¿Por pena?', 44, ROSE, 'Semibold'), w / 2, 180 + 12 * (1 - k1), alpha=a * c01(k1 * 1.5))
        k2 = pop(t, T(229) - 0.12, w=11, zeta=0.65)
        put(ctx, GLOSS('No se puede.', 100), w / 2, 300 + 14 * (1 - k2), scale=0.6 + 0.4 * k2, alpha=a * c01(k2 * 1.5))

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

# ---------------- title (over the hook), in her style ----------------
LABEL = 'teoría by andrés corrales'
def scrim(ctx, a):
    if a <= 0.002: return
    g = cairo.LinearGradient(0, 840, 0, H)
    g.add_color_stop_rgba(0, 0.06, 0, 0.03, 0); g.add_color_stop_rgba(0.45, 0.06, 0, 0.03, 0.55 * a); g.add_color_stop_rgba(1, 0.06, 0, 0.03, 0.8 * a)
    ctx.rectangle(0, 840, W, H - 840); ctx.set_source(g); ctx.fill()
def title(ctx, t, force=False):
    if t >= TITLE_END + 0.4 and not force: return
    fade = 1.0 if force else 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    scrim(ctx, fade * (1.0 if force else c01(t / 0.3)))
    n = len(LABEL) if force else min(len(LABEL), int(max(0, t - 0.1) / 0.03))
    if n > 0: put(ctx, SER(LABEL[:n], 34, BLUSH, 'Regular'), 66, 1030, alpha=fade, ax=0)
    e1 = 1.0 if force else spring(t - 0.35, w=9.0, zeta=0.8)
    put(ctx, GLOSS('Atención', 150), 50, 1150 + 30 * (1 - e1), scale=0.85 + 0.15 * e1, alpha=c01(e1 * 1.3) * fade, ax=0)
    for li, line in enumerate(('es lo único que', 'necesitas')):
        e = 1.0 if force else spring(t - (0.6 + 0.15 * li), w=9.0, zeta=0.88)
        put(ctx, SER(line, 96, WHITE, 'Semibold'), 66, 1310 + li * 112 + 26 * (1 - e), alpha=c01(e * 1.3) * fade, ax=0)
    if force: return
    for j, (px, py, r) in enumerate(((0.86, 0.6, 14), (0.12, 0.53, 9), (0.78, 0.79, 10))):
        sparkle(ctx, px * W, py * H, r, fade * c01((t - 0.5 - 0.2 * j) / 0.4), t, j * 2.1)

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
    tt = SER(line, 56, BLUSH, 'Medium'); sc = min(1.0, 920 / tt[4])
    pw_, ph_ = (tt[4] + 70) * sc, 96 * sc; y = 1450 + 8 * (1 - e)
    rr(ctx, W / 2 - pw_ / 2, y - ph_ / 2, pw_, ph_, ph_ / 2); ctx.set_source_rgba(0.12, 0.02, 0.07, 0.78 * e); ctx.fill()
    put(ctx, tt, W / 2, y + 2, scale=sc, alpha=e)

def progress(ctx, t):
    ctx.rectangle(0, H - 8, W, 8); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    x1 = W * c01(t / DUR)
    if x1 > 1:
        g = cairo.LinearGradient(0, 0, W, 0); g.add_color_stop_rgba(0, 1, 0.18, 0.58, 1); g.add_color_stop_rgba(1, 1, 0.6, 0.82, 1)
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
