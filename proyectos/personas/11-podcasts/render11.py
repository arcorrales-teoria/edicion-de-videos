"""IMG_8930 (intro) + IMG_8931 · 3 podcasts: 20VC, My First Million, David Senra. 1.05x, jump cuts, de corrido (no title card).
Intro full screen -> one split screen per podcast/episode as it is mentioned (speaker top, Spotify screenshot card below, podcast pill
on the seam) -> recap with the three covers during the CTA. Subtitles: white Helvetica Neue Bold, active word in the teoría yellow.
Framing locked per take. No SFX, no music. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit11 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {65: '20', 66: 'Minute', 67: 'VC,', 93: 'Wispr Flow,', 139: 'industrias.', 140: 'Estos', 156: 'escúchenlos', 164: 'Senra,',
       191: 'IA,', 203: 'Entonces,'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
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
SPLITS = [(T(64) - 0.05, T(91) - 0.05, '20vc_show'), (T(91) - 0.05, T(94) - 0.05, '20vc_viktor'), (T(94) - 0.05, T(98) - 0.05, '20vc_uber'),
          (T(98) - 0.05, T(110) - 0.05, 'mfm_show'), (T(110) - 0.05, T(140) - 0.05, 'mfm_im8'), (T(140) - 0.05, T(146) - 0.05, 'mfm_instinct'),
          (T(160) - 0.05, T(170) - 0.05, 'senra_show'), (T(170) - 0.05, T(188) - 0.05, 'senra_rahal'), (T(188) - 0.05, T(203) - 0.05, 'senra_leone'),
          (T(203) - 0.05, VTOTAL + 1, 'recap')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = [(T(65) - 0.05, T(98) - 0.05, 'The Twenty Minute VC'), (T(99) - 0.05, T(146) - 0.05, 'My First Million'), (T(163) - 0.05, T(203) - 0.05, 'David Senra')]

# ---------------- speaker framing: one locked box per take ----------------
FT = {'h': framing.FaceTrack(os.path.join(HERE, 'faces_8930.txt')), 'b': framing.FaceTrack(os.path.join(HERE, 'faces_8931.txt'))}
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
def speaker(fr16, t, panel, extra=1.0):
    vt = vt_frame(t); te = min(vt * SPEED, E.TOTAL - 0.001); si = E.seg_index(te)
    box = framing.head_crop(TAKE_BOX[si], face_zoom(t) * extra, panel=panel, top_air=0.09)
    return fx.resize_f(fr16, box, panel)

# ---------------- bottom panel: Spotify screenshot as a rounded card on a dark panel ----------------
REF = os.path.join(HERE, 'ref')
SHOTS = {'20vc_show': 'desk_capture.png', '20vc_viktor': '20vc_viktor.png', '20vc_uber': '20vc_uber.png', 'mfm_show': 'mfm_show.png',
         'mfm_im8': 'mfm_im8.png', 'mfm_instinct': 'mfm_instinct.png', 'senra_show': 'senra_show.png', 'senra_rahal': 'senra_rahal.png',
         'senra_leone': 'senra_leone.png'}
_img = {}
def shot(key):
    if key not in _img:
        im = Image.open(os.path.join(REF, SHOTS[key])).convert('RGB')
        im = im.crop((0, 0, im.width, min(im.height, int(im.width * 0.70))))          # header + buttons + tabs (below the subtitle line)
        s_ = min(1000 / im.width, 700 / im.height)
        im = im.resize((int(im.width * s_), int(im.height * s_)), Image.LANCZOS)
        _img[key] = (im, fx.pil_surface(im.convert('RGBA')))
    return _img[key]

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()

def card(ctx, key, vt, a):
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(0.04, 0.04, 0.045); ctx.fill()
    im, (surf, _buf) = shot(key)
    k = expo_out(prog(vt, a, 0.35)); sc = (0.95 + 0.05 * k) * (1 + 0.03 * c01((vt - a) / 6))
    ctx.save(); ctx.translate(W / 2, SEAM + 520); ctx.scale(sc, sc)
    x0, y0 = -im.width / 2, -im.height / 2
    rr(ctx, x0 + 6, y0 + 14, im.width, im.height, 22); ctx.set_source_rgba(0, 0, 0, 0.5 * k); ctx.fill()
    rr(ctx, x0, y0, im.width, im.height, 22); ctx.save(); ctx.clip()
    ctx.set_source_surface(surf, x0, y0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(c01(k * 3)); ctx.restore()
    rr(ctx, x0, y0, im.width, im.height, 22); ctx.set_source_rgba(1, 1, 1, 0.12 * k); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()

# recap: the three covers (cropped from the screenshots) with name + host
COVERS = [('desk_capture.png', (45, 95, 395, 445), 'The Twenty Minute VC', 'Harry Stebbings'),
          ('mfm_show.png', (39, 127, 390, 478), 'My First Million', 'Sam Parr y Shaan Puri'),
          ('senra_show.png', (31, 107, 382, 458), 'David Senra', 'Founders')]
_cov = []
def recap(ctx, vt, a):
    if not _cov:
        for f, box, n, h in COVERS:
            im = Image.open(os.path.join(REF, f)).convert('RGB').crop(box).resize((124, 124), Image.LANCZOS)
            _cov.append(fx.pil_surface(im.convert('RGBA')))
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(0.04, 0.04, 0.045); ctx.fill()
    put(ctx, T_('LOS 3 PODCASTS', HN, 30, YELF, 0.16, idx=BOLD), 90, SEAM + 190, alpha=c01((vt - a) / 0.3), ax=0)
    for k, ((f, box, name, host), (surf, _b)) in enumerate(zip(COVERS, _cov)):
        e = expo_out(prog(vt, a + 0.2 + 0.25 * k, 0.5))
        if e <= 0: continue
        y = SEAM + 300 + k * 160; x = 90 + 30 * (1 - e)
        ctx.save(); rr(ctx, x, y - 62, 124, 124, 14); ctx.clip(); ctx.set_source_surface(surf, x, y - 62); ctx.paint_with_alpha(e); ctx.restore()
        ctx.arc(x + 118, y - 56, 24, 0, 2 * math.pi); rgba(ctx, YELF, e); ctx.fill()
        put(ctx, T_(str(k + 1), HN, 30, (0.05, 0.05, 0.05, 1), 0, idx=BOLD), x + 118, y - 55, alpha=e)
        put(ctx, T_(name, HN, 56, WHITE, -0.02, idx=BOLD), x + 160, y - 16, alpha=e, ax=0)
        put(ctx, T_(host, HN, 36, GREY, 0, idx=REG), x + 160, y + 34, alpha=e, ax=0)

# ---------------- intro collage: "...tres recomendaciones de podcast" -> pieces pop in one by one, then leave ----------------
# (cover art / episode art cropped from the Spotify screenshots; plain rectangles like the reference reel, soft shadow only)
PIECES = [  # file, crop box, (x, y, width) in the 1080x1920 frame
    ('desk_capture.png', (45, 95, 395, 445), (20, 60, 300)),          # 20VC
    ('20vc_viktor.png', (41, 105, 400, 463), (770, 30, 290)),          # 20VC · Wispr Flow / Superhuman
    ('mfm_show.png', (39, 127, 390, 478), (-40, 600, 280)),            # My First Million
    ('20vc_uber.png', (37, 125, 388, 476), (830, 520, 270)),           # 20VC · Uber
    ('senra_show.png', (31, 107, 382, 458), (20, 1130, 270)),          # David Senra
    ('mfm_im8.png', (0, 0, 1480, 430), (560, 1210, 500)),              # MFM · $100M in under a year
    ('senra_rahal.png', (11, 69, 362, 420), (40, 1470, 270)),          # Senra · Peter Rahal
    ('mfm_instinct.png', (0, 0, 1560, 460), (350, 1490, 480)),         # MFM · Instinct, MUSE, Grokbot
    ('senra_leone.png', (5, 97, 363, 455), (820, 1450, 240)),          # Senra · Doug Leone
]
_pieces = []
def _load_pieces():
    from PIL import ImageFilter as _IF
    for f, box, (x, y, w) in PIECES:
        im = Image.open(os.path.join(REF, f)).convert('RGB').crop(box)
        h = int(w * im.height / im.width); im = im.resize((w, h), Image.LANCZOS)
        pad = 24; sh = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        blk = Image.new('RGBA', (w, h), (0, 0, 0, 120)); sh.paste(blk, (pad + 4, pad + 8)); sh = sh.filter(_IF.GaussianBlur(10))
        sh.alpha_composite(im.convert('RGBA'), (pad, pad))
        _pieces.append((fx.pil_surface(sh), x - pad, y - pad, w + 2 * pad, h + 2 * pad))
T_COLL_IN, COLL_STEP = T(33) - 0.02, 0.24          # "con tres recomendaciones de podcast ..."
T_COLL_OUT = T(43) - 0.08                           # gone by "para tener mucho más contexto"
def collage(ctx, vt):
    if vt < T_COLL_IN or vt > T_COLL_OUT + 0.6: return
    if not _pieces: _load_pieces()
    n = len(_pieces)
    for k, ((surf, _b), x, y, w, h) in enumerate(_pieces):
        t_in = T_COLL_IN + k * COLL_STEP; t_out = T_COLL_OUT + (n - 1 - k) * 0.04
        if vt < t_in or vt > t_out + 0.12: continue
        a = c01((vt - t_in) / 0.06) * (1 - c01((vt - t_out) / 0.12))
        sc = (1 + 0.10 * (1 - eo(prog(vt, t_in, 0.16)))) * (1 - 0.12 * c01((vt - t_out) / 0.12))
        ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(sc, sc)
        ctx.set_source_surface(surf, -w / 2, -h / 2); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a)
        ctx.restore()

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
    gx = -w / 2 + 50                                                     # podcast glyph: dot + two arcs
    ctx.arc(gx, 0, 5, 0, 2 * math.pi); ctx.set_source_rgba(YELF[0], YELF[1], YELF[2], e); ctx.fill()
    for rad in (11, 18):
        ctx.new_sub_path(); ctx.arc(gx, 0, rad, -math.pi * 0.3, math.pi * 0.3); ctx.new_sub_path(); ctx.arc(gx, 0, rad, math.pi * 0.7, math.pi * 1.3)
    ctx.set_source_rgba(YELF[0], YELF[1], YELF[2], e); ctx.set_line_width(2.8); ctx.stroke()
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
        collage(ctx, vt)
        subtitles(ctx, t, 1370, plate=T_COLL_IN <= vt <= T_COLL_OUT + 0.5)
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        if key == 'recap': recap(ctx, vt, a)
        else: card(ctx, key, vt, a)
        pill(ctx, vt)
        subtitles(ctx, t, 1065 if key != 'recap' else 1045, plate=True)
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
