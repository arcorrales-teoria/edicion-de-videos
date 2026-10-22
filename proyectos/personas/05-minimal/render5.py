"""IMG_8866 — title (5 s) + subtitles, few animations, no SFX, 1.1x speed. HDR passthrough + SDR copy."""
import sys, os, json, math, subprocess, wave
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..', '..', 'herramientas')
sys.path.insert(0, os.path.join(ROOT, 'v4')); sys.path.insert(0, ROOT)
_cwd = os.getcwd(); os.chdir(os.path.join(ROOT, 'v4'))
import render4 as K          # shared FPS-style components (fonts, glass, rise, pill, HDR compositing)
os.chdir(_cwd)
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location('edit5', os.path.join(HERE, 'edit5.py'))
E = importlib.util.module_from_spec(_spec); _cwd = os.getcwd(); os.chdir(HERE); _spec.loader.exec_module(E); os.chdir(_cwd)

from render import np, Image, cairo, c01, prog, eio, eo
W, H, FPS = K.W, K.H, K.FPS
SPEED = 1.1
TOTAL = E.TOTAL / SPEED
DUR = TOTAL + 0.35
T_, put, rise, glass, pill, corners_line, mono_label, check_icon = K.T_, K.put, K.rise, K.glass, K.pill, K.corners_line, K.mono_label, K.check_icon
expo_out, rgba = K.expo_out, K.rgba
BLUE, FG, MUTED = K.BLUE, K.FG, K.MUTED
HG800, HG300, HG500 = K.HG800, K.HG300, K.HG500

# ---------------- words (output time: transcribed from the 1.1x voice) ----------------
_ws = [w for s in json.load(open(os.path.join(HERE, 'v16.json')))['segments'] for w in s['words']]
FIX = {16: 'Claude Code', 18: 'Lovable.', 28: 'Lovable', 31: 'fronts,', 34: 'dashboards,', 47: 'front.', 51: 'Lovable',
       60: 'Claude Code', 79: 'Lovable', 107: 'Claude Code,', 115: 'Lovable', 121: 'Claude Code', 134: 'Claude',
       143: 'pushear', 48: 'Pero', 76: 'Pero'}
WORDS = []
for i, w in enumerate(_ws):
    if i == 75:   # "5" + ".5." -> "5.5."
        WORDS[-1] = (WORDS[-1][0], w['end'], '5.5.'); continue
    WORDS.append((w['start'], w['end'], FIX.get(i, w['word'].strip())))
def T(i): return _ws[i]['start']

TITLE_END = 5.0
def build_chunks():
    ch, cur = [], []
    for k, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[k + 1] if k + 1 < len(WORDS) else None
        chars = sum(len(x[2]) for x in cur)
        if (len(cur) >= 3 or chars >= 15 or w[2][-1] in '.,?' or nxt is None or nxt[0] - w[1] > 0.35
                or (nxt and len(nxt[2]) > 10 and chars > 8)):
            ch.append(cur); cur = []
    out = []
    for i, c in enumerate(ch):
        st = max(c[0][0] - 0.03, TITLE_END)
        en = ch[i + 1][0][0] - 0.03 if i + 1 < len(ch) else c[-1][1] + 0.4
        if en > st: out.append((st, min(en, c[-1][1] + 0.5), c))
    return out
CHUNKS = build_chunks()

def subtitles(ctx, t, y=1470):
    if t < TITLE_END: return
    for st, en, ws in CHUNKS:
        if st <= t < en: break
    else: return
    size = 64; gap = size * 0.28
    parts = []
    for (a, b, w) in ws:
        active = a - 0.03 <= t < b + 0.02 or (w == ws[-1][2] and t >= a)
        parts.append((T_(w, HG800, size, FG, -0.03, shadow=not active), active))
    total = sum(p[0][4] for p in parts) + gap * (len(parts) - 1)
    sc = min(1.0, 940 / total)
    e = expo_out(prog(t, st, 0.35))
    x = W / 2 - total * sc / 2
    for tt, active in parts:
        ww = tt[4] * sc; yy = y + 16 * (1 - e)
        if active:
            ctx.rectangle(x - 12 * sc, yy - size * 0.62 * sc, ww + 24 * sc, size * 1.2 * sc); rgba(ctx, BLUE, e); ctx.fill()
        put(ctx, tt, x, yy, scale=sc, alpha=e, ax=0)
        x += ww + gap * sc

