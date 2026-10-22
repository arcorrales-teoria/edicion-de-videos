"""IMG_8938 · Colossus article on David Vélez / Nubank. Each keep range is one spoken unit between real pauses
(silencedetect -25 dB, double-checked on the energy envelope); boundaries are then snapped to the quietest nearby point."""
import os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRCS = {'a': '/Users/acorrales/Downloads/IMG_8938.MOV'}
WAVS = {'a': 'src8938.wav'}
# every pause in this take is real silence (checked on the energy envelope) -> keep every spoken unit, drop the pauses
RAW = [
    ('a', 0.29, 3.33),
    ('a', 3.73, 4.89),
    ('a', 5.26, 5.92),
    ('a', 6.38, 7.08),
    ('a', 7.74, 8.89),
    ('a', 9.48, 10.00),
    ('a', 10.13, 11.14),
    ('a', 11.63, 12.44),
    ('a', 12.77, 15.34),
    ('a', 15.63, 16.17),
    ('a', 16.31, 16.92),
    # ('a', 17.34, 18.62),   # (removed: false start 'de cómo luchó contra… bancos')
    # ('a', 18.96, 19.89),   # (removed: false start 'de cómo luchó contra… bancos')
    # ('a', 20.06, 20.25),   # (removed: false start 'de cómo luchó contra… bancos')
    ('a', 21.05, 23.10),
    ('a', 23.50, 26.66),
    ('a', 27.12, 28.08),
    ('a', 28.50, 28.84),
    ('a', 29.16, 30.02),
    ('a', 30.61, 31.37),
    ('a', 31.83, 32.19),
    ('a', 33.18, 34.39),
    ('a', 34.67, 35.52),
    ('a', 35.87, 36.60),
    ('a', 36.80, 37.81),
    ('a', 38.34, 38.67),
    ('a', 39.15, 40.06),
    ('a', 40.60, 41.22),
    ('a', 41.72, 42.70),
    ('a', 43.30, 44.02),
    ('a', 44.89, 47.61),
    ('a', 47.73, 48.58),
    ('a', 48.74, 49.68),
    ('a', 50.07, 50.59),
    ('a', 51.17, 51.52),
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
