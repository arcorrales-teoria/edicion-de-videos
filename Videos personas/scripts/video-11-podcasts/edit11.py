"""IMG_8930 (intro) + IMG_8931 (3 podcasts: 20VC, My First Million, David Senra). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'h': '/Users/acorrales/Downloads/IMG_8930.MOV', 'b': '/Users/acorrales/Downloads/IMG_8931.MOV'}
WAVS = {'h': 'src8930.wav', 'b': 'src8931.wav'}
RAW = [
    # --- intro (8930) ---
    ('h', 0.62, 3.65), ('h', 4.04, 5.11), ('h', 5.26, 7.59), ('h', 7.93, 9.61), ('h', 9.94, 12.99),   # Oiga ... tres recomendaciones de podcast
    ('h', 13.17, 14.66), ('h', 14.96, 17.18), ('h', 17.32, 19.71),                                     # que usted debería ... Así que aquí vamos.
    # --- 8931 ---
    ('b', 0.60, 2.30), ('b', 2.87, 4.20), ('b', 4.90, 6.49), ('b', 6.97, 8.39), ('b', 8.78, 9.48),   # Primero, 20 Minute VC ... las empresas
    ('b', 10.09, 13.35), ('b', 14.24, 14.75), ('b', 15.02, 15.49), ('b', 16.36, 17.08),               # de más rápido crecimiento ... como Uber (sin "y todo") y demás.
    ('b', 20.03, 20.66), ('b', 20.94, 23.76), ('b', 24.18, 28.82), ('b', 29.11, 31.26), ('b', 31.47, 33.71),   # Segundo, My First Million ...
    ('b', 34.10, 37.78), ('b', 38.12, 41.21),                                                          # Estos manes tienen el alfa absoluto ... escúchenlos a ellos,
    ('b', 43.47, 45.27), ('b', 45.97, 46.99), ('b', 47.16, 50.04), ('b', 50.30, 51.86), ('b', 52.14, 55.44),   # Y por último, David Senra ...
    ('b', 55.86, 59.20),                                                                               # Entonces, ya saben, si quieren más listas, comenten ...
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
HOOK_END = OFF[8]                       # edit time where the body (8931) starts
def seg_index(t):
    for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); s, a, b = SEGS[i]
    return s, min(a + t - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f (%.2f at 1.05x)' % (TOTAL, TOTAL / 1.05))
