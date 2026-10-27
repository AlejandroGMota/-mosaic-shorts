# ¿Qué es PHP? + PHP2Shell (CVE-2026-109618 / CVE-2026-109619)

Investigación para video de Mosaic — serie "Sistemas operativos / explicado"
Fecha de corte: 22 de octubre de 2026. La situación sigue cambiando (exploits, catálogo KEV de CISA); revisar fuentes antes de publicar.

> Verificado el 22 oct contra el aviso oficial (php.net/archive/2026.php): CVE-2026-109618 (OOM corruption, GHSA-w8hw-w9fx-j79w) y CVE-2026-109619 (stale global state, GHSA-6wmf-4rv5-p3rp); corregidas en 8.5.12, 8.4.27, 8.3.36 y 8.2.35; CVSS v4.0 9.2 según el aviso previo del 20 oct; backports mínimos de código fuente para 7.4, 8.0 y 8.1. El aviso de php.net habla de un exploit demostrado en mod_php, pero no de explotación activa. Entre sus mitigaciones temporales está `memory_limit = -1` fijado con `php_admin_value` (para que la app no lo pueda cambiar) junto con `post_max_size` bajo; léelo en el aviso original antes de aplicarlo, porque contradice la intuición.

---

## 1. ¿Qué es PHP?

**Definición.** PHP ("PHP: Hypertext Preprocessor") es un lenguaje de programación interpretado del lado del servidor. Cuando visitas una página hecha en PHP, el servidor ejecuta el código, genera HTML y te envía solo el resultado; el navegador nunca ve el código PHP.

**Historia breve.**
- 1994–1995: Rasmus Lerdorf crea "Personal Home Page Tools", un conjunto de scripts para su web personal.
- 1997–1998: Andi Gutmans y Zeev Suraski reescriben el motor; PHP 3 adopta el nombre recursivo "PHP: Hypertext Preprocessor". Más tarde nace el motor Zend (PHP 4).
- 2015: PHP 7, gran salto de rendimiento.
- 2020: PHP 8 (compilador JIT, tipos más estrictos). Ramas con soporte hoy: 8.2, 8.3, 8.4 y 8.5. La 8.2 llega a fin de vida el 31 de diciembre de 2026 (según The Hacker News).
- Desde 2021 la **PHP Foundation** financia el desarrollo del núcleo.

**Para qué se usa.** Sitios dinámicos, tiendas en línea, APIs, paneles de administración. Lo usan CMS como WordPress, Drupal y Joomla, y frameworks como Laravel y Symfony. Wikipedia (MediaWiki) está hecha en PHP.

**Cuota de uso (W3Techs, datos del 22 de octubre de 2026):**
- PHP se usa en el **69.3 %** de los sitios web cuyo lenguaje del lado del servidor se conoce.
- Por versión mayor (entre sitios con PHP): PHP 8 = 65.3 %, PHP 7 = 26.9 %, PHP 5 = 7.7 %.
- Dentro de PHP 8: 8.3 = 34.8 %, 8.2 = 27.7 %, 8.1 = 15.2 %, 8.4 = 12.1 %, 8.0 = 5.8 %, 8.5 = 4.4 %.
- Dato clave para el video: más de un tercio de los sitios con PHP corren versiones 5.x, 7.x, 8.0 u 8.1, que ya no reciben parches oficiales.

---

## 2. La vulnerabilidad: "PHP2Shell"

Dos fallos críticos en el **núcleo** de PHP (no en un plugin ni en un framework), publicados juntos y apodados **PHP2Shell** / "php2shell".

| | CVE-2026-109618 | CVE-2026-109619 |
|---|---|---|
| Aviso GitHub | GHSA-w8hw-w9fx-j79w | GHSA-6wmf-4rv5-p3rp |
| Tipo | Corrupción de memoria al quedarse sin memoria (OOM) | Uso de memoria liberada (use-after-free) por estado "rancio" entre peticiones |
| Impacto | Ejecución remota de código sin autenticación | Ejecución remota de código sin autenticación |
| Severidad | CVSS v4.0 **9.2 (Crítica)** | CVSS v4.0 **9.2 (Crítica)** |
| Vector (Rapid7) | AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H | igual |

Notas sobre la severidad:
- Un **10.0** que circuló el 20 de octubre con la filtración es **incorrecto**, según la PHP Foundation.
- No pude consultar NVD (no devolvió datos), así que **no está confirmado** quién asignó el puntaje ni la clasificación CWE oficial.

