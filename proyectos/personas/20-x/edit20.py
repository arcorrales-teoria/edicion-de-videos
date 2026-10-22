"""IMG_9042 · "La red social que te da una ventaja 10x" (Twitter / X para estar en contexto). Outdoor take: pauses read on the
energy envelope (floor ~-34 dB)."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9042.MOV'}
WAVS = {'a': 'src9042s.wav'}
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
    ('a', 0.00, 6.01),                                                # Venga, si usted quiere estar en contexto de lo que está pasando ahora mismo en el mundo,
    ('a', 6.53, 12.94), ('a', 13.36, 14.73), ('a', 15.24, V(20.20, 20.40)),   # no en temas de noticias… sino en temas de tecnología… marketing, de ventas y todos los playbooks, usted debería estar en Twitter, o X pa' los amigos.
    ('a', V(22.02, 22.10), 24.33), ('a', 25.08, 29.87), ('a', 30.32, 32.88), ('a', 33.69, V(35.36, 35.44)),   # Estar en Twitter te da por ahí una ventaja 10x… donde toda la gente más crack está publicando todo, y donde todo lo que está pasando en el mundo ("literalmente" quitado)
    ('a', V(35.82, 35.88), 37.32), ('a', 37.84, 39.36), ('a', 39.72, 44.40), ('a', 44.80, 45.12), ('a', 45.22, V(46.44, 46.60)),   # se concentra ahí. Entonces, si usted quiere estar por delante del mundo, ya sabe: tiene que estar en Twitter. Yo les dejo una lista por acá de gente que yo sigo que ("literalmente" quitado)
    ('a', V(47.12, 47.18), V(47.90, 48.10)),                          # solo tiran alfa. ("entonces ya saben" quitado: cierra en "alfa")
]

NO_SNAP = {('a', 0.00)}
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
