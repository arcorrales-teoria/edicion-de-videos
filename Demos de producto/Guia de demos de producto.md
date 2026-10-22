# Guía de demos de producto (motion graphics)

Estándar para crear videos de lanzamiento y demos de producto con Claude: animación hecha con código (HTML, CSS y JavaScript), fondo con Shaders y render cuadro a cuadro a MP4. Sale de hacer el video de lanzamiento de job-status (proyecto `01-job-status-launch`).

> **Cómo usarla:** al empezar una sesión, dile a Claude: *"Lee `Demos de producto/Guia de demos de producto.md` y arma la demo con la plantilla."*

Para videos donde sales tú hablando a cámara, usa la guía de `Videos personas/`.

---

## 1. Estructura de carpetas

```
Demos de producto/
  Guia de demos de producto.md   ← esta guía
  plantilla/                     ← punto de partida de toda demo nueva
    video.html                   ← motor + escenas de ejemplo (16:9 y 9:16 en el mismo archivo)
    render.mjs                   ← captura los cuadros con Chrome (WebGPU)
    package.json                 ← dependencias (shaders, geist) y comandos
    assets/                      ← capturas de pantalla del producto
  proyectos/
    NN-nombre/                   ← una carpeta por demo, numeradas
      video.html, video-story.html, render.mjs, package.json
      assets/                    ← capturas usadas
      entregas/                  ← MP4 finales
      LEEME.md                   ← qué es, cómo rehacerlo, historial
```

**Importante (iCloud):** el Escritorio se sincroniza con iCloud y vacía archivos que no se usan. Eso rompe `node_modules` y cuelga los renders. Por eso:
- **Trabaja** en `~/Developer/<nombre-del-proyecto>` (fuera de iCloud).
- **Archiva aquí** al terminar: fuentes, capturas, entregas y LEEME. Nunca `node_modules` ni `frames/`.

---

## 2. Flujo de trabajo

1. **Brief en una línea:** producto, público, mensaje principal, duración (por defecto **20 s**) y formatos (por defecto **16:9 y 9:16**).
2. **Copiar la plantilla** a `~/Developer/<proyecto>` y correr `npm install`.
3. **Capturas del producto** (ver sección 4).
4. **Guion de escenas con tiempos exactos.** Estructura que funcionó:

   | Tiempo | Escena |
   |---|---|
   | 0 a 3,4 s | Marca + "by Andrés Corrales" y titular |
   | 3,4 a 7,4 s | Escena explicativa (por ejemplo, isométrica: todo converge en el producto) |
   | 7,4 a 14 s | Producto en ventana de navegador (2 o 3 pantallas, una idea por pantalla) |
   | 14 a 17 s | Funciones secundarias (tarjetas) |
   | 17 a 20 s | Cierre: marca, lema, etiqueta + URL, "by Andrés Corrales" |

5. **Construir** en `video.html`: cambiar `CONFIG`, reemplazar las escenas, dejar intacto el motor.
6. **Revisar cuadros de muestra** antes del render completo (sección 6).
7. **Render completo** y codificación (sección 7).
8. **Versión vertical** con `?formato=historia` y revisarla igual.
9. **Archivar** en `proyectos/NN-nombre/` y anotar la entrega en el LEEME del proyecto.

---

## 3. Reglas estándar (no negociables)

