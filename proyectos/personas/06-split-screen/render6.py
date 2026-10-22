"""IMG_8875 — split-screen reel (speaker top, silent screen recording bottom), 5 s title on the seam, white subtitles.
Style reference: IMG_8876.PNG. No SFX, no color correction (HDR passthrough + SDR copy)."""
import sys, os, json, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import fx, framing
FT = framing.FaceTrack(os.path.join(os.path.dirname(HERE), 'tools', 'faces_8875.txt'))
from fx import np, Image, W, H, FPS, prog, c01, expo_out, eio, eo, T_, put, rgba
_cwd = os.getcwd(); os.chdir(HERE); import edit6 as E; os.chdir(_cwd)

REC = '/Users/acorrales/Downloads/ScreenRecording_10-01-2026 19-14-13_1.MP4'
REC_DUR = 22.885
DUR = E.TOTAL + 0.3
SEAM = 960                       # top: speaker 1080x960 | bottom: recording 1080x960
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; BOLD = 1
WHITE = (1, 1, 1, 1)
TITLE_END = 5.0
TITLE = ['La campaña de QuikTrip', 'es una clase de', 'marketing']

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
P1_SRC0 = 1.2                            # skip the app's play/mute overlay at the start
P1 = min(REC_DUR - 0.05 - P1_SRC0, DUR)   # pass 1: real time
P2_SRC0 = 2.0                            # pass 2: from 2 s, slowed to fill the rest, tighter crop
def rec_stream():
    # pass 1: full-width crop of the video area (between the app title and the caption)
    f1 = (f'trim=start={P1_SRC0},setpts=PTS-STARTPTS,crop=960:853:30:770,scale=1080:960:flags=bicubic,fps=30,format=rgb24')
    rest = max(0.1, DUR - P1)
    slow = rest / (REC_DUR - P2_SRC0)
    f2 = (f'trim=start={P2_SRC0},setpts=(PTS-STARTPTS)*{slow:.5f},crop=900:800:70:840,scale=1080:960:flags=bicubic,fps=30,format=rgb24')
    for flt, dur, ss in ((f1, P1, 0), (f2, rest, 0)):
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', REC, '-an', '-vf', flt, '-t', f'{dur:.3f}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                             stdout=subprocess.PIPE)
        sz = 1080 * 960 * 3
        while True:
            b = p.stdout.read(sz)
            if len(b) < sz: break
            yield np.frombuffer(b, np.uint8).reshape(960, 1080, 3)
        p.kill()

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
    title(ctx, t); subtitles(ctx, t)
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
