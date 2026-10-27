#!/usr/bin/env python3
"""Mosaic Shorts audio step: pick take -> clean -> -14 LUFS -> transcribe -> subtitles.

Python 3.9+ standard library only; ffmpeg/ffprobe are called with subprocess.

Usage (normally through `shorts`):
    python3 audio.py procesar A2
    python3 audio.py procesar --todo
    python3 audio.py procesar A2 --engine guion --force
    python3 audio.py estado

Per Short (ID = A2, short = a2-como-funciona-...):
    in   audios/<guion>/<short>_toma-NN.wav     newest NN wins; audios/<guion>/_descartadas/ is ignored
    out  audios/<guion>/final/<short>/audio.wav  48 kHz 24-bit mono, -14 LUFS (stays on the Mac)
         audios/<guion>/final/<short>/info.json  take used, loudness measurements, engine
         shorts/<ID>/transcript.json, es.srt, es.vtt   (light files, committed to git)
Nothing is ever deleted: files that would be overwritten are moved to
audios/<guion>/_descartadas/<short>/<timestamp>/ first.

transcript.json schema ("mosaic-transcript/1"), times in seconds of final audio.wav:
{
  "schema": "mosaic-transcript/1",
  "id": "A2",                      Short ID (uppercase)
  "short": "a2-como-funciona-...", take prefix / folder name
  "language": "es",
  "duration": 43.512,              duration of audio.wav (s)
  "engine": "whisper.cpp",         whisper.cpp | faster-whisper | guion
  "model": "ggml-large-v3-turbo-q5_0.bin",
  "source_take": "a2-..._toma-01.wav",
  "created": "2026-10-27T20:00:00Z",
  "text": "Por primera vez, ...",
  "words": [                       one entry per spoken word, in order
    {"i": 0, "text": "Por", "norm": "por", "start": 0.15, "end": 0.38, "p": 0.97}
  ],                               norm = lowercase, no accents, only [a-z0-9]; p = confidence or null
  "segments": [                    subtitle cues (the same ones as es.srt / es.vtt)
    {"i": 0, "start": 0.15, "end": 2.9, "text": "Por primera vez, un iPhone", "first": 0, "last": 4}
  ]                                first/last = inclusive indexes into words
}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
REPO = PIPELINE.parent
SCHEMA = "mosaic-transcript/1"
TAKE_RE = re.compile(r"^(([a-z]\d+)-[a-z0-9-]*)_toma-(\d+)$")
NARR_RE = re.compile(r"^\s*\*\*NARRACI[OÓ]N:?\*\*:?\s*(.*)$", re.I)
STOP_RE = re.compile(r"^\s*(`?\*{0,2}\[ANIM\]|---|#)")


class PipelineError(Exception):
    pass


# --------------------------------------------------------------------------- config

def parse_toml(text: str) -> dict:
    """Tiny TOML subset: [sections], key = "string" | number | true/false, # comments."""
    data: dict = {}
    section = data
    for raw in text.splitlines():
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = data.setdefault(line[1:-1].strip(), {})
            continue
        if "=" not in line:
            raise PipelineError(f"config.toml: línea inválida: {raw!r}")
        key, value = (p.strip() for p in line.split("=", 1))
        section[key] = _toml_value(value)
    return data


def _strip_comment(line: str) -> str:
    quoted = False
    for i, ch in enumerate(line):
        if ch == '"':
            quoted = not quoted
        elif ch == "#" and not quoted:
            return line[:i]
    return line


def _toml_value(value: str):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value in ("true", "false"):
        return value == "true"
    try:
        return int(value)
    except ValueError:
        return float(value)


