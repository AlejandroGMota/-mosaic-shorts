# animaciones

Una carpeta por Short (`A2/index.html`) sobre la plantilla `_base/` (`base.css` + `base.js`).

## Agregar un Short

1. Copia `A2/` a `<ID>/` (por ejemplo `A3/`).
2. En `index.html` cambia `kicker`, `title` (siempre en forma de pregunta) y `SCRIPT` (la NARRACIÓN
   del guion, copiada tal cual).
3. Escribe las `anchors` en el orden de la narración: nombre → palabra o frase. Se buscan en
   `TRANSCRIPT` sin acentos ni mayúsculas, a partir de la anterior. Para números usa alternativas:
   `["seis hojas", "6 hojas"]` o `Mosaic.fnum("1.48")` (cubre «uno punto cuatro ocho», «1.48», «f/1.48»).
   Si una palabra no aparece, se estima por su posición en el guion y sale un aviso en el render.
4. Arma el DOM/SVG en `build()` y edita la lista `scenes`:
   `{ el: "#id", from: "ancla", to: "otra+0.3", fade: 0.4, update(t, s, A) {...} }`.
   Tiempos: número, `"ancla"`, `"ancla.end"`, `"ancla-0.2"`, `"start"`, `"end"` (fin del audio).
5. Revisa a mano en Edge (barra de reproducción, `?t=12.5`, arrastra el `transcript.json`) y luego
   `shorts video <ID> --preview`.

## Reglas

- `seek(t)` es pura: todo se calcula desde `t` (y `A`). Nada de `requestAnimationFrame`, `setTimeout`,
  `Math.random()` ni transiciones CSS (la plantilla las desactiva).
- Estilo: fondo claro, tipografía sobria, un protagonista por escena, easing suave, sin neón, sin manchas
  difuminadas, sin tarjetas iguales, sin rebote.
- Lo que se dibuja tiene que ser técnicamente correcto aunque la narración se equivoque.
- Aperturas en pantalla como `f/1.48`.
- Zona segura: el contenido importante entre y = 170 y 1540, x = 80 y 940 (YouTube tapa bordes).

Helpers: `Mosaic.ramp(t, a, b, ease)`, `Mosaic.keys(t, [[t0, v0], [t1, v1]])`, `Mosaic.lerp`,
`Mosaic.clamp`, `Mosaic.ease.{inOut,out,in,inOutSine}`, `Mosaic.el(tag, attrs, parent)`.
