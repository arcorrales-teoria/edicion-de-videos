"""IMG_8956 · "la técnica para que no se acabe tu plan de Claude" (chiste: no la tengo). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_8956.MOV'}
WAVS = {'a': 'src8956.wav'}
RAW = [
    ('a', 1.08, 1.66),                                   # Oiga,
    ('a', 3.12, 5.26), ('a', 5.57, 8.38), ('a', 8.57, 9.69), ('a', 10.13, 11.79),   # ...la mejor técnica ... todo el tiempo y todo momento,
    ('a', 12.79, 14.06),                                 # aquí se la voy a dar.
    # ('a', 14.92, 15.29),                               # (quitado: "Si os…" arranque en falso)
    ('a', 16.63, 17.47), ('a', 19.75, 21.27),            # Si usted quiere saber | qué tiene que hacer
    ('a', 21.67, 24.21), ('a', 24.45, 26.81), ('a', 27.01, 27.99),   # ... con un prompt utilizando Opus 5.5 y haciendo cualquier cosa,
    ('a', 29.06, 31.18),                                 # pues dígame, porque yo tampoco tengo ni idea.
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