### 2.1 CVE-2026-109618 — corrupción por falta de memoria
- Si una petición alcanza el `memory_limit` "justo en el momento equivocado", PHP puede dejar datos internos inicializados a medias y después tratarlos como válidos, corrompiendo la memoria (PHP Foundation; Google Cloud).
- Se alcanza mediante peticiones multipart (subida de archivos) manipuladas que agotan memoria aunque parezcan respetar los límites configurados (Rapid7; Tanium).
- Según el aviso citado por Rapid7, funciona con los límites por defecto y, en **Apache mod_php**, puede ocurrir **antes de que se ejecute cualquier código de la aplicación**. mod_php es la configuración de mayor riesgo.
- Despliegues mencionados como en riesgo: PHP-FPM, Apache mod_php, php-cgi, FrankenPHP, LiteSpeed.
- **Discrepancia:** la PHP Foundation dice que también se confirmó RCE en PHP-FPM a través de rutas de la aplicación; Rapid7 dice que el aviso no reporta un exploit completo en FPM para este CVE.

### 2.2 CVE-2026-109619 — estado "rancio" entre peticiones
- Un error fatal en el punto equivocado puede dejar estado interno apuntando a memoria que pertenecía a una petición anterior; una petición siguiente en el mismo proceso usa esa memoria ya liberada (PHP Foundation; Rapid7).
- Rutas confirmadas en el aviso (vía Rapid7): mod_php mediante la función de *backtraces* en errores fatales de PHP 8.5 (`fatal_error_backtraces`, activada por defecto), y el ciclo de vida de sesiones en mod_php y FPM. El progreso de subida de sesión (`session.upload_progress`, activado por defecto) es uno de los primeros consumidores de ese estado.
- Los errores fatales incluyen agotamiento de memoria y timeouts.
- El reportero demostró RCE contra una aplicación real en Apache con mod_php (PHP Foundation).
- Además de ejecutar código, estos fallos pueden **filtrar memoria del proceso**: contraseñas, tokens, llaves de API de otras peticiones (The Hacker News; Recorded Future).

### 2.3 Versiones afectadas y corregidas
- **Corregidas (21 oct 2026, 14:00 UTC aprox.): PHP 8.5.12, 8.4.27, 8.3.36 y 8.2.35.** Todo lo anterior en esas ramas está afectado.
- Ramas antiguas: Google Cloud dice "todas las versiones desde 5.4 hasta 8.5.11"; otras fuentes solo listan 8.2–8.5. El alcance exacto en versiones viejas **no está confirmado de forma uniforme**, pero sin soporte no hay que asumir que están a salvo.
- PHP 8.1 y anteriores no reciben actualizaciones regulares. Existen *backports* limitados del código fuente para 7.4, 8.0 y 8.1 en GitHub (ramas `PHP-7.4/8.0/8.1-CVE-2026-109618-109619`), según Rapid7. La recomendación general es migrar a 8.2 o superior.
- Ojo: Debian/Ubuntu/RHEL suelen aplicar el parche **sin cambiar el número de versión visible**; hay que revisar el changelog del paquete buscando los CVE.
- Discrepancia menor de fecha: la PHP Foundation dice 21 de octubre; el ChangeLog de php.net muestra "22 Oct 2026" para 8.5.12.

### 2.4 ¿Se está explotando?
Estado al 22 de octubre de 2026:
- **Intentos de explotación: sí.** watchTowr reporta explotación en sus honeypots desde el 21 de octubre; Cloudflare reporta ataques tempranos (vía Tanium/Tenable); Patchstack ve sobre todo sondeos.
- **Compromisos confirmados: no hay confirmación pública.** Rapid7: "no hemos observado explotación in-the-wild, aunque hay múltiples reportes de intentos"; CISA (22 oct) dice no haberla observado aún. No hay indicadores de compromiso (IoC) públicos.
- **Exploits públicos (PoC):** hay varios en GitHub, pero según Rapid7 cada uno funciona solo para combinaciones concretas de sistema, versión y servidor web, y ninguno parece fiable en general. Wiz demostró RCE sin autenticación contra WordPress, Drupal y Joomla (no público).
- **CISA KEV:** al 21 oct 14:04 UTC **no figuraba** (Tanium, watchTowr). No pude confirmar cambios posteriores. CISA sí emitió guía urgente: parchear de inmediato y, si se usa PHP 8.1 o anterior sin poder actualizar, **desconectar** esos sistemas.

### 2.5 Cronología (UTC)
- 2024: una auditoría externa de PHP detecta los primeros indicios del problema de OOM, sin ruta de ejecución de código.
- 11 ago 2026: Calif y OpenAI (Codex Security) reportan por separado una RCE con la misma causa raíz. 24 ago: Wiz reporta (Wiz la había descubierto el 19 ago y confirmado contra Drupal y WordPress).
- 20 oct: PHP preanuncia un lanzamiento fuera de ciclo. Se filtran los CVE con fecha y CVSS erróneos; Calif publica por error un video con una PoC funcionando.
- 21 oct, madrugada: Cloudflare activa reglas WAF por defecto; Chainguard publica imágenes parcheadas antes de la hora coordinada.
- 21 oct, ~14:00: se publican 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35. Poco después, watchTowr reporta intentos activos.
- 22 oct: CISA urge parchear. Algunas organizaciones (p. ej. BambooHR, sitios del gobierno neerlandés) apagaron servicios de forma preventiva.

