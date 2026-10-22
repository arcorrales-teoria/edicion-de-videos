import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from render import *          # drawing helpers, fonts, palette, paper, easing (v1 renderer)
import render as R
_scale = cairo.Context.scale
cairo.Context.scale = lambda self, sx, sy=None: _scale(self, max(sx, 1e-3), max(sx if sy is None else sy, 1e-3))
from edit import SEGS, src_of, seg_index

S2 = HERE
SRC = '/Users/acorrales/Downloads/IMG_8841.MOV'
TWSRC = '/Users/acorrales/Downloads/Twitter Video Downloader (2).mp4'
DUR = sum(b - a for a, b in SEGS)
FCX, FCY = 0.43, 0.42

# ---------------- words (output time) ----------------
_ws = [w for s in json.load(open(os.path.join(S2, 'v16.json')))['segments'] for w in s['words']]
FIX = {0: 'Claude', 13: 'ese', 21: 'Claude.', 22: 'Es', 23: 'un', 28: 'antes,', 31: 'mí,', 38: 'problema,',
       44: 'videos,', 47: 'torturosa.', 50: 'Claude?', 51: 'Literalmente', 54: '5.5,', 59: 'prompt,', 65: 'Claude',
       66: 'Code,', 70: 'video', 74: 'puede', 82: 'manera,', 84: 'subtítulos,', 87: 'todo,', 94: 'a',
       95: 'CapCut.', 98: 'bueno.', 109: 'ahora.', 117: 'mismo?', 118: 'Que', 127: 'parecer.', 128: 'Y',
       140: 'promptearle', 143: 'Claude', 152: 'sonido,', 159: 'más,', 171: 'mismo.', 172: 'Entonces',
       175: 'pruébenlo,', 180: 'va.', 181: 'Y', 188: 'Claude,', 192: 'Claude.'}
DROP = {14, 24}
WORDS = []
for i, w in enumerate(_ws):
    if i in DROP: continue
    if i == 55:
        WORDS[-1] = (WORDS[-1][0], w['end'], WORDS[-1][2]); continue
    txt = FIX.get(i, w['word'].strip())
    WORDS.append((w['start'], w['end'], txt))
def T(i):  # output start time of original whisper word index i
    return _ws[i]['start']

# ---------------- subtitles ----------------
HIDE_SUBS = [(1.06, 2.42)]
def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) for x in cur)
        brk = (len(cur) >= 4 or chars >= 16 or w[2][-1] in '.,?' or nxt is None or nxt[0] - w[1] > 0.35
               or (nxt and len(nxt[2]) > 11 and chars > 10))
        if brk: ch.append(cur); cur = []
    out = []
    for i, c in enumerate(ch):
        st = c[0][0] - 0.03
        en = ch[i + 1][0][0] - 0.03 if i + 1 < len(ch) else c[-1][1] + 0.4
        out.append((st, min(en, c[-1][1] + 0.5), c))
    return out
CHUNKS = build_chunks()

def subtitles(ctx, t, y):
    if any(a <= t < b for a, b in HIDE_SUBS): return
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

# ---------------- extra helpers ----------------
def stamp(ctx, label, x, y, t, t0, col=RED, rot=-0.12, size=120):
    if t < t0: return
    p = prog(t, t0, 0.2); s = 1.9 - 0.9 * eo(p); a = c01(p * 3)
    tt = text(label, F_LABEL, size, col, spacing=4)
    w, h = tt[4] + 70, size * 0.95 + 36
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.push_group()
    rrect(ctx, -w/2, -h/2, w, h, 14); rgba(ctx, CREAM, 0.88); ctx.fill()
    rrect(ctx, -w/2, -h/2, w, h, 14); rgba(ctx, col); ctx.set_line_width(9); ctx.stroke()
    rrect(ctx, -w/2 + 12, -h/2 + 12, w - 24, h - 24, 8); rgba(ctx, col); ctx.set_line_width(3); ctx.stroke()
    put(ctx, tt, 0, 8)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a); ctx.restore()

def person(ctx, x, y, s, col=INK):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.arc(0, -38, 24, 0, 2 * math.pi); rgba(ctx, col); ctx.fill()
    ctx.move_to(-40, 40); ctx.curve_to(-40, -6, 40, -6, 40, 40); ctx.close_path(); ctx.fill()
    ctx.restore()

def clock(ctx, x, y, r, t):
    ctx.arc(x, y, r, 0, 2 * math.pi); rgba(ctx, CREAM); ctx.fill()
    ctx.arc(x, y, r, 0, 2 * math.pi); rgba(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    for ang, ln, lw in [(t * 9, 0.75, 6), (t * 0.9, 0.5, 9)]:
        ctx.move_to(x, y); ctx.line_to(x + math.sin(ang) * r * ln, y - math.cos(ang) * r * ln)
        ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); rgba(ctx, TERRA if lw == 6 else INK); ctx.stroke()

