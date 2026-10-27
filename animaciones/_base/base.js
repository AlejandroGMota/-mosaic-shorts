/* Mosaic Shorts base runtime.
 *
 * Contract with pipeline/render.mjs:
 *   - window.TRANSCRIPT  transcript.json (schema mosaic-transcript/1), injected before load
 *   - window.RENDER      {duration, outro, total, fps, width, height, preview}, injected before load
 *   - window.seek(t)     t in seconds. Pure: the same t always draws the same frame. No
 *                        requestAnimationFrame, timers or CSS transitions are involved.
 *   - window.MOSAIC_READY = true once the page can be seeked; MOSAIC_WARNINGS lists problems.
 *
 * A Short calls Mosaic.short({...}) once:
 *   Mosaic.short({
 *     kicker: "Serie A · Cámara",
 *     title: "¿Cómo cabe ...?",
 *     script: "narration text from the guion",          // fallback timing when a word is missing
 *     anchors: {                                         // in narration order
 *       rotor: "rotor",                                  // first match after the previous anchor
 *       f148: { q: Mosaic.fnum("1.48"), after: "pasos" },// alternatives + explicit "after"
 *     },
 *     scenes: [
 *       { el: "#iris", from: "dentro", to: "profesional+0.5", fade: 0.5,
 *         update(t, s, A) { ... } },                      // s = {from, to, local, p, A}
 *     ],
 *     build() { ... },                                   // optional, once: create DOM/SVG
 *     update(t, A) { ... },                              // optional, every frame (pure)
 *   });
 * Times in scenes accept a number (s), "anchor", "anchor.end", "anchor+0.3", "anchor.end-0.2",
 * "start" (0) and "end" (end of the audio, where the 2 s outro starts).
 */
