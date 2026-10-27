"""Export synced subtitles (.srt + .vtt) from the corrected word-level transcript."""
import re, sys
from fx import WORDS

MAX_LINE = 42          # chars per line (broadcast/YouTube convention)
MAX_CUE_DUR = 6.5      # seconds
GAP_BREAK = 0.45       # pause that forces a new cue
WEAK = {"a", "al", "de", "del", "el", "la", "las", "los", "lo", "en", "y", "o", "que", "con", "un", "una",
        "por", "para", "se", "su", "sus", "es", "como", "sin", "cuando", "donde", "pues"}

def split_lines(text):
    if len(text) <= MAX_LINE: return [text]
    words = text.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= MAX_LINE and len(b) <= MAX_LINE:
            score = abs(len(a) - len(b)) + (40 if words[i - 1].lower().strip(",.") in WEAK else 0) \
                    - (12 if re.search(r"[,.]$", words[i - 1]) else 0)
            if best is None or score < best[0]: best = (score, [a, b])
    return best[1] if best else [text]

def fits(text):
    return max(len(l) for l in split_lines(text)) <= MAX_LINE

def build_cues(words):
    cues, cur = [], []
    for w in words:
        if cur:
            prev = cur[-1]
            cur_len = len(" ".join(x["w"] for x in cur))
            text = " ".join(x["w"] for x in cur + [w])
            natural = (re.search(r"[.?!]$", prev["w"]) and cur_len > 12) or \
                      (prev["w"].endswith(",") and cur_len >= 30) or (w["s"] - prev["e"] > GAP_BREAK)
            forced = not fits(text) or w["e"] - cur[0]["s"] > MAX_CUE_DUR
            if natural:
                cues.append(cur); cur = []
            elif forced:
                carry = []
                while len(cur) > 2 and cur[-1]["w"].lower().strip(",.") in WEAK:
                    carry.insert(0, cur.pop())
                cues.append(cur); cur = carry
        cur.append(w)
    if cur: cues.append(cur)
    return cues

def timed(cues):
    out = []
    for i, c in enumerate(cues):
        st = c[0]["s"]
        en = max(c[-1]["e"] + 0.3, st + 1.0)
        if i + 1 < len(cues): en = min(en, cues[i + 1][0]["s"] - 0.04)
        en = max(en, c[-1]["e"])
        if en <= st: en = st + 0.3
        out.append((st, en, split_lines(" ".join(w["w"] for w in c))))
    return out

def fmt(t, sep):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"

def write(cues, base):
    srt, vtt = [], ["WEBVTT", ""]
    for i, (st, en, lines) in enumerate(cues, 1):
        srt += [str(i), f"{fmt(st, ',')} --> {fmt(en, ',')}", *lines, ""]
        vtt += [f"{fmt(st, '.')} --> {fmt(en, '.')}", *lines, ""]
    open(base + ".srt", "w", encoding="utf-8").write("\n".join(srt))
    open(base + ".vtt", "w", encoding="utf-8").write("\n".join(vtt))

if __name__ == "__main__":
    cues = timed(build_cues(WORDS))
    write(cues, sys.argv[1])
    durs = [en - st for st, en, _ in cues]
    overl = sum(1 for a, b in zip(cues, cues[1:]) if a[1] > b[0])
    print(f"cues={len(cues)} max_line={max(len(l) for *_, ls in cues for l in ls)} "
          f"dur_min={min(durs):.2f} dur_max={max(durs):.2f} overlaps={overl} last_end={cues[-1][1]:.2f}")
