# Edición de videos: archivo madre

Este archivo lo lee Claude al empezar cualquier sesión. Dice dónde está cada cosa y qué pasos seguir cada vez que el usuario pide editar un video. Si algo de aquí contradice una guía, manda la guía; si una carpeta cambia de lugar, se actualiza este archivo en el mismo cambio.

**Usuario:** Andrés Corrales (marca `teoría by andrés corrales_`). Se le habla en español. Hace reels y TikToks hablando a cámara, y demos de producto.

---

## 1. Mapa de rutas

```
CLAUDE.md                          ← este archivo (madre)
LEEME.md                           ← entrada rápida para personas
guias/
  personas/reglas-y-estilos.md     ← REGLAS de la casa para videos con persona (fuente de verdad)
  personas/guia-completa-para-compartir.md   ← versión autocontenida para otras personas; no es la fuente de verdad
  demos/guia-demos-producto.md     ← guía de demos de producto (motion graphics)
  hook/                            ← estándares y biblioteca de hooks (ganchos de apertura)
herramientas/                      ← código compartido: fx.py, framing.py, dfclean.py, cover_teoria.py, swift/
  revisar-entorno.sh               ← qué hay instalado en esta máquina
  nuevo-proyecto.sh                ← crea el siguiente proyecto numerado con su LEEME
plantillas/
  pedido-persona.md                ← cómo pedir un video con persona
  LEEME-proyecto-persona.md, LEEME-proyecto-demo.md
  demo-producto/                   ← base de toda demo nueva (video.html, render.mjs, assets)
proyectos/
  personas/INDICE.md               ← catálogo de los 28 videos y qué proyecto copiar según el estilo
  personas/NN-nombre/              ← scripts, transcripción y LEEME de cada video
  demos/NN-nombre/                 ← una demo por carpeta
registro/
  historial-personas.md            ← qué se entregó, cuándo y qué se cortó
  historial-demos.md
entrada/                           ← material crudo del momento (no va a git)
salida/                            ← entregas del momento (no va a git)
.claude/skills, .agents/skills     ← skills de diseño (para demos y páginas HTML)
```

Rutas de entrega en el Mac del usuario: `~/Downloads` (Descargas). Los scripts viejos guardan rutas `/Users/acorrales/...` para el material crudo; el crudo ya no existe (se borró), así que los scripts sirven de referencia y para reutilizar componentes.

---

## 2. Protocolo: cada vez que pidan editar un video

Seguir en orden. No saltar el paso 1 ni el cierre.

### Paso 1. Clasificar y leer
| Pedido | Tipo | Leer antes de empezar |
|---|---|---|
| Alguien hablando a cámara (reel, TikTok, hook + cuerpo) | **Persona** | `guias/personas/reglas-y-estilos.md` (secciones 1 a 5 y 8), `guias/hook/estandares.md`, las últimas filas de `registro/historial-personas.md` |
| Video de lanzamiento o demo de un producto, hecho con código | **Demo** | `guias/demos/guia-demos-producto.md` y el LEEME de `proyectos/demos/01-job-status-launch/` |
| Cortar, unir, comprimir, subtitular o convertir un archivo | **Simple** | Solo la sección 4 de este archivo; usar ffmpeg directo y no crear proyecto numerado salvo que el usuario lo pida |

Si el pedido menciona una marca o un estilo ("como el de Graza", "el modelo Roadster"), abrir ese proyecto en `proyectos/personas/INDICE.md` y leer su LEEME y su `render*.py` antes de escribir código nuevo.

### Paso 2. Revisar el entorno
Correr `bash herramientas/revisar-entorno.sh` y decirle al usuario, en pocas líneas, qué se puede hacer aquí y qué no (sección 5). No empezar a renderizar sin saberlo.

### Paso 3. Completar el pedido
Usar `plantillas/pedido-persona.md` como lista. Preguntar **solo** lo que bloquee el trabajo (material, título si no lo propone Claude, estilo si es ambiguo, dónde entregar). Todo lo demás se decide con los valores por defecto de la guía, y se le dice al usuario qué se decidió. Una sola ronda de preguntas.

