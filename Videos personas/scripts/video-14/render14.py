"""IMG_8956 · "La técnica para que tu plan de $20 de Claude no se acabe" — bait-and-switch joke ("…dígame, porque yo tampoco
tengo ni idea"). No extra material, so the graphics carry the story: usage card -> empty "la técnica" note -> prompt + Opus 5.5
chip -> usage bar shoots to 100% (limit reached) -> punch-in + "NI IDEA" stamp + comment CTA. 1.05x, voice only (no SFX/music).
Generic dark UI cards with a terracotta accent (no logos). Framing locked per take. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import fx, framing
from fx import np, Image, cairo, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
from PIL import ImageFont, ImageDraw, ImageFilter, ImageEnhance
_cwd = os.getcwd(); os.chdir(HERE); import edit14 as E; os.chdir(_cwd)

DL = '/Users/acorrales/Downloads/'
SPEED = 1.05
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD, REG = 1, 0
YEL = (255, 231, 46); YELF = (1.0, 231 / 255, 46 / 255, 1); WHITE = (1, 1, 1, 1); GREY = (0.62, 0.62, 0.66, 1)
SEAM = 960

# ---------------- words (voice time, transcribed from the 1.05x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {1: '¿Se', 18: 'Claude', 21: 'dólares', 53: 'Claude', 67: '5.5', 72: 'Pues', 79: 'idea.'}
WORDS = [(w['start'], w['end'], FIX.get(i, w['word'].strip())) for i, w in enumerate(_ws)]
WORDS = [(a, b, '5.5') if w == '5.5' else (a, b, w) for a, b, w in WORDS if w != '5']   # "5" + ".5" -> one word
def T(i): return _ws[i]['start']
def Te(i): return _ws[i]['end']

# ---------------- timeline: no title card, no holds -> voice time == output time ----------------
TH, HOLD, T_CARD = 1e9, 0.0, 1e9
def vt_of(t): return t
def out_of(vt): return vt
def vt_frame(t): return t
VTOTAL = E.TOTAL / SPEED
DUR = VTOTAL + 1.4                                     # 1.1 s silent reaction after "ni idea" for the CTA
def in_card(t): return False

# ---------------- layout (voice time) ----------------
TITLE_END = 5.0
SPLITS = []
def split_at(vt):
    for a, b, k in SPLITS:
        if a <= vt < b: return a, b, k
    return None
PILLS = []

# ---------------- speaker framing: one locked box per take ----------------
FT = {'a': framing.FaceTrack(os.path.join(HERE, 'faces_8956.txt'))}
def _take_box(s, lo, hi):
    ft = FT[s]; m = (ft.t >= lo) & (ft.t <= hi)
    b = ft.b[m] if m.any() else ft.box((lo + hi) / 2)[None]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 5); chin = np.percentile(b[:, 1] + b[:, 3], 92); h = chin - top   # I lean in a lot in this take
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

# ---------------- graphics (all on the chest area, between the face and the subtitles) ----------------
ACC = (0xD9 / 255, 0x77 / 255, 0x57 / 255, 1)            # terracotta accent
CARD = (0.11, 0.105, 0.10); LINE = (1, 1, 1, 0.10); MUT = (0.62, 0.60, 0.58, 1); RED = (0.93, 0.27, 0.22, 1)
MENLO = '/System/Library/Fonts/Menlo.ttc'
CX, CY, CW, CH = W / 2, 1180, 860, 250                  # main card slot

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()

def panel(ctx, x, y, w, h, e, scale=1.0):
    ctx.save(); ctx.translate(x + w / 2, y + h / 2 + 24 * (1 - e)); s_ = (0.94 + 0.06 * e) * scale; ctx.scale(s_, s_); ctx.translate(-w / 2, -h / 2)
    rr(ctx, 6, 14, w, h, 24); ctx.set_source_rgba(0, 0, 0, 0.35 * e); ctx.fill()
    rr(ctx, 0, 0, w, h, 24); ctx.set_source_rgba(CARD[0], CARD[1], CARD[2], 0.94 * e); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.10 * e); ctx.set_line_width(2); ctx.stroke()
    return ctx                                               # caller draws in local coords, then ctx.restore()

def usage_card(ctx, vt):
    """'la sesión de Claude de 20 dólares… que le dure todo el tiempo' -> plan card with a usage bar creeping up;
    'con un prompt… haciendo cualquier cosa' -> bar shoots to 100%, turns red: limit reached"""
    a, b = TITLE_END, T(34) - 0.1
    a2, b2 = T(61) - 0.05, T(72) - 0.05
    if a <= vt < b + 0.25: e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - b) / 0.25)); phase = 1
    elif a2 <= vt < b2 + 0.25: e = expo_out(prog(vt, a2, 0.45)) * (1 - c01((vt - b2) / 0.25)); phase = 2
    else: return
    if e <= 0: return
    x0, y0 = CX - CW / 2, CY - CH / 2
    panel(ctx, x0, y0, CW, CH, e)
    put(ctx, T_('PLAN PRO · $20/MES', HN, 26, MUT, 0.14, idx=BOLD), 44, 52, alpha=e, ax=0)
    if phase == 1:
        u = 0.38 + 0.10 * c01((vt - a) / 3.0)
        if vt >= T(28) - 0.05:                                # "todo el tiempo y todo momento" -> infinity tag
            k = eo(prog(vt, T(28) - 0.05, 0.3)); tg = T_('∞  SIN LÍMITE', HN, 28, (0.06, 0.06, 0.06, 1), 0.08, idx=BOLD)
            rr(ctx, CW - 44 - tg[4] - 36, 30, tg[4] + 36, 46, 23); rgba(ctx, ACC, e * k); ctx.fill()
            put(ctx, tg, CW - 44 - tg[4] - 18, 54, alpha=e * k, ax=0)
    else:
        t_boom = T(69) - 0.05                                 # "haciendo cualquier cosa"
        u = 0.12 + 0.06 * c01((vt - a2) / 2.0) + 0.82 * eio(prog(vt, t_boom, 0.7))
    full = u >= 0.995
    put(ctx, T_('Uso de la sesión', HN, 44, WHITE, -0.01, idx=BOLD), 44, 112, alpha=e, ax=0)
    pct = T_('%d%%' % round(u * 100), HN, 44, RED if full else WHITE, 0, idx=BOLD)
    put(ctx, pct, CW - 44, 112, alpha=e, ax=1)
    rr(ctx, 44, 152, CW - 88, 22, 11); ctx.set_source_rgba(1, 1, 1, 0.10 * e); ctx.fill()
    rr(ctx, 44, 152, max(22, (CW - 88) * u), 22, 11); rgba(ctx, RED if full else ACC, e); ctx.fill()
    if full:
        k = eo(prog(vt, T(69) + 0.65, 0.3))
        put(ctx, T_('Límite alcanzado · se reinicia en 5 h', HN, 30, RED, 0, idx=BOLD), 44, 212, alpha=e * k, ax=0)
    else:
        put(ctx, T_('Se reinicia en 5 h', HN, 28, MUT, 0, idx=REG), 44, 212, alpha=e, ax=0)
    ctx.restore()

def technique_note(ctx, vt):
    """'Aquí se la voy a dar' -> a note 'La técnica:' with three empty numbered lines and a blinking cursor (sets up the joke);
    it stays while I repeat the setup; on 'pues dígame' it comes back and the lines fill with '???'"""
    spans = [(T(34) - 0.1, T(61) - 0.05, False), (T(72) - 0.05, VTOTAL + 1.6, True)]
    for a, b, punch in spans:
        if a <= vt < b + 0.25: break
    else: return
    e = expo_out(prog(vt, a, 0.45)) * (1 - c01((vt - b) / 0.25))
    if e <= 0: return
    h = 330; x0, y0 = CX - CW / 2, CY - 150
    panel(ctx, x0, y0, CW, h, e)
    put(ctx, T_('LA TÉCNICA', HN, 26, ACC, 0.18, idx=BOLD), 44, 50, alpha=e, ax=0)
    put(ctx, T_('Para que no se acabe tu plan de $20:', HN, 40, WHITE, -0.01, idx=BOLD), 44, 104, alpha=e, ax=0)
    for k in range(3):
        y = 168 + k * 54
        put(ctx, T_('%d.' % (k + 1), MENLO, 34, MUT, 0, idx=0), 44, y, alpha=e, ax=0)
        if punch and vt >= T(75) - 0.05 + 0.12 * k:          # "yo tampoco…" -> ??? appear line by line
            put(ctx, T_('???', MENLO, 34, WHITE, 0.05, idx=1), 96, y, alpha=e, ax=0)
        else:
            ctx.rectangle(96, y + 14, 420 - 90 * k, 2); ctx.set_source_rgba(1, 1, 1, 0.16 * e); ctx.fill()
    if not punch and int(vt * 2.2) % 2 == 0:                  # blinking cursor on line 1
        ctx.rectangle(98, 168 - 20, 4, 40); rgba(ctx, ACC, e); ctx.fill()
    ctx.restore()

PROMPT = 'Hazme todo el proyecto. Sin errores.'
def prompt_box(ctx, vt):
    """'con un prompt utilizando Opus 5.5' -> prompt box types out above the usage card; model chip pops on 'Opus'"""
    a, b = T(61) - 0.05, T(72) - 0.05
    if not (a <= vt < b + 0.25): return
    e = expo_out(prog(vt, a, 0.4)) * (1 - c01((vt - b) / 0.25))
    if e <= 0: return
    w_, h_ = CW, 128; x0, y0 = CX - CW / 2, CY - CH / 2 - 150
    panel(ctx, x0, y0, w_, h_, e)
    n = int(len(PROMPT) * c01((vt - T(62)) / 1.2))
    put(ctx, T_(PROMPT[:n] if n else ' ', HN, 36, WHITE, -0.01, idx=REG), 40, 52, alpha=e, ax=0)
    if n < len(PROMPT) and int(vt * 2.4) % 2 == 0:
        tw_ = T_(PROMPT[:n], HN, 36, WHITE, -0.01, idx=REG)[4] if n else 0
        ctx.rectangle(42 + tw_, 32, 3, 40); rgba(ctx, ACC, e); ctx.fill()
    k = eo(prog(vt, T(65) - 0.05, 0.3))
    if k > 0:
        ch_ = T_('Opus 5.5', HN, 28, WHITE, 0, idx=BOLD); cw_ = ch_[4] + 52
        rr(ctx, 40, 82, cw_, 36, 18); ctx.set_source_rgba(1, 1, 1, 0.10 * e * k); ctx.fill()
        ctx.arc(60, 100, 6, 0, 2 * math.pi); rgba(ctx, ACC, e * k); ctx.fill()
        put(ctx, ch_, 76, 101, alpha=e * k, ax=0)
    ctx.arc(w_ - 64, h_ / 2, 26, 0, 2 * math.pi); rgba(ctx, ACC, e); ctx.fill()        # send button
    ctx.move_to(w_ - 64, h_ / 2 + 11); ctx.line_to(w_ - 64, h_ / 2 - 11); ctx.move_to(w_ - 74, h_ / 2 - 1); ctx.line_to(w_ - 64, h_ / 2 - 11)
    ctx.line_to(w_ - 54, h_ / 2 - 1); ctx.set_source_rgba(1, 1, 1, e); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def stamp(ctx, vt):
    """'ni idea' -> yellow rubber-stamp lands on the note; then the comment CTA"""
    t0 = T(78) - 0.05
    if vt < t0: return
    k = prog(vt, t0, 0.22); e = c01(k * 3)
    s_ = 1.35 - 0.35 * eo(k)
    tt = T_('NI IDEA', HN, 96, (0.06, 0.06, 0.06, 1), 0.02, idx=BOLD)
    w_, h_ = tt[4] + 70, 130
    ctx.save(); ctx.translate(W / 2 + 150, CY + 40); ctx.rotate(math.radians(-8)); ctx.scale(s_, s_)
    rr(ctx, -w_ / 2, -h_ / 2, w_, h_, 14); ctx.set_source_rgba(1.0, 231 / 255, 46 / 255, e); ctx.fill_preserve()
    ctx.set_source_rgba(0, 0, 0, e); ctx.set_line_width(5); ctx.stroke()
    put(ctx, tt, 0, 4, alpha=e)
    ctx.restore()
    k2 = expo_out(prog(vt, VTOTAL + 0.05, 0.4))
    if k2 > 0:
        c = T_('¿Tú sí la sabes? Déjala en los comentarios', HN, 40, WHITE, -0.01, idx=BOLD)
        sc = min(1.0, 960 / c[4]); w_ = c[4] * sc + 60
        rr(ctx, W / 2 - w_ / 2, 1505 - 36 + 14 * (1 - k2), w_, 72, 36); rgba(ctx, ACC, k2); ctx.fill()
        put(ctx, c, W / 2, 1506 + 14 * (1 - k2), scale=sc, alpha=k2)

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

TITLE = ['LA TÉCNICA PARA QUE', 'TU PLAN DE $20 DE', 'CLAUDE NO SE ACABE']
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
    punch = 1.0                                                     # no punch-in: in the last take my head already touches the top of the frame
    sdr = np.zeros((H, W, 3), np.float32)
    arr, surf, ctx = fx.new_layer()
    sdr[:] = speaker(fr16, t, (W, H), extra=punch); hdr = sdr.copy()
    usage_card(ctx, vt); prompt_box(ctx, vt); technique_note(ctx, vt); stamp(ctx, vt)
    if t >= TITLE_END and vt < VTOTAL + 0.05: subtitles(ctx, t, 1505, plate=True)
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
