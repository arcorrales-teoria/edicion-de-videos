# Guía de edición de videos para redes (IG Reels)

> **Ubicación (2026-10-09):** esta guía vive en `Edición de videos/Videos personas/`. Los scripts están en `Videos personas/scripts/` (el acceso `Edición de videos/scripts` sigue funcionando). Las demos de producto tienen su propia guía en `Demos de producto/`.


Todo lo que aprendimos editando videos con Claude: cómo pedirlos, el flujo de trabajo, las reglas fijas (sonido, cortes, color), los estilos visuales que ya funcionaron, los errores que aparecieron y cómo se resolvieron.

Última actualización: 22 de octubre de 2026.

---

## 1. Reglas fijas (no negociables)

Estas reglas salen de correcciones reales. Aplican a **todos** los videos, salvo que se pida otra cosa explícitamente.

### Sonido
- **Solo mi voz + clicks secos.** Nada más.
- **Nunca** ping, chime, ding, notificación, sparkle ni ningún tono tipo "anuncio". El ping se escuchaba como una trompeta de anuncio.
- **Nunca** whoosh (sonaba raro en los zooms) ni pop (se escuchaba terrible).
- Si hay click, que sea **nítido, corto y suave** (tipo clic de mouse: golpe de ~6 ms en la banda de 2 a 7 kHz, sin tono) y **solo en los saltos de zoom y las transiciones**, no en cada elemento que aparece. Menos es más: unos 16 clicks en un video de 40 s.
- Clicks que **no** sirven: `click-soft.mp3` / `click.mp3` (en realidad son dos golpes con cola de 83 ms) y `key-press.mp3` (es un "tok" grave y hueco de ~200 Hz).
- Si hay música o audio de un video de terceros (B-roll), **va en silencio**. Choca con la voz.
- **Única excepción pedida**: la tarjeta de título good work_ lleva la **misma pista de la referencia** (`Twitter Video Downloader (4).mp4`, de 36.19 a 40.87 s, base de bajo con un golpe por segundo). Arranca cuando aparece la tarjeta, baja 8 dB mientras sigo hablando, queda 1.5 LU por debajo de la voz (como en la referencia) y termina con corte seco. La tarjeta dura lo mismo que la pista (4.7 s). Archivo: `scripts/video-9-ramp/card_music_full.wav`.

### Cortes de audio (el problema de la "trompeta")
El sonido raro tipo trompeta que aparecía en cada zoom **no era un efecto**: eran los cortes cayendo en medio de una vocal ("increíbleee", "eeeh"). Para que no vuelva a pasar:
1. Cada punto de corte se mueve al instante **más silencioso** cercano (±150 ms), midiendo la energía de la banda de voz (80 a 600 Hz).
2. Si un corte igual cae sobre una vocal, esa toma se **apaga en 70 ms** dentro de la misma toma. Nunca se "presta" audio de después del corte.
3. Fundidos cortos (12 a 25 ms) en cada empalme.
4. Reducción de ruido suave (`afftdn=nr=8`) para que el ruido del cuarto no salte entre tomas.
5. Volumen con **loudnorm lineal en dos pasadas** (−15 LUFS). El loudnorm dinámico "respira" en las pausas y se oye raro.

### Color
- **No retocar el color** salvo que se pida.
- Los videos del iPhone vienen en **HDR (HLG, BT.2020, 10 bits)**. **Desde el 13 oct 2026 se entrega solo la versión HDR** (`_HDR.mp4`: HEVC Main10, HLG, etiqueta `hvc1`). **Nada de SDR**: no generar ni dejar archivos `_SDR.mp4` en Descargas.
- Los gráficos se convierten a HLG con blanco de referencia al 75% de señal (203 nits, BT.2408) para que no encandilen.

### Encuadre de la cara (nunca cortar la cabeza)
- La cara se ubica con **detección de rostro de Apple Vision** (`scripts/herramientas/face.swift`, 6 cuadros por segundo) y el recorte se calcula con `scripts/framing.py`.
- El recorte se ancla a la parte de arriba de la cabeza (pelo incluido) con un 7% de aire, no al centro del cuadro. Sigue la cara suavemente dentro de cada toma.
- Zooms moderados en los saltos (1.0, 1.1, 1.0, 1.16). Si con el zoom se corta el mentón, el recorte se abre solo.
- Si en la grabación original la cabeza ya toca el borde de arriba, no hay más imagen: conviene grabar con un poco de aire sobre la cabeza.

### Título
- **Todo video lleva un título durante los primeros 5 segundos**, sin subtítulos encima. Los subtítulos empiezan cuando sale el título.
- El título resume la idea del video en 2 o 3 líneas cortas (ej. "La campaña de QuikTrip es una clase de marketing").

### Velocidad
- Si se pide acelerar (ej. 1.1x): el video se muestrea a 1.1x y la voz usa `atempo=1.1` (conserva el tono). Transcribir la voz ya acelerada para que subtítulos y animaciones queden en el tiempo final.

### Cortes y ritmo
- Quitar arranques en falso, muletillas y silencios de más de ~0.2 s.
- En cada salto de corte cambia el encuadre: ciclo de zoom 1.0 → 1.2 → 1.08 → 1.3, con un pequeño "asentamiento" (+5% que baja en 0.28 s) y deriva lenta de +3% durante la toma.
- Transcribir con Whisper `medium`. Nunca usar `initial_prompt` con la frase inicial, porque se "come" el comienzo.
- Verificar palabras dudosas re-transcribiendo solo ese fragmento.

---

## 2. Cómo pedir un video (plantilla)

Copia y completa:

```
Edita este video para IG: /Users/acorrales/Downloads/IMG_XXXX.MOV

- Hook: [qué frase o qué video va primero / título que debe aparecer]
- Estilo: [Vox (papel, marcador amarillo) | Fraud Prevention Series azul | otro]
- B-roll: [ruta del video de apoyo] → usar ~30 s, sin audio, sincronizado con lo que digo
- Elementos detrás de mí: [sí/no, en qué momentos]
- Sonido: solo voz + clicks nítidos en zooms y transiciones (ver reglas)
- Color: no retocar (entregar HDR + SDR)
- Portada: [sí/no, texto]
- Guardar en: Descargas
```

---

## 3. Flujo de trabajo (paso a paso)

1. **Revisar el material**: duración, rotación (`rotation=-90` = vertical), HDR o SDR, y una hoja de contacto de cuadros para ver dónde queda la cara.
2. **Transcribir** con Whisper medium con tiempos por palabra.
3. **Definir el corte**: rangos a conservar, quitar arranques en falso y repeticiones, y detectar silencios (`silencedetect -25 dB`). **Ajustar cada corte al punto más silencioso** (regla de la sección 1).
4. **Armar la voz**: empalmes con fundido, reducción de ruido suave y loudnorm lineal.
5. **Re-transcribir la voz editada** para tener los tiempos exactos en la línea de tiempo final (subtítulos y animaciones se anclan a palabras).
6. **Escribir el storyboard**: qué pasa en pantalla por cada frase (tabla frase → visual).
7. **Previsualizar** 20 a 35 cuadros clave en hojas de contacto y corregir (textos cortados, cosas tapando la cara, contraste).
8. **Render final** + verificación de cuadros en las transiciones.
9. **Audio aparte**: los cambios de sonido no requieren re-renderizar la imagen; solo se re-mezcla y se vuelve a unir (`-c:v copy`).
10. **Portada** (si se pide).