class Config:
    def __init__(self, guion: str | None = None):
        self.raw = parse_toml((PIPELINE / "config.toml").read_text(encoding="utf-8"))
        paths = self.raw.get("paths", {})
        base = os.environ.get("SOCIALMEDIA_DIR") or paths.get("socialmedia_dir") or str(REPO)
        self.root = Path(base).expanduser().resolve()
        self.guion = guion or paths.get("guion", "")
        self.audios = self.path(paths.get("audios_dir", "audios")) / self.guion
        self.final = self.audios / "final"
        self.discarded = self.audios / "_descartadas"
        self.shorts = self.root / "shorts"
        self.animaciones = self.root / "animaciones"
        self.guion_file = self.root / "guiones" / f"{self.guion}.md"
        self.audio = self.raw.get("audio", {})
        self.whisper = self.raw.get("whisper", {})

    def path(self, value: str) -> Path:
        p = Path(value).expanduser()
        return p if p.is_absolute() else self.root / p


# --------------------------------------------------------------------------- takes & guion

class Take:
    def __init__(self, path: Path, m: re.Match):
        self.path = path
        self.short = m.group(1)
        self.id = m.group(2).upper()
        self.n = int(m.group(3))


def find_takes(cfg: Config) -> dict:
    """ID -> newest Take. Only the top level of audios/<guion>/ counts (never _descartadas/)."""
    best: dict = {}
    if not cfg.audios.is_dir():
        return best
    for wav in sorted(cfg.audios.glob("*_toma-*.wav")):
        m = TAKE_RE.match(wav.stem)
        if not m:
            continue
        take = Take(wav, m)
        if take.id not in best or take.n > best[take.id].n:
            best[take.id] = take
    return best


def guion_items(cfg: Config) -> list:
    """[(ID, title, narration text)] in guion order, from '### A2 ⭐ Title' headings."""
    if not cfg.guion_file.exists():
        return []
    lines = cfg.guion_file.read_text(encoding="utf-8").splitlines()
    items = []
    i = 0
    while i < len(lines):
        m = re.match(r"^###\s+([A-Za-z]\d+)\b\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        sid, title = m.group(1).upper(), m.group(2).replace("⭐", "").strip()
        parts = []
        i += 1
        while i < len(lines) and not lines[i].startswith("### "):
            n = NARR_RE.match(lines[i])
            if n:
                if n.group(1).strip():
                    parts.append(n.group(1).strip())
                i += 1
                while i < len(lines) and not STOP_RE.match(lines[i]) and not NARR_RE.match(lines[i]):
                    if lines[i].strip():
                        parts.append(lines[i].strip())
                    i += 1
                continue
            i += 1
        items.append((sid, title, " ".join(parts)))
    return items


# --------------------------------------------------------------------------- helpers

def run(cmd: list, capture: bool = True) -> subprocess.CompletedProcess:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE if capture else None)
    except FileNotFoundError:
        raise PipelineError(f"no encuentro el programa: {cmd[0]}")
    if res.returncode != 0:
        err = (res.stderr or b"").decode("utf-8", "replace")[-2000:]
        raise PipelineError(f"falló: {' '.join(str(c) for c in cmd[:6])} ...\n{err}")
    return res


def ffmpeg(*args) -> str:
    res = run(["ffmpeg", "-hide_banner", "-nostats", "-y", *[str(a) for a in args]])
    return res.stderr.decode("utf-8", "replace")


def duration_of(path: Path) -> float:
    res = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    return float(res.stdout.decode().strip())


