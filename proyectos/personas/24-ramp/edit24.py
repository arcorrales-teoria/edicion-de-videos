"""IMG_9094 · Ramp ("New on Ramp: Q3") y construir en público: Croma y AbacatePay. Take cleaned FIRST with DeepFilterNet3
(src9094c.wav); cuts on the clean envelope (pauses < -45 dB > 0.28 s trimmed to 0.16 s). Removed: false start "si usted tiene una
startup, tienes que…", "diferente a lo que hace", "esos manes de Ramp" (repeat), the abandoned "no son el mega feature que va a hacer que
la gente o no va a hacer el", "por alguna", "lo que va a hacer es que ya como todo su sistema, todo se va a volver", "todo y",
"y literalmente eso", five "literalmente"."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9094.MOV'}
WAVS = {'a': 'src9094c.wav'}
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
    ('a', 2.47, 3.52),
    ('a', 3.70, 5.89),
    ('a', 6.02, 7.30),
    ('a', 7.52, 8.68),
    ('a', 8.92, 8.98),
    ('a', 10.17, 11.56),
    ('a', 12.02, 13.99),
    ('a', 14.13, 15.09),
    ('a', 15.97, 17.40),
    ('a', 18.98, 20.35),
    ('a', 20.55, 21.97),
    ('a', 22.40, 23.48),
    ('a', 24.04, 25.81),
    ('a', 26.02, 28.99),
    ('a', 29.49, 29.82),
    ('a', 30.05, 31.06),
    ('a', 36.58, 37.17),
    ('a', 37.38, 41.56),
    ('a', 41.79, 46.04),
    ('a', 46.84, 47.64),
    ('a', 47.80, 48.85),
    ('a', 49.03, 52.13),
    ('a', 52.27, 53.33),
    ('a', 57.04, 63.34),
    ('a', 63.61, 64.86),
    ('a', 65.10, 67.91),
    ('a', 68.06, 69.60),
    ('a', 70.08, 71.49),
    ('a', 71.77, 75.91),
    ('a', 76.09, 77.98),
    ('a', 78.80, 81.45),
    ('a', 81.65, 84.42),
    ('a', 84.57, 85.68),
    ('a', 85.86, 87.32),
    ('a', 87.46, 89.52),
    ('a', 89.77, 92.58),
    ('a', 92.71, 99.54),
    ('a', 99.71, 100.57),
    ('a', 100.80, 102.97),
    ('a', 103.11, 105.70),
    ('a', 107.95, 110.30),
    ('a', 110.50, 111.92),
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
