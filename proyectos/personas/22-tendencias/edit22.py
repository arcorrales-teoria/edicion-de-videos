"""IMG_9070 (hook) + IMG_9069 · "Cómo ir 2 años por delante en Latinoamérica". Both takes are cleaned FIRST with DeepFilterNet3
(src9069c.wav / src9070c.wav); cuts read on the clean envelope: pauses < -45 dB longer than 0.28 s trimmed to 0.16 s; removals: the repeated
"con el tema de los cursos", "ya eso dejó de estar de moda", and four "literalmente"."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9069.MOV', 'b': '/Users/acorrales/Downloads/IMG_9070.MOV'}
WAVS = {'a': 'src9069c.wav', 'b': 'src9070c.wav'}
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
    # HOOK (IMG_9070): si usted quiere montarse en una tendencia… esa es la forma de hacer tendencias en Latinoamérica
    ('b', 0.14, 1.99),
    ('b', 2.96, 4.65),
    ('b', 4.96, 6.45),
    ('b', 6.73, 8.08),
    ('b', 8.27, 8.83),
    ('b', 9.33, 10.15),
    ('b', 10.28, 11.98),
    ('b', 12.17, 12.95),
    # IMG_9069: históricamente en LATAM… esa es la teoría de hoy
    ('a', 0.24, 2.99),
    ('a', 3.34, 4.16),
    ('a', 4.46, 4.81),
    ('a', 5.01, 7.89),
    ('a', 8.15, 9.80),
    ('a', 10.54, 11.79),
    ('a', 12.27, 14.81),
    ('a', 14.97, 17.17),
    ('a', 17.35, 18.98),
    ('a', 19.20, 20.62),
    ('a', 21.10, 23.71),
    ('a', 23.93, 25.50),
    ('a', 25.76, 27.25),
    ('a', 29.29, 31.85),
    ('a', 32.06, 39.51),
    ('a', 39.83, 40.86),
    ('a', 41.00, 41.58),
    ('a', 42.05, 44.00),
    ('a', 44.32, 45.43),
    ('a', 45.67, 47.06),
    ('a', 47.23, 49.66),
    ('a', 50.48, 53.37),
    ('a', 53.73, 54.36),
    ('a', 56.08, 57.53),
    ('a', 57.76, 59.19),
    ('a', 59.44, 60.43),
    ('a', 61.80, 65.64),
    ('a', 65.87, 67.79),
    ('a', 68.01, 69.92),
    ('a', 70.37, 72.36),
    ('a', 72.65, 75.08),
    ('a', 75.22, 75.69),
    ('a', 76.02, 76.95),
]

NO_SNAP = set()
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