def gear(ctx, x, y, r, teeth, ang, col):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    n = teeth * 4
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        rr = r if (i // 2) % 2 == 0 else r * 0.8
        (ctx.move_to if i == 0 else ctx.line_to)(math.cos(a) * rr, math.sin(a) * rr)
    ctx.close_path(); rgba(ctx, col); ctx.fill()
    ctx.arc(0, 0, r * 0.3, 0, 2 * math.pi); rgba(ctx, CREAM); ctx.fill()
    ctx.restore()

def speaker(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-40, -18); ctx.line_to(-18, -18); ctx.line_to(8, -42); ctx.line_to(8, 42); ctx.line_to(-18, 18)
    ctx.line_to(-40, 18); ctx.close_path(); rgba(ctx, INK); ctx.fill()
    for i, r in enumerate((26, 46)):
        a = 0.55 + 0.45 * math.sin(t * 8 - i)
        ctx.arc(14, 0, r, -0.8, 0.8); rgba(ctx, TERRA, a); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()

def pop_scale(t, t0, d=0.28, s=2.0): return eback(prog(t, t0, d), s)

# ---------------- twitter frames ----------------
TW_USE = []  # (tw_start, dur) ranges we need
HOOK_TW = (2.0, 1.08)
MONTAGE = [(11.35, 1.0), (6.25, 0.7), (8.40, 0.55), (12.45, 0.55), (14.10, 0.62)]
INSET_TW = (3.72, 1.40)
TW_USE = [HOOK_TW] + MONTAGE + [INSET_TW]
TWF = {}
def load_tw():
    need = set()
    for a, d in TW_USE:
        for k in range(int(a * FPS) - 1, int((a + d) * FPS) + 3): need.add(k)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', TWSRC, '-vf', 'fps=30,scale=1080:608', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    k = 0
    while True:
        b = p.stdout.read(1080 * 608 * 3)
        if len(b) < 1080 * 608 * 3: break
        if k in need: TWF[k] = np.frombuffer(b, np.uint8).reshape(608, 1080, 3)
        k += 1
def tw_frame(tt):
    k = int(round(tt * FPS))
    while k not in TWF and k > 0: k -= 1
    return TWF[k]

def tw_fullscreen(arr, tt, zoom=1.0):
    f = tw_frame(tt)
    if zoom != 1.0:
        im = Image.fromarray(f); cw, ch = 1080 / zoom, 608 / zoom
        f = np.asarray(im.resize((1080, 608), Image.BILINEAR, box=((1080 - cw) / 2, (608 - ch) / 2, (1080 + cw) / 2, (608 + ch) / 2)))
    top = np.median(f[:6].reshape(-1, 3), axis=0); bot = np.median(f[-6:].reshape(-1, 3), axis=0)
    y0 = 660
    arr[:y0, :, :3] = top[::-1]; arr[y0 + 608:, :, :3] = bot[::-1]
    arr[y0:y0 + 608, :, 0] = f[..., 2]; arr[y0:y0 + 608, :, 1] = f[..., 1]; arr[y0:y0 + 608, :, 2] = f[..., 0]

def tw_surface(tt, w, h):
    im = Image.fromarray(tw_frame(tt)).resize((w, h), Image.BILINEAR).convert('RGBA')
    return pil_surface(im)

# ---------------- scenes (all times = output seconds) ----------------
def s_hook_title(ctx, t, fi):  # EDITAR VIDEOS / POR TI
    t0, t1 = T(3), T(5)
    k = pop_scale(t, t0, 0.22, 1.6)
    ctx.save(); ctx.translate(540, 250); ctx.rotate(-0.03); ctx.scale(k, k)
    a = text('EDITAR VIDEOS', F_LABEL, 168, INK, spacing=4)
    highlighter(ctx, -a[4] / 2 - 26, -92, a[4] + 52, 150, 1.0, seed=5)
    put(ctx, a, 0, 0)
    ctx.restore()
    if t >= t1:
        k2 = pop_scale(t, t1, 0.22, 2.2)
        ctx.save(); ctx.translate(540, 420); ctx.rotate(0.03); ctx.scale(k2, k2)
        b = text('POR TI', F_LABEL, 150, CREAM, spacing=6)
        w = b[4] + 70
        shadow(ctx, -w / 2, -80, w, 150, 18); rrect(ctx, -w / 2, -80, w, 150, 18); rgba(ctx, TERRA); ctx.fill()
        put(ctx, b, 0, 6)
        ctx.restore()

def s_this_video(ctx, t, fi, t0):  # hand-drawn frame around the screen
    p = eio(prog(t, t0, 0.7))
    m = 44
    pts = [(m, m + 6), (W - m, m), (W - m + 4, H - m), (m - 2, H - m - 4), (m, m + 6)]
    dense = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for u in np.linspace(0, 1, 30): dense.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
    partial(ctx, jit(dense, 1.4, fi // 4), p, 12, YEL)
    if t > t0 + 0.25:
        k = pop_scale(t, t0 + 0.25, 0.25, 2)
        ctx.save(); ctx.translate(250, 120); ctx.rotate(-0.04); ctx.scale(k, k)
        lab = text('ESTE VIDEO', F_LABEL, 64, INK, spacing=4); w = lab[4] + 60
        shadow(ctx, -w / 2, -45, w, 90, 12); rrect(ctx, -w / 2, -45, w, 90, 12); rgba(ctx, YEL); ctx.fill()
        put(ctx, lab, 0, 5); ctx.restore()

def s_checklist(ctx, t, fi):
    t0 = T(16) - 0.05
    k = pop_scale(t, t0, 0.3, 1.5)
    ctx.save(); ctx.translate(540, 270); ctx.rotate(-0.02); ctx.scale(k, k)
    card(ctx, -460, -170, 920, 340, 26)
    items = ['Cortes', 'Subtítulos', 'Animaciones', 'Sonido']
    for i, it in enumerate(items):
        ti = t0 + 0.12 + i * 0.22
        r, c = divmod(i, 2)
        x, y = -410 + c * 450, -70 + r * 140
        rrect(ctx, x, y - 34, 68, 68, 14); rgba(ctx, INK); ctx.set_line_width(5); ctx.stroke()
        if t >= ti:
            s = pop_scale(t, ti, 0.2, 2.5)
            ctx.save(); ctx.translate(x + 34, y); ctx.scale(s, s)
            rrect(ctx, -34, -34, 68, 68, 14); rgba(ctx, hexc('3E9B5F')); ctx.fill(); ctx.restore()
            check(ctx, x + 34, y, 1.0, prog(t, ti + 0.04, 0.15), CREAM, 8)
        put(ctx, text(it, F_SERIF, 50, INK), x + 90, y + 2, ax=0, alpha=0.35 + 0.65 * c01((t - ti) / 0.1))
    ctx.restore()
    tc = T(21) - 0.05
    if t >= tc:
        k = pop_scale(t, tc, 0.28, 2.2)
        ctx.save(); ctx.translate(760, 470); ctx.rotate(0.05); ctx.scale(k, k)
        lab = text('con Claude', F_BOLD, 54, CREAM); w = lab[4] + 130
        shadow(ctx, -w / 2, -48, w, 96, 48); rrect(ctx, -w / 2, -48, w, 96, 48); rgba(ctx, TERRA); ctx.fill()
        spark(ctx, -w / 2 + 55, 0, 27, CREAM, 8, rot=t); put(ctx, lab, -w / 2 + 98, 2, ax=0)
        ctx.restore()

def s_gamechanger(ctx, t, fi):
    stamp(ctx, 'GAME CHANGER', 540, 300, t, T(25) - 0.05, RED, -0.09, 130)

def s_suffer(ctx, t, fi):
    ta = T(29)
    if ta <= t < T(32) + 0.1:
        a = c01((t - ta) / 0.12) * (1 - c01((t - T(32)) / 0.1))
        put(ctx, text('yo también', F_HAND, 72, INK, stroke=0), 800, 250, alpha=a, rot=-0.06)
        hand_arrow(ctx, (760, 300), (640, 420), 40, eio(prog(t, ta + 0.05, 0.3)), 8, INK, 71 + fi // 4, head=28)
    tp = T(32) - 0.05
    if t >= tp:
        k = pop_scale(t, tp, 0.28, 1.4)
        ctx.save(); ctx.translate(540, 270); ctx.scale(k, k); ctx.rotate(0.015)
        card(ctx, -440, -160, 880, 320, 26)
        tl = T(38) - 0.05
        title = text('EL MISMO PROBLEMA', F_LABEL, 62, INK, spacing=4)
        highlighter(ctx, -title[4] / 2 - 14, -130, title[4] + 28, 58, prog(t, tl + 0.1, 0.3), seed=8)
        put(ctx, title, 0, -98, alpha=0.25 + 0.75 * c01((t - tl) / 0.1))
        for i in range(7):
            ti = tp + 0.05 + i * 0.07
            s = pop_scale(t, ti, 0.22, 2.5)
            if s <= 0: continue
            x = -360 + i * 120
            person(ctx, x, 50, s * 1.05, TERRA if i == 3 else INK)
            if t > tl:  # sweat drops
                dy = ((t - tl) * 60 + i * 13) % 40
                ctx.arc(x + 34, -8 + dy, 6, 0, 2 * math.pi); rgba(ctx, hexc('6A9BD1'), 1 - dy / 40); ctx.fill()
        ctx.restore()

def s_torture(ctx, t, fi):  # paper cutaway
    paper(ctx, fi)
    t0 = T(41) - 0.05
    hk = eo(prog(t, t0, 0.25))
    put(ctx, text('EDITAR VIDEOS', F_LABEL, 130, INK, spacing=4), 470, 330 + 20 * (1 - hk), alpha=hk)
    clock(ctx, 900, 320, 78, (t - t0) * 1.5)
    put(ctx, text('horas y horas…', F_HAND, 54, TERRA), 860, 460, alpha=c01((t - t0 - 0.5) / 0.2), rot=-0.03)
    # messy timeline
    card(ctx, 70, 560, 940, 560, 24, hexc('2A2927'))
    rng = np.random.default_rng(4)
    for tr in range(5):
        y = 610 + tr * 100
        ctx.rectangle(100, y + 70, 880, 2); rgba(ctx, CREAM, 0.15); ctx.fill()
        x = 100
        j = 0
        while x < 960:
            w = rng.uniform(40, 150)
            ti = t0 + 0.1 + (tr * 6 + j) * 0.025
            s = pop_scale(t, ti, 0.18, 2.4)
            if s > 0:
                ctx.save(); ctx.translate(x + w / 2, y + 35); ctx.scale(1, s)
                rrect(ctx, -w / 2 + 3, -30, min(w, 980 - x) - 6, 60, 8); rgba(ctx, hexc(TILE[(tr + j) % 6])); ctx.fill()
                ctx.restore()
            x += w; j += 1
    ph = 100 + 860 * ((t - t0) * 0.9 % 1)
    ctx.rectangle(ph, 590, 4, 510); rgba(ctx, RED); ctx.fill()
    stamp(ctx, 'TORTUROSA', 540, 830, t, T(47) - 0.03, RED, -0.1, 150)

def s_opus(ctx, t, fi):
    t0 = T(52) - 0.05
    if t < t0: return
    k = eback(prog(t, t0, 0.34), 1.6)
    ctx.save(); ctx.translate(540, -220 + (270 + 220) * k); ctx.rotate(-0.03)
    card(ctx, -400, -150, 800, 300, 26)
    lab = text('EL MODELO', F_LABEL, 54, INK, spacing=4)
    highlighter(ctx, -lab[4] / 2 - 16, -118, lab[4] + 32, 56, prog(t, t0 + 0.18, 0.28), seed=11)
    put(ctx, lab, 0, -84)
    t1 = text('Claude Opus ', F_SERIF, 96, INK); t2 = text('5.5', F_SERIF, 96, TERRA)
    tw = t1[4] + t2[4]
    put(ctx, t1, -tw / 2, 44, ax=0); ox = -tw / 2 + t1[4]
    put(ctx, t2, ox, 44, ax=0)
    tc = T(54) - 0.02
    if t >= tc:
        pts = jit(hand_ellipse(ox + t2[4] / 2, 50, t2[4] / 2 + 22, 64, 9), 1.0, 9 + fi // 4)
        partial(ctx, pts, eio(prog(t, tc, 0.4)), 7, TERRA)
    ctx.restore()

TERM_PROMPT = 'Edita este video: cortes, subtítulos y animaciones'
TLINES = R.wrap(TERM_PROMPT, F_MONO, 40, 760)
def s_terminal(ctx, t, fi):  # split top panel
    paper(ctx, fi)
    t0 = T(56) - 0.1
    k = pop_scale(t, t0 - 0.1, 0.3, 1.3)
    ctx.save(); ctx.translate(540, 560); ctx.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    shadow(ctx, -470, -330, 940, 660, 26, 0.3, 14)
    rrect(ctx, -470, -330, 940, 660, 26); rgba(ctx, hexc('1F1E1D')); ctx.fill()
    ctx.save(); rrect(ctx, -470, -330, 940, 84, 26); ctx.clip()
    ctx.rectangle(-470, -330, 940, 84); rgba(ctx, hexc('2E2D2B')); ctx.fill(); ctx.restore()
    for i, c in enumerate(['FF5F57', 'FEBC2E', '28C840']):
        ctx.arc(-420 + i * 44, -288, 13, 0, 2 * math.pi); rgba(ctx, hexc(c)); ctx.fill()
    tcode = T(65) - 0.05
    title = text('Claude Code', F_MONO, 40, CREAM if t < tcode else INK)
    if t >= tcode:
        highlighter(ctx, -title[4] / 2 - 18, -314, title[4] + 36, 54, prog(t, tcode, 0.25), seed=33)
    put(ctx, title, 0, -288)
    spark(ctx, -title[4] / 2 - 44, -288, 18, TERRA, 6, rot=t)
    # prompt lines
    n = int(len(TERM_PROMPT) * prog(t, t0 + 0.1, 1.0)); rem = n; y = -210
    put(ctx, text('>', F_MONO, 40, TERRA), -420, y, ax=0, ay=0)
    cur = None
    for ln in TLINES:
        seg = ln[:max(0, rem)]
        if seg: put(ctx, text(seg, F_MONO, 40, CREAM), -380, y, ax=0, ay=0)
        if cur is None and rem <= len(ln): cur = (seg, y)
        rem -= len(ln) + 1; y += 58
    if cur is None: cur = (TLINES[-1], y - 58)
    if n < len(TERM_PROMPT) or (fi // 8) % 2 == 0:
        cx = -380 + ImageFont.truetype(F_MONO, 40).getlength(cur[0]) + 8
        ctx.rectangle(cx, cur[1] + 8, 20, 46); rgba(ctx, CREAM, 0.8); ctx.fill()
    # file chip drops in on "le das tu video"
    tf = T(67) - 0.05
    if t >= tf:
        dk = eback(prog(t, tf, 0.35), 1.8)
        yy = -500 + (130 + 500) * dk
        lab = text('IMG_8841.MOV', F_MONO, 40, INK); w = lab[4] + 120
        shadow(ctx, -w / 2, yy - 50, w, 100, 18)
        rrect(ctx, -w / 2, yy - 50, w, 100, 18); rgba(ctx, CREAM); ctx.fill()
        play_icon(ctx, -w / 2 + 52, yy, 0.42, TERRA)
        put(ctx, lab, -w / 2 + 96, yy + 2, ax=0)
        if t > tf + 0.4:
            put(ctx, text('Listo: video cargado', F_MONO, 34, hexc('28C840')), -420, 250, ax=0, alpha=c01((t - tf - 0.4) / 0.15))
    ctx.restore()

def s_chips(ctx, t, fi):
    items = [('Subtítulos', T(84)), ('Animaciones', T(86)), ('Sonido', T(86) + 0.25), ('Cortes', T(87))]
    for i, (lab, ti) in enumerate(items):
        if t < ti - 0.05: continue
        k = pop_scale(t, ti - 0.05, 0.25, 2.4)
        r, c = divmod(i, 2)
        x, y = 290 + c * 500, 170 + r * 150
        tt = text(lab, F_BOLD, 54, INK); w = tt[4] + 120
        ctx.save(); ctx.translate(x, y); ctx.rotate((-1) ** i * 0.03); ctx.scale(k, k)
        shadow(ctx, -w / 2, -50, w, 100, 50); rrect(ctx, -w / 2, -50, w, 100, 50); rgba(ctx, CREAM); ctx.fill()
        ctx.arc(-w / 2 + 50, 0, 24, 0, 2 * math.pi); rgba(ctx, hexc('3E9B5F')); ctx.fill()
        check(ctx, -w / 2 + 50, 0, 0.62, 1, CREAM, 6)
        put(ctx, tt, -w / 2 + 88, 2, ax=0)
        ctx.restore()

def s_capcut(ctx, t, fi):
    t0 = T(93) - 0.1
    if t < t0: return
    k = pop_scale(t, t0, 0.3, 1.5)
    ctx.save(); ctx.translate(540, 270); ctx.scale(k, k); ctx.rotate(-0.02)
    card(ctx, -440, -150, 880, 300, 26)
    put(ctx, text('NADA QUE ENVIDIARLE', F_LABEL, 50, INK, spacing=4), 0, -98)
    a = text('Claude', F_SERIF, 84, TERRA); b = text('CapCut', F_SERIF, 84, INK, idx=0)
    put(ctx, a, -220, 40);
    tb = T(95) - 0.05
    put(ctx, b, 230, 40, alpha=c01((t - tb) / 0.12))
    for dy in (-14, 14):
        partial(ctx, jit([(-40, 42 + dy), (40, 40 + dy)], 1.2, fi // 4 + dy), eo(prog(t, tb + 0.1, 0.25)), 9, INK)
    ctx.restore()
    tg = T(96)
    if t >= tg:
        put(ctx, text('¡muy bueno!', F_HAND, 70, TERRA), 780, 470, alpha=c01((t - tg) / 0.15), rot=-0.06)

def s_noexcuse(ctx, t, fi):
    stamp(ctx, 'SIN EXCUSAS', 540, 300, t, T(101) - 0.05, RED, 0.08, 140)
    tc = T(108) - 0.05
    if t >= tc:
        k = pop_scale(t, tc, 0.25, 2)
        ctx.save(); ctx.translate(540, 470); ctx.scale(k, k); ctx.rotate(-0.03)
        lab = text('A crear contenido', F_BOLD, 50, CREAM); w = lab[4] + 70
        shadow(ctx, -w / 2, -44, w, 88, 44); rrect(ctx, -w / 2, -44, w, 88, 44); rgba(ctx, INK); ctx.fill()
        put(ctx, lab, 0, 2); ctx.restore()

def s_same(ctx, t, fi):  # paper: todos iguales
    paper(ctx, fi)
    t0 = T(110) - 0.05
    hk = eo(prog(t, t0, 0.25))
    title = text('EL PROBLEMA', F_LABEL, 150, INK, spacing=4)
    highlighter(ctx, 540 - title[4] / 2 - 20, 280, title[4] + 40, 108, prog(t, T(115) - 0.05, 0.3), seed=44)
    put(ctx, title, 540, 340 + 20 * (1 - hk), alpha=hk)
    tg = T(118) - 0.05
    tw_, th_, gap = 270, 200, 36
    gx = 540 - (3 * tw_ + 2 * gap) / 2
    for i in range(9):
        r, c = divmod(i, 3)
        x = gx + c * (tw_ + gap); y = 520 + r * (th_ + gap)
        k = pop_scale(t, tg + i * 0.05, 0.24, 2.2)
        if k <= 0: continue
        ctx.save(); ctx.translate(x + tw_ / 2, y + th_ / 2); ctx.scale(k, k)
        shadow(ctx, -tw_ / 2, -th_ / 2, tw_, th_, 18, 0.16, 6)
        rrect(ctx, -tw_ / 2, -th_ / 2, tw_, th_, 18); rgba(ctx, hexc('BDB6AA')); ctx.fill()
        ctx.arc(-70, -40, 30, 0, 2 * math.pi); rgba(ctx, CREAM); ctx.fill()
        rrect(ctx, -110, 30, 220, 18, 9); rgba(ctx, CREAM); ctx.fill()
        rrect(ctx, -110, 60, 140, 14, 7); rgba(ctx, CREAM, 0.7); ctx.fill()
        ctx.restore()
    stamp(ctx, 'TODOS IGUALES', 540, 1260, t, T(127) - 0.1, RED, -0.07, 110)

def s_skill(ctx, t, fi):  # split top panel
    paper(ctx, fi)
    t0 = T(128)
    hk = eo(prog(t, t0, 0.25))
    title = text('EL SKILL QUE VIENE', F_LABEL, 66, INK, spacing=5)
    put(ctx, title, 540, 150 + 20 * (1 - hk), alpha=hk)
    partial(ctx, jit([(540 - title[4] / 2, 204), (540 + title[4] / 2, 198)], 1, 3), eio(prog(t, T(137) - 0.05, 0.35)), 7, TERRA)
    tp = T(140) - 0.05
    if t >= tp:
        big = text('Promptear bien', F_SERIF, 104, INK)
        highlighter(ctx, 540 - big[4] / 2 - 20, 300, big[4] + 40, 100, prog(t, tp + 0.1, 0.3), seed=55)
        put(ctx, big, 540, 350, scale=0.9 + 0.1 * eo(prog(t, tp, 0.2)), alpha=c01((t - tp) / 0.1))
    ta = T(143) - 0.05
    if t >= ta:
        k = pop_scale(t, ta, 0.25, 2.2)
        ctx.save(); ctx.translate(820, 440); ctx.rotate(0.05); ctx.scale(k, k)
        lab = text('a Claude', F_BOLD, 44, CREAM); w = lab[4] + 110
        rrect(ctx, -w / 2, -38, w, 76, 38); rgba(ctx, TERRA); ctx.fill()
        spark(ctx, -w / 2 + 44, 0, 20, CREAM, 6, rot=t); put(ctx, lab, -w / 2 + 78, 2, ax=0)
        ctx.restore()
    # items: sonido / motion graphics / + más
    ts = T(152) - 0.1
    if t >= ts:
        k = pop_scale(t, ts, 0.28, 1.8)
        ctx.save(); ctx.translate(250, 740); ctx.scale(k, k)
        card(ctx, -190, -150, 380, 300, 24)
        speaker(ctx, 0, -20, 1.4, t)
        put(ctx, text('Sonido', F_SERIF, 54, INK), 0, 100)
        ctx.restore()
    tm = T(156) - 0.1
    if t >= tm:
        k = pop_scale(t, tm, 0.28, 1.8)
        ctx.save(); ctx.translate(730, 740); ctx.scale(k, k)
        card(ctx, -270, -150, 540, 300, 24, hexc('1B1B1B'))
        tt = INSET_TW[0] + min(t - tm, INSET_TW[1] - 0.05)
        surf, buf = tw_surface(tt, 500, 216)
        ctx.save(); rrect(ctx, -250, -130, 500, 216, 14); ctx.clip()
        ctx.set_source_surface(surf, -250, -130); ctx.paint(); ctx.restore()
        put(ctx, text('Motion graphics', F_SERIF, 50, CREAM), 0, 118)
        ctx.restore()
    tmas = T(159) - 0.05
    if t >= tmas:
        put(ctx, text('+ mucho más', F_HAND, 64, TERRA), 540, 1000, alpha=c01((t - tmas) / 0.15), rot=-0.03)

def s_machine(ctx, t, fi):  # paper: máquina de contenido
    paper(ctx, fi)
    t0 = T(160) - 0.05
    tm = T(165) - 0.05
    title = text('MÁQUINA DE CONTENIDO', F_LABEL, 104, INK, spacing=3)
    highlighter(ctx, 540 - title[4] / 2 - 18, 290, title[4] + 36, 84, prog(t, tm, 0.3), seed=66)
    put(ctx, title, 540, 335, alpha=eo(prog(t, t0, 0.25)))
    # input prompt chip
    tin = eo(prog(t, t0 + 0.2, 0.5))
    if t > t0 + 0.2:
        x = -150 + (520 - (-150)) * tin
        lab = text('prompt', F_MONO, 40, INK); w = lab[4] + 50
        rrect(ctx, x - w / 2, 780 - 40, w, 80, 16); rgba(ctx, CREAM); ctx.fill()
        rrect(ctx, x - w / 2, 780 - 40, w, 80, 16); rgba(ctx, INK); ctx.set_line_width(4); ctx.stroke()
        put(ctx, lab, x, 782)
    # machine body
    k = pop_scale(t, t0 + 0.05, 0.3, 1.4)
    ctx.save(); ctx.translate(540, 820); ctx.scale(k, k)
    shadow(ctx, -230, -200, 460, 400, 30, 0.25, 12)
    rrect(ctx, -230, -200, 460, 400, 30); rgba(ctx, TERRA); ctx.fill()
    rrect(ctx, -230, -200, 460, 400, 30); rgba(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    gear(ctx, -70, -30, 95, 8, t * 2.2, CREAM)
    gear(ctx, 85, 70, 70, 6, -t * 2.9 + 0.3, INK)
    spark(ctx, 120, -120, 30, CREAM, 9, rot=t * 2)
    ctx.restore()
    # conveyor output
    ctx.rectangle(770, 960, 330, 10); rgba(ctx, INK); ctx.fill()
    tc = T(167) - 0.2
    if t > tc:
        for j in range(8):
            ph = ((t - tc) * 1.6 - j * 0.28)
            if ph < 0: continue
            x = 760 + (ph % 1.6) * 260
            ctx.save(); ctx.translate(x, 905)
            rrect(ctx, -52, -40, 104, 80, 12); rgba(ctx, hexc(TILE[j % 6])); ctx.fill()
            ctx.move_to(-10, -16); ctx.line_to(18, 0); ctx.line_to(-10, 16); ctx.close_path(); rgba(ctx, CREAM); ctx.fill()
            ctx.restore()
    put(ctx, text('videos, videos, videos…', F_HAND, 58, TERRA), 540, 1200, alpha=c01((t - tc - 0.4) / 0.2), rot=-0.02)

def s_cta(ctx, t, fi):
    tp = T(175) - 0.05
    stamp(ctx, 'PRUÉBENLO', 540, 280, t, tp, TERRA, -0.07, 130)
    tc = T(176) - 0.05
    if t >= tc:
        k = pop_scale(t, tc, 0.28, 2)
        ctx.save(); ctx.translate(560, 470); ctx.rotate(0.03); ctx.scale(k, k)
        lab = text('Cuéntenme en comentarios', F_BOLD, 44, INK); w = lab[4] + 140
        shadow(ctx, -w / 2, -48, w, 96, 48); rrect(ctx, -w / 2, -48, w, 96, 48); rgba(ctx, CREAM); ctx.fill()
        chat_icon(ctx, -w / 2 + 62, 0, 0.42); put(ctx, lab, -w / 2 + 110, 2, ax=0)
        ctx.restore()

def s_end(ctx, t, fi):
    s_this_video(ctx, t, fi, T(182) - 0.05)
    t0 = T(185) - 0.05
    if t < t0: return
    k = eback(prog(t, t0, 0.38), 1.5)
    ctx.save(); ctx.translate(540, 2150 - (2150 - 1650) * k); ctx.rotate(-0.02)
    card(ctx, -400, -120, 800, 240, 28)
    lab = text('ESTE VIDEO LO EDITÓ', F_LABEL, 50, INK, spacing=4)
    highlighter(ctx, -lab[4] / 2 - 14, -92, lab[4] + 28, 52, prog(t, t0 + 0.3, 0.3), seed=91)
    put(ctx, lab, 0, -62)
    t1 = text('Claude', F_SERIF, 92, TERRA); t2 = text(' al 100%', F_SERIF, 64, INK)
    tw = t1[4] + t2[4] + 70
    spark(ctx, -tw / 2 + 26, 42, 26, TERRA, 9, rot=t)
    put(ctx, t1, -tw / 2 + 70, 42, ax=0); put(ctx, t2, -tw / 2 + 70 + t1[4], 48, ax=0)
    ctx.restore()

def nothing(ctx, t, fi): pass

# shot list: (start, end, kind, draw, zoom or None=cycle, extra)
MT0 = T(76) - 0.02                       # montage starts on "videos (demasiado increíbles)"
MT1 = MT0 + sum(d for _, d in MONTAGE)
SHOTS = [
    (0.00, T(3) - 0.02, 'tw', None, None, {'tw': HOOK_TW[0]}),
    (T(3) - 0.02, T(7) - 0.02, 'face', s_hook_title, 1.36, {}),
    (T(7) - 0.02, T(16) - 0.05, 'face', lambda c, t, f: s_this_video(c, t, f, T(7)), 1.0, {}),
    (T(16) - 0.05, T(22) - 0.02, 'face', s_checklist, 1.16, {}),
    (T(22) - 0.02, T(27) - 0.02, 'face', s_gamechanger, 1.38, {}),
    (T(27) - 0.02, T(41) - 0.05, 'face', s_suffer, None, {}),
    (T(41) - 0.05, T(48) - 0.05, 'paper', s_torture, None, {'slide': True}),
    (T(48) - 0.05, T(56) - 0.2, 'face', s_opus, None, {}),
    (T(56) - 0.2, T(71) - 0.02, 'split', s_terminal, None, {}),
    (T(71) - 0.02, MT0, 'face', nothing, 1.3, {}),
    (MT0, MT1, 'montage', None, None, {}),
    (MT1, T(88) - 0.05, 'face', s_chips, 1.08, {}),
    (T(88) - 0.05, T(99) - 0.03, 'face', s_capcut, None, {}),
    (T(99) - 0.03, T(110) - 0.08, 'face', s_noexcuse, None, {}),
    (T(110) - 0.08, T(128) - 0.05, 'paper', s_same, None, {'slide': True}),
    (T(128) - 0.05, T(160) - 0.05, 'split', s_skill, None, {}),
    (T(160) - 0.05, T(172) - 0.03, 'paper', s_machine, None, {'slide': True}),
    (T(172) - 0.03, T(181) - 0.03, 'face', s_cta, None, {}),
    (T(181) - 0.03, 999, 'face', s_end, 1.0, {}),
]
def shot_at(t):
    for s in SHOTS:
        if s[0] <= t < s[1]: return s
    return SHOTS[-1]

# zoom cycling: a new framing on every jump cut / shot change (face shots without fixed zoom)
ZCYCLE = [1.0, 1.24, 1.1, 1.34]
BLOCKS = {}
def block_zoom(t):
    key = (seg_index(t), shot_at(t)[0])
    if key not in BLOCKS:
        BLOCKS[key] = (len(BLOCKS), t)
    return BLOCKS[key]
def prebuild_blocks():
    n = int(DUR * FPS)
    last = None
    for fi in range(n):
        t = fi / FPS; b = block_zoom(t)
    # assign zooms ensuring consecutive distinct
    order = sorted(BLOCKS.items(), key=lambda kv: kv[1][0])
    for i, (k, (idx, t0)) in enumerate(order):
        BLOCKS[k] = (ZCYCLE[i % len(ZCYCLE)], t0)

def face_zoom(t):
    st, en, kind, fn, z, ex = shot_at(t)
    zb, t0 = BLOCKS.get((seg_index(t), st), (1.12, st))
    base = z if z is not None else zb
    return base * (1 + 0.035 * eio(c01((t - t0) / 3.0))) * (1 + 0.045 * (1 - eo(prog(t, t0, 0.28))))

def frame_face(img, z, size=(W, H), cy=FCY):
    return face_frame(img, z, cx=FCX, cy=cy, size=size)

SPLIT_Y = 1110
def render_frame(img, t, fi):
    st, en, kind, fn, z, ex = shot_at(t)
    arr = np.empty((H, W, 4), np.uint8); arr[..., 3] = 255
    sub_y = 1395
    if kind in ('face', 'paper', 'split'):
        zz = face_zoom(t) if kind == 'face' else (face_zoom(st - 0.01) if kind == 'paper' else 1.2)
        fr = np.asarray(frame_face(img, zz))
        arr[..., 0] = fr[..., 2]; arr[..., 1] = fr[..., 1]; arr[..., 2] = fr[..., 0]
    elif kind == 'tw':
        tt = ex['tw'] + (t - st)
        tw_fullscreen(arr, tt, 1.0 + 0.06 * (t - st))
    elif kind == 'montage':
        acc = st
        for a, d in MONTAGE:
            if t < acc + d or (a, d) == MONTAGE[-1]:
                tw_fullscreen(arr, a + (t - acc), 1.04); break
            acc += d
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W * 4)
    ctx = cairo.Context(surf)
    if kind == 'face':
        fn(ctx, t, fi)
    elif kind == 'paper':
        dx = W * (1 - eo(prog(t, st, 0.2))) if ex.get('slide') else 0
        ctx.save(); ctx.translate(dx, 0)
        for i in range(12):
            ctx.rectangle(-24 + i * 2, 0, 2, H); ctx.set_source_rgba(0, 0, 0, 0.2 * i / 12); ctx.fill()
        fn(ctx, t, fi); ctx.restore()
        sub_y = 1640
    elif kind == 'split':
        fp = np.asarray(frame_face(img, 1.25, size=(W, H - SPLIT_Y), cy=0.44))
        pan = np.empty((H - SPLIT_Y, W, 4), np.uint8)
        pan[..., 0] = fp[..., 2]; pan[..., 1] = fp[..., 1]; pan[..., 2] = fp[..., 0]; pan[..., 3] = 255
        ps = cairo.ImageSurface.create_for_data(pan, cairo.FORMAT_ARGB32, W, H - SPLIT_Y, W * 4)
        ctx.save(); ctx.rectangle(0, 0, W, SPLIT_Y); ctx.clip(); fn(ctx, t, fi); ctx.restore()
        ctx.set_source_surface(ps, 0, SPLIT_Y); ctx.rectangle(0, SPLIT_Y, W, H - SPLIT_Y); ctx.fill()
        for i in range(10):
            ctx.rectangle(0, SPLIT_Y + i * 2, W, 2); ctx.set_source_rgba(0, 0, 0, 0.16 * (1 - i / 10)); ctx.fill()
        ctx.rectangle(0, SPLIT_Y - 3, W, 6); rgba(ctx, INK); ctx.fill()
        sub_y = 1790
    subtitles(ctx, t, sub_y)
    surf.flush()
    return arr[..., [2, 1, 0]]

# ---------------- sound ----------------
EV = []
def ev(kind, at, g=1.0): EV.append((kind, at, g))
def build_events():
    ev('impact', 0.0, 1.0)
    ev('impact', T(3) - 0.02, 0.7); ev('pop', T(5) - 0.02, 0.9)
    ev('whoosh', T(7) - 0.08, 0.6); ev('scribble', T(7), 0.7); ev('pop', T(7) + 0.25, 0.6)
    ev('pop', T(16) - 0.05, 0.7)
    for i in range(4): ev('tick', T(16) + 0.07 + i * 0.22, 0.8)
    ev('pop', T(21) - 0.05, 0.8)
    ev('thud', T(25) - 0.05, 1.0)
    ev('scribble', T(29), 0.5); ev('pop', T(32) - 0.05, 0.6)
    for i in range(7): ev('click', T(32) + i * 0.07, 0.45)
    ev('scribble', T(38) + 0.05, 0.4)
    ev('whoosh', T(41) - 0.1, 0.9)
    for i in range(10): ev('click', T(41) + 0.1 + i * 0.06, 0.35)
    ev('thud', T(47) - 0.03, 1.0)
    ev('swish', T(48) - 0.1, 0.6); ev('pop', T(52) - 0.05, 0.7); ev('scribble', T(54), 0.6)
    ev('whoosh', T(56) - 0.25, 0.6)
    for i in range(16): ev('type', T(56) + i * 0.06, 0.5)
    ev('scribble', T(65) - 0.05, 0.5); ev('pop', T(67) + 0.1, 0.9)
    ev('whoosh', MT0 - 0.08, 0.9)
    acc = MT0
    for a, d in MONTAGE[:-1]:
        acc += d; ev('swish', acc - 0.04, 0.55)
    ev('whoosh', MT1 - 0.06, 0.6)
    for i, tt in enumerate([T(84), T(86), T(86) + 0.25, T(87)]): ev('pop', tt - 0.05, 0.55)
    ev('pop', T(93) - 0.1, 0.6); ev('scribble', T(95) + 0.05, 0.4)
    ev('thud', T(101) - 0.05, 1.0); ev('pop', T(108) - 0.05, 0.6)
    ev('whoosh', T(110) - 0.15, 0.9); ev('scribble', T(115), 0.4)
    for i in range(9): ev('click', T(118) - 0.05 + i * 0.05, 0.35)
    ev('thud', T(127) - 0.1, 0.8)
    ev('whoosh', T(128) - 0.12, 0.5); ev('scribble', T(137), 0.4); ev('scribble', T(140), 0.5)
    ev('pop', T(143) - 0.05, 0.6); ev('pop', T(152) - 0.1, 0.7); ev('pop', T(156) - 0.1, 0.8)
    ev('whoosh', T(160) - 0.12, 0.9); ev('scribble', T(165), 0.4)
    ev('thud', T(175) - 0.05, 0.7); ev('pop', T(176) - 0.05, 0.7)
    ev('scribble', T(182), 0.5); ev('ding', T(185), 0.9)

def synth2(kind, rng):
    if kind == 'impact':
        n = int(0.6 * SR); tt = np.arange(n) / SR
        f = 48 + 90 * np.exp(-tt * 18); ph = 2 * np.pi * np.cumsum(f) / SR
        boom = np.sin(ph) * np.exp(-tt * 6)
        nz = rng.normal(0, 1, n); nz = np.convolve(nz, np.ones(8) / 8, 'same') * np.exp(-tt * 30)
        return (boom * 0.28 + nz * 0.08)
    if kind == 'thud':
        n = int(0.3 * SR); tt = np.arange(n) / SR
        f = 60 + 80 * np.exp(-tt * 30); ph = 2 * np.pi * np.cumsum(f) / SR
        nz = rng.normal(0, 1, n) * np.exp(-tt * 70)
        return np.sin(ph) * np.exp(-tt * 14) * 0.24 + nz * 0.05
    return R.synth(kind, rng)
SR = R.SR

def build_audio():
    with wave.open(os.path.join(S2, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mix = np.zeros((int((DUR + 1) * SR), 2), np.float32); mix[:len(v)] += v
    # twitter clip music under its visuals
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', TWSRC, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le',
                    os.path.join(S2, 'tw48.wav')])
    with wave.open(os.path.join(S2, 'tw48.wav')) as w:
        tw = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    def lay(out_t0, tw_t0, d, g, fin=0.03, fout=0.12):
        a = tw[int(tw_t0 * SR): int((tw_t0 + d) * SR)].copy(); n = len(a)
        env = np.ones(n); fi_, fo = int(fin * SR), int(fout * SR)
        env[:fi_] = np.linspace(0, 1, fi_); env[-fo:] = np.linspace(1, 0, fo)
        i0 = int(out_t0 * SR); mix[i0:i0 + n] += a * env[:, None] * g
    # twitter clip plays muted (its music clashed with the voice)
    rng = np.random.default_rng(3)
    for kind, at, g in EV:
        y = synth2(kind, rng) * g; i0 = int(at * SR)
        pan = rng.uniform(-0.2, 0.2); seg = mix[i0:i0 + len(y)]; n = len(seg)
        seg[:, 0] += y[:n] * (1 - pan); seg[:, 1] += y[:n] * (1 + pan)
    mix = mix[:int(DUR * SR)]
    peak = np.abs(mix).max()
    if peak > 0.97: mix *= 0.97 / peak
    with wave.open(os.path.join(S2, 'mix.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------- main ----------------
def reader():
    cmd = ['ffmpeg', '-v', 'error', '-i', SRC, '-vf', 'fps=30,scale=1440:2560,eq=contrast=1.06:saturation=1.1:gamma=0.98',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 3)
    k = 0
    while True:
        b = p.stdout.read(SW * SH * 3)
        if len(b) < SW * SH * 3: break
        yield k, b
        k += 1

def frames(times=None):
    """yield (fi, t, PIL image) for output frames, pulling source frames by the edit mapping"""
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    it = reader(); cur_k, cur_b = next(it)
    for fi in want:
        t = fi / FPS
        k = int(round(src_of(t) * FPS))
        while cur_k < k:
            try: cur_k, cur_b = next(it)
            except StopIteration: break
        yield fi, t, Image.frombuffer('RGB', (SW, SH), cur_b, 'raw', 'RGB', 0, 1)

def main():
    load_tw(); prebuild_blocks(); build_events()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(S2, 'prev'), exist_ok=True)
        for fi, t, img in frames(times):
            Image.fromarray(np.ascontiguousarray(render_frame(img, t, fi))).save(os.path.join(S2, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    outp = sys.argv[2]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', os.path.join(S2, 'mix.wav'),
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp], stdin=subprocess.PIPE)
    for fi, t, img in frames():
        enc.stdin.write(np.ascontiguousarray(render_frame(img, t, fi)).tobytes())
        if fi % 300 == 0: print('frame', fi, flush=True)
    enc.stdin.close(); enc.wait(); print('done', outp)

if __name__ == '__main__':
    main()
