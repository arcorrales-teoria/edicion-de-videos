import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.append(os.path.join(ROOT, 'v2'))
from render import *                    # base helpers (v1)
import render as R
os.chdir(os.path.join(ROOT, 'v2'))
from render2 import stamp, person, speaker, gear, pop_scale   # v2 helpers (+ safe cairo scale)
os.chdir(HERE)
from edit3 import SEGS, SRCF, src_of, seg_index, TOTAL

TWSRC = '/Users/acorrales/Downloads/Twitter Video Download.mp4'
OUTRO = 1.0
DUR = TOTAL + OUTRO
FCX, FCY = 0.50, 0.37

# ---------------- words ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {12: 'vi', 14: 'este', 31: 'MUD\\WTR.', 159: 'Claude', 170: 'promptear', 173: 'Claude',
       175: 'promptearle', 72: '¿Esto', 75: 'Vea', 233: 'email'}
DROP = {32, 171, 234}
WORDS = []
for i, w in enumerate(_ws):
    if i in DROP:
        WORDS[-1] = (WORDS[-1][0], w['end'], WORDS[-1][2]); continue
    WORDS.append((w['start'], w['end'], FIX.get(i, w['word'].strip())))
def T(i): return _ws[i]['start']

def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) for x in cur)
        if (len(cur) >= 4 or chars >= 16 or w[2][-1] in '.,?' or nxt is None or nxt[0] - w[1] > 0.35
                or (nxt and len(nxt[2]) > 11 and chars > 10)):
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
    size = 76; sp = size * 0.40
    parts = []
    for (a, b, w) in ws:
        active = a - 0.03 <= t < b + 0.02 or (w == ws[-1][2] and t >= a)
        parts.append((text(w, F_SUB, size, YEL if active else CREAM, stroke=9, stroke_col=hexc('111111'), shadow=True), active))
    total = sum(p[0][4] for p in parts) + sp * (len(parts) - 1)
    sc = min(1.0, 960 / total)
    k = eback(prog(t, st, 0.16), 2.2); cs = sc * (0.84 + 0.16 * k); al = c01((t - st) / 0.06)
    x = W / 2 - total * cs / 2
    for tt, active in parts:
        ww = tt[4] * cs
        put(ctx, tt, x + ww / 2, y, scale=cs * (1.07 if active else 1.0), alpha=al)
        x += ww + sp * cs

# ---------------- icons ----------------
def cup(ctx, x, y, s, col=INK):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-40, -30); ctx.line_to(40, -30); ctx.line_to(32, 40); ctx.curve_to(30, 50, -30, 50, -32, 40); ctx.close_path()
    rgba(ctx, col); ctx.fill()
    ctx.arc(46, 2, 18, -1.3, 1.3); ctx.set_line_width(9); ctx.stroke()
    for dx in (-16, 4, 22):
        ctx.move_to(dx, -44); ctx.curve_to(dx - 10, -56, dx + 10, -64, dx, -78)
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); rgba(ctx, col, 0.6); ctx.stroke()
    ctx.restore()

