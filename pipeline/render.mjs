#!/usr/bin/env node
// Mosaic Shorts renderer: animaciones/<ID>/index.html + audio.wav -> MP4 (H.264 + AAC).
//
//   node render.mjs A2                 1080x1920, 25 fps -> audios/<guion>/final/<short>/A2.mp4
//   node render.mjs A2 --preview       540x960, 12 fps   -> .../A2-preview.mp4
//   node render.mjs A2 --capturas 2,10,20 [--solo-capturas]
//
// The page is driven frame by frame through window.seek(t). TRANSCRIPT and RENDER are injected
// with addInitScript because file:// pages cannot fetch the JSON. Subtitles are never burned in.
// Options for testing only: --browser chromium, --audio <wav>, --transcript <json>, --out <mp4>.
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const PIPELINE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.dirname(PIPELINE);

class RenderError extends Error {}

function parseToml(text) {
  const data = {};
  let section = data;
  for (const raw of text.split(/\r?\n/)) {
    let line = "";
    let quoted = false;
    for (const ch of raw) {
      if (ch === '"') quoted = !quoted;
      if (ch === "#" && !quoted) break;
      line += ch;
    }
    line = line.trim();
    if (!line) continue;
    const sec = line.match(/^\[(.+)\]$/);
    if (sec) {
      section = data[sec[1].trim()] ??= {};
      continue;
    }
    const eq = line.indexOf("=");
    if (eq < 0) throw new RenderError(`config.toml: línea inválida: ${raw}`);
    const key = line.slice(0, eq).trim();
    const value = line.slice(eq + 1).trim();
    if (value.startsWith('"')) section[key] = value.slice(1, -1);
    else if (value === "true" || value === "false") section[key] = value === "true";
    else section[key] = Number(value);
  }
  return data;
}

function expand(p) {
  return p.startsWith("~") ? path.join(process.env.HOME || "", p.slice(1)) : p;
}

function parseArgs(argv) {
  const opts = { preview: false, capturas: [], soloCapturas: false };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => {
      if (i + 1 >= argv.length) throw new RenderError(`${a} necesita un valor`);
      return argv[++i];
    };
    if (a === "--preview") opts.preview = true;
    else if (a === "--capturas") opts.capturas = next().split(",").filter(Boolean).map(Number);
    else if (a === "--solo-capturas") opts.soloCapturas = true;
    else if (a === "--browser") opts.browser = next();
    else if (a === "--audio") opts.audio = next();
    else if (a === "--transcript") opts.transcript = next();
    else if (a === "--out") opts.out = next();
    else if (a === "--guion") opts.guion = next();
    else if (a.startsWith("--")) throw new RenderError(`opción desconocida: ${a}`);
    else rest.push(a);
  }
  if (rest.length !== 1) throw new RenderError("uso: render.mjs <ID> [--preview] [--capturas 2,10]");
  if (opts.capturas.some((t) => !Number.isFinite(t) || t < 0)) throw new RenderError("--capturas: segundos inválidos");
  opts.id = rest[0].toUpperCase();
  return opts;
}

function locate(opts, cfg) {
  const paths = cfg.paths || {};
  const root = path.resolve(expand(process.env.SOCIALMEDIA_DIR || paths.socialmedia_dir || REPO));
  const guion = opts.guion || paths.guion;
  const audiosDir = path.resolve(root, expand(paths.audios_dir || "audios"), guion);
  const finalDir = path.join(audiosDir, "final");
  const prefix = opts.id.toLowerCase() + "-";
  const shortName = fs.existsSync(finalDir)
    ? fs.readdirSync(finalDir).filter((d) => d.startsWith(prefix)).sort()[0]
    : undefined;
  const shortDir = shortName ? path.join(finalDir, shortName) : undefined;
  const html = path.join(root, "animaciones", opts.id, "index.html");
  const transcript = opts.transcript || path.join(root, "shorts", opts.id, "transcript.json");
  const audio = opts.audio || (shortDir && path.join(shortDir, "audio.wav"));
  if (!fs.existsSync(html)) throw new RenderError(`no existe ${html}`);
  if (!fs.existsSync(transcript)) throw new RenderError(`no existe ${transcript} (corre: shorts audio ${opts.id})`);
  if (!audio || !fs.existsSync(audio)) {
    throw new RenderError(`no encuentro el audio.wav de ${opts.id} en ${finalDir} (corre: shorts audio ${opts.id})`);
  }
  const outDir = opts.out ? path.dirname(path.resolve(opts.out)) : shortDir || path.dirname(path.resolve(audio));
  const out = opts.out ? path.resolve(opts.out) : path.join(outDir, `${opts.id}${opts.preview ? "-preview" : ""}.mp4`);
  return { root, html, transcript, audio, out, outDir, shortName, audiosDir };
}

function probeDuration(file) {
  const out = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", file]);
  const d = Number(String(out).trim());
  if (!Number.isFinite(d) || d <= 0) throw new RenderError(`duración inválida de ${file}`);
  return d;
}

function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

// Never delete: an existing output goes to audios/<guion>/_descartadas/<short>/<timestamp>/.
function discard(file, loc) {
  if (!fs.existsSync(file)) return;
  const dest = path.join(loc.audiosDir, "_descartadas", loc.shortName || "render", stamp());
  fs.mkdirSync(dest, { recursive: true });
  fs.renameSync(file, path.join(dest, path.basename(file)));
  console.log(`  · versión anterior movida a ${dest}`);
}

