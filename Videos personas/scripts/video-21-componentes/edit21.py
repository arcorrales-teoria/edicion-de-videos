"""IMG_9068 · "14 librerías para que tu web no parezca hecha con IA" (componentes para Claude). Pauses read on the energy
envelope (floor ~-29 dB)."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9068.MOV'}
WAVS = {'a': 'src9068s.wav'}
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
    ('a', 0.00, 12.30),                                               # Venga, si usted está haciendo páginas web con Claude… está haciendo la mitad del trabajo, porque lo más importante para Claude
    ('a', 12.50, 18.86), ('a', 19.28, 24.44), ('a', 24.56, 30.77),    # ahora mismo es tener componentes… para cuando necesita hacer tu proyecto o tu página web. ¿Cómo así que componentes? Venga, pues le explico: …no se vea hecha
    ('a', 31.23, V(34.44, 34.56)),                          # por Claude, sino que sea una página web profesional y real. ("literalmente" quitado)
    # 34.5-36.1 quitado: "y cómo así que componentes" (segunda vez)
    ('a', 36.10, 36.56), ('a', 36.80, 37.22), ('a', 37.60, 38.24), ('a', 38.50, 39.42), ('a', 39.86, 40.88), ('a', 41.00, 43.52),   # botones, shaders, animaciones de texto, alineaciones, cómo está estructurada la página web,
    # 43.52-47.04 quitado: "cómo va a ser estructurada absolutamente todo dentro de eso" (repite)
    ('a', V(46.98, 47.06), 50.40), ('a', 51.14, 53.30),               # las transiciones y todo ese montón de cosas que hay alrededor de hacer buenas páginas web.
    # 53.30-56.10 quitado: "que hacen que realmente tu proyecto se vea" (frase sin terminar)
    ('a', 56.10, 59.44), ('a', 59.76, 61.00), ('a', 61.40, 64.04),   # ¿Y cuáles los utilizo yo? Por acá les voy a dejar una lista… en los comentarios un link donde van a encontrar todo. Lo único que tienen que hacer
    ('a', V(65.86, 65.92), 68.22), ('a', 68.58, 71.66), ('a', 72.16, 74.58), ('a', 75.12, 81.88),   # es entrar, ver el componente que les guste, copiárselo y pegárselo a Claude Code, y él va a hacer exactamente lo mismo… así la haya hecho una AI. ("literalmente" x2 quitados)
    ('a', 82.30, 89.03), ('a', 89.45, 92.70),                         # Y si quieren realmente tener un buen diseño, contraten a …, la mejor diseñadora que conozco, y no tienen ninguno de esos problemas como los estoy teniendo yo. Ya saben.
]

NO_SNAP = {('a', 0.00), ('a', 89.45), ('a', 31.23), ('a', 36.10), ('a', 61.40), ('a', 24.56), ('a', 68.58), ('a', 72.16)}
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
