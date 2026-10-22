# Cómo editar videos para Reels/TikTok con Claude (Claude Code)

Guía completa y autocontenida para que **cualquier persona** pueda editar sus videos verticales hablando a cámara con Claude Code: cortes limpios, subtítulos, pantallas divididas, imágenes y videos de apoyo, animaciones sutiles, títulos y portadas.

Sale de editar 12 videos reales y de corregir cada error que apareció en el camino. No necesitas saber editar: le describes a Claude lo que quieres y él escribe y ejecuta los scripts. Esta guía le da a Claude (y a ti) el contexto para hacerlo bien desde el primer intento.

> **Cómo usarla:** guarda este archivo en la carpeta donde vas a trabajar y, al empezar una sesión de Claude Code, dile: *"Lee `Guia para editar videos con Claude.md` y sigue sus reglas."*

---

## Índice

1. [Qué se puede hacer](#1-qué-se-puede-hacer)
2. [Instalación (una sola vez)](#2-instalación-una-sola-vez)
3. [Cómo grabar para que la edición salga bien](#3-cómo-grabar-para-que-la-edición-salga-bien)
4. [Cómo pedirle el video a Claude](#4-cómo-pedirle-el-video-a-claude)
5. [El flujo de trabajo, paso a paso](#5-el-flujo-de-trabajo-paso-a-paso)
6. [Reglas de calidad (no negociables)](#6-reglas-de-calidad-no-negociables)
7. [Formatos y estilos que funcionan](#7-formatos-y-estilos-que-funcionan)
8. [Portadas](#8-portadas)
9. [Checklist antes de entregar](#9-checklist-antes-de-entregar)
10. [Errores típicos y cómo se resolvieron](#10-errores-típicos-y-cómo-se-resolvieron)
11. [Código base (para que Claude no empiece de cero)](#11-código-base-para-que-claude-no-empiece-de-cero)
12. [Glosario](#12-glosario)

---

## 1. Qué se puede hacer

Partiendo de uno o varios clips grabados con el celular (vertical, hablando a cámara):

- **Cortes automáticos**: quitar silencios, muletillas, arranques en falso y repeticiones, sin que se note el corte en el audio.
- **Jump cuts con zoom**: cada corte cambia ligeramente el encuadre (1.0 → 1.08 → 1.0 → 1.14) para darle ritmo.
- **Velocidad** (1.05x o 1.1x) sin cambiar el tono de la voz.
- **Subtítulos** palabra por palabra, con la palabra que se está diciendo resaltada.
- **Título** en los primeros segundos.
- **Pantalla dividida**: tú arriba y abajo una grabación de pantalla, un video de apoyo (B-roll) o una imagen, sincronizados con lo que dices.
- **Píldoras con links** (website, @usuario, nombre de podcast).
- **Animaciones sutiles**: cifras que cuentan, etiquetas con nombres, citas, collages que aparecen uno por uno, resúmenes finales con los links.
- **Tarjeta de título estilo "good work_"**: la imagen se posteriza, aparece un rótulo escrito a máquina y el título grande.
- **Brand look** de una marca (sus colores y su estilo gráfico).
- **Portadas** (banner del reel) que se leen bien en la cuadrícula del perfil.
- **Color intacto**: si grabas en HDR con iPhone, el video final conserva el mismo color.

---

## 2. Instalación (una sola vez)

Probado en **macOS** (Apple Silicon). En Windows o Linux todo funciona salvo la detección de rostro con Apple Vision (ver alternativa abajo).

```bash
# 1. Homebrew (si no lo tienes): https://brew.sh
# 2. Herramientas
brew install ffmpeg cairo python@3.11
pip3 install openai-whisper numpy pillow cairocffi

# 3. Compilador de Swift (para detectar la cara con Apple Vision)
xcode-select --install

# 4. Opcional: capturar páginas web como imagen o video
npx playwright install chromium
```

| Herramienta | Para qué |
|---|---|
| **ffmpeg** | Leer y escribir video, recortar, cambiar velocidad, detectar silencios, medir volumen |
| **Whisper** (modelo `medium`) | Transcribir con tiempos por palabra (en español funciona muy bien) |
| **Python + numpy + Pillow + cairocffi** | Dibujar gráficos, texto y animaciones cuadro a cuadro |
| **Apple Vision** (Swift) | Ubicar la cara en cada toma, para que el encuadre nunca corte la cabeza |
| **Playwright** (opcional) | Capturar una página web completa para mostrarla en el video |

> Si estás en Windows/Linux: la detección de rostro se puede reemplazar por `mediapipe` (Python). Lo demás es igual.

**Carpeta sugerida:**
```
Edición de videos/
├── Guia para editar videos con Claude.md   ← este archivo
└── scripts/
    ├── fx.py            (utilidades compartidas: texto, HDR, codificadores)
    ├── framing.py       (encuadre que no corta la cabeza)
    ├── herramientas/face.swift
    └── video-N-nombre/  (una carpeta por video: edit.py, voice_build.py, render.py, cover.py)
```

---

## 3. Cómo grabar para que la edición salga bien

- **Vertical**, cámara a la altura de los ojos y con **aire arriba de la cabeza** (un palmo). Si la cabeza toca el borde de arriba, no hay forma de agregar ese espacio después: los zooms y las portadas te cortan el pelo.
- **Haz pausas entre frases.** Un silencio claro de medio segundo hace que el corte sea perfecto. Si te equivocas, haz una pausa y repite la frase completa: Claude detecta el arranque en falso y se queda con la segunda versión.
- Graba el **hook aparte** si quieres probar varias versiones (un clip corto de 10 s). Después se une al cuerpo.
- Cuarto silencioso, sin música de fondo.
- Si vas a mostrar una página o app: haz una **grabación de pantalla** limpia (sin notificaciones), o pásale el link a Claude para que la capture.
- iPhone en HDR está bien: se entrega una versión HDR (para IG) y una SDR de respaldo.

---

## 4. Cómo pedirle el video a Claude

### Plantilla

```
Edita este video para IG: ~/Downloads/IMG_XXXX.MOV
(si son varios: hook = IMG_A.MOV, cuerpo = IMG_B.MOV, IMG_C.MOV)

- Título: "[texto]"  (o: sin título / tarjeta estilo good work)
- Velocidad: 1.05x
- Cortes: quitar muletillas, repeticiones y pausas; acortar la parte donde me extiendo
- Apoyo: [ruta del video/imagen] cuando digo "[frase]"  → sin audio
- Links: [website / @usuario] cuando digo "[frase]"
- Animaciones: sutiles, solo cuando aporten
- Estilo: [igual al video anterior / brand look de X / referencia: ruta de captura]
- Portada: sí, con [esta imagen / mi cara] y el título "[texto]"
- Sonido: solo mi voz (sin efectos ni música)
- Guardar en: Descargas
```

### Ejemplos de pedidos reales que funcionaron

- *"Edita este video igual que los de referencia (rutas), con pantalla dividida y la grabación de pantalla abajo. Corta los primeros 8 s y los últimos 2 s del apoyo, velocidad 1.1, título de 5 s, y agrega el link cuando digo 'esta gente'."*
- *"Agrega estas imágenes cuando vaya diciendo [frase → imagen], que todo el video tenga el brand look de [marca], y después de que diga '[frase]' pon la portada con el estilo de este video [referencia]."*
- *"Este tiene que ser de corrido, sin título, solo cortes. Y que cuando diga 'le voy a recomendar estos podcasts' salgan las imágenes una por una y después se quiten."*
- *"Haz un video sobre este artículo [link], con esta imagen de portada y el título '[texto]'. Agrega animaciones sutiles cuando sea necesario."*

### Consejos

- Dale a Claude **referencias visuales** (capturas de otros reels o portadas): copia el estilo con mucha precisión.
- Pide **cambios concretos** ("el video tiembla", "los subtítulos tapan el contenido, súbelos", "el título más directo"). Cada corrección se vuelve una regla para los videos siguientes.
- Prefiere **títulos directos** (una promesa concreta: "3 páginas para que tu website no parezca hecho con IA") en vez de preguntas.

---

## 5. El flujo de trabajo, paso a paso

Este es el proceso que Claude debe seguir. Cada paso incluye cómo se verifica.

### 5.1 Revisar el material
```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,color_transfer:stream_side_data=rotation -of compact video.MOV
# rotation=-90 → vertical; color_transfer=arib-std-b67 → HDR (HLG)
ffmpeg -i video.MOV -vf "fps=1/4,scale=150:-1,tile=13x1" -frames:v 1 hoja.jpg   # hoja de contacto
```
Mirar dónde queda la cara, si hay aire arriba y si los clips de apoyo tienen interfaz que hay que recortar (íconos de like, subtítulos de otro creador, barra de estado, fondo de escritorio).

### 5.2 Transcribir
```bash
ffmpeg -i video.MOV -vn -ac 2 -ar 48000 -c:a pcm_s16le src.wav
whisper src.wav --model medium --language es --word_timestamps True --output_format json
```
- **Nunca** usar `initial_prompt` con la primera frase: Whisper se "come" el comienzo.
- Si una palabra es dudosa, re-transcribir **solo ese fragmento** (3–5 s). Si sigue dudosa, preguntarle al usuario o marcarla en el resumen final.

### 5.3 Detectar pausas y armar "unidades" de habla
```bash
ffmpeg -i src.wav -af silencedetect=n=-25dB:d=0.15 -f null - 2>&1 | grep silence_
```
Cada tramo entre silencios es una **unidad**. Se listan con sus palabras para decidir qué conservar.

**Importante:** algunas "pausas" esconden palabras suaves (un "y", un "que", un nombre). Antes de quitar una pausa, medir su energía cada 30 ms: si en el medio hay valores por encima de −35 dB, hay voz y **no se corta**.

### 5.4 Decidir los cortes
- Quitar: pausas, muletillas ("eeh", "como", "importante" de relleno), **arranques en falso** (frase empezada, pausa, frase repetida completa → quedarse con la segunda), repeticiones ("vean esos manes, esos manes" → una sola) e intros que repiten el hook.
- Cortes **dentro** de una unidad: buscar en la curva de energía un valle (< −30 dB) entre las dos palabras.
- Acortar las partes largas manteniendo la idea principal de cada frase.

### 5.5 Ajustar cada corte al punto más silencioso (`snap`)
Cada borde se mueve al instante con menos energía en la banda de voz (80–600 Hz), dentro de ±60 ms. Así ningún corte cae dentro de una vocal (ver código en la sección 11).

### 5.6 Armar la voz
Empalmes con fundidos cortos (12–25 ms), fundido de 70 ms si el corte cae sobre voz, reducción de ruido suave, **loudnorm lineal en dos pasadas a −15 LUFS** y `atempo` para la velocidad (sección 11).

### 5.7 Re-transcribir la voz final
Se transcribe la voz **ya editada y acelerada**. Así los subtítulos y las animaciones quedan anclados a los tiempos reales del video final. Revisar el texto completo: confirma que no se coló ninguna palabra cortada ni ninguna muletilla.

### 5.8 Storyboard (frase → qué se ve)
Una tabla simple antes de renderizar. Ejemplo:

| Frase | En pantalla |
|---|---|
| "La primera, UIMaxxing" | Pantalla dividida: landing de la página + píldora `uimaxx.ing` |
| "cards, chatbots…" | Recorrido por los componentes |
| "pegarle el siguiente código a Claude Code" | Zoom al comando `npx …` con un recuadro amarillo |

### 5.9 Detectar la cara y fijar el encuadre por toma
Detección con Apple Vision a 6 fps → **un encuadre fijo por toma** (ver sección 6). Nunca seguir la cara cuadro a cuadro.

### 5.10 Previsualizar
Renderizar 12–25 cuadros clave en una hoja de contacto y revisarlos: textos cortados, cosas tapando la cara, subtítulos sobre contenido importante, contraste, tildes completas.

### 5.11 Render final + verificación
- Render HDR + SDR.
- Revisar duración, códec, `color_transfer` y volumen (`ffmpeg -i final.mp4 -af ebur128 -f null -` → ~−15 LUFS).
- Hoja de contacto del video final (un cuadro cada 2–2.5 s) y de cada transición importante.

### 5.12 Portada
Ver sección 8.

### 5.13 Entregar
Nombres nuevos en cada versión (`_v2`, `_v3`) para que el reproductor no muestre una versión vieja en caché. Resumen corto al usuario: qué se cortó, qué se agregó y qué decisiones tomó Claude por su cuenta.

---

## 6. Reglas de calidad (no negociables)

### Audio
- **Solo la voz.** Sin ping, chime, whoosh, pop ni efectos de "anuncio": suenan baratos.
- **Audio de videos de terceros (B-roll): siempre en silencio**, porque choca con la voz.
- Excepción solo si el usuario la pide (por ejemplo, la música de una tarjeta de título copiada de una referencia). En ese caso:
  - medir el volumen de la música relativo a la voz en la referencia y mantener la misma proporción;
  - bajarla 8 dB mientras hay voz;
  - cortarla en seco como en la referencia.
- **Loudnorm lineal** en dos pasadas (−15 LUFS, pico −1.5 dB). El loudnorm dinámico "respira" en las pausas.

### Cortes
- Un sonido raro tipo "trompeta" en los cortes **no es un efecto**: es un corte cayendo dentro de una vocal. Se arregla ajustando cada corte al punto más silencioso y con un fundido de 70 ms sobre la voz.
- Ritmo: ninguna pausa de más de ~0.2 s.

### Color (HDR del iPhone)
- **No retocar el color** salvo que se pida.
- Entregar dos versiones:
  - `_HDR.mp4`: HEVC Main10, HLG, BT.2020, etiqueta `hvc1`. Es la que se sube a Instagram: el color queda idéntico al del teléfono.
  - `_SDR.mp4`: H.264 BT.709, como respaldo.
- Los gráficos y las grabaciones de pantalla (SDR) se convierten a HLG con el blanco al 75% de señal (203 nits, BT.2408), para que no encandilen.

### Encuadre
- **Nunca cortar la cabeza.** El recorte se ancla al borde superior del pelo (la caja de Vision empieza en la frente: sumar ~30% de la altura de la cara) con un 7–9% de aire.
- **Encuadre fijo por toma**, sin seguir la cara cuadro a cuadro: la detección salta cuando la persona se acerca o pasa las manos por la cara, y el video "tiembla". Por toma:
  - x = mediana del centro de la cara;
  - borde de arriba = percentil 15;
  - mentón = percentil 85.

  Dentro de una toma, el recorte solo se mueve con el zoom suave. **Verificar:** menos de ~2 px de movimiento por cuadro.
- Zooms por corte: 1.0 / 1.08 / 1.0 / 1.14, con un pequeño "asentamiento" (+5% que baja en 0.28 s) y una deriva lenta de +3%. Si la persona está muy cerca de la cámara, zooms más suaves.

### Título
- Por defecto, título de **5 s** al inicio, **sin subtítulos encima** (los subtítulos empiezan cuando sale el título).
- Puede ir como texto sobre el video en vivo o como tarjeta posterizada (sección 7.5). Si el usuario pide "de corrido" o "sin título", no se pone.
- Texto **directo** (número + beneficio), no en pregunta.

### Subtítulos
- Bloques de 3–4 palabras (~19 caracteres), que cortan en puntuación y pausas.
- Helvetica Neue Bold ~66 px, blancos con sombra; la **palabra activa en un color de acento** (amarillo `#FFE72E`, o un bloque del color de la marca).
- Posición: a la altura del pecho (y ≈ 1370 de 1920) en pantalla completa. En pantalla dividida, justo debajo de la línea de división (y ≈ 1065) sobre una **placa oscura**, para no tapar el contenido de abajo.
- Dejar libre el 20% inferior del cuadro (ahí va la interfaz de IG).
- Corregir lo que Whisper transcribe mal: nombres de marcas ("Cloud" → Claude, "UA Maxing" → UIMaxxing, "Whisperflow" → Wispr Flow), anglicismos y tildes.

### Velocidad
- La voz usa `atempo` (conserva el tono) y el video se muestrea a la misma velocidad. 1.05x es un buen valor por defecto; 1.1x si el ritmo es lento.

### Apoyo (B-roll, grabaciones de pantalla, imágenes)
- **Recortar la interfaz**: barra de estado, íconos de like/comentarios, subtítulos de otro creador, controles de reproducción y fondo de escritorio. Si una grabación cambia de pantalla, cada pantalla puede llevar su propio recorte.
- Sincronizar cada imagen con la frase exacta que la menciona.
- Si el apoyo dura menos que la sección, desacelerarlo parejo (0.9x) en vez de repetirlo.
- Usar solo los fragmentos buenos (montaje de 4–5 planos de ~1.5 s).

---

## 7. Formatos y estilos que funcionan

### 7.1 Mínimo (cara + subtítulos)
Pantalla completa, jump cuts con zoom, título de 5 s y subtítulos. Ideal para opiniones.

### 7.2 Pantalla dividida + website
- Arriba (1080×960): tú. Abajo (1080×960): grabación de pantalla o video de apoyo, sin audio.
- **Píldora con el link** sobre la línea de división, desde que lo mencionas hasta el final de la sección (fondo negro al 70%, texto blanco y un ícono pequeño).
- Útil para: "esta página hace X", herramientas, apps, onboardings.

### 7.3 Lista de N recomendaciones (herramientas, podcasts, libros)
- Hook en pantalla completa → una sección dividida por ítem, cada una con su píldora → **resumen final** con los N ítems: número en un cuadro de color, nombre, link o autor. Así el espectador puede hacer captura.
- Variación "collage": cuando dices "les voy a recomendar…", las portadas de los ítems **aparecen una por una** alrededor de tu cara (cada ~0.24 s, con un pequeño rebote), se quedan un par de segundos y se van en orden inverso. Mientras está el collage, los subtítulos llevan placa oscura.

### 7.4 Brand look de una marca
- Sacar la paleta del sitio (por ejemplo, con el formato `branding` de Firecrawl). Si la tipografía de la marca no está instalada, reemplazarla por una parecida (Helvetica Neue).
- La palabra activa del subtítulo va sobre un bloque del color de la marca.
- En pantalla dividida: panel del color de la marca, la imagen como tarjeta redondeada con sombra, una etiqueta negra encima ("BROADWAY", "KUMAR") y detalles gráficos propios de la marca.
- El handle de la marca (`@marca`) en píldora cuando dices "síganlos".

### 7.5 Tarjeta de título "good work_" (posterizada)
Basada en las tarjetas del canal *good work_*. Después de la frase que plantea el tema:
1. La imagen se **posteriza**: contraste 1.15, saturación 1.45, brillo 1.12, filtro mediana 5 y **5 niveles por canal**, que dan rosados y pastel. Una paleta adaptativa da todo café, así que no se usa.
2. Un rótulo chico se escribe letra por letra con cursor: `tu marca_` (por ejemplo, `teoría by andrés corrales_`).
3. Aparece el **título grande** en mayúsculas, amarillo `#FFE72E` con borde negro de 7–9 px y sombra.
4. La imagen se congela con un acercamiento lento hasta completar ~4.7 s, y luego corte seco al video normal.

El título debe verse al menos ~1.7 s. Si el congelado cae justo después de un corte, congelar en el último cuadro de la toma anterior, no en el de la siguiente.

### 7.6 Video sobre un artículo / noticia
- Título de 5 s sobre el video en vivo.
- Panel editorial con el look de la publicación:
  - fondo papel (`#F7F7F5`) y tipografía con serifa (New York, Georgia);
  - el titular y el autor;
  - la foto principal con un acercamiento lento.
- **Animaciones sutiles con datos reales del artículo**, cada una cuando se nombra:
  - cifra grande que cuenta hacia arriba, barra fina de progreso y "Fuente: [publicación]";
  - "antes → después" con una flecha que se dibuja;
  - etiqueta con nombre y cargo sobre una foto;
  - cita textual de una fuente en una tarjeta.
- Al final, una píldora con el link y el tiempo de lectura.

### 7.7 Otros que funcionaron
- **Explicativo estilo Vox**: tarjetas de papel crema con grano, marcador amarillo, flechas y círculos dibujados a mano, sellos tipo goma.
- **Texto detrás de la persona**: segmentación de silueta (Apple Vision `VNGeneratePersonSegmentationRequest`) para poner el texto detrás de la cabeza. Solo funciona si hay aire arriba.
- **Estilo tech oscuro**: negro + un color de acento, grilla fina, esquinas de detección de línea, texto que entra palabra por palabra con desenfoque. Ojo: **texto de color oscuro sobre negro no se lee en el teléfono**, así que va texto blanco sobre un bloque de color.

### 7.8 Formato "UI motion" sobre tu propio video (el más reciente)
- Tu video en pantalla completa con tu fondo real (sin lienzo gris) y sin zooms.
- Todos los gráficos en una **franja arriba que no baje de las cejas**. Mide dónde quedan los ojos: en un selfie cercano están en y ≈ 560-600 de 1920.
- **Una sola forma que se transforma** entre estados (tarjeta → página → contador → píldora…), con *springs* en forma cerrada (función pura del tiempo) y el contenido entrando con un fundido corto.
- Interacciones animadas en vez de capturas cuando se explica un producto: chat con "escribiendo…", notificaciones, botones que cambian de estado con un cursor que hace clic, listas que entran una por una.
- Subtítulos simples (una línea, blancos con sombra) y barra de progreso de color en el borde inferior.
- Si recortas a la persona para poner cosas detrás, difumina los bordes laterales de la silueta o se verá una "caja" con el fondo original.
- Antes de un render largo, muestra 2 o 3 opciones de un mismo cuadro y deja que la persona elija.

---

## 8. Portadas

Tamaño **1080×1920**, pero lo importante es el **recorte 4:5 central (y de 285 a 1635)**: es lo que se ve en la cuadrícula del perfil. Ahí tienen que quedar completos el título y la cara.

### Elegir el cuadro
- Medir la nitidez en la zona de la cara (varianza de bordes) y elegir entre los 16 cuadros más nítidos uno con expresión (sonrisa, mirada a cámara).
- **Revisar los ojos**: el cuadro exacto puede caer en un parpadeo, así que extraer 4–6 cuadros vecinos y elegir.
- Si la cabeza toca el borde de arriba: bajar todo el cuadro ~190 px y extender la pared de arriba (estirada y difuminada). Con la posterización o con piezas encima no se nota.

### Tres estilos probados
1. **Posterizada "good work_"**: tu foto posterizada, rótulo chico arriba (`tu marca_`) y título grande amarillo con borde negro en 3–4 líneas del mismo tamaño, debajo de la cara (nunca encima de ojos o boca).
2. **Collage**: tu foto al natural al centro y alrededor rectángulos con las imágenes de lo que mencionas, con sombra suave, montándose un poco sobre los bordes. Texto blanco con borde negro, centrado, tipo caption.
3. **Imagen del tema** (artículo, producto): la foto principal a sangre, con el título amarillo **encima de la cabeza** de la persona de la foto y una sombra suave detrás del texto.

---

## 9. Checklist antes de entregar

- [ ] No quedan arranques en falso, repeticiones ni pausas largas (leer la transcripción de la voz final completa).
- [ ] Ningún corte cae dentro de una vocal.
- [ ] Solo voz (o exactamente el audio que se pidió).
- [ ] Volumen ≈ −15 LUFS.
- [ ] Subtítulos correctos: marcas, nombres propios, tildes.
- [ ] Las tildes de los textos grandes se ven completas (ÁÉÍÓÚ en mayúsculas).
- [ ] La cabeza nunca se corta y el video no tiembla (menos de ~2 px de movimiento por cuadro dentro de una toma).
- [ ] Nada tapa la cara; los subtítulos no tapan el contenido importante del panel de abajo.
- [ ] Textos de al menos ~36–40 px y con buen contraste en un teléfono.
- [ ] Color sin retocar; HDR + SDR entregados.
- [ ] Revisadas las transiciones (sin franjas negras, caras duplicadas ni cuadros de otra toma).
- [ ] Portada revisada en el recorte 4:5.
- [ ] Archivos con nombre nuevo en cada versión.

---

## 10. Errores típicos y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| Sonido tipo "trompeta" en cada zoom | Cortes dentro de vocales | Ajustar cortes al punto más silencioso + fundido de 70 ms |
| Volumen que "respira" en las pausas | Loudnorm dinámico | Loudnorm lineal en dos pasadas |
| Una palabra desaparece después de un corte | La "pausa" tenía una palabra suave | Medir la energía dentro de cada pausa antes de quitarla |
| Whisper inventa o une palabras ("y todo y demás", "le hace") | Habla rápida o arrastrada | Re-transcribir solo ese fragmento; corregir en subtítulos |
| **El video tiembla** | Encuadre siguiendo la detección de cara cuadro a cuadro | Encuadre fijo por toma |
| La cabeza se corta arriba | Caja de la cara sin pelo / poco aire | Sumar ~30% de la cara hacia arriba + 7–9% de aire |
| Tildes cortadas ("CAMPANAS") | El lienzo del texto no dejaba espacio arriba | Margen extra para los acentos al dibujar texto |
| Tilde mal ubicada al dibujar letra por letra | Se dibujaba carácter por carácter | Dibujar la palabra completa cuando no hay tracking |
| Subtítulo ilegible sobre una imagen clara | Texto blanco sobre fondo blanco | Placa oscura detrás del subtítulo |
| Subtítulos tapando la grabación de abajo | Posición muy baja | Subirlos justo debajo de la línea de división |
| Texto de color ilegible en el teléfono | Azul o morado oscuro sobre negro | Texto blanco sobre un bloque de color |
| Franja negra o cara duplicada en una transición | Panel deslizándose sobre la toma anterior | Corte seco |
| Cuadro de otra toma durante una pausa congelada | El congelado caía después del corte | Congelar en el último cuadro de la toma anterior |
| Valores inválidos (NaN) en la mitad de abajo | Memoria sin inicializar (`np.empty`) bajo un panel opaco | Inicializar con `np.zeros` |
| Colores raros en la conversión a HDR | Bug de `numpy @` (matmul) en algunos macOS | Multiplicación de matriz explícita |
| El usuario sigue viendo/oyendo la versión vieja | Caché del reproductor | Nombre de archivo nuevo en cada entrega |
| Portada con los ojos cerrados | El cuadro exacto cae en un parpadeo | Revisar cuadros vecinos |
| Música de un clip de terceros chocando con la voz | Audio del B-roll | B-roll siempre en silencio |

---

## 11. Código base (para que Claude no empiece de cero)

Fragmentos esenciales y probados. Claude puede armar el resto (dibujo de gráficos, layouts) a partir de esto.

### 11.1 Detección de cara (Apple Vision) — `herramientas/face.swift`
```swift
import Foundation
import Vision
import ImageIO
// uso: face <carpeta con NNNNN.jpg> -> imprime "indice x y w h" (normalizado, origen arriba-izquierda) de la cara más grande
let dir = URL(fileURLWithPath: CommandLine.arguments[1])
let files = try FileManager.default.contentsOfDirectory(atPath: dir.path).filter { $0.hasSuffix(".jpg") }.sorted()
let req = VNDetectFaceRectanglesRequest()
for f in files {
    autoreleasepool {
        guard let src = CGImageSourceCreateWithURL(dir.appendingPathComponent(f) as CFURL, nil),
              let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { return }
        try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
        let idx = f.replacingOccurrences(of: ".jpg", with: "")
        if let best = (req.results ?? []).max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }) {
            let b = best.boundingBox
            print("\(idx) \(b.origin.x) \(1 - b.origin.y - b.height) \(b.width) \(b.height)")
        } else { print("\(idx) nan nan nan nan") }
    }
}
```
```bash
swiftc -O face.swift -o face
mkdir ff && ffmpeg -i video.MOV -vf "fps=6,scale=720:1280" -q:v 4 ff/%05d.jpg
./face ff > faces.txt
```

### 11.2 Encuadre fijo por toma que nunca corta la cabeza
```python
import numpy as np

def take_box(face_t, face_b, lo, hi):
    """face_t: tiempos (s); face_b: cajas [x, y, w, h] en px de la fuente. Una caja robusta por toma [lo, hi]."""
    m = (face_t >= lo) & (face_t <= hi)
    b = face_b[m]
    cx = np.median(b[:, 0] + b[:, 2] / 2); fw = np.median(b[:, 2])
    top = np.percentile(b[:, 1], 15); chin = np.percentile(b[:, 1] + b[:, 3], 85); h = chin - top
    return (cx - fw / 2, top - 0.12 * h, fw, h * 1.12)        # margen extra para el pelo

def head_crop(face, zoom, panel=(1080, 1920), sw=1440, sh=2560, top_air=0.09, chin_max=0.90):
    """recorte anclado arriba de la cabeza; si el mentón quedaría afuera, abre el zoom"""
    fx_, fy, fw, fh = face
    head_top = fy - 0.30 * fh; chin = fy + fh; pw, ph = panel; z = zoom
    for _ in range(12):
        cw = sw / z; ch = cw * ph / pw
        if ch > sh: ch = sh; cw = ch * pw / ph
        y0 = head_top - top_air * ch
        if chin <= y0 + chin_max * ch or z <= 1.0: break
        z = max(1.0, z - 0.05)
    x0 = min(max(fx_ + fw / 2 - cw / 2, 0), sw - cw); y0 = min(max(y0, 0), sh - ch)
    return (x0, y0, x0 + cw, y0 + ch)
```

### 11.3 Ajustar cada corte al punto más silencioso
```python
import numpy as np, wave
def load(path):
    w = wave.open(path); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768
    return x, sr
def voiced_db(x, sr, t):                       # energía en la banda de voz (80–600 Hz), ventana de 10 ms
    seg = x[int(t * sr):int(t * sr) + 480]
    if len(seg) < 480: return 0
    F = np.fft.rfftfreq(480, 1 / sr); band = (F > 80) & (F < 600)
    return 20 * np.log10(np.sqrt((np.abs(np.fft.rfft(seg * np.hanning(480)))[band] ** 2).mean()) + 1e-9)
def snap(segments, x, sr):
    """segments: [(inicio, fin), ...] en segundos de la fuente"""
    out = []
    for a, b in segments:
        a2 = min(np.arange(max(0, a - 0.06), a + 0.03, 0.005), key=lambda t: voiced_db(x, sr, t))
        b2 = min(np.arange(b - 0.03, b + 0.06, 0.005), key=lambda t: voiced_db(x, sr, t))
        out.append((float(a2), float(b2)))
    return out
```

### 11.4 Armar la voz (fundidos, ruido, loudnorm lineal, velocidad)
```python
import json, subprocess
# 1) pegar los segmentos con fundido de entrada (12–25 ms) y de salida (12 ms, o 70 ms si el borde cae sobre voz)
#    -> voice_raw.wav
run = lambda a: subprocess.run(a, capture_output=True, text=True)
run(['ffmpeg', '-y', '-i', 'voice_raw.wav', '-af', 'highpass=f=80,afftdn=nr=8:nf=-45:tn=1', 'voice_dn.wav'])
r = run(['ffmpeg', '-i', 'voice_dn.wav', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
af = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,atempo=1.05")
run(['ffmpeg', '-y', '-i', 'voice_dn.wav', '-af', af, '-ar', '48000', '-c:a', 'pcm_s16le', 'voice_final.wav'])
```

### 11.5 Leer video HDR del iPhone y escribir HDR + SDR
```python
import subprocess
W, H, FPS = 1080, 1920, 30
def hlg_reader(path, w=1440, h=2560):
    """cuadros de la fuente HLG como señal HLG en RGB BT.2020 (rango completo, 16 bits)"""
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf',
           f'fps=30,scale={w}:{h}:in_color_matrix=bt2020:in_range=tv:out_range=pc:flags=bicubic+accurate_rnd+full_chroma_int,format=rgb48le',
           '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 6)
    while True:
        b = p.stdout.read(w * h * 6)
        if len(b) < w * h * 6: break
        yield b

def encoders(out_hdr, out_sdr, audio):
    common = ['-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)]
    hdr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb48le', '-color_range', 'pc', '-i', '-', '-i', audio,
        '-vf', 'scale=out_color_matrix=bt2020:in_range=pc:out_range=tv:flags=bicubic+accurate_rnd,format=yuv420p10le',
        '-c:v', 'libx265', '-crf', '17', '-preset', 'medium', '-tag:v', 'hvc1',
        '-x265-params', 'colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error',
        '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_hdr], stdin=subprocess.PIPE)
    sdr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y'] + common + ['-pix_fmt', 'rgb24', '-i', '-', '-i', audio,
        '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
        '-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out_sdr], stdin=subprocess.PIPE)
    return hdr, sdr
```

### 11.6 Gráficos SDR → HLG (para que no encandilen en HDR)
```python
import numpy as np, math
a_, b_, c_ = 0.17883277, 0.28466892, 0.55991073
EREF = (math.exp((0.75 - c_) / a_) + b_) / 12                     # blanco de gráficos al 75% de señal HLG (203 nits)
M = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]], np.float32)   # BT.709 -> BT.2020
LUT = np.where(np.arange(256) / 255 <= 0.04045, (np.arange(256) / 255) / 12.92, ((np.arange(256) / 255 + 0.055) / 1.055) ** 2.4).astype(np.float32)
def srgb8_to_hlg(rgb8):
    l = LUT[rgb8]
    lin = np.stack([l[..., 0] * M[i, 0] + l[..., 1] * M[i, 1] + l[..., 2] * M[i, 2] for i in range(3)], -1)   # sin "@" (bug en macOS)
    E = np.clip(lin * EREF, 1e-6, 1)
    return np.where(E <= 1 / 12, np.sqrt(3 * E), a_ * np.log(np.maximum(12 * E - b_, 1e-6)) + c_).astype(np.float32)
```
En el render, cada cuadro se arma dos veces: la versión SDR (la señal HLG mostrada tal cual + gráficos en sRGB) y la HDR (señal HLG + gráficos convertidos con `srgb8_to_hlg`).

### 11.7 Posterizar (tarjeta y portada "good work_")
```python
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
def posterize(rgb8):
    im = Image.fromarray(rgb8).resize((540, 960), Image.BILINEAR)
    im = ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.45)).enhance(1.12)
    im = im.filter(ImageFilter.MedianFilter(5))
    a = np.asarray(im).astype(np.float32) / 255; L = 5
    q = Image.fromarray((np.round(a * (L - 1)) / (L - 1) * 255).astype(np.uint8)).filter(ImageFilter.ModeFilter(3))
    return np.asarray(q.resize((1080, 1920), Image.BILINEAR))
```

### 11.8 Texto amarillo con borde negro (títulos y portadas)
```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HN = '/System/Library/Fonts/HelveticaNeue.ttc'     # índice 1 = Bold, 0 = Regular
def stroked(txt, size, fill=(255, 231, 46), stroke=8, idx=1):
    f = ImageFont.truetype(HN, size, index=idx)
    tw = f.getlength(txt); asc, desc = f.getmetrics(); pad = stroke + 24
    img = Image.new('RGBA', (int(tw + 2 * pad), int(asc + desc + 2 * pad)), (0, 0, 0, 0))
    sh = img.copy(); ImageDraw.Draw(sh).text((pad + 5, pad + 6), txt, font=f, fill=(0, 0, 0, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(img).text((pad, pad), txt, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return img, pad, tw
# Varias líneas: calcular una sola escala para todas  s = min(1, ancho_max / max(anchos))
```

### 11.9 Capturar una página web (para mostrarla en el video)
```javascript
// node cult_shot.js   (requiere playwright)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2, colorScheme: 'dark' });
  const p = await ctx.newPage();
  await p.goto('https://ejemplo.com/pagina', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  await p.screenshot({ path: 'pagina.png', fullPage: true });
  await b.close();
})();
```
Luego se anima con un paneo (recorte que se desplaza hacia la parte que se menciona) y se resalta lo importante con un recuadro.

### 11.10 Comandos útiles de verificación
```bash
# volumen integrado (objetivo ≈ -15 LUFS)
ffmpeg -i final.mp4 -af ebur128 -f null - 2>&1 | grep -A1 Integrated
# hoja de contacto del resultado (un cuadro cada 2.5 s)
ffmpeg -i final_SDR.mp4 -vf "fps=1/2.5,scale=150:267,tile=13x2" -frames:v 1 final.jpg
# energía de un tramo (para buscar valles entre palabras)
python3 -c "import wave,numpy as np;w=wave.open('src.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,2).mean(1)/32768;print(' '.join('%.2f:%d'%(t,20*np.log10(np.sqrt((x[int(t*sr):int((t+.03)*sr)]**2).mean())+1e-9)) for t in np.arange(10,12,.03)))"
```

---

## 12. Glosario

- **Hook**: la primera frase o el primer clip, que tiene que enganchar en 1–3 s.
- **Jump cut**: corte dentro de la misma toma; el cambio de zoom lo disimula y le da ritmo.
- **B-roll / apoyo**: imagen o video que acompaña lo que dices.
- **Pantalla dividida (split)**: tú arriba y el apoyo abajo, cada uno en 1080×960.
- **Píldora**: etiqueta redondeada con un link o un nombre.
- **Placa**: fondo oscuro redondeado detrás de un subtítulo para que se lea.
- **Arranque en falso**: frase que se empieza, se corta y se repite.
- **LUFS**: unidad de volumen percibido. −15 LUFS funciona bien en Reels.
- **HDR / HLG**: el formato de color de alto rango del iPhone. **SDR**: el formato normal.
- **Recorte 4:5**: la parte central de la portada que se ve en la cuadrícula del perfil de Instagram.
- **Posterizar**: reducir los colores de una imagen a pocos tonos planos (efecto "recorte de papel").