---

## 4. Subtítulos

- Bloques de hasta 3 o 4 palabras (o ~16 caracteres), cortando en puntuación y pausas.
- La palabra que se está diciendo se resalta:
  - Estilo Vox: texto en amarillo `#FFD84D`.
  - Estilo FPS azul: bloque azul detrás de la palabra con texto blanco.
- Posición: a la altura del pecho (~y 1400 de 1920) en tomas de cara; más abajo en tarjetas. Dejar libre el ~20% inferior (ahí va la interfaz de IG).
- Corregir a mano lo que Whisper transcribe mal:
  - "Cloud" → Claude
  - "prometer" → promptear
  - "capcoat" → CapCut
  - "Bad Water" → MUD\WTR
  - "leen" → le den

---

## 5. Estilos visuales que ya funcionaron

### A. Estilo Vox explicativo (videos IMG_8840 e IMG_8841)
- Tarjetas de papel crema con textura y grano, marcador amarillo `#FFD84D` y acento terracota `#D97757`.
- Tipografías: Georgia Bold (titulares), DIN Condensed Bold (etiquetas y sellos), Bradley Hand (notas a mano), Montserrat ExtraBold (subtítulos), Menlo (terminal).
- Elementos: círculos y flechas dibujados a mano (se dibujan solos), sellos tipo goma ("GAME CHANGER", "SIN EXCUSAS"), checklist, terminal de Claude Code, planos divididos (gráfico arriba, cara abajo), cortes a pantalla completa de papel.

### B. Texto detrás de mí + B-roll (video IMG_8850 + IMG_8851)
- Segmentación de persona con **Apple Vision** (`scripts/herramientas/segment.swift`): recorte de silueta por cuadro para poner texto detrás de la cabeza.
- Funciona solo si hay aire arriba de la cabeza. Si la cabeza toca el borde superior, no se puede.
- B-roll de terceros en pantalla completa con mi silueta recortada en una esquina (estilo reacción).

### C. Estilo Fraud Prevention Series en azul (video IMG_8856)
Basado en `Truora Marketing/Campañas/Fraud Prevention Series/00 Diseño y assets` y el proyecto `fraud-series-hyperframes`, pero **en azul, no morado**, para que no se parezca a Truora:
- Paleta: negro `#000`, azul `#0066FF` (reemplaza al morado `#2F09FE` de Truora), blanco `#FAFBFF` y gris `#8B8EA8`.
- Tipografías: Host Grotesk (mezclar pesos 800 y 300 en la misma frase) y JetBrains Mono en mayúscula con tracking 0.2 em para etiquetas (desde `fraud-series-hyperframes/assets/fonts`).
- Elementos:
  - grilla de 1 px que deriva
  - esquinas de detección **de línea**
  - HUD en las esquinas
  - paneles de vidrio
  - texto que entra palabra por palabra con blur
  - barrido de grilla pixelada azul como transición
  - cintas diagonales con términos
  - grafo de nodos conectados con pulsos
  - contador animado (ej. 10x)
  - plano dividido con opciones y resaltado que salta
- Sin logo de Truora ni "Fraud Prevention Series" en videos personales.
- **Texto azul sobre negro no se lee en el teléfono** → usar texto blanco sobre un bloque azul.
- **Nada de cuadrados/píxeles alrededor de la cara.** Los píxeles decorativos van solo en tarjetas negras y en la transición.

### D. Pantalla dividida (referencia `IMG_8876.PNG`, video IMG_8875)
- Arriba (1080 x 960): yo en encuadre cerrado, con zoom distinto en cada salto de corte.
- Abajo (1080 x 960): el video de apoyo o la grabación de pantalla, **sin audio**, recortado para sacar la interfaz de la app (íconos de like, comentarios, título y caption).
- Título de 5 s sobre la línea de división: Helvetica Neue Bold (índice 1 de `HelveticaNeue.ttc`), 104 px, letras juntas (-0.055 em), blanco con sombra, sobre una franja negra al 36%.
- Subtítulos: Helvetica Neue Bold 62 px, blancos con sombra, una sola línea en la mitad inferior (y = 1300). Sin resaltado de palabra y sin animaciones extra.
- Si el apoyo dura menos que el video: primera pasada a velocidad real y segunda pasada más lenta con un recorte más cerrado, para que no se note la repetición.
- Si se menciona una página o producto, agregar el **website** como píldora sobre la línea de división desde que se menciona ("se las dejo acá") hasta el final, con un pulso suave cuando se dice "website".
- Recortar la grabación de pantalla para dejar solo el contenido (sin barra de estado, captions del creador, íconos de like ni controles de reproducción). Evitar los segundos donde aparecen controles de pausa o de avance.
- Si el apoyo es SDR (grabación de pantalla) y el video es HDR, el apoyo se convierte a HLG igual que los gráficos.
- Si la grabación de pantalla es de una app oscura (texto blanco sobre negro), los subtítulos llevan una **placa negra redondeada al 85%** detrás; si no, se mezclan con los textos de la interfaz.
- Si el apoyo dura un poco menos que el video, se desacelera parejo (ej. 0.9x) para mostrar todo el proceso una sola vez. Cada pantalla puede tener su propio recorte (más cerrado en pantallas con poco contenido).
- Si estoy muy cerca de la cámara: zooms más suaves (1.0, 1.07, 1.0, 1.12) y más aire arriba (caja de la cara +12% hacia arriba, `top_air=0.09`).
- **Encuadre fijo por toma** (no seguir la cara cuadro a cuadro): la detección de Apple Vision salta cuando me acerco o paso las manos por la cara y el video "tiembla". Se calcula un encuadre por toma (mediana en x, percentil 15 arriba / 85 en el mentón) y solo se mueve con el zoom suave. Verificar: dentro de una toma el recorte se mueve menos de ~2 px por cuadro.
- Si la grabación de abajo tiene mucho contenido, los **subtítulos van justo debajo de la píldora del website (y ≈ 1065)**, no a 1300, para no tapar el contenido.

