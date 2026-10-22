import json
KEEP = [(0.88, 8.30), (16.13, 27.25), (27.25, 32.18), (34.32, 37.90), (37.90, 47.95),
        (48.72, 50.00), (50.25, 58.15), (58.30, 71.05), (71.05, 77.40)]
SIL = [tuple(map(float, l.split())) for l in open('sil.txt')]
PAD = 0.05
def segments():
    out = []
    for a, b in KEEP:
        cur = a
        for s, e in SIL:
            if e - s < 0.2: continue
            cs, ce = max(s + PAD, a), min(e - PAD, b)
            if ce - cs > 0.08 and cs > cur:
                out.append((cur, cs)); cur = ce
        if b - cur > 0.05: out.append((cur, b))
    # merge touching
    m = []
    for s in out:
        if m and abs(m[-1][1] - s[0]) < 0.02: m[-1] = (m[-1][0], s[1])
        else: m.append(s)
    return [s for s in m if s[1] - s[0] > 0.12]
SEGS = segments() + [(77.40, 77.95)]  # tail beat for end card
OFF = []; acc = 0
for a, b in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
def M(t):
    """source time -> output time (times inside cut gaps snap to next kept segment)"""
    for (a, b), o in zip(SEGS, OFF):
        if t < a: return o
        if t <= b: return o + t - a
    return TOTAL
def seg_index(tout):
    for i, ((a, b), o) in enumerate(zip(SEGS, OFF)):
        if tout < o + b - a: return i
    return len(SEGS) - 1
def src_of(tout):
    i = seg_index(tout); a, b = SEGS[i]
    return min(a + tout - OFF[i], b)
if __name__ == '__main__':
    print(len(SEGS), 'segments, total %.2f s' % TOTAL)
    for (a, b), o in zip(SEGS, OFF): print('%6.2f-%6.2f -> %6.2f  (%.2f)' % (a, b, o, b - a))
