#!/usr/bin/env bash
# Crea la carpeta del siguiente proyecto con su número correlativo y su LEEME.
# Uso: herramientas/nuevo-proyecto.sh personas <nombre-corto>
#      herramientas/nuevo-proyecto.sh demos    <nombre-corto>
# Ejemplo: herramientas/nuevo-proyecto.sh personas notion  ->  proyectos/personas/29-notion/
set -euo pipefail

raiz="$(cd "$(dirname "$0")/.." && pwd)"
tipo="${1:-}"; nombre="${2:-}"
if [[ ! "$tipo" =~ ^(personas|demos)$ || -z "$nombre" ]]; then
  echo "Uso: $0 personas|demos <nombre-corto>" >&2; exit 1
fi

# nombre sin tildes, en minúsculas y con guiones
slug="$(python3 -c "import re,sys,unicodedata as u; s=u.normalize('NFKD',sys.argv[1]).encode('ascii','ignore').decode().lower(); print(re.sub(r'[^a-z0-9]+','-',s).strip('-'))" "$nombre")"
[[ -n "$slug" ]] || { echo "Nombre inválido: '$nombre'" >&2; exit 1; }

base="$raiz/proyectos/$tipo"
ultimo="$(ls -1 "$base" 2>/dev/null | grep -E '^[0-9]{2}-' | sed -E 's/^([0-9]+)-.*/\1/' | sort -n | tail -1 || true)"
sig="$(printf '%02d' $((10#${ultimo:-0} + 1)))"
destino="$base/$sig-$slug"
[[ ! -e "$destino" ]] || { echo "Ya existe: $destino" >&2; exit 1; }

if [[ "$tipo" == "demos" ]]; then
  mkdir -p "$destino"
  (cd "$raiz/plantillas/demo-producto" && tar cf - --exclude=node_modules --exclude='frames*' .) | (cd "$destino" && tar xf -)
  mkdir -p "$destino/entregas"
  plantilla="$raiz/plantillas/LEEME-proyecto-demo.md"
else
  mkdir -p "$destino"
  plantilla="$raiz/plantillas/LEEME-proyecto-persona.md"
fi
sed -e "s/{{NUMERO}}/$sig/g" -e "s/{{NOMBRE}}/$slug/g" -e "s/{{FECHA}}/$(date +%F)/g" "$plantilla" > "$destino/LEEME.md"

echo "Creado: ${destino#$raiz/}"
