SRCF = {'h': '/Users/acorrales/Downloads/IMG_8851.MOV', 'm': '/Users/acorrales/Downloads/IMG_8850.MOV'}
KEEP = [('h', 0.0, 4.36), ('m', 0.62, 71.50)]
SIL = {'h': [tuple(map(float, l.split())) for l in open('sil_a51.txt')],
       'm': [tuple(map(float, l.split())) for l in open('sil_a50.txt')]}
PAD = 0.05
def segments():
    out = []
    for src, a, b in KEEP:
        cur = a
        for s, e in SIL[src]:
            if e - s < 0.2: continue
            cs, ce = max(s + PAD, a), min(e - PAD, b)
            if ce - cs > 0.08 and cs > cur:
                out.append((src, cur, cs)); cur = ce
        if b - cur > 0.05: out.append((src, cur, b))
    return [s for s in out if s[2] - s[1] > 0.12]
SEGS = segments()
OFF = []; acc = 0
for s, a, b in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
def seg_index(t):
    for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
        if t < o + b - a: return i
    return len(SEGS) - 1
def src_of(t):
    i = seg_index(t); s, a, b = SEGS[i]
    return s, min(a + t - OFF[i], b)
def M(src, t):
    for (s, a, b), o in zip(SEGS, OFF):
        if s != src: continue
        if t < a: return o
        if t <= b: return o + t - a
    return TOTAL
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f' % TOTAL)