# ---------------- the few graphics ----------------
def title(ctx, t, fi):
    if t >= TITLE_END: return
    k_in = expo_out(prog(t, 0.05, 0.8)); k_out = 1 - c01((t - (TITLE_END - 0.4)) / 0.4)
    a = k_in * k_out
    if a <= 0: return
    ctx.save(); ctx.translate(0, 40 * (1 - k_in) - 30 * (1 - k_out))
    x, y, w, h = 70, 1010, 940, 490
    glass(ctx, x, y, w, h, 30, a, 0.72)
    corners_line(ctx, x, y, w, h, 1, 48, 5, FG, a)
    mono_label(ctx, t, 0.25, 'Idea de startup', x + 50, y + 70, 30, FG, True, fi)
    t_out = TITLE_END - 0.4
    rise(ctx, t, 0.45, ['Un', 'conector', 'entre'], 540, y + 200, [74] * 3, [HG300] * 3, [FG] * 3, t_out=t_out)
    rise(ctx, t, 0.75, ['Claude', 'Code'], 540, y + 305, [96, 96], [HG800, HG800], [FG, FG], t_out=t_out)
    rise(ctx, t, 1.05, ['y', 'Lovable'], 540, y + 410, [96, 96], [HG300, HG800], [FG, FG], bg=BLUE, t_out=t_out)
    ctx.restore()

def opus_pill(ctx, t, fi):
    t0 = T(73) - 0.1; t1 = T(76) - 0.1
    if not (t0 <= t < t1 + 0.3): return
    k = expo_out(prog(t, t0, 0.6)) * (1 - c01((t - t1) / 0.3))
    pill(ctx, 540, 1110, 'Claude Code + Opus 5.5', k, None, FG, 48, BLUE)

ROWS = [(T(109) - 0.05, 'Mi equipo', 'Lovable'), (T(117) - 0.05, 'Yo', 'Claude Code'), (T(144) - 0.05, 'Un proyecto', 'en conjunto')]
def team_panel(ctx, t, fi):
    t0 = ROWS[0][0] - 0.15; t1 = T(148)
    if not (t0 <= t < t1 + 0.4): return
    e = expo_out(prog(t, t0, 0.8)) * (1 - c01((t - t1) / 0.4))
    x, y, w, h = 90, 960, 900, 420
    ctx.save(); ctx.translate(0, 60 * (1 - expo_out(prog(t, t0, 0.8))))
    glass(ctx, x, y, w, h, 28, e, 0.7)
    for i, (ti, lab, val) in enumerate(ROWS):
        ry = y + 95 + i * 118
        if i < 2: ctx.rectangle(x + 44, ry + 58, w - 88, 1); rgba(ctx, FG, 0.14 * e); ctx.fill()
        if t < ti: continue
        a = expo_out(prog(t, ti, 0.5)) * e
        if i < 2:
            ctx.rectangle(x + 44, ry - 8, 16, 16); rgba(ctx, FG, a); ctx.fill()
            put(ctx, T_(lab, HG300, 50, FG, -0.02), x + 84, ry + 1, alpha=a, ax=0)
            tv = T_(val, HG800, 50, FG, -0.03)
            put(ctx, tv, x + w - 44, ry + 1, alpha=a, ax=1)
        else:
            check_icon(ctx, x + 70, ry + 4, 30, t, ti)
            rise(ctx, t, ti + 0.05, ['Un', 'proyecto', 'en', 'conjunto.'], x + 120, ry + 4, [54] * 4, [HG300, HG800, HG300, HG800], [FG] * 4, align='left', stagger=0.07)
    ctx.restore()

