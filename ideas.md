# Qué buscamos (ideas y guiones)

Última actualización: 2026-10-27. Copia de trabajo para la nube; el original vive en la bóveda de Enrique (`Videos/Estilo.md`, `Videos/Estado.md`).

## La idea de un Short
- **Cómo funciona algo que la gente usa a diario**, explicado para **público general curioso** (México y Latam), sin jerga.
- **Duración (cambio del 27 oct):** menos de 3 minutos (≈ 450 palabras como tope a ~3 palabras por segundo). La longitud la decide el contenido: si explicarlo bien pide más tiempo, se alarga; si cabe en 45 s, se queda en 45 s. Ya no hay que recortar un buen guion para que quepa en 130 palabras.
- Título en forma de **pregunta**, de 60 caracteres o menos.
- Estructura: gancho (la pregunta, en los primeros 2 s) → mecanismo → un número o comparación concreta → remate. Cada Short se entiende solo; nada de «te lo explico en el siguiente» (el orden de publicación puede cambiar).
- **Mecanismo antes que marca:** la marca solo como ejemplo cuando ayuda. Sin rumores ni patentes como gancho. Nada de contenido fanboy.
- Que se pueda **animar correctamente** en 2D (diagrama, comparación, contador, flujo, zoom a un componente) o 3D para objetos físicos.
- Datos verificables, con fuente. Lo dudoso va en «Pendiente de verificar antes de publicar».

Forma de escribir (voz de Enrique, palabras difíciles, temas afines): `voz.md`.

## Qué ha funcionado (vistas al 26–27 oct 2026)
- «RAM, ROM y disco: ¿quién olvida todo al apagar?» — 791 (el mejor).
- Planificación apropiativa — 288. Swapping — 257.
- Conclusión: los fundamentos explicados con algo cotidiano funcionan mejor.

## Qué se descartó y por qué
- B5, C3, C4, C5 (`shorts-hardware-2026-10-27.md`): débiles o demasiado centrados en Apple.
- Clips de terceros en inglés (Karpathy, Linus): riesgo de Content ID.

## Series e IDs
ID = letra + número (`M1`, `I12`…); es el prefijo del nombre de las tomas (`m1-…_toma-01.wav`) y de `shorts/<ID>/` y `animaciones/<ID>/`. No reutilizar letras.

| Letra | Serie | Estado |
|---|---|---|
| A, B, C | Hardware (iPhone 18 Pro, iPhone Duo, Apple Silicon) | lote 1 · 11 grabados |
| M | Memoria, chips y SO | lote 2 |
| I | IA por dentro | lote 2 · incluye «¿Por qué una IA de 7B apenas cabe en una Mac de 8 GB?» |
| T | Celular por dentro, sin marca | lote 2 |
| R | Internet y redes | lote 2 |
| N | Noticias (qué cambia para quien hace software o tiene un negocio) | lote 3 · se publican pronto o pierden vigencia |

## Ideas para próximos lotes (anotadas el 29 oct)

Aún sin guion. Antes de escribir, verificar lo marcado y leer `voz.md`. Letras propuestas: **G** (algoritmos) y **E** (energía y baterías); confirmar que no choquen con la serie W que propone `voz.md`.

### Serie G · Algoritmos: cómo deciden las apps
Gancho común: «lo que ves no es casualidad, es una receta». Cada Short, un mecanismo dibujable.

**Recomendaciones (el centro de la serie)** — sigue de I13 (TikTok) sin repetirlo:
- **¿Cómo sabe una app qué te va a gustar si nunca te ha visto?** Filtrado colaborativo: «a quien le gustó lo mismo que a ti, también le gustó…». Dato: el Premio Netflix (2006–2009) dio un millón de dólares a quien mejorara 10 % sus recomendaciones; lo ganó una unión de equipos con 20 minutos de ventaja.
- **¿Por qué Amazon te recomienda una funda justo después de comprar un celular?** Filtrado artículo por artículo: compara productos que se compran juntos, no personas (Amazon, 2003). Animación: tabla de «se compran juntos».
- **¿Qué hace una app cuando eres nuevo y no sabe nada de ti?** El arranque en frío: preguntar gustos, mostrar lo popular, probar y medir.
- **¿Por qué el algoritmo a veces te muestra algo que no tiene nada que ver?** Explorar contra explotar: si solo te diera lo que ya te gusta, nunca aprendería nada nuevo de ti.
- **¿Por qué ves cada vez más de lo mismo?** La burbuja: cada clic refuerza el perfil. Cierre práctico: cómo «reentrenar» tu feed (marcar «no me interesa», buscar temas nuevos).
- **¿El algoritmo mide si te gustó o solo si lo viste?** Tiempo visto contra satisfacción (encuestas dentro de la app). Verificar qué publica YouTube hoy sobre «valued watch time».

