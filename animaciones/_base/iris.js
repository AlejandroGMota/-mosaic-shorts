/* Lens iris (aperture diaphragm) drawing, shared by the aperture Shorts.
 * Load after base.js:  <script src="../_base/iris.js"></script>
 *
 * Geometry: n blades whose inner edges form a regular polygon of circumradius r. Blade k is
 * bounded by side k (V_k -> V_k+1), the extension of that side beyond V_k+1 up to the housing,
 * the housing arc, and the extension of side k-1 beyond V_k. The blades tile the housing.
 * Optics helpers: with the focal length fixed, diameter ∝ 1/N and light ∝ area ∝ 1/N².
 */
(function () {
  "use strict";
  const { el } = Mosaic;
  let clipCount = 0;

  function rayToCircle(p, u, R) {
    const b = p[0] * u[0] + p[1] * u[1];
    const c = p[0] * p[0] + p[1] * p[1] - R * R;
    const s = -b + Math.sqrt(Math.max(0, b * b - c));
    return [p[0] + u[0] * s, p[1] + u[1] * s];
  }

  function paths(n, r, rot, R) {
    const V = [];
    for (let k = 0; k < n; k++) {
      const a = rot + (k * 2 * Math.PI) / n;
      V.push([r * Math.cos(a), r * Math.sin(a)]);
    }
    const U = V.map((v, k) => {
      const w = V[(k + 1) % n];
      const dx = w[0] - v[0], dy = w[1] - v[1], l = Math.hypot(dx, dy);
      return [dx / l, dy / l];
    });
    const blades = [];
    for (let k = 0; k < n; k++) {
      const v0 = V[k], v1 = V[(k + 1) % n];
      const front = rayToCircle(v1, U[k], R);
      const back = rayToCircle(v0, U[(k - 1 + n) % n], R);
      const a1 = Math.atan2(front[1], front[0]);
      const a0 = Math.atan2(back[1], back[0]);
      let d = a0 - a1;
      while (d > 0) d -= 2 * Math.PI;
      while (d <= -2 * Math.PI) d += 2 * Math.PI;
      const pts = [v0, v1, front];
      const steps = Math.max(2, Math.ceil(Math.abs(d) / 0.08));
      for (let i = 1; i < steps; i++) {
        const a = a1 + (d * i) / steps;
        pts.push([R * Math.cos(a), R * Math.sin(a)]);
      }
      pts.push(back);
      blades.push("M" + pts.map((p) => p[0].toFixed(2) + " " + p[1].toFixed(2)).join(" L") + " Z");
    }
    const poly = V.map((p) => p[0].toFixed(2) + "," + p[1].toFixed(2)).join(" ");
    return { blades, poly, V };
  }

  /** Front view of a lens: barrel, rotor ring with ticks, n blades and the light behind them. */
  function make(parent, { n = 6, R = 300, ring = 40, rotorW = 30, ticks = 36, light = "#f4dc93" } = {}) {
    const g = el("g", {}, parent);
    el("circle", { r: R + ring + rotorW + 2, fill: "#d9d5cc" }, g);
    const rotor = el("circle", { r: R + ring + rotorW / 2, fill: "none", stroke: "#8f8a7f", "stroke-width": rotorW }, g);
    const tickG = el("g", {}, g);
    for (let i = 0; i < ticks; i++) {
      const a = (i * 2 * Math.PI) / ticks;
      const r0 = R + ring + 4, r1 = R + ring + rotorW - 4;
      el("line", { x1: r0 * Math.cos(a), y1: r0 * Math.sin(a), x2: r1 * Math.cos(a), y2: r1 * Math.sin(a),
        stroke: "#5c584f", "stroke-width": 3, "stroke-linecap": "round" }, tickG);
    }
    el("circle", { r: R + ring / 2, fill: "none", stroke: "#2e2d2a", "stroke-width": ring }, g);
    const glow = el("circle", { r: R + 1, fill: light }, g);
    const clipId = "iris-clip-" + ++clipCount;
    el("circle", { r: R + 1 }, el("clipPath", { id: clipId }, el("defs", {}, g)));
    const bladeG = el("g", { "clip-path": `url(#${clipId})` }, g);
    const blades = [];
    for (let k = 0; k < n; k++) {
      blades.push(el("path", { fill: k % 2 ? "#3f3d38" : "#4a4842", stroke: "#77736a", "stroke-width": 2, "stroke-linejoin": "round" }, bladeG));
    }
    el("circle", { r: R + 1, fill: "none", stroke: "#2e2d2a", "stroke-width": 4 }, g);
    const poly = el("polygon", { fill: "none", stroke: "#3a9a80", "stroke-width": 6, "stroke-linejoin": "round", opacity: 0 }, g);
    const rMax = 0.86 * R;
    return {
      g, rotor, tickG, blades, poly, glow, n, R, rMax,
      /** Radius of the opening for f-number N, with f/1.48 = fully open. */
      rOf: (N) => (rMax * 1.48) / N,
      /** Draw with opening radius r; the polygon and the rotor turn a little as it closes. */
      draw(r) {
        const c = 1 - r / rMax;
        const p = paths(n, r, -Math.PI / 2 + c * 0.9, R + 2);
        p.blades.forEach((d, k) => blades[k].setAttribute("d", d));
        poly.setAttribute("points", p.poly);
        tickG.setAttribute("transform", `rotate(${(c * -38).toFixed(3)})`);
        return p;
      },
    };
  }

  /** Light that gets in relative to f/4: (4 / N)². */
  const lightVs = (N, ref = 4) => Math.pow(ref / N, 2);

  Mosaic.iris = { paths, make, lightVs };
})();
