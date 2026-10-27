# Gestión de la memoria — render

Requisitos (gratis): Python 3, `pip install cairocffi pangocffi pangocairocffi numpy`, ffmpeg, fuentes Inter y JetBrains Mono.

- `engine.py` — motor 2D (cairo/pango → ffmpeg).
- `scenes.py` — las 8 escenas; los tiempos en segundos salen de `transcript.json` (timestamps por palabra).
- `render_part.py <inicio> <fin> <salida.mp4>` — renderiza un tramo (se paraleliza en 4 y se concatena).
- Previsualizar un frame: `python -c "from scenes import *; still(frame, 75, 'f.png')"`
