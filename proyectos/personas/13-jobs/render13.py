"""IMG_8946 · "Toda tu búsqueda de trabajo en un solo lugar" — job-status. 1.05x.
5 s title (teoría label typed + yellow outlined lines); "LinkedIn, el correo… una locura" -> LinkedIn + Gmail screenshots pile up
below (Gmail with personal data blurred); then each job-status feature from the screen recording, synced to what I say
(window cropped, letterboxed on black); "el correo es lleno de spam… se pierden los procesos" -> the inbox again, fading out;
CTA full screen. Subtitles: white Helvetica Neue Bold, active word in the teoría yellow. Framing locked per take. Voice only."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit13 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {24: 'Esta', 74: 'trackeando', 96: 'da', 124: 'vaina', 125: 'game', 126: 'changer,', 166: 'escríbanme,', 171: 'quieran'}
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
TITLE_END = 5.0
SPLITS = [(T(10) - 0.05, T(24) - 0.05, 'chaos'),
          (T(24) - 0.05, T(39) - 0.05, 'js_hero'), (T(39) - 0.05, T(50) - 0.05, 'js_connect'), (T(50) - 0.05, T(79) - 0.05, 'js_stages'),
          (T(79) - 0.05, T(95) - 0.05, 'js_follow'), (T(95) - 0.05, T(121) - 0.05, 'js_map'), (T(121) - 0.05, T(135) - 0.05, 'js_view'),
          (T(135) - 0.05, T(161) - 0.05, 'inbox')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = [(T(25) - 0.05, T(135) - 0.05, 'job-status')]

# ---------------- speaker framing: one locked box per take ----------------
FT = {'a': framing.FaceTrack(os.path.join(HERE, 'faces_8946.txt'))}
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

# ---------------- bottom panels ----------------
REF = os.path.join(HERE, 'ref')
REC = DL + 'video_jobstatus.mp4'
WIN = 'crop=1290:880:180:115,scale=1080:737:flags=bicubic,pad=1080:960:0:150:0x0A0A0A'   # site window only, letterboxed on black
CLIPS = {'js_hero': [(0.3, 4.6)], 'js_connect': [(19.0, 21.4)], 'js_stages': [(15.0, 18.8), (5.0, 8.5)],
         'js_follow': [(23.5, 29.5)], 'js_map': [(9.0, 12.5), (32.0, 34.0)], 'js_view': [(30.0, 31.9), (37.0, 38.6)]}
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

def chaos(ctx, vt, a):
    """'LinkedIn' -> LinkedIn jobs list; 'el correo' -> Gmail inbox on top; 'todo es una locura' -> unread badges pop"""
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(0.04, 0.04, 0.045); ctx.fill()
    card(ctx, 'linkedin_jobs.png', 600, 360, SEAM + 520, -4, expo_out(prog(vt, T(10) - 0.05, 0.4)), crop_h=760)
    card(ctx, 'gmail_blur.png', 900, 600, SEAM + 600, 3, expo_out(prog(vt, T(11) - 0.05, 0.4)), crop_h=560)
    badge(ctx, 615, SEAM + 170, '+113', prog(vt, T(16) - 0.05, 0.25))
    badge(ctx, 1000, SEAM + 300, '+50', prog(vt, T(17) - 0.05, 0.25))
    badge(ctx, 110, SEAM + 260, '24', prog(vt, T(18), 0.25))

def inbox(ctx, vt, a, b):
    """'todo está muy disperso' -> both screenshots; 'el correo… spam' -> inbox scrolls; 'se pierden' -> everything fades and blurs"""
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(0.04, 0.04, 0.045); ctx.fill()
    out = c01((vt - (T(157) - 0.05)) / 0.9)                                # "se pierden todos estos procesos"
    card(ctx, 'linkedin_jobs.png', 560, 300, SEAM + 520, -5, expo_out(prog(vt, a, 0.4)) * (1 - out), crop_h=720)
    card(ctx, 'gmail_blur.png', 1000, 560, SEAM + 560, 2, expo_out(prog(vt, T(142) - 0.05, 0.4)) * (1 - out), crop_h=620,
         scroll=eio(prog(vt, T(143), 3.5)), blur=out)

# ---------------- website pill on the seam ----------------
def pill(ctx, vt):
    for a, b, txt in PILLS:
        if a <= vt < b: break
    else: return
    e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - (b - 0.15)) / 0.15))
    tt = T_(txt, HN, 46, WHITE, -0.01, idx=BOLD); sub = T_('GRATIS EN BETA', HN, 22, (0.55, 0.85, 0.6, 1), 0.14, idx=BOLD)
    w = tt[4] + sub[4] + 150; h = 86
    ctx.save(); ctx.translate(W / 2, SEAM + 22 * (1 - e))
    ctx.new_sub_path(); r = h / 2
    ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(0.05, 0.05, 0.05, 0.92 * e); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 0.25 * e); ctx.set_line_width(2); ctx.stroke()
    for k, hh in enumerate((14, 24, 18)):                                   # little bar-chart glyph, like the job-status logo
        ctx.rectangle(-w / 2 + 34 + k * 9, 12 - hh, 6, hh); ctx.set_source_rgba(1, 1, 1, e); ctx.fill()
    put(ctx, tt, -w / 2 + 76, 2, alpha=e, ax=0)
    ctx.arc(-w / 2 + 92 + tt[4], 0, 6, 0, 2 * math.pi); ctx.set_source_rgba(0.3, 0.85, 0.45, e); ctx.fill()
    put(ctx, sub, -w / 2 + 108 + tt[4], 2, alpha=e, ax=0)
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

TITLE = ['TODA TU BÚSQUEDA', 'DE TRABAJO EN', 'UN SOLO LUGAR']
_tit = [stroked(l, 120, YEL, 7, BOLD, -0.01) for l in TITLE]
def title_layer(t):
    if t >= TITLE_END: return None
    k = t - 0.1
    if k < 0: return None
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fade = 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    n = min(len(LABEL), int(k / 0.022) + 1)
    txt = LABEL[:n] + '_' if n < len(LABEL) else (LABEL if int(k * 2.2) % 2 == 0 else LABEL[:-1])
    x0, y_lab = 60, 830                                                    # on the seam (the screenshots pile up below)
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
        if t >= TITLE_END: subtitles(ctx, t, 1370, plate=True)      # gray hoodie: white words need the plate
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        if key.startswith('js_'):
            bottom = rec_frame(key, vt, a, b)
            sdr[SEAM:] = bottom.astype(np.float32) / 255; hdr[SEAM:] = fx.srgb8_to_hlg(bottom)
        elif key == 'chaos': chaos(ctx, vt, a)
        elif key == 'inbox': inbox(ctx, vt, a, b)
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
