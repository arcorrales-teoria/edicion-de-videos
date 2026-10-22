"""Cover (portada) in the good-work_ style: posterized frame + 'teoría by andrés corrales_' + big yellow title. 1080x1920, readable in the 4:5 grid crop."""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np, framing, fx
from PIL import Image
import render10 as R
T_SRC = 41.9
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(T_SRC), '-i', R.E.SRCS['a'], '-frames:v', '1', '-vf',
                      'scale=1440:2560:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint16).reshape(2560, 1440, 3).astype(np.float32) / 65535
box = framing.head_crop(R.FT['a'].box(T_SRC), 1.12, panel=(1080, 1920), top_air=0.24)
img = Image.fromarray(R.posterize(fx.to8(fx.resize_f(fr, box, (1080, 1920))))).convert('RGBA')
x0 = 56
lab = R.stroked('teoría by andrés corrales_', 54, R.YEL, 5, R.REG)
img.alpha_composite(lab[0], (x0 - lab[1], 1010 - lab[1]))
y = 1082
LINES = [R.stroked(line, 150, R.YEL, 9, R.BOLD, -0.02) for line in ['3 PÁGINAS PARA', 'QUE TU WEBSITE', 'NO PAREZCA', 'HECHO CON IA']]
s = min(1.0, min(968 / t[2] for t in LINES))                         # one size for every line
for t in LINES:
    ti = t[0] if s >= 1 else t[0].resize((int(t[0].width * s), int(t[0].height * s)), Image.LANCZOS)
    img.alpha_composite(ti, (int(x0 - t[1] * s), int(y - t[1] * s))); y += int(150 * s)
out = sys.argv[1] if len(sys.argv) > 1 else '/Users/acorrales/Downloads/IMG_8927_ui_portada.jpg'
img.convert('RGB').save(out, quality=94)
img.convert('RGB').crop((0, 285, 1080, 1635)).resize((540, 675)).save(os.path.join(HERE, 'contact', 'cover_4x5.jpg'), quality=85)
print('saved', out)
