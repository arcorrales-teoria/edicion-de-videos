"""Cover (portada) as a collage, per the user's reference reel (Screenshot 2026-10-04 at 7.10.11 PM): my frame in the middle,
podcast/episode art as plain rectangles around it, and a white caption with a black outline. 1080x1920; face + text inside the 4:5 crop."""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
import numpy as np, fx
from PIL import Image, ImageFilter, ImageEnhance, ImageFont, ImageDraw
import render11 as R
T_SRC = 2.0
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(T_SRC), '-i', R.E.SRCS['h'], '-frames:v', '1', '-vf',
                      'scale=1440:2560:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint16).reshape(2560, 1440, 3).astype(np.float32) / 65535
full = Image.fromarray(fx.to8(fx.resize_f(fr, (0, 0, 1440, 2560), (1080, 1920))))
full = ImageEnhance.Contrast(ImageEnhance.Color(full).enhance(1.08)).enhance(1.06)
SHIFT = 190                                   # head sits at the top edge in this take: push down, extend the wall
img = Image.new('RGB', (1080, 1920)); img.paste(full, (0, SHIFT))
img.paste(full.crop((0, 0, 1080, 12)).resize((1080, SHIFT), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)), (0, 0))
img = img.convert('RGBA')

def piece(f, box, x, y, w):
    im = Image.open(os.path.join(HERE, 'ref', f)).convert('RGB').crop(box)
    h = int(w * im.height / im.width); im = im.resize((w, h), Image.LANCZOS)
    sh = Image.new('RGBA', (w + 48, h + 48), (0, 0, 0, 0)); sh.paste(Image.new('RGBA', (w, h), (0, 0, 0, 110)), (28, 32))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); img.alpha_composite(sh, (x - 24, y - 24)); img.paste(im, (x, y))
# around the face (face ~ x 220-860, y 400-1330 after the shift); grid crop is y 285-1635
piece('desk_capture.png', (45, 95, 395, 445), 30, 250, 300)          # 20VC
piece('20vc_viktor.png', (41, 105, 400, 463), 790, 300, 270)         # 20VC · Viktor / Wispr Flow
piece('mfm_show.png', (39, 127, 390, 478), -30, 690, 270)            # My First Million
piece('20vc_uber.png', (37, 125, 388, 476), 840, 690, 260)           # 20VC · Uber
piece('senra_show.png', (31, 107, 382, 458), 20, 1360, 270)          # David Senra
piece('senra_rahal.png', (11, 69, 362, 420), 800, 1370, 260)         # Senra · Peter Rahal
piece('mfm_im8.png', (0, 0, 1480, 430), 300, 1540, 500)              # MFM · $100M
piece('senra_leone.png', (5, 97, 363, 455), 330, 60, 230)            # Senra · Doug Leone (top, above the head)
piece('mfm_instinct.png', (0, 0, 1560, 460), 600, 40, 470)           # MFM · Instinct

# caption: white, black outline, centred (as in the reference)
f = ImageFont.truetype(R.HN, 74, index=R.BOLD); d = ImageDraw.Draw(img)
for k, line in enumerate(['3 podcasts para adelantarte', 'a tu competencia']):
    w = d.textlength(line, font=f); y = 1160 + k * 88
    d.text(((1080 - w) / 2, y), line, font=f, fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
out = sys.argv[1] if len(sys.argv) > 1 else '/Users/acorrales/Downloads/IMG_8930_podcasts_portada_collage.jpg'
img.convert('RGB').save(out, quality=94)
img.convert('RGB').crop((0, 285, 1080, 1635)).resize((540, 675)).save(os.path.join(HERE, 'contact', 'cover_collage_4x5.jpg'), quality=85)
print('saved', out)
