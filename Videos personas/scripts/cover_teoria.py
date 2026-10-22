"""Portada teoría (good work_ look): posterized frame of me + 'teoría by andrés corrales_' + yellow outlined title.
usage: cover_teoria.py <video> <seconds> <out.jpg> <line1|line2|...> [shift_px]"""
import sys, subprocess, numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
sys.path.insert(0, '/Users/acorrales/Desktop/Edición de videos/scripts'); import fx
HN = '/System/Library/Fonts/HelveticaNeue.ttc'; YEL = (255, 231, 46)
def posterize(rgb8):
    im = Image.fromarray(rgb8).resize((540, 960), Image.BILINEAR)
    im = ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.45)).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5)); a = np.asarray(im).astype(np.float32) / 255; L = 5
    q = Image.fromarray((np.round(a * (L - 1)) / (L - 1) * 255).astype(np.uint8)).filter(ImageFilter.ModeFilter(3))
    return q.resize((1080, 1920), Image.BILINEAR)
def stroked(txt, size, stroke, idx):
    f = ImageFont.truetype(HN, size, index=idx); tw = f.getlength(txt); asc, desc = f.getmetrics(); pad = stroke + 24
    img = Image.new('RGBA', (int(tw + 2 * pad), int(asc + desc + 2 * pad)), (0, 0, 0, 0))
    sh = img.copy(); ImageDraw.Draw(sh).text((pad + 5, pad + 6), txt, font=f, fill=(0, 0, 0, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=YEL + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return img, pad, tw
video, sec, out, lines = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4].split('|')
SHIFT = int(sys.argv[5]) if len(sys.argv) > 5 else 220
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(sec), '-i', video, '-frames:v', '1', '-vf',
                      'scale=1440:2560:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint16).reshape(2560, 1440, 3).astype(np.float32) / 65535
full = Image.fromarray(fx.to8(fx.resize_f(fr, (0, 0, 1440, 2560), (1080, 1920))))
canvas = Image.new('RGB', (1080, 1920)); canvas.paste(full, (0, SHIFT))              # head touches the top: push down, extend the wall
canvas.paste(full.crop((0, 0, 1080, 12)).resize((1080, SHIFT), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)), (0, 0))
img = posterize(np.asarray(canvas)).convert('RGBA')
x0 = 56; lab = stroked('teoría by andrés corrales_', 54, 5, 0); img.alpha_composite(lab[0], (x0 - lab[1], 1060 - lab[1]))
L = [stroked(l, 150, 9, 1) for l in lines]; s = min(1.0, min(968 / t[2] for t in L)); y = 1134
for t in L:
    ti = t[0].resize((int(t[0].width * s), int(t[0].height * s)), Image.LANCZOS) if s < 1 else t[0]
    img.alpha_composite(ti, (int(x0 - t[1] * s), int(y - t[1] * s))); y += int(150 * s)
img.convert('RGB').save(out, quality=94)
img.convert('RGB').crop((0, 285, 1080, 1635)).resize((540, 675)).save(out.replace('.jpg', '_4x5_preview.jpg').replace('/Users/acorrales/Downloads', '/tmp'), quality=85)
print('saved', out)