### Paso 4. Ubicar el material
- Pedir el archivo en `entrada/`, un enlace descargable o Google Drive (si el conector está conectado en la sesión). Si el usuario lo sube a una rama, tomarlo de ahí.
- Con `ffprobe`: duración, rotación (`rotation=-90` = vertical), HDR o SDR, fps. Para videos con cara, hoja de contacto de cuadros.
- Material que no está y no se puede reconstruir: avisar y no inventarlo. Nunca usar datos reales de otras personas en capturas (difuminar o usar cuentas de ejemplo).

### Paso 5. Crear el proyecto
```bash
bash herramientas/nuevo-proyecto.sh personas <nombre-corto>   # o: demos <nombre-corto>
```
El script crea la carpeta con el número siguiente y su LEEME. Después, copiar los scripts del proyecto más parecido (tabla de `proyectos/personas/INDICE.md`), renombrándolos con el número nuevo, y anotar en el LEEME de dónde se partió. Importar el código común con `sys.path.insert(0, <raiz>/herramientas)` como se explica en `herramientas/LEEME.md`.

### Paso 6. Trabajar
- **Persona:** seguir el flujo de `reglas-y-estilos.md` sección 3 (revisar, transcribir, cortar en el punto más silencioso, armar la voz, re-transcribir, storyboard, previsualizar, render, audio aparte, portada).
- **Demo:** seguir `guia-demos-producto.md` secciones 2 a 7.
- **Intermedios pesados** (audio `.wav`, cuadros `.jpg`, hojas de contacto, `frames/`): trabajarlos en el directorio temporal de la sesión, no en el repositorio. En el proyecto solo quedan scripts, la transcripción con tiempos (`*.json`), portada y LEEME.
- **Punto de control obligatorio:** antes de un render largo con un diseño nuevo, mostrar 2 o 3 cuadros clave (hoja de contacto) y dejar que el usuario corrija.
- Cuando el usuario corrija algo ("no me gusta X", "siempre hazlo Y"), aplicar el cambio **y** guardarlo como regla (paso 9).

### Paso 7. Verificar
Pasar la lista de `reglas-y-estilos.md` sección 8. Comprobar con `ffprobe` la duración, la resolución (1080×1920 en vertical) y que el audio existe. Revisar cuadros en cada transición. Decir con precisión qué se verificó y qué no (por ejemplo, "no pude escuchar el audio; medí el volumen con loudnorm").

### Paso 8. Entregar
- Guardar en `salida/` con **nombre nuevo en cada versión** (`IMG_XXXX_tema_editado_v2_HDR.mp4`), para evitar que el reproductor muestre una versión vieja en caché.
- Entregar solo la versión HDR cuando el origen es HDR (regla vigente desde el 13 oct 2026), más la portada si se pidió.
- Los videos no se suben a git. Si el usuario quiere recibirlo fuera de la sesión: Google Drive (si está conectado) o un enlace.

### Paso 9. Cerrar (siempre)
1. `LEEME.md` del proyecto: pedido, decisiones, cortes hechos, archivos, entrega.
2. Agregar una fila al final de la tabla de `registro/historial-personas.md` (o `historial-demos.md`).
3. Agregar la línea del proyecto a `proyectos/personas/INDICE.md`.
4. Si hubo una regla nueva o una corrección del usuario: `guias/personas/reglas-y-estilos.md` (con fecha, en la sección que corresponda y en la tabla de errores si fue un error) o `guias/hook/estandares.md` si trata del gancho de apertura.
5. Si se agregó una carpeta o un archivo importante, actualizar el mapa de la sección 1.
6. Commit en la rama de la sesión y push. Crear el pull request en borrador si no existe.

---

## 3. Reglas que no se negocian (resumen)

El detalle y las razones están en `guias/personas/reglas-y-estilos.md`. Si hay diferencia, manda la guía.

