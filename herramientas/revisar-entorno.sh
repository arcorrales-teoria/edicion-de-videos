#!/usr/bin/env bash
# Revisa qué herramientas de edición hay en esta máquina (Mac del autor o sesión en la nube).
# Uso: herramientas/revisar-entorno.sh
# Solo informa; no instala nada. La columna "si falta" dice qué hacer.

ok()   { printf '  OK     %-22s %s\n' "$1" "$2"; }
falta(){ printf '  FALTA  %-22s %s\n' "$1" "$2"; }

echo "Sistema: $(uname -s) $(uname -m)"
echo; echo "Programas"
for p in ffmpeg ffprobe python3 node npx; do
  if command -v "$p" >/dev/null 2>&1; then ok "$p" "$(command -v "$p")"; else falta "$p" "instalar (apt install ffmpeg / brew install ffmpeg)"; fi
done
if command -v whisper >/dev/null 2>&1 || python3 -c "import whisper" 2>/dev/null; then ok whisper "transcripción lista"; else falta whisper "pip install openai-whisper (o faster-whisper); modelo medium, idioma es"; fi
if command -v swiftc >/dev/null 2>&1; then ok swiftc "Apple Vision disponible (face.swift / segment.swift)"; else falta swiftc "sin Apple Vision: usar mediapipe u OpenCV para la cara (ver CLAUDE.md, sección Entorno)"; fi

echo; echo "Librerías de Python"
for m in numpy PIL cairocffi torch; do
  if python3 -c "import $m" 2>/dev/null; then ok "$m" "importa"; else falta "$m" "pip install $( [ "$m" = PIL ] && echo pillow || echo "$m" )"; fi
done

echo; echo "Fuentes (las guías usan Helvetica Neue, Geist, New York)"
for f in "HelveticaNeue" "Geist" "NewYork" "Saira"; do
  if fc-list 2>/dev/null | grep -qi "$f" || ls /System/Library/Fonts/*"$f"* ~/Library/Fonts/*"$f"* 2>/dev/null | grep -q .; then ok "$f" "instalada"; else falta "$f" "usar una equivalente (Inter/Liberation Sans/DejaVu) y avisar al usuario"; fi
done

echo; echo "Archivos de trabajo"
raiz="$(cd "$(dirname "$0")/.." && pwd)"
echo "  entrada/: $(find "$raiz/entrada" -type f ! -name '.gitkeep' 2>/dev/null | wc -l) archivos"
echo "  salida/:  $(find "$raiz/salida" -type f ! -name '.gitkeep' 2>/dev/null | wc -l) archivos"
echo "  espacio libre en el repo: $(df -h "$raiz" | awk 'NR==2{print $4}')"
