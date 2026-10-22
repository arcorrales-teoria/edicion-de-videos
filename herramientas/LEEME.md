# Herramientas compartidas

Código que usan todos los proyectos. No guardar aquí nada específico de un video.

| Archivo | Para qué |
|---|---|
| `fx.py` | Módulo autónomo: texto con tracking y sombra, easing, composición HDR/SDR, lector HLG, codificadores. Base de todo render nuevo. Requiere `cairocffi`. |
| `framing.py` | Encuadre que nunca corta la cabeza (usa las detecciones de `swift/face.swift`). |
| `dfclean.py` | Limpieza de ruido de la voz con DeepFilterNet3: `dfclean.py voz_cruda.wav voz_limpia.wav [atten_lim_db]`. Corre en un entorno aparte (ver `guias/personas/reglas-y-estilos.md`, sección 5.I). |
| `cover_teoria.py` | Portada estilo "teoría": `cover_teoria.py <video> <segundo> <salida.jpg> "LÍNEA 1\|LÍNEA 2"`. |
| `swift/face.swift` | Detección de rostro con Apple Vision (solo macOS). |
| `swift/segment.swift` | Segmentación de persona con Apple Vision (solo macOS). |
| `revisar-entorno.sh` | Informa qué programas, librerías y fuentes hay en la máquina actual. Correrlo al empezar. |
| `nuevo-proyecto.sh` | Crea `proyectos/personas/NN-nombre/` o `proyectos/demos/NN-nombre/` con el número siguiente y su LEEME. |

## Cómo importar desde un proyecto
Los scripts de `proyectos/personas/NN-nombre/` agregan esta carpeta al `sys.path`:

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'herramientas'))
import fx
```
