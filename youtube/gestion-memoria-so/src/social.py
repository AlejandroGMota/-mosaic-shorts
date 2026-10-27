"""Vertical 9:16 clips and square 1:1 full video, composed from the same scenes."""
import sys, math
from scenes import *
from fx import background, captions_big, pulse

CROP = (100, 180, 1820, 950)   # content region of the 16:9 composition

def draw_content(cv, t, x, y, w, al=1.0):
    cx0, cy0, cx1, cy1 = CROP
    s = w / (cx1 - cx0); h = (cy1 - cy0) * s
    c = cv.c
    cv.rect(x - 14, y - 14, w + 28, h + 28, fill=with_a(PANEL, .55 * al), stroke=with_a(LINE, al), lw=2, r=22)
    c.save(); c.rectangle(x, y, w, h); c.clip()
    c.translate(x, y); c.scale(s, s); c.translate(-cx0, -cy0)
    cv.push(al); content(cv, t); cv.pop()
    c.restore()
    return h

CLIPS = {  # id: (start, end, kicker, hook, accent)
    "01-ram-vs-rom":      (19.5, 47.97, "MEMORIA PRINCIPAL", "RAM vs ROM: ¿cuál pierde tus datos al apagar?", PRI),
    "02-mmu-base-limite": (61.53, 94.69, "MMU", "¿Cómo encuentra el sistema operativo tu programa en la RAM?", PRI),
    "03-particiones":     (94.69, 145.64, "ASIGNACIÓN DE MEMORIA", "Particiones estáticas vs dinámicas", SEC),
    "04-segmentacion":    (145.64, 178.4, "SEGMENTACIÓN", "Liberar memoria sin matar el proceso", PRI),
}
END_CARD = 2.2

def wrap_text(cv, s, x, y, size, maxw, col, weight=800, lh=1.15):
    words = s.split(); line = ""; yy = y
    for w in words:
        test = (line + " " + w).strip()
        if cv.measure(test, size, "Inter", weight)[0] > maxw and line:
            cv.text(line, x, yy, size, col, "Inter", weight, align="center"); yy += size * lh; line = w
        else: line = test
    if line: cv.text(line, x, yy, size, col, "Inter", weight, align="center"); yy += size * lh
    return yy

def vertical(cid):
    a, b, kick, hook, acc = CLIPS[cid]
    dur = b - a + END_CARD
    def f(cv, lt):
        t = a + lt
        background(cv, lt)
        end = prog(lt, b - a, .4)
        hp = ease_back(clamp(lt / .6))
        cv.push(clamp(hp) * (1 - end), dy=(1 - hp) * -30)
        cv.text(kick, 540, 170, 26, acc, "JetBrains Mono", 700, align="center")
        wrap_text(cv, hook, 540, 220, 66, 960, TXT)
        cv.pop()
        ca = prog(lt, .3, .5) * (1 - end)
        draw_content(cv, min(t, b - .46), 30, 560, 1020, ca)
        cv.push(1 - end); captions_big(cv, min(t, b - .01), 540, 1260, 960, 60); cv.pop()
        # progress + cta
        cv.rect(80, 1760, 920, 8, fill=LINE, r=4); cv.rect(80, 1760, 920 * clamp(lt / dur), 8, fill=acc, r=4)
        cv.text("SISTEMAS OPERATIVOS / EXPLICADO", 540, 1700, 22, MUTED, "JetBrains Mono", 700, align="center")
        if end > 0:
            ep = ease_back(clamp((lt - (b - a)) / .6))
            cv.push(clamp(ep))
            cv.text("Video completo", 540, 820, 80, TXT, "Inter", 900, align="center")
            cv.text("en YouTube", 540, 920, 80, SEC, "Inter", 900, align="center")
            cv.text("Gestión de la memoria por el sistema operativo", 540, 1060, 30, MUTED, "Inter", 500, align="center")
            cv.pop()
    return f, dur, a

def square():
    def f(cv, t):
        background(cv, t)
        for (sa, sb, num, kick, head, acc) in SECTIONS:
            al = win(t, sa, sb, .35)
            if al <= 0: continue
            cv.push(al, dy=(1 - prog(t, sa, .5)) * 14)
            cv.text(f"{num} · {kick}", 540, 46, 22, acc if acc != TXT else SEC, "JetBrains Mono", 700, align="center")
            cv.text(head, 540, 84, 52, TXT, "Inter", 800, align="center")
            cv.pop()
        draw_content(cv, t, 50, 210, 980, 1)
        captions_big(cv, t, 540, 860, 980, 44, 34)
        cv.rect(60, 1040, 960, 6, fill=LINE, r=3); cv.rect(60, 1040, 960 * clamp(t / DURATION), 6, fill=SEC, r=3)
    return f

if __name__ == "__main__":
    kind, out, s0, s1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    if kind == "square":
        render(square(), DURATION, out, start=s0, end=s1, size=(1080, 1080))
    else:
        f, dur, a = vertical(kind)
        render(f, dur, out, start=s0, end=min(s1, dur), size=(1080, 1920))
