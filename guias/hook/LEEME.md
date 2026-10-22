# Hooks (ganchos de apertura)

Todo lo que sabemos sobre cómo abrir un video: la frase y el título de los primeros segundos, cómo se graba, cómo se une al cuerpo. Esta carpeta crece: cada vez que el usuario muestre un ejemplo, una referencia o una corrección sobre hooks, se guarda aquí.

| Archivo | Qué hay |
|---|---|
| `estandares.md` | Reglas vigentes sobre hooks, con fecha y origen. Es lo que Claude lee antes de editar. |
| `biblioteca/` | Un archivo por ejemplo o referencia que el usuario comparta (`AAAA-MM-DD-nombre.md`). Se parte de `biblioteca/PLANTILLA.md`. |

## Cómo se alimenta (para Claude)
1. El usuario muestra un hook (video, captura, texto) y comenta qué le gusta o qué no.
2. Crear `biblioteca/AAAA-MM-DD-nombre.md` con la plantilla: qué es, por qué funciona, qué se copia y qué no.
3. Si de ahí sale una regla general, agregarla a `estandares.md` con fecha y su origen. Si contradice una regla anterior, dejar la nueva y tachar o quitar la vieja, nunca ambas.
4. Los archivos de video o imagen pesados no se guardan en git; se anota dónde están.
5. Al editar un video, el hook sigue `estandares.md` salvo que el pedido diga otra cosa.
