# 01 · job-status launch (20 s)

Video de lanzamiento de job-status. Motion graphics sin audio, fondo con Shaders y capturas de la cuenta de ejemplo.

## Escenas
| Tiempo | Escena |
|---|---|
| 0 a 3,4 s | Marca + "by Andrés Corrales" y titular "Tu búsqueda laboral, en un solo lugar." |
| 3,4 a 7,4 s | Isométrica: LinkedIn, Gmail, CV y Calendario convergen en la pantalla de job-status |
| 7,4 a 10,6 s | Ventana del producto: Inicio y Tablero |
| 10,6 a 14 s | Matriz de puntos leyendo Gmail y lista de Ofertas |
| 14 a 17 s | Mapa de personas y Seguimiento semanal |
| 17 a 20 s | Cierre: marca, lema, beta, URL y "by Andrés Corrales" |

## Archivos
- `video.html`: versión 16:9 (1920×1080).
- `video-story.html`: versión 9:16 para historias (1080×1920).
- `render.mjs`: `node render.mjs <desde> <hasta> <carpeta> <página> <ancho> <alto>`.
- `assets/`: capturas usadas (modo oscuro).
- `entregas/`: MP4 finales.

## Rehacerlo
La copia de trabajo vive en `~/Developer/job-status-launch` (con `node_modules`). Si no existe, copiar esta carpeta a `~/Developer/`, correr `npm install` y seguir la sección 7 de la guía.

## Entregas
| Fecha | Archivo | Formato |
|---|---|---|
| 2026-10-09 | job-status-launch-20s.mp4 | 16:9, alta calidad |
| 2026-10-09 | job-status-launch-20s-liviano.mp4 | 16:9, para redes |
| 2026-10-09 | job-status-historia-ig-20s.mp4 | 9:16, historias de Instagram |

## Pendiente
Si el producto cambia de nombre, actualizar los textos y volver a renderizar las tres versiones.
