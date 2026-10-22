"""IMG_9123 (hook) + IMG_9124 + IMG_9125 (inserted mid-video) · Casey Neistat. Shortened as much as possible (user request).
Takes cleaned with DeepFilterNet3 before cutting. Kept only one sentence per idea; removed repeats ("dudo mucho que se lo enseñen",
"y para mí quién es…", "lo mejor de todo es que el man te va contando…", "el man te ha hecho un cuento" x2, "lo mínimo es eso"),
all "literalmente", and the false start "si uno quiere empezar a lo que sea"."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9123.MOV', 'b': '/Users/acorrales/Downloads/IMG_9124.MOV', 'c': '/Users/acorrales/Downloads/IMG_9125.MOV'}
WAVS = {'a': 'src9123c.wav', 'b': 'src9124c.wav', 'c': 'src9125c.wav'}
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
    ('a', 0.62, 3.46),
    ('a', 4.13, 7.07),
    ('a', 12.67, 15.80),
    ('a', 21.45, 22.15),
    ('a', 22.72, 24.48),
    ('a', 24.81, 25.27),
    ('b', 0.00, 1.36),
    ('b', 1.61, 2.92),
    ('b', 3.08, 5.53),
    ('b', 6.56, 7.06),
    ('b', 7.51, 8.65),
    ('b', 8.85, 10.34),
    ('b', 10.94, 13.42),
    ('b', 13.77, 14.69),
    ('b', 14.98, 15.28),
    ('b', 16.10, 17.19),
    ('b', 17.39, 20.21),
    ('b', 20.48, 21.90),
    ('b', 22.34, 23.25),
    ('b', 23.41, 24.77),
    ('b', 25.00, 26.50),
    ('c', 1.91, 4.89),
    ('c', 5.24, 6.25),
    ('c', 6.55, 7.25),
    ('c', 7.49, 8.76),
    ('c', 9.04, 10.45),
    ('c', 16.69, 18.16),
    ('c', 18.41, 19.34),
    ('c', 23.10, 23.32),
    ('c', 23.53, 23.94),
    ('c', 24.10, 24.50),
    ('b', 38.49, 41.30),
    ('b', 42.36, 43.62),
    ('b', 54.50, 55.60),
    ('b', 59.79, 61.58),
    ('b', 61.78, 62.79),
    ('b', 63.19, 65.15),
    ('b', 65.42, 66.30),
    ('b', 68.07, 69.46),
    ('b', 69.66, 71.24),
    ('b', 71.53, 74.36),
    ('b', 75.45, 75.77),
    ('b', 76.30, 77.42),
    ('b', 85.04, 86.25),
    ('b', 86.55, 87.98),
    ('b', 88.28, 89.64),
    ('b', 89.87, 91.20),
]

NO_SNAP = {(s_, a_) for s_, a_, b_ in RAW}                                 # boundaries already sit in clean silence
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
