"""IMG_9108 · Idea de startup: una app que te recomiende restaurantes. Recorded walking on the street: cleaned FIRST with
DeepFilterNet3 (src9108c.wav), cuts on the clean envelope. Removed: "márica", three "literalmente/literal", "o no hay un LLM o hay
algo", "nosotros todo el día abrimos restaurantes", "de lo que uno tenga", "porque es que en mucho tiempo", "¿quién es? no sé",
"eso es una vaina"."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9108.MOV'}
WAVS = {'a': 'src9108c.wav'}
import wave as _w, numpy as _np, os as _os
_X = {}
def _load(s):
    if s not in _X:
        wf = _w.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), WAVS[s]))
        _X[s] = (_np.frombuffer(wf.readframes(wf.getnframes()), _np.int16).reshape(-1, 2).astype(_np.float32).mean(1) / 32768, wf.getframerate())
    return _X[s]
def V(lo, hi, s='a'):
    x, sr = _load(s); ts = _np.arange(lo, hi, 0.005)
    return float(min(ts, key=lambda t: _np.sqrt((x[int(t * sr):int((t + 0.02) * sr)] ** 2).mean())))
RAW = [
    ('a', 0.40, 2.05),
    ('a', 3.05, 5.22),
    ('a', 5.42, 6.38),
    ('a', 6.66, 6.72),
    ('a', 7.73, 8.38),
    ('a', 8.65, 9.58),
    ('a', 10.20, 12.00),
    ('a', 14.94, 16.33),
    ('a', 16.69, 19.87),
    ('a', 20.29, 20.37),
    ('a', 21.99, 22.99),
    ('a', 23.34, 25.92),
    ('a', 26.13, 27.98),
    ('a', 28.93, 30.61),
    ('a', 30.81, 33.75),
    ('a', 33.97, 34.46),
    ('a', 34.83, 37.01),
    ('a', 37.22, 37.81),
    ('a', 38.04, 39.22),
    ('a', 39.75, 41.81),
    ('a', 42.11, 43.19),
    ('a', 43.70, 45.86),
    ('a', 47.17, 48.80),
    ('a', 49.08, 49.80),
    ('a', 50.10, 51.47),
    ('a', 51.88, 54.14),
    ('a', 54.46, 55.53),
    ('a', 55.68, 56.46),
    ('a', 56.71, 58.26),
    ('a', 59.53, 61.31),
    ('a', 61.49, 62.64),
    ('a', 63.24, 65.05),
    ('a', 65.51, 68.12),
    ('a', 68.36, 69.45),
    ('a', 69.60, 70.77),
    ('a', 71.24, 73.73),
    ('a', 74.11, 74.19),
    ('a', 75.54, 77.77),
    ('a', 78.07, 78.45),
    ('a', 78.94, 80.67),
    ('a', 81.20, 83.14),
    ('a', 83.54, 86.12),
    ('a', 86.30, 88.75),
    ('a', 88.95, 91.55),
    ('a', 92.87, 95.35),
]

NO_SNAP = {(s_, a_) for s_, a_, b_ in RAW}                                 # every boundary sits in clean silence already: no snapping
_x = {}
def _wav(s):
    if s not in _x:
        w = wave.open(os.path.join(HERE, WAVS[s])); sr = w.getframerate()
        _x[s] = (np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768, sr)
    return _x[s]
def vb(s, t):
    x, sr = _wav(s); i = int(t * sr); seg = x[i:i + 480]
    if len(seg) < 480: return 0
    F = np.fft.rfftfreq(480, 1 / sr); band = (F > 80) & (F < 600)
    return 20 * np.log10(np.sqrt((np.abs(np.fft.rfft(seg * np.hanning(480)))[band] ** 2).mean()) + 1e-9)

def _snap(raw):
    """move every boundary to the quietest point within +-60 ms (pads are already in the pauses)"""
    out = []
    for s, a, b in raw:
        if (s, a) in NO_SNAP: out.append((s, a, b)); continue
        a2 = min(np.arange(max(0.0, a - 0.06), a + 0.03, 0.005), key=lambda t: vb(s, t))
        b2 = min(np.arange(b - 0.03, b + 0.06, 0.005), key=lambda t: vb(s, t))
        out.append((s, float(a2), float(b2)))
    return out
SEGS = _snap(RAW)
OFF = []; acc = 0
for s, a, b in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
HOOK_END = TOTAL
def seg_index(t):
    for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); s, a, b = SEGS[i]
    return s, min(a + t - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f (%.2f at 1.05x)' % (TOTAL, TOTAL / 1.05))
