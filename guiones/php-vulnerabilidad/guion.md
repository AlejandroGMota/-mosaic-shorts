# Guion: ¿Qué es PHP? y PHP2Shell, la falla que puso en alerta a medio internet

Mosaic · Serie "Sistemas operativos / explicado"
Duración objetivo: 3–4 min (~500 palabras de narración)
Datos al 22 de octubre de 2026. Revisar antes de grabar si CISA lo agregó al catálogo KEV o si hay compromisos confirmados.

---

## 1. Hook (0:00–0:20)

**NARRACIÓN:**
Casi siete de cada diez sitios web —de los que se sabe con qué están hechos— funcionan con un lenguaje del que quizá nunca has oído hablar. Y esta semana, ese lenguaje recibió un parche de emergencia por dos fallas críticas. Hoy te explico qué es PHP, qué pasó y qué tienes que hacer si tienes un sitio web.

**[ANIM]** Pantalla negra → contador que sube hasta "69.3 %" con una cuadrícula de 10 iconos de navegador; 7 se iluminan. Título "PHP2Shell" aparece con efecto de alerta roja parpadeante. Fuente pequeña: "W3Techs, oct 2026".

---

## 2. ¿Qué es PHP? (0:20–1:05)

**NARRACIÓN:**
PHP es un lenguaje de programación que se ejecuta en el servidor, no en tu navegador. Cuando entras a una página, el servidor ejecuta el código PHP, arma el HTML y te manda solo el resultado.
Nació en 1994 como un proyecto personal de Rasmus Lerdorf para su propia página. Hoy mueve WordPress, Drupal, Joomla, Laravel y hasta Wikipedia.
Según W3Techs, PHP está detrás del 69.3 % de los sitios cuyo lenguaje de servidor se conoce. Y aquí viene el dato incómodo: más de un tercio de esos sitios usan versiones viejas que ya no reciben parches.

**[ANIM]** Diagrama de flujo: navegador → flecha "petición" → caja servidor con logo "PHP" (engranes girando) → flecha "HTML" de vuelta al navegador. Luego línea de tiempo horizontal: 1994 "Personal Home Page" → 1998 PHP 3 → 2015 PHP 7 → 2020 PHP 8 → 2026 PHP 8.5. Cierra con barra apilada: PHP 8 / PHP 7 / PHP 5, resaltando en rojo las versiones sin soporte.

---

## 3. La vulnerabilidad (1:05–1:45)

**NARRACIÓN:**
El 21 de octubre de 2026, el equipo de PHP publicó actualizaciones urgentes para dos fallas en el corazón del lenguaje: CVE-2026-109618 y CVE-2026-109619, apodadas "PHP2Shell".
Las dos tienen severidad crítica, 9.2 sobre 10, y permiten algo grave: ejecutar código en tu servidor sin necesidad de usuario ni contraseña.
Ya hay intentos de ataque reportados por empresas de seguridad como watchTowr y Cloudflare. Lo que todavía no hay es confirmación pública de servidores comprometidos. Pero la CISA, la agencia de ciberseguridad de Estados Unidos, ya pidió parchear de inmediato.

**[ANIM]** Dos "tarjetas" de CVE que entran desde los lados con los números. Medidor tipo velocímetro que sube a 9.2 en zona roja. Icono de candado abierto + texto "Sin autenticación". Mapa con pulsos naranjas = "intentos detectados", con etiqueta clara "intentos, no compromisos confirmados".

---

## 4. ¿Cómo funciona? (1:45–2:40)

**NARRACIÓN:**
Sin entrar en detalles peligrosos, la idea es esta.
Primera falla: un atacante envía una petición, por ejemplo una subida de archivos, diseñada para que PHP se quede sin memoria justo en el peor momento. PHP deja datos a medio armar y después los usa como si estuvieran bien. Esa memoria corrupta puede convertirse en una puerta para ejecutar código. En servidores Apache con mod_php puede pasar incluso antes de que tu aplicación se ejecute.
Segunda falla: un error fatal deja "basura" de una petición anterior. Si la siguiente petición cae en el mismo proceso, PHP usa memoria que ya había liberado.
Y además de ejecutar código, estas fallas pueden filtrar datos de otras peticiones: contraseñas, tokens o llaves de API.

**[ANIM]** Animación de un "almacén" de memoria con cajas. Falla 1: llega un paquete enorme, la barra de memoria se llena, una caja queda a medio armar (bordes punteados) y luego es tomada como válida → se pone roja. Falla 2: dos peticiones en fila; la primera se cae con "error fatal", deja una caja fantasma; la segunda la toma → alerta. Cierra con cajas de las que salen iconos de llave y contraseña "escapando". Sin código en pantalla.

---

## 5. Qué hacer hoy (2:40–3:30)

**NARRACIÓN:**
Si tienes un sitio con PHP, esto es lo que importa.
Uno: revisa tu versión. Las versiones corregidas son 8.5.12, 8.4.27, 8.3.36 y 8.2.35.
Dos: actualiza y reinicia los procesos de PHP. Si estás en hosting compartido, confirma con tu proveedor que ya aplicó el parche.
Tres: ojo, actualizar WordPress o tus plugins no arregla esto. El problema está en PHP, no en tu CMS.
Cuatro: si sigues en PHP 8.1 o anterior, es momento de migrar. Mientras tanto, usa un firewall de aplicaciones y limita el tamaño de las peticiones. Son parches temporales, no una solución.
Y si estuviste expuesto, cambia tus contraseñas y llaves de API.

**[ANIM]** Checklist animada con 5 casillas que se marcan una a una. En el paso 1, terminal estilizada mostrando "php -v" y un número de versión que pasa de rojo a verde. En el paso 3, logo genérico de CMS con una "X" y flecha hacia el motor "PHP". En el paso 4, escudo con "WAF" y un embudo que reduce el tamaño de un paquete.

---

## 6. Cierre / CTA (3:30–3:50)

**NARRACIÓN:**
PHP lleva más de treinta años sosteniendo buena parte de internet, y esta falla nos recuerda que lo que no se ve también se tiene que mantener.
En el blog tienes la investigación completa con todas las fuentes y los pasos detallados: blog.alejandrogmota.com. Suscríbete a Mosaic para más sistemas explicados, y comparte este video con quien tenga un sitio web. Nos vemos.

**[ANIM]** Zoom out del servidor hasta un globo terráqueo lleno de puntos de luz (sitios PHP). Tarjeta final con URL "blog.alejandrogmota.com" grande, botón de suscripción de Mosaic y texto "Serie: Sistemas operativos / explicado".

---

### Notas de producción
- Narración ≈ 500 palabras → ~3:30–3:50 a ritmo pausado.
- Mantener en pantalla la etiqueta "intentos, no compromisos confirmados" para no exagerar.
- Fuentes completas en `investigacion.md`.
- Revisión 22 oct (sesión principal): hook ajustado — el 69.3 % de W3Techs es sobre sitios cuyo lenguaje de servidor se conoce, no "sitios que visitas". CVE, versiones corregidas y CVSS 9.2 verificados contra el aviso oficial en php.net/archive/2026.php.
- El CTA manda al blog, pero esta investigación todavía no es un artículo publicado: publicarla antes del video o cambiar el CTA.
