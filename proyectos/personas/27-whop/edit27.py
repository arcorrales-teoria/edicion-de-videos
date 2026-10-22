"""IMG_9115 + IMG_9116 · Whop (de revender sneakers a US$200M con Sequoia). Both takes cleaned FIRST with DeepFilterNet3
(src9115c / src9116c); cuts on the clean envelope. Removed: twelve "literalmente", "márica, Whop es lo que usted necesita si es un
coach, si es un…" (restart), the repeated "para cualquier mercado", "y los volvieron," (restart), "porque ese man les trajo y"
(abandoned), "que todos sus cursos y" (abandoned)."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9115.MOV', 'b': '/Users/acorrales/Downloads/IMG_9116.MOV'}
WAVS = {'a': 'src9115c.wav', 'b': 'src9116c.wav'}
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
    ('a', 0.00, 1.25),
    ('a', 2.27, 4.81),
    ('a', 5.05, 8.56),
    ('a', 8.90, 10.69),
    ('a', 10.81, 13.53),
    ('a', 13.78, 15.74),
    ('a', 16.27, 16.86),
    ('a', 17.09, 18.38),
    ('a', 18.53, 19.73),
    ('a', 19.86, 20.80),
    ('a', 21.64, 21.72),
    ('a', 28.17, 28.40),
    ('a', 28.96, 33.23),
    ('a', 33.35, 35.64),
    ('a', 35.76, 36.64),
    ('a', 37.70, 38.05),
    ('a', 38.21, 40.79),
    ('a', 41.14, 45.02),
    ('a', 45.20, 48.00),
    ('a', 49.18, 55.78),
    ('a', 56.03, 58.20),
    ('a', 58.35, 61.10),
    ('a', 61.29, 62.40),
    ('a', 63.13, 65.10),
    ('a', 67.02, 67.72),
    ('a', 67.90, 69.91),
    ('a', 70.15, 75.45),
    ('a', 75.58, 77.23),
    ('a', 77.81, 79.71),
    ('a', 79.93, 85.40),
    ('a', 87.67, 90.08),
    ('a', 90.23, 91.45),
    ('a', 91.59, 94.49),
    ('a', 94.69, 96.80),
    ('a', 97.22, 98.16),
    ('a', 98.36, 98.44),
    ('a', 99.44, 102.00),
    ('a', 103.48, 106.92),
    ('a', 107.28, 110.31),
    ('a', 112.89, 116.50),
    # IMG_9116: lo mejor es su marketing… invertiría en ellos
    ('b', 0.00, 5.94),
    ('b', 6.23, 7.25),
    ('b', 8.55, 12.53),
    ('b', 12.75, 13.48),
    ('b', 13.64, 15.95),
    ('b', 16.17, 16.42),
    ('b', 16.93, 20.93),
    ('b', 21.08, 23.60),
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
