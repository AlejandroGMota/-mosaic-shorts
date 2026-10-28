/* Shared drawing helpers for the R series (Internet y redes). Load after base.js.
 * Everything is static SVG built once; animation stays in each Short's seek-driven update.
 * Icons are drawn centred on (x, y) inside a <g> that is returned, so callers can move or fade it. */
(function () {
  "use strict";
  const { el } = Mosaic;
  const C = { ink: "#1d1d1b", ink2: "#4a4843", muted: "#827e74", line: "#d6d1c5", paper: "#f3f0e9", paper2: "#e9e5dc", card: "#faf8f3",
    blue: "#2f5e8e", fuchsia: "#b3386b", mint: "#3a9a80", amber: "#c98a1b" };

  /** Deterministic pseudo-random in [0, 1). */
  const rnd = (i) => { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };

  function group(parent, x, y, s) {
    return el("g", { transform: `translate(${x} ${y}) scale(${s || 1})` }, parent);
  }
  function place(node, x, y, s) {
    node.setAttribute("transform", `translate(${(+x).toFixed(1)} ${(+y).toFixed(1)}) scale(${s === undefined ? 1 : s})`);
  }
  function op(node, v) { node.setAttribute("opacity", String(Math.max(0, Math.min(1, v)))); }

  /** Phone, 110 x 200 at s = 1. */
  function phone(parent, x, y, s, color) {
    const g = group(parent, x, y, s);
    el("rect", { x: -55, y: -100, width: 110, height: 200, rx: 18, fill: C.card, stroke: color || C.ink, "stroke-width": 6 }, g);
    el("rect", { x: -43, y: -80, width: 86, height: 152, rx: 6, fill: C.paper2 }, g);
    el("line", { x1: -14, y1: 86, x2: 14, y2: 86, stroke: color || C.ink, "stroke-width": 5, "stroke-linecap": "round" }, g);
    return g;
  }

  /** Router: a disc with four arrows (the usual network-diagram symbol). r = 34 at s = 1. */
  function router(parent, x, y, s, color) {
    const g = group(parent, x, y, s);
    const c = color || C.blue;
    el("circle", { r: 34, fill: C.card, stroke: c, "stroke-width": 5 }, g);
    for (let k = 0; k < 4; k++) {
      const a = (k * Math.PI) / 2 + Math.PI / 4;
      const ux = Math.cos(a), uy = Math.sin(a);
      const inward = k % 2 === 0;
      const p0 = inward ? 24 : 7, p1 = inward ? 9 : 22;
      el("line", { x1: ux * p0, y1: uy * p0, x2: ux * p1, y2: uy * p1, stroke: c, "stroke-width": 4, "stroke-linecap": "round" }, g);
      const tip = p1, back = inward ? tip + 7 : tip - 7;
      el("polyline", { points: `${ux * back - uy * 5},${uy * back + ux * 5} ${ux * tip},${uy * tip} ${ux * back + uy * 5},${uy * back - ux * 5}`, fill: "none", stroke: c, "stroke-width": 4, "stroke-linecap": "round", "stroke-linejoin": "round" }, g);
    }
    return g;
  }

  /** Cell tower: lattice mast with two signal arcs. About 70 x 130 at s = 1, base at y + 65. */
  function tower(parent, x, y, s, color) {
    const g = group(parent, x, y, s);
    const c = color || C.ink2;
    el("polyline", { points: "-30,65 0,-45 30,65", fill: "none", stroke: c, "stroke-width": 5, "stroke-linejoin": "round" }, g);
    el("line", { x1: -18, y1: 20, x2: 18, y2: 20, stroke: c, "stroke-width": 4 }, g);
    el("line", { x1: -24, y1: 42, x2: 24, y2: 42, stroke: c, "stroke-width": 4 }, g);
    el("circle", { cx: 0, cy: -50, r: 7, fill: c }, g);
    for (const r of [22, 38]) {
      el("path", { d: `M${-r * 0.7} ${-50 - r * 0.7} A${r} ${r} 0 0 0 ${-r * 0.7} ${-50 + r * 0.7}`, fill: "none", stroke: c, "stroke-width": 4, "stroke-linecap": "round" }, g);
      el("path", { d: `M${r * 0.7} ${-50 - r * 0.7} A${r} ${r} 0 0 1 ${r * 0.7} ${-50 + r * 0.7}`, fill: "none", stroke: c, "stroke-width": 4, "stroke-linecap": "round" }, g);
    }
    return g;
  }

  /** Building with a grid of windows, w x h at s = 1, centred. */
  function building(parent, x, y, w, h, color, s) {
    const g = group(parent, x, y, s);
    const c = color || C.ink2;
    el("rect", { x: -w / 2, y: -h / 2, width: w, height: h, rx: 6, fill: C.card, stroke: c, "stroke-width": 5 }, g);
    const cols = Math.max(2, Math.round(w / 34)), rows = Math.max(2, Math.round(h / 40));
    const gw = (w - 24) / cols, gh = (h - 40) / rows;
    for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
      el("rect", { x: -w / 2 + 12 + i * gw + 4, y: -h / 2 + 12 + j * gh + 4, width: gw - 8, height: gh - 10, rx: 2, fill: c, opacity: 0.25 }, g);
    }
    return g;
  }

  /** Padlock, 60 x 70 at s = 1. */
  function lock(parent, x, y, s, color, open) {
    const g = group(parent, x, y, s);
    const c = color || C.mint;
    el("path", { d: open ? "M-18 -6 V-26 A18 18 0 0 1 18 -26 V-34" : "M-18 -6 V-26 A18 18 0 0 1 18 -26 V-6", fill: "none", stroke: c, "stroke-width": 8, "stroke-linecap": "round" }, g);
    el("rect", { x: -30, y: -8, width: 60, height: 46, rx: 8, fill: c }, g);
    el("circle", { cx: 0, cy: 12, r: 6, fill: C.card }, g);
    el("rect", { x: -2.5, y: 14, width: 5, height: 12, rx: 2, fill: C.card }, g);
    return g;
  }

  /** Packet: a data block with a coloured header strip ("etiqueta"). 76 x 48 at s = 1. */
  function packet(parent, x, y, s, color, text) {
    const g = group(parent, x, y, s);
    const c = color || C.blue;
    el("rect", { x: -38, y: -24, width: 76, height: 48, rx: 6, fill: C.card, stroke: c, "stroke-width": 4 }, g);
    el("rect", { x: -38, y: -24, width: 24, height: 48, rx: 6, fill: c }, g);
    if (text !== undefined) el("text", { x: 12, y: 11, "text-anchor": "middle", "font-size": 30, "font-weight": 700, fill: c, text }, g);
    return g;
  }

  /** Server rack with disks / blades. 120 x 200 at s = 1. */
  function rack(parent, x, y, s, color) {
    const g = group(parent, x, y, s);
    const c = color || C.ink2;
    el("rect", { x: -60, y: -100, width: 120, height: 200, rx: 8, fill: C.card, stroke: c, "stroke-width": 5 }, g);
    for (let j = 0; j < 6; j++) {
      el("rect", { x: -46, y: -86 + j * 30, width: 92, height: 22, rx: 3, fill: C.paper2, stroke: c, "stroke-width": 2 }, g);
      el("circle", { cx: 34, cy: -75 + j * 30, r: 4, fill: C.mint }, g);
    }
    return g;
  }

  /** Simple cloud outline, about 260 x 150 at s = 1. */
  function cloud(parent, x, y, s, color) {
    const g = group(parent, x, y, s);
    el("path", { d: "M-100 50 A50 50 0 0 1 -80 -36 A70 70 0 0 1 40 -56 A55 55 0 0 1 120 10 A40 40 0 0 1 100 50 Z", fill: C.card, stroke: color || C.blue, "stroke-width": 6, "stroke-linejoin": "round" }, g);
    return g;
  }

  /** Point at fraction p (0..1) of the length of a polyline [[x, y], ...]. */
  function along(pts, p) {
    const seg = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) {
      const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      seg.push(d); total += d;
    }
    let d = Math.max(0, Math.min(1, p)) * total;
    for (let i = 0; i < seg.length; i++) {
      if (d <= seg[i] || i === seg.length - 1) {
        const q = seg[i] ? Math.min(1, d / seg[i]) : 0;
        return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * q, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * q];
      }
      d -= seg[i];
    }
    return pts[pts.length - 1];
  }
  const ptsStr = (pts) => pts.map((p) => p[0].toFixed(1) + "," + p[1].toFixed(1)).join(" ");

  /** Thousands with a thin space (written form for numbers on screen): 1000000 -> "1 000 000". */
  const thousands = (n) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " ");

  /** Arrow head marker-free line with a triangle at (x2, y2). Returns a <g>. */
  function arrow(parent, x1, y1, x2, y2, color, w) {
    const g = el("g", {}, parent);
    const c = color || C.ink2, sw = w || 5;
    const a = Math.atan2(y2 - y1, x2 - x1), L = 8 + sw * 2.2;
    const bx = x2 - Math.cos(a) * L, by = y2 - Math.sin(a) * L;
    el("line", { x1, y1, x2: bx, y2: by, stroke: c, "stroke-width": sw, "stroke-linecap": "round" }, g);
    el("polygon", { points: `${x2},${y2} ${bx - Math.sin(a) * L * 0.55},${by + Math.cos(a) * L * 0.55} ${bx + Math.sin(a) * L * 0.55},${by - Math.cos(a) * L * 0.55}`, fill: c }, g);
    return g;
  }

  window.Redes = { C, rnd, group, place, op, phone, router, tower, building, lock, packet, rack, cloud, along, ptsStr, thousands, arrow };
})();
