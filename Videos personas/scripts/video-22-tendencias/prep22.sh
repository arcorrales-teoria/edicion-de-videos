#!/bin/bash
# Tendencias (video 22): IMG_9070 is the HOOK, IMG_9069 the body. Both takes are cleaned with DeepFilterNet3 BEFORE cutting,
# so the cuts are read on the clean envelope (street noise hid the pauses in the raw audio).
set -e; cd "$(dirname "$0")"
DF_PY=${DF_PY:-/private/tmp/claude-501/-Users-acorrales-Desktop-Edici-n-de-videos/a25c8139-6d4f-4c18-ab75-0c0fbdf4c322/scratchpad/dfenv/bin/python}
for f in 9069 9070; do
  ffmpeg -v error -y -i ~/Downloads/IMG_$f.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src${f}s.wav
  $DF_PY ../dfclean.py src${f}s.wav df$f.wav && ffmpeg -v error -y -i df$f.wav -ac 2 -ar 48000 -c:a pcm_s16le src${f}c.wav
done
echo "listo: python3 edit22.py && python3 voice_build22.py && python3 render22.py full <salida_HDR.mp4>"