### E. Portada "good work_" → "teoría by andrés corrales_" (desde el video IMG_8913, 3 oct 2026)
**Estilo de portada por defecto para todos los videos.** Referencia: las portadas y el cierre del canal *good work_* (Dan Toomey).
- Foto mía **posterizada**: contraste 1.15, saturación 1.45, brillo 1.12, filtro mediana 5 y **5 niveles por canal** (da rosados y pastel como la referencia; la paleta adaptativa daba todo café).
- Arriba a la izquierda, chico: `teoría by andrés corrales_` (Helvetica Neue regular, amarillo `#FFE72E` con borde negro).
- Título grande en MAYÚSCULAS, Helvetica Neue Bold, amarillo `#FFE72E`, borde negro de 7 a 9 px y sombra; 2 o 3 líneas que llenen el ancho.
- Todo (cara completa + título) dentro del recorte 4:5 (y de 285 a 1635).
- **Dentro del video**: después de la frase que plantea el tema, la imagen se posteriza, el rótulo se escribe letra por letra con cursor `_` y aparece el título de golpe; pausa congelada de 1.5 s (sin audio) y vuelve el video normal. El título debe verse al menos ~1.7 s.
- Script: `scripts/video-9-ramp/cover9.py` (portada) y `card_text()` / `posterize()` en `render9.py`.

### F. Brand look de una marca (Ramp, video IMG_8913)
- Colores de la marca sacados del sitio (Ramp: lima `#E4F222`, tinta `#1A1919`). Su tipografía (Lausanne) no está instalada → Helvetica Neue.
- Subtítulos: blancos en negrita y la palabra activa sobre bloque lima con texto tinta.
- Cuando se menciona una imagen: pantalla dividida, yo arriba y abajo **panel lima** con la imagen como tarjeta redondeada, etiqueta negra arriba (ej. "BROADWAY") y cuadritos decorativos como en sus gráficos. En el seam, los subtítulos llevan placa tinta.
- Handle de la marca (`@tryramp`) en píldora lima arriba desde que digo "sígalos".

### G. Portada collage + collage en la intro (video IMG_8930, referencia: reel de @marianariveraarenas)
- Portada: mi foto **sin posterizar** al centro y alrededor imágenes rectangulares (portadas/episodios), sin bordes redondeados, con sombra suave, montándose un poco sobre los bordes de la cabeza pero sin tapar ojos ni boca. Texto **blanco con borde negro**, centrado, en minúsculas tipo caption (Helvetica Neue Bold 74 px, borde 6 px). Script: `scripts/video-11-podcasts/cover11b.py`.
- En el video: cuando digo "le voy a recomendar estos…", las mismas imágenes **aparecen una por una** alrededor de mi cara (cada 0.24 s, con un pequeño rebote) y después **se quitan** en orden inverso. Mientras está el collage, los subtítulos llevan placa oscura. Función `collage()` en `render11.py`.

### H. Video sobre un artículo (Colossus / Nubank, video IMG_8938)
- Título de 5 s **sobre el video en vivo** (sin congelar ni posterizar): rótulo `teoría by andrés corrales_` escrito letra por letra + título amarillo con borde negro en la mitad de abajo.
- Panel editorial estilo de la publicación: fondo papel `#F7F7F5`, serif **New York** (fuente variable del sistema, `set_variation_by_name('Semibold')`), acento del producto (morado Nubank `#820AD1`).
- Animaciones sutiles con **datos reales del artículo**, cada una cuando la nombro: cifra grande que cuenta hacia arriba + barra fina + fuente ("Fuente: Colossus"). Etiquetas con los nombres de los fundadores en pantalla completa, cita de un inversor sobre la foto, píldora con el link al final.
- Portada: la foto principal del artículo a sangre, con el título amarillo **encima de la cabeza** de la persona (nunca sobre la cara). Script: `scripts/video-12-nubank/cover12.py`.

