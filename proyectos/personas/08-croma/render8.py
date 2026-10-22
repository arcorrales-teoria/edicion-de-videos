"""IMG_8907 · split-screen reel (+ website pill), 1.1x: speaker top, silent Croma onboarding recording bottom, 5 s title on the seam,
white subtitles. Same style as IMG_8877 (split + website) and IMG_8866 (1.1x). No SFX, no color correction (HDR passthrough + SDR copy)."""
import sys, os, json, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
FT = framing.FaceTrack(os.path.join(HERE, 'faces_8907.txt'))
from fx import np, Image, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
_cwd = os.getcwd(); os.chdir(HERE); import edit8 as E; os.chdir(_cwd)

REC = '/Users/acorrales/Downloads/Onboarding Croma.mp4'
REC_A, REC_B = 8.0, 35.933 - 2.0     # drop the first 8 s and the last 2 s
URL = 'usecroma.com'
SPEED = 1.1
TOTAL = E.TOTAL / SPEED
DUR = TOTAL + 0.3
SEAM = 960                       # top: speaker 1080x960 | bottom: recording 1080x960
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD = 1
WHITE = (1, 1, 1, 1)
TITLE_END = 5.0
SUB_Y = 1065                      # just under the website pill: the empty top strip of the app, so the onboarding stays visible
TITLE = ['Un buen onboarding', 'es lo que te permite', 'conseguir más usuarios']

# ---------------- words ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {0: 'Venga,', 1: 'si', 27: 'producto,', 31: 'mal.', 32: '¿Por', 34: 'Porque', 39: 'principal.', 45: 'crearon', 48: 'lindo,',
       51: 'dice,', 58: 'hay,', 67: 'hacer,', 79: 'página,', 87: 'lindo,', 93: 'hacer,', 102: 'nada', 112: 'fricción,', 123: 'vainas,',
       124: 'sígueme.'}
WORDS = []
for i, w in enumerate(_ws):
    if i in (41, 43): continue                                   # Whisper split "esos manes" into "eso es mal es"
    if i == 40: WORDS.append((w['start'], _ws[41]['end'], 'Esos')); continue
    if i == 42: WORDS.append((w['start'], _ws[43]['end'], 'manes')); continue
    WORDS.append((w['start'], w['end'], FIX.get(i, w['word'].strip())))

def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) + 1 for x in cur)
        if (len(cur) >= 5 or chars >= 24 or w[2][-1] in '.,?' or nxt is None or nxt[0] - w[1] > 0.35):
            ch.append(cur); cur = []
    out = []
    for j, c in enumerate(ch):
        st = max(c[0][0] - 0.03, TITLE_END)
        en = ch[j + 1][0][0] - 0.03 if j + 1 < len(ch) else c[-1][1] + 0.4
        if en > st: out.append((st, min(en, c[-1][1] + 0.6), c))
    return out
CHUNKS = build_chunks()

def subtitles(ctx, t):
    if t < TITLE_END: return
    for st, en, ws in CHUNKS:
        if st <= t < en: break
    else: return
    line = ' '.join(x[2] for x in ws)
    tt = T_(line, HN, 62, WHITE, -0.035, shadow=7, idx=BOLD, shadow_a=210, shadow_off=4)
    sc = min(1.0, 940 / tt[4]); a = c01((t - st) / 0.08)
    bw, bh = tt[4] * sc + 56, 92                 # soft dark plate: the Croma UI behind is busy white-on-black text
    import math
    ctx.new_sub_path(); r = 22; x0, y0 = W / 2 - bw / 2, SUB_Y - bh / 2 + 4
    ctx.arc(x0 + bw - r, y0 + r, r, -math.pi / 2, 0); ctx.arc(x0 + bw - r, y0 + bh - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y0 + bh - r, r, math.pi / 2, math.pi); ctx.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.85 * a); ctx.fill()
    put(ctx, tt, W / 2, SUB_Y, scale=sc, alpha=a)

