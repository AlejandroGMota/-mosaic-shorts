# mosaic-shorts

Shorts del canal de YouTube «Mosaic» (nicho: cómo funciona la tecnología). El avance por Short está en `seguimiento.md`, la única fuente de verdad (✅ hecho · ⏳ en curso/siguiente · — sin empezar; fecha en cada cambio).

## Quién hace qué
- **Claude Code local** (la Mac; el directorio empieza con `/Users/admin/`): **no escribe código ni ejecuta nada**. Solo da comandos para que Enrique los corra y lleva `seguimiento.md`. Respuestas cortas: comandos y estado de `seguimiento.md`.
- **Claude Code en la nube** (claude.ai/code): escribe `pipeline/` y `animaciones/<ID>/index.html`, prueba en baja resolución, actualiza `seguimiento.md` y hace push.
- **La Mac** (M1 8 GB, macOS, bash 3.2): graba, limpia el audio, transcribe y renderiza.

## Estructura
- `guiones/` — guiones con bloques `**NARRACIÓN:**` (se lee) y `[ANIM]` (se anima). Un `###` por Short.
- `grabador/` — teleprompter + grabación WAV local (`server.py`, `index.html`).
- `pipeline/` — `shorts` (bash 3.2), `audio.py`, `config.toml`, `render.mjs`.
- `shorts/<ID>/` — archivos ligeros que sí se suben: `transcript.json`, `es.srt`, `es.vtt`.
- `animaciones/<ID>/index.html` — una animación por Short, con `window.seek(t)`.
- Solo en la Mac (fuera de git): `audios/` con los WAV, MP4/MOV, `_descartadas/`, `scrumboard/`, `posts-blog/ia-local/`.

## Ciclo por lote
1. Mac · Enrique: grabar con el grabador.
2. Mac: `shorts audio --todo` → limpia, transcribe y copia `transcript.json` + `es.srt` a `shorts/<ID>/`.
3. Mac: `git add shorts seguimiento.md && git commit -m "audio: <IDs>" && git push`.
4. Nube: escribe/ajusta `animaciones/<ID>/index.html` sincronizada con `transcript.json`, prueba en baja resolución, push y `seguimiento.md`.
5. Mac: `git pull && shorts video <ID>` → render 1080×1920 con Playwright + ffmpeg y el `audio.wav` local. 5.1 Enrique revisa.
6. Mac (Claude Code con MCP): subir a YouTube y marcar Publicado.

## Estilo (copia para la nube; el original está en la bóveda de Enrique, `Videos/Estilo.md`)
- 9:16, 1080×1920, 25 fps. Audio a −14 LUFS. Cierre de 2 s «Video completo en el canal». Subtítulos **nunca quemados** (el `.srt` se sube aparte).
- Narración de Enrique en español, sin música ni efectos.
- La animación **no debe parecer hecha con IA**: nada de fondos oscuros con neón, manchas de color difuminadas, tarjetas iguales ni rebote en todo. 3D (Blender, Eevee) para objetos físicos; 2D limpio (HTML o Manim) para diagramas. Lo visual debe ser técnicamente correcto aunque el audio tenga un error.
- En pantalla las aperturas van como `f/1.48`; la narración dice «efe uno punto cuatro ocho».
- Títulos en forma de pregunta.
- Nada de contenido fanboy de marcas (Apple u otras): primero el mecanismo; la marca solo como ejemplo cuando ayuda a entenderlo. Sin rumores ni patentes como gancho.

## Contenido (decidido 2026-10-27)
Detalle completo (qué buscamos, qué funcionó, descartes, IDs, nombres de archivo): `ideas.md`.
- Audiencia: público general curioso (México y Latam) que usa celular y compu y quiere entender cómo funcionan. Lenguaje cotidiano, sin jerga; si un término técnico hace falta, se explica en la misma frase.
- Series e IDs (letra + número; no reutilizar A, B, C): **M** memoria, chips y SO · **I** IA por dentro · **T** celular por dentro, sin marca · **R** internet y redes.
- Ritmo: 3 Shorts al día durante 2 semanas; luego se decide con métricas.

## Reglas
- Microsoft Edge, nunca Chrome.
- No borrar nada: lo que sobre va a `_descartadas/`.
- Nada de credenciales en el repo.
- Respuestas en español; código, identificadores, comentarios y commits en inglés.

## Contexto completo (solo en la Mac)
@/Users/admin/Documents/Obsidian/Enrique/Videos/Flujo.md
@/Users/admin/Documents/Obsidian/Enrique/Videos/Estilo.md
@/Users/admin/Documents/Obsidian/Enrique/Videos/Estado.md