### I. Formato actual (desde el 13 oct 2026, videos IMG_9008 e IMG_9010): **usar este por defecto**
Referencias de motion: `Referencia 1.mp4` (una sola forma que se transforma, estilo Dribbble), los prompts de "UI motion" y "Apple keynote" (springs, sin rebotes exagerados, contenido que cambia con un fundido corto) y el video de VEED (persona adelante, cosas detrás).
- **Fondo**: el cuarto real, **sin lienzo ni fondo gris**. Se rechazaron el fondo plano y el fondo desenfocado; el usuario eligió la **opción C**: yo en tamaño completo con mi cuarto y los gráficos encima.
- **Franja de gráficos**: todo va arriba, **por encima de los ojos**, de y = 46 a y ≈ 430 (máx. 384 px de alto y 1000 de ancho). Las tarjetas se escalan solas para caber. Si algo baja de y ≈ 470 tapa cejas y gafas.
- **Una sola forma que se transforma**: una tarjeta (blanca, negra o del color de la app) cuyo x, y, ancho, alto, radio y color cambian con *springs* entre estados. El contenido de cada estado entra con un fundido corto + 14 px de subida y sale en 0.12 s. Ejemplo: perfil → página del producto → tweets → contador 0→100 → píldora negra cuyo texto cambia ("Partnership programs" → "Programas de creadores UGC" → "Ads") → LinkedIn.
- **Springs en forma cerrada** (función pura del tiempo): `1 - e^(-ζωx)(cos ω_d x + ζω/ω_d sin ω_d x)`, ω ≈ 12, ζ ≈ 0.86 (apenas sobrepaso). Un valor que cambia de objetivo varias veces es la suma de un spring por cambio.
- **Interacciones animadas** en lugar de capturas cuando se explica un producto: chat de WhatsApp con "escribiendo…" (tres puntos), burbujas que entran y texto que se escribe, scroll automático para que el último mensaje quede visible; notificaciones que bajan una por una; correo con los importantes resaltados; apps conectadas a un centro con pulsos de datos; ruta de vuelo que se dibuja; botón "Seguir" → "Siguiendo" con cursor que hace clic; comentario donde se escribe "WhatsApp" y se envía; lista de espera con clic.
- **Etiquetas de sección**: píldora blanca "01 · Nombre" / "02 · Nombre" debajo de la franja cuando hay una lista.
- **Tipografía**: Geist (`~/Library/Fonts/Geist-*.otf`) para UI y subtítulos; serif New York para marcas editoriales (ej. Instinct).
- **Marca del producto**: sus colores y su logo (Instinct: blanco y tinta, arena `#E6DBD1`, el muñequito de palitos de su web; el chat en el tema oscuro de WhatsApp).
- **Cuando el usuario pide "los colores y valores de la marca"** (IMG_9025, Graza, 14 oct 2026): toda la edición se viste con la marca, no solo las tarjetas. Paleta sacada de sus capturas con un cuentagotas (Graza: crema `#F3E7DA`, tinta oliva `#3D4230`, lima `#D4DF55`, verde `#B0ED8D`); su logo y su ícono se extraen de las capturas como máscara alfa y se tiñen. Tipografía que imite la suya con lo que hay instalado (Graza: New York comprimida al 80% en horizontal ≈ su serif alta; Courier New Bold ≈ su mono de botones). Subtítulos en una píldora del color de fondo de la marca con borde de su tinta; título en su serif con la palabra clave en su color de acento; barra de progreso en su color de acento (lima) en vez de azul. Se recrean sus propios componentes como interacciones (el pop-up de Graza con botones lima que se cliquean: "TASTE / BRAND / NARRATIVA"; etiquetas tipo `*SQUISH*` `*DRIP*`).
- **Fragmentos de un video de otra persona** (reel de referencia): sin su audio y sin sus subtítulos. Sus subtítulos quemados van en el centro (y ≈ 1000-1150 en una grabación de 1170×2532): se recorta la ventana de arriba (y 270-990) o la de abajo (y 1180-1990), siempre con x < 1010 para no llevarse los íconos de Instagram de la derecha; las tomas sin subtítulo (productos) pueden ir completas. Se usan solo tomas de producto/b-roll, nunca la cara del otro creador. Van dentro de la tarjeta que se transforma.
- **Hook grabado aparte** (IMG_9027 reemplazó el arranque de IMG_9025): va como fuente 'b' en el mismo `RAW`; se quita del video principal la frase que repetía el hook ("esta es la historia de Graza") y la forma entra justo en "Número uno" para que el cambio de toma se sienta integrado.
- **Lanzamientos de producto con look propio** (IMG_9044, Tesla Roadster, 16 oct 2026): se copia el *look* del lanzamiento, no solo los colores. Roadster: escenario negro, tipografía Saira (Google Fonts, OFL, descargada en `fonts/` del video) ≈ la de tesla.com/roadster, líneas finas doradas bajo los títulos, el logo ROADSTER dorado extraído con sus colores, íconos de su página (aero activa, propulsores, succión) traducidos, barra de progreso con la luz roja de la cola. Se permiten **pantallas completas** cortas (negro + clip a lo ancho + logo + explicación) para lo más fuerte del producto y para el final, y **montajes de memes** sobre un velo oscuro (capturas que caen apiladas, la anterior se oscurece). La gráfica de su página (downforce vs. velocidad) se reutiliza como metáfora animada (viralidad vs. "que hablen de usted" hasta 99%).
- **Tomas al aire libre** (cielo claro, chaqueta clara): los subtítulos van sobre una placa oscura y el título sobre un degradado negro abajo; si no, el blanco no se lee. Con ruido de fondo constante (piso ≈ -22 dB) `silencedetect` no encuentra pausas: se leen en la envolvente de energía (umbral = percentil 10 + 4 dB).
- **Ritmo (17 oct 2026, nota del usuario sobre el Roadster)**: el Roadster (video 19) es **el modelo a usar**, pero "que las animaciones no aparezcan y desaparezcan tan rápido". Cada tarjeta se queda **≥ 3 s** (mejor 4-8 s), una tarjeta por idea, y los elementos se van construyendo dentro de ella. Springs más lentos (ω ≈ 9, ζ ≈ 0.88-0.92), entrada en 0.35 s, salida en 0.3 s, y el contenido sube durante 0.6 s. La tarjeta puede entrar mientras el título sigue abajo.
- **Estilo de animaciones actual = video 20 (X)** (19 oct 2026: "guardemos ese estilo de animaciones"). **No usar la textura de puntos**: "se ve raro".
- **Key visual tipo "Texture Lab"** (video 20, referencia de David Haz; la trama de puntos se descartó): marco color hueso `#EEEBE5` con radio 34 y un panel interior con radio 22. Adentro va una textura de puntos (campo de color suave renderizado como trama de puntos, generada en el script) con tipografía enorme y delgada (Geist Thin/ExtraLight, como su "14°"), o una interfaz de X recreada en negro con SF Pro (≈ Chirp) y azul `#1D9BF0`.
- **Audio: reducción de ruido con IA (desde el 19 oct 2026)**: el usuario se quejó del ruido de la calle. Ahora la voz pasa por **DeepFilterNet3** (modelo neural de mejora de voz, local, gratis) en vez de `afftdn`: el piso de ruido baja de ≈ -29 dB a ≈ -64 dB sin tocar la voz. Corre en un entorno aparte para no romper el PyTorch de Whisper: `python3.11 -m venv dfenv && dfenv/bin/pip install torch==2.0.1 torchaudio==2.0.2 "numpy<2" deepfilternet`, y se usa con `scripts/dfclean.py voice_raw.wav voice_df.wav [atten_lim_db]` dentro de `voice_build`. El tercer argumento deja un poco de ambiente si suena demasiado seco (30 dB ≈ natural). Con ruido de calle fuerte, limpiar la toma completa **antes** de cortar (las pausas aparecen a -70/-80 dB y los cortes caen exactos; video 22). Si solo cambia el audio, no hace falta re-renderizar: se reemplaza la pista con `ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac`.
- **Título**: 5 s sobre mi cara en vivo, abajo: `teoría by andrés corrales_` escrito letra por letra + título blanco en Geist Bold que entra palabra por palabra. Sin subtítulos encima.
- **Subtítulos simples**: Geist SemiBold 58 px, blancos con sombra suave, una línea de hasta 4 palabras, sin resaltar palabra, en y = 1450.
- **Barra de progreso azul** `#2F6BFF` de 10 px en el borde inferior (pista blanca al 25%).
- **Sin sonidos** (solo voz), **sin movimiento de cámara**, **nunca raya (—)** en los textos del video. **Solo HDR** (sin versión SDR).
- Si alguna vez se recorta a la persona (opción B o lienzo): **difuminar los bordes laterales** de la silueta (rampa del 20% del ancho); los hombros se salen del cuadro y queda una "caja" con el fondo del cuarto.
- Antes de un render largo con un cambio de diseño grande, mostrar 2 o 3 opciones de un mismo cuadro en Descargas y dejar elegir.
- Scripts: `scripts/video-16-marketing/render16.py` y `scripts/video-17-instinct/render17.py` (variable `LAYOUT`: `C` = actual; `B` = recorte con fondo desenfocado; `canvas` = lienzo gris, rechazado). Portadas: `scripts/cover_teoria.py <video> <segundo> <salida.jpg> "LÍNEA 1|LÍNEA 2|..."`. Los renders pesados se hacen fuera del Escritorio (iCloud) y aquí se archivan los scripts.

---

## 6. B-roll de terceros (videos de Twitter, etc.)

- Usar solo una parte (~30 a 40 s en un video de ~70 s), no el clip completo.
- **Sin su audio.**
- Sincronizar cada fragmento con lo que digo (tabla frase → momento del clip). Ejemplo MUD\WTR:
  - "para dar descuentos" → la landing
  - "más niveles, mayor descuento" → 5% → 7% → 9% OFF
  - "divertido" → nivel arcoíris
- Dar crédito ("vía @usuario") si se va a publicar.

---

## 7. Portadas (banner del reel)