def title(ctx, t):
    if t >= TITLE_END: return
    a = c01((t - 0.05) / 0.25) * (1 - c01((t - (TITLE_END - 0.35)) / 0.35))
    if a <= 0: return
    s = 0.96 + 0.04 * expo_out(prog(t, 0.05, 0.6))
    lines = [T_(l, HN, 104, WHITE, -0.055, shadow=8, idx=BOLD, shadow_a=200, shadow_off=5) for l in TITLE]
    lh = 108; y0 = SEAM - lh * (len(lines) - 1) / 2 - 20
    # translucent dark band behind the title (as in the reference)
    ctx.rectangle(0, y0 - 78, W, lh * len(lines) + 70); ctx.set_source_rgba(0, 0, 0, 0.36 * a); ctx.fill()
    sc0 = min(1.0, min(1000 / tt[4] for tt in lines))          # one size for every line
    for k, tt in enumerate(lines):
        sc = sc0 * s
        put(ctx, tt, W / 2, y0 + k * lh, scale=sc, alpha=a)

# ---------------- camera (top panel): jump-cut zoom cycle ----------------
CUTS = [o / SPEED for o in E.OFF]
ZC = [1.0, 1.07, 1.0, 1.12]           # gentler than 8877: in this take the face is very close to the lens
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6)
    t0 = CUTS[i]; base = ZC[i % 4]
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))

# ---------------- bottom panel: silent screen recording (two passes, app UI cropped out) ----------------
# three screens, each cropped to its content (no desktop wallpaper, no side widget); the whole process plays once, slowed to fit
RATE = (REC_B - REC_A) / (DUR + 0.2)
PARTS = [(REC_A, 23.85, 'crop=785:698:440:211,scale=1080:960:flags=bicubic'),                         # logo + questions + countries
         (23.85, 32.25, 'crop=990:880:337:115,scale=1080:960:flags=bicubic'),                          # "¿Cómo quieres empezar?"
         (32.25, REC_B, 'crop=990:880:135:115,scale=1080:960:flags=bicubic')]  # dashboard (sidebar + API keys)
def rec_stream():
    for (a, b, crop) in PARTS:
        flt = f'trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{RATE},{crop},fps=30,format=rgb24'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', REC, '-an', '-vf', flt, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             stdout=subprocess.PIPE)
        sz = 1080 * 960 * 3; last = None
        while True:
            b_ = p.stdout.read(sz)
            if len(b_) < sz: break
            last = np.frombuffer(b_, np.uint8).reshape(960, 1080, 3); yield last
        p.kill()
    while True: yield last                                      # hold the last frame if we run a hair short

# ---------------- website pill ----------------
def _word_t(prefix, after=0.0):
    for (a, b, w) in WORDS:
        if a >= after and w.lower().startswith(prefix): return a
    return None
T_URL = (_word_t('esos') or 10.5) - 0.1     # "esos manes" (esta gente) -> their link
T_WEB = T_URL
def website(ctx, t):
    if t < max(T_URL, TITLE_END): return
    t0 = max(T_URL, TITLE_END)
    e = expo_out(prog(t, t0, 0.5))
    pulse = 1 + 0.07 * np.sin(np.pi * prog(t, T_WEB - 0.05, 0.45))
    tt = T_(URL, HN, 50, WHITE, -0.02, idx=BOLD)
    w = tt[4] + 118; h = 92
    ctx.save(); ctx.translate(W / 2, SEAM + 22 * (1 - e)); ctx.scale(pulse, pulse)
    from fx import cairo
    import math
    ctx.new_sub_path(); r = h / 2
    ctx.arc(-w / 2 + r, 0, r, math.pi / 2, 3 * math.pi / 2); ctx.arc(w / 2 - r, 0, r, -math.pi / 2, math.pi / 2); ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.62 * e); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 0.35 * e); ctx.set_line_width(2); ctx.stroke()
    gx = -w / 2 + 50                      # tiny globe icon
    ctx.arc(gx, 0, 17, 0, 2 * math.pi); ctx.save(); ctx.scale(0.45, 1); ctx.arc(gx / 0.45, 0, 17, 0, 2 * math.pi); ctx.restore()
    ctx.move_to(gx - 17, 0); ctx.line_to(gx + 17, 0)
    ctx.set_source_rgba(1, 1, 1, e); ctx.set_line_width(2.6); ctx.stroke()
    put(ctx, tt, -w / 2 + 84, 2, alpha=e, ax=0)
    ctx.restore()

