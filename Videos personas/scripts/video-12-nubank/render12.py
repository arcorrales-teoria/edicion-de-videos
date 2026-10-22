"""IMG_8938 · "El mejor artículo que leerás esta semana" — Colossus feature on David Vélez / Nubank ("Coming to America"). 1.05x.
5 s title on a live full-screen shot (teoría label typed + yellow outlined title) -> split screens with a Colossus-like editorial
panel (off-white, New York serif, Nubank purple) for the article, the photos and a few subtle data beats taken from the article
-> founder chips -> Doug Leone quote -> link pill. Subtitles: white Helvetica Neue Bold, active word in the teoría yellow.
Framing locked per take. No SFX, no music. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit12 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {9: 'suelte', 13: 'léase', 36: 'Nubank,', 43: 'Brasil,', 50: 'Colombia,', 60: 'de', 61: 'Rappi,', 87: 'scrollear.',
       92: 'léanse'}
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
SPLITS = [(TITLE_END, T(25) - 0.05, 'header'), (T(25) - 0.05, T(37) - 0.05, 'portrait'),
          (T(37) - 0.05, T(44) - 0.05, 'stat_br'), (T(44) - 0.05, T(51) - 0.05, 'stat_co'), (T(51) - 0.05, T(55) - 0.05, 'stat_reg'),
          (T(73) - 0.05, T(79) - 0.05, 'quote'), (T(79) - 0.05, T(95) - 0.05, 'header2')]
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = [(T(79) + 0.3, T(95) - 0.05, 'colossus.com · Coming to America')]

# ---------------- speaker framing: one locked box per take ----------------
FT = {'a': framing.FaceTrack(os.path.join(HERE, 'faces_8938.txt'))}
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

# ---------------- Colossus-like editorial panel ----------------
REF = os.path.join(HERE, 'ref')
PAPER = (0.969, 0.969, 0.961); INKC = (0.07, 0.07, 0.07, 1); MUT = (0.42, 0.42, 0.42, 1); PURPLE = (0x82 / 255, 0x0A / 255, 0xD1 / 255, 1)
NY, NYI = '/System/Library/Fonts/NewYork.ttf', '/System/Library/Fonts/NewYorkItalic.ttf'
_sc = {}
def S_(txt, size, col=INKC, var='Semibold', font=NY):
    """serif text (New York variable font) -> cairo text tuple usable by put()"""
    key = (txt, size, col, var, font)
    if key in _sc: return _sc[key]
    f = ImageFont.truetype(font, size); f.set_variation_by_name(var)
    asc, desc = f.getmetrics(); tw = max(1, f.getlength(txt)); pad = 10 + int(size * 0.25)
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=tuple(int(c * 255) for c in col[:3]) + (255,))
    surf, buf = fx.pil_surface(img); r = (surf, buf, w, h, tw, asc); _sc[key] = r; return r

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()

_ph = {}
def photo(key):
    """full-bleed photos for the bottom half (crop box picked per image, source px)"""
    if key not in _ph:
        f, box = {'header': ('article_header.png', (279, 0, 1721, 1282)),
                  'header2': ('article_header.png', (279, 0, 1721, 1282)),
                  'portrait': ('NUBANK-COLOSSUS-MAG0051-scaled.jpg', (0, 230, 2048, 2050)),
                  'quote': ('NUBANK-COLOSSUS-MAG0115-2-scaled.jpg', (0, 260, 1707, 1777))}[key]
        _ph[key] = (Image.open(os.path.join(REF, f)).convert('RGB'), box)
    return _ph[key]
def kenburns(key, vt, a, b, z1=1.06):
    im, (x0, y0, x1, y1) = photo(key)
    k = eio(c01((vt - a) / max(b - a, 0.1))); z = 1 + (z1 - 1) * k
    cw, ch = (x1 - x0) / z, (y1 - y0) / z; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - (y1 - y0) * 0.04 * k
    bx0 = min(max(cx - cw / 2, 0), im.width - cw); by0 = min(max(cy - ch / 2, 0), im.height - ch)
    return np.asarray(im.resize((W, SEAM), Image.BICUBIC, box=(bx0, by0, bx0 + cw, by0 + ch)))

_hd = {}
def header_panel(vt, a, b, key):
    """the article as it appears on colossus.com: headline + dek + byline in serif on paper, the opening photo below (slow push-in)"""
    if key not in _hd:
        base = Image.new('RGB', (W, SEAM), tuple(int(c * 255) for c in PAPER)); d = ImageDraw.Draw(base)
        def f(size, var, font=NY):
            ft = ImageFont.truetype(font, size); ft.set_variation_by_name(var); return ft
        hl = f(86, 'Semibold'); d.text(((W - d.textlength('Coming to America', font=hl)) / 2, 150), 'Coming to America', font=hl, fill=(18, 18, 18))
        dk = ImageFont.truetype(HN, 27, index=REG)
        for j, line in enumerate(['After facing down regulators, oligopolies, and corruption in Latin',
                                  'America, Nubank founder David Vélez faces his biggest challenge yet']):
            d.text(((W - d.textlength(line, font=dk)) / 2, 262 + j * 36), line, font=dk, fill=(60, 60, 60))
        by = f(26, 'Semibold'); txt = 'By Gabi Marques  ·  Colossus  ·  32 min'
        d.text(((W - d.textlength(txt, font=by)) / 2, 344), txt, font=by, fill=(70, 70, 70))
        _hd[key] = (base, Image.open(os.path.join(REF, 'article_header.png')).convert('RGB'))
    base, src = _hd[key]
    img = base.copy()
    k = eio(c01((vt - a) / max(b - a, 0.1))); z = 1 + 0.06 * k
    x0, y0, x1, y1 = 140, 330, 1860, 1282                                  # opening photo (David + the nu logo)
    pw, ph = W, SEAM - 400
    cw = (x1 - x0) / z; ch = cw * ph / pw; cx = (x0 + x1) / 2; cy = (y0 + y1) / 2 + 30
    by0 = min(max(y0, cy - ch / 2), y1 - ch); box = (cx - cw / 2, by0, cx + cw / 2, by0 + ch)
    img.paste(src.resize((pw, ph), Image.BICUBIC, box=box), (0, 400))
    return np.asarray(img)

def paper(ctx):
    ctx.rectangle(0, SEAM, W, H - SEAM); ctx.set_source_rgb(*PAPER); ctx.fill()
    ctx.rectangle(90, SEAM + 150, W - 180, 2); ctx.set_source_rgba(0, 0, 0, 0.12); ctx.fill()

def kicker(ctx, txt, y, e):
    put(ctx, T_(txt, HN, 26, MUT, 0.18, idx=BOLD), 90, y, alpha=e, ax=0)

def stat(ctx, vt, a, kick, big, big_val, caption, foot):
    """kicker / big purple serif figure (counts up) / caption / thin bar / source"""
    paper(ctx); e = expo_out(prog(vt, a, 0.45))
    kicker(ctx, kick, SEAM + 205, e)
    k = eo(prog(vt, a + 0.1, 0.9))
    txt = big(k) if callable(big) else big
    put(ctx, S_(txt, 190, PURPLE, 'Bold'), 82, SEAM + 360 + 20 * (1 - e), alpha=e, ax=0)
    for j, line in enumerate(caption):
        put(ctx, S_(line, 50, INKC, 'Medium'), 90, SEAM + 520 + j * 64 + 14 * (1 - e), alpha=c01((vt - a - 0.15 - 0.1 * j) / 0.3), ax=0)
    if big_val is not None:                                                # thin progress bar under the figure
        ctx.rectangle(90, SEAM + 700, W - 180, 10); ctx.set_source_rgba(0, 0, 0, 0.08 * e); ctx.fill()
        ctx.rectangle(90, SEAM + 700, (W - 180) * big_val * k, 10); rgba(ctx, PURPLE, e); ctx.fill()
    put(ctx, T_(foot, HN, 24, MUT, 0.02, idx=REG), 90, SEAM + 760, alpha=c01((vt - a - 0.4) / 0.3), ax=0)

def stat_reg(ctx, vt, a):
    paper(ctx); e = expo_out(prog(vt, a, 0.45))
    kicker(ctx, 'BANCO CENTRAL DE BRASIL · DIC 2016', SEAM + 205, e)
    put(ctx, S_('30 días', 150, INKC, 'Bold'), 90, SEAM + 345, alpha=e, ax=0)
    k = eo(prog(vt, a + 0.35, 0.5))                                        # arrow draws, then "2 días" lands in purple
    x0 = 90 + S_('30 días', 150, INKC, 'Bold')[4] + 30
    ctx.move_to(x0, SEAM + 340); ctx.line_to(x0 + 110 * k, SEAM + 340); rgba(ctx, INKC, e); ctx.set_line_width(8); ctx.stroke()
    if k > 0.6:
        ctx.move_to(x0 + 110, SEAM + 340); ctx.line_to(x0 + 84, SEAM + 318); ctx.move_to(x0 + 110, SEAM + 340); ctx.line_to(x0 + 84, SEAM + 362); ctx.stroke()
    put(ctx, S_('2', 150, PURPLE, 'Bold'), x0 + 140, SEAM + 345 + 16 * (1 - eo(prog(vt, a + 0.75, 0.3))), alpha=c01((vt - a - 0.75) / 0.2), ax=0)
    for j, line in enumerate(['El plazo para pagarle a los comercios.', 'Casi quiebra a Nubank: sus clientes', 'lo frenaron en 4 días.']):
        put(ctx, S_(line, 46, INKC, 'Medium'), 90, SEAM + 500 + j * 60, alpha=c01((vt - a - 0.25 - 0.1 * j) / 0.3), ax=0)
    put(ctx, T_('Fuente: Colossus, "Coming to America"', HN, 24, MUT, 0.02, idx=REG), 90, SEAM + 760, alpha=c01((vt - a - 0.5) / 0.3), ax=0)

QUOTE = ['“He has vision. He executes.', 'He’s tough as nails.”']
def quote(ctx, vt, a, bottom):
    """photo of David with a paper quote card from Doug Leone"""
    e = expo_out(prog(vt, a + 0.2, 0.5))
    cw, chh = 900, 300; x0 = (W - cw) / 2; y0 = SEAM + 600 + 30 * (1 - e)
    rr(ctx, x0, y0, cw, chh, 18); ctx.set_source_rgba(PAPER[0], PAPER[1], PAPER[2], 0.96 * e); ctx.fill()
    ctx.rectangle(x0 + 40, y0 + 46, 6, 150); rgba(ctx, PURPLE, e); ctx.fill()
    for j, line in enumerate(QUOTE):
        put(ctx, S_(line, 52, INKC, 'Medium Italic', NYI), x0 + 72, y0 + 80 + j * 66, alpha=e, ax=0)
    put(ctx, T_('DOUG LEONE · SEQUOIA CAPITAL', HN, 24, MUT, 0.16, idx=BOLD), x0 + 72, y0 + 236, alpha=e, ax=0)

def caption_tag(ctx, vt, a, title, sub):
    """lower-third on a photo: name + role on a paper tag"""
    e = expo_out(prog(vt, a + 0.25, 0.5))
    t1 = S_(title, 54, INKC, 'Bold'); t2 = T_(sub, HN, 26, MUT, 0.14, idx=BOLD)
    w = max(t1[4], t2[4]) + 70; x0 = 70 - 30 * (1 - e); y0 = H - 470
    rr(ctx, x0, y0, w, 132, 14); ctx.set_source_rgba(PAPER[0], PAPER[1], PAPER[2], 0.96 * e); ctx.fill()
    ctx.rectangle(x0, y0, 8, 132); rgba(ctx, PURPLE, e); ctx.fill()
    put(ctx, t1, x0 + 34, y0 + 48, alpha=e, ax=0); put(ctx, t2, x0 + 34, y0 + 100, alpha=e, ax=0)

# ---------------- founders (full screen): two quiet chips as the names are said ----------------
def founders(ctx, vt):
    if not (T(56) - 0.05 <= vt < T(73) - 0.05): return
    for j, (tk, name, co) in enumerate([(56, 'David Vélez', 'NUBANK'), (59, 'Simón Borrero', 'RAPPI')]):
        e = expo_out(prog(vt, T(tk) - 0.05, 0.45)) * (1 - c01((vt - (T(73) - 0.3)) / 0.25))
        if e <= 0: continue
        t1 = S_(name, 48, INKC, 'Bold'); t2 = T_(co, HN, 24, PURPLE, 0.18, idx=BOLD)
        w = max(t1[4], t2[4]) + 64; x0 = 60 if j == 0 else W - 60 - w; y0 = 1120 + 18 * (1 - e)
        rr(ctx, x0, y0, w, 112, 16); ctx.set_source_rgba(PAPER[0], PAPER[1], PAPER[2], 0.94 * e); ctx.fill()
        put(ctx, t1, x0 + 32, y0 + 42, alpha=e, ax=0); put(ctx, t2, x0 + 32, y0 + 84, alpha=e, ax=0)

# ---------------- website pill on the seam ----------------
def pill(ctx, vt):
    for a, b, txt in PILLS:
        if a <= vt < b: break
    else: return
    e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - (b - 0.15)) / 0.15))
    tt = T_(txt, HN, 44, INKC, -0.01, idx=BOLD)
    w = tt[4] + 110; h = 86
    ctx.save(); ctx.translate(W / 2, SEAM + 22 * (1 - e))
    ctx.new_sub_path(); r = h / 2
    ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(PAPER[0], PAPER[1], PAPER[2], 0.97 * e); ctx.fill()
    ctx.arc(-w / 2 + 46, 0, 9, 0, 2 * math.pi); rgba(ctx, PURPLE, e); ctx.fill()
    put(ctx, tt, -w / 2 + 72, 2, alpha=e, ax=0)
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

TITLE = ['EL MEJOR ARTÍCULO', 'QUE LEERÁS', 'ESTA SEMANA']
_tit = [stroked(l, 120, YEL, 7, BOLD, -0.01) for l in TITLE]
def title_layer(t):
    if t >= TITLE_END: return None
    k = t - 0.1
    if k < 0: return None
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fade = 1 - c01((t - (TITLE_END - 0.3)) / 0.3)
    n = min(len(LABEL), int(k / 0.022) + 1)
    txt = LABEL[:n] + '_' if n < len(LABEL) else (LABEL if int(k * 2.2) % 2 == 0 else LABEL[:-1])
    x0, y_lab = 60, 1130
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
        founders(ctx, vt)
        if t >= TITLE_END: subtitles(ctx, t, 1370)
    else:
        a, b, key = sp
        sdr[:SEAM] = speaker(fr16, t, (W, SEAM)); hdr = sdr.copy()
        if key in ('header', 'header2'):
            bottom = header_panel(vt, a, b, key)
            sdr[SEAM:] = bottom.astype(np.float32) / 255; hdr[SEAM:] = fx.srgb8_to_hlg(bottom)
        elif key in ('portrait', 'quote'):
            bottom = kenburns(key, vt, a, b)
            sdr[SEAM:] = bottom.astype(np.float32) / 255; hdr[SEAM:] = fx.srgb8_to_hlg(bottom)
            if key == 'portrait': caption_tag(ctx, vt, a, 'David Vélez', 'FUNDADOR Y CEO DE NUBANK')
            if key == 'quote': quote(ctx, vt, a, bottom)
        elif key == 'stat_br':
            stat(ctx, vt, a, 'BRASIL · 2013', lambda k: '%d%%' % round(90 * k), 0.90,
                 ['del mercado lo controlaban', '5 bancos. Nubank fue contra ellos.'], 'Fuente: Colossus, "Coming to America"')
        elif key == 'stat_co':
            stat(ctx, vt, a, 'COLOMBIA', lambda k: '%d.ª' % max(4, round(12 - 8 * k)), None,
                 ['institución financiera del país', 'por depósitos, en menos de 6 años.'], 'Fuente: Colossus, "Coming to America"')
        elif key == 'stat_reg':
            stat_reg(ctx, vt, a)
        pill(ctx, vt)
        subtitles(ctx, t, 1065, plate=True)
    surf.flush()
    fx.layer_over(sdr, hdr, arr)
    ti = title_layer(t)
    if ti is not None:                                                     # PIL layer for the outlined title
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