- **Sonido:** solo la voz. Nada de ping, chime, whoosh, pop ni música. Audio de terceros siempre en silencio. Voz con limpieza de ruido (DeepFilterNet cuando hay ruido de calle, antes de cortar) y loudnorm lineal en dos pasadas a −15 LUFS.
- **Cortes:** cada corte va al instante más silencioso (±150 ms); nunca dentro de una vocal. Se quitan arranques en falso, muletillas ("literalmente"), repeticiones y silencios de más de ~0.2 s.
- **Color:** no retocar. Origen HDR (HLG) se entrega solo en HDR; nada de SDR.
- **Encuadre:** nunca cortar la cabeza. Sin movimiento de cámara salvo que se pida.
- **Título:** todo video lleva título durante los primeros 5 s, sin subtítulos encima; ver `guias/hook/estandares.md`.
- **Subtítulos:** una línea, hasta 4 palabras, nada en el 20% inferior (interfaz de IG). Corregir lo que Whisper transcribe mal (Claude, CapCut, MUD\WTR).
- **Formato por defecto:** el actual (sección 5.I de la guía): cuarto real, franja de gráficos arriba de los ojos, una forma que se transforma, Geist, barra de progreso azul. Modelos: `19-roadster` y `20-x`.
- **Material de otros:** sin su audio ni sus subtítulos; nunca la cara del otro creador; dar crédito si se publica.
- **Texto:** español, **nunca raya (—)**. Nunca el gráfico de "sistema solar / radar". No usar la textura de puntos.
- **Velocidad:** 1.05x por defecto, con `atempo` para conservar el tono; transcribir ya acelerado.
- **Demos:** exactamente 20 s (600 cuadros a 30 fps), firma "by Andrés Corrales" al inicio y al final, sin audio, datos ficticios, historias con 250 px libres arriba y 340 px abajo.

---

## 4. Ediciones simples (ffmpeg directo)

Para pedidos que no son un proyecto: cortar (`-ss`/`-to`, recodificar si el corte debe ser exacto), unir (`concat`), cambiar velocidad (`setpts` y `atempo`), extraer audio, convertir formato o relación de aspecto, comprimir (`libx264 -crf 23`), sacar cuadros o GIF, quemar subtítulos (`subtitles` con un `.srt`). Mantener la resolución y el color del original. Guardar en `salida/` con nombre nuevo y decir qué comando se usó.

---

## 5. Entorno: Mac del autor frente a sesión en la nube

Las guías y los scripts se escribieron en un **Mac** (Apple Silicon). Las sesiones de nube son Linux y no tienen todo:

| Necesidad | En el Mac | En la nube |
|---|---|---|
| ffmpeg con libx265, loudnorm, zscale | sí | sí (comprobado) |
| Python con numpy y Pillow | sí | sí |
| `cairocffi` (lo usa `fx.py` para dibujar) | sí | falta; `pip install cairocffi` (necesita libcairo del sistema) |
| Whisper (transcripción) | sí | falta; `pip install openai-whisper` o `faster-whisper`, modelo `medium`, idioma `es` |
| Detección de rostro (Apple Vision, `swift/face.swift`) | sí | no existe; reemplazar por mediapipe u OpenCV y avisar que cambió |
| Fuentes Helvetica Neue, Geist, New York, Saira | sí | faltan; usar una equivalente instalada y avisar |
| DeepFilterNet | entorno aparte | `pip install deepfilternet` en un entorno aparte |

Reglas: no afirmar que algo funciona sin haberlo corrido; si una herramienta falta, instalarla si hay red o decirle al usuario qué cambia en el resultado. Los scripts de los videos antiguos no se pueden volver a renderizar porque falta el material crudo.

---

## 6. Convenciones del repositorio

- Proyectos: `NN-nombre` (dos cifras), en `proyectos/personas/` y `proyectos/demos/`. Crear siempre con `herramientas/nuevo-proyecto.sh`.
- Nombres de archivo sin tildes ni espacios en carpetas y scripts nuevos.
- Cada video: `edit<NN>.py` (cortes y tiempos), `voice_build<NN>.py`, `render<NN>.py`, `cover<NN>.py`, `v<NN>.json` (transcripción).
- Lo que va a git: scripts, JSON de transcripción, portadas finales, LEEME, guías. Lo que no: videos crudos y renders, `.wav`, `frames/`, `node_modules/`.
- Cuando el usuario muestre ejemplos de ganchos o referencias, guardarlos en `guias/hook/biblioteca/` con su plantilla.
- Rama de trabajo de la sesión: la que indique el sistema; no empujar a otra. Después de empujar, abrir el pull request en borrador si no existe.
