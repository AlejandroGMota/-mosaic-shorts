"""Write translated .srt/.vtt reusing the Spanish cue timings."""
import re, sys
from subtitles import WORDS, build_cues, timed, fmt
from translations import LANGS

def reflow(text):
    words = text.split()
    for maxl in (42, 48):
        if len(text) <= maxl: return [text]
        best = None
        for i in range(1, len(words)):
            a, b = " ".join(words[:i]), " ".join(words[i:])
            if len(a) <= maxl and len(b) <= maxl:
                sc = abs(len(a) - len(b)) - (12 if re.search(r"[,.;:]$", words[i - 1]) else 0)
                if best is None or sc < best[0]: best = (sc, [a, b])
        if best: return best[1]
    # 3 balanced lines
    target = len(text) / 3; lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > target * 1.15 and len(lines) < 2: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur]

def main(base):
    cues = timed(build_cues(WORDS))
    for lang, block in LANGS.items():
        tr = block.strip().split("\n")
        assert len(tr) == len(cues), f"{lang}: {len(tr)} lines vs {len(cues)} cues"
        srt, vtt = [], ["WEBVTT", f"Language: {lang}", ""]
        for i, ((st, en, _), txt) in enumerate(zip(cues, tr), 1):
            ls = reflow(txt.strip())
            srt += [str(i), f"{fmt(st, ',')} --> {fmt(en, ',')}", *ls, ""]
            vtt += [f"{fmt(st, '.')} --> {fmt(en, '.')}", *ls, ""]
        open(f"{base}.{lang}.srt", "w", encoding="utf-8").write("\n".join(srt))
        open(f"{base}.{lang}.vtt", "w", encoding="utf-8").write("\n".join(vtt))
        mx = max(len(l) for b in tr for l in reflow(b)); n3 = sum(1 for b in tr if len(reflow(b)) > 2)
        print(f"{lang}: {len(tr)} cues, max_line={mx}, 3-line cues={n3}")

if __name__ == "__main__":
    main(sys.argv[1])
