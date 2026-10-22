"""IMG_9008 + IMG_9009 · 2 personas de marketing para seguir (Héctor Serrano, Matt Swulinski). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9008.MOV', 'b': '/Users/acorrales/Downloads/IMG_9009.mov'}
WAVS = {'a': 'src9008.wav', 'b': 'src9009.wav'}
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
    # 9008 — 0.33-5.11 quitado: arranque en falso "Si usted está trabajando, si usted está estudiando o trabajando en marketing"
    ('a', 5.90, 8.36), ('a', 8.63, 10.34),                                  # Si usted está estudiando o está trabajando en algún área de marketing en alguna compañía,
    ('a', 10.84, 13.44), ('a', 13.78, 15.45), ('a', 15.58, 16.58), ('a', 16.81, 17.43), ('a', 17.55, 19.63),   # estas son las … que usted tiene que seguir…
    ('a', 20.18, 20.61), ('a', 20.89, V(22.05, 22.30)),                     # Primero, Héctor Serrano, ese man (sin "es…")
    ('a', 22.98, 24.94), ('a', 25.27, 29.05), ('a', 29.21, 30.49), ('a', 30.64, 32.14), ('a', 32.25, 34.23),   # fue el segundo empleado de Wispr Flow …
    # 34.57 "Segundo." quitado (se repite al inicio de 9009)
    ('b', 0.00, 0.48), ('b', 0.73, 2.24), ('b', 2.73, 3.52), ('b', 3.63, 5.69), ('b', 5.96, 7.81), ('b', 8.17, 9.36),   # Segundo, ese man, Matt Swulinski …
    # 9.75-11.67 quitado: "UGC, creadores UGC," (repetición)
    ('b', 11.96, 13.18), ('b', 13.49, 14.23), ('b', 14.40, 16.11),           # programas de creadores UGC, ads, de todo, de un montón de empresas.
    ('b', 16.56, 18.82), ('b', 19.02, 20.70), ('b', 21.27, 21.59), ('b', 21.72, 23.00), ('b', 23.34, 24.22), ('b', 24.62, 25.64),   # Y esta es la gente …
    # 26.34-29.45 + "en todo lo que está cambiando" quitado (repetía la idea)
    ('b', V(30.85, 31.10, 'b'), 32.76), ('b', 33.20, 35.06), ('b', 35.29, 36.95),   # porque marketing ahora mismo está cambiando tanto …
    ('b', 37.28, 38.42), ('b', 38.57, 39.17), ('b', 39.33, 40.21),           # Entonces ya sabes, estos dos manes, buenísimos, se los dejo ahí.
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
