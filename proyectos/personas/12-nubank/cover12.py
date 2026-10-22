"""Cover (portada): the article's opening photo (Colossus, David Vélez in the Nubank office) full-bleed, with the teoría label and
the title in the good-work_ yellow. 1080x1920; title + David's face inside the 4:5 grid crop (y 285-1635)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas')); sys.path.insert(0, HERE)
from PIL import Image, ImageFilter, ImageEnhance
import render12 as R
im = Image.open(os.path.join(HERE, 'ref', 'NUBANK-COLOSSUS-MAG0143-scaled.jpg')).convert('RGB')
img = im.crop((400, 0, 1360, 1707)).resize((1080, 1920), Image.LANCZOS)
# soft darkening behind the text block only (keeps the photo intact, lifts the yellow off the wood)
shade = Image.new('L', (1080, 1920), 0)
for y in range(1920):
    v = int(120 * max(0, 1 - abs(y - 500) / 420)); shade.paste(v, (0, y, 1080, y + 1))
img = Image.composite(Image.new('RGB', (1080, 1920), (0, 0, 0)), img, shade).convert('RGBA')
x0 = 56
lab = R.stroked('teoría by andrés corrales_', 52, R.YEL, 5, R.REG)
img.alpha_composite(lab[0], (x0 - lab[1], 312 - lab[1]))
LINES = [R.stroked(l, 150, R.YEL, 9, R.BOLD, -0.02) for l in ['EL MEJOR ARTÍCULO', 'QUE LEERÁS', 'ESTA SEMANA']]
s = min(1.0, min(968 / t[2] for t in LINES)); y = 382
for t in LINES:
    ti = t[0].resize((int(t[0].width * s), int(t[0].height * s)), Image.LANCZOS) if s < 1 else t[0]
    img.alpha_composite(ti, (int(x0 - t[1] * s), int(y - t[1] * s))); y += int(156 * s)
out = sys.argv[1] if len(sys.argv) > 1 else '/Users/acorrales/Downloads/IMG_8938_nubank_portada.jpg'
img.convert('RGB').save(out, quality=94)
img.convert('RGB').crop((0, 285, 1080, 1635)).resize((540, 675)).save(os.path.join(HERE, 'contact', 'cover_4x5.jpg'), quality=85)
print('saved', out)
