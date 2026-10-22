"""IMG_9043 (hook) + IMG_9044 · Tesla Roadster ("el mejor lanzamiento del año"). Outdoor take with steady background noise:
pauses were read on the energy envelope (floor ~-22 dB) instead of silencedetect. Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9043.MOV', 'b': '/Users/acorrales/Downloads/IMG_9044.MOV'}
WAVS = {'a': 'src9043s.wav', 'b': 'src9044s.wav'}
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
    ('a', 0.30, 4.30),                                                # Oiga, literalmente Elon acaba de romper el internet ahora mismo con esa vaina. (el "literalmente" del hook se deja: sin pausa limpia antes de "Elon")
    ('b', 0.04, 2.96),                                                # Y es que ayer lanzaron el Tesla Roadster
    ('b', 2.97, 3.63), ('b', V(4.52, 4.68, 'b'), 7.99), ('b', 8.21, 9.62),          # y lo mejor: el auto casi que puede volar, y es como lo más cercano que tenemos a autos voladores. (pausa larga y "si" quitados)
    ('b', 9.69, 13.50),                                               # Por acá les dejo varios memes y varias cosas que están pasando alrededor de eso.
    # 13.50-16.48 quitado: "pero sobre todo lo mejor de todo eso"
    ('b', 16.48, V(23.86, 24.00, 'b')),                               # Y lo mejor que tiene Elon es que entiende demasiado bien cómo hacer que absolutamente todo el santo mundo hable de usted.
    ('b', 25.14, 30.70),                                              # Ese es el mayor superpoder de Elon, más allá de que el man construye de todo y es un genio absoluto. ("literalmente" quitado)
    ('b', 30.72, V(35.58, 35.68, 'b')), ('b', V(37.12, 37.22, 'b'), 39.00),   # Si usted sabe cómo hacer que la gente hable de usted, que usted se vuelva viral, ya tiene el 99% ganado. ("literalmente" quitado)
    ('b', V(39.78, 39.86, 'b'), 44.08),                               # Eso es lo más increíble que tiene Elon, y que entiende demasiado bien ("literalmente" quitado)
    ('b', 44.96, 47.80), ('b', 48.15, 52.26),                         # sobre todo cómo volverse viral a nivel de memes, a nivel de noticias, a nivel de todo. Entonces es un 360 muy bueno de la viralidad,
    ('b', V(52.86, 53.00, 'b'), 55.12), ('b', 56.48, 58.62),          # ese man, para cada lanzamiento que hace, todo el mundo está hablando de él, todo el mundo hace un meme de él. ("que literalmente" y "literalmente" quitados)
    # 58.62-60.58 quitado: "entonces es increíble"
    ('b', 60.58, 65.20),                                              # Y verdad que el producto es una locura, es de los mejores lanzamientos de producto que yo vi en mi vida.
]

NO_SNAP = {('b', 0.04)}
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
