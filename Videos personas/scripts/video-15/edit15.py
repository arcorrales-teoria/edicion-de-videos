"""IMG_8957 · treg.to (herramientas para tu Claude). The CTA line is moved to the end. Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_8957.MOV'}
WAVS = {'a': 'src8957.wav'}
import wave as _w, numpy as _np
_wf = _w.open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'src8957.wav'))
_sr = _wf.getframerate(); _x = _np.frombuffer(_wf.readframes(_wf.getnframes()), _np.int16).reshape(-1, 2).astype(_np.float32).mean(1) / 32768
def V(lo, hi):
    """quietest 20 ms point between lo and hi (a word boundary inside connected speech)"""
    ts = _np.arange(lo, hi, 0.005)
    return float(min(ts, key=lambda t: _np.sqrt((_x[int(t * _sr):int((t + 0.02) * _sr)] ** 2).mean())))
RAW = [
    ('a', 0.47, 3.10), ('a', 3.44, 6.88),                         # Le vengo con la mejor herramienta para que su Claude tenga superpoderes…
    # 7.22-12.02 quitado: primer intento "resulta que hay una página que se llama treg.to… se llama"
    ('a', 12.29, 14.37),                                          # Resulta que hay una página que se llama treg.to
    ('a', 14.58, 15.82), ('a', 16.30, V(18.25, 18.50)),           # y lo que hace esta vaina es darle herramientas a su Claude.
    # "¿Cómo así, qué herramienta? Entonces" quitado
    ('a', 19.82, 22.42), ('a', 22.88, 24.57), ('a', 24.70, 26.21),   # Si quieren que su Claude sea un experto prospectando… venderles.
    # 26.75-30.53 quitado: arranque en falso "literalmente lo que él tiene es un montón de…"
    ('a', 31.14, 32.81), ('a', 33.10, 34.17), ('a', 34.45, 36.15), ('a', 36.43, 38.67),   # lo que él hace es que tiene un montón de apps… Apollo, Lusha, Instantly
    ('a', 39.05, 41.81), ('a', 41.93, V(44.45, 44.78)),           # va y busca… te lo arroja. Esto es una vaina loquísima.
    ('a', V(44.45, 44.78), 47.32), ('a', 47.71, 50.26), ('a', 50.38, 51.53), ('a', 51.84, 55.16),   # Lo mismo… scrap de Instagram, TikTok, Twitter…
    # "Y esa vaina es una locura porque literalmente" quitado
    ('a', 57.89, 59.99), ('a', 60.34, 63.57), ('a', 63.70, 64.69), ('a', 64.87, 65.70), ('a', 65.93, 67.04),   # Hay muchas que son baratas… y puedes volverte
    ('a', V(69.25, 69.40), 70.33),                                # (sin "a volver volver") la mejor persona
    ('a', 70.59, 73.02), ('a', 73.15, 73.75), ('a', 73.93, 75.88), ('a', 76.01, 76.77),   # en tu área de trabajo… lo que él hace es enrutar
    ('a', 77.03, V(77.62, 77.76)), ('a', 78.50, 80.72), ('a', 80.84, 82.14), ('a', 82.40, 82.79), ('a', 82.96, V(83.55, 84.05)),   # para saber qué es lo mejor… game changer.
    ('a', V(87.80, 88.25), 89.11), ('a', 89.29, V(90.90, 91.15)), ('a', 92.03, 95.81), ('a', 96.06, 96.61), ('a', 96.98, 98.33),   # Y lo más fácil… quedan con superpoderes.
    ('a', V(83.55, 84.05), 86.07),                                # Así que ya saben, utilícenlo. Por acá les dejo todo.  (movido al final)
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
