"""IMG_8927 (hook) + IMG_8925 + IMG_8926 · "¿Tu web parece hecha con IA?" — 3 tools: UIMaxxing, Arc, Cult UI. 1.05x.
Hook full screen -> good-work_ title card (posterized, 'teoría by andrés corrales_', reference music bed) -> one split screen per tool
(speaker top, silent screen recording / page capture below, website pill on the seam) -> recap of the 3 links -> CTA full screen.
Subtitles: white Helvetica Neue Bold, active word in the teoría yellow. Framing locked per take. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit10 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {0: '¡Pilas!', 1: 'Estas', 25: 'IA,', 44: 'UIMaxxing.', 88: 'pegarle', 93: 'Claude', 94: 'Code,', 97: 'va', 102: 'Arc.',
       138: 'Cult UI.', 153: 'Claude', 225: 'generaste', 229: 'IA', 234: 'Entonces,', 236: 'saben:'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws) if i != 230]   # 230 = "ahí" (Whisper heard "con IA" as "con ella ahí")
def T(i): return _ws[i]['start']
def Te(i): return _ws[i]['end']

# ---------------- timeline: voice time vt <-> output time t (title card holds while the reference music bed plays) ----------------
T_CARD = T(34) - 0.03                      # "El último es el mejor, así que quédense."
TH = Te(41) + 0.03
MUSIC = os.path.join(HERE, 'card_music_full.wav')
with wave.open(MUSIC) as _w: MUSIC_DUR = _w.getnframes() / _w.getframerate()
HOLD = T_CARD + MUSIC_DUR - TH
def vt_of(t): return t if t < TH else (TH if t < TH + HOLD else t - HOLD)
def out_of(vt): return vt if vt < TH else vt + HOLD
TF = min(TH, E.HOOK_END / SPEED - 0.05)
def vt_frame(t): return TF if TH <= t < TH + HOLD else vt_of(t)
VTOTAL = E.TOTAL / SPEED
DUR = out_of(VTOTAL) + 0.3
def in_card(t): return T_CARD <= vt_of(t) and t < TH + HOLD

# ---------------- layout (voice time) ----------------
SPLITS = [(T(42) - 0.05, T(87) - 0.10, 'uimax'), (T(87) - 0.10, T(101) - 0.05, 'uimax_code'),
          (T(101) - 0.05, T(137) - 0.05, 'arc'), (T(137) - 0.05, T(171) - 0.05, 'cult'),
          (T(171) - 0.05, T(234) - 0.05, 'recap')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = [(T(44) - 0.05, T(101) - 0.05, 'uimaxx.ing'), (T(102) - 0.05, T(137) - 0.05, 'uiarc.dev'), (T(138) - 0.05, T(171) - 0.05, 'cult-ui.com')]

# ---------------- speaker framing: one locked box per take ----------------
FT = {'h': framing.FaceTrack(os.path.join(HERE, 'faces_8927.txt')), 'a': framing.FaceTrack(os.path.join(HERE, 'faces_8925.txt')),
      'b': framing.FaceTrack(os.path.join(HERE, 'faces_8926.txt'))}
def _take_box(s, lo, hi):
    ft = FT[s]; m = (ft.t >= lo) & (ft.t <= hi)
    b = ft.b[m] if m.any() else ft.box((lo + hi) / 2)[None]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 15); chin = np.percentile(b[:, 1] + b[:, 3], 85); h = chin - top
    return (cx - fw / 2, top - 0.12 * h, fw, h * 1.12)
TAKE_BOX = [_take_box(s, a, b) for s, a, b in E.SEGS]
CUTS = sorted({out_of(o / SPEED) for o in E.OFF} | {out_of(a) for a, b, k in SPLITS} | {out_of(SPLITS[-1][1])} | {TH + HOLD})
ZC = [1.0, 1.08, 1.0, 1.14]
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6) if t >= CUTS[0] else 0
    t0 = CUTS[i] if t >= CUTS[0] else 0; base = ZC[i % 4]
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))
def speaker(fr16, t, panel, extra=1.0):
    vt = vt_frame(t); te = min(vt * SPEED, E.TOTAL - 0.001); si = E.seg_index(te)
    box = framing.head_crop(TAKE_BOX[si], face_zoom(t) * extra, panel=panel, top_air=0.09)
    return fx.resize_f(fr16, box, panel)

# ---------------- bottom panel sources ----------------
def ff_frames(path, a, b, vf, n_out):
    """read [a, b] of a clip, cropped/scaled by vf, retimed to exactly n_out frames (uniform speed)"""
    rate = (b - a) / max(n_out / FPS, 1e-3)
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', path, '-an', '-vf',
                        f'setpts=PTS/{rate:.5f},fps={FPS},{vf},format=rgb24', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    sz = W * SEAM * 3; buf = p.stdout
    fr = [np.frombuffer(buf[i:i + sz], np.uint8).reshape(SEAM, W, 3) for i in range(0, len(buf) - sz + 1, sz)]
    return (fr + [fr[-1]] * max(0, n_out - len(fr)))[:n_out]

UIMAX = DL + 'UIMAXXING.mp4'
ARC = DL + 'ScreenRecording_10-04-2026 17-40-59_1.MP4'
UX_CROP = 'crop=990:880:338:115,scale=1080:960:flags=bicubic'          # page content only (no desktop wallpaper / side widget)
ARC_CROP = 'crop=1030:916:0:1010,scale=1080:960:flags=bicubic'        # the component preview, above that reel's own captions/IG UI
_cache = {}
def panel_clip(key, a, b):
    if key in _cache: return _cache[key]
    n = int(round((out_of(b) - out_of(a)) * FPS)) + 2
    if key == 'uimax':
        n1 = int(round((T(49) - 0.05 - a) * FPS))                        # landing while "La primera, UIMaxxing, esto es una locura"
        fr = ff_frames(UIMAX, 1.4, 3.6, UX_CROP, n1) + ff_frames(UIMAX, 3.6, 20.5, UX_CROP, n - n1)
    elif key == 'arc':
        fr = ff_frames(ARC, 3.6, 18.6, ARC_CROP, n)
    _cache[key] = fr; return fr

# landing still for the "copy this code" beat (command box at x 520-955, y 627-667 of the 1662x1080 recording)
_land = None
def uimax_code(vt, a, b):
    global _land
    if _land is None:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '2.8', '-i', UIMAX, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             capture_output=True).stdout
        _land = Image.frombytes('RGB', (1662, 1080), raw)
    k = eio(prog(vt, a, 1.2))
    cw = 990 + (760 - 990) * k; ch = cw * SEAM / W; cx = 830 + (738 - 830) * k; cy = 555 + (640 - 555) * k
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    img = _land.resize((W, SEAM), Image.BICUBIC, box=box)
    s = W / cw                                                           # command box in panel coords, for the highlight
    return np.asarray(img), ((520 - box[0]) * s, (627 - box[1]) * s, (955 - box[0]) * s, (667 - box[1]) * s)

# cult-ui page (Playwright full-page capture, 2x): pan from the title + card preview down to the install command
_cult = None
def cult_frame(vt, a, b):
    """card phase: tight on the Texture Card preview (x 812-1748 of the 2x capture); then pan down to the install command"""
    global _cult
    if _cult is None: _cult = Image.open(os.path.join(HERE, 'ref', 'cult_wide.png')).convert('RGB')
    t_copy = T(148) - 0.1
    if vt < t_copy:
        k = eio(prog(vt, a + 0.3, t_copy - a - 0.3)); x0, cw, y = 730, 1100, 380 + (1480 - 380) * k
    else:
        k = eio(prog(vt, t_copy, 0.8)); x0, cw = 730 + (560 - 730) * k, 1100; y = 1480 + (3372 - 1100 * SEAM / W / 2 - 1480) * k
    ch = cw * SEAM / W; box = (x0, y, x0 + cw, y + ch); s = W / cw
    hl = ((612 - x0) * s, (3340 - y) * s, (1400 - x0) * s, (3404 - y) * s)   # "pnpm dlx shadcn@latest add @cult-ui/texture-card"
    return np.asarray(_cult.resize((W, SEAM), Image.BICUBIC, box=box)), hl

def highlight(ctx, box, k):
    if k <= 0: return
    x0, y0, x1, y1 = box; pad = 10; x0 -= pad; y0 = y0 - pad + SEAM; x1 += pad; y1 = y1 + pad + SEAM
    w = (x1 - x0) * eo(k); r = 12
    ctx.new_sub_path(); ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0); ctx.arc(x0 + w - r, y1 - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi); ctx.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(YELF[0], YELF[1], YELF[2], 0.16 * c01(k * 2)); ctx.fill_preserve(); rgba(ctx, YELF); ctx.set_line_width(5); ctx.stroke()

# ---------------- recap of the three links ----------------
RECAP = [('UIMaxxing', 'uimaxx.ing'), ('Arc', 'uiarc.dev'), ('Cult UI', 'cult-ui.com')]
def recap(ctx, vt, a):
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(0.04, 0.04, 0.045); ctx.fill()
    hd = T_('LAS 3 HERRAMIENTAS', HN, 30, YELF, 0.16, idx=BOLD)
    put(ctx, hd, 90, SEAM + 190, alpha=c01((vt - a) / 0.3), ax=0)
    for k, (name, url) in enumerate(RECAP):
        e = expo_out(prog(vt, a + 0.25 + 0.3 * k, 0.5))
        if e <= 0: continue
        y = SEAM + 290 + k * 150; x = 90 + 30 * (1 - e)
        ctx.rectangle(x, y - 48, 96, 96); rgba(ctx, YELF, e); ctx.fill()
        put(ctx, T_(str(k + 1), HN, 64, (0.05, 0.05, 0.05, 1), 0, idx=BOLD), x + 48, y + 2, alpha=e)
        put(ctx, T_(name, HN, 60, WHITE, -0.02, idx=BOLD), x + 130, y - 18, alpha=e, ax=0)
        put(ctx, T_(url, HN, 38, GREY, 0, idx=REG), x + 130, y + 32, alpha=e, ax=0)
        if k == 2:                                                       # callback to the hook: "el último es el mejor"
            tg = T_('EL MEJOR', HN, 26, (0.05, 0.05, 0.05, 1), 0.12, idx=BOLD)
            tx = x + 130 + T_(name, HN, 60, WHITE, -0.02, idx=BOLD)[4] + 24
            ctx.rectangle(tx, y - 40, tg[4] + 28, 44); rgba(ctx, YELF, e); ctx.fill()
            put(ctx, tg, tx + 14, y - 17, alpha=e, ax=0)

# ---------------- website pill on the seam ----------------
def pill(ctx, vt):
    for a, b, url in PILLS:
        if a <= vt < b: break
    else: return
    e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - (b - 0.15)) / 0.15))
    tt = T_(url, HN, 50, WHITE, -0.02, idx=BOLD)
    w = tt[4] + 118; h = 92
    ctx.save(); ctx.translate(W / 2, SEAM + 22 * (1 - e))
    ctx.new_sub_path(); r = h / 2
    ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.72 * e); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 0.35 * e); ctx.set_line_width(2); ctx.stroke()
    gx = -w / 2 + 50
    ctx.arc(gx, 0, 17, 0, 2 * math.pi); ctx.save(); ctx.scale(0.45, 1); ctx.arc(gx / 0.45, 0, 17, 0, 2 * math.pi); ctx.restore()
    ctx.move_to(gx - 17, 0); ctx.line_to(gx + 17, 0)
    ctx.set_source_rgba(1, 1, 1, e); ctx.set_line_width(2.6); ctx.stroke()
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

_tit = [stroked(l, 116, YEL, 7, BOLD, -0.01) for l in TITLE]
def card_text(img, t):
    k = t - T_CARD
    if k < 0.15: return
    n = min(len(LABEL), int((k - 0.15) / 0.022) + 1)
    x0, y_lab = 60, 1120
    txt = LABEL[:n] + '_' if n < len(LABEL) else (LABEL if int(k * 2.2) % 2 == 0 else LABEL[:-1])
    sub = stroked(txt, 46, YEL, 4, REG); img.alpha_composite(sub[0], (x0 - sub[1], y_lab - sub[1]))
    if k > 0.15 + 0.022 * len(LABEL) + 0.12:
        y = y_lab + 64
        s = min(1.0, min(960 / ttw for _, _, ttw in _tit))          # one size for every line
        for timg, tpad, ttw in _tit:
            ti = timg if s >= 1 else timg.resize((int(timg.width * s), int(timg.height * s)), Image.LANCZOS)
            img.alpha_composite(ti, (int(x0 - tpad * s), int(y - tpad * s))); y += int(126 * s)

# ---------------- frame ----------------
def render_frame(fr16, t):
    vt = vt_of(t)
    sdr = np.zeros((H, W, 3), np.float32)
    if in_card(t):
        full = speaker(fr16, t, (W, H), extra=1 + 0.06 * eio(prog(t, TH, HOLD)))
        img = Image.fromarray(posterize(fx.to8(full))).convert('RGBA'); card_text(img, t)
        rgb8 = np.asarray(img.convert('RGB'))
        return rgb8.astype(np.float32) / 255, fx.srgb8_to_hlg(rgb8)
    sp = split_at(vt)
    arr, surf, ctx = fx.new_layer()
    if sp is None:
        sdr[:] = speaker(fr16, t, (W, H)); hdr = sdr.copy()
        subtitles(ctx, t, 1370)
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        bottom, hl, hk = None, None, 0
        if key in ('uimax', 'arc'):
            fr = panel_clip(key, a, b); bottom = fr[min(len(fr) - 1, int(round((t - out_of(a)) * FPS)))]
        elif key == 'uimax_code':
            bottom, hl = uimax_code(vt, a, b); hk = prog(vt, T(89) - 0.1, 0.5)          # "el siguiente código"
        elif key == 'cult':
            bottom, hl = cult_frame(vt, a, b); hk = prog(vt, T(148) + 0.75, 0.5)        # after the pan lands on the command
        if bottom is not None:
            sdr[SEAM:] = bottom.astype(np.float32) / 255; hdr[SEAM:] = fx.srgb8_to_hlg(bottom)
        else:
            recap(ctx, vt, a)
        if hl is not None: highlight(ctx, hl, hk)
        pill(ctx, vt)
        subtitles(ctx, t, 1065 if key != 'recap' else 1040, plate=True)
    surf.flush()
    fx.layer_over(sdr, hdr, arr)
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
    cut = int(TH * SR); m[:cut] = v[:cut]
    rest = v[cut:]; d0 = cut + int(HOLD * SR); m[d0:d0 + len(rest[:n - d0])] = rest[:n - d0]
    # title-card music bed (good work_ reference, 36.19-40.87 s): 1.5 LU under the voice as in the reference, ducked 8 dB
    # while I'm still talking, hard cut at the end
    with wave.open(MUSIC) as w:
        mu = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    mu = mu * 10 ** (3.4 / 20)
    tt = np.arange(len(mu)) / SR + T_CARD
    duck = np.where(tt < TH, 10 ** (-8 / 20), 1.0)
    k = int(0.06 * SR); duck = np.convolve(duck, np.ones(k) / k, mode='same'); duck[:k] = duck[k]; duck[-k:] = 1.0
    mu *= duck[:, None]; f = int(0.01 * SR); mu[-f:] *= np.linspace(1, 0, f)[:, None]
    a0 = int(T_CARD * SR); m[a0:a0 + len(mu)] += mu
    pk = np.abs(m).max()
    if pk > 0.97: m *= 0.97 / pk
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