- **Desde el 20 oct 2026 (feed actual):** la portada es **el mismo cuadro del título del video**: mi cara + `teoría by andrés corrales` + el título, con la tipografía y los colores de ese video (sin posterizar ni amarillo). Se genera con el `title(force=True)` del render sobre el cuadro con mejor cara (ej. `scripts/video-23-atencion/cover23.py`). Revisar el recorte 4:5.
- **Video de referencia de otra persona/marca (20 oct 2026):** su película es la columna del tramo: suena en silencio dentro de la tarjeta casi todo el tiempo (fragmentos elegidos por frase, recortados por encima de sus subtítulos) con una franja inferior de etiquetas literales. El look general queda **normal** (tarjeta oscura, Geist, subtítulos en píldora oscura); el rosado copiado de Darshita se rechazó ("déjalo normal"). Ver `video-23-atencion/render23b.py` y `video-24-ramp/render24.py`.
- **Nunca** usar el gráfico de "sistema solar / radar" (puntos orbitando un nombre): "se ve malísimo". Explicaciones literales con clips, capturas y frases reales.

- 1080 × 1920. Revisar el **recorte central 4:5 (y de 285 a 1635)** que muestra la cuadrícula del perfil: ahí deben leerse el título y la cara.
- Elegir el cuadro más nítido y expresivo (medir nitidez con varianza del Laplaciano en la zona de la cara y comparar sonrisas).
- Opciones que funcionaron:
  - Panel de papel arriba con titular + foto abajo.
  - Fondo de color con título **detrás de la cabeza** (silueta recortada) + sello + teléfono con el producto.
- Si se recorta la silueta, desvanecer los bordes laterales del cuadro original para que no se vea el corte recto.

---

## 8. Checklist antes de entregar

- [ ] No quedan arranques en falso ni silencios largos.
- [ ] Ningún corte cae dentro de una vocal (escuchar cada zoom).
- [ ] Solo voz + clicks nítidos (sin ping, chime, whoosh ni pop).
- [ ] Subtítulos correctos (nombres de marcas, "Claude", tildes).
- [ ] Las tildes de los textos grandes se ven completas (CAMPAÑAS, ESTÁ, MÁS).
- [ ] Nada tapa la cara (paneles, sellos, píxeles).
- [ ] Texto importante de al menos 36 a 40 px y con buen contraste en el teléfono.
- [ ] El color no fue retocado; entregado solo en HDR (sin SDR).
- [ ] Revisar cuadros en cada transición (sin franjas negras ni caras duplicadas).
- [ ] Nombres de archivo nuevos en cada entrega grande (evita escuchar una versión vieja en caché).

---

## 9. Errores que aparecieron y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| "Trompeta" en cada zoom / animación | Cortes dentro de vocales | Ajustar cortes al punto más silencioso + fundido de 70 ms en vocales |
| Sonido raro en los zooms | Whoosh + loudnorm dinámico | Quitar whoosh; loudnorm lineal en dos pasadas |
| Tildes cortadas ("CAMPANAS", "ESTA") | El lienzo del texto no dejaba espacio arriba de las mayúsculas | Espacio extra simétrico para acentos en `text()` |
| Franja negra al entrar al plano dividido | El panel bajaba sin fondo | Corte seco al plano dividido |
| Cara duplicada en transición | Panel deslizándose sobre la toma anterior | Corte seco |
| Audio del B-roll chocaba con la voz | Música del clip de Twitter | B-roll siempre en silencio |
| Texto azul ilegible en el teléfono | Azul oscuro sobre negro | Texto blanco sobre bloque azul |
| Valores inválidos en conversión HDR | Bug de numpy `@` (matmul) en macOS | Multiplicación de matriz explícita |
| El usuario seguía oyendo un sonido ya quitado | Reproductor con versión en caché | Entregar con nombre de archivo nuevo |

---

## 10. Herramientas técnicas

- **ffmpeg 8.1**: decodificación en `rgb48le` (HDR), HEVC Main10 HLG (`libx265`, `-tag:v hvc1`) y H.264 SDR.
- **Whisper** (modelo `medium`, idioma `es`, `--word_timestamps True`).
- **Python + cairo** (`/opt/homebrew/lib/libcairo.2.dylib`) para dibujar gráficos; **PIL** para texto (carga fuentes `.woff2`).
- **Apple Vision** (`VNGeneratePersonSegmentationRequest`, calidad `.accurate`) para recortar la silueta: `swiftc -O segment.swift -o segment`, uso `segment <carpeta_jpg> <carpeta_mascaras>`.
- **Librería de efectos**: `~/.claude/skills/media-use/audio/assets/sfx/` (19 archivos). Casi ninguno sirve según las reglas de sonido; preferir el click sintético nítido. Para más variedad: instalar el CLI de HeyGen y hacer `heygen auth login --oauth`.
- Fuentes del estilo FPS: `Desktop/Truora Marketing/fraud-series-hyperframes/assets/fonts/`.

