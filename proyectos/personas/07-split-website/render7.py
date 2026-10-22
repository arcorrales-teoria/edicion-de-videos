"""IMG_8877 · split-screen reel (+ website pill) (speaker top, silent screen recording bottom), 5 s title on the seam, white subtitles.
Style reference: IMG_8876.PNG. No SFX, no color correction (HDR passthrough + SDR copy)."""
import sys, os, json, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
FT = framing.FaceTrack(os.path.join(os.path.dirname(HERE), 'tools', 'faces_8877.txt'))
from fx import np, Image, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
_cwd = os.getcwd(); os.chdir(HERE); import edit6 as E   # (edit6.py in this folder points to IMG_8877); os.chdir(_cwd)

REC = '/Users/acorrales/Downloads/ScreenRecording_10-01-2026 19-39-56_1.MP4'
REC_DUR = 15.08
URL = 'bubbbly.com/bloom'
DUR = E.TOTAL + 0.3
SEAM = 960                       # top: speaker 1080x960 | bottom: recording 1080x960
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD = 1
WHITE = (1, 1, 1, 1)
TITLE_END = 5.0
TITLE = ['Esta página convierte', 'tus QR en ramos', 'de flores']

# ---------------- words ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
WORDS = []
i = 0
while i < len(_ws):
    w = _ws[i]; txt = w['word'].strip(); end = w['end']
    if txt.lower().startswith('quick') and i + 1 < len(_ws) and _ws[i + 1]['word'].strip().lower().startswith('trip'):
        tail = _ws[i + 1]['word'].strip()[4:]; txt = 'QuikTrip' + tail; end = _ws[i + 1]['end']; i += 1
    elif txt == 'increíbles?': txt = 'increíble?'
    elif txt == 'ese' and i + 1 < len(_ws) and _ws[i + 1]['word'].strip().startswith('2026'): txt = 'este'
    elif txt == 'que' and i == 0: pass
    elif txt.lower().startswith('buquet'): txt = 'buqué'
    elif txt.startswith('opamina'): txt = 'dopamina'
    elif txt == 'código': txt = 'códigos'
    elif txt == 'QRs,': txt = 'QR,'
    elif txt == 'sabes.': txt = 'saben.'
    WORDS.append((w['start'], end, txt)); i += 1
if WORDS and WORDS[0][2].lower().startswith('definitivamente'):
    WORDS[0] = (WORDS[0][0], WORDS[0][1], 'Definitivamente,')

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
    sc = min(1.0, 980 / tt[4])
    put(ctx, tt, W / 2, 1300, scale=sc, alpha=c01((t - st) / 0.08))

def title(ctx, t):
    if t >= TITLE_END: return
    a = c01((t - 0.05) / 0.25) * (1 - c01((t - (TITLE_END - 0.35)) / 0.35))
    if a <= 0: return
    s = 0.96 + 0.04 * expo_out(prog(t, 0.05, 0.6))
    lines = [T_(l, HN, 104, WHITE, -0.055, shadow=8, idx=BOLD, shadow_a=200, shadow_off=5) for l in TITLE]
    lh = 108; y0 = SEAM - lh * (len(lines) - 1) / 2 - 20
    # translucent dark band behind the title (as in the reference)
    ctx.rectangle(0, y0 - 78, W, lh * len(lines) + 70); ctx.set_source_rgba(0, 0, 0, 0.36 * a); ctx.fill()
    for k, tt in enumerate(lines):
        sc = min(1.0, 1010 / tt[4]) * s
        put(ctx, tt, W / 2, y0 + k * lh, scale=sc, alpha=a)

# ---------------- camera (top panel): jump-cut zoom cycle ----------------
CUTS = list(E.OFF)
ZC = [1.0, 1.1, 1.0, 1.16]
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6)
    t0 = CUTS[i]; base = ZC[i % 4]
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))

# ---------------- bottom panel: silent screen recording (two passes, app UI cropped out) ----------------
CROP_A = 'crop=900:800:150:530'          # laptop screen with the bouquet / QR (no captions, no like icons, no dock)
CROP_B = 'crop=760:676:220:590'          # tighter variant
PASSES = [(5.0, 15.0, 1.0, CROP_A), (0.0, 1.8, 0.6, CROP_B), (5.0, 15.0, 0.85, CROP_B), (5.0, 15.0, 0.8, CROP_A), (5.0, 15.0, 0.9, CROP_B)]
def rec_stream():
    left = DUR + 0.2
    for (a, b, rate, crop) in PASSES:
        if left <= 0: break
        d = min((b - a) / rate, left); left -= d
        flt = (f'trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{rate},{crop},scale=1080:960:flags=bicubic,fps=30,format=rgb24')
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', REC, '-an', '-vf', flt, '-t', f'{d:.3f}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             stdout=subprocess.PIPE)
        sz = 1080 * 960 * 3
        while True:
            b_ = p.stdout.read(sz)
            if len(b_) < sz: break
            yield np.frombuffer(b_, np.uint8).reshape(960, 1080, 3)
        p.kill()

# ---------------- website pill ----------------
def _word_t(prefix, after=0.0):
    for (a, b, w) in WORDS:
        if a >= after and w.lower().startswith(prefix): return a
    return None
T_URL = (_word_t('dejo') or 7.5) - 0.1
T_WEB = _word_t('website') or 22.0
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

# ---------------- frame ----------------
def render_frame(fr16, rec8, t):
    sdr = np.empty((H, W, 3), np.float32)
    te = min(t, E.TOTAL - 0.001); si = E.seg_index(te); lo, hi = E.SEGS[si]
    box = framing.head_crop(FT.box(E.src_of(te), lo, hi), face_zoom(t), panel=(W, SEAM))
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
        st = E.src_of(min(t, E.TOTAL - 0.001)) + max(0, t - E.TOTAL)
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
