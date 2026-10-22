"""IMG_9068 · "14 librerías para que tu web no parezca hecha con IA". 1.05x, voice only.
Current house style = the X reel (video 20): one card per idea, each holds several seconds, slow springs, elements build inside.
Key visual = React Bits (reactbits.dev): near-black cards with hairline borders, glossy gradient pills with an icon disc, thin line
backgrounds (waves, concentric frames, bars), code / terminal windows, preset lists. No halftone dots (rejected on 19 oct 2026).
One full-screen beat: the 14-library list (thumbnail · name · domain). Subtitles on a dark pill. Purple-blue progress bar. HDR only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, SCRIPTS); sys.path.insert(0, HERE)
import fx
from fx import np, Image, cairo, W, H, FPS, prog, c01, eio, eo, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter
_cwd = os.getcwd(); os.chdir(HERE); import edit21 as E; os.chdir(_cwd)

SPEED = 1.05
REF = os.path.join(HERE, 'ref'); WEB = os.path.join(HERE, 'web')
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
_ws = [w for s in json.load(open(os.path.join(HERE, 'v21.json')))['segments'] for w in s['words']]
FIX = {31: 'se', 32: '', 46: 'para', 106: 'profesional', 107: 'y real.', 108: 'Botones,', 109: 'shaders,', 112: 'texto,', 136: '¿Y cuáles',
       184: 'pegárselo', 189: 'él', 190: '', 191: 'va', 193: 'hacer', 203: 'va a adaptar.', 217: 'profesional', 223: 'hecha', 228: 'la',
       230: 'hecho', 243: 'Moraleja', 244: 'Design,', 250: 'Y', 252: 'tienen'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for w in WORDS if w[2]]
def T(i): return _ws[i]['start']
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.5
TITLE_END = T(36) - 0.1                                                   # title holds the whole hook ("…la mitad del trabajo")

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

# ---------------- the 14 libraries ----------------
LIBS = [('Arc UI', 'uiarc.dev', REF + '/c10.png'), ('BuilderTools', 'buildertools.sh', WEB + '/02_buildertools.png'),
        ('UImaxxing', 'uimaxx.ing', WEB + '/03_uimaxx.png'), ('Libraries.dev', 'libraries.dev', REF + '/c09.png'),
        ('Procedural Sounds', 'procedural-sounds.vercel.app', WEB + '/05_sounds.png'), ('beUI', 'beui.dev', REF + '/c07.png'),
        ('Cult UI', 'cult-ui.com', REF + '/c06.png'), ('Aceternity UI', 'ui.aceternity.com', WEB + '/08_aceternity.png'),
        ('Beautiful UI', 'beautifului.dev', REF + '/c03.png'), ('Canvas UI', 'canvasui.dev', WEB + '/10_canvasui.png'),
        ('React Bits', 'reactbits.dev', REF + '/c02.png'), ('Kobra', 'kobra.systems', WEB + '/12_kobra.png'),
        ('Mobbin', 'mobbin.com', WEB + '/13_mobbin.png'), ('21st.dev', '21st.dev', WEB + '/14_21st.png')]
LIBS = [(n, d, p.replace(REF, os.path.join(HERE, 'ref')) if p.startswith(REF) else p) for n, d, p in LIBS]
GRADS = ['purple', 'pink', 'blue', 'teal', 'green']

# ---------------- the morphing card (band above my eyes) ----------------
CX = W / 2
STATES = [  # (start, name, x-centre, y-centre, w, h, radius, fill)
    (T(15) - 0.10, 'refs', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(42) - 0.10, 'libs', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(63) - 0.10, 'project', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(74) - 0.10, 'why', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(108) - 0.10, 'kinds', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(168) - 0.10, 'copy', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(204) - 0.10, 'pro', CX, 260, 1000, 420, 26, CARD[:3]),
    (T(233) - 0.10, 'designer', CX, 260, 1000, 420, 26, CARD[:3]),
]
BAND_TOP, BAND_H, BAND_W = 46, 420, 1000
SHAPE_ON = STATES[0][0]
LIST_BEAT = (T(136) - 0.10, T(168) - 0.12)                               # full-screen: the 14 libraries
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
    if STATES[i][1] == 'kinds': b = min(b, LIST_BEAT[0])
    return c01((t - a - 0.10) / 0.35) * (1 - c01((t - b) / 0.30))

CODE = ["import GradientWaves from './GradientWaves';", "", "export default function Hero() {", "  return (",
        "    <GradientWaves", '      waveColor="#38bdf8"', "      amplitude={1.8}", "    />", "  );", "}"]

def draw_state(ctx, t, name, w, h, a, lift, st0):
    if name == 'refs':                                                          # screenshots dropped into a Claude prompt -> 50%
        waves(ctx, 0, 0, w, h, t, a, col=C(96, 165, 250))
        panel(ctx, 40, 40, w - 80, 230, a, 20)
        put(ctx, GT('Hazme una página web como estas', 30, WHITE), 76, 86 + lift, alpha=a, ax=0)
        shots = [(T(22) - 0.15, LIBS[0][2]), (T(24) - 0.15, LIBS[7][2]), (T(35) - 0.25, LIBS[10][2])]
        for j, (t0, p) in enumerate(shots):                                     # "screenshots… y se las está pasando"
            k = pop(t, t0)
            if k <= 0.001: continue
            x = 76 + j * 200; y = 130 + 40 * (1 - k)
            ctx.save(); ctx.translate(x + 90, y + 56); ctx.rotate((-0.05, 0.03, -0.02)[j] * (1 - k)); ctx.translate(-90, -56)
            paint(ctx, p, None, 0, 0, 180, 112, a * c01(k * 1.4), r=10)
            rr(ctx, 0, 0, 180, 112, 10); rgba(ctx, LINE, a * c01(k * 1.4)); ctx.set_line_width(1.5); ctx.stroke(); ctx.restore()
        ctx.arc(w - 100, 220, 28, 0, 2 * math.pi); rgba(ctx, C(217, 119, 87), a); ctx.fill()        # send button
        ctx.move_to(w - 100, 232); ctx.line_to(w - 100, 206); ctx.move_to(w - 111, 217); ctx.line_to(w - 100, 206); ctx.line_to(w - 89, 217)
        ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(3.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        kb = pop(t, T(38) - 0.15)                                               # "la mitad del trabajo"
        put(ctx, GT('Trabajo hecho', 24, MUTE), 40, 318, alpha=a * c01(kb * 1.5), ax=0)
        rr(ctx, 40, 344, w - 80, 22, 11); rgba(ctx, LINE, a * c01(kb * 1.5)); ctx.fill()
        fillw = (w - 80) * 0.5 * eio(prog(t, T(38) - 0.1, 0.9))
        if fillw > 1:
            g = cairo.LinearGradient(40, 0, 40 + fillw, 0); g.add_color_stop_rgba(0, *GRAD['purple'][0][:3], a); g.add_color_stop_rgba(1, *GRAD['blue'][1][:3], a)
            rr(ctx, 40, 344, fillw, 22, 11); ctx.set_source(g); ctx.fill()
        put(ctx, GT('%d%%' % int(round(100 * fillw / (w - 80))), 40, WHITE, 'SemiBold'), w - 40, 316, alpha=a * c01(kb * 1.5), ax=1)
    elif name == 'libs':                                                        # terminal + libraries
        waves(ctx, 0, 0, w, h, t, a)
        panel(ctx, 40, 40, 560, 340, a, 18, 'Terminal')
        lines = [(st0 + 0.3, '$ npx shadcn@latest add', WHITE), (st0 + 0.3, '  @react-bits/GradientWaves', WHITE),
                 (T(52) - 0.1, 'Checking registry.', MUTE), (T(55) - 0.2, 'Created 2 files.', MUTE), (T(57) - 0.1, 'Component ready.', OK)]
        y = 116
        for j, (t0, txt, col) in enumerate(lines):
            if t < t0: break
            s = typed(txt, t, t0, 40 if j < 2 else 60)
            if j >= 2: check(ctx, 76, y - 2, 18, OK, a * c01((t - t0) / 0.2)); put(ctx, MT(s, 24, col), 98, y, alpha=a, ax=0)
            else: put(ctx, MT(s, 24, col), 66, y, alpha=a, ax=0)
            y += 50
        put(ctx, GT('Librerías', 24, MUTE), 640, 70, alpha=a * eo(prog(t, T(55) - 0.2, 0.4)), ax=0)
        for j, (nm, g_) in enumerate((('React Bits', 'purple'), ('Arc UI', 'blue'), ('Aceternity', 'pink'), ('Cult UI', 'teal'), ('beUI', 'green'))):
            k = pop(t, T(55) - 0.15 + 0.22 * j)                                   # "librerías de componentes que él sepa cómo usar"
            if k <= 0.001: continue
            gpill(ctx, 640 + 150 + 20 * (1 - k), 126 + j * 58, nm, a * c01(k * 1.5), g_, size=24, h=48, scale=1.0)
    elif name == 'project':                                                     # Hero.jsx -> preview
        panel(ctx, 40, 40, 520, 340, a, 18, 'Hero.jsx')
        n_lines = int(len(CODE) * c01((t - st0 - 0.2) / 2.2)) + 1
        for j, ln in enumerate(CODE[:n_lines]):
            put(ctx, MT(str(j + 1), 19, DIM), 70, 112 + j * 27, alpha=a, ax=1)
            put(ctx, MT(ln, 19, C(225, 225, 235)), 84, 112 + j * 27, alpha=a, ax=0)
        k = pop(t, T(68) - 0.15)                                                # "tu proyecto": the preview renders
        rr(ctx, 590, 40, w - 630, 340, 18); rgba(ctx, BG, a); ctx.fill()
        ctx.save(); rr(ctx, 590, 40, w - 630, 340, 18); ctx.clip()
        waves(ctx, 590, 40, w - 630, 340, t, a * c01(k * 1.4), n=22, col=C(56, 189, 248), amp=34)
        put(ctx, GT('Tu proyecto', 40, WHITE, 'SemiBold'), 590 + (w - 630) / 2, 196 + 20 * (1 - k), alpha=a * c01(k * 1.4))
        put(ctx, GT('con componentes reales', 22, MUTE), 590 + (w - 630) / 2, 240 + 20 * (1 - k), alpha=a * c01(k * 1.4))
        ctx.restore(); rr(ctx, 590, 40, w - 630, 340, 18); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
    elif name == 'why':                                                         # generic AI page vs a real one
        k1 = pop(t, st0 + 0.15); k2 = pop(t, T(100) - 0.15)
        x1, x2, yy, pw, ph = 40, 520, 40, 440, 280
        if k1 > 0.001:                                                          # the "made by AI" look: purple gradient, centred hero, 3 equal cards
            aa = a * c01(k1 * 1.4)
            ctx.save(); rr(ctx, x1, yy, pw, ph, 16); ctx.clip()
            g = cairo.LinearGradient(x1, yy, x1 + pw, yy + ph); g.add_color_stop_rgba(0, 0.36, 0.2, 0.85, aa); g.add_color_stop_rgba(1, 0.85, 0.3, 0.75, aa)
            ctx.rectangle(x1, yy, pw, ph); ctx.set_source(g); ctx.fill()
            put(ctx, GT('Welcome to Our Platform', 26, WHITE, 'Bold'), x1 + pw / 2, yy + 70, alpha=aa)
            put(ctx, GT('The best solution for your needs', 16, C(255, 255, 255, 0.85)), x1 + pw / 2, yy + 102, alpha=aa)
            rr(ctx, x1 + pw / 2 - 70, yy + 122, 140, 36, 18); ctx.set_source_rgba(1, 1, 1, aa); ctx.fill()
            put(ctx, GT('Get Started', 16, C(90, 50, 200), 'SemiBold'), x1 + pw / 2, yy + 141, alpha=aa)
            for j in range(3):
                rr(ctx, x1 + 24 + j * 136, yy + 182, 120, 78, 10); ctx.set_source_rgba(1, 1, 1, 0.9 * aa); ctx.fill()
                ctx.arc(x1 + 84 + j * 136, yy + 208, 12, 0, 2 * math.pi); ctx.set_source_rgba(0.55, 0.35, 0.95, aa); ctx.fill()
                rr(ctx, x1 + 44 + j * 136, yy + 232, 80, 8, 4); ctx.set_source_rgba(0.75, 0.75, 0.8, aa); ctx.fill()
            ctx.restore()
            kx = pop(t, T(97) - 0.15)                                           # "hecha por Claude"
            put(ctx, GT('Hecha por IA', 28, WHITE, 'Medium'), x1, yy + ph + 44, alpha=aa, ax=0)
            if kx > 0.001: cross(ctx, x1 + pw - 22, yy + ph + 44, 22, BAD, aa * c01(kx * 1.5))
        if k2 > 0.001:                                                          # "sino… profesional y real"
            aa = a * c01(k2 * 1.4)
            ctx.save(); ctx.translate(30 * (1 - k2), 0)
            paint(ctx, LIBS[0][2], None, x2, yy, pw, ph, aa, r=16)
            rr(ctx, x2, yy, pw, ph, 16); rgba(ctx, LINE, aa); ctx.set_line_width(1.5); ctx.stroke()
            put(ctx, GT('Profesional y real', 28, WHITE, 'Medium'), x2, yy + ph + 44, alpha=aa, ax=0)
            check(ctx, x2 + pw - 22, yy + ph + 44, 26, OK, aa, eo(prog(t, T(107) - 0.1, 0.4)))
            ctx.restore()
    elif name == 'kinds':                                                       # what "components" means: six live tiles
        tiles = [('Botones', T(108)), ('Shaders', T(109)), ('Animaciones de texto', T(110)), ('Alineaciones', T(113)),
                 ('Estructura', T(114)), ('Transiciones', T(120))]
        tw_, th_ = 296, 150
        for j, (lbl, t0) in enumerate(tiles):
            k = pop(t, t0 - 0.2)
            col, row = j % 3, j // 3
            x = 40 + col * (tw_ + 16); y = 34 + row * (th_ + 48)
            rr(ctx, x, y, tw_, th_, 14); rgba(ctx, PANEL, a * (0.35 + 0.65 * c01(k * 1.4))); ctx.fill_preserve(); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()
            if k <= 0.001: continue
            aa = a * c01(k * 1.4); lt = t - t0
            ctx.save(); rr(ctx, x, y, tw_, th_, 14); ctx.clip(); ctx.translate(x, y + 12 * (1 - k))
            if j == 0:
                press = 0.5 + 0.5 * math.sin(lt * 3.2)
                gpill(ctx, tw_ / 2, 52, 'Get started', aa, 'purple', size=20, h=42, scale=0.96 + 0.04 * press)
                gpill(ctx, tw_ / 2, 108, 'Primary', aa, 'blue', size=20, h=42, icon=False)
            elif j == 1: waves(ctx, 0, 0, tw_, th_, t * 1.6, aa * 3.0, n=14, col=C(96, 165, 250), amp=16)
            elif j == 2:
                word = 'Componentes'; f_x = 26
                for ci, ch in enumerate(word):
                    kk = c01((lt % 3.0 - 0.08 * ci) / 0.35)
                    tt = GT(ch, 40, WHITE, 'SemiBold'); put(ctx, tt, f_x, th_ / 2 + 14 * (1 - kk), alpha=aa * kk, ax=0); f_x += tt[4]
            elif j == 3:
                for gx in (74, 148, 222): ctx.rectangle(gx, 10, 1, th_ - 20); rgba(ctx, C(244, 114, 182), aa * 0.6); ctx.fill()
                for bi in range(3):
                    snap = eo(c01((lt - 0.3 * bi) / 0.6))
                    bx = 74 * (bi + 1) - 30 + (30 + 25 * (bi - 1)) * (1 - snap)
                    rr(ctx, bx, 40 + bi * 30, 60, 22, 5); rgba(ctx, WHITE, aa * 0.85); ctx.fill()
            elif j == 4:
                parts = [(14, 14, tw_ - 28, 16), (14, 40, tw_ - 28, 46), (14, 96, 82, 40), (107, 96, 82, 40), (200, 96, 82, 40)]
                for pi, (px, py, pww, phh) in enumerate(parts):
                    kk = c01((lt - 0.2 * pi) / 0.4)
                    rr(ctx, px, py, pww, phh, 5); rgba(ctx, WHITE, aa * 0.18 * kk); ctx.fill_preserve(); rgba(ctx, WHITE, aa * 0.5 * kk); ctx.set_line_width(1.2); ctx.stroke()
            elif j == 5:
                m = 0.5 - 0.5 * math.cos(lt * 1.6)
                ww, hh = 120 + 120 * m, 40 + 60 * m
                rr(ctx, tw_ / 2 - ww / 2, th_ / 2 - hh / 2, ww, hh, 20 - 6 * m); g_ = GRAD['teal']
                g = cairo.LinearGradient(0, 0, tw_, 0); g.add_color_stop_rgba(0, *g_[0][:3], aa); g.add_color_stop_rgba(1, *g_[1][:3], aa); ctx.set_source(g); ctx.fill()
            ctx.restore()
            put(ctx, GT(lbl, 24, WHITE, 'Medium'), x + 4, y + th_ + 24, alpha=aa, ax=0)
    elif name == 'copy':                                                        # copy from the library, paste into Claude Code
        panel(ctx, 40, 40, 440, 340, a, 18, 'TextureButton.tsx')
        code = ['<TextureButton', '  variant="accent"', '  size="lg"', '>', '  Get started', '</TextureButton>']
        for j, ln in enumerate(code): put(ctx, MT(ln, 22, C(225, 225, 235)), 66, 118 + j * 34, alpha=a, ax=0)
        tc = T(182) - 0.05                                                       # "copiárselo"
        copied = c01((t - tc) / 0.15)
        rr(ctx, 360, 56, 100, 34, 8); ctx.set_source_rgba(1, 1, 1, (0.10 + 0.08 * copied) * a); ctx.fill()
        put(ctx, GT('Copiado' if copied else 'Copiar', 18, OK if copied else WHITE, 'Medium'), 410, 74, alpha=a)
        kc = pop(t, T(183) - 0.1)
        rr(ctx, 520, 40, w - 560, 340, 18); rgba(ctx, C(20, 18, 16), a * c01(kc * 1.4)); ctx.fill_preserve(); rgba(ctx, LINE, a * c01(kc * 1.4)); ctx.set_line_width(1.5); ctx.stroke()
        if kc > 0.001:
            aa = a * c01(kc * 1.4)
            put(ctx, GT('Claude Code', 22, C(217, 119, 87), 'SemiBold'), 548, 74, alpha=aa, ax=0)
            ctx.rectangle(520, 98, w - 560, 1); rgba(ctx, LINE, aa); ctx.fill()
            pasted = c01((t - (T(184) - 0.05)) / 0.15)                          # "pegárselo a Claude Code"
            put(ctx, MT('>', 22, MUTE), 548, 132, alpha=aa, ax=0)
            put(ctx, MT('[Pegado: TextureButton.tsx]' if pasted else '', 20, C(225, 225, 235)), 572, 132, alpha=aa * pasted, ax=0)
            steps = [(T(189) - 0.1, 'Leyendo el componente'), (T(197) - 0.15, 'Adaptándolo a tu proyecto'), (T(203) + 0.25, 'Listo')]
            for j, (t0, txt) in enumerate(steps):
                kk = pop(t, t0)
                if kk <= 0.001: continue
                yy = 190 + j * 54
                done = j == 2 or t > steps[min(j + 1, 2)][0]
                if done: check(ctx, 560, yy, 20, OK, aa * c01(kk * 1.5))
                else: ctx.arc(560, yy, 7, 0, 2 * math.pi); rgba(ctx, C(217, 119, 87), aa * (0.5 + 0.5 * math.sin(t * 6))); ctx.fill()
                put(ctx, GT(txt, 24, OK if j == 2 else WHITE, 'Medium' if j == 2 else 'Regular'), 584, yy, alpha=aa * c01(kk * 1.5), ax=0)
        cx_ = track(t, [(tc - 0.6, 410), (T(183) + 0.2, 640)], w - 60, w=8.0, zeta=0.95)
        cy_ = track(t, [(tc - 0.6, 78), (T(183) + 0.2, 140)], h - 30, w=8.0, zeta=0.95)
        press = max(math.sin(math.pi * c01((t - tc + 0.08) / 0.2)), math.sin(math.pi * c01((t - T(184) + 0.08) / 0.2)))
        cursor(ctx, cx_, cy_, a * c01((t - tc + 1.0) / 0.3) * (1 - c01((t - T(189)) / 0.4)), press)
    elif name == 'pro':                                                         # the three results
        waves(ctx, 0, 0, w, h, t, a, col=C(74, 222, 128), amp=20)
        put(ctx, GT('Tu página web', 30, MUTE), w / 2, 70 + lift, alpha=a)
        items = [(min(T(213) - 0.15, st0 + 0.6), 'Mucho mejor', 'purple'), (T(216) - 0.15, 'Más profesional', 'blue'), (T(225) - 0.2, 'No parece hecha por IA', 'green')]
        for j, (t0, lbl, g_) in enumerate(items):
            k = pop(t, t0)
            if k <= 0.001: continue
            gpill(ctx, w / 2 + 20 * (1 - k), 150 + j * 84, lbl, a * c01(k * 1.5), g_, size=30, h=64)
    elif name == 'designer':                                                    # Moraleja Design: name, url and their work
        waves(ctx, 0, 0, w, h, t, a, col=C(244, 114, 182), amp=22)
        put(ctx, GT('¿Quieres un buen diseño?', 30, WHITE, 'SemiBold'), 44, 70 + lift, alpha=a, ax=0)
        k = pop(t, T(241) - 0.15)                                               # "contraten a Moraleja Design"
        if k > 0.001:
            gpill(ctx, 44 + 160 + 20 * (1 - k), 150, 'Moraleja Design', a * c01(k * 1.5), 'pink', size=30, h=66)
            put(ctx, MT('moraleja.co', 24, C(244, 114, 182)), 48, 222, alpha=a * c01(k * 1.5), ax=0)
        k2 = pop(t, T(245) - 0.1)
        put(ctx, GT('La mejor diseñadora que conozco', 24, MUTE), 48, 270, alpha=a * c01(k2 * 1.5), ax=0)
        k3 = pop(t, T(253) - 0.15)                                              # "y no tienen ninguno de esos problemas"
        if k3 > 0.001:
            check(ctx, 60, 336, 22, OK, a * c01(k3 * 1.5), eo(prog(t, T(253), 0.4)))
            put(ctx, GT('Cero problemas de diseño', 24, WHITE, 'Medium'), 84, 336, alpha=a * c01(k3 * 1.5), ax=0)
        shots = [('m4b.png', (0, 0, 1170, 1180)), ('m2.png', None), ('m1.png', None), ('m3.png', None)]   # Instagram, Lab, Gallery, Contact
        x0, y0, pw, ph = 500, 36, w - 536, h - 72
        rr(ctx, x0, y0, pw, ph, 16); rgba(ctx, BG, a); ctx.fill()
        span = (DUR - 0.3 - (st0 + 0.3)) / len(shots)
        for j, (nm, crop) in enumerate(shots):
            t0 = st0 + 0.3 + span * j
            fa = c01((t - t0) / 0.6) * (1 - c01((t - (t0 + span)) / 0.6)) if j < len(shots) - 1 else c01((t - t0) / 0.6)
            if fa <= 0.002: continue
            zoom = 1.0 + 0.04 * c01((t - t0) / (span + 0.6))                     # slow push-in inside the frame
            ctx.save(); rr(ctx, x0, y0, pw, ph, 16); ctx.clip()
            ctx.translate(x0 + pw / 2, y0 + ph / 2); ctx.scale(zoom, zoom); ctx.translate(-(x0 + pw / 2), -(y0 + ph / 2))
            paint(ctx, os.path.join(HERE, 'ref', nm), crop, x0, y0, pw, ph, a * fa, r=16)
            ctx.restore()
        rr(ctx, x0, y0, pw, ph, 16); rgba(ctx, LINE, a); ctx.set_line_width(1.5); ctx.stroke()

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

# ---------------- full-screen beat: the list ----------------
def list_beat(ctx, t):
    a = beat_a(t, LIST_BEAT)
    if a <= 0.002: return
    ctx.rectangle(0, 0, W, H); rgba(ctx, BG, 0.96 * a); ctx.fill()
    waves(ctx, 0, 0, W, 420, t, a, n=22, col=C(167, 139, 250), amp=30)
    t0 = LIST_BEAT[0]
    put(ctx, GT('La lista', 30, MUTE, 'Medium'), 70, 150, alpha=a * eo(prog(t, t0 + 0.1, 0.4)), ax=0)
    put(ctx, GT('14 librerías de componentes', 60, WHITE, 'SemiBold'), 70, 214, alpha=a * eo(prog(t, t0 + 0.2, 0.5)), ax=0)
    put(ctx, GT('Link en los comentarios', 26, C(167, 139, 250), 'Medium'), 70, 266, alpha=a * eo(prog(t, T(160) - 0.1, 0.4)), ax=0)
    for j, (nm, dom, p) in enumerate(LIBS):
        k = pop(t, t0 + 0.45 + 0.17 * j)                                         # rows cascade in, then the whole list holds
        if k <= 0.001: continue
        col, row = j % 2, j // 2
        x = 50 + col * 500; y = 320 + row * 152
        aa = a * c01(k * 1.4); dy = 24 * (1 - k)
        rr(ctx, x, y + dy, 480, 136, 18); rgba(ctx, CARD, aa); ctx.fill_preserve(); rgba(ctx, LINE, aa); ctx.set_line_width(1.5); ctx.stroke()
        paint(ctx, p, None, x + 12, y + 12 + dy, 180, 112, aa, r=10)
        g_ = GRADS[j % len(GRADS)]
        ctx.arc(x + 216, y + 50 + dy, 7, 0, 2 * math.pi); rgba(ctx, GRAD[g_][1], aa); ctx.fill()
        put(ctx, GT('%02d' % (j + 1), 20, MUTE, 'Medium'), x + 232, y + 50 + dy, alpha=aa, ax=0)
        tt = GT(nm, 30, WHITE, 'SemiBold'); s_ = min(1.0, 250 / tt[4])
        put(ctx, tt, x + 210, y + 88 + dy, scale=s_, alpha=aa, ax=0)
        td = MT(dom, 17, MUTE); s2 = min(1.0, 255 / td[4])
        put(ctx, td, x + 210, y + 118 + dy, scale=s2, alpha=aa, ax=0)

# ---------------- title (over the hook) ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = [['14', 'librerías', 'para'], ['que', 'tu', 'web', 'no'], ['parezca', 'hecha'], ['con', 'IA']]
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
            tt = GT(wd, 112, C(167, 139, 250) if wd in ('14', 'IA') else WHITE, 'SemiBold', shadow=10, shadow_a=200)
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
    draw_shape(ctx, t); list_beat(ctx, t); title(ctx, t); subtitles(ctx, t); progress(ctx, t)
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