# one locked framing per take (no per-frame face tracking: the Vision boxes jump when I lean in / hands cross the face -> shaky crop)
def _take_box(lo, hi):
    m = (FT.t >= lo) & (FT.t <= hi)
    b = FT.b[m] if m.any() else FT.box((lo + hi) / 2)[None]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 15); chin = np.percentile(b[:, 1] + b[:, 3], 85)
    h = chin - top
    return (cx - fw / 2, top - 0.12 * h, fw, h * 1.12)          # extra room for the full hair volume
TAKE_BOX = [_take_box(a, b) for a, b in E.SEGS]

# ---------------- frame ----------------
def render_frame(fr16, rec8, t):
    sdr = np.empty((H, W, 3), np.float32)
    te = min(t * SPEED, E.TOTAL - 0.001); si = E.seg_index(te); lo, hi = E.SEGS[si]
    fb = TAKE_BOX[si]
    box = framing.head_crop(fb, face_zoom(t), panel=(W, SEAM), top_air=0.09)
    top = fx.resize_f(fr16, box, (W, SEAM))
    sdr[:SEAM] = top
    hdr = sdr.copy()
    sdr[SEAM:] = rec8.astype(np.float32) / 255
    hdr[SEAM:] = fx.srgb8_to_hlg(rec8)
    arr, surf, ctx = fx.new_layer()
    title(ctx, t); website(ctx, t); subtitles(ctx, t)
    surf.flush()
    fx.layer_over(sdr, hdr, arr)
    return sdr, hdr

def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    src = fx.hlg_reader(E.SRC); cur_k, cur_b = -1, None
    rec = rec_stream(); rk, rcur = -1, None
    for fi in want:
        t = fi / FPS
        st = E.src_of(min(t * SPEED, E.TOTAL - 0.001)) + max(0, t * SPEED - E.TOTAL)
        k = int(round(st * FPS))
        while cur_k < k:
            try: cur_k, cur_b = next(src)
            except StopIteration: break
        while rk < fi:
            try: rcur = next(rec); rk += 1
            except StopIteration: rk = fi
        fr = np.frombuffer(cur_b, np.uint16).reshape(fx.SH, fx.SW, 3).astype(np.float32) / 65535
        yield fi, t, fr, rcur

def build_audio():
    SR = 48000
    with wave.open(os.path.join(HERE, 'voice_s16.wav')) as w:
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(DUR * SR); m = np.zeros((n, 2), np.float32); m[:min(n, len(v))] = v[:n]
    with wave.open(os.path.join(HERE, 'mix.wav'), 'wb') as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(os.path.join(HERE, 'prev'), exist_ok=True)
        for fi, t, fr, rec in frames(times):
            sdr, hdr = render_frame(fr, rec, t)
            Image.fromarray(fx.to8(sdr)).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    eh, es = fx.encoders(sys.argv[2], sys.argv[3], os.path.join(HERE, 'mix.wav'))
    for fi, t, fr, rec in frames():
        sdr, hdr = render_frame(fr, rec, t)
        eh.stdin.write(np.ascontiguousarray(fx.to16(hdr)).tobytes()); es.stdin.write(np.ascontiguousarray(fx.to8(sdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    for e_ in (eh, es): e_.stdin.close()
    for e_ in (eh, es): e_.wait()
    print('done', sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
