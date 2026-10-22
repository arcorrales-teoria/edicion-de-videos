"""IMG_9088 · Darshita Patankar ("Design is Dead") y la atención. Take cleaned FIRST with DeepFilterNet3 (src9088c.wav);
cuts on the clean envelope: pauses < -45 dB longer than 0.28 s trimmed to 0.16 s. Removed (REMOVE): "literalmente" x4, "oe, pucha",
"y esa vaina eventualmente va a suceder que todo", the repeated "le están lloviendo ofertas… obviamente no, no", the whole first try
"no sé, uno por qué no debería estar haciendo todo lo posible… va a lograrla" (keeps "¿Y por qué uno no está haciendo…?"), "le fue"."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_9088.MOV'}
WAVS = {'a': 'src9088c.wav'}
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
    ('a', 0.20, 0.45),
    ('a', 1.22, 4.48),
    ('a', 5.11, 6.66),
    ('a', 6.85, 9.02),
    ('a', 9.37, 9.64),
    ('a', 11.10, 12.42),
    ('a', 12.96, 14.20),
    ('a', 14.33, 16.47),
    ('a', 16.65, 18.28),
    ('a', 18.52, 19.86),
    ('a', 20.67, 21.44),
    ('a', 21.57, 25.28),
    ('a', 25.62, 27.54),
    ('a', 27.75, 30.97),
    ('a', 31.62, 33.40),
    ('a', 34.70, 39.18),
    ('a', 39.71, 40.65),
    ('a', 40.99, 42.53),
    ('a', 43.40, 45.44),
    ('a', 45.63, 45.95),
    ('a', 47.52, 48.16),
    ('a', 48.31, 49.31),
    ('a', 49.67, 52.29),
    ('a', 52.41, 54.33),
    ('a', 61.00, 65.40),
    ('a', 65.64, 67.18),
    ('a', 68.10, 69.63),
    ('a', 69.89, 72.52),
    ('a', 72.81, 73.42),
    ('a', 87.08, 89.94),
    ('a', 90.18, 91.22),
    ('a', 91.92, 93.80),
    ('a', 94.16, 95.95),
    ('a', 96.16, 97.22),
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
