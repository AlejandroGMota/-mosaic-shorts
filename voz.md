# Voz de Enrique: cómo escribir guiones que suenen a él

Última actualización: 2026-10-27. Léelo antes de escribir o ajustar cualquier guion. Complementa a `ideas.md` (qué contar) con **cómo contarlo**.

Base: comparación palabra por palabra entre lo escrito y lo grabado en los 11 Shorts del lote 1 (`shorts/<ID>/transcript.json` contra `guiones/shorts-hardware-2026-10-27.md`). Desde el lote 2 la regla es leer el guion tal cual, así que el guion tiene que estar escrito ya como Enrique habla.

---

## Quién habla

- Enrique es **ingeniero de software** (full stack: web, APIs, bases de datos, automatización con IA). Explica tecnología como alguien que la construye, no como reseñista de productos.
- Público: gente curiosa de México y Latam que usa celular y compu. Tutea («tu celular», «tu compu»).
- Tono: claro, tranquilo, sin exagerar. Nada de «¡increíble!», «te va a volar la cabeza» ni misterio artificial.

## Lo que hace al leer (y por qué el guion ya debe venir así)

| Lo que hizo al grabar | Ejemplos reales | Regla para escribir |
|---|---|---|
| Cambia la marca por el objeto genérico | «el iPhone» → «los teléfonos»; «del iPhone Duo» → «de un teléfono plegable» | Mecanismo primero: escribe el objeto genérico; la marca solo si es la noticia. |
| Quita los apartes editoriales | «Ojo:», «Y un dato honesto:», «Moraleja:», «Eso te lo explico en el siguiente» | No uses muletillas de guionista. Si un dato es importante, va como frase normal. |
| Agrega conectores de explicación | «por ejemplo», «es decir, que», «o sea», «Pero,», «Ahora,», «se llama» | Úsalos: así explica él. Uno o dos por guion, no en cada frase. |
| Prefiere frases completas a las cortadas con dos puntos | «Primero: la pantalla…» → «Primero, la pantalla…»; «ese plano» → «esa parte plana» | Escribe oraciones normales con sujeto y verbo. Pocos dos puntos. |
| Cambia palabras coloquiales o raras por neutras | «poquito» → «poco»; «sale con» → «tiene»; «usa» → «utiliza»; «al cien por ciento» → «a su estado original» | Vocabulario neutro y claro, sin diminutivos. |
| Ajusta concordancias al plural | «quede» → «queden»; «se vuelve» → «se vuelven»; «tiene» → «tienen» | Que el sujeto de cada verbo sea obvio. Evita frases con dos sujetos posibles. |
| Recorta datos de precisión al final de una frase larga | se perdió «en un número pequeño de equipos» (B2) y el número de patente (B3) | Los matices importantes van **al principio** de la frase o en una frase propia, no colgados al final. |

**Velocidad real:** entre 2.5 y 3.4 palabras por segundo; promedio ≈ 2.9. Para estimar la duración: 1 minuto ≈ 175 palabras; 3 minutos (el tope) ≈ 520 palabras.

## Palabras que se complican (al leerlas o al transcribirlas)

Whisper las escribió mal; puede ser pronunciación o el reconocedor, pero en ambos casos rompen las anclas de la animación:

| Escrito | Se transcribió | Mejor escribir |
|---|---|---|
| converge | «corveje» | «coincide en un punto» |
| nano-textura | «anotextura» | «una textura microscópica» |
| bisagra | «brisagra» | «bisagra» (va bien si se pronuncia despacio) o «la unión» |
| plegables | «pregables» | «plegables», pero no dos veces seguidas con «pantallas» |
| fingía | «fijía» | «simulaba» |
| iPhone Duo | «iPhone 2» | evitar nombres de modelo; si hace falta, escribir «el plegable de Apple» |

Otras reglas:
- **Números:** se escriben como se dicen («efe uno punto cuatro ocho», «dieciséis mil millones»). El reconocedor los pasa a dígitos y eso está bien: las animaciones aceptan las dos formas.
- **Siglas:** como se leen («cinco ge», «ce pe u» solo si hace falta; mejor «el procesador»).
- **Inglés:** solo los términos que de verdad se usan así (token, wifi, bluetooth) y explicados en la misma frase.
- **Trabalenguas:** evita varias palabras con «r» doble o «pl/pr» juntas («pantallas plegables prometen…»).

## Estructura que le funciona

1. **Gancho en forma de pregunta**, cotidiano y concreto, en la primera frase.
2. **Mecanismo** explicado con una comparación de la vida diaria (el escritorio y la bodega, la carretera y los carriles).
3. **Un número o comparación concreta** que se pueda dibujar.
4. **Remate práctico** («si vas a vender tu compu…») o una frase que cierre la idea. Nunca «en el siguiente video».

Duración: lo que pida el tema, siempre menos de 3 minutos (ver `ideas.md`).

## Temas afines a su carrera (para nuevas ideas)

Mismo nicho del canal (cómo funciona la tecnología de todos los días), visto desde quien hace software. Propuesta de serie nueva **W · La web y el software por dentro** (letra libre; no reutilizar A, B, C, M, I, T, R, N):

- ¿Qué pasa cuando le das «pagar» en una tienda en línea? (pasarela, banco, 3-D Secure)
- ¿Por qué las páginas guardan tu contraseña sin saberla? (hash)
- ¿Qué es una API y por qué todas las apps la usan? (mesero que lleva pedidos)
- ¿Por qué se cae una página cuando todos entran a la vez? (capacidad, colas, caché)
- ¿Qué es una cookie y por qué todas te piden permiso?
- ¿Cómo llega un código de verificación por SMS y por qué no es tan seguro?
- ¿Por qué el botón de «pagar» no te cobra dos veces si le picas dos veces? (idempotencia; viene del artículo del blog b1.2)
- ¿Qué pasa cuando una app «se reintenta» sola? (retries y backoff; del blog b1.4)
- ¿Cómo una IA usa herramientas, como consultar tu calendario? (MCP, de su experiencia construyendo uno)
- ¿Cómo funciona un bot de WhatsApp por dentro?
- ¿Qué es la nube para quien publica una página? (servidores, hosting, despliegue)
- ¿Por qué tu app pide actualizarse tan seguido? (parches de seguridad, dependencias)

Regla: si el tema no se puede explicar a alguien que no programa, no es Short; puede ir al video largo.

## Pendiente de confirmar con Enrique

1. ¿Hablas en primera persona de tu trabajo («en mi trabajo hago APIs…») o el canal se queda impersonal?
2. ¿Mencionas tu profesión en algún Short («soy ingeniero de software y…») como gancho de confianza?
3. ¿Hay palabras que no te gustan o que nunca dirías? ¿Muletillas tuyas que sí quieres conservar («o sea», «es decir»)?
4. ¿Algún toque de humor o se queda serio?
5. ¿La serie W te late, o esos temas van mejor como videos largos del blog?
