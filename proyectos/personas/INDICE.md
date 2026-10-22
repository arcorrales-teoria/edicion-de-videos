# Índice de proyectos de videos con persona

Una carpeta por video: `NN-nombre/` (número de dos cifras, siguiente libre al crear uno nuevo; ver `herramientas/nuevo-proyecto.sh`). Cada una guarda los scripts del video (`edit`, `voice_build`, `render`, `cover`), la transcripción con tiempos (`*.json`) y los intermedios de trabajo (audio, cuadros, hojas de contacto).

- **Reglas y estilos:** `../../guias/personas/reglas-y-estilos.md`
- **Qué se entregó y cómo:** `../../registro/historial-personas.md`
- **Código compartido:** `../../herramientas/` (`fx.py`, `framing.py`, `dfclean.py`, `cover_teoria.py`)

Los videos crudos (IMG_xxxx.MOV) no están en el repositorio. Los scripts apuntan a rutas del Mac del autor para el material de entrada: sirven como referencia y para reutilizar componentes, y las importaciones de `fx.py` ya apuntan a `herramientas/`.

## Qué proyecto copiar según el estilo que se pida

| Si piden... | Partir de |
|---|---|
| Formato actual por defecto (cuarto real + una forma que se transforma arriba) | `19-roadster` (modelo), `20-x` (animaciones actuales) |
| Brand look de una marca | `18-graza`, `27-whop`, `24-ramp` |
| Material de referencia de otra persona o marca en silencio dentro de una tarjeta | `23-atencion` (`render23b.py`), `25-kapso`, `24-ramp` |
| Solo motion graphics (sin material de apoyo) | `26-restaurantes`, `14-claude-plan` |
| Pantalla dividida con grabación de pantalla abajo | `07-split-website`, `08-croma` |
| Sin movimiento de cámara | `15-treg` |
| Video sobre un artículo | `12-nubank` |
| Cortes duros, muy recortado | `28-casey` |
| Portada con el cuadro del título | `23-atencion/cover23.py` |
| Limpieza de audio con IA antes de cortar | `22-tendencias`, `26-restaurantes` |

## Proyectos