(function () {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const DIGITS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"];
  const warnings = [];
  window.MOSAIC_WARNINGS = warnings;

  // ------------------------------------------------------------------ math & easing
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const ease = {
    linear: (p) => p,
    in: (p) => p * p * p,
    out: (p) => 1 - Math.pow(1 - p, 3),
    inOut: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    inOutSine: (p) => -(Math.cos(Math.PI * p) - 1) / 2,
  };
  /** 0..1 progress of t between a and b, eased. */
  const ramp = (t, a, b, e = ease.inOut) => (b <= a ? (t >= b ? 1 : 0) : e(clamp((t - a) / (b - a))));
  /** Piecewise interpolation: keys = [[t0, v0], [t1, v1], ...] (sorted by time). */
  function keys(t, ks, e = ease.inOut) {
    if (t <= ks[0][0]) return ks[0][1];
    for (let i = 1; i < ks.length; i++) {
      if (t <= ks[i][0]) return lerp(ks[i - 1][1], ks[i][1], ramp(t, ks[i - 1][0], ks[i][0], ks[i][2] || e));
    }
    return ks[ks.length - 1][1];
  }

  // ------------------------------------------------------------------ text matching
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]/g, "");
  }

  /** How an aperture is said and how Whisper may write it: fnum("1.48") -> alternatives. */
  function fnum(n) {
    const [a, b] = String(n).split(".");
    const spoken = [DIGITS[+a]].concat(b ? ["punto"].concat(b.split("").map((d) => DIGITS[+d])) : []).join(" ");
    return [spoken, "efe " + spoken, String(n), "f/" + n, "f" + n, String(n).replace(".", ",")];
  }

  /** First match of any alternative in a list of normalized words, starting at index `from`. */
  function findIn(normWords, alts, from) {
    let best = null;
    for (const alt of [].concat(alts)) {
      const q = norm(alt);
      if (!q) continue;
      for (let i = from; i < normWords.length; i++) {
        if (best && i >= best.i) break;
        let joined = "";
        for (let k = i; k < Math.min(normWords.length, i + 8); k++) {
          joined += normWords[k];
          if (joined === q) {
            best = { i, k };
            break;
          }
          if (joined.length >= q.length || !q.startsWith(joined)) break;
        }
      }
    }
    return best;
  }

  function resolveAnchors(defs, transcript, script, duration) {
    const words = (transcript && transcript.words) || [];
    const tNorm = words.map((w) => w.norm || norm(w.text));
    const sNorm = String(script || "").split(/\s+/).map(norm).filter(Boolean);
    const names = Object.keys(defs || {});
    const out = {};
    const list = [];
    let prev = null;
    for (const name of names) {
      const d = typeof defs[name] === "object" && !Array.isArray(defs[name]) ? defs[name] : { q: defs[name] };
      const after = d.after === undefined ? prev : d.after;
      const ref = after ? out[after] : null;
      if (after && !ref) warnings.push(`ancla "${name}": "after" apunta a "${after}", que no existe (o va después)`);
      const sm = findIn(sNorm, d.q, ref && ref.si !== undefined ? ref.si : 0);
      const tm = words.length ? findIn(tNorm, d.q, ref && ref.wi !== undefined ? ref.wi : 0) : null;
      const a = { name, found: !!tm, si: sm ? sm.i : undefined, sk: sm ? sm.k : undefined };
      if (tm) {
        a.wi = tm.i;
        a.start = words[tm.i].start;
        a.end = words[tm.k].end;
      } else if (ref && ref.wi !== undefined) {
        a.wi = ref.wi;
      }
      if (!sm && !tm) warnings.push(`ancla "${name}": no aparece ni en TRANSCRIPT ni en el guion (${[].concat(d.q).join(" | ")})`);
      out[name] = a;
      list.push(a);
      prev = name;
    }
    // Missing words: interpolate by guion position between the nearest anchors that were found.
    const total = Math.max(sNorm.length, 1);
    list.forEach((a, idx) => {
      if (a.found) return;
      let lo = { t: 0, s: 0 };
      let hi = { t: duration, s: total };
      for (let j = idx - 1; j >= 0; j--) if (list[j].found && list[j].si !== undefined) { lo = { t: list[j].start, s: list[j].si }; break; }
      for (let j = idx + 1; j < list.length; j++) if (list[j].found && list[j].si !== undefined) { hi = { t: list[j].start, s: list[j].si }; break; }
      if (a.si === undefined) {
        a.start = idx > 0 ? list[idx - 1].end + 0.3 : 0;
        a.end = a.start + 0.4;
        return;
      }
      const p = hi.s > lo.s ? (a.si - lo.s) / (hi.s - lo.s) : 0;
      a.start = lerp(lo.t, hi.t, clamp(p));
      const pe = hi.s > lo.s ? (a.sk + 1 - lo.s) / (hi.s - lo.s) : 0;
      a.end = Math.max(a.start + 0.2, lerp(lo.t, hi.t, clamp(pe)));
      if (words.length) warnings.push(`ancla "${a.name}": no está en TRANSCRIPT; estimada en ${a.start.toFixed(2)} s`);
    });
    return out;
  }

  // ------------------------------------------------------------------ DOM helpers
  function el(tag, attrs, parent) {
    const svgTags = /^(svg|g|path|circle|rect|line|polyline|polygon|ellipse|text|tspan|defs|clipPath|mask|linearGradient|radialGradient|stop|use)$/;
    const node = svgTags.test(tag) ? document.createElementNS(SVG_NS, tag) : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    }
    if (parent) parent.appendChild(node);
    return node;
  }
  const $ = (sel) => (typeof sel === "string" ? document.querySelector(sel) : sel);

  // ------------------------------------------------------------------ runtime
  let spec = null;
  let A = null;
  let scenes = [];
  let total = 0;
  let stage, content, outroEl;

  function timeOf(ref) {
    if (typeof ref === "number") return ref;
    if (ref === "start") return 0;
    if (ref === "end") return A.duration;
    const m = /^([A-Za-z0-9_]+)(\.end)?\s*([+-]\s*\d+(?:\.\d+)?)?$/.exec(String(ref));
    if (!m || !A[m[1]] || typeof A[m[1]] !== "object") {
      warnings.push(`tiempo inválido: "${ref}"`);
      return 0;
    }
    const base = m[2] ? A[m[1]].end : A[m[1]].start;
    return base + (m[3] ? parseFloat(m[3].replace(/\s/g, "")) : 0);
  }

  function fit() {
    const s = Math.min(window.innerWidth / 1080, window.innerHeight / 1920);
    stage.style.transform = `translate(${(window.innerWidth - 1080 * s) / 2}px, ${(window.innerHeight - 1920 * s) / 2}px) scale(${s})`;
  }

  function buildChrome() {
    stage = document.getElementById("stage");
    if (!stage) throw new Error('falta <div id="stage">');
    content = document.getElementById("content") || stage;
    if (spec.title && !stage.querySelector(".m-header")) {
      const h = el("div", { class: "m-header" });
      if (spec.kicker) el("div", { class: "m-kicker", text: spec.kicker }, h);
      el("h1", { class: "m-title", text: spec.title }, h);
      content.appendChild(h);
    }
    outroEl = el("div", { class: "mosaic-outro" }, stage);
    const mark = el("div", { class: "mark" }, outroEl);
    for (let i = 0; i < 9; i++) el("i", {}, mark);
    el("div", { class: "name", text: "Mosaic" }, outroEl);
    el("div", { class: "cta", text: "Video completo en el canal" }, outroEl);
  }

  function init() {
    warnings.length = 0;
    const T = window.TRANSCRIPT || null;
    const R = window.RENDER || null;
    const scriptWords = String(spec.script || "").split(/\s+/).filter(Boolean).length;
    const duration = (R && R.duration) || (T && T.duration) || Math.max(10, scriptWords / 2.6 + 1);
    const outro = R && R.outro !== undefined ? R.outro : 2;
    total = duration + outro;
    if (!T) warnings.push("sin TRANSCRIPT: tiempos estimados desde el guion");
    A = resolveAnchors(spec.anchors, T, spec.script, duration);
    A.duration = duration;
    A.total = total;
    A.t = timeOf;
    scenes = (spec.scenes || []).map((s, i) => {
      const node = $(s.el);
      if (!node) warnings.push(`escena ${i}: no existe ${s.el}`);
      const from = timeOf(s.from === undefined ? 0 : s.from);
      const to = s.to === undefined ? duration : timeOf(s.to);
      if (to <= from) warnings.push(`escena ${s.el}: termina (${to.toFixed(2)}) antes de empezar (${from.toFixed(2)})`);
      return Object.assign({}, s, { node, from, to, fadeIn: s.fadeIn ?? s.fade ?? 0.45, fadeOut: s.fadeOut ?? s.fade ?? 0.45 });
    });
  }

  function seek(t) {
    t = clamp(Number(t) || 0, 0, total);
    const outroP = ramp(t, A.duration, A.duration + 0.35, ease.inOut);
    content.style.opacity = String(1 - outroP);
    outroEl.style.opacity = String(outroP);
    outroEl.style.visibility = outroP > 0 ? "visible" : "hidden";
    const header = stage.querySelector(".m-header");
    if (header) {
      const h = ramp(t, 0, 0.5, ease.out);
      header.style.opacity = String(h);
      header.style.transform = `translateY(${(1 - h) * 16}px)`;
    }
    for (const s of scenes) {
      if (!s.node) continue;
      const pin = s.fadeIn > 0 ? ramp(t, s.from, s.from + s.fadeIn, ease.out) : t >= s.from ? 1 : 0;
      const pout = s.fadeOut > 0 ? ramp(t, s.to - s.fadeOut, s.to, ease.inOut) : t >= s.to ? 1 : 0;
      const o = pin * (1 - pout);
      s.node.style.opacity = String(o);
      s.node.style.visibility = o > 0.001 ? "visible" : "hidden";
      const rise = s.rise ?? 18;
      if (rise) s.node.style.transform = `translateY(${(1 - pin) * rise}px)`;
      if (o > 0.001 && s.update) {
        const local = t - s.from;
        s.update(t, { from: s.from, to: s.to, local, p: clamp(local / Math.max(1e-6, s.to - s.from)), A }, A);
      }
    }
    if (spec.update) spec.update(t, A);
    window.MOSAIC_T = t;
  }

  // Manual preview in the browser (never used by the renderer).
  function devControls() {
    const bar = el("div", { id: "mosaic-dev" }, document.body);
    const play = el("button", { type: "button", text: "▶" }, bar);
    const range = el("input", { type: "range", min: "0", max: String(total), step: "0.04", value: "0" }, bar);
    const label = el("span", { text: "0.00 s" }, bar);
    const warn = el("span", { class: "warn" }, bar);
    el("span", { text: "· arrastra aquí transcript.json" }, bar);
    let playing = false;
    let t0 = 0;
    let wall = 0;
    const show = (t) => {
      seek(t);
      range.value = String(t);
      label.textContent = `${t.toFixed(2)} / ${total.toFixed(2)} s`;
      warn.textContent = warnings.length ? `⚠ ${warnings.length}: ${warnings[0]}` : "";
      warn.title = warnings.join("\n");
    };
    const tick = (now) => {
      if (!playing) return;
      const t = t0 + (now - wall) / 1000;
      if (t >= total) { playing = false; play.textContent = "▶"; show(total); return; }
      show(t);
      requestAnimationFrame(tick);
    };
    play.onclick = () => {
      playing = !playing;
      play.textContent = playing ? "❚❚" : "▶";
      if (playing) { t0 = Number(range.value) >= total ? 0 : Number(range.value); wall = performance.now(); requestAnimationFrame(tick); }
    };
    range.oninput = () => { playing = false; play.textContent = "▶"; show(Number(range.value)); };
    document.addEventListener("dragover", (e) => e.preventDefault());
    document.addEventListener("drop", async (e) => {
      e.preventDefault();
      const f = e.dataTransfer.files[0];
      if (!f) return;
      try {
        window.TRANSCRIPT = JSON.parse(await f.text());
        init();
        range.max = String(total);
        show(0);
      } catch (err) {
        warn.textContent = `transcript inválido: ${err.message}`;
      }
    });
    const q = new URLSearchParams(location.search).get("t");
    show(q ? Number(q) : 0);
    if (warnings.length) console.warn(warnings.join("\n"));
  }

  function short(s) {
    spec = s;
    const start = () => {
      buildChrome();
      if (spec.build) spec.build();
      init();
      fit();
      window.addEventListener("resize", fit);
      window.seek = seek;
      seek(0);
      const ready = () => {
        window.MOSAIC_READY = true;
        if (!window.RENDER) devControls();
      };
      (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(ready, ready);
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
  }

  window.Mosaic = { short, el, $, clamp, lerp, ease, ramp, keys, norm, fnum, findIn, resolveAnchors };
})();
