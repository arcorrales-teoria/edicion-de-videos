SRC = '/Users/acorrales/Downloads/IMG_8907.mov'
KEEP = [(5.76, 18.12), (19.22, 42.55)]
SIL = [tuple(map(float, l.split())) for l in open('sil.txt')]
PAD = 0.05
def segments():
    out = []
    for a, b in KEEP:
        cur = a
        for s, e in SIL:
            if e - s < 0.18: continue
            cs, ce = max(s + PAD, a), min(e - PAD, b)
            if ce - cs > 0.06 and cs > cur:
                out.append((cur, cs)); cur = ce
        if b - cur > 0.05: out.append((cur, b))
    return [s for s in out if s[1] - s[0] > 0.12]
SEGS = segments()

# --- snap every internal boundary to the quietest nearby point (voiced band 80-600 Hz), so no cut lands inside a vowel/"eeh"
def _snap(segs):
    import numpy as np, wave, os
    w = wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src48.wav')); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768
    F = np.fft.rfftfreq(480, 1 / sr); band = (F > 80) & (F < 600); win = np.hanning(480)
    def vb(t):
        i = int(t * sr); seg = x[i:i + 480]
        return 20 * np.log10(np.sqrt((np.abs(np.fft.rfft(seg * win))[band] ** 2).mean()) + 1e-9) if len(seg) == 480 else 0
    out = [list(sg) for sg in segs]
    for i in range(len(out)):
        a, b = out[i]
        if i > 0:                       # start: look slightly before (into the removed pause) or just after
            lo = max(out[i - 1][1] + 0.02, a - 0.15)
            out[i][0] = min(np.arange(lo, a + 0.04, 0.005), key=vb)
        if i < len(out) - 1:            # end: look into the removed pause (after) or just before
            hi = min(out[i + 1][0] - 0.02, b + 0.15)
            out[i][1] = min(np.arange(b - 0.04, hi, 0.005), key=vb)
    return [(float(a), float(b)) for a, b in out if b - a > 0.12]
SEGS = _snap(SEGS)
SEGS[-1] = (SEGS[-1][0], 42.32)      # let the tail of "sígueme" ring out
OFF = []; acc = 0
for a, b in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
def seg_index(t):
    for i, ((a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); a, b = SEGS[i]
    return min(a + t - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f' % TOTAL)
