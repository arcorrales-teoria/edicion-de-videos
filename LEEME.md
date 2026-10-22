# Edición de videos

Todo lo necesario para crear videos con Claude: reglas de la casa, código compartido, plantillas y el archivo de cada video ya hecho.

**Claude empieza siempre por `CLAUDE.md`**: ahí está el mapa de carpetas y el protocolo paso a paso para cada pedido de edición. Esta página es solo la entrada rápida para personas.

## Cómo pedir un video
- **Con persona** (reel o TikTok hablando a cámara): "Edita este video: [archivo o enlace]. Título: ..." Hay una plantilla en `plantillas/pedido-persona.md`.
- **Demo de producto** (motion graphics hechos con código): "Arma una demo de [producto] con la plantilla."
- **Edición simple** (cortar, unir, comprimir, subtitular): dilo tal cual; no hace falta ningún formato.

## Carpetas
| Carpeta | Qué hay |
|---|---|
| `CLAUDE.md` | Archivo madre: mapa, protocolo y reglas clave |
| `guias/personas/` | Reglas y estilos de la casa; guía completa para compartir con otras personas |
| `guias/demos/` | Guía de demos de producto |
| `guias/hook/` | Estándares y biblioteca de hooks (ganchos de apertura) |
| `herramientas/` | Código compartido (`fx.py`, `framing.py`, ...) y scripts de apoyo |
| `plantillas/` | Plantilla de demo, LEEME de proyecto y plantilla de pedido |
| `proyectos/personas/` | Un video por carpeta (`01-vox` ... `28-casey`), con `INDICE.md` |
| `proyectos/demos/` | Una demo por carpeta |
| `registro/` | Historial de entregas |
| `entrada/` y `salida/` | Material crudo y entregas del momento (no se suben a git) |
| `.claude/`, `.agents/` | Skills de diseño |

## Convenciones
- Proyectos numerados: `NN-nombre` en `proyectos/personas/` y en `proyectos/demos/`.
- Cada proyecto guarda sus scripts, la transcripción con tiempos y un LEEME con lo entregado.
- Nunca usar raya (—) en los textos de los videos.
- Renders pesados (cuadros, audio intermedio) fuera del repositorio; aquí se archivan scripts, transcripciones y portadas.
- Si el repositorio vive en una carpeta sincronizada con iCloud, trabajar los renders en `~/Developer/`.