### 2.6 Exposición
- Modat: ~4.38 millones de servicios PHP en ~1.89 millones de hosts; ~79 % de los que muestran versión están en ramas sin soporte.
- VirusTotal: ~5.1 millones de IPs con PHP; de las ~1.1 millones que muestran versión, ~758 mil usan ramas EOL (5.4–8.1).
- Son conteos de exposición, no de servidores comprometidos ni confirmadamente vulnerables; los métodos difieren.

---

## 3. ¿A quién afecta?
- A cualquiera con un servidor que ejecute PHP sin parchear: hosting compartido, VPS, contenedores Docker, WordPress/Drupal/Joomla/Laravel.
- **Mayor riesgo:** Apache con mod_php, versiones sin soporte (7.x, 8.0, 8.1) y servidores expuestos que aceptan subidas de archivos.
- **Importante:** actualizar WordPress o los plugins **no** corrige esto. El fallo está en el intérprete PHP; lo corrige tu proveedor de hosting, tu paquete del sistema o tu imagen de contenedor.
- Las aplicaciones en la nube con PHP gestionado (p. ej. App Engine Standard 8.2+) se parchearon solas; Cloud Run, GKE y contenedores propios requieren reconstruir y redesplegar.

## 4. ¿Qué hacer?
1. **Comprobar la versión de PHP** (panel del hosting o `php -v` / página de diagnóstico interna, nunca pública).
2. **Actualizar** a 8.5.12, 8.4.27, 8.3.36 u 8.2.35 (o el paquete de tu distro que mencione los CVE) y **reiniciar** todos los procesos PHP (FPM, Apache).
3. Si estás en 8.1 o anterior: planear migración a 8.2+ ya; mientras tanto, CISA recomienda sacarlo de línea si no se puede proteger.
4. **Mitigaciones temporales** (no sustituyen el parche):
   - `session.upload_progress.enabled=0` a nivel servidor/pool (no vale `ini_set()` ni `.user.ini`) y reiniciar.
   - En PHP 8.5: `fatal_error_backtraces=0` a nivel servidor.
   - Limitar tamaño de petición en el servidor web/proxy; `post_max_size` bajo (8M si no hay subidas, 32M si las hay); bloquear multipart si la app no lo usa.
   - No usar `RLIMIT_AS`/`RLIMIT_DATA`.
   - Reglas WAF (Cloudflare las activó por defecto; Google Cloud Armor tiene reglas gestionadas).
   - Ocultar errores (`display_errors`, `@`) **no** protege.
5. Si estuviste expuesto: revisar logs de peticiones multipart anómalas y errores fatales, y considerar rotar secretos (contraseñas, llaves de API), ya que los fallos pueden filtrar memoria.
6. Después de parchear, revisar `memory_limit` y `post_max_size`: el nuevo límite estricto de memoria termina el proceso.

## 5. Lo que NO está confirmado
- Asignador oficial del CVSS y CWE (NVD no consultable en esta investigación).
- Inclusión en CISA KEV posterior al 21 de octubre.
- Compromisos reales confirmados (solo intentos y sondeos).
- Alcance exacto en PHP 5.x/7.x (fuentes difieren).
- RCE completa en PHP-FPM para CVE-2026-109618 (Foundation vs. Rapid7).

---

## Fuentes
- PHP — aviso de seguridad oficial (archivo 2026): https://www.php.net/archive/2026.php
- PHP Foundation — Today's PHP Security Release (21 oct 2026): https://thephp.foundation/blog/2026/10/21/todays-php-security-release-and-how-were-strengthening-php-security/
- PHP 8 ChangeLog: https://www.php.net/ChangeLog-8.php
- Aviso GHSA-w8hw-w9fx-j79w: https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w
- Aviso GHSA-6wmf-4rv5-p3rp: https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp
- Rapid7 ETR: https://www.rapid7.com/blog/post/etr-cve-2026-109618-and-cve-2026-109619-critical-unauthenticated-remote-code-execution-in-php/
- watchTowr FAQ: https://watchtowr.com/intelligence/php-cve-2026-109618-faq/
- The Hacker News: https://thehackernews.com/2026/10/php-issues-emergency-patches-for-two.html
- Google Cloud: https://cloud.google.com/blog/products/identity-security/responding-to-core-php-vulnerabilities-cve-2026-109618-cve-2026-109619
- Recorded Future: https://www.recordedfuture.com/blog/php2shell-vulnerability-exploitation
- Tanium: https://www.tanium.com/blog/php2shell-responding-to-cve-2026-109618-and-cve-2026-109619
- CISA (vía MBT Magazine): https://www.mbtmag.com/cybersecurity/news/22976990/cisa-offers-php-vulnerability-guidance
- Catálogo CISA KEV: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2026-109618 · https://nvd.nist.gov/vuln/detail/CVE-2026-109619
- W3Techs, uso de PHP: https://w3techs.com/technologies/details/pl-php · https://w3techs.com/technologies/details/pl-php/8
