# pipeline

Del WAV grabado al MP4 1080×1920 del Short. Todo corre en la Mac (M1, macOS, bash 3.2 / zsh).

```
audios/<guion>/<short>_toma-NN.wav     (grabador, solo en la Mac)
        │  shorts audio A2   →  limpia ruido, acorta pausas, −14 LUFS (2 pasadas), transcribe
        ▼
audios/<guion>/final/<short>/audio.wav, info.json            (solo en la Mac)
shorts/A2/transcript.json, es.srt, es.vtt                    (se suben a git)
        │  shorts video A2   →  Edge (Playwright) abre animaciones/A2/index.html,
        ▼                       window.seek(t) fotograma a fotograma → ffmpeg H.264 + AAC
audios/<guion>/final/<short>/A2.mp4                           (solo en la Mac)
```

- La toma que se usa es la de mayor `NN` en `audios/<guion>/`; lo que está en `_descartadas/` se ignora.
- El ID sale del prefijo del nombre: `a2-como-funciona-..._toma-01.wav` → `A2`.
- Nunca se borra nada: si un archivo se va a sobrescribir, la versión anterior se mueve a
  `audios/<guion>/_descartadas/<short>/<fecha-hora>/`.
- Subtítulos nunca quemados: `es.srt` / `es.vtt` se suben aparte a YouTube.
- Duración del video = duración de `audio.wav` + 2 s de cierre «Video completo en el canal».

## Instalación (una vez)

```bash
brew install ffmpeg whisper-cpp node
```

```bash
brew install --cask microsoft-edge
```

Modelo de whisper.cpp (≈550 MB, cabe bien en 8 GB y usa Metal):

```bash
mkdir -p ~/models/whisper
```

```bash
curl -L -o ~/models/whisper/ggml-large-v3-turbo-q5_0.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin
```

Playwright (usa el Edge instalado, no descarga navegadores):

```bash
cd ~/proyectos/proyectosPersonales/socialmedia/pipeline && npm install
```

Alias en `~/.zshrc`:

```bash
alias shorts='bash ~/proyectos/proyectosPersonales/socialmedia/pipeline/shorts'
```

Opcional, solo si whisper.cpp no funciona (faster-whisper en CPU, más lento):

```bash
python3 -m venv ~/.venvs/fw && ~/.venvs/fw/bin/pip install faster-whisper
```

Revisar que todo esté:

```bash
shorts doctor
```

## Uso

Probar toda la cadena con un WAV sintético (no toca tus audios; trabaja en una carpeta temporal):

```bash
shorts prueba A2
```

Procesar audio de un Short o de todos los que tengan toma nueva:

```bash
shorts audio A2
```

```bash
shorts audio --todo
```

Subir los archivos ligeros:

```bash
git add shorts seguimiento.md && git commit -m "audio: A2" && git push
```

Render rápido para revisar (540×960, 12 fps) y render final:

```bash
shorts video A2 --preview
```

```bash
shorts video A2
```

Guardar fotogramas sueltos (segundos) para revisar sin hacer el video:

```bash
shorts video A2 --preview --capturas 3,10,25 --solo-capturas
```

Estado de todos los Shorts:

```bash
shorts estado
```

Abrir una animación a mano en Edge (barra para reproducir; arrastra `shorts/A2/transcript.json`
sobre la página para usar los tiempos reales):

```bash
open -a "Microsoft Edge" ~/proyectos/proyectosPersonales/socialmedia/animaciones/A2/index.html
```

## Opciones

| Comando | Opción | Qué hace |
|---|---|---|
| `audio` | `--engine whisper.cpp\|faster-whisper\|guion` | motor de transcripción (por defecto `auto`: whisper.cpp y si no, faster-whisper) |
| `audio` | `--force` | con `--todo`, rehace también lo ya procesado |
| `audio` | `--guion <nombre>` | otro guion (por defecto el de `config.toml`) |
| `video` | `--preview` | 540×960 a 12 fps |
| `video` | `--capturas 2,10` / `--solo-capturas` | PNG de esos segundos en `final/<short>/capturas*/` |
| `video` | `--audio`, `--transcript`, `--out`, `--browser chromium` | solo para pruebas |

El motor `guion` no transcribe: reparte las palabras del guion sobre los tramos con voz. Sirve para
probar sin whisper; los tiempos son aproximados.

Todo lo ajustable (rutas, LUFS, umbral de silencio, pausa máxima, modelo, resolución, fps) está en
`config.toml`. La variable `SOCIALMEDIA_DIR` cambia la carpeta raíz.

## transcript.json

Esquema `mosaic-transcript/1`, tiempos en segundos del `audio.wav` final. Definición completa en el
encabezado de `audio.py`.

```json
{
  "schema": "mosaic-transcript/1",
  "id": "A2",
  "short": "a2-como-funciona-la-apertura-variable-del-iphone-18-pro",
  "language": "es",
  "duration": 43.512,
  "engine": "whisper.cpp",
  "model": "ggml-large-v3-turbo-q5_0.bin",
  "source_take": "a2-como-funciona-la-apertura-variable-del-iphone-18-pro_toma-01.wav",
  "created": "2026-10-27T20:00:00Z",
  "text": "Por primera vez, un iPhone tiene apertura variable. ...",
  "words": [{ "i": 0, "text": "Por", "norm": "por", "start": 0.15, "end": 0.38, "p": 0.97 }],
  "segments": [{ "i": 0, "start": 0.15, "end": 1.2, "text": "Por primera vez,", "first": 0, "last": 2 }]
}
```

`norm` = minúsculas, sin acentos, solo `[a-z0-9]` (así se buscan las anclas). `segments` son los mismos
subtítulos de `es.srt`.

## Animaciones

Cada Short es `animaciones/<ID>/index.html` sobre la plantilla `animaciones/_base/` (ver
`animaciones/README.md`). Contrato con el renderer:

- `render.mjs` inyecta `window.TRANSCRIPT` y `window.RENDER` con `addInitScript` (file:// no permite fetch).
- `window.seek(t)` dibuja el fotograma del segundo `t`: función pura, sin `requestAnimationFrame`, timers ni
  transiciones CSS.
- Después de `audio.duration` la plantilla muestra el cierre de 2 s.
