# Shorts · Gestión de la memoria por el SO

Fuente: video completo https://youtu.be/qW7c3KGP4vk (canal Mosaic). Formato: 1080x1920, 25 fps, sin subtítulos quemados, cierre de 2 s "Video completo en el canal".
Tramos tomados del audio original (se evita 61.5–94.7 s por el error técnico de "direcciones físicas en disco").

> Fechas: el video completo ya es público, así que estos salen primero (23–26 oct, 7 pm). Los del procesador van del 28 oct al 1 nov, después de publicar su video completo el 27.

| # | Archivo | Audio (s) | Duración | Fecha sugerida |
|---|---------|-----------|----------|----------------|
| 01 | 01-ram-rom-disco.mp4 | 19.5–61.3 | 43.8 s | vie 23 oct 2026 |
| 02 | 02-particiones-estaticas.mp4 | 94.5–116.9 | 24.4 s | sáb 24 oct 2026 |
| 03 | 03-particiones-dinamicas.mp4 | 117.0–145.3 | 30.3 s | dom 25 oct 2026 |
| 04 | 04-segmentacion.mp4 | 145.4–178.4 | 35.0 s | lun 26 oct 2026 |

---

## 01 · RAM, ROM y disco
**Título:** RAM, ROM y disco: ¿quién olvida todo al apagar? #Shorts

**Descripción:**
La RAM guarda lo que estás ejecutando, pero es volátil: se apaga y lo pierde todo. La ROM solo se lee y guarda el firmware de arranque. Y el disco (SSD o HDD) conserva tus archivos de forma permanente hasta que un programa se carga a la RAM para ejecutarse.

Video completo: https://youtu.be/qW7c3KGP4vk
Más en el blog: https://blog.alejandrogmota.com

#Shorts #SistemasOperativos #RAM #ROM #Informática #Programación #AprendeEnYouTube

---

## 02 · Particiones estáticas
**Título:** Particiones fijas: así se desperdicia la memoria #Shorts

**Descripción:**
Con particiones estáticas la memoria se divide en bloques de tamaño fijo. Si un proceso de 128 KB cae en una partición de 512 KB, 384 KB quedan sin usar: eso es fragmentación interna. El SO lleva una tabla con el tamaño y el estado de cada partición.

Video completo: https://youtu.be/qW7c3KGP4vk
Más en el blog: https://blog.alejandrogmota.com

#Shorts #SistemasOperativos #GestiónDeMemoria #Fragmentación #Informática #Programación

---

## 03 · Particiones dinámicas
**Título:** Particiones dinámicas: memoria a la medida de cada proceso #Shorts

**Descripción:**
En particiones dinámicas cada proceso recibe justo el espacio que necesita, uno tras otro y sin huecos. El SO anota base, tamaño y estado de cada proceso (en su PCB) y lleva una tabla del espacio libre. Cuando un proceso termina deja un hueco que puede ocupar otro más pequeño.

Video completo: https://youtu.be/qW7c3KGP4vk
Más en el blog: https://blog.alejandrogmota.com

#Shorts #SistemasOperativos #GestiónDeMemoria #PCB #Informática #Programación

---

## 04 · Segmentación
**Título:** Segmentación: tu programa se carga en pedazos #Shorts

**Descripción:**
Con segmentación un proceso no ocupa un solo bloque: se divide en segmentos (código, datos, pila) y la MMU ubica cada uno donde haya espacio. Se puede liberar un solo segmento mientras el resto sigue en memoria, y un segmento en espera ocupa ese lugar.

Video completo: https://youtu.be/qW7c3KGP4vk
Más en el blog: https://blog.alejandrogmota.com

#Shorts #SistemasOperativos #Segmentación #MMU #Informática #Programación

---

## Estado
- Renderizados el 22 oct con el código de `claude/codigo-shorts-memoria.md` (la tarea en la nube no pudo guardar los mp4 en la Mac).
- `.srt` de cada Short recortados del `gestion-memoria-so.es.srt` corregido del video completo.
- Audio normalizado a −14 LUFS.
- Copias en `instagram/gestion-memoria-so/` y `tiktok/gestion-memoria-so/` (quitar `#Shorts` del texto ahí).