def closing_pill(ctx, t, fi):
    t0 = T(159) - 0.08
    if t < t0: return
    pill(ctx, 540, 1110, 'Todavía no existe', expo_out(prog(t, t0, 0.6)), BLUE, FG, 52, FG, glassy=False)

GRAPHICS = [title, opus_pill, team_panel, closing_pill]

# ---------------- camera: jump-cut zoom cycle (no other transitions) ----------------
CUTS = [o / SPEED for o in E.OFF]
ZCYCLE = [1.0, 1.2, 1.08, 1.3]
def face_zoom(t):
    i = max(k for k, c in enumerate(CUTS) if c <= t + 1e-6)
    t0 = CUTS[i]; base = ZCYCLE[i % 4] if i > 0 else 1.0
    if i == 0: base = 1.0 + 0.12 * (1 - expo_out(prog(t, 0, 1.2)))
    return base * (1 + 0.03 * eio(c01((t - t0) / 3.0))) * (1 + (0.05 if i > 0 else 0) * (1 - eo(prog(t, t0, 0.28))))

def render_frame(fr16, t, fi):
    arr, surf, ctx = K.new_layer()
    base = K.resize_f(fr16, K.crop_box(face_zoom(t)), (W, H))
    for g in GRAPHICS: g(ctx, t, fi)
    subtitles(ctx, t)
    surf.flush()
    sdr = base.copy(); hdr = base
    K.layer_over(sdr, hdr, arr)
    return sdr, hdr

# ---------------- io ----------------
def frames(times=None):
    n = int(DUR * FPS)
    want = range(n) if times is None else sorted({int(round(x * FPS)) for x in times})
    cmd = ['ffmpeg', '-v', 'error', '-i', E.SRC, '-vf',
           'fps=30,scale=1440:2560:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
           '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1440 * 2560 * 6)
    sz = 1440 * 2560 * 6; cur_k = -1; cur_b = None
    for fi in want:
        t = fi / FPS
        te = min(t * SPEED, E.TOTAL - 0.001)
        st = E.src_of(te) + max(0, t * SPEED - E.TOTAL)
        k = int(round(st * FPS))
        while cur_k < k:
            b = p.stdout.read(sz)
            if len(b) < sz: break
            cur_k += 1; cur_b = b
        fr = np.frombuffer(cur_b, np.uint16).reshape(2560, 1440, 3).astype(np.float32) / 65535
        yield fi, t, fr
    p.kill()

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
        for fi, t, fr in frames(times):
            sdr, hdr = render_frame(fr, t, fi)
            Image.fromarray(K.to8(sdr)).save(os.path.join(HERE, 'prev', 'p%05.2f.jpg' % t), quality=85)
        return
    build_audio()
    out_hdr, out_sdr = sys.argv[2], sys.argv[3]
    common = ['-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)]
    enc_h = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb48le', '-color_range', 'pc', '-i', '-',
                             '-i', os.path.join(HERE, 'mix.wav'),
                             '-vf', 'scale=out_color_matrix=bt2020:in_range=pc:out_range=tv:flags=bicubic+accurate_rnd,format=yuv420p10le',
                             '-c:v', 'libx265', '-crf', '17', '-preset', 'medium', '-tag:v', 'hvc1',
                             '-x265-params', 'colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error',
                             '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_hdr], stdin=subprocess.PIPE)
    enc_s = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb24', '-i', '-',
                             '-i', os.path.join(HERE, 'mix.wav'),
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                             '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-bsf:v',
                             'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_sdr], stdin=subprocess.PIPE)
    for fi, t, fr in frames():
        sdr, hdr = render_frame(fr, t, fi)
        enc_h.stdin.write(np.ascontiguousarray(K.to16(hdr)).tobytes())
        enc_s.stdin.write(np.ascontiguousarray(K.to8(sdr)).tobytes())
        if fi % 300 == 0: print('frame', fi, '/', int(DUR * FPS), flush=True)
    for e_ in (enc_h, enc_s): e_.stdin.close()
    for e_ in (enc_h, enc_s): e_.wait()
    print('done', out_hdr, out_sdr)

if __name__ == '__main__':
    main()
