"""IMG_8957 · treg.to — "Dale superpoderes a tu Claude". 1.05x, voice only (no SFX / music).
NO camera movement at all (user: zooms look shaky): full frame when full screen, one fixed crop for the top half of the split.
Split screens with the silent treg demo (window cropped) + 'treg.to' pill; drawn animations where there is no footage:
connected-apps diagram (Apollo, Lusha, Instantly -> search fans out -> result comes back), social scraping chips,
setup command highlight, big link CTA at the end. Subtitles: white Helvetica Neue Bold, active word in the teoría yellow."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit15 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {9: 'Claude', 14: 'vuelva', 28: 'treg', 29: '.to', 41: 'Claude.', 46: 'Claude', 57: 'contactarlas', 73: 'Lusha,',
       74: 'Instantly,', 119: 'scraping', 148: 'puedes', 165: 'esto.', 172: 'enruta', 175: '', 186: 'prompteando.', 195: 'game',
       196: 'changer.', 212: 'Claude', 213: 'Code.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [w for i, w in enumerate(WORDS) if w[2] and i not in (75,)]          # "Instant League" -> "Instantly"
def T(i): return _ws[i]['start']
def Te(i): return _ws[i]['end']

# ---------------- timeline: no title card, no holds -> voice time == output time ----------------
TH, HOLD, T_CARD = 1e9, 0.0, 1e9
def vt_of(t): return t
def out_of(vt): return vt
def vt_frame(t): return t
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 0.3
def in_card(t): return False

# ---------------- layout (voice time) ----------------
TITLE_END = 5.0
SPLITS = [(T(20) - 0.05, T(42) - 0.05, 'js_hero'),
          (T(60) - 0.05, T(99) - 0.05, 'apps'),
          (T(116) - 0.05, T(130) - 0.05, 'social'),
          (T(130) - 0.05, T(146) - 0.05, 'js_cheap'),
          (T(166) - 0.05, T(197) - 0.05, 'js_route'),
          (T(209) - 0.05, T(226) - 0.05, 'setup')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = [(a + (T(28) - 0.05 - a if k == 'js_hero' else 0), b, 'treg.to') for a, b, k in SPLITS]

# ---------------- speaker framing: one locked box per take ----------------
FT = {'a': framing.FaceTrack(os.path.join(HERE, 'faces_8957.txt'))}
def _take_box(s, lo, hi):
    ft = FT[s]; m = (ft.t >= lo) & (ft.t <= hi)
    b = ft.b[m] if m.any() else ft.box((lo + hi) / 2)[None]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 15); chin = np.percentile(b[:, 1] + b[:, 3], 85); h = chin - top
    return (cx - fw / 2, top - 0.12 * h, fw, h * 1.12)
TAKE_BOX = [_take_box(s, a, b) for s, a, b in E.SEGS]
CUTS = sorted({o / SPEED for o in E.OFF} | {a for a, b, k in SPLITS} | {b for a, b, k in SPLITS if b < VTOTAL})
ZC = [1.0, 1.08, 1.0, 1.14]
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6) if t >= CUTS[0] else 0
    t0 = CUTS[i] if t >= CUTS[0] else 0; base = ZC[i % 4]
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))
TOP_BOX = (0, 40, 1440, 1320)                 # one fixed crop for the split's top half (whole width, head + chin), never moves
def speaker(fr16, t, panel, extra=1.0):
    box = (0, 0, 1440, 2560) if panel[1] == H else TOP_BOX
    return fx.resize_f(fr16, box, panel)

# ---------------- bottom panels ----------------
REF = os.path.join(HERE, 'ref')
REC = DL + 'TREG.mp4'
WIN = 'crop=1404:880:131:116,scale=1080:677:flags=bicubic,pad=1080:960:0:150:0xFDFDFB'   # site window only (no wallpaper/widget), on the site's off-white
CLIPS = {'js_hero': [(0.2, 5.6)], 'js_cheap': [(24.4, 27.6)], 'js_route': [(17.6, 24.2)]}
def ff_frames(path, a, b, vf, n_out):
    rate = (b - a) / max(n_out / FPS, 1e-3)
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', path, '-an', '-vf',
                        f'setpts=PTS/{rate:.5f},fps={FPS},{vf},format=rgb24', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    sz = W * SEAM * 3; buf = p.stdout
    fr = [np.frombuffer(buf[i:i + sz], np.uint8).reshape(SEAM, W, 3) for i in range(0, len(buf) - sz + 1, sz)]
    return (fr + [fr[-1]] * max(0, n_out - len(fr)))[:n_out]
_clip = {}
def rec_frame(key, vt, a, b):
    if key not in _clip:
        n = int(round((b - a) * FPS)) + 2; parts = CLIPS[key]; tot = sum(y - x for x, y in parts); fr = []
        for k, (x, y) in enumerate(parts):
            m = n - len(fr) if k == len(parts) - 1 else int(round(n * (y - x) / tot))
            fr += ff_frames(REC, x, y, WIN, m)
        _clip[key] = fr
    fr = _clip[key]; return fr[min(len(fr) - 1, int(round((vt - a) * FPS)))]

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()

_shots = {}
def shot(name, width):
    key = (name, width)
    if key not in _shots:
        im = Image.open(os.path.join(REF, name)).convert('RGB'); h = int(width * im.height / im.width)
        im = im.resize((width, h), Image.LANCZOS); _shots[key] = (im, fx.pil_surface(im.convert('RGBA')))
    return _shots[key]

def card(ctx, name, width, cx, cy, ang, e, crop_h=None, scroll=0.0, blur=0.0):
    im, (surf, _b) = shot(name, width); w, h = im.width, (crop_h or im.height)
    if e <= 0: return
    ctx.save(); ctx.translate(cx, cy + 40 * (1 - e)); ctx.rotate(math.radians(ang)); sc = 0.92 + 0.08 * e; ctx.scale(sc, sc)
    rr(ctx, -w / 2 + 8, -h / 2 + 16, w, h, 16); ctx.set_source_rgba(0, 0, 0, 0.45 * e); ctx.fill()
    rr(ctx, -w / 2, -h / 2, w, h, 16); ctx.save(); ctx.clip()
    ctx.set_source_surface(surf, -w / 2, -h / 2 - scroll * max(0, im.height - h)); ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(e * (1 - 0.6 * blur)); ctx.restore()
    ctx.restore()

def badge(ctx, x, y, txt, e):
    if e <= 0: return
    tt = T_(txt, HN, 34, WHITE, 0, idx=BOLD); w = max(64, tt[4] + 34); h = 58; s_ = 0.6 + 0.4 * eo(e)
    ctx.save(); ctx.translate(x, y); ctx.scale(s_, s_)
    rr(ctx, -w / 2, -h / 2, w, h, h / 2); ctx.set_source_rgba(0.86, 0.15, 0.15, e); ctx.fill(); put(ctx, tt, 0, 2, alpha=e)
    ctx.restore()

INK = (0.07, 0.07, 0.07, 1); MUTE = (0.45, 0.45, 0.45, 1); GREEN = (0.13, 0.65, 0.42, 1); PAPER = (0.992, 0.992, 0.984)
def paper(ctx):
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(*PAPER); ctx.fill()

def chip(ctx, x, y, txt, e, col=INK, sub=None, hl=0.0):
    if e <= 0: return
    tt = T_(txt, HN, 38, col, -0.01, idx=BOLD); w_ = tt[4] + 70; h_ = 76 if sub is None else 96
    s_ = 0.85 + 0.15 * eo(e)
    ctx.save(); ctx.translate(x, y); ctx.scale(s_, s_)
    rr(ctx, -w_ / 2 + 3, -h_ / 2 + 6, w_, h_, 18); ctx.set_source_rgba(0, 0, 0, 0.08 * e); ctx.fill()
    rr(ctx, -w_ / 2, -h_ / 2, w_, h_, 18); ctx.set_source_rgba(1, 1, 1, e); ctx.fill_preserve()
    if hl > 0: ctx.set_source_rgba(GREEN[0], GREEN[1], GREEN[2], e * hl); ctx.set_line_width(5)
    else: ctx.set_source_rgba(0, 0, 0, 0.10 * e); ctx.set_line_width(2)
    ctx.stroke()
    put(ctx, tt, 0, -12 if sub else 2, alpha=e)
    if sub: put(ctx, T_(sub, MENLO_, 22, MUTE, 0, idx=0), 0, 26, alpha=e)
    ctx.restore()
MENLO_ = '/System/Library/Fonts/Menlo.ttc'

def hub(ctx, x, y, e, pulse=0.0):
    r = 74 * (0.85 + 0.15 * eo(e)) * (1 + 0.06 * pulse)
    ctx.arc(x, y, r, 0, 2 * math.pi); rgba(ctx, INK, e); ctx.fill()
    for k, (dx, dy) in enumerate([(-14, -14), (14, -14), (-14, 14)]):                # treg-like mark
        ctx.rectangle(x + dx - 11, y + dy - 11, 22, 22); ctx.set_source_rgba(1, 1, 1, e); ctx.fill()
    put(ctx, T_('treg', MENLO_, 30, INK, 0, idx=1), x, y + r + 36, alpha=e)

def wire(ctx, x0, y0, x1, y1, e, dot=None, col=(0, 0, 0, 0.18)):
    ctx.move_to(x0, y0); ctx.line_to(x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)
    ctx.set_source_rgba(*col); ctx.set_line_width(3); ctx.stroke()
    if dot is not None and 0 < dot < 1:
        ctx.arc(x0 + (x1 - x0) * dot, y0 + (y1 - y0) * dot, 9, 0, 2 * math.pi); rgba(ctx, YELF if col[3] < 0.5 else GREEN); ctx.fill()

APPS = [('Apollo', 72, 220, 380), ('Lusha', 73, 540, 330), ('Instantly', 74, 860, 380)]
def apps_panel(ctx, vt, a):
    """'tiene un montón de apps conectadas' -> hub; 'Apollo, Lusha, Instantly' -> chips + wires; 'un montón' -> +3,400 tools;
    'va y busca las cosas en cada una' -> pulses travel out; 'y la que tenga te lo arroja' -> Apollo lights up, result comes back"""
    paper(ctx); hx, hy = W / 2, SEAM + 690
    hub(ctx, hx, hy, expo_out(prog(vt, a, 0.4)))
    t_go, t_back = T(84) - 0.05, T(96) - 0.05
    for name, wi, x, y in APPS:
        e = expo_out(prog(vt, T(wi) - 0.05, 0.35)); yy = SEAM + y
        win = name == 'Apollo' and vt >= t_back
        wire(ctx, hx, hy - 60, x, yy + 40, e)
        go = prog(vt, t_go + 0.15 * APPS.index((name, wi, x, y)), 0.7)
        if 0 < go < 1: wire(ctx, hx, hy - 60, x, yy + 40, 1, dot=go)
        if win:
            back = prog(vt, t_back, 0.6); wire(ctx, x, yy + 40, hx, hy - 60, 1, dot=back, col=(GREEN[0], GREEN[1], GREEN[2], 0.9))
        chip(ctx, x, yy, name, e, hl=eo(prog(vt, t_back, 0.25)) if name == 'Apollo' else 0)
    e = expo_out(prog(vt, T(76) - 0.05, 0.35))
    if e > 0:
        tt = T_('+ 3,400 herramientas', MENLO_, 30, MUTE, 0, idx=0); put(ctx, tt, hx, SEAM + 250, alpha=e)
    k = expo_out(prog(vt, t_back + 0.45, 0.4))                # result card under the hub
    if k > 0:
        w_, h_ = 640, 110; x0, y0 = hx - w_ / 2, SEAM + 820 + 20 * (1 - k)
        rr(ctx, x0, y0, w_, h_, 20); ctx.set_source_rgba(1, 1, 1, k); ctx.fill_preserve(); ctx.set_source_rgba(GREEN[0], GREEN[1], GREEN[2], k); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(x0 + 56, y0 + 46, 18, 0, 2 * math.pi); rgba(ctx, GREEN, k); ctx.fill()
        ctx.move_to(x0 + 47, y0 + 47); ctx.line_to(x0 + 53, y0 + 54); ctx.line_to(x0 + 65, y0 + 39); ctx.set_source_rgba(1, 1, 1, k); ctx.set_line_width(4); ctx.stroke()
        put(ctx, T_('12 cuentas clave encontradas', HN, 36, INK, -0.01, idx=BOLD), x0 + 90, y0 + 46, alpha=k, ax=0)
        put(ctx, T_('vía Apollo · lista para contactar', MENLO_, 22, MUTE, 0, idx=0), x0 + 90, y0 + 84, alpha=k, ax=0)

SOCIAL = [('Instagram', 121, 330, 340), ('TikTok', 123, 750, 340), ('X / Twitter', 125, 330, 540), ('+ lo que sea', 126, 750, 540)]
def social_panel(ctx, vt, a):
    """'quieres hacer un contenido increíble… scraping de Instagram, TikTok, Twitter, de lo que sea' -> source chips land one by one,
    each with a fake 'posts' counter ticking up"""
    paper(ctx)
    put(ctx, T_('SCRAPING PARA TU CONTENIDO', HN, 26, MUTE, 0.16, idx=BOLD), W / 2, SEAM + 200, alpha=expo_out(prog(vt, a, 0.4)))
    for name, wi, x, y in SOCIAL:
        e = expo_out(prog(vt, T(wi) - 0.05, 0.35))
        n = int(40 + 460 * eo(prog(vt, T(wi), 1.6)))
        chip(ctx, x, SEAM + y, name, e, sub=None if name.startswith('+') else '%d posts' % n)
    k = expo_out(prog(vt, T(126) + 0.3, 0.4))
    if k > 0:
        put(ctx, T_('→ contexto para tus agentes y skills', HN, 34, INK, -0.01, idx=BOLD), W / 2, SEAM + 760, alpha=k)

def setup_panel(ctx, vt, a):
    """'lo tienen que conectar a su Claude Code' -> the line from treg's site to paste into the agent; 'le mandan la conexión' ->
    copy button pressed, 'Copiado' tick; 'y listo' -> green check"""
    paper(ctx); e = expo_out(prog(vt, a, 0.4))
    put(ctx, T_('PÉGALE ESTO A TU AGENTE', HN, 26, MUTE, 0.16, idx=BOLD), W / 2, SEAM + 260, alpha=e)
    w_, h_ = 940, 150; x0, y0 = (W - w_) / 2, SEAM + 330 + 20 * (1 - e)
    rr(ctx, x0, y0, w_, h_, 26); rgba(ctx, INK, e); ctx.fill()
    cmd = '$ set up treg - https://treg.to/llms.txt'
    n = int(len(cmd) * c01((vt - a - 0.2) / 1.1))
    put(ctx, T_(cmd[:n] or ' ', MENLO_, 25, (0.9, 0.9, 0.9, 1), 0, idx=0), x0 + 36, y0 + h_ / 2 + 2, alpha=e, ax=0)
    t_copy = T(214) - 0.05; k = prog(vt, t_copy, 0.25)
    bw = 150; bx = x0 + w_ - bw - 22; by = y0 + (h_ - 64) / 2; press = 1 - 0.06 * math.sin(math.pi * c01(k))
    ctx.save(); ctx.translate(bx + bw / 2, by + 32); ctx.scale(press, press)
    rr(ctx, -bw / 2, -32, bw, 64, 14); ctx.set_source_rgba(1, 1, 1, e); ctx.fill()
    put(ctx, T_('copiado' if vt >= t_copy + 0.12 else 'copy', HN, 28, INK, 0, idx=BOLD), 0, 2, alpha=e)
    ctx.restore()
    for j, (lbl, wi) in enumerate([('Claude Code', 212), ('treg conectado', 224), ('listo', 225)]):
        kk = expo_out(prog(vt, T(wi) - 0.05, 0.35))
        if kk <= 0: continue
        y = SEAM + 590 + j * 80; x = W / 2 - 230
        ctx.arc(x, y, 22, 0, 2 * math.pi); rgba(ctx, GREEN, kk); ctx.fill()
        ctx.move_to(x - 10, y + 1); ctx.line_to(x - 3, y + 9); ctx.line_to(x + 11, y - 8); ctx.set_source_rgba(1, 1, 1, kk); ctx.set_line_width(4); ctx.stroke()
        put(ctx, T_(lbl, HN, 38, INK, -0.01, idx=BOLD), x + 44, y + 2, alpha=kk, ax=0)

def cta(ctx, vt):
    """'Por acá les dejo todo' -> big link button over the chest, stays to the end"""
    k = expo_out(prog(vt, T(234) - 0.05, 0.45))
    if k <= 0: return
    tt = T_('treg.to', HN, 70, INK, -0.02, idx=BOLD); sub = T_('LINK EN LA DESCRIPCIÓN', HN, 22, MUTE, 0.16, idx=BOLD)
    w_, h_ = max(tt[4], sub[4]) + 170, 150; x0, y0 = (W - w_) / 2, 1400 + 30 * (1 - k)
    rr(ctx, x0 + 4, y0 + 10, w_, h_, 34); ctx.set_source_rgba(0, 0, 0, 0.3 * k); ctx.fill()
    rr(ctx, x0, y0, w_, h_, 34); ctx.set_source_rgba(1, 1, 1, k); ctx.fill()
    ctx.save(); ctx.translate(x0 + 70, y0 + 62)
    for dx, dy in [(-12, -12), (12, -12), (-12, 12)]: ctx.rectangle(dx - 10, dy - 10, 20, 20); rgba(ctx, INK, k); ctx.fill()
    ctx.restore()
    put(ctx, tt, x0 + 120, y0 + 64, alpha=k, ax=0); put(ctx, sub, x0 + 120, y0 + 118, alpha=k, ax=0)

def pill(ctx, vt):
    for a, b, txt in PILLS:
        if a <= vt < b: break
    else: return
    e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - (b - 0.15)) / 0.15))
    tt = T_(txt, HN, 46, WHITE, -0.01, idx=BOLD)
    w = tt[4] + 120; h = 86
    ctx.save(); ctx.translate(W / 2, SEAM + 22 * (1 - e))
    ctx.new_sub_path(); r = h / 2
    ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(0.05, 0.05, 0.05, 0.92 * e); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 0.25 * e); ctx.set_line_width(2); ctx.stroke()
    for dx, dy in [(-7, -7), (7, -7), (-7, 7)]:
        ctx.rectangle(-w / 2 + 48 + dx - 6, dy - 6, 12, 12); ctx.set_source_rgba(1, 1, 1, e); ctx.fill()
    put(ctx, tt, -w / 2 + 84, 2, alpha=e, ax=0)
    ctx.restore()

# ---------------- subtitles ----------------
def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) + 1 for x in cur)
        if (len(cur) >= 4 or chars >= 19 or w[2][-1] in '.,?:!' or nxt is None or nxt[0] - w[1] > 0.35
                or (nxt and len(nxt[2]) > 10 and chars > 9)):
            ch.append(cur); cur = []
    out = []
    for j, c in enumerate(ch):
        st = c[0][0] - 0.03
        en = ch[j + 1][0][0] - 0.03 if j + 1 < len(ch) else c[-1][1] + 0.4
        out.append((st, min(en, c[-1][1] + 0.5), c))
    return out
CHUNKS = build_chunks()

def subtitles(ctx, t, y, plate=False):
    vt = vt_of(t)
    if in_card(t): return
    for st, en, ws in CHUNKS:
        if st <= vt < en: break
    else: return
    size = 66; gap = size * 0.27
    parts = []
    for (a, b, w) in ws:
        active = a - 0.03 <= vt < b + 0.02 or (w == ws[-1][2] and vt >= a)
        parts.append(T_(w, HN, size, YELF if active else WHITE, -0.02, shadow=7, idx=BOLD, shadow_a=230, shadow_off=4))
    total = sum(p[4] for p in parts) + gap * (len(parts) - 1)
    sc = min(1.0, 980 / total); e = expo_out(prog(vt, st, 0.25))
    x = W / 2 - total * sc / 2
    if plate:
        pw, ph = total * sc + 56, size * 1.5 * sc; r = 18; px, py = W / 2 - pw / 2, y + 12 * (1 - e) - ph / 2 - 2
        ctx.new_sub_path(); ctx.arc(px + pw - r, py + r, r, -math.pi / 2, 0); ctx.arc(px + pw - r, py + ph - r, r, 0, math.pi / 2)
        ctx.arc(px + r, py + ph - r, r, math.pi / 2, math.pi); ctx.arc(px + r, py + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
        ctx.set_source_rgba(0, 0, 0, 0.8 * e); ctx.fill()
    for tt in parts:
        put(ctx, tt, x, y + 12 * (1 - e), scale=sc, alpha=e, ax=0); x += tt[4] * sc + gap * sc

# ---------------- good-work_ title card ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = ['3 PÁGINAS PARA QUE', 'TU WEBSITE NO PAREZCA', 'HECHO CON IA']
def stroked(txt, size, fill, stroke, idx, track=0.0, shadow=True):
    f = ImageFont.truetype(HN, size, index=idx)
    sp = track * size; widths = [f.getlength(ch) + sp for ch in txt]; tw = sum(widths) - sp
    asc, desc = f.getmetrics(); pad = stroke + 24
    w, h = int(tw + 2 * pad), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    def draw(d, col, sw, off=(0, 0)):
        if track == 0:
            d.text((pad + off[0], pad + off[1]), txt, font=f, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0, 255)); return
        x = pad + off[0]
        for ch, cw in zip(txt, widths):
            d.text((x, pad + off[1]), ch, font=f, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0, 255)); x += cw
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, 255), stroke, (5, 6))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    draw(ImageDraw.Draw(img), fill + (255,), stroke)
    return img, pad, tw

def posterize(rgb8):
    im = Image.fromarray(rgb8).resize((540, 960), Image.BILINEAR)
    im = ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.45)).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5))
    a = np.asarray(im).astype(np.float32) / 255; L = 5
    q = Image.fromarray((np.round(a * (L - 1)) / (L - 1) * 255).astype(np.uint8)).filter(ImageFilter.ModeFilter(3))
    return np.asarray(q.resize((W, H), Image.BILINEAR))

TITLE = ['DALE SUPERPODERES', 'A TU CLAUDE CON', 'ESTA PÁGINA']
_tit = [stroked(l, 120, YEL, 7, BOLD, -0.01) for l in TITLE]
def title_layer(t):
    if t >= TITLE_END: return None
    k = t - 0.1
    if k < 0: return None
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fade = 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    n = min(len(LABEL), int(k / 0.022) + 1)
    txt = LABEL[:n] + '_' if n < len(LABEL) else (LABEL if int(k * 2.2) % 2 == 0 else LABEL[:-1])
    x0, y_lab = 60, 1180
    sub = stroked(txt, 46, YEL, 4, REG); img.alpha_composite(sub[0], (x0 - sub[1], y_lab - sub[1]))
    if k > 0.022 * len(LABEL) + 0.12:
        y = y_lab + 64; s_ = min(1.0, min(960 / ttw for _, _, ttw in _tit))
        for timg, tpad, ttw in _tit:
            ti = timg.resize((int(timg.width * s_), int(timg.height * s_)), Image.LANCZOS) if s_ < 1 else timg
            img.alpha_composite(ti, (int(x0 - tpad * s_), int(y - tpad * s_))); y += int(128 * s_)
    if fade < 1:
        a = np.asarray(img).copy(); a[..., 3] = (a[..., 3] * fade).astype(np.uint8); img = Image.fromarray(a)
    return img

# ---------------- frame ----------------
def render_frame(fr16, t):
    vt = t
    sdr = np.zeros((H, W, 3), np.float32)
    sp = split_at(vt)
    arr, surf, ctx = fx.new_layer()
    if sp is None:
        sdr[:] = speaker(fr16, t, (W, H)); hdr = sdr.copy()
        cta(ctx, vt)
        if t >= TITLE_END: subtitles(ctx, t, 1290 if vt >= T(234) - 0.05 else 1370, plate=True)
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        if key.startswith('js_'):
            bottom = rec_frame(key, vt, a, b)
            sdr[SEAM:] = bottom.astype(np.float32) / 255; hdr[SEAM:] = fx.srgb8_to_hlg(bottom)
        elif key == 'apps': apps_panel(ctx, vt, a)
        elif key == 'social': social_panel(ctx, vt, a)
        elif key == 'setup': setup_panel(ctx, vt, a)
        pill(ctx, vt)
        if t >= TITLE_END: subtitles(ctx, t, 1065, plate=True)
    surf.flush()
    fx.layer_over(sdr, hdr, arr)
    ti = title_layer(t)
    if ti is not None:
        a8 = np.asarray(ti); al = a8[..., 3:4].astype(np.float32) / 255; ys, xs = np.nonzero(a8[..., 3])
        if len(ys):
            c8 = a8[ys, xs, :3]; aa = al[ys, xs]
            sdr[ys, xs] = c8.astype(np.float32) / 255 * aa + sdr[ys, xs] * (1 - aa)
            hdr[ys, xs] = fx.srgb8_to_hlg(c8) * aa + hdr[ys, xs] * (1 - aa)
    return sdr, hdr

def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    readers = {k: fx.hlg_reader(E.SRCS[k]) for k in E.SRCS}; cur = {k: (-1, None) for k in E.SRCS}
    for fi in want:
        t = fi / FPS; vt = vt_frame(t)
        te = min(vt * SPEED, E.TOTAL - 0.001)
        s, st = E.src_of(te)
        if vt * SPEED > E.TOTAL: st += vt * SPEED - E.TOTAL
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
    n = int(DUR * SR); m = np.zeros((n, 2), np.float32)
    m[:min(n, len(v))] = v[:n]
    with wave.open(os.path.join(HERE, 'mix.wav'), 'wb') as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(HERE, 'prev'), exist_ok=True)
        for fi, t, fr in frames(times):
            sdr, hdr = render_frame(fr, t)
            Image.fromarray(fx.to8(sdr)).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    eh, es = fx.encoders(sys.argv[2], sys.argv[3], os.path.join(HERE, 'mix.wav'))
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t)
        eh.stdin.write(np.ascontiguousarray(fx.to16(hdr)).tobytes()); es.stdin.write(np.ascontiguousarray(fx.to8(sdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    for e_ in (eh, es): e_.stdin.close()
    for e_ in (eh, es): e_.wait()
    print('done', sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
