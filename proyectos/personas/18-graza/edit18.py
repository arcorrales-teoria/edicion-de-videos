"""IMG_9027 (hook) + IMG_9025 · Graza (cómo volvieron el aceite de oliva una marca increíble). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9025.MOV', 'b': '/Users/acorrales/Downloads/IMG_9027.MOV'}
WAVS = {'a': 'src9025s.wav', 'b': 'src9027s.wav'}
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
    # HOOK (IMG_9027, grabado después): reemplaza el arranque "Los mejores fundadores… lo vuelven increíble" de IMG_9025
    ('b', 0.19, 3.96), ('b', 4.28, 6.93), ('b', 7.25, 8.52),           # Estas son marcas que la están rompiendo… si trabaja en mercadeo. Número uno: Graza.
    # IMG_9025 0.00-17.45 quitado: arranques en falso, el hook viejo y "esta es la historia de Graza" (ya lo dice el hook)
    ('a', 17.45, 18.44), ('a', 19.01, 19.88), ('a', 20.14, 22.68),    # ¿Qué es Graza? Es una marca de aceite de oliva, así como lo escuchan, aceite de oliva. ("literalmente" quitado)
    ('a', 23.00, V(23.14, 23.22)), ('a', V(24.06, 24.12), 24.63),     # Pero aceite de oliva … ("aceite de oliva, ¿cómo?" quitado)
    ('a', 26.07, 26.55), ('a', 26.81, 29.74),                         # … bacano, que dan ganas de comprar, lo que tú ves la botella y dices "ve, eso es chévere". ("chévere" repetido quitado)
    ('a', 30.56, 34.06),                                    # La botella es como un squish, o sea tú la puedes apretar donde sale el aceite de oliva. ("y literalmente" quitado)
    ('a', V(34.88, 34.98), 35.90),                                    # El fundador se inspiró ("y literalmente" quitado)
    ('a', 36.50, 37.72), ('a', 37.96, 39.37), ('a', 39.76, 40.62),    # un día en su ducha, que veía cómo exprimía el shampoo en el baño.
    ('a', 40.93, 41.31), ('a', 42.04, 43.07),                         # Entonces creó una marca ("literalmente se me han" quitado)
    ('a', 43.40, 46.72),                                              # aspiracional, bonita, con una esencia increíble,
    ('a', 47.07, 49.56), ('a', 49.93, 52.89),                         # diferente a todas las marcas tradicionales… o sea tú ves un aceite de oliva normal y todas son iguales,
    ('a', 53.20, 56.23),                                              # la misma botella de vidrio, mismo color, absolutamente todo.
    ('a', 56.44, 57.88), ('a', 58.19, 59.45), ('a', 59.78, 60.80),    # Y eso es lo que dijeron: venga, ¿qué pasa si nosotros le metemos taste,
    ('a', 61.07, 63.19), ('a', 63.39, 65.19), ('a', 65.49, 66.37),    # le metemos un brand y le metemos una narrativa bacana a un producto que todo el día utilizan, el aceite de oliva?
    # 66.37-68.28 quitado: "y literalmente"
    ('a', 68.28, 70.25), ('a', 70.44, 72.03),                         # Así fue como lo lograron y esos manes son enormes en Estados Unidos.
    ('a', 72.33, 72.59), ('a', 72.88, 74.15), ('a', 74.41, 77.03),    # Son ahora mismo el consumer brand más importante y más grande de Estados Unidos.
    ('a', V(78.00, 78.10), 78.45), ('a', 78.81, 80.07), ('a', 80.64, 82.53),   # Hay una oportunidad muy grande en ver cualquier cosa que uno está haciendo. ("y literalmente" quitado)
    ('a', 83.03, 85.56),                                              # O sea, uno puede ir a una vitrina de cualquier supermercado
    ('a', V(86.64, 86.74), 87.00), ('a', 87.46, 88.10), ('a', 88.49, 88.90), ('a', 89.41, 90.61),   # ver y pensar: ¿por qué esto es todo igual? ("y literalmente" quitado)
    ('a', 91.16, 92.48),                                              # ¿Qué pasa si yo lo haría diferente?
    ('a', 92.79, 93.84), ('a', 94.58, 95.39), ('a', 95.82, 96.56), ('a', 96.91, 97.66),   # Y ahí es donde está la verdadera oportunidad de crear valor. ("la realidad" quitado)
]

NO_SNAP = {('a', 19.01), ('a', 30.56), ('a', 40.93), ('a', 42.04), ('a', 92.79), ('a', 94.58)}
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
