"""Face-aware framing for the speaker panel: never cut the head.
Uses Apple Vision face boxes (tools/face.swift, sampled at 6 fps, normalized top-left coords)."""
import numpy as np

class FaceTrack:
    def __init__(self, path, fps=6.0, sw=1440, sh=2560):
        rows = [l.split() for l in open(path) if l.strip()]
        self.t = np.array([(int(r[0]) - 1) / fps for r in rows])
        b = np.array([[float(v) for v in r[1:]] for r in rows])
        good = ~np.isnan(b).any(1)
        for k in range(4):                      # fill gaps by interpolation
            b[~good, k] = np.interp(self.t[~good], self.t[good], b[good, k])
        self.b = b * np.array([sw, sh, sw, sh]); self.sw, self.sh = sw, sh

    def box(self, src_t, lo=None, hi=None, win=0.4):
        """smoothed face box (x, y, w, h in source px) around src_t, optionally limited to one take [lo, hi]"""
        a, b = src_t - win, src_t + win
        if lo is not None: a = max(a, lo)
        if hi is not None: b = min(b, hi)
        m = (self.t >= a) & (self.t <= b)
        if not m.any(): m = np.abs(self.t - src_t) == np.abs(self.t - src_t).min()
        return np.median(self.b[m], axis=0)

def head_crop(face, zoom, panel=(1080, 960), sw=1440, sh=2560, top_air=0.07, chin_max=0.90):
    """crop box that keeps the whole head: hair top `top_air` below the panel top; opens up if the chin would fall out"""
    fx, fy, fw, fh = face
    head_top = fy - 0.30 * fh                   # Vision boxes start at the brows/forehead; add room for hair
    chin = fy + fh
    pw, ph = panel
    z = zoom
    for _ in range(12):
        cw = sw / z; ch = cw * ph / pw
        if ch > sh: ch = sh; cw = ch * pw / ph
        y0 = head_top - top_air * ch
        if chin <= y0 + chin_max * ch or z <= 1.0: break
        z = max(1.0, z - 0.05)
    x0 = fx + fw / 2 - cw / 2
    x0 = min(max(x0, 0), sw - cw); y0 = min(max(y0, 0), sh - ch)
    return (x0, y0, x0 + cw, y0 + ch)