Los scripts de cada video están en `scripts/`:
- `fx.py`: **módulo compartido y autónomo** (texto con tracking y sombra, easing, composición HDR/SDR, lector HLG, codificadores). Úsalo como base para videos nuevos; no depende de archivos temporales.
- `video-1-vox/render.py`: base con todas las utilidades (texto, papel, flechas, marcador).
- `video-2-claude-edita/`: cortes con saltos, B-roll de Twitter y portada.
- `video-3-mudwtr/`: dos videos unidos, texto detrás de la persona, B-roll sincronizado y portada con silueta.
- `video-4-fps-azul/`: estilo FPS azul, HDR/SDR, `voice_build.py` con los cortes limpios.
- `video-5-minimal-1.1x/`: título + subtítulos, pocas animaciones, 1.1x.
- `video-6-split-screen/`: pantalla dividida con grabación de pantalla abajo.
- `video-7-split-website/`: pantalla dividida + píldora con el website.
- `video-28-casey/`: Casey Neistat (IMG_9123 hook + IMG_9124 + IMG_9125 en la mitad). **Recortado al máximo (147 s → 64 s)**: una frase por idea, sin repeticiones. Formato de su comercial "Make It Count" (Nike): tarjetas negras, pantallas completas negras con su película 16:9 en cortes secos, frases en mayúsculas Helvetica Neue Bold arriba a la izquierda con crédito abajo a la derecha, subtítulos en mayúsculas blancas sin caja, rojo solo como acento (tachados, hilo, barra). Sus miniaturas de YouTube (Do Hard Things, MrBeast) en la mitad.
- `video-27-whop/`: Whop (IMG_9115 + IMG_9116). Todo en el estilo de Whop (pedido del usuario): tarjetas carbón, naranja Whop `#FE6243`, texto blanco; **subtítulos blancos con la palabra que se dice en naranja**; su película y su volante de partners en silencio, fotos de fundadores y vallas. Se evitaron fragmentos con correos/nombres reales y con texto en inglés.
- `video-26-restaurantes/`: idea de startup (IMG_9108), **sin material externo**: todo son motion graphics dibujados e interactivos, uno por idea: feed de TikTok y chat con amigos, app que pregunta tus gustos y recomienda, mapa de Bogotá con restaurantes nuevos y "el de siempre", barras de confianza (TikTok vs. amigo), búsquedas tachadas (TripAdvisor / Google), reloj de hambre con Fácil/Rápido tachados, la oportunidad, guía actualizada toda la semana, newsletter Top 5 (nuevos / en tendencia) y botón "Yo pagaría" con clic. Look normal con acento naranja. Grabado en la calle: DeepFilterNet antes de cortar.
- `video-25-kapso/`: Kapso (IMG_9102 + `KAPSO_INFO.mp4`, grabación de su página). Mismo sistema que el 23 v2: su página se ve en silencio todo el video dentro de una tarjeta negra, un fragmento por frase (estirado si es corto), franja de etiquetas literales, verde WhatsApp de acento. Se recorta el borde gris de la grabación y el final donde aparece el escritorio.
- `video-24-ramp/`: Ramp (IMG_9094). Su película "New on Ramp: Q3" suena en silencio todo el tramo de Ramp con etiquetas lima; luego Croma (negro, mono espaciado, diagrama Claude → Croma → DIAN / Supersociedades, sus publicaciones) y AbacatePay (blanco, verde azulado, sus publicaciones semanales). Portada = cuadro del título estilo Ramp.
- `video-23-atencion/`: Darshita Patankar, "Design is Dead" (IMG_9088). **v2 (render23b.py) es la entregada**: look normal + su película casi todo el tiempo. La v1 tenía la identidad de su película: negro ciruela y fucsia, letras script rosadas brillantes en 3D (Pacifico con extrusión, borde y cara en degradado), serif con brillo rosa, destellos de 4 puntas. Sus tomas van recortadas por encima de sus subtítulos y en silencio. Explicaciones literales (cadena "atrae gente → atrae miradas → todo sucede"), sin metáforas. La portada es el cuadro del título (`cover23.py`).
- `video-22-tendencias/`: tendencias EE. UU. → Latam (hook IMG_9070 + IMG_9069). Estilo del video 21. El hilo visual es una línea de tiempo de dos carriles (EE. UU. / LATAM) con curvas de tendencia que se retrasan, se copian y se adelantan. El audio se limpia con DeepFilterNet **antes** de cortar.
- `video-21-componentes/`: librerías de componentes (IMG_9068). Estilo del video 20 con key visual React Bits: tarjetas casi negras, píldoras con degradado, ventanas de código/terminal, líneas de fondo; lista de las 14 librerías en pantalla completa (miniatura · nombre · dominio). `shots.js` toma capturas de las páginas que no tienen captura del usuario (Playwright de la caché de npx).
- `video-20-x/`: Twitter / X (IMG_9042). Modelo Roadster con ritmo más lento y key visual Texture Lab: Contexto (noticias tachado, tecnología), "Qué está pasando", Twitter → X → 10x, feed que baja, todo se concentra en X, "por delante del mundo" y "A quién seguir" con clics.
- `video-19-roadster/`: Tesla Roadster (hook IMG_9043 + IMG_9044). Formato I con el look del lanzamiento: escenario negro, Saira, logo ROADSTER, pantallas completas del vuelo y del final, dos montajes de memes, radar de atención, gráfica de viralidad al 99%, anillo de 360°. `prep19.sh` regenera audio, fuente, logos, íconos y clips.
- `video-18-graza/`: Graza (hook IMG_9027 + IMG_9025). Formato I con el brand de Graza (paleta, logo, serif comprimida, mono, subtítulos en píldora crema, barra lima), clips del reel de referencia recortados sin sus subtítulos, botella squeeze animada, botellas "todas iguales", quiz con clics, góndola del supermercado. `ref/` y `clips/` se regeneran con `prep18.sh` (v18.json es la transcripción con tiempos de la voz editada).
- `video-17-instinct/`: Instinct (IMG_9010 + IMG_9011). Formato I: cuarto real + forma que se transforma arriba, chat de WhatsApp animado, apps conectadas, notificaciones, correo, vuelo, lista de espera, invitación.
- `video-16-marketing/`: 2 personas de marketing (IMG_9008 + IMG_9009). Formato I con perfiles, Wispr Flow, tweets, contador, píldora que cambia, LinkedIn y Seguir → Siguiendo.
- `video-15/`: treg.to. **Sin ningún movimiento de cámara** (pedido: los zooms se ven temblorosos): pantalla completa = cuadro original entero; mitad de arriba del split = un solo recorte fijo para todo el video. Demo sin audio + animaciones propias (diagrama de apps conectadas que busca y devuelve un resultado, chips de redes, comando de instalación con botón copiar, botón grande con el link al final). La frase del CTA se movió al final.
- `video-14/`: video sin material de apoyo (chiste de Claude): toda la historia la cuentan gráficos genéricos sobre el pecho (tarjeta de uso con barra, nota "La técnica" vacía, caja de prompt + chip Opus 5.5, barra que se llena al 100% en rojo, sello "NI IDEA" y CTA para comentar). Sin punch-in si la cabeza ya toca el borde de arriba.
- `video-13-jobs/`: producto (job-status). Capturas de LinkedIn + Gmail que se apilan con contadores rojos ("todo es una locura"); **datos personales de la captura de Gmail difuminados** (correo, códigos, alertas del banco, nombres); cada función de la grabación sincronizada con lo que digo; el correo vuelve y se desvanece en "se pierden los procesos".
- `video-12-nubank/`: video sobre un artículo (Colossus, David Vélez). Título en vivo, panel editorial, datos animados, portada con la foto del artículo.
- `video-11-podcasts/`: intro + 1 clip, 3 podcasts. **Sin tarjeta de título, de corrido** con cortes. Capturas de Spotify como tarjetas sobre panel oscuro (recortadas al encabezado, para que el subtítulo no las tape), píldora con el nombre del podcast y resumen final con las 3 portadas. Portada: si la cabeza toca el borde de arriba, bajar el cuadro ~190 px y extender la pared (`cover11.py`).
- `video-10-ui/`: hook + 2 clips, 3 herramientas (UIMaxxing, Arc, Cult UI) en pantalla dividida con píldora de link, resumen final con los 3 links, tarjeta good work_ con música, portada (`cover10.py`). La página de Cult UI se capturó con Playwright (`cult_shot.js`, captura de página completa a 2x) y se anima con paneo.
- `video-9-ramp/`: dos videos unidos (hook + cuerpo recortado), 1.05x, brand look de Ramp, tarjeta de título good work_ posterizada y portada (`cover9.py`).
- `video-8-croma/`: pantalla dividida + website + 1.1x (combina 7 y 5). Recorte del apoyo por pantalla (cada pantalla con su propio recorte) y apoyo desacelerado para cubrir todo el video.
- `framing.py`: encuadre que nunca corta la cabeza (usa `herramientas/face.swift`).
- `herramientas/segment.swift`: segmentación de persona.

Los scripts tienen rutas de trabajo temporales; sirven como referencia y para reutilizar componentes.

---

## 11. Historial de videos entregados (en Descargas)

