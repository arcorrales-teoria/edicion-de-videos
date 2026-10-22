#!/bin/bash
# Atención / Darshita (video 23): clean the take with DeepFilterNet3 BEFORE cutting, extract her film's shots (cropped above its
# burned-in subtitles, silent), the X screenshots crops, and the script font.
set -e; cd "$(dirname "$0")"; mkdir -p ref clips fonts
DF_PY=${DF_PY:-/private/tmp/claude-501/-Users-acorrales-Desktop-Edici-n-de-videos/a25c8139-6d4f-4c18-ab75-0c0fbdf4c322/scratchpad/dfenv/bin/python}
ffmpeg -v error -y -i ~/Downloads/IMG_9088.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src9088s.wav
$DF_PY ../dfclean.py src9088s.wav df9088.wav && ffmpeg -v error -y -i df9088.wav -ac 2 -ar 48000 -c:a pcm_s16le src9088c.wav
cp ~/Downloads/"Twitter Video Downloader (2).mp4" refvid.mp4
for n in 85 86 87; do cp ~/Downloads/IMG_90$n.PNG ref/i$n.png; done
curl -sL -o fonts/Pacifico.ttf "https://github.com/google/fonts/raw/main/ofl/pacifico/Pacifico-Regular.ttf"
python3 - <<'PY'
from PIL import Image
a = Image.open('ref/i85.png').convert('RGB'); b = Image.open('ref/i86.png').convert('RGB'); c = Image.open('ref/i87.png').convert('RGB')
for k, (im, box) in {'t_text': (a, (0, 110, 1170, 1210)), 't_photo': (a, (20, 1235, 1150, 1900)), 't_stats': (a, (0, 1940, 1170, 2130)),
                     'q_ankur': (b, (0, 640, 1170, 1150)), 'q_aleks': (c, (0, 520, 1170, 1050))}.items(): im.crop(box).save('ref/%s.png' % k)
PY
clip(){ mkdir -p clips/$1; ffmpeg -v error -y -ss $2 -t $3 -i refvid.mp4 -an -vf "fps=30,crop=2578:850:0:0,scale=1290:-2,format=rgb24" -q:v 2 clips/$1/%04d.jpg; }
clip bed 0.4 6.5; clip dead 9.7 2.4; clip news 119.6 2.6; clip hi 19.8 3.2; clip type 86.0 3.0; clip welcome 105.8 3.0; clip game 168.2 2.6; clip call 236.0 7.0; clip logo 243.8 2.4
echo "listo: python3 edit23.py && python3 voice_build23.py && python3 render23.py full <salida_HDR.mp4> && python3 cover23.py 1.6 portada.jpg"
