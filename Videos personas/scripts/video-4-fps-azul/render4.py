"""IMG_8856 — IG reel edited in the Fraud Prevention Series visual language (HDR HLG passthrough + SDR copy)."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from render import (cairo, np, Image, ImageFont, ImageDraw, ImageFilter, pil_surface, rrect, partial, jit,
                    c01, prog, eo, eio, eback, W, H, FPS)
import render as R
_scale = cairo.Context.scale
cairo.Context.scale = lambda self, sx, sy=None: _scale(self, max(sx, 1e-3), max(sx if sy is None else sy, 1e-3))
from edit4 import SEGS, src_of, seg_index, TOTAL, SRC

OUTRO = 1.35
DUR = TOTAL + OUTRO
SW, SH = 1440, 2560
FCX, FCY = 0.46, 0.26

# ---------------- FPS design tokens ----------------
FD = '/Users/acorrales/Desktop/Truora Marketing/fraud-series-hyperframes/assets/fonts/'
HG800, HG300, HG500, MONO = FD + 'HostGrotesk-800.woff2', FD + 'HostGrotesk-300.woff2', FD + 'HostGrotesk-500.woff2', FD + 'JetBrainsMono-400.woff2'
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
BLUE, FG, MUTED, ALERT, BLACK = hexc('0066FF'), hexc('FAFBFF'), hexc('8B8EA8'), hexc('EE792F'), hexc('000000')
def rgba(ctx, c, a=None): ctx.set_source_rgba(c[0], c[1], c[2], c[3] if a is None else a)

# ---------------- text (with tracking + cached blur variants) ----------------
_tc = {}
def T_(txt, font, size, col=FG, track=0.0, blur=0, shadow=False):
    """track in em (e.g. -0.045 headline, 0.2 mono labels)"""
    blur = int(round(blur / 3.0)) * 3
    key = (txt, font, size, col, track, blur, shadow)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(font, size)
    asc, desc = f.getmetrics(); ext = max(0, -f.getbbox('ÁÉÑ')[1])
    sp = track * size
    widths = [f.getlength(ch) + sp for ch in txt]; tw = max(1, sum(widths) - sp)
    pad = 8 + ext + blur * 2 + (22 if shadow else 0)
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    col8 = tuple(int(c * 255) for c in col[:3]) + (int(col[3] * 255),)
    def draw(d, fill):
        x = pad
        for ch, cw in zip(txt, widths):
            d.text((x, pad), ch, font=f, fill=fill); x += cw
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (0, 6))
    draw(ImageDraw.Draw(img), col8)
    if blur: img = img.filter(ImageFilter.GaussianBlur(blur))
    s, buf = pil_surface(img)
    r = (s, buf, w, h, tw, asc); _tc[key] = r; return r

def put(ctx, t, x, y, scale=1.0, alpha=1.0, ax=0.5, ay=0.5, rot=0.0):
    """ax is relative to the glyph run (0 = left edge of text, 0.5 = centre, 1 = right edge)"""
    s, _, w, h, tw, _ = t
    if alpha <= 0.002: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale)
    ctx.set_source_surface(s, -((w - tw) / 2 + tw * ax), -h * ay)
    ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(alpha); ctx.restore()

def expo_out(x): x = c01(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def expo_io(x):
    x = c01(x)
    if x in (0, 1): return x
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2
def back_out(x, s=1.7): return eback(x, s)
def p2in(x): x = c01(x); return x * x

def rise(ctx, t, t0, words, x, y, sizes, weights, cols, align='center', track=-0.045, stagger=0.1, dur=0.7, gap=0.26, t_out=None, bg=None):
    """FPS per-word rise: each word rises 8% of its height with blur resolving. words: list of strings."""
    ts = [T_(w, weights[i], sizes[i], cols[i], track) for i, w in enumerate(words)]
    total = sum(tt[4] for tt in ts) + sum(sizes[i] * gap for i in range(len(ts) - 1))
    cx = x - total / 2 if align == 'center' else x
    ko = 1.0
    if t_out is not None and t >= t_out:
        ko = 1 - p2in(prog(t, t_out, 0.4))
    for i, (wd, tt) in enumerate(zip(words, ts)):
        p = prog(t, t0 + i * stagger, dur)
        if p <= 0: cx += tt[4] + sizes[i] * gap; continue
        e = expo_out(p)
        bl = 12 * (1 - e) + (14 * (1 - ko) if ko < 1 else 0)
        tb = T_(wd, weights[i], sizes[i], cols[i], track, blur=bl)
        if bg is not None:
            pad = sizes[i] * 0.14; ext = sizes[i] * gap if i < len(words) - 1 else 0
            yy = y + sizes[i] * 0.08 * (1 - e)
            ctx.rectangle(cx - pad, yy - sizes[i] * 0.58, tt[4] + 2 * pad + ext, sizes[i] * 1.12); rgba(ctx, bg, e * ko); ctx.fill()
        put(ctx, tb, cx, y + sizes[i] * 0.08 * (1 - e) - (1 - ko) * 30, alpha=e * ko, ax=0)
        cx += tt[4] + sizes[i] * gap
    return total

# ---------------- FPS elements ----------------
def grid_bg(ctx, t, x=0, y=0, w=W, h=H, cell=120):
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    rgba(ctx, BLACK); ctx.paint()
    off = (t * 6) % cell
    ctx.set_line_width(1); rgba(ctx, FG, 0.10)
    xx = x - cell + off
    while xx < x + w: ctx.move_to(xx + 0.5, y); ctx.line_to(xx + 0.5, y + h); xx += cell
    yy = y - cell + off
    while yy < y + h: ctx.move_to(x, yy + 0.5); ctx.line_to(x + w, yy + 0.5); yy += cell
    ctx.stroke(); ctx.restore()

_rng = np.random.default_rng(7)
AMB = []
for i in range(34):
    side = i % 4
    s = [14, 22, 34, 22, 14, 56][i % 6]
    if side == 0: x, y = _rng.uniform(20, 150), _rng.uniform(250, 1700)
    elif side == 1: x, y = _rng.uniform(930, 1060), _rng.uniform(250, 1700)
    elif side == 2: x, y = _rng.uniform(40, 1040), _rng.uniform(220, 330)
    else: x, y = _rng.uniform(40, 1040), _rng.uniform(1560, 1700)
    AMB.append((x, y, s, i % 5 == 0, _rng.integers(0, 1000)))
def ambient(ctx, fi, n=34, gain=1.0, sides_only=False):
    for (x, y, s, white, seed) in AMB[:n]:
        if sides_only and 150 < x < 930: continue
        step = (fi // 9 + seed) % 7
        op = [0, 0.25, 0.5, 0.75, 1.0, 0.5, 0][step] * gain
        if op <= 0: continue
        ctx.rectangle(x, y, s, s); rgba(ctx, FG if white else BLUE, op * (0.5 if white else 1)); ctx.fill()

def corners_line(ctx, x, y, w, h, k=1.0, arm=54, lw=5, col=FG, alpha=1.0):
    ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_SQUARE); rgba(ctx, col, alpha)
    for (cx, cy, dx, dy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
        ctx.move_to(cx, cy + dy * arm * k); ctx.line_to(cx, cy); ctx.line_to(cx + dx * arm * k, cy); ctx.stroke()

def corner_targets(x, y, w, h, px=14, step=16, n=7):
    pts = []
    for (cx, cy, dx, dy) in [(x, y, 1, 1), (x + w - px, y, -1, 1), (x, y + h - px, 1, -1), (x + w - px, y + h - px, -1, -1)]:
        for i in range(n): pts.append((cx + dx * i * step, cy))
        for i in range(1, n): pts.append((cx, cy + dy * i * step))
    return pts
_prng = np.random.default_rng(11)
PIX_FROM = [(_prng.uniform(0, W), _prng.uniform(0, H), _prng.uniform(0, 0.55)) for _ in range(52)]
def corners_pixel(ctx, t, t0, box, contract=40, alpha=1.0):
    x, y, w, h = box
    lock = expo_out(prog(t, t0 + 1.0, 0.55))
    x += contract * lock; y += contract * lock; w -= 2 * contract * lock; h -= 2 * contract * lock
    tg = corner_targets(x, y, w, h)
    for i, (tx, ty) in enumerate(tg):
        fx, fy, d = PIX_FROM[i % len(PIX_FROM)]
        p = expo_out(prog(t, t0 + d, 0.45))
        if p <= 0: continue
        s = 24 - 10 * p
        px_, py_ = fx + (tx - fx) * p, fy + (ty - fy) * p
        col = tuple(BLUE[j] + (FG[j] - BLUE[j]) * lock for j in range(3)) + (1,)
        ctx.rectangle(px_, py_, s, s); rgba(ctx, col, alpha); ctx.fill()

def mono_label(ctx, t, t0, txt, x, y, size=26, col=FG, blink=True, fi=0, ax=0.0, sq=BLUE):
    if t < t0: return
    e = expo_out(prog(t, t0, 0.7))
    tt = T_(txt.upper(), MONO, size, col, 0.2)
    xx = x if ax == 0 else x - (tt[4] + 30) * ax
    if blink and ((fi // 13) % 2 == 0 or t < t0 + 0.5):
        ctx.rectangle(xx, y - size * 0.36 + 24 * (1 - e), size * 0.6, size * 0.6); rgba(ctx, sq, e); ctx.fill()
    put(ctx, tt, xx + size * 0.6 + 14, y + 24 * (1 - e), alpha=e, ax=0)

def glass(ctx, x, y, w, h, r=26, alpha=1.0, fill_a=0.62):
    rrect(ctx, x, y, w, h, r); ctx.set_source_rgba(0.06, 0.06, 0.11, fill_a * alpha); ctx.fill()
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.10 * alpha); g.add_color_stop_rgba(0.35, 1, 1, 1, 0.02 * alpha); g.add_color_stop_rgba(1, 1, 1, 1, 0.0)
    rrect(ctx, x, y, w, h, r); ctx.set_source(g); ctx.fill()
    rrect(ctx, x + 1, y + 1, w - 2, h - 2, r); ctx.set_source_rgba(0.98, 0.98, 1, 0.20 * alpha); ctx.set_line_width(2); ctx.stroke()

def check_icon(ctx, x, y, r, t, t0, col=FG):
    p = prog(t, t0, 0.5)
    if p <= 0: return
    s = 0.6 + 0.4 * back_out(p, 2.0); rot = math.radians(-18) * (1 - expo_out(p))
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.arc(0, 0, r, 0, 2 * math.pi); rgba(ctx, col, c01(p * 3)); ctx.set_line_width(4); ctx.stroke()
    partial(ctx, [(-r * 0.42, 0), (-r * 0.1, r * 0.3), (r * 0.45, -r * 0.32)], prog(t, t0 + 0.12, 0.35), 5, col)
    ctx.restore()

def x_icon(ctx, x, y, s, col, lw=3):
    ctx.move_to(x - s, y - s); ctx.line_to(x + s, y + s); ctx.move_to(x + s, y - s); ctx.line_to(x - s, y + s)
    rgba(ctx, col); ctx.set_line_width(lw); ctx.stroke()

def pill(ctx, x, y, label, k=1.0, fill=None, tcol=FG, size=40, sq=BLUE, glassy=True, alpha=1.0):
    tt = T_(label, HG500, size, tcol, -0.01)
    w, h = tt[4] + 104, size * 2.1
    ctx.save(); ctx.translate(x, y + 40 * (1 - k)); a = c01(k) * alpha
    if glassy and fill is None: glass(ctx, -w / 2, -h / 2, w, h, h / 2, a)
    else: rrect(ctx, -w / 2, -h / 2, w, h, h / 2); rgba(ctx, fill, a); ctx.fill()
    ctx.rectangle(-w / 2 + 36, -7, 14, 14); rgba(ctx, sq, a); ctx.fill()
    put(ctx, tt, -w / 2 + 64, 2, alpha=a, ax=0)
    ctx.restore()
    return w

# pixel grid wipe (vertical: 9 x 16 cells of 120 px)
def grid_wipe(ctx, t, tc, col=BLUE):
    if not (tc - 0.42 <= t < tc + 0.42): return
    for r_ in range(16):
        for c_ in range(9):
            cx, cy = c_ * 120 + 60, r_ * 120 + 60
            d = math.hypot((c_ - 4) / 4.5, (r_ - 7.5) / 8) / 1.42
            if t < tc: s = expo_out(prog(t, tc - 0.42 + d * 0.22, 0.2))
            else: s = 1 - expo_out(prog(t, tc + (1 - d) * 0.22, 0.2))
            if s <= 0: continue
            hs = 60 * s + 0.6
            ctx.rectangle(cx - hs, cy - hs, 2 * hs, 2 * hs)
    rgba(ctx, col); ctx.fill()

# ---------------- words / subtitles ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {0: 'Les', 7: 'Claude', 13: 'graphics,', 23: 'Y', 24: 'quien', 27: 'pues,', 28: 'pucha,', 38: 'virales.', 43: 'página,',
       46: 'skill,', 73: 'Claude.', 75: 'decir,', 82: 'dé', 83: 'súper', 88: 'Claude.', 89: 'Ya', 99: 'Ahora', 106: 'súper',
       109: 'Claude,', 115: 'mejor.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
def _map(i):
    """scene cues were authored against the previous transcript; map old word index -> current index"""
    if i <= 81: return i
    if i == 82: return 83
    if 83 <= i <= 101: return i + 2
    if i == 102: return 104
    if i == 103: return 106
    return i + 4
def T(i): return _ws[_map(i)]['start']

def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) for x in cur)
        if (len(cur) >= 3 or chars >= 15 or w[2][-1] in '.,?' or nxt is None or nxt[0] - w[1] > 0.35
                or (nxt and len(nxt[2]) > 10 and chars > 8)):
            ch.append(cur); cur = []
    out = []
    for i, c in enumerate(ch):
        st = c[0][0] - 0.03
        en = ch[i + 1][0][0] - 0.03 if i + 1 < len(ch) else c[-1][1] + 0.4
        out.append((st, min(en, c[-1][1] + 0.5), c))
    return out
CHUNKS = build_chunks()

def subtitles(ctx, t, y):
    for st, en, ws in CHUNKS:
        if st <= t < en: break
    else: return
    size = 64; gap = size * 0.28
    parts = []
    for (a, b, w) in ws:
        active = a - 0.03 <= t < b + 0.02 or (w == ws[-1][2] and t >= a)
        parts.append((T_(w, HG800, size, FG, -0.03, shadow=not active), active))
    total = sum(p[0][4] for p in parts) + gap * (len(parts) - 1)
    sc = min(1.0, 940 / total)
    e = expo_out(prog(t, st, 0.35)); al = e
    x = W / 2 - total * sc / 2
    for tt, active in parts:
        ww = tt[4] * sc
        yy = y + 16 * (1 - e)
        if active:
            ctx.rectangle(x - 12 * sc, yy - size * 0.62 * sc, ww + 24 * sc, size * 1.2 * sc); rgba(ctx, BLUE, al); ctx.fill()
        put(ctx, tt, x, yy, scale=sc, alpha=al, ax=0)
        x += ww + gap * sc

# ---------------- scenes ----------------
def hud(ctx, t, fi, a=1.0):
    e = c01((t - 0.4) / 1.0) * a
    if e <= 0: return
    put(ctx, T_('CLAUDE · EDICIÓN', MONO, 22, FG, 0.2), 60, 150, alpha=e * 0.85, ax=0)
    for i, w in enumerate(['EDITAR', 'ANIMAR', 'ESCALAR']):
        put(ctx, T_(w, MONO, 17, MUTED, 0.2), 1020, 140 + i * 24, alpha=e, ax=1)

def s1_front(ctx, t, fi):  # hook: pixel corners fly in and lock around the face + UNA IDEA
    k = expo_out(prog(t, 0.05, 0.9))
    corners_line(ctx, 230 - 120 * (1 - k), 110 - 120 * (1 - k), 620 + 240 * (1 - k), 740 + 240 * (1 - k), 1, 64, 6, FG, k)
    if t > T(4) - 0.1:
        glass(ctx, 300, 950, 480, 96, 48, expo_out(prog(t, T(4) - 0.1, 0.6)))
        mono_label(ctx, t, T(4) - 0.05, 'Una idea', 345, 998, 32, FG, True, fi)

ROWS = [(T(9) - 0.05, 'Editar videos'), (T(12) - 0.05, 'Motion graphics'), (T(16) - 0.05, 'De todo')]
def s2_front(ctx, t, fi):  # capacidades panel (telemetry rows + success check)
    t0 = T(7) - 0.1
    if t < t0: return
    e = expo_out(prog(t, t0, 1.0))
    x, y, w, h = 90, 880, 900, 540
    ctx.save(); ctx.translate(0, 100 * (1 - e))
    glass(ctx, x, y, w, h, 28, e)
    mono_label(ctx, t, t0 + 0.2, 'Claude ya puede', x + 44, y + 62, 30, MUTED, True, fi)
    for i, (ti, lab) in enumerate(ROWS):
        ry = y + 150 + i * 98
        ctx.rectangle(x + 44, ry + 50, w - 88, 1); rgba(ctx, FG, 0.14 * e); ctx.fill()
        if t < ti: continue
        a = expo_out(prog(t, ti, 0.5))
        ctx.rectangle(x + 44, ry - 8, 16, 16); rgba(ctx, FG, a); ctx.fill()
        put(ctx, T_(lab, HG500, 44, FG, -0.01), x + 84, ry + 1, alpha=a, ax=0)
        put(ctx, T_('SÍ', MONO, 34, FG, 0.12), x + w - 44, ry + 1, alpha=a, ax=1)
    tc = T(21) - 0.1
    check_icon(ctx, x + 80, y + h - 72, 34, t, tc)
    if t >= tc + 0.1:
        rise(ctx, t, tc + 0.1, ['Ahora', 'mismo.'], x + 135, y + h - 72, [60, 60], [HG800, HG300], [FG, FG], align='left', stagger=0.08)
    ctx.restore()

def s3_card(ctx, t, fi):  # "Quien cree esto / va a ser increíble."
    grid_bg(ctx, t); ambient(ctx, fi); hud(ctx, t, fi)
    t0 = T(23)
    k = expo_out(prog(t, t0 - 0.05, 0.7))
    corners_line(ctx, 90 - 30 * (1 - k), 560 - 30 * (1 - k), 900 + 60 * (1 - k), 560 + 60 * (1 - k), 1, 60, 6, FG, k)
    mono_label(ctx, t, t0, 'La idea', 140, 640, 26, FG, True, fi)
    rise(ctx, t, T(24) - 0.05, ['Quien', 'cree', 'esto'], 540, 800, [118] * 3, [HG800] * 3, [FG] * 3)
    rise(ctx, t, T(29) - 0.05, ['va', 'a', 'ser'], 540, 940, [104] * 3, [HG300] * 3, [FG] * 3, stagger=0.06)
    rise(ctx, t, T(32) - 0.05, ['increíble.'], 540, 1075, [118], [HG800], [FG], bg=BLUE)

def s4_front(ctx, t, fi):  # viral
    ta = T(37) - 0.1
    if t < ta: return
    pill(ctx, 540, 1080, 'Se vuelve viral', expo_out(prog(t, ta, 0.6)), BLUE, FG, 50, FG, glassy=False)

CHIPS = [(T(42) - 0.05, 'Una página'), (T(45) - 0.05, 'Un skill'), (T(49) - 0.05, 'Lo que sea')]
def s5_card(ctx, t, fi):  # split bottom: state-chip rail with travelling highlight
    t0 = CHIPS[0][0] - 0.3
    mono_label(ctx, t, t0, 'Alguien que haga', 120, 1100, 26, MUTED, True, fi)
    ys = [1210, 1330, 1450]
    # travelling highlight
    idx = sum(1 for ti, _ in CHIPS if t >= ti) - 1
    if idx >= 0:
        prev = max(0, idx - 1)
        u = expo_io(prog(t, CHIPS[idx][0], 0.5))
        hy = ys[prev] + (ys[idx] - ys[prev]) * u if idx > 0 else ys[0]
        rrect(ctx, 110, hy - 50, 560, 100, 50); rgba(ctx, BLUE); ctx.fill()
    for i, (ti, lab) in enumerate(CHIPS):
        k = expo_out(prog(t, ti - 0.25, 0.6))
        if k <= 0: continue
        on = idx == i
        tt = T_(lab, HG800 if on else HG300, 58, FG, -0.03)
        ctx.save(); ctx.translate(0, 40 * (1 - k))
        if not on:
            rrect(ctx, 110, ys[i] - 50, 560, 100, 50); ctx.set_source_rgba(1, 1, 1, 0.06 * k); ctx.fill()
            rrect(ctx, 111, ys[i] - 49, 558, 98, 49); ctx.set_source_rgba(1, 1, 1, 0.22 * k); ctx.set_line_width(2); ctx.stroke()
        ctx.rectangle(150, ys[i] - 7, 14, 14); rgba(ctx, FG, k); ctx.fill()
        put(ctx, tt, 190, ys[i] + 2, alpha=k, ax=0)
        ctx.restore()
    corners_line(ctx, 740, 1180, 250, 300, 1, 40, 5, FG, 0.5)
    put(ctx, T_('01', HG800, 150, BLUE, -0.04), 865, 1330, alpha=0.9 if idx == 0 else 0.0)
    put(ctx, T_('02', HG800, 150, BLUE, -0.04), 865, 1330, alpha=0.9 if idx == 1 else 0.0)
    put(ctx, T_('03', HG800, 150, BLUE, -0.04), 865, 1330, alpha=0.9 if idx == 2 else 0.0)

TERMS1 = ['Transiciones', 'Textos', 'Gráficos', 'Elementos', 'Librerías', 'Zooms']
TERMS2 = ['Subtítulos', 'Sonido', 'Motion graphics', 'Plantillas', 'Efectos', 'Cortes']
PLATE = [(T(55), 'Librerías'), (T(57), 'Transiciones'), (T(59), 'Textos'), (T(61), 'Gráficos'), (T(63), 'Elementos'), (T(65), 'y más.')]
def ribbon(ctx, t, y, rot, terms, speed, bg, fg, xcol, t0):
    k = expo_out(prog(t, t0, 0.9))
    ctx.save(); ctx.translate(540 + (1 - k) * 1400 * (1 if speed > 0 else -1), y); ctx.rotate(rot)
    ctx.rectangle(-1100, -52, 2200, 104); rgba(ctx, bg); ctx.fill()
    items = []
    for s in terms: items.append(T_(s, HG500, 44, fg, -0.01))
    seglen = sum(tt[4] + 110 for tt in items)
    off = (t * speed) % seglen
    x = -1100 - seglen + off
    while x < 1100:
        for tt in items:
            put(ctx, tt, x, 2, ax=0); x_icon(ctx, x + tt[4] + 55, 0, 11, xcol, 4); x += tt[4] + 110
    ctx.restore()

def s6_card(ctx, t, fi):  # libraries: ribbons + plate that switches with each spoken item
    grid_bg(ctx, t); ambient(ctx, fi); hud(ctx, t, fi)
    t0 = T(52) - 0.2
    mono_label(ctx, t, t0, 'Donde esté cargado', 120, 330, 26, MUTED, True, fi)
    ribbon(ctx, t, 520, -0.12, TERMS1, 150, BLUE, FG, FG, t0)
    ribbon(ctx, t, 1330, 0.10, TERMS2, -150, FG, BLACK, BLUE, t0 + 0.15)
    e = expo_out(prog(t, t0 + 0.2, 0.8))
    glass(ctx, 100, 760, 880, 340, 30, e, 0.78)
    corners_line(ctx, 100, 760, 880, 340, 1, 44, 5, FG, e)
    cur = None
    for i, (ti, lab) in enumerate(PLATE):
        if t >= ti - 0.05: cur = (i, ti, lab)
    if cur is None:
        rise(ctx, t, t0 + 0.4, ['Las', 'librerías'], 540, 930, [96, 96], [HG300, HG800], [FG, FG])
    else:
        i, ti, lab = cur
        p = expo_out(prog(t, ti - 0.05, 0.45))
        tt = T_(lab, HG800, 112, BLUE if i == len(PLATE) - 1 else FG, -0.045, blur=10 * (1 - p))
        put(ctx, tt, 540, 930 + 30 * (1 - p), alpha=p)
        put(ctx, T_('%02d / %02d' % (i + 1, len(PLATE)), MONO, 22, MUTED, 0.2), 950, 800, alpha=e, ax=1)

def s7_front(ctx, t, fi):  # detection frame locks on face
    t0 = T(68) - 0.05
    k = expo_out(prog(t, t0, 0.8))
    corners_line(ctx, 150 - 80 * (1 - k), 90 - 80 * (1 - k), 780 + 160 * (1 - k), 820 + 160 * (1 - k), 1, 64, 6, FG, k)
    tl = T(70) - 0.05
    if t >= tl:
        glass(ctx, 190, 950, 700, 96, 48, expo_out(prog(t, tl, 0.6)))
        mono_label(ctx, t, tl, 'Editar bien con Claude', 235, 998, 28, FG, True, fi)

def s8_front(ctx, t, fi):  # súper poderes de edición
    ts = T(82) - 0.1
    if t < ts: return
    e = expo_out(prog(t, ts, 0.8))
    glass(ctx, 90, 920, 900, 420, 30, e)
    corners_line(ctx, 90, 920, 900, 420, 1, 50, 5, FG, e)
    mono_label(ctx, t, ts + 0.05, 'Le da', 150, 1000, 26, MUTED, True, fi)
    rise(ctx, t, ts + 0.05, ['Súper'], 540, 1110, [140], [HG800], [FG])
    rise(ctx, t, ts + 0.2, ['poderes'], 540, 1225, [120], [HG300], [FG], bg=BLUE)
    tt = T(83) - 0.05
    if t >= tt: put(ctx, T_('DE EDICIÓN', MONO, 26, FG, 0.2), 540, 1302, alpha=expo_out(prog(t, tt, 0.5)))

def s9_front(ctx, t, fi):  # ya lo tenemos (success check) + editar activo
    tc = T(87) - 0.05
    if t < tc: return
    e = expo_out(prog(t, tc, 0.8))
    glass(ctx, 110, 950, 860, 180, 90, e)
    check_icon(ctx, 210, 1040, 44, t, tc + 0.1)
    rise(ctx, t, tc + 0.2, ['Ya', 'lo', 'tenemos.'], 290, 1040, [66, 66, 66], [HG800, HG300, HG300], [FG, FG, FG], align='left', stagger=0.08)
    ta = T(94) - 0.05
    if t >= ta:
        pill(ctx, 540, 1215, 'Editar · activo', expo_out(prog(t, ta, 0.6)), None, FG, 40, BLUE)

NODES = ['Transiciones', 'Textos', 'Gráficos', 'Sonido', 'Subtítulos', 'Zooms']
def s10_card(ctx, t, fi):  # constellation hub: paquetes → Claude
    grid_bg(ctx, t); ambient(ctx, fi); hud(ctx, t, fi)
    t0 = T(97)
    rise(ctx, t, T(99) - 0.1, ['Paquetes', 'de'], 540, 390, [92, 92], [HG300, HG300], [FG, FG])
    rise(ctx, t, T(103) - 0.12, ['súper', 'poderes.'], 540, 515, [104, 104], [HG800, HG800], [FG, FG], bg=BLUE)
    cx, cy, cw, ch = 540, 1010, 330, 130
    ce = expo_out(prog(t, t0, 0.8))
    filled = expo_out(prog(t, T(105) - 0.1, 0.5))
    rrect(ctx, cx - cw / 2, cy - ch / 2, cw, ch, 24); rgba(ctx, BLUE, filled * ce); ctx.fill()
    glass(ctx, cx - cw / 2, cy - ch / 2, cw, ch, 24, ce, 0.62 * (1 - filled))
    corners_line(ctx, cx - cw / 2 - 26 - 60 * (1 - ce), cy - ch / 2 - 26 - 60 * (1 - ce), cw + 52 + 120 * (1 - ce), ch + 52 + 120 * (1 - ce), 1, 30, 4, FG, ce)
    put(ctx, T_('Claude', HG800, 70, FG, -0.04), cx, cy + 2, alpha=ce)
    for i, lab in enumerate(NODES):
        side = -1 if i < 3 else 1; row = i % 3
        nw, nh = 300, 92
        nx = 40 if side < 0 else W - 40 - nw
        ny = 790 + row * 220
        tl = t0 + 0.15 + i * 0.28
        p = expo_io(prog(t, tl, 0.5))
        if p <= 0: continue
        # right-angle connector: centre edge -> elbow -> node edge
        sx = cx + side * cw / 2; sy = cy + (row - 1) * 36
        ex = nx + (nw if side < 0 else 0); ey = ny + nh / 2
        mx = (sx + ex) / 2
        pts = [(sx, sy), (mx, sy), (mx, ey), (ex, ey)]
        dense = []
        for (ax_, ay_), (bx_, by_) in zip(pts, pts[1:]):
            for u in np.linspace(0, 1, 16): dense.append((ax_ + (bx_ - ax_) * u, ay_ + (by_ - ay_) * u))
        partial(ctx, dense, p, 3, BLUE if filled < 0.5 else FG)
        ctx.rectangle(sx - 5, sy - 5, 10, 10); rgba(ctx, FG, p); ctx.fill()
        if p >= 1:
            # pulses travelling node -> centre
            for k_ in range(2):
                u = ((t - tl) * 0.8 + k_ * 0.5) % 1
                idx = int((1 - u) * (len(dense) - 1))
                qx, qy = dense[idx]
                ctx.rectangle(qx - 7, qy - 7, 14, 14); rgba(ctx, BLUE); ctx.fill()
                ctx.rectangle(qx - 3, qy - 3, 6, 6); rgba(ctx, FG); ctx.fill()
        ne = expo_out(prog(t, tl + 0.35, 0.6))
        if ne > 0:
            ctx.save(); ctx.translate(0, 30 * (1 - ne))
            glass(ctx, nx, ny, nw, nh, 20, ne)
            ctx.rectangle(ex - 4, ey - 4, 8, 8); rgba(ctx, FG, ne); ctx.fill()
            put(ctx, T_(lab, HG500, 38, FG, -0.01), nx + nw / 2, ny + nh / 2 + 2, alpha=ne)
            ctx.restore()

def s11_front(ctx, t, fi):  # 10x count-up
    t0 = T(109) - 0.35
    if t < t0: return
    e = expo_out(prog(t, t0, 0.6))
    box = (150, 1010, 780, 390)
    glass(ctx, *box, 30, e, 0.7)
    corners_line(ctx, *box, 1, 50, 5, FG, e)
    n = int(round(10 * expo_out(prog(t, t0 + 0.1, 0.9))))
    num = T_(str(n), HG800, 250, FG, -0.045); xx = T_('x', HG800, 250, BLUE, -0.045)
    tw = num[4] + xx[4]
    put(ctx, num, 540 - tw / 2, 1175, scale=0.94 + 0.06 * e, alpha=e, ax=0)
    put(ctx, xx, 540 - tw / 2 + num[4], 1175, scale=0.94 + 0.06 * e, alpha=e, ax=0)
    tm = T(111) - 0.05
    if t >= tm: mono_label(ctx, t, tm, 'Mejor', 430, 1340, 32, FG, True, fi)

def outro_card(ctx, t, fi):
    grid_bg(ctx, t); ambient(ctx, fi); hud(ctx, t, fi)
    t0 = TOTAL + 0.05
    mono_label(ctx, t, t0, 'Una idea para construir', 120, 700, 26, MUTED, True, fi)
    rise(ctx, t, t0 + 0.1, ['Súper', 'poderes'], 540, 860, [128, 128], [HG800, HG300], [FG, FG])
    rise(ctx, t, t0 + 0.35, ['para', 'Claude.'], 540, 1000, [118, 118], [HG300, HG800], [FG, FG], bg=BLUE)
    corners_line(ctx, 70, 740, 940, 380, 1, 50, 5, FG, expo_out(prog(t, t0, 0.8)))
    # final pixel dissolve to black
    dp = prog(t, DUR - 0.55, 0.5)
    if dp > 0:
        rng = np.random.default_rng(5)
        order = rng.permutation(9 * 16)
        n = int(dp * len(order))
        for j in order[:n]:
            r_, c_ = divmod(int(j), 9)
            ctx.rectangle(c_ * 120, r_ * 120, 120, 120)
        rgba(ctx, BLACK); ctx.fill()

# shot list ------------------------------------------------------------
def S(t0, t1, kind, front=None, zoom=None, extra=None): return dict(t0=t0, t1=t1, kind=kind, front=front, zoom=zoom, extra=extra or {})
C3a, C3b = T(23) - 0.02, T(33) - 0.02
C6a, C6b = T(52) - 0.25, T(68) - 0.02
C10a, C10b = T(97) - 0.02, T(106) - 0.02
SHOTS = [
    S(0.0, T(5) - 0.02, 'face', s1_front, 'hook'),
    S(T(5) - 0.02, C3a, 'face', s2_front),
    S(C3a, C3b, 'card', s3_card),
    S(C3b, T(39) - 0.02, 'face', s4_front, 1.34),
    S(T(39) - 0.02, C6a, 'split', s5_card),
    S(C6a, C6b, 'card', s6_card),
    S(C6b, T(74) - 0.02, 'face', s7_front, 1.0),
    S(T(74) - 0.02, T(87) - 0.02, 'face', s8_front),
    S(T(87) - 0.02, C10a, 'face', s9_front),
    S(C10a, C10b, 'card', s10_card),
    S(C10b, TOTAL, 'face', s11_front),
    S(TOTAL, 999, 'card', outro_card),
]
WIPES = [C3a, C3b, C6a, C6b, C10a, C10b, TOTAL]
def shot_at(t):
    for s in SHOTS:
        if s['t0'] <= t < s['t1']: return s
    return SHOTS[-1]

ZCYCLE = [1.0, 1.2, 1.08, 1.3]
BLOCKS = {}
def prebuild_blocks():
    order = []
    for fi in range(int(DUR * FPS)):
        t = fi / FPS; key = (seg_index(min(t, TOTAL - 0.001)), shot_at(t)['t0'])
        if key not in BLOCKS: BLOCKS[key] = t; order.append(key)
    for i, k in enumerate(order): BLOCKS[k] = (ZCYCLE[i % 4], BLOCKS[k])
def face_zoom(t):
    s = shot_at(t)
    zb, t0 = BLOCKS.get((seg_index(min(t, TOTAL - 0.001)), s['t0']), (1.1, s['t0']))
    if s['zoom'] == 'hook': return 1.0 + 0.28 * (1 - expo_out(prog(t, 0.0, 1.2)))
    base = s['zoom'] if s['zoom'] is not None else zb
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + 0.05 * (1 - eo(prog(t, t0, 0.28))))
def crop_box(z, size=(W, H), cx=FCX, cy=FCY):
    ow, oh = size; cw = SW / z; ch = cw * oh / ow
    x0 = min(max(cx * SW - cw / 2, 0), SW - cw); y0 = min(max(cy * SH - ch / 2, 0), SH - ch)
    return (x0, y0, x0 + cw, y0 + ch)

# ---------------- HDR / SDR compositing ----------------
M709_2020 = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]], np.float32)
_ha, _hb, _hc = 0.17883277, 0.28466892, 0.55991073
EREF = (math.exp((0.75 - _hc) / _ha) + _hb) / 12      # HLG scene light for 75% signal (BT.2408 reference white)
_lut = np.where(np.arange(256) / 255 <= 0.04045, (np.arange(256) / 255) / 12.92, ((np.arange(256) / 255 + 0.055) / 1.055) ** 2.4).astype(np.float32)
def srgb8_to_hlg(rgb8):
    l = _lut[rgb8]; M = M709_2020
    lin = np.stack([l[..., 0] * M[i, 0] + l[..., 1] * M[i, 1] + l[..., 2] * M[i, 2] for i in range(3)], -1)
    E = np.clip(lin * EREF, 1e-6, 1)
    return np.where(E <= 1 / 12, np.sqrt(3 * E), _ha * np.log(np.maximum(12 * E - _hb, 1e-6)) + _hc).astype(np.float32)

def resize_f(fr, box, size):
    return np.dstack([np.asarray(Image.fromarray(fr[..., c], 'F').resize(size, Image.BILINEAR, box=box)) for c in range(3)])

def layer_over(sdr, hdr, arr, y0=0):
    """composite a premultiplied BGRA8 cairo layer over both float buffers (SDR: signal-space sRGB, HDR: HLG)"""
    a8 = arr[..., 3]
    ys, xs = np.nonzero(a8)
    if len(ys) == 0: return
    a = a8[ys, xs].astype(np.float32)[:, None] / 255
    pm = arr[ys, xs][:, [2, 1, 0]].astype(np.float32) / 255
    col = np.clip(pm / np.maximum(a, 1e-4), 0, 1)
    c8 = np.clip(col * 255 + 0.5, 0, 255).astype(np.uint8)
    yy = ys + y0
    sdr[yy, xs] = pm + sdr[yy, xs] * (1 - a)
    hdr[yy, xs] = srgb8_to_hlg(c8) * a + hdr[yy, xs] * (1 - a)

def new_layer(h=H):
    arr = np.zeros((h, W, 4), np.uint8)
    s = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, h, W * 4)
    return arr, s, cairo.Context(s)

def render_frame(fr16, t, fi):
    s = shot_at(t); kind = s['kind']
    arr, surf, ctx = new_layer()
    sub_y = 1470
    if kind == 'face':
        z = face_zoom(t); base = resize_f(fr16, crop_box(z), (W, H))
        hud(ctx, t, fi)
        if s['front']: s['front'](ctx, t, fi)
    elif kind == 'split':
        base = np.zeros((H, W, 3), np.float32)
        base[:1000] = resize_f(fr16, crop_box(1.0, (W, 1000), cy=0.2), (W, 1000))
        ctx.save(); ctx.rectangle(0, 1000, W, H - 1000); ctx.clip(); grid_bg(ctx, t, 0, 1000, W, H - 1000); ambient(ctx, fi, 34); ctx.restore()
        ctx.rectangle(0, 996, W, 8); rgba(ctx, BLUE); ctx.fill()
        corners_line(ctx, 90, 70, 900, 860, 1, 50, 5, FG, expo_out(prog(t, s['t0'], 0.7)))
        hud(ctx, t, fi); s['front'](ctx, t, fi)
        sub_y = 1640
    else:
        base = np.zeros((H, W, 3), np.float32)
        s['front'](ctx, t, fi)
        sub_y = 1560
    for tc in WIPES: grid_wipe(ctx, t, tc)
    if t < TOTAL: subtitles(ctx, t, sub_y)
    surf.flush()
    sdr = base.copy(); hdr = base
    layer_over(sdr, hdr, arr)
    return sdr, hdr

# ---------------- sound design: real SFX (media-use bundled library) ----------------
SFXDIR = os.path.expanduser('~/.claude/skills/media-use/audio/assets/sfx/')
def _load(name):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', SFXDIR + name + '.mp3', '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'],
                       capture_output=True).stdout
    x = np.frombuffer(b, np.float32).copy()
    x /= (np.abs(x).max() + 1e-9)
    env = np.convolve(np.abs(x), np.ones(240) / 240, 'same')
    return x, int(np.argmax(env))            # sample, peak index (used to align the hit to the event time)
# kind -> (file, peak level dBFS, align on peak?)
SFXMAP = {'whoosh': ('whoosh', -17.0, True), 'pop': ('pop', -19.0, False), 'ding': ('ping', -23.0, False),
          'chime': ('chime', -21.0, False), 'click': ('key-press', -15.0, False), 'key': ('key-press', -17.0, False)}   # single dry transient; click-soft had a double hit + tail
EV = []
def build_events():
    ev = lambda k, a, g=0.0: EV.append(('click' if k in ('ding', 'chime') else k, a, g)) if k != 'pop' else None   # pop removed; ding/chime -> dry click (user preference)
    # transitions
    for tc in WIPES: ev('click', tc - 0.02, 1)           # transitions: click only (no whoosh)
    ev('click', T(39) - 0.02)                            # into split
    # stickers / labels / panels
    ev('pop', T(4) - 0.1); ev('pop', T(7) - 0.1, -2); ev('pop', T(37) - 0.1)
    for ti, _ in CHIPS: ev('pop', ti - 0.25, -2)
    ev('pop', T(70) - 0.05, -2); ev('pop', T(82) - 0.1); ev('pop', T(87) - 0.05, -2); ev('pop', T(94) - 0.05, -3)
    ev('pop', TOTAL + 0.1, -3)
    # key data -> soft ding
    ev('ding', T(21) - 0.05); ev('ding', T(32) - 0.05); ev('ding', T(87) + 0.12)
    ev('ding', T(105) - 0.1, 1); ev('chime', T(110) - 0.02)
    # clicks: rows, plate switches, chip highlight, graph connections, labels
    for ti, _ in ROWS: ev('click', ti)
    for ti, _ in PLATE[1:]: ev('click', ti - 0.05, -2)
    for ti, _ in CHIPS[1:]: ev('click', ti, -1)
    for i in range(6): ev('key', T(97) + 0.15 + i * 0.28, -2)
    ev('click', T(24) - 0.05, -3); ev('click', T(29) - 0.05, -4)
    # a dry click on every zoom jump-cut (face shots), skipping ones that already have a click nearby
    for (seg, shot_t0), (z, t0) in sorted(BLOCKS.items(), key=lambda kv: kv[1][1]):
        if t0 < 0.2 or shot_at(t0)['kind'] != 'face': continue
        if any(k == 'click' and abs(a_ - t0) < 0.25 for k, a_, _ in EV): continue
        EV.append(('click', t0 - 0.01, -1.0))

def build_audio():
    """mix.wav = voice only (A). mix_B.wav = voice + crisp band-limited click on zoom cuts / transitions only (B)."""
    SR = 48000
    with wave.open(os.path.join(HERE, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(DUR * SR)
    def save(name, m):
        m = m[:n]; pk = np.abs(m).max()
        if pk > 0.97: m = m * (0.97 / pk)
        with wave.open(os.path.join(HERE, name), 'wb') as o:
            o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((m * 32767).astype(np.int16).tobytes())
    base = np.zeros((n + SR, 2), np.float32); base[:len(v)] += v
    save('mix.wav', base.copy())
    rng = np.random.default_rng(1); L = int(0.008 * SR); tt = np.arange(L) / SR
    F = np.fft.rfft(rng.normal(0, 1, 4096)); f = np.fft.rfftfreq(4096, 1 / SR)
    F *= np.exp(-0.5 * ((np.log(np.maximum(f, 1)) - np.log(4000)) / 0.45) ** 2)
    click = np.fft.irfft(F)[:L] * np.exp(-tt * 750) * np.minimum(1, tt / 0.0002)
    click = click / np.abs(click).max() * 10 ** (-20 / 20)
    times = set(round(t, 3) for t in WIPES); times.add(round(T(39) - 0.02, 3))
    for (seg, st), (z, t0) in BLOCKS.items():
        if t0 > 0.2 and shot_at(t0)['kind'] == 'face': times.add(round(t0, 3))
    keep = []
    for t in sorted(times):
        if not keep or t - keep[-1] > 0.3: keep.append(t)
    for t in keep:
        i0 = int((t - 0.01) * SR); base[i0:i0 + L] += click[:, None]
    save('mix_B.wav', base)
    print('B clicks', len(keep))

def build_audio_old():
    with wave.open(os.path.join(HERE, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    SR = 48000
    mix = np.zeros((int((DUR + 1) * SR), 2), np.float32); mix[:len(v)] += v
    cache = {k: _load(f) for k, (f, _, _) in SFXMAP.items()}
    rng = np.random.default_rng(3)
    for kind, at, gdb in EV:
        x, pk = cache[kind]; _, lvl, align = SFXMAP[kind]
        r = rng.uniform(0.96, 1.04)                                   # small pitch/tempo variation per hit
        n2 = int(len(x) / r); y = np.interp(np.arange(n2) * r, np.arange(len(x)), x)
        y *= 10 ** ((lvl + gdb) / 20)
        i0 = int(at * SR) - (int(pk / r) if align else 0)
        if i0 < 0: y = y[-i0:]; i0 = 0
        seg = mix[i0:i0 + len(y)]; n = len(seg); pan = rng.uniform(-0.15, 0.15)
        seg[:, 0] += y[:n] * (1 - pan); seg[:, 1] += y[:n] * (1 + pan)
    mix = mix[:int(DUR * SR)]
    pk = np.abs(mix).max()
    if pk > 0.97: mix *= 0.97 / pk
    with wave.open(os.path.join(HERE, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------- io ----------------
def reader():
    cmd = ['ffmpeg', '-v', 'error', '-i', SRC, '-vf',
           'fps=30,scale=1440:2560:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
           '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 6)
    k = 0
    while True:
        b = p.stdout.read(SW * SH * 6)
        if len(b) < SW * SH * 6: break
        yield k, b; k += 1
    p.kill()

def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    it = reader(); cur_k, cur_b = next(it)
    for fi in want:
        t = fi / FPS
        st = src_of(min(t, TOTAL - 0.001)) + max(0, t - TOTAL)
        k = int(round(st * FPS))
        while cur_k < k:
            try: cur_k, cur_b = next(it)
            except StopIteration: break
        fr = np.frombuffer(cur_b, np.uint16).reshape(SH, SW, 3).astype(np.float32) / 65535
        yield fi, t, fr

def to8(x): return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
def to16(x): return (np.clip(x, 0, 1) * 65535 + 0.5).astype(np.uint16)

def main():
    prebuild_blocks(); build_events()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(HERE, 'prev'), exist_ok=True)
        for fi, t, fr in frames(times):
            sdr, hdr = render_frame(fr, t, fi)
            Image.fromarray(to8(sdr)).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    out_hdr, out_sdr = sys.argv[2], sys.argv[3]
    common = ['-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)]
    enc_h = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb48le', '-color_range', 'pc', '-i', '-',
                             '-i', os.path.join(HERE, 'mix.wav'),
                             '-vf', 'scale=out_color_matrix=bt2020:in_range=pc:out_range=tv:flags=bicubic+accurate_rnd,format=yuv420p10le',
                             '-c:v', 'libx265', '-crf', '17', '-preset', 'medium', '-tag:v', 'hvc1',
                             '-x265-params', 'colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error',
                             '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_hdr], stdin=subprocess.PIPE)
    enc_s = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb24', '-i', '-',
                             '-i', os.path.join(HERE, 'mix.wav'),
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                             '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
                             '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_sdr], stdin=subprocess.PIPE)
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t, fi)
        enc_h.stdin.write(np.ascontiguousarray(to16(hdr)).tobytes())
        enc_s.stdin.write(np.ascontiguousarray(to8(sdr)).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    for e in (enc_h, enc_s): e.stdin.close()
    for e in (enc_h, enc_s): e.wait()
    print('done', out_hdr, out_sdr)

if __name__ == '__main__':
    main()
