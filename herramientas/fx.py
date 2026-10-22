"""Shared helpers for Andrés's video edits: text rendering, easing, HDR (HLG) + SDR compositing, IO.
Standalone (no dependency on per-video scripts). Vive en herramientas/fx.py."""
import ctypes.util as _u
_f = _u.find_library
_u.find_library = lambda n: '/opt/homebrew/lib/libcairo.2.dylib' if 'cairo' in n else _f(n)
import cairocffi as cairo
import numpy as np, math, subprocess
from PIL import Image, ImageFont, ImageDraw, ImageFilter

_scale = cairo.Context.scale
cairo.Context.scale = lambda self, sx, sy=None: _scale(self, max(sx, 1e-3), max(sx if sy is None else sy, 1e-3))

W, H, FPS = 1080, 1920, 30
SW, SH = 1440, 2560

# ---------- easing ----------
def c01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def prog(t, a, d): return c01((t - a) / d)
def expo_out(x): x = c01(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def eio(x): x = c01(x); return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eo(x): x = c01(x); return 1 - (1 - x) ** 3

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
def rgba(ctx, c, a=None): ctx.set_source_rgba(c[0], c[1], c[2], c[3] if a is None else a)

# ---------- text -> cairo surface (cached; tracking in em; optional soft shadow) ----------
def pil_surface(img):
    a = np.asarray(img.convert('RGBA')).astype(np.float32); al = a[..., 3:4] / 255.0
    bgra = np.empty(a.shape, np.uint8)
    bgra[..., 0] = (a[..., 2] * al[..., 0]); bgra[..., 1] = (a[..., 1] * al[..., 0])
    bgra[..., 2] = (a[..., 0] * al[..., 0]); bgra[..., 3] = a[..., 3]
    bgra = np.ascontiguousarray(bgra)
    return cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, img.width, img.height, img.width * 4), bgra

_tc = {}
def T_(txt, font, size, col=(1, 1, 1, 1), track=0.0, shadow=0, idx=0, shadow_a=170, shadow_off=6):
    key = (txt, font, size, col, track, shadow, idx, shadow_a, shadow_off)
    if key in _tc: return _tc[key]
    f = ImageFont.truetype(font, size, index=idx)
    asc, desc = f.getmetrics(); ext = max(0, -f.getbbox('ÁÉÑ')[1])
    sp = track * size
    widths = [f.getlength(ch) + sp for ch in txt]; tw = max(1, sum(widths) - sp)
    pad = 8 + ext + (shadow * 2 + shadow_off if shadow else 0)
    w, h = int(tw + 2 * pad + 2), int(asc + desc + 2 * pad)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    def draw(d, fill):
        x = pad
        for ch, cw in zip(txt, widths): d.text((x, pad), ch, font=f, fill=fill); x += cw
    if shadow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, shadow_a))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)), (0, shadow_off))
    draw(ImageDraw.Draw(img), tuple(int(c * 255) for c in col[:3]) + (int(col[3] * 255),))
    s, buf = pil_surface(img)
    r = (s, buf, w, h, tw, asc); _tc[key] = r; return r

def put(ctx, t, x, y, scale=1.0, alpha=1.0, ax=0.5, ay=0.5):
    """ax relative to the glyph run (0 left edge, 0.5 centre, 1 right edge)"""
    s, _, w, h, tw, _ = t
    if alpha <= 0.002: return
    ctx.save(); ctx.translate(x, y); ctx.scale(scale, scale)
    ctx.set_source_surface(s, -((w - tw) / 2 + tw * ax), -h * ay)
    ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(alpha); ctx.restore()

# ---------- HDR (HLG) / SDR compositing ----------
M709_2020 = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]], np.float32)
_ha, _hb, _hc = 0.17883277, 0.28466892, 0.55991073
EREF = (math.exp((0.75 - _hc) / _ha) + _hb) / 12          # BT.2408: graphics white at 75% HLG signal (203 nits)
_lut = np.where(np.arange(256) / 255 <= 0.04045, (np.arange(256) / 255) / 12.92, ((np.arange(256) / 255 + 0.055) / 1.055) ** 2.4).astype(np.float32)
def srgb8_to_hlg(rgb8):
    l = _lut[rgb8]; M = M709_2020                           # explicit 3x3 (numpy matmul misbehaves on this macOS build)
    lin = np.stack([l[..., 0] * M[i, 0] + l[..., 1] * M[i, 1] + l[..., 2] * M[i, 2] for i in range(3)], -1)
    E = np.clip(lin * EREF, 1e-6, 1)
    return np.where(E <= 1 / 12, np.sqrt(3 * E), _ha * np.log(np.maximum(12 * E - _hb, 1e-6)) + _hc).astype(np.float32)

def resize_f(fr, box, size):
    """float32 HxWx3 -> crop box -> size (bilinear, per channel)"""
    return np.dstack([np.asarray(Image.fromarray(fr[..., c], 'F').resize(size, Image.BILINEAR, box=box)) for c in range(3)])

def new_layer(h=H):
    arr = np.zeros((h, W, 4), np.uint8)
    s = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, h, W * 4)
    return arr, s, cairo.Context(s)

def layer_over(sdr, hdr, arr):
    a8 = arr[..., 3]; ys, xs = np.nonzero(a8)
    if len(ys) == 0: return
    a = a8[ys, xs].astype(np.float32)[:, None] / 255
    pm = arr[ys, xs][:, [2, 1, 0]].astype(np.float32) / 255
    c8 = np.clip(np.clip(pm / np.maximum(a, 1e-4), 0, 1) * 255 + 0.5, 0, 255).astype(np.uint8)
    sdr[ys, xs] = pm + sdr[ys, xs] * (1 - a)
    hdr[ys, xs] = srgb8_to_hlg(c8) * a + hdr[ys, xs] * (1 - a)

def to8(x): return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
def to16(x): return (np.clip(x, 0, 1) * 65535 + 0.5).astype(np.uint16)

def crop_box(z, size, cx, cy, sw=SW, sh=SH):
    ow, oh = size; cw = sw / z; ch = cw * oh / ow
    x0 = min(max(cx * sw - cw / 2, 0), sw - cw); y0 = min(max(cy * sh - ch / 2, 0), sh - ch)
    return (x0, y0, x0 + cw, y0 + ch)

# ---------- IO ----------
def hlg_reader(path, w=SW, h=SH):
    """iPhone HLG source -> float32 frames (HLG signal, BT.2020 RGB, full range)"""
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf',
           f'fps=30,scale={w}:{h}:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
           '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 6)
    sz = w * h * 6; k = 0
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz: break
        yield k, b; k += 1
    p.kill()

def encoders(out_hdr, out_sdr, audio_wav):
    common = ['-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)]
    eh = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb48le', '-color_range', 'pc', '-i', '-', '-i', audio_wav,
                          '-vf', 'scale=out_color_matrix=bt2020:in_range=pc:out_range=tv:flags=bicubic+accurate_rnd,format=yuv420p10le',
                          '-c:v', 'libx265', '-crf', '17', '-preset', 'medium', '-tag:v', 'hvc1',
                          '-x265-params', 'colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error',
                          '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_hdr], stdin=subprocess.PIPE)
    es = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb24', '-i', '-', '-i', audio_wav,
                          '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
                          '-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_sdr], stdin=subprocess.PIPE)
    return eh, es