- **Duración exacta:** 20 s = 600 cuadros a 30 fps. Verificar con `ffprobe` (`nb_frames=600`, `duration=20.000000`).
- **Firma:** "by Andrés Corrales" **al comienzo** (debajo de la marca, visible al menos 1,5 s) **y al final** (último elemento del cierre).
- **Sin audio** por defecto. Si se pide sonido, aplican las reglas de `Videos personas`: nada de ping, chime, whoosh ni pop.
- **Textos:** en español, frases cortas, una idea por pantalla. **Nunca usar raya (—).**
- **Datos ficticios** en las capturas: usar la cuenta de ejemplo, nunca datos reales de personas.
- **Paleta:** grises oscuros (#0a0a0a a #232323), texto #ededed, secundario #8a8a8a, y **un solo acento** (job-status: verde #34d399).
- **Tipografía:** Geist (títulos 600, tracking −0,045 a −0,05em) y Geist Mono para etiquetas en mayúsculas.
- **Movimiento:** entradas que suben y se enfocan desde un desenfoque (`reveal`, `revealWords`) con curva `outExpo`; salidas con `inCubic` hacia arriba. Nada de rebotes exagerados ni giros.
- **Historias (9:16):** dejar libres los **250 px de arriba** y los **340 px de abajo** (ahí va la interfaz de Instagram). Títulos de 66 a 104 px en varias líneas, ventanas escaladas a 0,76 y tarjetas apiladas.

---

## 4. Capturas del producto

- Tomarlas con Chrome sin ventana a 1440×900 (o recortadas con `clip`), en **modo oscuro** si el video es oscuro.
- **Esperar a que carguen todas las imágenes** antes de capturar (logos, foto del login). Si no, salen recuadros vacíos.
- En apps con cuenta de ejemplo que se reinicia, **los IDs cambian en cada ingreso**: buscar el ID real (por ejemplo, por API) antes de abrir un detalle.
- Si la app tiene sincronizaciones automáticas, revisar que no aparezcan avisos o errores en la captura.
- Exportar a WebP (`cwebp -q 86`) para que pesen poco.

---

## 5. Stack técnico

- **Página:** HTML + CSS + JS, una sola función `render(t)` que dibuja todo según el tiempo `t` (en segundos). Nada de animaciones CSS por su cuenta: todo depende de `t`.
- **Fondo:** paquete `shaders` (WebGPU). Capas que funcionan: `FlowingGradient` (grises), `DotGrid`, `Vignette` y `FilmGrain`. **No usar `Godrays`**: aun con intensidad baja tapa todo.
- **Tiempo virtual:** la página reemplaza `performance.now` y `requestAnimationFrame`. `window.__frame(n)` fija el reloj en el cuadro `n`, dibuja y avanza el shader. Así cada cuadro sale exacto.
- **Render:** `render.mjs` abre Chrome sin ventana con WebGPU (`--enable-unsafe-webgpu --use-angle=metal`), sin caché, y guarda un JPG por cuadro.
- **Escenas isométricas:** SVG con proyección `P(x,y,z)`. Las caras se dibujan en 2D y se proyectan con `matrix(...)` (ver `proyectos/01-job-status-launch/video.html`, funciones `box`, `topPlane` y `frontPlane`).

---

## 6. Revisión antes del render completo

Renderizar 6 a 9 cuadros clave (uno por escena y uno en cada transición) y armar una hoja de contacto:

```bash
for n in 45 80 190 250 300 345 470 595; do node render.mjs $n $n test video.html 1920 1080 >/dev/null; done
cd test && ffmpeg -y -i f0045.jpg -i f0080.jpg -i f0190.jpg -i f0250.jpg -filter_complex "[0][1][2][3]hstack=4" contacto.jpg
```

Revisar: textos cortados o encimados, elementos fuera de la zona segura, imágenes vacías y que la firma se lea.

---

## 7. Render y codificación

```bash
python3 -m http.server 8765 &                     # servir la carpeta
node render.mjs 0 599 frames video.html 1920 1080 # 16:9
node render.mjs 0 599 frames-historia 'video.html?formato=historia' 1080 1920   # 9:16

# Calidad alta
ffmpeg -framerate 30 -i frames/f%04d.jpg -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart nombre-20s.mp4
# Liviana para redes
ffmpeg -i nombre-20s.mp4 -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -movflags +faststart nombre-20s-liviano.mp4
# Historia
ffmpeg -framerate 30 -i frames-historia/f%04d.jpg -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart nombre-historia-ig-20s.mp4

ffprobe -v error -show_entries format=duration -show_entries stream=nb_frames -of default=nw=1 nombre-20s.mp4
```

Entregar en `~/Downloads` y copiar a `proyectos/NN-nombre/entregas/`.

---

## 8. Errores conocidos y solución

| Problema | Solución |
|---|---|
| `ReferenceError: process is not defined` al cargar Shaders | Definir `window.process = { env: { NODE_ENV: "production" } }` antes de importar |
| Fondo negro, el shader no dibuja | Servir por `http://` (no `file://`) y abrir Chrome con `--enable-unsafe-webgpu --use-angle=metal` |
| Reaparecen efectos que ya se quitaron | Caché del navegador: `render.mjs` usa perfil nuevo y `Network.setCacheDisabled` |
| Matriz de puntos o canvas vacío con movimiento reducido | Redibujar cuando cambia el tamaño del elemento |
| Capturas con recuadros vacíos | Esperar a que carguen todas las imágenes antes de capturar |
| El detalle no abre en la captura | El ID de la cuenta de ejemplo cambió: buscar el ID real |
| Render o build colgados | iCloud vació archivos: trabajar en `~/Developer`, nunca en el Escritorio |
| Texto partido en dos líneas ("job-" / "status") | `white-space: nowrap` en la marca y ancho fijo en el contenedor |

---

## 9. Checklist de entrega

- [ ] 600 cuadros, 20,000 s exactos (16:9 y 9:16).
- [ ] "by Andrés Corrales" al inicio y al final.
- [ ] Sin rayas (—) en los textos; ortografía revisada.
- [ ] Capturas con datos ficticios y sin avisos de error.
- [ ] Historia: nada importante en los 250 px de arriba ni en los 340 px de abajo.
- [ ] Hoja de contacto revisada antes del render completo.
- [ ] Archivos en `~/Downloads` y archivados en `proyectos/NN-nombre/` con su LEEME.

---

## 10. Historial

| # | Proyecto | Fecha | Entregas |
|---|---|---|---|
| 01 | job-status launch | 2026-10-09 | 16:9 (alta y liviana) y 9:16 para historias, 20 s |
