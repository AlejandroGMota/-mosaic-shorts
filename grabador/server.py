#!/usr/bin/env python3
"""Grabador de guiones — teleprompter local + grabación WAV sin pérdida.

Uso:
    python3 server.py            # abre http://127.0.0.1:8765
    PORT=9000 python3 server.py

Lee los guiones de ../socialmedia/guiones/*.md (bloques **NARRACIÓN:**) y guarda las
tomas en ../socialmedia/audios/<guion>/<short>_toma-NN.wav + .json (marcas por parte).
Solo escucha en 127.0.0.1. Sin dependencias: Python 3.9+ de la Mac.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

BASE = Path(__file__).resolve().parent
SOCIAL = Path(os.environ.get("SOCIALMEDIA_DIR", BASE.parent / "socialmedia"))
GUIONES = SOCIAL / "guiones"
AUDIOS = SOCIAL / "audios"
PORT = int(os.environ.get("PORT", "8765"))
MAX_UPLOAD = 300 * 1024 * 1024  # 300 MB ≈ 35 min de WAV 48 kHz/24 bits mono

ANIM_RE = re.compile(r"^\s*(`?\*{0,2}\[ANIM\]|---|#)")
NARR_RE = re.compile(r"^\s*\*\*NARRACI[OÓ]N:?\*\*:?\s*(.*)$", re.I)


def slug(text: str) -> str:
    text = text.lower()
    for a, b in zip("áéíóúüñ", "aeiouun"):
        text = text.replace(a, b)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or "sin-titulo"


def clean_heading(line: str) -> str:
    return re.sub(r"^#+\s*", "", line).replace("⭐", "").strip()


def parse_guion(path: Path) -> list[dict]:
    """Un item por '###' con narración; si el archivo no usa '###', todo el archivo es un item."""
    lines = path.read_text(encoding="utf-8").splitlines()
    h1 = next((clean_heading(l) for l in lines if l.startswith("# ")), path.stem)
    items: dict[str, dict] = {}
    order: list[str] = []
    h2 = h3 = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            h3 = clean_heading(line)
        elif line.startswith("## "):
            h2, h3 = clean_heading(line), None
        m = NARR_RE.match(line)
        if m:
            key = h3 or h1
            if key not in items:
                star = False
                if h3:  # buscar si el heading original llevaba ⭐
                    star = any(l.startswith("### ") and clean_heading(l) == h3 and "⭐" in l for l in lines)
                items[key] = {"title": key, "section": h2 if h3 else None, "star": star, "parts": []}
                order.append(key)
            para = [m.group(1)] if m.group(1).strip() else []
            i += 1
            while i < len(lines) and not ANIM_RE.match(lines[i]) and not NARR_RE.match(lines[i]):
                if lines[i].strip():
                    para.append(lines[i].strip())
                i += 1
            # Cada renglón del guion = una parte (pausa natural al leer).
            items[key]["parts"].extend(p for p in para if p)
            continue
        i += 1
    out = []
    for key in order:
        it = items[key]
        if not it["parts"]:
            continue
        it["id"] = slug(it["title"])
        it["words"] = sum(len(p.split()) for p in it["parts"])
        out.append(it)
    return out


def list_guiones() -> list[dict]:
    files = []
    for path in sorted(GUIONES.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.name.upper() == "PLAN.MD":
            continue
        try:
            items = parse_guion(path)
        except Exception as e:  # un archivo raro no debe tumbar la app
            print(f"[aviso] no pude leer {path.name}: {e}", file=sys.stderr)
            continue
        if not items:
            continue
        for it in items:
            it["takes"] = sorted(p.name for p in (AUDIOS / path.stem).glob(f"{it['id']}_toma-*.wav"))
        files.append({"file": path.stem, "items": items})
    for sub in sorted(p for p in GUIONES.iterdir() if p.is_dir()):
        for path in sorted(sub.glob("guion*.md")):
            items = parse_guion(path)
            for it in items:
                it["takes"] = sorted(p.name for p in (AUDIOS / sub.name).glob(f"{it['id']}_toma-*.wav"))
            if items:
                files.append({"file": sub.name, "items": items})
    return files


class Handler(BaseHTTPRequestHandler):
    server_version = "GrabadorGuiones/1.0"

    def log_message(self, fmt, *args):  # consola limpia
        if "/api/" in (args[0] if args else ""):
            sys.stderr.write("· " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, ctype: str = "application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            return self._send(200, (BASE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if url.path == "/api/guiones":
            return self._json(200, {"guiones": list_guiones(), "audios": str(AUDIOS)})
        if url.path == "/api/audio":
            q = parse_qs(url.query)
            try:
                f = AUDIOS / slug(q["file"][0]) / Path(q["take"][0]).name
            except (KeyError, IndexError):
                return self._json(400, {"error": "faltan parámetros"})
            if not f.exists() or f.suffix != ".wav":
                return self._json(404, {"error": "no existe"})
            return self._send(200, f.read_bytes(), "audio/wav")
        return self._json(404, {"error": "ruta no encontrada"})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/api/grabar":
            return self._json(404, {"error": "ruta no encontrada"})
        q = parse_qs(url.query)
        try:
            file_id, item_id = slug(q["file"][0]), slug(q["id"][0])
            length = int(self.headers.get("Content-Length", "0"))
        except (KeyError, IndexError, ValueError):
            return self._json(400, {"error": "faltan parámetros"})
        if length <= 44 or length > MAX_UPLOAD:
            return self._json(400, {"error": f"tamaño inválido: {length}"})
        data = self.rfile.read(length)
        if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
            return self._json(400, {"error": "no es WAV"})
        folder = AUDIOS / file_id
        folder.mkdir(parents=True, exist_ok=True)
        # Nombre = el Short que se va a hacer: <short>_toma-NN.wav
        n = 1 + max([int(m.group(1)) for p in folder.glob(f"{item_id}_toma-*.wav") if (m := re.search(r"_toma-(\d+)$", p.stem))] or [0])
        wav = folder / f"{item_id}_toma-{n:02d}.wav"
        tmp = wav.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(wav)  # escritura atómica: nunca queda un WAV a medias
        meta_raw = self.headers.get("X-Marcas", "")
        try:
            meta = json.loads(unquote(meta_raw)) if meta_raw else {}
        except json.JSONDecodeError:
            meta = {"error": "marcas ilegibles"}
        meta.update({"wav": wav.name, "bytes": length, "guardado": datetime.now().isoformat(timespec="seconds")})
        wav.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✔ guardado {wav.relative_to(SOCIAL)} ({length / 1e6:.1f} MB)")
        return self._json(200, {"ok": True, "take": wav.name, "path": str(wav)})


def main() -> None:
    if not GUIONES.exists():
        sys.exit(f"No encuentro la carpeta de guiones: {GUIONES}")
    AUDIOS.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Grabador de guiones en {url}\nGuiones: {GUIONES}\nAudios:  {AUDIOS}\nCtrl+C para cerrar.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrado.")


if __name__ == "__main__":
    main()