def mushroom(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -16, -6, 32, 56, 12); rgba(ctx, CREAM); ctx.fill()
    rrect(ctx, -16, -6, 32, 56, 12); rgba(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(-62, 0); ctx.curve_to(-62, -70, 62, -70, 62, 0); ctx.close_path(); rgba(ctx, TERRA); ctx.fill()
    ctx.move_to(-62, 0); ctx.curve_to(-62, -70, 62, -70, 62, 0); ctx.close_path(); rgba(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    for dx, dy, r in ((-30, -22, 9), (4, -38, 10), (34, -18, 8)):
        ctx.arc(dx, dy, r, 0, 2 * math.pi); rgba(ctx, CREAM); ctx.fill()
    ctx.restore()

def envelope(ctx, x, y, s, col=INK):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -58, -40, 116, 80, 10); rgba(ctx, col); ctx.set_line_width(7); ctx.stroke()
    ctx.move_to(-54, -34); ctx.line_to(0, 8); ctx.line_to(54, -34); ctx.stroke()
    ctx.restore()

def gamepad(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -62, -34, 124, 68, 34); rgba(ctx, hexc('6A9BD1')); ctx.fill()
    ctx.rectangle(-42, -6, 28, 12); ctx.rectangle(-34, -14, 12, 28); rgba(ctx, CREAM); ctx.fill()
    for dx, dy in ((26, -8), (40, 6)):
        ctx.arc(dx, dy, 7, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

def gift(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.rectangle(-44, -20, 88, 64); rgba(ctx, hexc('E8B84A')); ctx.fill()
    ctx.rectangle(-50, -36, 100, 20); rgba(ctx, hexc('D97757')); ctx.fill()
    ctx.rectangle(-8, -36, 16, 80); rgba(ctx, RED); ctx.fill()
    ctx.restore()

def coupon(ctx, x, y, s, label='%'):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -66, -38, 132, 76, 10); rgba(ctx, hexc('7FB685')); ctx.fill()
    for sy in (-38, 38):
        ctx.arc(0, sy, 12, 0, 2 * math.pi); rgba(ctx, PAPER); ctx.fill()
    put(ctx, text(label, F_LABEL, 60, CREAM), 0, 4)
    ctx.restore()

def xmark(ctx, x, y, s, p, fi):
    partial(ctx, jit([(x - 40 * s, y - 40 * s), (x + 40 * s, y + 40 * s)], 1.5, fi // 4), p * 2, 12, RED)
    partial(ctx, jit([(x + 40 * s, y - 40 * s), (x - 40 * s, y + 40 * s)], 1.5, fi // 4 + 1), p * 2 - 1, 12, RED)

def chip(ctx, x, y, label, k, fill=CREAM, tcol=INK, size=46, rot=0.0, icon=None):
    if k <= 0: return
    lab = text(label, F_BOLD, size, tcol); pad = 110 if icon else 64
    w = lab[4] + pad; h = size * 1.9
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k, k)
    shadow(ctx, -w / 2, -h / 2, w, h, h / 2); rrect(ctx, -w / 2, -h / 2, w, h, h / 2); rgba(ctx, fill); ctx.fill()
    if icon == 'spark': spark(ctx, -w / 2 + 50, 0, 20, tcol, 6)
    put(ctx, lab, -w / 2 + (pad - 32 if icon else pad / 2), 2, ax=0)
    ctx.restore()

def behind_word(ctx, t, t0, txt, y, size, col=INK, spacing=4, maxw=1020):
    """big word drawn BEHIND the speaker (called before person composite)"""
    if t < t0: return
    tt = text(txt, F_LABEL, size, col, spacing=spacing)
    s = min(1.0, maxw / tt[4])
    k = eo(prog(t, t0, 0.28))
    put(ctx, tt, 540, y + 60 * (1 - k), scale=s, alpha=k)

# ---------------- twitter frames ----------------
TW_USE = [(16.5, 0.6), (1.3, 3.0), (7.2, 2.4), (15.0, 3.1), (20.0, 1.6), (31.6, 1.4), (51.95, 1.7),
          (34.8, 2.7), (27.0, 4.0), (44.0, 2.3), (39.2, 2.8), (15.0, 2.2), (58.8, 2.6)]
TWF = {}
TWW, TWH = 1080, 2171
def load_tw():
    need = set()
    for a, d in TW_USE:
        for k in range(int(a * FPS) - 1, int((a + d) * FPS) + 3): need.add(k)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', TWSRC, '-vf', f'fps=30,scale={TWW}:{TWH}', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    k = 0
    while True:
        b = p.stdout.read(TWW * TWH * 3)
        if len(b) < TWW * TWH * 3: break
        if k in need: TWF[k] = np.frombuffer(b, np.uint8).reshape(TWH, TWW, 3)
        k += 1
def tw_frame(tt):
    k = int(round(tt * FPS))
    while k not in TWF and k > 0: k -= 1
    return TWF[k]

# ---------------- masks ----------------
MDIR = {'h': os.path.join(HERE, 'seg/mh'), 'm': os.path.join(HERE, 'seg/mm')}
_mprev = {'key': None, 'm': None}
def mask_for(src, st, box, size, fi):
    k = int(round(st * FPS)) + 1
    path = os.path.join(MDIR[src], '%05d.png' % k)
    while not os.path.exists(path) and k > 1:
        k -= 1; path = os.path.join(MDIR[src], '%05d.png' % k)
    m = Image.open(path).convert('L')
    mw, mh = m.size
    x0, y0, x1, y1 = box
    m = m.resize(size, Image.BILINEAR, box=(x0 * mw / SW, y0 * mh / SH, x1 * mw / SW, y1 * mh / SH))
    m = m.filter(ImageFilter.GaussianBlur(1.6))
    a = np.asarray(m, np.float32) / 255
    a = np.clip((a - 0.12) / 0.76, 0, 1)
    if _mprev['key'] == (src, fi - 1, size) and _mprev['m'] is not None:
        a = 0.65 * a + 0.35 * _mprev['m']
    _mprev['key'] = (src, fi, size); _mprev['m'] = a
    return a

def crop_box(z, cx=FCX, cy=FCY, size=(W, H)):
    ow, oh = size
    cw = SW / z; ch = cw * oh / ow
    x0 = min(max(cx * SW - cw / 2, 0), SW - cw); y0 = min(max(cy * SH - ch / 2, 0), SH - ch)
    return (x0, y0, x0 + cw, y0 + ch)

# ---------------- scenes ----------------
def hook_behind(ctx, t, fi):
    behind_word(ctx, t, T(6) - 0.04, 'MEJORES CAMPAÑAS', 165, 140, INK, 3)
    behind_word(ctx, t, T(8) - 0.04, 'DE MARKETING', 310, 150, TERRA, 4)
def hook_front(ctx, t, fi):
    t0 = T(15) - 0.05
    if t < t0: return
    p = prog(t, t0, 0.2); s = 1.8 - 0.8 * eo(p)
    tt = text('2026', F_LABEL, 210, INK, spacing=6); w = tt[4] + 80
    ctx.save(); ctx.translate(540, 1245); ctx.rotate(-0.06); ctx.scale(s * 0.85, s * 0.85)
    shadow(ctx, -w / 2, -115, w, 230, 22); rrect(ctx, -w / 2, -115, w, 230, 22); rgba(ctx, YEL); ctx.fill()
    rrect(ctx, -w / 2 + 12, -103, w - 24, 206, 14); rgba(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    put(ctx, tt, 0, 12); ctx.restore()

def m1_front(ctx, t, fi):
    tc = T(19) - 0.05
    if t >= tc:
        k = pop_scale(t, tc, 0.28, 2)
        ctx.save(); ctx.translate(220, 230); ctx.rotate(-0.05); ctx.scale(k, k)
        card(ctx, -120, -120, 240, 240, 30); cup(ctx, 0, 20, 1.2); ctx.restore()

def m3_behind(ctx, t, fi):
    behind_word(ctx, t, T(31) + 0.2, 'MUD\\WTR', 250, 300, INK, 8)
def m3_front(ctx, t, fi):
    t1, t2, t3 = T(37) - 0.05, T(39) - 0.05, T(44) - 0.05
    if t < t1: return
    k = pop_scale(t, t1, 0.3, 1.5)
    ctx.save(); ctx.translate(540, 1170); ctx.scale(k, k); ctx.rotate(-0.015)
    card(ctx, -430, -115, 860, 230, 28)
    cup(ctx, -360, 18, 1.0)
    put(ctx, text('café', F_SERIF, 60, INK), -290, 10, ax=0)
    if t >= t2:
        k2 = pop_scale(t, t2, 0.25, 2.2)
        ctx.save(); ctx.translate(-120, 10); ctx.scale(k2, k2)
        lab = text('EE.UU.', F_LABEL, 50, CREAM, spacing=3); w = lab[4] + 40
        rrect(ctx, -w / 2 + 40, -34, w, 68, 12); rgba(ctx, hexc('3B5BA9')); ctx.fill()
        put(ctx, lab, 40, 4); ctx.restore()
    if t >= t3:
        k3 = pop_scale(t, t3, 0.3, 2.2)
        put(ctx, text('+', F_SERIF, 80, TERRA), 55, 6, alpha=c01(k3))
        ctx.save(); ctx.translate(150, 40); ctx.scale(k3, k3); mushroom(ctx, 0, 0, 0.9); ctx.restore()
        put(ctx, text('hongos', F_SERIF, 56, INK), 212, 10, ax=0, alpha=c01((t - t3) / 0.15))
    ctx.restore()

LEVELS = [(T(58) - 0.02, '1', '5%'), (T(63) - 0.02, '2', '7%'), (T(68) - 0.02, '3', '9%')]
def levels_overlay(ctx, t, fi):
    for i, (tl, lv, pc) in enumerate(LEVELS):
        if t < tl: continue
        k = pop_scale(t, tl, 0.25, 2.2)
        ctx.save(); ctx.translate(230, 300 + i * 130); ctx.scale(k, k); ctx.rotate(-0.02)
        lab = text(f'Nivel {lv}', F_BOLD, 44, INK); pct = text(pc, F_LABEL, 70, CREAM)
        w = 360
        shadow(ctx, -w / 2, -52, w, 104, 26); rrect(ctx, -w / 2, -52, w, 104, 26); rgba(ctx, CREAM); ctx.fill()
        put(ctx, lab, -w / 2 + 28, 2, ax=0)
        rrect(ctx, w / 2 - 130, -40, 112, 80, 18); rgba(ctx, hexc('3E9B5F') if i == 2 else TERRA); ctx.fill()
        put(ctx, pct, w / 2 - 74, 6)
        ctx.restore()
    # rising arrow
    if t >= LEVELS[1][0]:
        hand_arrow(ctx, (445, 690), (445, 330), -40, eio(prog(t, LEVELS[1][0], 1.2)), 9, YEL, 17 + fi // 4, head=34)

def tw_chip_campaign(ctx, t, fi, t0):
    k = pop_scale(t, t0 + 0.1, 0.3, 2) * (1 - c01((t - t0 - 2.6) / 0.2))
    chip(ctx, 540, 150, 'Campaña de MUD\\WTR', k, INK, CREAM, 46, -0.02)

def interact_chips(ctx, t, fi):
    chip(ctx, 300, 330, 'Interactivo', pop_scale(t, T(111) - 0.05, 0.28, 2.2), YEL, INK, 54, -0.05)
    chip(ctx, 700, 460, 'Divertido', pop_scale(t, T(114) - 0.05, 0.28, 2.2), TERRA, CREAM, 54, 0.05)
def won_stamp(ctx, t, fi):
    stamp(ctx, '¿Y SI SE LO GANAN?', 540, 360, t, T(102) - 0.1, TERRA, -0.06, 96)

def m7_front(ctx, t, fi):  # "le puedes dar un descuento"
    chip(ctx, 540, 250, 'Descuento = correo', pop_scale(t, T(95) - 0.05, 0.28, 2), CREAM, INK, 50, -0.03)

def m10_front(ctx, t, fi):
    stamp(ctx, 'LO HACEN CON TODO', 540, 300, t, T(131) - 0.05, RED, 0.06, 100)

def f_front(ctx, t, fi):
    chip(ctx, 540, 250, 'Leaderboard + códigos', pop_scale(t, T(136) - 0.05, 0.28, 2), YEL, INK, 50, 0.03)

def m12_front(ctx, t, fi):
    tt = T(151) - 0.05
    if t >= tt:
        put(ctx, text('lo más sencillo', F_HAND, 76, CREAM, shadow=True), 540, 250, alpha=c01((t - tt) / 0.15), rot=-0.04)
        partial(ctx, jit([(330, 320), (760, 312)], 1.2, fi // 4), eio(prog(t, tt + 0.1, 0.3)), 8, YEL)

GAME_PROMPT = 'Crea un juego tipo Angry Birds para mi marca de café, con niveles y descuentos'
GLINES = R.wrap(GAME_PROMPT, F_MONO, 38, 780)
def s_code(ctx, t, fi):  # split top panel: Claude Code + phone preview
    paper(ctx, fi)
    t0 = T(154) - 0.08
    k = pop_scale(t, t0, 0.3, 1.3)
    ctx.save(); ctx.translate(500, 450); ctx.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    shadow(ctx, -440, -330, 880, 660, 26, 0.3, 14)
    rrect(ctx, -440, -330, 880, 660, 26); rgba(ctx, hexc('1F1E1D')); ctx.fill()
    ctx.save(); rrect(ctx, -440, -330, 880, 80, 26); ctx.clip()
    ctx.rectangle(-440, -330, 880, 80); rgba(ctx, hexc('2E2D2B')); ctx.fill(); ctx.restore()
    for i, c in enumerate(['FF5F57', 'FEBC2E', '28C840']):
        ctx.arc(-392 + i * 42, -290, 12, 0, 2 * math.pi); rgba(ctx, hexc(c)); ctx.fill()
    tcode = T(159) - 0.05
    title = text('Claude Code', F_MONO, 38, CREAM if t < tcode else INK)
    if t >= tcode: highlighter(ctx, -title[4] / 2 - 16, -314, title[4] + 32, 50, prog(t, tcode, 0.25), seed=33)
    put(ctx, title, 0, -290); spark(ctx, -title[4] / 2 - 40, -290, 17, TERRA, 6, rot=t)
    n = int(len(GAME_PROMPT) * prog(t, T(166), T(179) - T(166))); rem = n; y = -220
    put(ctx, text('>', F_MONO, 38, TERRA), -400, y, ax=0, ay=0)
    cur = None
    for ln in GLINES:
        seg = ln[:max(0, rem)]
        if seg: put(ctx, text(seg, F_MONO, 38, CREAM), -362, y, ax=0, ay=0)
        if cur is None and rem <= len(ln): cur = (seg, y)
        rem -= len(ln) + 1; y += 54
    if cur is None: cur = (GLINES[-1], y - 54)
    if n < len(GAME_PROMPT) or (fi // 8) % 2 == 0:
        cx = -362 + ImageFont.truetype(F_MONO, 38).getlength(cur[0]) + 6
        ctx.rectangle(cx, cur[1] + 8, 18, 44); rgba(ctx, CREAM, 0.8); ctx.fill()
    tg = T(179) - 0.05
    for i, ln in enumerate(['+ index.html', '+ juego.js  (física y niveles)', '+ descuentos.js']):
        ti = tg + i * 0.14
        if t >= ti:
            put(ctx, text(ln, F_MONO, 34, hexc('28C840')), -400, 20 + i * 52, ax=0, ay=0, alpha=c01((t - ti) / 0.08))
    ctx.restore()
    # phone preview
    tp = T(180) - 0.05
    if t >= tp:
        k = eback(prog(t, tp, 0.35), 1.6)
        ctx.save(); ctx.translate(870, 780 + 400 * (1 - k)); ctx.rotate(0.06)
        pw, ph = 230, 462
        shadow(ctx, -pw / 2 - 12, -ph / 2 - 12, pw + 24, ph + 24, 40, 0.35, 12)
        rrect(ctx, -pw / 2 - 12, -ph / 2 - 12, pw + 24, ph + 24, 40); rgba(ctx, INK); ctx.fill()
        tt = 15.0 + min(t - tp, 2.1)
        im = Image.fromarray(tw_frame(tt)).resize((pw, ph), Image.BILINEAR).convert('RGBA')
        surf, buf = pil_surface(im)
        ctx.save(); rrect(ctx, -pw / 2, -ph / 2, pw, ph, 30); ctx.clip()
        ctx.set_source_surface(surf, -pw / 2, -ph / 2); ctx.paint(); ctx.restore()
        ctx.restore()

def m14_behind(ctx, t, fi):
    behind_word(ctx, t, T(191) - 0.04, 'NUEVO', 160, 180, INK, 8)
    behind_word(ctx, t, T(192) - 0.04, 'ESTÁNDAR', 340, 210, TERRA, 8)

def s_more(ctx, t, fi):  # paper: más y más cosas → interactuar con la marca
    paper(ctx, fi)
    t0 = T(200) - 0.05
    ttl = text('MÁS Y MÁS', F_LABEL, 150, INK, spacing=4)
    highlighter(ctx, 540 - ttl[4] / 2 - 20, 250, ttl[4] + 40, 110, prog(t, T(206) - 0.05, 0.3), seed=12)
    put(ctx, ttl, 540, 310, alpha=eo(prog(t, t0, 0.25)))
    bx, px, ny = 250, 830, 820
    k1 = pop_scale(t, t0 + 0.05, 0.3, 1.8); k2 = pop_scale(t, t0 + 0.2, 0.3, 1.8)
    ctx.save(); ctx.translate(bx, ny); ctx.scale(k1, k1)
    ctx.arc(0, 0, 130, 0, 2 * math.pi); rgba(ctx, TERRA); ctx.fill()
    ctx.arc(0, 0, 130, 0, 2 * math.pi); rgba(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    cup(ctx, 0, 14, 1.3, CREAM); ctx.restore()
    ctx.save(); ctx.translate(px, ny); ctx.scale(k2, k2)
    ctx.arc(0, 0, 130, 0, 2 * math.pi); rgba(ctx, CREAM); ctx.fill()
    ctx.arc(0, 0, 130, 0, 2 * math.pi); rgba(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    person(ctx, 0, 10, 1.3); ctx.restore()
    tm = T(219) - 0.05
    lb = text('MARCA', F_LABEL, 64, INK, spacing=4)
    if t >= tm: highlighter(ctx, bx - lb[4] / 2 - 12, ny + 158, lb[4] + 24, 60, prog(t, tm, 0.25), seed=2)
    put(ctx, lb, bx, ny + 192, alpha=k1 and 1)
    put(ctx, text('GENTE', F_LABEL, 64, INK, spacing=4), px, ny + 192, alpha=k2 and 1)
    # items flying brand -> person
    items = [(T(206), gamepad), (T(208), gift), (T(209), lambda c, x, y, s: coupon(c, x, y, s, '%')), (T(209) + 0.35, lambda c, x, y, s: spark(c, x, y, 34 * s, hexc('E8B84A'), 12))]
    for i, (ti, fn) in enumerate(items):
        if t < ti: continue
        u = eio(prog(t, ti, 0.7))
        ex, ey = [(px - 190, ny - 190), (px - 60, ny - 250), (px + 80, ny - 240), (px + 180, ny - 160)][i]
        x = bx + (ex - bx) * u; y = (ny - 60) + (ey - (ny - 60)) * u - math.sin(math.pi * u) * 220
        fn(ctx, x, y, 1.25)
    ti = T(216) - 0.05
    if t >= ti:
        hand_arrow(ctx, (bx + 150, ny + 20), (px - 150, ny + 20), 30, eio(prog(t, ti, 0.35)), 8, INK, 5 + fi // 4, head=28)
        hand_arrow(ctx, (px - 150, ny + 70), (bx + 150, ny + 70), 30, eio(prog(t, ti + 0.2, 0.35)), 8, TERRA, 6 + fi // 4, head=28)
        put(ctx, text('interactuar', F_HAND, 66, TERRA), 540, 1060, alpha=c01((t - ti) / 0.2), rot=-0.03)

def m16_behind(ctx, t, fi):
    behind_word(ctx, t, T(224) - 0.04, 'CONEXIÓN', 250, 240, INK, 8)
def m16_front(ctx, t, fi):
    for i, (ti, kind, lab) in enumerate([(T(228) - 0.05, 'video', 'Video'), (T(232) - 0.05, 'mail', 'Email')]):
        if t < ti: continue
        k = pop_scale(t, ti, 0.28, 2)
        x = 330 + i * 420
        ctx.save(); ctx.translate(x, 1160); ctx.rotate((-1) ** i * 0.04); ctx.scale(k, k)
        card(ctx, -150, -100, 300, 200, 24)
        if kind == 'video': play_icon(ctx, 0, -18, 0.95)
        else: envelope(ctx, 0, -18, 0.95)
        put(ctx, text(lab, F_SERIF, 44, INK), 0, 62)
        ctx.restore()
        xmark(ctx, x + 110, 1070, 0.7, prog(t, ti + 0.25 + (0.2 if i == 0 else 0.1), 0.3), fi)

def m18_behind(ctx, t, fi):
    behind_word(ctx, t, T(241) - 0.05, 'MÁS', 260, 340, TERRA, 10)

def outro(ctx, t, fi):
    t0 = TOTAL - 0.4
    k = pop_scale(t, t0, 0.35, 1.6)
    if k <= 0: return
    ctx.save(); ctx.translate(540, 300); ctx.scale(k, k); ctx.rotate(-0.02)
    card(ctx, -420, -130, 840, 260, 28)
    lab = text('CAMPAÑA', F_LABEL, 50, INK, spacing=5)
    highlighter(ctx, -lab[4] / 2 - 14, -102, lab[4] + 28, 52, 1, seed=4)
    put(ctx, lab, 0, -72)
    put(ctx, text('MUD\\WTR · Angry Pumpkins', F_SERIF, 50, INK), 0, 40)
    ctx.restore()

# ---------------- shots ----------------
# kind: face | tw | split | paper ; behind/front callables ; zoom (None = jump-cut cycle); tw: (tw_t0)
TWS = []   # (out_t0, out_t1, tw_t0) for audio-free bookkeeping / previews
def S(t0, t1, kind, front=None, behind=None, zoom=None, tw=None, extra=None):
    return dict(t0=t0, t1=t1, kind=kind, front=front, behind=behind, zoom=zoom, tw=tw, extra=extra or {})
H1 = T(16) - 0.25
SHOTS = [
    S(0.0, H1, 'face', hook_front, hook_behind, 'hook'),
    S(H1, T(22) - 0.02, 'face', m1_front),
    S(T(22) - 0.02, T(24) - 0.02, 'tw', tw=16.5),
    S(T(24) - 0.02, T(24) + 2.98, 'tw', lambda c, t, f: tw_chip_campaign(c, t, f, T(24)), tw=1.3),
    S(T(24) + 2.98, T(45) - 0.02, 'face', m3_front, m3_behind, 1.0),
    S(T(45) - 0.02, T(50) - 0.02, 'tw', tw=7.2),
    S(T(50) - 0.02, T(58) - 0.04, 'tw', tw=15.0),
    S(T(58) - 0.04, T(63) - 0.04, 'tw', levels_overlay, tw=20.0),
    S(T(63) - 0.04, T(68) - 0.04, 'tw', levels_overlay, tw=31.6),
    S(T(68) - 0.04, T(72) - 0.04, 'tw', levels_overlay, tw=51.95),
    S(T(72) - 0.04, T(75) - 0.04, 'face', None, None, 1.34),
    S(T(75) - 0.04, T(88) - 0.04, 'face', None, lambda c, t, f: (behind_word(c, t, T(85) - 0.04, 'EL MARKETING', 160, 180, INK, 6),
                                                                 behind_word(c, t, T(87) - 0.04, 'ESTÁ CAMBIANDO', 330, 170, TERRA, 5)), 1.0),
    S(T(88) - 0.04, T(98) - 0.04, 'tw', m7_front, tw=34.8),
    S(T(98) - 0.04, T(112) - 0.04, 'tw', lambda c, t, f: (won_stamp(c, t, f), interact_chips(c, t, f)), tw=27.0),
    S(T(112) - 0.04, T(121) - 0.04, 'tw', interact_chips, tw=44.0),
    S(T(121) - 0.04, T(134) - 0.04, 'face', m10_front),
    S(T(134) - 0.04, T(146) - 0.04, 'tw', f_front, tw=39.2),
    S(T(146) - 0.04, T(154) - 0.08, 'face', m12_front),
    S(T(154) - 0.08, T(188) - 0.04, 'split', s_code),
    S(T(188) - 0.04, T(200) - 0.05, 'face', None, m14_behind, 1.0),
    S(T(200) - 0.05, T(220) - 0.04, 'paper', s_more, extra={'slide': True}),
    S(T(220) - 0.04, T(238) - 0.04, 'face', m16_front, m16_behind, 1.0),
    S(T(238) - 0.04, T(242) + 0.3, 'face', None, m18_behind, 1.0),
    S(T(242) + 0.3, 999, 'tw', outro, tw=58.8),
]
def shot_at(t):
    for s in SHOTS:
        if s['t0'] <= t < s['t1']: return s
    return SHOTS[-1]

ZCYCLE = [1.0, 1.24, 1.1, 1.34]
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
    if s['zoom'] == 'hook':
        return 1.0 + 0.3 * (1 - eio(prog(t, 0.0, T(6) - 0.1)))
    base = s['zoom'] if s['zoom'] is not None else zb
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + 0.05 * (1 - eo(prog(t, t0, 0.28))))

SPLIT_Y = 1110
def to_bgra(arr, rgb, y0=0):
    h = rgb.shape[0]
    arr[y0:y0 + h, :, 0] = rgb[..., 2]; arr[y0:y0 + h, :, 1] = rgb[..., 1]; arr[y0:y0 + h, :, 2] = rgb[..., 0]

def composite_person(arr, rgb, m, y0=0, x0=0):
    h, w = m.shape
    a = m[..., None]
    region = arr[y0:y0 + h, x0:x0 + w, :3].astype(np.float32)
    bgr = rgb[..., ::-1].astype(np.float32)
    arr[y0:y0 + h, x0:x0 + w, :3] = (bgr * a + region * (1 - a)).astype(np.uint8)

def render_frame(img, src, st, t, fi):
    s = shot_at(t); kind = s['kind']
    arr = np.empty((H, W, 4), np.uint8); arr[..., 3] = 255
    sub_y = 1395
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W * 4)
    ctx = cairo.Context(surf)
    if kind == 'face':
        z = face_zoom(t); box = crop_box(z)
        fr = np.asarray(img.resize((W, H), Image.BILINEAR, box=box))
        to_bgra(arr, fr)
        if s['behind']:
            s['behind'](ctx, t, fi); surf.flush()
            composite_person(arr, fr, mask_for(src, st, box, (W, H), fi))
            surf.mark_dirty()
        if s['front']: s['front'](ctx, t, fi)
    elif kind == 'tw':
        tt = s['tw'] + (t - s['t0'])
        f = tw_frame(tt)
        zin = 1.0 + 0.12 * (1 - eo(prog(t, s['t0'], 0.22)))       # zoom-in transition into each clip
        oy = (TWH - H) // 2
        if zin > 1.001:
            im = Image.fromarray(f); cw, ch = W / zin, H / zin
            fr = np.asarray(im.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, oy + (H - ch) / 2, (W + cw) / 2, oy + (H + ch) / 2)))
        else:
            fr = f[oy:oy + H]
        to_bgra(arr, fr)
        # speaker cut-out in the corner (reaction style)
        box = crop_box(1.0)
        pw, ph = 470, 836
        face_small = np.asarray(img.resize((pw, ph), Image.BILINEAR, box=box))
        m = mask_for(src, st, box, (pw, ph), fi)
        pk = eo(prog(t, s['t0'], 0.2))
        yoff = int(H - ph + 60 + (1 - pk) * 80)
        x0 = W - pw + 40
        vis_h = H - yoff; vis_w = W - x0
        composite_person(arr, face_small[:vis_h, :vis_w], m[:vis_h, :vis_w], yoff, x0)
        surf.mark_dirty()
        if s['front']: s['front'](ctx, t, fi)
        sub_y = 1090
    elif kind == 'split':
        box = crop_box(1.25, cy=0.40, size=(W, H - SPLIT_Y))
        fp = np.asarray(img.resize((W, H - SPLIT_Y), Image.BILINEAR, box=box))
        to_bgra(arr, fp, SPLIT_Y); surf.mark_dirty()
        ctx.save(); ctx.rectangle(0, 0, W, SPLIT_Y); ctx.clip(); s['front'](ctx, t, fi); ctx.restore()
        for i in range(10):
            ctx.rectangle(0, SPLIT_Y + i * 2, W, 2); ctx.set_source_rgba(0, 0, 0, 0.16 * (1 - i / 10)); ctx.fill()
        ctx.rectangle(0, SPLIT_Y - 3, W, 6); rgba(ctx, INK); ctx.fill()
        sub_y = 1790
    elif kind == 'paper':
        z = face_zoom(s['t0'] - 0.01); box = crop_box(z)
        to_bgra(arr, np.asarray(img.resize((W, H), Image.BILINEAR, box=box))); surf.mark_dirty()
        dx = W * (1 - eo(prog(t, s['t0'], 0.2))) if s['extra'].get('slide') else 0
        ctx.save(); ctx.translate(dx, 0)
        for i in range(12):
            ctx.rectangle(-24 + i * 2, 0, 2, H); ctx.set_source_rgba(0, 0, 0, 0.2 * i / 12); ctx.fill()
        s['front'](ctx, t, fi); ctx.restore()
        sub_y = 1640
    if t < TOTAL: subtitles(ctx, t, sub_y)
    surf.flush()
    return arr[..., [2, 1, 0]]

# ---------------- sound (clicks + emphasis only) ----------------
EV = []
def ev(kind, at, g=1.0): EV.append((kind, at, g))
def build_events():
    for i in (6, 8): ev('click', T(i) - 0.04, 0.8)
    ev('pop', T(15) - 0.05, 1.0)
    ev('pop', T(19) - 0.05, 0.6)
    for s in SHOTS:
        if s['kind'] in ('tw', 'split', 'paper') and s['t0'] > 0.5: ev('click', s['t0'] - 0.01, 0.7)
    ev('pop', T(24) + 0.1, 0.5)
    ev('click', T(31) + 0.2, 0.7); ev('pop', T(37) - 0.05, 0.6); ev('click', T(39) - 0.05, 0.6); ev('pop', T(44) - 0.05, 0.7)
    for tl, _, _ in LEVELS: ev('pop', tl, 0.8)
    ev('scribble', LEVELS[1][0], 0.4)
    ev('click', T(85) - 0.04, 0.6); ev('click', T(87) - 0.04, 0.6)
    ev('pop', T(95) - 0.05, 0.6); ev('pop', T(102) - 0.1, 0.8); ev('pop', T(111) - 0.05, 0.7); ev('pop', T(114) - 0.05, 0.7)
    ev('pop', T(131) - 0.05, 0.8); ev('pop', T(136) - 0.05, 0.6); ev('scribble', T(151), 0.4)
    for i in range(22): ev('type', T(166) + i * (T(179) - T(166)) / 22, 0.5)
    for i in range(3): ev('tick', T(179) - 0.05 + i * 0.14, 0.7)
    ev('pop', T(180) - 0.05, 0.6)
    ev('click', T(191) - 0.04, 0.7); ev('click', T(192) - 0.04, 0.7)
    ev('scribble', T(206) - 0.05, 0.4)
    for ti in (T(206), T(208), T(209), T(209) + 0.35): ev('pop', ti, 0.5)
    ev('scribble', T(216), 0.4)
    ev('click', T(224) - 0.04, 0.7); ev('pop', T(228) - 0.05, 0.6); ev('pop', T(232) - 0.05, 0.6)
    ev('scribble', T(228) + 0.2, 0.4); ev('scribble', T(232) + 0.15, 0.4)
    ev('pop', T(241) - 0.05, 0.9); ev('pop', TOTAL - 0.4, 0.7)

def build_audio():
    with wave.open(os.path.join(HERE, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    SR = R.SR
    mix = np.zeros((int((DUR + 1) * SR), 2), np.float32); mix[:len(v)] += v
    rng = np.random.default_rng(3)
    for kind, at, g in EV:
        y = R.synth(kind, rng) * g; i0 = int(at * SR)
        seg = mix[i0:i0 + len(y)]; n = len(seg); pan = rng.uniform(-0.2, 0.2)
        seg[:, 0] += y[:n] * (1 - pan); seg[:, 1] += y[:n] * (1 + pan)
    mix = mix[:int(DUR * SR)]
    pk = np.abs(mix).max()
    if pk > 0.97: mix *= 0.97 / pk
    with wave.open(os.path.join(HERE, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------- main ----------------
def reader(path):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', 'fps=30,scale=1440:2560,eq=contrast=1.06:saturation=1.1:gamma=0.98',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 3)
    k = 0
    while True:
        b = p.stdout.read(SW * SH * 3)
        if len(b) < SW * SH * 3: break
        yield k, b; k += 1
    p.kill()

def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    cur_src, it, cur_k, cur_b = None, None, -1, None
    for fi in want:
        t = fi / FPS
        src, st = src_of(min(t, TOTAL - 0.001))
        if t >= TOTAL: st = st + (t - TOTAL + 0.001)
        if src != cur_src:
            it = reader(SRCF[src]); cur_src = src; cur_k, cur_b = next(it)
        k = int(round(st * FPS))
        while cur_k < k:
            try: cur_k, cur_b = next(it)
            except StopIteration: break
        yield fi, t, src, st, Image.frombuffer('RGB', (SW, SH), cur_b, 'raw', 'RGB', 0, 1)

def main():
    load_tw(); prebuild_blocks(); build_events()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(HERE, 'prev'), exist_ok=True)
        for fi, t, src, st, img in frames(times):
            Image.fromarray(np.ascontiguousarray(render_frame(img, src, st, t, fi))).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    outp = sys.argv[2]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', os.path.join(HERE, 'mix.wav'),
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp], stdin=subprocess.PIPE)
    for fi, t, src, st, img in frames():
        enc.stdin.write(np.ascontiguousarray(render_frame(img, src, st, t, fi)).tobytes())
        if fi % 300 == 0: print('frame', fi, flush=True)
    enc.stdin.close(); enc.wait(); print('done', outp)

if __name__ == '__main__':
    main()
