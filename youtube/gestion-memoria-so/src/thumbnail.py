"""YouTube thumbnail 1280x720."""
import math, random
from engine import *
from fx import background
PRI = BLUE

def thumb(path):
    cv = Canvas(1280, 720); cv.clear(BG); background(cv, 0)
    c = cv.c
    # glow behind the memory stack
    g = cairo.RadialGradient(980, 360, 20, 980, 360, 420)
    g.add_color_stop_rgba(0, .93, .28, .6, .28); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.paint()
    # memory stack (right)
    X, Y, Wd = 820, 70, 330
    cv.rect(X - 14, Y - 14, Wd + 28, 562, fill=PANEL, stroke=PRI, lw=4, r=18)
    blocks = [("S.O.", 90, hexrgb('475069')), ("Código", 120, PRI), ("", 30, None), ("Datos", 100, FUC), ("Pila", 70, MINT), ("", 40, None), ("P2", 92, PRI)]
    y = Y
    for lab, h, col in blocks:
        if col is None:
            cv.rect(X, y, Wd, h - 8, fill=with_a(AMBER, .12), stroke=AMBER, lw=3, r=8)
            c.set_dash([10, 8]); cv.rect(X, y, Wd, h - 8, stroke=AMBER, lw=3, r=8); c.set_dash([])
        else:
            cv.rect(X, y, Wd, h - 8, fill=with_a(col, .35), stroke=col, lw=4, r=10)
            cv.text(lab, X + Wd / 2, y + (h - 8) / 2, 34, TXT, "Inter", 800, align="center", anchor_v="middle")
        y += h
    # title (left)
    cv.text("¿CÓMO EL SO", 60, 70, 66, TXT, "Inter", 900)
    cv.text("GESTIONA LA", 60, 150, 66, TXT, "Inter", 900)
    cv.text("MEMORIA?", 54, 230, 100, FUC, "Inter", 900)
    cv.rect(62, 368, 420, 10, fill=FUC, r=5)
    for i, s in enumerate(["RAM · ROM", "PARTICIONES", "SEGMENTACIÓN"]):
        w, h = cv.measure(s, 28, "JetBrains Mono", 700)
        yy = 420 + i * 78
        cv.rect(60, yy, w + 36, h + 18, fill=with_a(PRI, .18), stroke=PRI, lw=3, r=10)
        cv.text(s, 78, yy + 9, 28, TXT, "JetBrains Mono", 700)
    cv.surf.write_to_png(path)

if __name__ == "__main__":
    thumb("../miniatura_youtube.png")