**Ordenamiento: una sola idea, con ejemplo del mundo real** (no las barras de siempre):
- **Elegida: ¿Cómo ordenas un millón de paquetes sin comparar dos?** Ordenamiento por dígitos (radix sort), el que usaban las máquinas de tarjetas perforadas desde fines del siglo XIX: se reparten los paquetes en 10 cajones por el último dígito del código postal, se juntan en orden y se repite con el siguiente dígito. Con 5 dígitos (los códigos postales de México) son 5 pasadas, sin comparar nunca un paquete contra otro. Animación: banda con paquetes y 10 cajones por pasada. Verificar: cómo ordenan hoy las paqueterías (Correos de México, Estafeta); el guion debe decir que es el principio, no afirmar que lo usan tal cual.
- *Respaldo:* **¿Por qué ordenar algo que ya está casi en orden es instantáneo?** Timsort (Tim Peters, 2002), el que usan Python y Chrome (desde 2018): busca tramos que ya vienen ordenados y solo los fusiona. Ejemplo cotidiano: ordenar tu lista de contactos cuando solo agregaste dos.
- *Relacionada, si se quiere un gancho viral:* ¿Por qué el «aleatorio» de tu música no se siente aleatorio? (Es mezclar, no ordenar; verificar qué cambiaron los servicios de música en su modo aleatorio.)

**Redes neuronales que clasifican imágenes** — sigue de I5 (cómo aprende a reconocer un gato) sin repetirlo:
- **¿Cómo ve una foto una IA?** Píxeles → números → filtros que detectan bordes, luego formas, luego objetos (capas de una red convolucional). Animación: un filtro de 3×3 recorriendo la foto.
- **¿Cómo encuentra tu celular todas tus fotos de «perro»?** Clasificación dentro del celular, sin subir tus fotos; etiquetas con probabilidad. Verificar qué hace cada sistema en el dispositivo y qué en la nube.
- **¿Por qué una IA confunde un chihuahua con un panqué?** Errores por parecido de patrones (el meme chihuahua contra muffin); qué ve la red en realidad.
- **¿Una calcomanía puede engañar a una IA?** Ejemplos adversarios: cambios mínimos que hacen que una señal de alto se clasifique mal. Verificar el estudio original antes de citarlo.

### Serie E · Energía y baterías (rama de hardware)
Puede ser un Short largo (hasta 3 min) o una mini-serie de 3 a 4.
- **¿Qué hay dentro de una batería y por qué hay tantos tipos?** (el largo, línea de tiempo):
  - 1800: pila de Volta (zinc, cobre y papel con salmuera), la primera con corriente continua.
  - 1859: plomo-ácido de Planté, la primera recargable; la idea sigue en las baterías de coche de 12 V.
  - 1899: níquel-cadmio (Jungner).
  - Años cincuenta: alcalina (las AA de siempre); verificar inventor y año.
  - 1989: níquel-metal hidruro (NiMH), las recargables de cámara y control.
  - 1991: primera batería de ion-litio comercial (Sony); Premio Nobel de Química 2019 a Goodenough, Whittingham y Yoshino (verificar en nobelprize.org).
  - Hoy: química del cátodo dentro del ion-litio (LCO en celulares, NMC y LFP en coches eléctricos), sodio-ion y estado sólido en desarrollo (verificar estado comercial al grabar).
  - Mecanismo común: ánodo, cátodo, electrolito y separador; los iones viajan por dentro y los electrones por fuera, por el circuito.
- **¿Por qué los coches eléctricos usan baterías distintas a las del celular?** LFP contra NMC: costo, duración en ciclos, seguridad y densidad de energía.
- **¿Por qué las baterías de litio a veces se inflan o se incendian?** Separador dañado, cortocircuito interno, calor que se alimenta solo. Relación con T5 (desgaste) y T4 (carga lenta al final).
- **¿Qué es una batería de estado sólido y por qué todavía no la tienes?** Electrolito sólido en vez de líquido; promesa contra problemas de fabricación. Solo con fuentes primarias, sin rumores (regla del canal).

Fuentes de la investigación inicial: [Wikipedia: Punched card sorter](https://en.wikipedia.org/wiki/Punched_card_sorter) · [Wikipedia: Radix sort](https://www.wikipedia.org/wiki/Radix_sort) · [V8: Getting things sorted (2018)](https://v8.dev/blog/array-sort) · [Netflix Prize, arXiv 1202.1112](https://arxiv.org/pdf/1202.1112) · [TechRadar: cómo saben los algoritmos de recomendación lo que te gusta](https://www.techradar.com/news/internet/how-recommendation-algorithms-know-what-you-ll-like-1078924) · [Mining.com: evolución de las baterías](https://www.mining.com/web/infographic-the-evolution-of-battery-technology/) · [Naval Technology: línea de tiempo del ion-litio](https://www.naval-technology.com/analyst-comment/lithium-ion-lib-timeline/)

## Nombres de archivo
- Un archivo por lote: `guiones/shorts-lote-NN-AAAA-MM-DD.md` (el lote 1 se llama `shorts-hardware-2026-10-27.md`).
- Dentro: `## SERIE <letra> · <tema>`, y por Short `### <ID> [⭐] <Título?>`, luego `**NARRACIÓN:**` y `[ANIM]`.
- La NARRACIÓN se escribe como se lee en voz alta («cinco ge», «efe uno punto cuatro ocho»); en pantalla (`[ANIM]`) va la forma escrita (5G, f/1.48).
- ⭐ = los mejores, se graban primero.

## Ritmo
3 Shorts al día durante 2 semanas; después se decide con métricas si se sube (meta de Enrique: 10 al día).
