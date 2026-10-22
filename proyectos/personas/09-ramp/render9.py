"""IMG_8913 + IMG_8914 · "¿Cómo hace marketing Ramp?" — Ramp brand look (lime #E4F222 / ink #1A1919), 1.05x.
Full-screen speaker; split screen (speaker top, lime panel with a media card below) whenever a reference image/clip is mentioned.
After "...que está utilizando Ramp." the picture posterizes into a good-work_ style title card ("teoría by andrés corrales_").
No SFX, no color correction (HDR passthrough + SDR copy). Framing locked per take (no per-frame tracking -> no shake)."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit9 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
LIME = (0xE4 / 255, 0xF2 / 255, 0x22 / 255, 1); INK = (0x1A / 255, 0x19 / 255, 0x19 / 255, 1); WHITE = (1, 1, 1, 1)
YEL = (255, 231, 46)                      # good-work_ title yellow
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {29: 'Ramp.', 63: 'es:', 67: 'finance,', 69: 'bien,', 93: 'literalmente', 95: 'cómo', 108: 'tarjetas.', 117: 'marketing,',
       118: 'sí', 120: 'sólo', 152: 'hiperviral,', 164: 'Method:', 186: 'en', 189: 'Instagram.', 190: 'Hacen'}
WORDS = []
for i, w in enumerate(_ws):
    if i in (143, 145): continue
    if i == 141: WORDS.append((w['start'], _ws[142]['end'], 'del')); continue           # "de el seman del accountant" -> del "Indian accountant"
    if i == 142: WORDS.append((_ws[143]['start'], _ws[143]['end'], '"Indian')); continue
    if i == 144: WORDS.append((w['start'], _ws[145]['end'], 'accountant"')); continue
    WORDS.append((w['start'], w['end'], FIX.get(i, w['word'].strip())))
def T(i): return _ws[i]['start']
def Te(i): return _ws[i]['end']

# ---------------- timeline: voice time vt <-> output time t (1 s freeze hold after "explicar.") ----------------
TH = Te(36) + 0.03
T_CARD = T(30) - 0.03
# the card plays the reference's own music bed (good work_, 36.19-40.87 s): the card lasts exactly as long as the track
MUSIC = os.path.join(HERE, 'card_music_full.wav')
with wave.open(MUSIC) as _w: MUSIC_DUR = _w.getnframes() / _w.getframerate()
HOLD = T_CARD + MUSIC_DUR - TH
def vt_of(t): return t if t < TH else (TH if t < TH + HOLD else t - HOLD)
def out_of(vt): return vt if vt < TH else vt + HOLD
TF = min(TH, E.HOOK_END / SPEED - 0.05)          # freeze on the last frame of the hook take (TH can fall past the cut)
def vt_frame(t): return TF if TH <= t < TH + HOLD else vt_of(t)
VTOTAL = E.TOTAL / SPEED
DUR = out_of(VTOTAL) + 0.3

# ---------------- layout schedule (voice time) ----------------
# (start, end, media key)
SPLITS = [(T(5) - 0.05, T(8) - 0.05, 'broadway'), (T(8) - 0.05, T(12) - 0.05, 'contador'), (T(12) - 0.05, Te(16) + 0.35, 'cards'),
          (T(64) - 0.05, T(70) - 0.05, 'fun1'), (T(70) - 0.05, Te(73) + 0.35, 'fun2'),
          (T(87) - 0.05, T(109) - 0.08, 'musical'),
          (T(138) - 0.05, T(150) - 0.05, 'contador2'), (T(150) - 0.05, T(167) - 0.08, 'kumar')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
def in_card(t): return T_CARD <= vt_of(t) and t < TH + HOLD

# ---------------- speaker framing: one locked box per take ----------------
FT = {'a': framing.FaceTrack(os.path.join(HERE, 'faces_8913.txt')), 'b': framing.FaceTrack(os.path.join(HERE, 'faces_8914.txt'))}
def _take_box(s, lo, hi):
    ft = FT[s]; m = (ft.t >= lo) & (ft.t <= hi)
    b = ft.b[m] if m.any() else ft.box((lo + hi) / 2)[None]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 15); chin = np.percentile(b[:, 1] + b[:, 3], 85); h = chin - top
    return (cx - fw / 2, top - 0.12 * h, fw, h * 1.12)
TAKE_BOX = [_take_box(s, a, b) for s, a, b in E.SEGS]
CUTS = sorted({out_of(o / SPEED) for o in E.OFF} | {out_of(a) for a, b, k in SPLITS} | {out_of(b) for a, b, k in SPLITS} | {TH + HOLD})
ZC = [1.0, 1.08, 1.0, 1.14]
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6) if t >= CUTS[0] else 0
    t0 = CUTS[i] if t >= CUTS[0] else 0; base = ZC[i % 4]
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))

# ---------------- media cards (lime panel, Ramp look) ----------------
def _rgb(p): return Image.open(p).convert('RGB')
def _crop(im, box): return im.crop(box)
CARD_MAX = (1000, 860)
def _fit(im, maxw=CARD_MAX[0], maxh=CARD_MAX[1]):
    s = min(maxw / im.width, maxh / im.height); return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
REF = os.path.join(HERE, 'ref')
MEDIA = {
    'broadway': (_fit(_crop(_rgb(os.path.join(REF, 'broadway.png')), (0, 540, 1170, 1580))), 'BROADWAY'),
    'contador': (_fit(_crop(_rgb(os.path.join(REF, 'contador.png')), (0, 330, 1170, 1370))), 'UN CONTADOR INDIO'),
    'cards': (_fit(_rgb(os.path.join(REF, 'ramp_cards.png'))), 'TARJETAS CORPORATIVAS'),
    'fun1': (_fit(_rgb(os.path.join(REF, 'ramp_fun1.jpg'))), 'FINANCE, BUT FUN'),
    'fun2': (_fit(_rgb(os.path.join(REF, 'ramp_fun2.jpg'))), 'FINANCE, BUT FUN'),
    'contador2': (_fit(_crop(_rgb(os.path.join(REF, 'contador.png')), (0, 330, 1170, 1370))), 'KUMAR'),
    'kumar': (_fit(_crop(_rgb(os.path.join(REF, 'kumar.png')), (0, 127, 1170, 1167))), '@THEKUMARMETHOD'),
}
KUMAR_LINK = (36, 690, 526, 614)        # 'ramp.com/thekumarmethod' row in the cropped screenshot (x0, x1, y0, y1, source px)

def card_layer(ctx, img_rgba_surface, cw, ch, label, k_in, t_local, highlight=None):
    """lime panel + rounded media card with a soft shadow + ink label tag (all inside the bottom half)"""
    ctx.save(); ctx.rectangle(0, SEAM, W, H - SEAM); ctx.clip()
    rgba(ctx, LIME); ctx.paint()
    # pixel squares, as in Ramp's own graphics
    for (x, y, s) in [(70, SEAM + 80, 18), (92, SEAM + 58, 14), (980, SEAM + 840, 18), (1004, SEAM + 862, 12), (60, SEAM + 870, 12)]:
        ctx.rectangle(x, y, s, s); rgba(ctx, INK, 0.85); ctx.fill()
    sc = (0.94 + 0.06 * expo_out(k_in)) * (1 + 0.025 * c01(t_local / 6))
    cx, cy = W / 2, SEAM + 480 + 10
    ctx.translate(cx, cy); ctx.scale(sc, sc)
    r = 22; x0, y0 = -cw / 2, -ch / 2
    def rr(x, y, w, h, r):
        ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
    rr(x0 + 6, y0 + 14, cw, ch, r); ctx.set_source_rgba(0, 0, 0, 0.22 * c01(k_in * 2)); ctx.fill()
    rr(x0, y0, cw, ch, r); ctx.save(); ctx.clip()
    ctx.set_source_surface(img_rgba_surface, x0, y0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(c01(k_in * 3))
    ctx.restore()
    if highlight is not None:
        (hx0, hx1, hy0, hy1), hk = highlight
        if hk > 0:
            rr(x0 + hx0, y0 + hy0, (hx1 - hx0) * eo(hk), hy1 - hy0, 14)
            ctx.set_source_rgba(LIME[0], LIME[1], LIME[2], 0.28 * c01(hk * 2)); ctx.fill_preserve()
            rgba(ctx, LIME); ctx.set_line_width(6); ctx.stroke()
    # label tag, top-left of the card
    tt = T_(label, HN, 30, LIME, 0.06, idx=BOLD)
    tw = tt[4] + 36; th = 52; lx, ly = x0 + 24, y0 - th / 2
    rr(lx, ly, tw, th, 10); rgba(ctx, INK, c01(k_in * 3)); ctx.fill()
    put(ctx, tt, lx + 18, ly + th / 2 + 1, alpha=c01(k_in * 3), ax=0)
    ctx.restore()

_surf_cache = {}
def pil_to_surface(img):
    key = id(img)
    if key not in _surf_cache: _surf_cache[key] = fx.pil_surface(img.convert('RGBA'))
    return _surf_cache[key][0]

# ---------------- silent B-roll (Bill Pay: The Musical) ----------------
MUSICAL = DL + 'Twitter Video Downloader (3).mp4'
CLIPS = [(2.0, 3.5), (11.0, 12.6), (14.0, 15.5), (20.0, 21.2), (41.4, 44.0)]   # title card, "Bill Pay!", Billicon Valley, crowd, ramp flag
MW, MH = 1000, 562
def musical_frames(n_needed):
    out = []
    for a, b in CLIPS:
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', MUSICAL, '-an', '-vf',
                            f'fps=30,scale={MW}:{MH}:flags=bicubic,format=rgb24', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
        buf = p.stdout; sz = MW * MH * 3
        out += [Image.frombytes('RGB', (MW, MH), buf[i:i + sz]) for i in range(0, len(buf) - sz + 1, sz)]
    if len(out) < n_needed: out += [out[-1]] * (n_needed - len(out))
    return out
_mus = None

# ---------------- subtitles (Ramp: white bold, active word on a lime block) ----------------
def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) + 1 for x in cur)
        if (len(cur) >= 4 or chars >= 19 or w[2][-1] in '.,?:' or nxt is None or nxt[0] - w[1] > 0.35
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
        parts.append((T_(w, HN, size, INK if active else WHITE, -0.02, shadow=0 if active else 7, idx=BOLD, shadow_a=200, shadow_off=4), active))
    total = sum(p[0][4] for p in parts) + gap * (len(parts) - 1)
    sc = min(1.0, 980 / total); e = expo_out(prog(vt, st, 0.25))
    x = W / 2 - total * sc / 2
    if plate:                           # on the seam: ink plate so white words never sit on the lime panel
        pw, ph = total * sc + 56, size * 1.5 * sc; r = 18; px, py = W / 2 - pw / 2, y + 12 * (1 - e) - ph / 2 - 2
        ctx.new_sub_path(); ctx.arc(px + pw - r, py + r, r, -math.pi / 2, 0); ctx.arc(px + pw - r, py + ph - r, r, 0, math.pi / 2)
        ctx.arc(px + r, py + ph - r, r, math.pi / 2, math.pi); ctx.arc(px + r, py + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
        rgba(ctx, INK, e); ctx.fill()
    for tt, active in parts:
        ww = tt[4] * sc; yy = y + 12 * (1 - e)
        if active:
            ctx.rectangle(x - 12 * sc, yy - size * 0.60 * sc, ww + 24 * sc, size * 1.16 * sc); rgba(ctx, LIME, e); ctx.fill()
        put(ctx, tt, x, yy, scale=sc, alpha=e, ax=0)
        x += ww + gap * sc

# ---------------- @tryramp pill (from "sígalos" to the end) ----------------
T_PILL = T(183) - 0.05
def handle_pill(ctx, t):
    vt = vt_of(t)
    if vt < T_PILL: return
    e = expo_out(prog(vt, T_PILL, 0.5))
    tt = T_('@tryramp', HN, 52, INK, -0.01, idx=BOLD); sub = T_('X  ·  INSTAGRAM', HN, 24, INK, 0.12, idx=BOLD)
    w = tt[4] + 80; h = 112
    ctx.save(); ctx.translate(W / 2, 250 - 30 * (1 - e))
    ctx.new_sub_path(); r = 26
    ctx.arc(w / 2 - r, -h / 2 + r, r, -math.pi / 2, 0); ctx.arc(w / 2 - r, h / 2 - r, r, 0, math.pi / 2)
    ctx.arc(-w / 2 + r, h / 2 - r, r, math.pi / 2, math.pi); ctx.arc(-w / 2 + r, -h / 2 + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
    rgba(ctx, LIME, e); ctx.fill()
    put(ctx, sub, 0, -22, alpha=e); put(ctx, tt, 0, 18, alpha=e)
    ctx.restore()

# ---------------- good-work_ title card ----------------
LABEL = 'teoría by andrés corrales_'
TITLE = ['¿CÓMO HACE', 'MARKETING RAMP?']
def stroked(txt, size, fill, stroke, idx, track=0.0, shadow=True):
    f = ImageFont.truetype(HN, size, index=idx)
    sp = track * size; widths = [f.getlength(ch) + sp for ch in txt]; tw = sum(widths) - sp
    asc, desc = f.getmetrics(); pad = stroke + 24
    w, h = int(tw + 2 * pad), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    def draw(d, col, sw, off=(0, 0)):
        if track == 0:                  # whole string at once: keeps composed accents (í) in place
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
    """good-work_ look: flat cut-out colour (5 levels per channel after a median smooth) -> pinks/pastels, no palette flicker"""
    im = Image.fromarray(rgb8).resize((540, 960), Image.BILINEAR)
    im = ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.45)).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5))
    a = np.asarray(im).astype(np.float32) / 255; L = 5
    q = Image.fromarray((np.round(a * (L - 1)) / (L - 1) * 255).astype(np.uint8)).filter(ImageFilter.ModeFilter(3))
    return np.asarray(q.resize((W, H), Image.BILINEAR))

_lab = stroked(LABEL, 46, YEL, 4, REG)
_tit = [stroked(l, 116, YEL, 7, BOLD, -0.01) for l in TITLE]
def card_text(img, t):
    """typed label with cursor, then the title pops in (as in the reference)"""
    k = t - T_CARD
    if k < 0.15: return
    lab, pad, tw = _lab
    n = min(len(LABEL), int((k - 0.15) / 0.022) + 1)
    x0, y_lab = 60, 1080
    if n < len(LABEL):
        sub = stroked(LABEL[:n] + '_', 46, YEL, 4, REG)
        img.alpha_composite(sub[0], (x0 - sub[1], y_lab - sub[1]))
    else:
        txt = LABEL if int(k * 2.2) % 2 == 0 else LABEL[:-1]
        sub = stroked(txt, 46, YEL, 4, REG); img.alpha_composite(sub[0], (x0 - sub[1], y_lab - sub[1]))
    if k > 0.15 + 0.022 * len(LABEL) + 0.12:
        y = y_lab + 64
        for timg, tpad, ttw in _tit:
            s = min(1.0, 960 / ttw)
            ti = timg if s >= 1 else timg.resize((int(timg.width * s), int(timg.height * s)), Image.LANCZOS)
            img.alpha_composite(ti, (int(x0 - tpad * s), int(y - tpad * s))); y += int(126 * s)

# ---------------- frame ----------------
def speaker(fr16, t, panel, extra=1.0):
    vt = vt_frame(t); te = min(vt * SPEED, E.TOTAL - 0.001); si = E.seg_index(te)
    box = framing.head_crop(TAKE_BOX[si], face_zoom(t) * extra, panel=panel, top_air=0.09)
    return fx.resize_f(fr16, box, panel)

def render_frame(fr16, t):
    global _mus
    vt = vt_of(t)
    sdr = np.zeros((H, W, 3), np.float32)
    if in_card(t):
        full = speaker(fr16, t, (W, H), extra=1 + 0.06 * eio(prog(t, TH, HOLD)))     # slow push-in on the frozen frame
        poster = posterize(fx.to8(full))
        img = Image.fromarray(poster).convert('RGBA'); card_text(img, t)          # output clock: the cursor keeps blinking during the hold
        rgb8 = np.asarray(img.convert('RGB'))
        sdr[:] = rgb8.astype(np.float32) / 255
        return sdr, fx.srgb8_to_hlg(rgb8)
    sp = split_at(vt)
    arr, surf, ctx = fx.new_layer()
    if sp is None:
        sdr[:] = speaker(fr16, t, (W, H)); hdr = sdr.copy()
        subtitles(ctx, t, 1370)
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        k_in = prog(vt, a, 0.35)
        if key == 'musical':
            if _mus is None: _mus = musical_frames(int((b - a) * FPS) + 40)
            img = _mus[min(len(_mus) - 1, int((vt - a) * FPS))]
        else:
            img = MEDIA[key][0]
        label = 'BILL PAY: THE MUSICAL' if key == 'musical' else MEDIA[key][1]
        hl = None
        if key == 'kumar':
            sx = img.width / 1170; hk = prog(vt, T(165) - 0.1, 0.45)
            hl = ((KUMAR_LINK[0] * sx, KUMAR_LINK[1] * sx, KUMAR_LINK[2] * sx, KUMAR_LINK[3] * sx), hk)
        if key == 'musical': msurf, _keep = fx.pil_surface(img.convert('RGBA'))
        else: msurf = pil_to_surface(img)
        card_layer(ctx, msurf, img.width, img.height, label, k_in, vt - a, hl)
        subtitles(ctx, t, SEAM + 2, plate=True)
    handle_pill(ctx, t)
    surf.flush()
    # graphics layer: the bottom lime panel is opaque, composite it like any graphic
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
    # card music: same level relative to the voice as in the reference (music 1.5 LU under the voice -> +3.4 dB here),
    # ducked 8 dB while I'm still talking ("Y hoy te la vengo a explicar"), hard cut at the end like the reference
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