function startFfmpeg({ fps, total, audio, out, video }) {
  const args = [
    "-hide_banner", "-loglevel", "error", "-y",
    "-f", "image2pipe", "-framerate", String(fps), "-c:v", "png", "-i", "-",
    "-i", audio,
    "-filter_complex", "[1:a]apad[a]",
    "-map", "0:v", "-map", "[a]", "-t", total.toFixed(3),
    "-c:v", "libx264", "-preset", video.x264_preset || "medium", "-crf", String(video.crf ?? 18),
    "-pix_fmt", "yuv420p", "-r", String(fps), "-profile:v", "high",
    "-c:a", "aac", "-b:a", video.audio_bitrate || "192k", "-ar", "48000",
    "-movflags", "+faststart", out,
  ];
  const proc = spawn("ffmpeg", args, { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((resolve, reject) => {
    proc.on("error", (e) => reject(new RenderError(`no pude iniciar ffmpeg: ${e.message}`)));
    proc.on("close", (code) => (code === 0 ? resolve() : reject(new RenderError(`ffmpeg terminó con código ${code}`))));
  });
  return { proc, done };
}

function writeFrame(stream, buf) {
  return new Promise((resolve, reject) => {
    const ok = stream.write(buf, (err) => (err ? reject(err) : null));
    if (ok) resolve();
    else stream.once("drain", resolve);
  });
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const cfg = parseToml(fs.readFileSync(path.join(PIPELINE, "config.toml"), "utf8"));
  const video = cfg.video || {};
  const loc = locate(opts, cfg);
  const width = opts.preview ? video.preview_width || 540 : video.width || 1080;
  const height = opts.preview ? video.preview_height || 960 : video.height || 1920;
  const fps = opts.preview ? video.preview_fps || 12 : video.fps || 25;
  const outro = video.outro_seconds ?? 2;
  const duration = probeDuration(loc.audio);
  const total = duration + outro;
  const frames = Math.ceil(total * fps);
  const transcript = JSON.parse(fs.readFileSync(loc.transcript, "utf8"));
  const render = { id: opts.id, duration, outro, total, fps, width, height, preview: opts.preview };

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    throw new RenderError(`falta Playwright: cd "${PIPELINE}" && npm install`);
  }
  const browserName = opts.browser || video.browser || "msedge";
  const launch = browserName === "chromium" ? {} : { channel: browserName };
  console.log(`▶ ${opts.id}: ${width}x${height} @ ${fps} fps · ${total.toFixed(2)} s (${duration.toFixed(2)} + ${outro} de cierre) · ${frames} fotogramas · ${browserName}`);
  let browser;
  try {
    browser = await chromium.launch(launch);
  } catch (e) {
    throw new RenderError(`no pude abrir ${browserName}: ${e.message.split("\n")[0]}`);
  }
  try {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    const pageErrors = [];
    page.on("pageerror", (e) => pageErrors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error" || m.type() === "warning") console.log(`  [página] ${m.text()}`);
    });
    await page.addInitScript({
      content: `window.TRANSCRIPT = ${JSON.stringify(transcript)}; window.RENDER = ${JSON.stringify(render)};`,
    });
    await page.goto(pathToFileURL(loc.html).href, { waitUntil: "load" });
    await page.waitForFunction(() => window.MOSAIC_READY === true, null, { timeout: 15000 }).catch(() => {
      throw new RenderError(`la animación no llamó a Mosaic.short() (¿error de JS?) ${pageErrors.join(" | ")}`);
    });
    if (pageErrors.length) throw new RenderError(`errores de JS en la página: ${pageErrors.join(" | ")}`);
    const warnings = await page.evaluate(() => window.MOSAIC_WARNINGS || []);
    for (const w of warnings) console.log(`  ⚠ ${w}`);

    const shot = async (t) => {
      await page.evaluate((tt) => window.seek(tt), t);
      return page.screenshot({ type: "png", animations: "disabled", caret: "hide" });
    };

    if (opts.capturas.length) {
      const dir = path.join(loc.outDir, opts.preview ? "capturas-preview" : "capturas");
      fs.mkdirSync(dir, { recursive: true });
      for (const t of opts.capturas) {
        const file = path.join(dir, `${opts.id}-${t.toFixed(2).padStart(6, "0")}s.png`);
        discard(file, loc);
        fs.writeFileSync(file, await shot(Math.min(t, total)));
      }
      console.log(`  · ${opts.capturas.length} capturas en ${dir}`);
    }
    if (opts.soloCapturas) return;

    discard(loc.out, loc);
    const ff = startFfmpeg({ fps, total, audio: loc.audio, out: loc.out, video });
    const started = Date.now();
    let failed = null;
    ff.done.catch((e) => (failed = e));
    for (let i = 0; i < frames; i++) {
      if (failed) throw failed;
      await writeFrame(ff.proc.stdin, await shot(i / fps));
      if (i % (fps * 5) === 0 || i === frames - 1) {
        const pct = Math.round(((i + 1) / frames) * 100);
        const secs = (Date.now() - started) / 1000;
        process.stdout.write(`\r  · fotograma ${i + 1}/${frames} (${pct}%) · ${secs.toFixed(0)} s`);
      }
    }
    ff.proc.stdin.end();
    await ff.done;
    if (pageErrors.length) throw new RenderError(`errores de JS durante el render: ${pageErrors.join(" | ")}`);
    console.log(`\n  ✔ ${loc.out}`);
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  console.error(`✖ ${e instanceof RenderError ? e.message : e.stack || e}`);
  process.exit(1);
});