def last_json(text: str) -> dict:
    start = text.rfind("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise PipelineError("ffmpeg no devolvió el JSON de loudnorm")
    return json.loads(text[start:end + 1])


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def discard(cfg: Config, short: str, files: list, when: str) -> None:
    """Move existing files to _descartadas/<short>/<when>/ (never delete)."""
    existing = [f for f in files if f.exists()]
    if not existing:
        return
    dest = cfg.discarded / short / when
    dest.mkdir(parents=True, exist_ok=True)
    for f in existing:
        target = dest / f.name
        if target.exists():
            target = dest / f"{f.parent.name}-{f.name}"
        shutil.move(str(f), str(target))
    print(f"  · versión anterior movida a {dest.relative_to(cfg.root) if cfg.root in dest.parents else dest}")


def norm(word: str) -> str:
    text = unicodedata.normalize("NFD", word.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", text)


# --------------------------------------------------------------------------- audio

def clean_audio(cfg: Config, src: Path, dst: Path) -> None:
    a = cfg.audio
    thr = f"{a.get('silence_threshold_db', -40)}dB"
    chain = ",".join([
        f"highpass=f={a.get('highpass_hz', 80)}",
        f"afftdn=nr={a.get('denoise_nr', 12)}:nf={a.get('denoise_nf', -50)}:tn=1",
        # ffmpeg >= 6.1 semantics: silence longer than stop_duration is cut down to stop_duration.
        "silenceremove=start_periods=1:start_duration=0:start_threshold={thr}:start_silence={edge}"
        ":stop_periods=-1:stop_duration={maxp}:stop_threshold={thr}:stop_silence=0".format(
            thr=thr, edge=a.get("edge_pause", 0.15), maxp=a.get("max_pause", 0.45)),
    ])
    ffmpeg("-i", src, "-ac", "1", "-af", chain, "-c:a", "pcm_f32le", dst)


def loudnorm(cfg: Config, src: Path, dst: Path) -> dict:
    a = cfg.audio
    target = "I={}:TP={}:LRA={}".format(a.get("lufs", -14.0), a.get("true_peak", -1.5), a.get("lra", 11.0))
    m = last_json(ffmpeg("-i", src, "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"))
    if m.get("input_i") in ("-inf", None) or float(m["input_i"]) < -70:
        raise PipelineError("la toma está en silencio (loudnorm no mide nada)")
    second = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true:print_format=json")
    out = last_json(ffmpeg("-i", src, "-af", second, "-ar", a.get("sample_rate", 48000), "-ac", "1",
                           "-c:a", "pcm_s24le", dst))
    return {"pass1": m, "pass2": out}


def speech_spans(cfg: Config, wav: Path) -> list:
    """Non-silent spans [(start, end)] using ffmpeg silencedetect."""
    thr = cfg.audio.get("silence_threshold_db", -40)
    log = ffmpeg("-i", wav, "-af", f"silencedetect=n={thr}dB:d=0.2", "-f", "null", "-")
    total = duration_of(wav)
    spans, cursor = [], 0.0
    for line in log.splitlines():
        s = re.search(r"silence_start: (-?[\d.]+)", line)
        e = re.search(r"silence_end: ([\d.]+)", line)
        if s:
            start = max(0.0, float(s.group(1)))
            if start - cursor > 0.05:
                spans.append((cursor, start))
        if e:
            cursor = float(e.group(1))
    if total - cursor > 0.05:
        spans.append((cursor, total))
    return spans or [(0.0, total)]


# --------------------------------------------------------------------------- transcription engines

def engine_available(cfg: Config, name: str) -> tuple:
    w = cfg.whisper
    if name == "whisper.cpp":
        exe = shutil.which(w.get("cpp_bin", "whisper-cli")) or (
            str(Path(w.get("cpp_bin", "")).expanduser()) if Path(w.get("cpp_bin", "")).expanduser().is_file() else None)
        model = Path(w.get("cpp_model", "")).expanduser()
        if not exe:
            return False, "no encuentro whisper-cli (brew install whisper-cpp)"
        if not model.is_file():
            return False, f"no encuentro el modelo {model}"
        return True, exe
    if name == "faster-whisper":
        py = Path(w.get("fw_python", "~/.venvs/fw/bin/python")).expanduser()
        if not py.is_file():
            return False, f"no encuentro {py}"
        res = subprocess.run([str(py), "-c", "import faster_whisper"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            return False, f"{py} no tiene faster_whisper"
        return True, str(py)
    if name == "guion":
        return True, "guion"
    return False, f"motor desconocido: {name}"


def pick_engine(cfg: Config, requested: str) -> str:
    if requested != "auto":
        ok, why = engine_available(cfg, requested)
        if not ok:
            raise PipelineError(f"{requested}: {why}")
        return requested
    reasons = []
    for name in ("whisper.cpp", "faster-whisper"):
        ok, why = engine_available(cfg, name)
        if ok:
            return name
        reasons.append(f"{name}: {why}")
    raise PipelineError("no hay motor de transcripción.\n  " + "\n  ".join(reasons)
                        + "\n  Corre `shorts doctor`. Solo para probar: --engine guion")


def transcribe_whisper_cpp(cfg: Config, wav: Path, tmp: Path) -> tuple:
    w = cfg.whisper
    _, exe = engine_available(cfg, "whisper.cpp")
    model = Path(w["cpp_model"]).expanduser()
    wav16 = tmp / "in16k.wav"
    ffmpeg("-i", wav, "-ar", 16000, "-ac", 1, "-c:a", "pcm_s16le", wav16)
    base = tmp / "whisper"
    cmd = [exe, "-m", str(model), "-f", str(wav16), "-l", w.get("language", "es"),
           "-ml", "1", "-sow", "-ojf", "-of", str(base), "-np"]
    if w.get("prompt"):
        cmd += ["--prompt", w["prompt"]]
    if w.get("cpp_dtw"):
        cmd += ["-dtw", w["cpp_dtw"]]
    run(cmd)
    data = json.loads((tmp / "whisper.json").read_bytes().decode("utf-8", "replace"))
    words = []
    for seg in data.get("transcription", []):
        text = seg.get("text", "").strip()
        if not text or text.startswith("["):
            continue
        t0 = seg["offsets"]["from"] / 1000.0
        t1 = seg["offsets"]["to"] / 1000.0
        probs = [t.get("p") for t in seg.get("tokens", []) if isinstance(t.get("p"), (int, float))
                 and not t.get("text", "").startswith("[")]
        p = round(sum(probs) / len(probs), 3) if probs else None
        words.extend(_split_span(text, t0, t1, p))
    return words, model.name


FW_SCRIPT = r"""
import json, sys
from faster_whisper import WhisperModel
wav, model, lang, prompt = sys.argv[1:5]
m = WhisperModel(model, device="cpu", compute_type="int8")
segs, _ = m.transcribe(wav, language=lang, word_timestamps=True, beam_size=5,
                       initial_prompt=prompt or None, vad_filter=False)
out = []
for s in segs:
    for w in s.words or []:
        out.append({"text": w.word, "start": w.start, "end": w.end, "p": w.probability})
print(json.dumps(out))
"""


def transcribe_faster_whisper(cfg: Config, wav: Path, tmp: Path) -> tuple:
    w = cfg.whisper
    _, py = engine_available(cfg, "faster-whisper")
    model = w.get("fw_model", "medium")
    res = run([py, "-c", FW_SCRIPT, str(wav), model, w.get("language", "es"), w.get("prompt", "")])
    words = []
    for item in json.loads(res.stdout.decode("utf-8")):
        p = round(float(item["p"]), 3) if item.get("p") is not None else None
        words.extend(_split_span(item["text"].strip(), float(item["start"]), float(item["end"]), p))
    return words, model


def transcribe_guion(cfg: Config, wav: Path, narration: str) -> tuple:
    """Fallback for tests: spread the guion words over the detected speech spans.

    Timing is approximate (by character length), so only use it to test the pipeline.
    """
    tokens = narration.split()
    if not tokens:
        raise PipelineError("el guion no tiene NARRACIÓN para este Short")
    spans = speech_spans(cfg, wav)
    speech = sum(e - s for s, e in spans)
    weights = [len(t) + 1 for t in tokens]
    total_w = float(sum(weights))
    words, acc = [], 0.0
    for tok, wt in zip(tokens, weights):
        v0, v1 = acc / total_w * speech, (acc + wt) / total_w * speech
        acc += wt
        start, i0 = _virtual_to_real(spans, v0)
        end, i1 = _virtual_to_real(spans, v1)
        _, im = _virtual_to_real(spans, (v0 + v1) / 2)
        if i0 != im:  # a word never straddles a pause: keep it inside the span holding its middle
            start = spans[im][0]
        if i1 != im:
            end = spans[im][1]
        words.append({"text": tok, "start": start, "end": end, "p": None})
    return words, "guion"


def _virtual_to_real(spans: list, v: float) -> tuple:
    acc = 0.0
    for i, (s, e) in enumerate(spans):
        if v <= acc + (e - s):
            return s + (v - acc), i
        acc += e - s
    return spans[-1][1], len(spans) - 1


def _split_span(text: str, t0: float, t1: float, p) -> list:
    parts = text.split()
    if len(parts) <= 1:
        return [{"text": text, "start": t0, "end": t1, "p": p}] if text else []
    total = float(sum(len(x) for x in parts))
    out, acc = [], 0.0
    for x in parts:
        a = t0 + (t1 - t0) * acc / total
        acc += len(x)
        out.append({"text": x, "start": a, "end": t0 + (t1 - t0) * acc / total, "p": p})
    return out


# --------------------------------------------------------------------------- transcript & subtitles

def tidy_words(words: list, duration: float) -> list:
    out, last_end = [], 0.0
    for w in words:
        text = w["text"].strip()
        if not text or not norm(text) and not re.search(r"\w", text):
            if out and text:  # bare punctuation token: glue to the previous word
                out[-1]["text"] += text
            continue
        start = min(max(float(w["start"]), last_end), duration)
        end = min(max(float(w["end"]), start + 0.05), duration)
        out.append({"i": len(out), "text": text, "norm": norm(text),
                    "start": round(start, 3), "end": round(end, 3), "p": w.get("p")})
        last_end = start
    return out


def build_segments(words: list, max_chars: int = 42, max_gap: float = 0.7) -> list:
    """Subtitle cues: split at sentence/clause ends and pauses, then balance long clauses."""
    clauses: list = []
    cur: list = []
    for w in words:
        if cur and w["start"] - cur[-1]["end"] > max_gap:
            clauses.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.?!…:;,]$", w["text"]):
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)

    merged: list = []  # glue short clauses ("Abierto,") to the next one when they fit together
    for c in clauses:
        if merged and _chars(merged[-1]) < 16 and _chars(merged[-1]) + 1 + _chars(c) <= max_chars \
                and not re.search(r"[.?!…]$", merged[-1][-1]["text"]) \
                and c[0]["start"] - merged[-1][-1]["end"] <= max_gap:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)

    segs: list = []
    for c in merged:
        for chunk in _balance(c, max_chars):
            segs.append({"i": len(segs), "start": chunk[0]["start"], "end": chunk[-1]["end"],
                         "text": " ".join(w["text"] for w in chunk),
                         "first": chunk[0]["i"], "last": chunk[-1]["i"]})
    for a, b in zip(segs, segs[1:]):  # cues never overlap
        a["end"] = min(a["end"], b["start"])
    return segs


def _chars(ws: list) -> int:
    return len(" ".join(w["text"] for w in ws))


def _balance(ws: list, max_chars: int) -> list:
    """Split a clause into the fewest chunks <= max_chars with similar lengths."""
    n = -(-_chars(ws) // max_chars)
    if n <= 1 or len(ws) <= 1:
        return [ws]
    target = _chars(ws) / n
    out, cur = [], []
    for w in ws:
        if cur and len(out) < n - 1 and (_chars(cur + [w]) > max_chars or _chars(cur) >= target):
            out.append(cur)
            cur = []
        cur.append(w)
    out.append(cur)
    return out


def fmt_time(t: float, sep: str) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def to_srt(segs: list) -> str:
    return "".join(f"{i + 1}\n{fmt_time(s['start'], ',')} --> {fmt_time(s['end'], ',')}\n{s['text']}\n\n"
                   for i, s in enumerate(segs))


def to_vtt(segs: list) -> str:
    return "WEBVTT\n\n" + "".join(f"{fmt_time(s['start'], '.')} --> {fmt_time(s['end'], '.')}\n{s['text']}\n\n"
                                  for s in segs)


# --------------------------------------------------------------------------- commands

def process(cfg: Config, take: Take, engine: str, narration: str) -> None:
    when = stamp()
    out_dir = cfg.final / take.short
    short_dir = cfg.shorts / take.id
    print(f"▶ {take.id}: {take.path.name}")
    with tempfile.TemporaryDirectory(prefix="mosaic-") as tmp_s:
        tmp = Path(tmp_s)
        clean = tmp / "limpio.wav"
        normed = tmp / "audio.wav"
        print("  · limpiando ruido y silencios")
        clean_audio(cfg, take.path, clean)
        print("  · normalizando (loudnorm, 2 pasadas)")
        loud = loudnorm(cfg, clean, normed)
        duration = duration_of(normed)
        print(f"  · transcribiendo con {engine}")
        if engine == "whisper.cpp":
            raw, model = transcribe_whisper_cpp(cfg, normed, tmp)
        elif engine == "faster-whisper":
            raw, model = transcribe_faster_whisper(cfg, normed, tmp)
        else:
            raw, model = transcribe_guion(cfg, normed, narration)
        words = tidy_words(raw, duration)
        if not words:
            raise PipelineError("la transcripción salió vacía")
        segs = build_segments(words)
        transcript = {
            "schema": SCHEMA, "id": take.id, "short": take.short,
            "language": cfg.whisper.get("language", "es"), "duration": round(duration, 3),
            "engine": engine, "model": model, "source_take": take.path.name,
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "text": " ".join(w["text"] for w in words), "words": words, "segments": segs,
        }
        files = {
            "transcript.json": json.dumps(transcript, ensure_ascii=False, indent=1) + "\n",
            "es.srt": to_srt(segs),
            "es.vtt": to_vtt(segs),
        }
        info = {"id": take.id, "short": take.short, "source_take": take.path.name, "engine": engine,
                "model": model, "duration": round(duration, 3), "processed": transcript["created"],
                "loudnorm": loud}

        out_dir.mkdir(parents=True, exist_ok=True)
        short_dir.mkdir(parents=True, exist_ok=True)
        changed = [short_dir / n for n in files
                   if (short_dir / n).exists() and (short_dir / n).read_text(encoding="utf-8") != files[n]]
        discard(cfg, take.short, [out_dir / n for n in ("audio.wav", "info.json", *files)] + changed, when)
        shutil.move(str(normed), str(out_dir / "audio.wav"))
        (out_dir / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for name, content in files.items():
            (out_dir / name).write_text(content, encoding="utf-8")
            (short_dir / name).write_text(content, encoding="utf-8")
    out_i = loud["pass2"].get("output_i")
    print(f"  ✔ {duration:.1f} s · {out_i} LUFS · {len(words)} palabras · {len(segs)} subtítulos")
    print(f"    {out_dir / 'audio.wav'}")
    print(f"    {short_dir.relative_to(cfg.root)}/transcript.json, es.srt, es.vtt")


def processed_take(cfg: Config, take: Take) -> str | None:
    info = cfg.final / take.short / "info.json"
    if not (cfg.final / take.short / "audio.wav").exists() or not info.exists():
        return None
    try:
        return json.loads(info.read_text(encoding="utf-8")).get("source_take")
    except (OSError, ValueError):
        return None


def cmd_procesar(args) -> int:
    cfg = Config(args.guion)
    takes = find_takes(cfg)
    if not takes:
        raise PipelineError(f"no hay tomas en {cfg.audios}")
    narrations = {sid: text for sid, _, text in guion_items(cfg)}
    if args.todo:
        chosen = [t for _, t in sorted(takes.items())
                  if args.force or processed_take(cfg, t) != t.path.name]
        if not chosen:
            print("Nada pendiente: todas las tomas más recientes ya están procesadas (usa --force para rehacer).")
            return 0
    else:
        chosen = []
        for sid in args.ids:
            sid = sid.upper()
            if sid not in takes:
                raise PipelineError(f"{sid}: no hay tomas {sid.lower()}-*_toma-NN.wav en {cfg.audios}")
            chosen.append(takes[sid])
    engine = pick_engine(cfg, args.engine or cfg.whisper.get("engine", "auto"))
    failed = []
    for take in chosen:
        try:
            process(cfg, take, engine, narrations.get(take.id, ""))
        except PipelineError as e:
            print(f"  ✖ {take.id}: {e}", file=sys.stderr)
            failed.append(take.id)
    if failed:
        print(f"Fallaron: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


def cmd_estado(args) -> int:
    cfg = Config(args.guion)
    takes = find_takes(cfg)
    ids = [sid for sid, _, _ in guion_items(cfg)]
    ids += [sid for sid in sorted(takes) if sid not in ids]
    print(f"Guion: {cfg.guion}   Audios: {cfg.audios}")
    print(f"{'ID':<4} {'toma':<6} {'audio':<10} {'transcript':<11} {'animación':<10} {'video':<6}")
    for sid in ids:
        take = takes.get(sid)
        toma = f"{take.n:02d}" if take else "—"
        audio = "—"
        video = "—"
        if take:
            done = processed_take(cfg, take)
            audio = "✓" if done == take.path.name else ("↻ nueva" if done else "pendiente")
            video = "✓" if (cfg.final / take.short / f"{sid}.mp4").exists() else "—"
        tr = "✓" if (cfg.shorts / sid / "transcript.json").exists() else "—"
        anim = "✓" if (cfg.animaciones / sid / "index.html").exists() else "—"
        print(f"{sid:<4} {toma:<6} {audio:<10} {tr:<11} {anim:<10} {video:<6}")
    return 0


def cmd_motores(args) -> int:
    cfg = Config(args.guion)
    for name in ("whisper.cpp", "faster-whisper"):
        ok, why = engine_available(cfg, name)
        print(f"{'ok' if ok else 'falta'}\t{name}\t{why}")
    return 0


def cmd_narracion(args) -> int:
    cfg = Config(args.guion)
    for sid, title, text in guion_items(cfg):
        if sid == args.id.upper():
            print(text)
            return 0
    raise PipelineError(f"{args.id}: no está en {cfg.guion_file}")


def take_prefix(sid: str, title: str) -> str:
    """Same slug the grabador uses for take names: 'a2-como-funciona-...' (max 60 chars)."""
    text = unicodedata.normalize("NFD", f"{sid} {title}".lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60]


def cmd_slug(args) -> int:
    cfg = Config(args.guion)
    for sid, title, _ in guion_items(cfg):
        if sid == args.id.upper():
            print(f"{cfg.guion}\t{take_prefix(sid, title)}")
            return 0
    raise PipelineError(f"{args.id}: no está en {cfg.guion_file}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="audio.py", description="Mosaic Shorts: audio + transcript")
    ap.add_argument("--guion", help="guion (default: config.toml)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("procesar", help="clean, normalize and transcribe takes")
    p.add_argument("ids", nargs="*", help="Short IDs, e.g. A2 B1")
    p.add_argument("--todo", action="store_true", help="every Short whose newest take is not processed yet")
    p.add_argument("--force", action="store_true", help="with --todo: redo already processed takes too")
    p.add_argument("--engine", choices=["auto", "whisper.cpp", "faster-whisper", "guion"])
    p.set_defaults(func=cmd_procesar)
    sub.add_parser("estado", help="status table").set_defaults(func=cmd_estado)
    sub.add_parser("motores", help="check transcription engines").set_defaults(func=cmd_motores)
    p = sub.add_parser("narracion", help="print the guion narration of a Short")
    p.add_argument("id")
    p.set_defaults(func=cmd_narracion)
    p = sub.add_parser("slug", help="print '<guion>\\t<take prefix>' of a Short")
    p.add_argument("id")
    p.set_defaults(func=cmd_slug)
    args = ap.parse_args(argv)
    if args.cmd == "procesar" and not args.todo and not args.ids:
        ap.error("indica un ID (A2) o --todo")
    try:
        return args.func(args)
    except PipelineError as e:
        print(f"✖ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
