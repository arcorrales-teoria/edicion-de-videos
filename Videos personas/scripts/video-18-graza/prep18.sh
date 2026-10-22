#!/bin/bash
# Graza (video 18): regenerate audio, reference images, brand marks and the silent b-roll clips next to the scripts.
# Inputs (Downloads/Desktop): IMG_9025.MOV, IMG_9027.MOV, ScreenRecording_10-14-2026 18-59-35_1.MP4, Graza screenshots of 14 oct 2026.
set -e; cd "$(dirname "$0")"; mkdir -p ref clips
ffmpeg -v error -y -i ~/Downloads/IMG_9025.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src9025s.wav
ffmpeg -v error -y -i ~/Downloads/IMG_9027.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src9027s.wav
cp ~/Downloads/"ScreenRecording_10-14-2026 18-59-35_1.MP4" rec.mp4
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.03.12 p.m..png" ref/cap2.png   # pop-up quiz (referencia)
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.04.28 p.m..png" ref/cap4.png   # Graza in Glass
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.04.34 p.m..png" ref/cap5.png   # olive-tap icon
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.04.49 p.m..png" ref/cap6.png   # 3 bottles
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.04.57 p.m..png" ref/cap7.png   # bottles + food
cp "$HOME/Desktop/Captura de pantalla 2026-10-14 a las 7.05.10 p.m..png" ref/cap8.png   # wordmark
cp ~/Downloads/DSC_3873-1.jpg ref/dsc.jpg
python3 - <<'PY'
from PIL import Image
import numpy as np
def ext(src, box, out, hi, lo=60):
    c = np.asarray(Image.open('ref/' + src).convert('RGB').crop(box)).astype(np.float32); lum = c.mean(-1)
    al = np.clip((hi - lum) / (hi - lo), 0, 1); ys, xs = np.nonzero(al > 0.05); al = al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgba = np.zeros(al.shape + (4,), np.uint8); rgba[..., :3] = 255; rgba[..., 3] = (al * 255).astype(np.uint8); Image.fromarray(rgba).save('ref/' + out)
ext('cap8.png', (20, 120, 2817, 960), 'wordmark.png', 222)     # stops before a stray mark at x 2818
ext('cap5.png', (900, 50, 1420, 560), 'olive.png', 115)        # hard threshold drops the grey "DRIP" text
PY
# reference reel: its captions sit at y~1000-1150 and the IG icons at x>1010, so crop above/below and keep x<1010
clip(){ rm -rf clips/$1; mkdir -p clips/$1; ffmpeg -v error -y -ss $2 -t $3 -i rec.mp4 -an -vf "fps=30,crop=$4,format=rgb24" -q:v 2 clips/$1/%04d.jpg; }
clip sq 25.02 2.80 1010:810:0:1180
clip soap 23.92 0.92 1010:720:0:270
clip chips 34.86 0.68 980:1680:10:300
clip mayo 35.66 0.70 980:1680:10:300
clip can 36.56 1.30 980:1680:10:300
echo "listo: python3 edit18.py && python3 voice_build18.py && python3 render18.py full <salida_HDR.mp4>"
