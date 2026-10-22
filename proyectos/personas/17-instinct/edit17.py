"""IMG_9010 + IMG_9011 · Instinct (asistente personal que vive en WhatsApp). Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9010.MOV', 'b': '/Users/acorrales/Downloads/IMG_9011.MOV'}
WAVS = {'a': 'src9010.wav', 'b': 'src9011.wav'}
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
    ('a', 0.65, 3.28), ('a', 4.08, 4.69), ('a', 4.91, 5.37),            # Oiga, un amigo me acaba de mandar la invitación a Instinct y esto es una locura.
    # 5.66-8.44 quitado: arranques en falso "resulta de que esto es una app… que literalmente es…"
    ('a', 8.90, 12.90),                                                   # Resulta que esto es un agente que vive en WhatsApp… Instinct.
    ('a', 14.23, 16.00), ('a', 16.40, 16.69), ('a', 16.84, 18.97), ('a', 19.34, 21.41), ('a', 21.62, V(22.55, 22.95)),   # … te escribe como una persona.
    # "por ejemplo, les pongo un caso. Yo tenía una reunión, tú…" (primer intento) quitado
    ('a', 27.11, 28.96), ('a', 29.16, 32.50), ('a', 32.78, 33.96), ('a', 34.11, 35.90),   # Por ejemplo… me mandó un mensaje como "¡Hola Andrés!"
    # 36.55-38.28 quitado: "te hizo… Hola Andrés" (repetido)
    ('a', 38.55, 41.78), ('a', 41.98, 44.51),                             # te recuerdo que tienes que inscribirte… todo el tiempo está viendo cosas.
    ('a', 44.95, 45.64), ('a', 46.19, 49.45), ('a', 49.74, 50.37), ('a', 50.69, 52.33), ('a', 52.47, 54.03),   # Inclusive, un amigo… búscame los que estén más baratos.
    ('a', 54.29, 55.92), ('a', 56.20, 59.62), ('a', 59.94, 60.65), ('a', 61.76, 63.93), ('a', 64.15, 64.96), ('a', 65.20, 66.13),
    ('b', 0.18, 1.31), ('b', 1.45, 2.72), ('b', 3.46, 6.13), ('b', 6.51, 7.32), ('b', 7.81, 10.16), ('b', 10.47, 11.98),   # Lo mejor… para que lo empieces a utilizar hoy.
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
