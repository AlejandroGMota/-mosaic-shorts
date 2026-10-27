# Plan: videos desde blog.alejandrogmota.com

## Flujo (por video)
1. **Guion** — Claude lo escribe desde el artículo (`Tech-Science-Blog/tmp/<id>.md`) → `guiones/<id>.md`
2. **Grabación** — Enrique lee solo las líneas de **NARRACIÓN** (las `[ANIM]` son para Claude). Graba en WAV/MP4, ritmo natural.
3. **Transcripción** — Whisper local con timestamps por palabra.
4. **Ilustración** — Claude anima siguiendo las marcas `[ANIM]` del guion, sincronizado al audio.
5. **Entrega** — `socialmedia/youtube/<id>/` (16:9) y luego cortes 9:16 para Shorts/Reels/TikTok.
6. **CTA** — cierre con link al artículo del blog (objetivo: tráfico).

## Formato estándar
- Idioma de narración: **español** (el artículo está en inglés; términos técnicos en inglés).
- Duración objetivo: **3–4 min** (≈450–550 palabras). Un artículo = un video; no se lee completo, se condensa a la idea central + 1 ejemplo + 1 acción.
- Estructura: Hook (0–10 s) → Problema → Mecanismo → Solución → Qué hacer hoy → CTA al blog.
- Colores: azul = el sistema/lo "normal", fucsia = el problema/lo nuevo, ámbar = advertencia.

## Orden de producción
Prioridad: serie Backend (encaja con marca de dev, más visual, artículos ya publicados). Idiomas después.

| # | ID | Artículo | Estado |
|---|----|----------|--------|
| 1 | b1.1 | The Dual-Write Problem | ✅ guion listo |
| 2 | b1.2 | Idempotency: APIs That Survive Retries | pendiente |
| 3 | b1.3 | Delivery Semantics & the Exactly-Once Myth | pendiente |
| 4 | b1.4 | Timeouts, Retries, and Backoff | pendiente |
| 5 | b2.2 | The Transactional Outbox | pendiente |
| 6 | b2.3 | Circuit Breakers and Bulkheads | pendiente |
| 7 | b2.6 | Sagas | pendiente |
| 8 | b1.5 | Consistency Models / CAP | pendiente |
| 9 | b2.4 | Hexagonal Architecture in Go | pendiente |
| 10 | b2.1 | Event-Driven Architecture at Scale | pendiente |
| — | a1.4 | Testing Effect (flashcards) | serie idiomas, después |
| — | a2.7 | Comprehensible Input 95% | serie idiomas, después |
| — | a4.1 | Why Duolingo Won't Make You Fluent | serie idiomas, después (buen hook) |

Nota: b2.7 en adelante aún no están publicados; no hacer video hasta que lo estén (el CTA apuntaría a nada).
