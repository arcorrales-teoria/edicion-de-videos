"""IMG_8927 (hook) + IMG_8925 + IMG_8926 (tools: UIMaxxing, Arc, Cult UI). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'h': '/Users/acorrales/Downloads/IMG_8927.MOV', 'a': '/Users/acorrales/Downloads/IMG_8925.MOV', 'b': '/Users/acorrales/Downloads/IMG_8926.MOV'}
WAVS = {'h': 'src8927.wav', 'a': 'src8925.wav', 'b': 'src8926.wav'}
RAW = [
    # --- hook (8927) ---
    ('h', 0.42, 3.99), ('h', 4.23, 6.30), ('h', 6.60, 8.18), ('h', 8.43, 9.24),   # Pilas, estas son tres herramientas ... hecho por un diseñador.
    ('h', 9.50, 11.70),                                                            # El último es el mejor, así que quédense.   (title card)
    # --- 8925 (sin la intro: repetía el hook) ---
    ('a', 10.43, 13.14), ('a', 13.74, 15.48), ('a', 15.74, 17.10), ('a', 17.24, 17.40),   # La primera, UIMaxxing ... de los que ustedes quieran
    ('a', 17.58, 18.09), ('a', 18.37, 19.21), ('a', 19.71, 19.87), ('a', 20.06, 22.44),   # cards, chatbots, procesos de cards, lo que ustedes quieran
    ('a', 22.64, 25.26), ('a', 25.56, 27.32),                                              # lo tienen acá, buenísima, es gratis, ... lo único que tienen que hacer
    ('a', 28.43, 30.65), ('a', 30.93, 31.31),                                              # (sin "pegarle un,") pegarle el siguiente código a Claude Code,
    ('a', 32.38, 33.37),                                                                   # (sin "importante,") y él va a hacer todo.
    ('a', 33.53, 35.25), ('a', 35.52, 37.64), ('a', 37.79, 38.56), ('a', 38.70, 39.84),   # Segunda, Arc ... son los componentes,
    ('a', 40.09, 40.93), ('a', 41.24, 41.66), ('a', 41.90, 46.27),                         # los botones, las interacciones ... demasiado bien hecho.
    # --- 8926 ---
    ('b', 0.02, 0.79), ('b', 0.95, 4.64), ('b', 4.88, 7.07), ('b', 7.40, 8.21), ('b', 8.65, 11.32),   # Tercera, Cult UI ... lo van a hacer.
    ('b', 11.73, 13.18), ('b', 13.68, 15.05), ('b', 15.56, 16.68), ('b', 16.96, 18.17), ('b', 18.39, 20.85),
    ('b', 21.13, 21.85), ('b', 22.13, 24.57), ('b', 25.01, 25.49), ('b', 25.83, 26.79),
    ('b', 26.99, 27.46), ('b', 27.83, 29.54), ('b', 29.71, 30.45),                         # Entonces ya saben, comenten ... y les mando más.
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
HOOK_END = OFF[5]                       # edit time where the body (8925) starts
def seg_index(t):
    for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); s, a, b = SEGS[i]
    return s, min(a + t - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f (%.2f at 1.05x)' % (TOTAL, TOTAL / 1.05))
