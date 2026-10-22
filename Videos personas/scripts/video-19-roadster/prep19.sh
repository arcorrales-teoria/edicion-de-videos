#!/bin/bash
# Tesla Roadster (video 19): regenerate audio, fonts, wordmarks/icons and the silent clips next to the scripts.
# Inputs: ~/Downloads/IMG_9043.MOV, IMG_9044.MOV, "Twitter Video Downloader (1).mp4" (tw1), "Twitter Video Downloader.mp4" (tw2),
# and the 14 images pasted on 16 oct 2026 saved as ref/i23.png … ref/i36.png (23-29 memes, 30-36 tesla.com/roadster key visuals).
set -e; cd "$(dirname "$0")"; mkdir -p ref clips fonts
for f in 9043 9044; do ffmpeg -v error -y -i ~/Downloads/IMG_$f.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src${f}s.wav; done
cp ~/Downloads/"Twitter Video Downloader (1).mp4" tw1.mp4; cp ~/Downloads/"Twitter Video Downloader.mp4" tw2.mp4
curl -sL -o fonts/Saira.ttf "https://github.com/google/fonts/raw/main/ofl/saira/Saira%5Bwdth,wght%5D.ttf"   # OFL, ~ tesla.com/roadster type
python3 - <<'PY'
from PIL import Image
import numpy as np
def ext(src, box, out, lo=25, hi=200):        # light-on-black marks -> alpha, colours kept (the ROADSTER gold gradient)
    a = np.asarray(Image.open('ref/' + src).convert('RGB').crop(box)).astype(np.float32); al = np.clip((a.max(-1) - lo) / (hi - lo), 0, 1)
    ys, xs = np.nonzero(al > 0.04); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    al = al[y0:y1, x0:x1]; rgb = np.clip(a[y0:y1, x0:x1] / np.maximum(al[..., None], 1e-3), 0, 255)
    Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8)).save('ref/' + out)
ext('i30.png', (200, 590, 950, 660), 'roadster.png'); ext('i30.png', (50, 60, 240, 100), 'tesla.png')
ext('i31.png', (470, 45, 590, 140), 'ic_aero.png'); ext('i31.png', (930, 45, 1020, 140), 'ic_thrust.png'); ext('i31.png', (1370, 45, 1465, 140), 'ic_fan.png')
PY
clip(){ rm -rf clips/$1; mkdir -p clips/$1; ffmpeg -v error -y -ss $3 -t $4 -i $2 -an -vf "fps=30,scale=1080:-2,format=rgb24" -q:v 2 clips/$1/%04d.jpg; }
clip fly tw1.mp4 0.2 5.4      # off the ramp, thrusters, landing in smoke
clip hud tw2.mp4 4.3 3.4      # launch with the G-force / altitude HUD
clip end tw2.mp4 19.0 5.0     # flying over the truck (ending)
echo "listo: python3 edit19.py && python3 voice_build19.py && python3 render19.py full <salida_HDR.mp4>"
