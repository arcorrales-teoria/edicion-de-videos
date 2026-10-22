"""IMG_8913 (hook) + IMG_8914 (body, trimmed hard: it ran ~82 s). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_8913.mov', 'b': '/Users/acorrales/Downloads/IMG_8914.MOV'}
WAVS = {'a': 'src8913.wav', 'b': 'src8914.wav'}
RAW = [
    # --- hook (8913) ---
    ('a', 1.94, 2.70), ('a', 2.89, 3.98), ('a', 4.39, 5.82), ('a', 6.63, 6.97), ('a', 7.23, 9.11),   # ¿Qué tiene que ver un show de Broadway, un contador indio y una empresa de tarjetas corporativas?
    ('a', 9.33, 12.01),                                                                            # Pues resulta que esa es la estrategia de marketing que está utilizando Ramp.
    ('a', 12.34, 13.41),                                                                           # Y hoy te la vengo a explicar.   (title card)
    # --- body (8914) ---
    ('b', 2.075, 2.65), ('b', 3.23, 6.83),              # Ramp es una empresa de tarjetas corporativas como para controlar todo el gasto que tiene tu empresa
    ('b', 10.42, 11.26), ('b', 11.57, 13.04),           # y esos manes tienen una teoría súper bacana y es
    ('b', 13.71, 14.44), ('b', 14.68, 15.21),           # (sin "como") tenemos que hacer finance
    ('b', 15.57, 15.93), ('b', 16.19, 16.71), ('b', 17.16, 17.92), ('b', 18.34, 18.83), ('b', 19.21, 19.86),  # pero bien, como chévere, charro, chistoso
    ('b', 20.14, 22.49), ('b', 22.77, 23.95),           # y literalmente todas las estrategias que hacen esos manes son para eso. Entonces
    ('b', 27.94, 29.37), ('b', 29.55, 30.63),           # la letra del show de Broadway literalmente es
    ('b', 32.76, 35.19), ('b', 35.87, 38.28),           # (sin el primer "cómo") cómo ellos ayudan a las empresas a mejorar su gasto corporativo con sus tarjetas
    ('b', 41.33, 42.86), ('b', 43.20, 44.18), ('b', 44.46, 45.54),   # uno puede hacer cualquier cosa a nivel de marketing, sí y sólo
    ('b', 45.97, 46.40), ('b', 47.28, 48.22),           # si tiene (sin "realmente como") ese nivel
    ('b', 48.54, 48.82), ('b', 49.10, 49.69), ('b', 50.12, 50.94),   # de llevar (sin "como") tu mensaje
    ('b', 51.54, 52.74),                                # a todo lo que vayas a hacer
    ('b', 53.03, 56.79), ('b', 57.11, 58.49), ('b', 58.72, 60.82), ('b', 61.11, 61.71),   # Kumar ... utiliza Ramp
    ('b', 64.89, 67.53), ('b', 67.89, 68.36), ('b', 68.49, 69.21),   # me parece de las mejores estrategias de marketing que hay ahora mismo
    ('b', 69.52, 71.68), ('b', 71.96, 73.20), ('b', 73.33, 74.98), ('b', 75.27, 76.02),   # sígalos ... que he podido ver
]

NO_SNAP = {('b', 2.075)}            # 'de que|Ramp' is connected speech: start exactly on the R
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
        a2 = min(np.arange(a - 0.06, a + 0.03, 0.005), key=lambda t: vb(s, t))
        b2 = min(np.arange(b - 0.03, b + 0.06, 0.005), key=lambda t: vb(s, t))
        out.append((s, float(a2), float(b2)))
    return out
SEGS = _snap(RAW)
OFF = []; acc = 0
for s, a, b in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
HOOK_END = OFF[7]                       # edit time where the body (8914) starts
def seg_index(t):
    for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); s, a, b = SEGS[i]
    return s, min(a + t - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f (%.2f at 1.05x)' % (TOTAL, TOTAL / 1.05))
