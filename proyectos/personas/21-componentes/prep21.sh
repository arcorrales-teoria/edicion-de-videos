#!/bin/bash
# Componentes (video 21): regenerate audio, the user's screenshots (Desktop, 19 oct 2026 8:32-8:48) and the site captures.
set -e; cd "$(dirname "$0")"; mkdir -p ref web
ffmpeg -v error -y -i ~/Downloads/IMG_9068.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src9068s.wav
i=1; for f in "$HOME"/Desktop/Captura*2026-10-19*; do cp "$f" ref/$(printf "c%02d" $i).png; i=$((i+1)); done   # c01-c02 React Bits key visual
node shots.js web     # Playwright (npx cache) captures of the 14 sites, 1440x900 @2x, dark scheme
echo "listo: python3 edit21.py && python3 voice_build21.py && python3 render21.py full <salida_HDR.mp4>"
# Moraleja Design (final card): Desktop 19 oct 2026 9:45:48 / 9:45:56 / 9:46:00 -> ref/m1-m3.png, ~/Downloads/IMG_9072.PNG -> ref/m4.png;
# ref/m4b.png = m4 with the "Followed by…" row (third-party names) blurred: box (20, 870, 1150, 1040), GaussianBlur(22).