| Video | Archivo final | Estilo | Notas |
|---|---|---|---|
| IMG_8840 (22 s → 14 s) | `IMG_8840_editado.mp4` | Vox | Primer video: "Claude edita videos con un prompt" |
| IMG_8841 (78 s → 60 s) | `IMG_8841_editado.mp4` + `IMG_8841_portada.jpg` | Vox + B-roll | B-roll sin audio. Pendiente: tildes de "PRUÉBENLO" y "MÁQUINA" (bug corregido después) |
| IMG_8851 + IMG_8850 (hook + 72 s → 70 s) | `IMG_8850_editado.mp4` + `IMG_8850_portada.jpg` | Texto detrás + B-roll MUD\WTR | "Mejores campañas de marketing 2026" |
| IMG_8856 (51 s → 41 s) | `IMG_8856_v3_A_voz_HDR.mp4` (solo voz) / `IMG_8856_v3_B_voz_click_HDR.mp4` (voz + click) | FPS azul | Versión con cortes limpios (sin "trompeta"). Las versiones sin "v3" están obsoletas |
| IMG_8866 (69 s → 52 s a 1.1x) | `IMG_8866_editado_HDR.mp4` / `_SDR.mp4` | Mínimo (FPS azul) | Título 5 s, luego solo subtítulos, 3 animaciones, sin sonidos, velocidad 1.1x |
| IMG_8875 (67 s → 49 s) | `IMG_8875_editado_v2_HDR.mp4` / `_SDR.mp4` (v2: cara completa) | Pantalla dividida (ref. IMG_8876) | Abajo: grabación de pantalla de QuikTrip sin audio. Título 5 s. Se cortó el tramo trabado ("doger en Estados…") |
| IMG_8877 (42 s → 37 s) | `IMG_8877_editado_HDR.mp4` / `_SDR.mp4` | Pantalla dividida + website | Abajo: bubbbly.com/bloom (QR que parecen flores) sin audio. Píldora con el website |
| IMG_8907 (43 s → 31 s a 1.1x) | `IMG_8907_editado_v4_HDR.mp4` / `_SDR.mp4` (v4: sin temblor, título nuevo, subtítulos arriba) | Pantalla dividida + website + 1.1x | Título: "Un buen onboarding es lo que te permite conseguir más usuarios". Abajo: onboarding de Croma (sin primeros 8 s ni últimos 2 s). Píldora `usecroma.com` desde "esos manes". Se cortó el arranque en falso y la repetición "vean esos manes" |
| IMG_8913 + IMG_8914 (16 s + 82 s → 60 s a 1.05x) | `IMG_8913_ramp_editado_v3_HDR.mp4` / `_SDR.mp4` (v3: con la pista de good work_ en la tarjeta) + `IMG_8913_ramp_portada.jpg` | Brand look Ramp + tarjeta good work_ | "¿Cómo hace marketing Ramp?". Se recortó la segunda parte (de 82 s a ~47 s). Imágenes: Bill Pay, Kumar, tarjetas, Finance but fun, perfil de @thekumarmethod; B-roll del musical sin audio |
| IMG_8927 (hook) + IMG_8925 + IMG_8926 (93 s → 67 s a 1.05x) | `IMG_8927_ui_editado_v2_HDR.mp4` / `_SDR.mp4` + `IMG_8927_ui_portada.jpg` | Pantalla dividida + tarjeta good work_ | "3 páginas para que tu website no parezca hecho con IA" (el usuario prefiere títulos directos, no en pregunta). Se quitó la intro de 8925 (repetía el hook), "pegarle un,", "importante" y "Y tercera, ya les voy a decir cuál". Subtítulos blancos con la palabra activa en amarillo teoría |
| IMG_8930 + IMG_8931 (81 s → 61 s a 1.05x) | `IMG_8930_podcasts_editado_v2_HDR.mp4` / `_SDR.mp4` (v2: collage en la intro) + `IMG_8930_podcasts_portada_collage.jpg` | Pantalla dividida, sin tarjeta de título | 20VC, My First Million, David Senra. Se quitó "Entonces, sencillamente, si quieren tener más contexto, buenísimo", "y todo" y "traen a los mejores invitados…" |
| IMG_8938 (52 s → 35 s a 1.05x) | `IMG_8938_nubank_editado_HDR.mp4` / `_SDR.mp4` + `IMG_8938_nubank_portada.jpg` | Panel editorial + datos animados | "El mejor artículo que leerás esta semana". Se quitó el arranque en falso "de cómo luchó contra… bancos" |
| IMG_8946 (65 s → 48 s a 1.05x) | `IMG_8946_jobstatus_editado_HDR.mp4` / `_SDR.mp4` + `IMG_8946_jobstatus_portada.jpg` | Pantalla dividida + capturas | "Toda tu búsqueda de trabajo en un solo lugar". Se quitó "venga", "si usted" repetido, "comenten" repetido y "Gracias, adiós" |
| IMG_8956 (33 s → 21 s a 1.05x) | `IMG_8956_claude_editado_HDR.mp4` / `_SDR.mp4` + `IMG_8956_claude_portada.jpg` | Animaciones propias (sin apoyo) | "La técnica para que tu plan de $20 de Claude no se acabe" (remate: "yo tampoco tengo ni idea"). Se quitó el arranque en falso "Si os…" |
| IMG_8957 (100 s → 69 s a 1.05x) | `IMG_8957_treg_editado_HDR.mp4` / `_SDR.mp4` + `IMG_8957_treg_portada.jpg` | Split con demo + animaciones, cámara fija | "Dale superpoderes a tu Claude con esta página". Se quitaron: primer intento de "se llama treg.to", "¿cómo así, qué herramienta?", "literalmente lo que él tiene es un montón de…", "esa vaina es una locura porque literalmente", "volver volver", "le mandan" repetido y "brutal" |
| IMG_9008 + IMG_9009 (78 s → 51 s a 1.05x) | `IMG_9008_marketing_editado_v3_HDR.mp4` / `_SDR.mp4` + `IMG_9008_marketing_portada.jpg` | Formato I (opción C) | "2 personas que tienes que seguir si estás en marketing" (Héctor Serrano, Matt Swulinski). Se quitó el arranque en falso inicial, "es…", el "Segundo" repetido, "UGC, creadores UGC" y la frase repetida "y usted tiene que seguir esa gente…" |
| IMG_9010 + IMG_9011 (79 s → 56 s a 1.05x) | `IMG_9010_instinct_editado_HDR.mp4` / `_SDR.mp4` + `IMG_9010_instinct_portada.jpg` | Formato I (opción C) | "Tu asistente personal ahora vive en WhatsApp". Se quitaron los arranques en falso ("resulta que esto es una app…", "yo tenía una reunión, tú…"), el "Hola Andrés" repetido y "Gracias por ver el video" |
| IMG_9027 + IMG_9025 (113 s → 66 s a 1.05x) | `IMG_9025_graza_editado_HDR.mp4` + `IMG_9025_graza_portada.jpg` | Formato I con brand de Graza | "Marcas que tienes que seguir si trabajas en marketing · Nº 1 Graza". Hook nuevo (IMG_9027); se quitaron los arranques en falso, el hook viejo, "esta es la historia de Graza", "aceite de oliva, ¿cómo?", "chévere" repetido, "se me han", "la realidad" y varios "literalmente". Fragmentos del reel de referencia sin audio ni subtítulos. Solo HDR |
| IMG_9043 + IMG_9044 (70 s → 54 s a 1.05x) | `IMG_9044_roadster_editado_HDR.mp4` + `IMG_9044_roadster_portada.jpg` | Formato I con look del lanzamiento de Tesla | "El mejor lanzamiento del año". Se quitaron la pausa larga y el "si" después de "lo mejor", "pero sobre todo lo mejor de todo eso", varios "literalmente" y "entonces es increíble" (cierra en "de los mejores lanzamientos de producto que yo vi en mi vida"). Clips de la demo y memes sin audio. Solo HDR |
| IMG_9042 (49 s → 39 s a 1.05x) | `IMG_9042_x_editado_HDR.mp4` + `IMG_9042_x_portada.jpg` | Modelo Roadster, ritmo lento, key visual Texture Lab + interfaz de X | "La red social que te da una ventaja 10x". Se quitaron tres "literalmente", pausas largas y "entonces ya saben" (cierra en "solo tiran alfa"). Solo HDR |
| IMG_9068 (93 s → 74 s a 1.05x) | `IMG_9068_componentes_editado_HDR.mp4` + `IMG_9068_componentes_portada.jpg` | Estilo video 20 + key visual React Bits | "14 librerías para que tu web no parezca hecha con IA". Se quitaron el segundo "y cómo así que componentes", "cómo va a ser estructurada absolutamente todo dentro de eso", "que hacen que realmente tu proyecto se vea" (sin terminar), cuatro "literalmente" y pausas. Solo HDR |
| IMG_9070 + IMG_9069 (13 s + 77 s → 71 s a 1.05x) | `IMG_9069_tendencias_editado_HDR.mp4` + `IMG_9069_tendencias_portada.jpg` | Estilo video 21, línea de tiempo EE. UU./LATAM | "Cómo ir 2 años por delante en Latinoamérica". IMG_9070 va de hook. Se quitaron "con el tema de los cursos" (repetido), "ya eso dejó de estar de moda" (repetido), cuatro "literalmente" y pausas largas. Audio con DeepFilterNet. Solo HDR |
| IMG_9088 (99 s → 58 s a 1.05x) | `IMG_9088_atencion_editado_v2_HDR.mp4` + `IMG_9088_atencion_portada.jpg` | v2: look normal + su película casi todo el tiempo (la v1 rosada se rechazó) | "Atención es lo único que necesitas". Muchos errores cortados: 5 "literalmente", "oe, pucha", "y esa vaina eventualmente va a suceder que todo", la repetición de "le están lloviendo ofertas… obviamente no, no", el primer intento de "¿por qué no debería…" y "le fue". Clips de su película sin audio ni subtítulos. Audio con DeepFilterNet. Solo HDR |
| IMG_9094 (114 s → 81 s a 1.05x) | `IMG_9094_ramp_editado_HDR.mp4` + `IMG_9094_ramp_portada.jpg` | Película de Ramp + Croma + AbacatePay en su identidad | "Así consigue clientes Ramp". Se quitaron el arranque en falso, "diferente a lo que hace", "esos manes de Ramp" repetido, la frase abandonada "no son el mega feature que va a hacer que la gente o no", "por alguna", "lo que va a hacer es que ya como todo su sistema", "todo y", "y literalmente eso" y cinco "literalmente". Solo HDR |
| IMG_9102 (95 s → 64 s a 1.05x) | `IMG_9102_kapso_editado_HDR.mp4` + `IMG_9102_kapso_portada.jpg` | Su página dentro de la tarjeta todo el video, look normal | "La mejor herramienta para tu WhatsApp Business". Se quitaron cuatro "literalmente", "tu, tu bot", "y literalmente pues", "te puede", "como si fuera un" (sin terminar) y la toma repetida "puedes montar todo todo y tener… un bot de WhatsApp para tus clientes". Solo HDR |
| IMG_9108 (96 s → 67 s a 1.05x) | `IMG_9108_restaurantes_editado_HDR.mp4` + `IMG_9108_restaurantes_portada.jpg` | Solo motion graphics dibujados (no había material) | "Una idea de startup que yo pagaría". Se quitaron "márica", tres "literalmente", "o no hay un LLM o hay algo", "nosotros todo el día abrimos restaurantes", "de lo que uno tenga", "porque es que en mucho tiempo", "¿quién es? no sé" y "eso es una vaina". Ruido de calle quitado con DeepFilterNet. Solo HDR |
| IMG_9115 + IMG_9116 (117 s + 25 s → 105 s a 1.05x) | `IMG_9115_whop_editado_v2_HDR.mp4` + `IMG_9115_whop_portada.jpg` (v2 con fragmentos de su tercer video, "Here's to the humans") | Estilo Whop (naranja y carbón, subtítulos blancos con palabra naranja) | "De revender sneakers a US$200M". Se quitaron doce "literalmente", el reinicio "márica, Whop es lo que usted necesita si es un coach, si es un…", "para cualquier mercado" repetido, "y los volvieron" (reinicio), "porque ese man les trajo y" y "que todos sus cursos y" (sin terminar). Solo HDR |
| IMG_9123 + IMG_9124 + IMG_9125 (147 s → 64 s a 1.05x) | `IMG_9123_casey_editado_HDR.mp4` + `IMG_9123_casey_portada.jpg` | Formato "Make It Count" de Casey | "El mejor storyteller de YouTube". Pedido: acortar todo lo posible. Se quitaron "dudo mucho que se lo enseñen…", "y para mí quién es de los mejores…", "y lo mejor de todo es que el man te va contando…", "el man te ha hecho un cuento" (x2), "te hace sentir tranquilo", "me están echando un cuento… lo mínimo es eso", "si uno quiere empezar a lo que sea", "tiene unos maravillosos", "que no tiene que ver nada con decirle no a MrBeast" y todos los "literalmente". Solo HDR |

> **Nota (20 oct 2026):** a pedido del usuario se borraron de Descargas los 16 videos crudos (IMG_9008 a IMG_9094, 4.5 GB). Quedan los editados, las portadas y los videos de referencia. Los scripts de `video-16` a `video-24` ya no pueden volver a renderizar sin el material original. También se borraron la v1 rosada de IMG_9088 y las 11 copias `_SDR.mp4` viejas (IMG_8866 a IMG_8957): de cada video queda solo la última versión en HDR.

> **Nota (8 oct 2026):** se limpió Descargas. Solo quedan las versiones finales de la tabla (HDR + SDR + portada). Los originales (IMG_xxxx.MOV) y los apoyos (grabaciones, capturas) se borraron, así que los scripts de `scripts/` ya no pueden volver a renderizar esos videos sin el material original.
