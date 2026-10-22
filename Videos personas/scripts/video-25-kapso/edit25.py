"""IMG_9102 · Kapso (WhatsApp para negocios y para developers, manejable desde Claude). Take cleaned FIRST with DeepFilterNet3
(src9102c.wav); cuts on the clean envelope. Removed: four "literalmente", the doubled "tu, tu bot", "y literalmente pues",
"te puede", the abandoned "como si fuera un", and the retake "puedes montar todo todo y tener… un bot de WhatsApp para tus
clientes" (keeps the second, complete take)."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9102.MOV'}
WAVS = {'a': 'src9102c.wav'}
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
    ('a', 0.12, 2.52),
    ('a', 2.64, 4.45),
    ('a', 4.62, 6.67),
    ('a', 6.94, 7.82),
    ('a', 8.05, 10.01),
    ('a', 10.26, 11.74),
    ('a', 12.06, 13.40),
    ('a', 13.83, 14.98),
    ('a', 15.39, 17.50),
    ('a', 17.75, 18.61),
    ('a', 18.87, 19.84),
    ('a', 20.44, 21.34),
    ('a', 21.56, 23.70),
    ('a', 23.91, 25.24),
    ('a', 25.52, 27.27),
    ('a', 27.74, 28.54),
    ('a', 29.39, 31.04),
    ('a', 31.21, 32.57),
    ('a', 32.79, 39.93),
    ('a', 42.32, 43.11),
    ('a', 43.51, 45.15),
    ('a', 45.38, 47.78),
    ('a', 47.91, 48.80),
    ('a', 49.45, 52.54),
    ('a', 52.71, 53.51),
    ('a', 53.83, 55.66),
    ('a', 56.96, 58.89),
    ('a', 59.06, 60.19),
    ('a', 60.53, 64.83),
    ('a', 65.09, 66.79),
    ('a', 74.98, 78.35),
    ('a', 78.90, 79.75),
    ('a', 79.88, 82.42),
    ('a', 82.82, 83.61),
    ('a', 83.75, 85.71),
    ('a', 85.90, 87.84),
    ('a', 88.24, 88.79),
    ('a', 89.08, 90.09),
]

NO_SNAP = {(s_, a_) for s_, a_, b_ in RAW}                                 # every boundary sits in clean silence already: no snapping
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
