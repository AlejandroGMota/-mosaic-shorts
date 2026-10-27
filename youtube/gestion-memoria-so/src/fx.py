"""Ambient motion, flowing connectors and karaoke captions."""
import json, math, os, re
from engine import *

_TILE = None
def background(cv, t):
    # slow drifting dot grid + soft vignette glow
    W, H = cv.w, cv.h
    c = cv.c; step = 64; ox = (t * 6) % step; oy = (t * 3) % step
    global _TILE
    if _TILE is None:
        _TILE = cairo.ImageSurface(cairo.FORMAT_ARGB32, step, step)
        tc = cairo.Context(_TILE); tc.set_source_rgba(*with_a(LINE, 0.55)); tc.rectangle(0, 0, 2, 2); tc.fill()
    pat = cairo.SurfacePattern(_TILE); pat.set_extend(cairo.EXTEND_REPEAT)
    m = cairo.Matrix(); m.translate(-ox, -oy); pat.set_matrix(m)
    c.set_source(pat); c.paint()
    g = cairo.RadialGradient(W * .5 + 220 * math.sin(t * .05), H * .45, 80, W * .5, H * .5, 1100)
    g.add_color_stop_rgba(0, 0.23, 0.51, 0.96, 0.07); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.paint()

def flow(cv, x1, y1, x2, y2, t, col, al=1.0, n=4, speed=0.6, r=4):
    """Dots travelling along a segment, continuously."""
    if al <= 0: return
    for i in range(n):
        p = ((t * speed) + i / n) % 1.0
        a = math.sin(p * math.pi) * al
        cv.circle(lerp(x1, x2, p), lerp(y1, y2, p), r, fill=with_a(col, a))

def pulse(t, f=1.2):
    return 0.5 + 0.5 * math.sin(t * f * 2 * math.pi)

# ---------- captions ----------
FIX = [("operativo El", "operativo. El"), ("está lo sólido", "de estado sólido"), ("Unity", "Unit"), ("En Memory", "La Memory"),
       ("por ubicar", "para ubicar"), ("de mismo modo", "del mismo modo"), ("quitar la memoria", "quitar de la memoria")]

def load_words(path):
    d = json.load(open(path))
    words = [dict(w=w["w"], s=w["s"], e=w["e"]) for seg in d for w in seg["words"]]
    # apply phrase fixes on the word stream (same word count when possible)
    txt = [w["w"] for w in words]
    for a, b in FIX:
        aw, bw = a.split(), b.split()
        for i in range(len(txt) - len(aw) + 1):
            if [x.strip(".,¿?") for x in txt[i:i + len(aw)]] == aw:
                if len(aw) == len(bw):
                    for k in range(len(aw)): txt[i + k] = txt[i + k].replace(aw[k], bw[k])
                else:
                    txt[i] = b; 
                    for k in range(1, len(aw)): txt[i + k] = ""
    for w, s in zip(words, txt): w["w"] = s
    return [w for w in words if w["w"]]

def chunk(words, maxc=44):
    out, cur = [], []
    for w in words:
        line = " ".join(x["w"] for x in cur + [w])
        brk = cur and (len(line) > maxc or w["s"] - cur[-1]["e"] > 0.6)
        if brk: out.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.?!]$", w["w"]) and len(" ".join(x["w"] for x in cur)) > 18: out.append(cur); cur = []
    if cur: out.append(cur)
    return out

WORDS = load_words(os.path.join(os.path.dirname(__file__), "transcript.json"))
CHUNKS = chunk(WORDS)

def captions(cv, t, y=990, size=30):
    for i, ch in enumerate(CHUNKS):
        a, b = ch[0]["s"] - 0.12, ch[-1]["e"] + 0.25
        if i + 1 < len(CHUNKS): b = min(max(b, ch[-1]["e"] + 0.25), CHUNKS[i + 1][0]["s"] - 0.12)
        if not (a <= t < b): continue
        al = min(prog(t, a, .15), 1 - prog(t, b - .15, .15))
        dy = (1 - prog(t, a, .25)) * 10
        widths = [cv.measure(w["w"], size, "Inter", 700)[0] for w in ch]
        sp = cv.measure(" ", size, "Inter", 700)[0] + 2
        tw = sum(widths) + sp * (len(ch) - 1)
        x = W / 2 - tw / 2
        cv.rect(x - 26, y - 30 + dy, tw + 52, 60, fill=with_a(hexrgb('05070d'), .82 * al), stroke=with_a(LINE, al), lw=1.5, r=14)
        for k, (w, ww) in enumerate(zip(ch, widths)):
            nxt = ch[k + 1]["s"] if k + 1 < len(ch) else 1e9
            said = t >= w["s"]; now = w["s"] <= t < min(w["e"] + 0.05, nxt)
            col = FUC if now else (TXT if said else MUTED)
            if now:
                cv.rect(x - 6, y - 22 + dy, ww + 12, 44, fill=with_a(FUC, .16 * al), r=8)
            cv.text(w["w"], x, y + dy, size, with_a(col, al), "Inter", 700, anchor_v="middle")
            x += ww + sp
        return


def chunk_by_width(cv, words, maxw, size):
    """Split a word list into lines that fit maxw."""
    lines, cur, cw = [], [], 0
    sp = cv.measure(" ", size, "Inter", 800)[0]
    for w in words:
        ww = cv.measure(w["w"], size, "Inter", 800)[0]
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    return lines, sp

SHORT_CHUNKS = None
def captions_big(cv, t, cx, y, maxw, size, max_chars=26):
    global SHORT_CHUNKS
    if SHORT_CHUNKS is None: SHORT_CHUNKS = chunk(WORDS, max_chars)
    CH = SHORT_CHUNKS
    for i, ch in enumerate(CH):
        a, b = ch[0]["s"] - 0.1, ch[-1]["e"] + 0.25
        if i + 1 < len(CH): b = min(b, CH[i + 1][0]["s"] - 0.1)
        if not (a <= t < b): continue
        pop = ease_back(clamp((t - a) / .25)); al = clamp(pop)
        lines, sp = chunk_by_width(cv, ch, maxw, size)
        lh = size * 1.3
        flat = [w for line in lines for w, _ in line]
        starts = {id(w): (flat[i + 1]["s"] if i + 1 < len(flat) else 1e9) for i, w in enumerate(flat)}
        for li, line in enumerate(lines):
            tw = sum(ww for _, ww in line) + sp * (len(line) - 1)
            x = cx - tw / 2; yy = y + li * lh + (1 - pop) * 20
            for w, ww in line:
                now = w["s"] <= t < min(w["e"] + 0.05, starts[id(w)]); said = t >= w["s"]
                col = FUC if now else (TXT if said else with_a(TXT, .45))
                if now: cv.rect(x - 8, yy - size * .62, ww + 16, size * 1.24, fill=with_a(FUC, .18 * al), r=10)
                cv.text(w["w"], x, yy, size, with_a(col, al), "Inter", 800, anchor_v="middle")
                x += ww + sp
        return
