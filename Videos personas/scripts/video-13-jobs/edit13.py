"""IMG_8946 · job-status (centraliza tu búsqueda de trabajo). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_8946.MOV'}
WAVS = {'a': 'src8946.wav'}
# all pauses are real silence (energy checked); keep every spoken unit except the false start / repeats / sign-off
RAW = [
    ('a', 0.47, 1.19),
    # ('a', 2.17, 2.84),   # (quitado: venga)
    # ('a', 3.56, 4.14),   # (quitado: si usted, (arranque en falso))
    ('a', 4.76, 6.60),
    ('a', 7.09, 7.33),
    ('a', 7.47, 7.74),
    ('a', 7.97, 8.76),
    ('a', 9.04, 11.42),
    ('a', 11.77, 12.94),
    ('a', 13.57, 15.79),
    ('a', 16.06, 16.84),
    ('a', 16.96, 18.76),
    ('a', 19.02, 19.85),
    ('a', 20.13, 21.99),
    ('a', 22.46, 23.96),
    ('a', 24.27, 26.57),
    ('a', 26.87, 27.48),
    ('a', 27.80, 29.77),
    ('a', 30.03, 30.76),
    ('a', 31.03, 31.98),
    ('a', 32.28, 33.83),
    ('a', 34.55, 35.63),
    ('a', 35.85, 37.61),
    ('a', 37.90, 40.23),
    ('a', 40.61, 43.17),
    ('a', 43.52, 43.93),
    ('a', 44.40, 45.19),
    ('a', 45.37, 46.16),
    ('a', 46.43, 47.88),
    ('a', 48.01, 48.74),
    ('a', 49.08, 52.27),
    ('a', 52.46, 54.08),
    ('a', 54.38, 57.14),
    ('a', 57.50, 58.21),
    ('a', 58.36, 58.89),
    ('a', 59.12, 59.83),
    # ('a', 60.20, 60.88),   # (quitado: comenten (repetido))
    ('a', 61.36, 63.36),
    # ('a', 63.97, 64.93),   # (quitado: Gracias, adiós)
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