- `01-vox/render.py`: base con todas las utilidades (texto, papel, flechas, marcador).
- `02-claude-edita/`: cortes con saltos, B-roll de Twitter y portada.
- `03-mudwtr/`: dos videos unidos, texto detrás de la persona, B-roll sincronizado y portada con silueta.
- `04-fps-azul/`: estilo FPS azul, HDR/SDR, `voice_build.py` con los cortes limpios.
- `05-minimal/`: título + subtítulos, pocas animaciones, 1.1x.
- `06-split-screen/`: pantalla dividida con grabación de pantalla abajo.
- `07-split-website/`: pantalla dividida + píldora con el website.
- `08-croma/`: pantalla dividida + website + 1.1x (combina 7 y 5). Recorte del apoyo por pantalla (cada pantalla con su propio recorte) y apoyo desacelerado para cubrir todo el video.
- `09-ramp/`: dos videos unidos (hook + cuerpo recortado), 1.05x, brand look de Ramp, tarjeta de título good work_ posterizada y portada (`cover9.py`).
- `10-ui/`: hook + 2 clips, 3 herramientas (UIMaxxing, Arc, Cult UI) en pantalla dividida con píldora de link, resumen final con los 3 links, tarjeta good work_ con música, portada (`cover10.py`). La página de Cult UI se capturó con Playwright (`cult_shot.js`, captura de página completa a 2x) y se anima con paneo.
- `11-podcasts/`: intro + 1 clip, 3 podcasts. **Sin tarjeta de título, de corrido** con cortes. Capturas de Spotify como tarjetas sobre panel oscuro (recortadas al encabezado, para que el subtítulo no las tape), píldora con el nombre del podcast y resumen final con las 3 portadas. Portada: si la cabeza toca el borde de arriba, bajar el cuadro ~190 px y extender la pared (`cover11.py`).
- `12-nubank/`: video sobre un artículo (Colossus, David Vélez). Título en vivo, panel editorial, datos animados, portada con la foto del artículo.
- `13-jobs/`: producto (job-status). Capturas de LinkedIn + Gmail que se apilan con contadores rojos ("todo es una locura"); **datos personales de la captura de Gmail difuminados** (correo, códigos, alertas del banco, nombres); cada función de la grabación sincronizada con lo que digo; el correo vuelve y se desvanece en "se pierden los procesos".
- `14-claude-plan/`: video sin material de apoyo (chiste de Claude): toda la historia la cuentan gráficos genéricos sobre el pecho (tarjeta de uso con barra, nota "La técnica" vacía, caja de prompt + chip Opus 5.5, barra que se llena al 100% en rojo, sello "NI IDEA" y CTA para comentar). Sin punch-in si la cabeza ya toca el borde de arriba.
- `15-treg/`: treg.to. **Sin ningún movimiento de cámara** (pedido: los zooms se ven temblorosos): pantalla completa = cuadro original entero; mitad de arriba del split = un solo recorte fijo para todo el video. Demo sin audio + animaciones propias (diagrama de apps conectadas que busca y devuelve un resultado, chips de redes, comando de instalación con botón copiar, botón grande con el link al final). La frase del CTA se movió al final.
- `16-marketing/`: 2 personas de marketing (IMG_9008 + IMG_9009). Formato I con perfiles, Wispr Flow, tweets, contador, píldora que cambia, LinkedIn y Seguir → Siguiendo.
- `17-instinct/`: Instinct (IMG_9010 + IMG_9011). Formato I: cuarto real + forma que se transforma arriba, chat de WhatsApp animado, apps conectadas, notificaciones, correo, vuelo, lista de espera, invitación.
- `18-graza/`: Graza (hook IMG_9027 + IMG_9025). Formato I con el brand de Graza (paleta, logo, serif comprimida, mono, subtítulos en píldora crema, barra lima), clips del reel de referencia recortados sin sus subtítulos, botella squeeze animada, botellas "todas iguales", quiz con clics, góndola del supermercado. `ref/` y `clips/` se regeneran con `prep18.sh` (v18.json es la transcripción con tiempos de la voz editada).
- `19-roadster/`: Tesla Roadster (hook IMG_9043 + IMG_9044). Formato I con el look del lanzamiento: escenario negro, Saira, logo ROADSTER, pantallas completas del vuelo y del final, dos montajes de memes, radar de atención, gráfica de viralidad al 99%, anillo de 360°. `prep19.sh` regenera audio, fuente, logos, íconos y clips.
- `20-x/`: Twitter / X (IMG_9042). Modelo Roadster con ritmo más lento y key visual Texture Lab: Contexto (noticias tachado, tecnología), "Qué está pasando", Twitter → X → 10x, feed que baja, todo se concentra en X, "por delante del mundo" y "A quién seguir" con clics.
- `21-componentes/`: librerías de componentes (IMG_9068). Estilo del video 20 con key visual React Bits: tarjetas casi negras, píldoras con degradado, ventanas de código/terminal, líneas de fondo; lista de las 14 librerías en pantalla completa (miniatura · nombre · dominio). `shots.js` toma capturas de las páginas que no tienen captura del usuario (Playwright de la caché de npx).
- `22-tendencias/`: tendencias EE. UU. → Latam (hook IMG_9070 + IMG_9069). Estilo del video 21. El hilo visual es una línea de tiempo de dos carriles (EE. UU. / LATAM) con curvas de tendencia que se retrasan, se copian y se adelantan. El audio se limpia con DeepFilterNet **antes** de cortar.
- `23-atencion/`: Darshita Patankar, "Design is Dead" (IMG_9088). **v2 (render23b.py) es la entregada**: look normal + su película casi todo el tiempo. La v1 tenía la identidad de su película: negro ciruela y fucsia, letras script rosadas brillantes en 3D (Pacifico con extrusión, borde y cara en degradado), serif con brillo rosa, destellos de 4 puntas. Sus tomas van recortadas por encima de sus subtítulos y en silencio. Explicaciones literales (cadena "atrae gente → atrae miradas → todo sucede"), sin metáforas. La portada es el cuadro del título (`cover23.py`).
- `24-ramp/`: Ramp (IMG_9094). Su película "New on Ramp: Q3" suena en silencio todo el tramo de Ramp con etiquetas lima; luego Croma (negro, mono espaciado, diagrama Claude → Croma → DIAN / Supersociedades, sus publicaciones) y AbacatePay (blanco, verde azulado, sus publicaciones semanales). Portada = cuadro del título estilo Ramp.
- `25-kapso/`: Kapso (IMG_9102 + `KAPSO_INFO.mp4`, grabación de su página). Mismo sistema que el 23 v2: su página se ve en silencio todo el video dentro de una tarjeta negra, un fragmento por frase (estirado si es corto), franja de etiquetas literales, verde WhatsApp de acento. Se recorta el borde gris de la grabación y el final donde aparece el escritorio.
- `26-restaurantes/`: idea de startup (IMG_9108), **sin material externo**: todo son motion graphics dibujados e interactivos, uno por idea: feed de TikTok y chat con amigos, app que pregunta tus gustos y recomienda, mapa de Bogotá con restaurantes nuevos y "el de siempre", barras de confianza (TikTok vs. amigo), búsquedas tachadas (TripAdvisor / Google), reloj de hambre con Fácil/Rápido tachados, la oportunidad, guía actualizada toda la semana, newsletter Top 5 (nuevos / en tendencia) y botón "Yo pagaría" con clic. Look normal con acento naranja. Grabado en la calle: DeepFilterNet antes de cortar.
- `27-whop/`: Whop (IMG_9115 + IMG_9116). Todo en el estilo de Whop (pedido del usuario): tarjetas carbón, naranja Whop `#FE6243`, texto blanco; **subtítulos blancos con la palabra que se dice en naranja**; su película y su volante de partners en silencio, fotos de fundadores y vallas. Se evitaron fragmentos con correos/nombres reales y con texto en inglés.
- `28-casey/`: Casey Neistat (IMG_9123 hook + IMG_9124 + IMG_9125 en la mitad). **Recortado al máximo (147 s → 64 s)**: una frase por idea, sin repeticiones. Formato de su comercial "Make It Count" (Nike): tarjetas negras, pantallas completas negras con su película 16:9 en cortes secos, frases en mayúsculas Helvetica Neue Bold arriba a la izquierda con crédito abajo a la derecha, subtítulos en mayúsculas blancas sin caja, rojo solo como acento (tachados, hilo, barra). Sus miniaturas de YouTube (Do Hard Things, MrBeast) en la mitad.
