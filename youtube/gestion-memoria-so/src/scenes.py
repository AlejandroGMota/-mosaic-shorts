"""Gestión de la memoria por el SO — 16:9. Times (s) come from work/transcript.json (word-level)."""
import math, random
from engine import *
from fx import background, flow, pulse, captions

AUDIO_END = 178.4
DURATION = AUDIO_END + 3.0
PRI, SEC, WARN, OK = BLUE, FUC, AMBER, MINT
GRAY = hexrgb('475069')

def win(t, a, b, d=0.45):
    """Opacity of an element living in [a, b)."""
    return min(prog(t, a, d), 1 - prog(t, b - d, d))

# ---------- shared chrome ----------
SECTIONS = [  # (start, end, number, kicker, headline, accent)
    (0.0,   13.9,  "01", "INTRODUCCIÓN", "Gestión de la memoria", TXT),
    (13.9,  19.5,  "02", "TIPOS",        "Dos tipos de memoria", TXT),
    (19.5,  47.97, "03", "PRINCIPAL",    "Memoria principal: RAM y ROM", PRI),
    (47.97, 61.53, "04", "SECUNDARIA",   "Memoria secundaria", SEC),
    (61.53, 94.69, "05", "MMU",          "Direcciones: base y límite", PRI),
    (94.69, 117.24,"06", "ASIGNACIÓN",   "Particiones estáticas", PRI),
    (117.24,145.64,"07", "ASIGNACIÓN",   "Particiones dinámicas", PRI),
    (145.64,DURATION,"08","SEGMENTACIÓN", "Gestión por segmentación", PRI),
]

def chrome(cv, t):
    cv.text("SISTEMAS OPERATIVOS / EXPLICADO", 120, 62, 17, TXT, "JetBrains Mono", 700)
    cv.line(120, 104, 1800, 104, LINE, 1.5)
    cv.line(120, 1036, 1800, 1036, LINE, 1.5)
    w, _ = cv.text("PRINCIPAL", 120, 1046, 16, PRI, "JetBrains Mono", 700)
    cv.text("/ SECUNDARIA", 120 + w + 12, 1046, 16, SEC, "JetBrains Mono", 700)
    for (a, b, num, kick, head, acc) in SECTIONS:
        al = win(t, a, b, 0.35)
        if num == '01': al *= prog(t, 6.6, .5)
        if al <= 0: continue
        cv.push(al)
        cv.text(kick, 1800, 62, 15, acc if acc != TXT else MUTED, "JetBrains Mono", 700, align="right")
        cv.text(f"PARTE {num}", 1800, 1046, 15, MUTED, "JetBrains Mono", 700, align="right")
        dy = (1 - prog(t, a, 0.6)) * 18
        cv.text(num, 120, 142 + dy, 17, acc if acc != TXT else SEC, "JetBrains Mono", 700)
        cv.text(head, 120, 170 + dy, 52, TXT, "Inter", 800)
        cv.pop()

def tag(cv, s, x, y, col, al=1.0, size=18, align="left"):
    w, h = cv.measure(s, size, "JetBrains Mono", 700)
    px = x if align == "left" else x - (w + 28) / 2 if align == "center" else x - w - 28
    cv.rect(px, y, w + 28, h + 14, fill=with_a(col, 0.14 * al), stroke=with_a(col, al), lw=1.5, r=8)
    cv.text(s, px + 14, y + 7, size, with_a(col, al), "JetBrains Mono", 700)
    return w + 28

def block(cv, x, y, w, h, label, col, al=1.0, sub=None, size=22, fill_a=0.18):
    if al <= 0: return
    cv.rect(x, y, w, h, fill=with_a(col, fill_a * al), stroke=with_a(col, al), lw=2, r=8)
    if label:
        yy = y + h / 2 - (14 if sub else 0)
        cv.text(label, x + w / 2, yy, size, with_a(TXT, al), "Inter", 700, align="center", anchor_v="middle")
        if sub: cv.text(sub, x + w / 2, yy + 28, size - 6, with_a(MUTED, al), "JetBrains Mono", 500, align="center", anchor_v="middle")

def check(cv, x, y, col, p, s=14):
    if p <= 0: return
    c = cv.c; c.set_source_rgba(*col); c.set_line_width(4); c.set_line_cap(cairo.LINE_CAP_ROUND)
    pts = [(x - s, y), (x - s * .3, y + s * .7), (x + s, y - s * .8)]
    L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); d = (L1 + L2) * p
    c.move_to(*pts[0])
    if d <= L1: c.line_to(lerp(pts[0][0], pts[1][0], d / L1), lerp(pts[0][1], pts[1][1], d / L1))
    else:
        c.line_to(*pts[1]); q = (d - L1) / L2; c.line_to(lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))
    c.stroke()

def cross(cv, x, y, col, p, s=14):
    if p <= 0: return
    q1, q2 = clamp(p * 2), clamp(p * 2 - 1)
    cv.line(x - s, y - s, lerp(x - s, x + s, q1), lerp(y - s, y + s, q1), col, 4)
    if q2 > 0: cv.line(x + s, y - s, lerp(x + s, x - s, q2), lerp(y - s, y + s, q2), col, 4)

def table(cv, x, y, cols, rows, t, t_head, row_ts, col_w, accent, hl=None):
    """cols: headers; rows: list of list[str|(str,color)]; row_ts: appear time per row."""
    a = prog(t, t_head, 0.4)
    if a <= 0: return
    W = sum(col_w); cv.push(a)
    cv.rect(x, y, W, 44, fill=with_a(accent, 0.16), stroke=None, r=6)
    cx = x
    for h, w in zip(cols, col_w):
        cv.text(h, cx + 14, y + 12, 15, accent, "JetBrains Mono", 700); cx += w
    for i, (r, rt) in enumerate(zip(rows, row_ts)):
        ra = prog(t, rt, 0.35)
        if ra <= 0: continue
        ry = y + 50 + i * 42
        if hl and hl[0] == i: cv.rect(x, ry - 2, W, 40, fill=with_a(WARN, 0.18 * hl[1]), r=6)
        cv.line(x, ry + 40, x + W, ry + 40, with_a(LINE, ra), 1)
        cx = x
        for cell, w in zip(r, col_w):
            s, col = (cell, TXT) if isinstance(cell, str) else cell
            cv.text(s, cx + 14, ry + 9 + (1 - ra) * 8, 19, with_a(col, ra), "JetBrains Mono", 500); cx += w
    cv.pop()

# ---------- scenes ----------
def s_intro_title(cv, t):
    o = 1 - prog(t, 6.4, .6)
    if o <= 0: return
    rnd = random.Random(3)
    # memory cells filling behind the title
    for r in range(6):
        for c in range(24):
            x, y = 160 + c * 67, 250 + r * 92
            st = 0.2 + rnd.random() * 3.6
            p = prog(t, st, .5)
            col = PRI if rnd.random() < .7 else SEC
            cv.rect(x, y, 58, 80, fill=with_a(col, (.04 + .16 * p) * o), stroke=with_a(LINE, o), lw=1, r=5)
    cv.rect(0, 380, W, 330, fill=with_a(BG, .78 * o))
    words = ["Gestión", "de", "la", "memoria"]
    ws = [cv.measure(w, 110, "Inter", 900)[0] for w in words]; sp = 30
    x = W / 2 - (sum(ws) + sp * 3) / 2
    for i, (w, wd) in enumerate(zip(words, ws)):
        p = ease_back(clamp((t - (0.4 + i * .28)) / .6))
        cv.c.save(); cv.c.rectangle(0, 400, W, 150); cv.c.clip()
        cv.text(w, x, 420 + (1 - p) * 120, 110, with_a(SEC if w == "memoria" else TXT, o), "Inter", 900)
        cv.c.restore(); x += wd + sp
    u = prog(t, 1.8, 1.0, ease_io)
    cv.rect(W / 2 - 420 * u, 560, 840 * u, 4, fill=with_a(SEC, o), r=2)
    cv.text("por el sistema operativo", W / 2, 600, 36, with_a(MUTED, o * prog(t, 4.2, .6)), "Inter", 500, align="center")

def s_intro(cv, t):
    # libera (9.54) / asigna (10.52) / programas (12.44)
    s_intro_title(cv, t)
    x0, y0, W, H = 360, 520, 1200, 120
    a = prog(t, 6.6, 0.6)
    cv.push(a)
    cv.text("por el sistema operativo", 960, 300, 34, with_a(MUTED, prog(t, 5.3, 0.6)), "Inter", 500, align="center")
    cv.rect(x0, y0, W, H, fill=PANEL, stroke=LINE, lw=2, r=12)
    cv.text("MEMORIA", x0, y0 - 34, 16, MUTED, "JetBrains Mono", 700)
    block(cv, x0 + 10, y0 + 10, 160, H - 20, "S.O.", GRAY, 1, size=22)
    # an old block gets released
    rel = prog(t, 9.54, 0.7)
    block(cv, x0 + 180, y0 + 10, 300, H - 20, "P0", SEC, 1 - rel)
    if t > 9.3: tag(cv, "libera", x0 + 330, y0 + H + 30, SEC, prog(t, 9.54, .3) * (1 - prog(t, 12.6, .4)), align="center")
    # new ones get assigned
    for i, (lab, w) in enumerate([("P1", 220), ("P2", 260), ("P3", 300)]):
        st = 10.52 + i * 0.55
        p = ease_back(clamp((t - st) / .6))
        xs = x0 + 180 + sum([220, 260, 300][:i]) + i * 10
        block(cv, xs, y0 + 10 - (1 - p) * 140, w, H - 20, lab, PRI, clamp(p))
    if t > 10.3: tag(cv, "asigna", x0 + 640, y0 + H + 30, PRI, prog(t, 10.52, .3), align="center")
    if t > 12.4:
        cv.text("a los distintos programas", 960, 760, 26, with_a(TXT, prog(t, 12.44, .5)), "Inter", 600, align="center")
    cv.pop()

def s_types(cv, t):
    for (x, lab, col, st, sub) in [(220, "Memoria principal", PRI, 17.2, "RAM · ROM"), (1000, "Memoria secundaria", SEC, 18.3, "SSD · HDD")]:
        p = ease_back(clamp((t - st) / .7))
        if p <= 0: continue
        cv.push(clamp(p), dy=(1 - p) * 60)
        cv.rect(x, 360, 700, 440, fill=with_a(col, 0.08 + .05 * pulse(t, .6)), stroke=col, lw=2.5 + 1.5 * pulse(t, .6), r=18)
        cv.text(lab, x + 350, 540, 46, TXT, "Inter", 800, align="center")
        cv.text(sub, x + 350, 620, 24, col, "JetBrains Mono", 700, align="center")
        cv.pop()
    if t < 17.2:
        p = prog(t, 15.72, .5)
        cv.text("2", 960, 520, 220, with_a(TXT, p), "Inter", 900, align="center", anchor_v="middle")

def cells(cv, x, y, cols, rows, sz, gap, fills, col, al):
    for r in range(rows):
        for c in range(cols):
            f = fills.get((r, c), 0)
            cv.rect(x + c * (sz + gap), y + r * (sz + gap), sz, sz, fill=with_a(col, (0.05 + 0.55 * f) * al), stroke=with_a(col, 0.45 * al), lw=1.2, r=4)

def plug(cv, x, y, on, al):
    col = OK if on > 0.5 else RED
    cv.rect(x, y, 56, 34, fill=with_a(PANEL, al), stroke=with_a(col, al), lw=2, r=6)
    cv.line(x + 18, y - 12, x + 18, y, with_a(col, al), 4); cv.line(x + 38, y - 12, x + 38, y, with_a(col, al), 4)
    cv.text("⚡" if on > 0.5 else "OFF", x + 28, y + 17, 15, with_a(col, al), "JetBrains Mono", 700, align="center", anchor_v="middle")

def s_principal(cv, t):
    # RAM card (left) and ROM card (right)
    focusR = prog(t, 23.72, .5) * (1 - prog(t, 34.77, .5)); focusO = prog(t, 34.77, .5)
    for i, (x, lab, st, foc) in enumerate([(120, "RAM", 22.2, focusR), (980, "ROM", 23.04, focusO)]):
        p = prog(t, st, .5)
        if p <= 0: continue
        cv.push(p * (0.55 + 0.45 * max(foc, 1 - prog(t, 23.72, .5))))
        cv.rect(x, 290, 820, 620, fill=PANEL, stroke=with_a(PRI, 0.4 + 0.6 * foc), lw=2.5 + 2 * foc * pulse(t, .7), r=16)
        cv.text(lab, x + 40, 320, 44, TXT, "Inter", 800)
        cv.pop()
    # ---- RAM ----
    if t > 22.0:
        a = prog(t, 22.2, .5)
        gx, gy = 180, 430
        fill = {}
        fp = prog(t, 25.22, 1.6, ease_io)
        for k in range(32):
            if k / 32 < fp: fill[(k // 8, k % 8)] = 1
        off = prog(t, 33.5, .8)
        for k in fill: fill[k] *= (1 - off)
        cells(cv, gx, gy, 8, 4, 78, 10, fill, PRI, a)
        if t > 25.0: cv.text("datos del programa en ejecución", 180, 800, 20, with_a(MUTED, prog(t, 25.66, .4) * a), "JetBrains Mono", 500)
        # random access
        if 28.3 < t < 33.6:
            rnd = random.Random(7); seq = [(rnd.randrange(4), rnd.randrange(8)) for _ in range(8)]
            k = int((t - 28.46) / 0.32)
            if 0 <= k < len(seq):
                r, c = seq[k]
                cv.rect(gx + c * 88 - 4, gy + r * 88 - 4, 86, 86, stroke=TXT, lw=3, r=6)
            tag(cv, "acceso aleatorio", 180, 850, PRI, prog(t, 28.46, .3) * (1 - prog(t, 31.0, .3)))
        plug(cv, 820, 330, 0 if t > 33.3 else 1, prog(t, 31.16, .4))
        if t > 31.0:
            tag(cv, "volátil", 180, 850, RED, prog(t, 31.74, .3))
            if t > 33.0: cross(cv, 848, 312, RED, prog(t, 33.3, .4))
    # ---- ROM ----
    if t > 23.0:
        a = prog(t, 23.04, .5)
        gx, gy = 1040, 430
        fill = {(r, c): 1 for r in range(4) for c in range(8)}
        cells(cv, gx, gy, 8, 4, 78, 10, fill, PRI, a * (0.45 + 0.55 * focusO))
        if t > 36.0:
            tag(cv, "solo lectura", 1040, 800, PRI, prog(t, 36.08, .3))
        if t > 37.8:
            tag(cv, "firmware de arranque", 1260, 800, PRI, prog(t, 37.96, .3))
        # boot progress
        if t > 39.8:
            bp = prog(t, 40.04, 2.4, ease_io)
            cv.rect(1040, 860, 700, 14, fill=LINE, r=7); cv.rect(1040, 860, 700 * bp, 14, fill=OK, r=7)
            cv.text("arranque", 1040, 884, 16, MUTED, "JetBrains Mono", 500)
            for i, comp in enumerate(["CPU", "RAM", "Disco"]):
                st = 41.54 + i * 0.5
                xx = 1240 + i * 170
                cv.text(comp, xx, 884, 16, with_a(TXT, prog(t, st, .3)), "JetBrains Mono", 700)
                check(cv, xx + 80, 893, OK, prog(t, st + .15, .35), 8)
        plug(cv, 1680, 330, 0 if t > 45.6 else 1, prog(t, 43.84, .4))
        if t > 45.4:
            cross(cv, 1708, 312, RED, prog(t, 45.6, .4))
            tag(cv, "no volátil", 1500, 336, OK, prog(t, 46.68, .3))

def disk(cv, x, y, lab, col, al):
    cv.rect(x, y, 260, 170, fill=with_a(col, 0.12 * al), stroke=with_a(col, al), lw=2.5, r=14)
    cv.text(lab, x + 130, y + 85, 34, with_a(TXT, al), "Inter", 800, align="center", anchor_v="middle")

def s_secundaria(cv, t):
    a = prog(t, 49.3, .5)
    cv.push(a)
    cv.rect(120, 300, 760, 610, fill=PANEL, stroke=SEC, lw=2.5 + 1.5 * pulse(t, .6) * (1 - prog(t, 57.5, .4)), r=16)
    cv.text("SECUNDARIA", 160, 330, 18, SEC, "JetBrains Mono", 700)
    disk(cv, 170, 400, "SSD", SEC, prog(t, 54.65, .5))
    disk(cv, 470, 400, "HDD", SEC, prog(t, 56.23, .5))
    for i, f in enumerate(["app.exe", "fotos/", "doc.pdf", "juego/"]):
        p = prog(t, 51.19 + i * 0.25, .4)
        tag(cv, f, 170 + (i % 2) * 300, 640 + (i // 2) * 70, SEC, p, 17)
    tag(cv, "permanente", 170, 820, OK, prog(t, 52.59, .3))
    cv.pop()
    # RAM on the right
    r = prog(t, 57.47, .5)
    cv.push(r)
    cv.rect(1040, 300, 760, 610, fill=PANEL, stroke=PRI, lw=2.5 + 1.5 * pulse(t, .6) * prog(t, 59.5, .4), r=16)
    cv.text("PRINCIPAL · RAM", 1080, 330, 18, PRI, "JetBrains Mono", 700)
    cells(cv, 1090, 420, 8, 4, 74, 8, {}, PRI, 1)
    cv.pop()
    # program travels disk -> RAM
    if t > 57.9:
        p = prog(t, 59.27, 1.4, ease_io)
        x = lerp(170, 1090, p); y = lerp(640, 420 + 82, p)
        block(cv, x, y, 230, 72, "app.exe", lerp(0, 1, 1) and (PRI if p > .5 else SEC), prog(t, 57.93, .3), size=20, fill_a=.3)
        cv.arrow(890, 610, 1030, 610, with_a(TXT, .6 * prog(t, 59.0, .4)), 3, prog(t, 59.0, .6))
        flow(cv, 890, 610, 1020, 610, t, SEC, prog(t, 59.6, .4), n=3, speed=.9)

def s_mmu(cv, t):
    # CPU -> MMU (base + límite) -> RAM physical addresses
    a = prog(t, 61.67, .5)
    cv.push(a)
    block(cv, 140, 430, 230, 150, "Proceso", GRAY, 1, sub="dir. lógica", size=26)
    # MMU
    cv.rect(560, 360, 520, 300, fill=with_a(PRI, .06 + .05 * pulse(t, .5)), stroke=PRI, lw=2.5 + 1.5 * pulse(t, .5), r=16)
    cv.text("MMU", 820, 395, 40, TXT, "Inter", 800, align="center")
    cv.text("Memory Management Unit", 820, 450, 17, MUTED, "JetBrains Mono", 500, align="center")
    cv.pop()
    # RAM column
    rp = prog(t, 69.83, .5)
    RX, RY, RW, RH = 1360, 230, 300, 670
    cv.push(rp)
    cv.rect(RX, RY, RW, RH, fill=PANEL, stroke=PRI, lw=2.5, r=10)
    cv.text("RAM", RX + RW / 2, RY - 40, 20, PRI, "JetBrains Mono", 700, align="center")
    for i, adr in enumerate(["0", "25600", "30004", "42094", "88000", "102400"]):
        yy = RY + [0, .2, .3, .42, .8, 1][i] * RH
        cv.line(RX - 14, yy, RX, yy, MUTED, 1.5)
        cv.text(adr, RX - 22, yy, 15, MUTED, "JetBrains Mono", 500, align="right", anchor_v="middle")
    block(cv, RX + 8, RY + 6, RW - 16, .2 * RH - 12, "S.O.", GRAY, 1, size=20)
    cv.text("direcciones físicas", RX + RW / 2, RY + RH + 18, 16, MUTED, "JetBrains Mono", 500, align="center")
    cv.pop()
    # process block placed at base 30004
    by0, by1 = RY + .3 * RH, RY + .42 * RH
    pb = prog(t, 74.35, .6)
    block(cv, RX + 8, by0 + 3, RW - 16, by1 - by0 - 6, "proceso", PRI, pb, size=20, fill_a=.3)
    # registers inside MMU
    br = prog(t, 74.35, .4)
    cv.push(br)
    cv.rect(600, 500, 210, 120, fill=PANEL, stroke=with_a(PRI, .5 + .5 * prog(t, 86.41, .3) * (1 - prog(t, 90.5, .3))), lw=2.5, r=10)
    cv.text("registro base", 705, 520, 15, MUTED, "JetBrains Mono", 700, align="center")
    cv.text("30004", 705, 570, 34, PRI, "JetBrains Mono", 700, align="center", anchor_v="middle")
    cv.pop()
    lr = prog(t, 90.85, .4)
    cv.push(lr)
    cv.rect(830, 500, 210, 120, fill=PANEL, stroke=WARN, lw=2.5, r=10)
    cv.text("registro límite", 935, 520, 15, MUTED, "JetBrains Mono", 700, align="center")
    cv.text("12090", 935, 570, 34, WARN, "JetBrains Mono", 700, align="center", anchor_v="middle")
    cv.pop()
    # limit bracket on RAM
    if lr > 0:
        cv.line(RX + RW + 20, by0, RX + RW + 20, lerp(by0, by1, lr), WARN, 3)
        cv.line(RX + RW + 12, by0, RX + RW + 28, by0, WARN, 3); cv.line(RX + RW + 12, by1, RX + RW + 28, by1, with_a(WARN, lr), 3)
        cv.text("límite", RX + RW + 36, (by0 + by1) / 2, 16, with_a(WARN, lr), "JetBrains Mono", 700, anchor_v="middle")
    # base reference arrow
    if t > 87.9:
        cv.arrow(810, 560, RX - 30, by0, with_a(PRI, .9), 3, prog(t, 88.11, .7))
        flow(cv, 810, 560, RX - 30, by0, t, PRI, prog(t, 88.9, .4), n=4, speed=.7)
    # byte zoom (78.31 - 81.5)
    z = win(t, 78.31, 81.6, .3)
    if z > 0:
        cv.push(z)
        cv.rect(560, 700, 520, 150, fill=PANEL, stroke=LINE, lw=2, r=12)
        cv.text("cada byte = 1 dirección", 820, 714, 16, MUTED, "JetBrains Mono", 700, align="center")
        for i in range(5):
            cv.rect(580 + i * 98, 760, 88, 64, fill=with_a(PRI, .15), stroke=PRI, lw=1.5, r=6)
            cv.text(str(30004 + i), 624 + i * 98, 792, 15, TXT, "JetBrains Mono", 500, align="center", anchor_v="middle")
        cv.pop()
    # translation: logical 256 + base -> 30260, check < limit
    if t > 92.5:
        p = prog(t, 92.99, .5)
        cv.push(p)
        cv.rect(560, 700, 520, 150, fill=PANEL, stroke=PRI, lw=2, r=12)
        cv.text("lógica 256  <  12090", 820, 728, 20, TXT, "JetBrains Mono", 700, align="center")
        check(cv, 1050, 742, OK, prog(t, 93.3, .4), 10)
        cv.text("30004 + 256 = 30260", 820, 790, 28, PRI, "JetBrains Mono", 700, align="center")
        cv.pop()
        yy = lerp(by0, by1, 256 / 12090 * 8 + .1)
        cv.arrow(1080, 790, RX + 4, yy, with_a(OK, p), 3, prog(t, 93.4, .6))
        flow(cv, 1080, 790, RX + 4, yy, t, OK, prog(t, 94.0, .3), n=3, speed=.9)
    # logical address travels CPU -> MMU
    if t > 63.8:
        p = prog(t, 64.23, 1.0, ease_io) * (1 - prog(t, 67.6, .3))
        cv.arrow(380, 505, 550, 505, with_a(TXT, .7), 3, prog(t, 64.0, .5))
        flow(cv, 380, 505, 545, 505, t, TXT, prog(t, 64.6, .4), n=3, speed=.8)
        if p > 0: tag(cv, "256", lerp(390, 470, p), 452, TXT, p, 17)

MEM_X, MEM_Y, MEM_W, MEM_H = 140, 330, 1640, 150
def membar(cv, al, label="MEMORIA PRINCIPAL"):
    cv.rect(MEM_X, MEM_Y, MEM_W, MEM_H, fill=with_a(PANEL, al), stroke=with_a(LINE, al), lw=2, r=12)
    cv.text(label, MEM_X, MEM_Y - 32, 16, with_a(MUTED, al), "JetBrains Mono", 700)

def s_static(cv, t):
    a = prog(t, 99.6, .5)
    if t < 99.9:
        cv.text("¿Cómo se asigna espacio a los procesos?", 960, 560, 40, with_a(TXT, prog(t, 95.0, .5)), "Inter", 700, align="center")
        return
    cv.push(a)
    membar(cv, 1, "MEMORIA PRINCIPAL · 1024 KB")
    parts = [("S.O.", 64, GRAY), ("Partición 1", 512, PRI), ("Partición 2", 256, PRI), ("Partición 3", 128, PRI), ("P4", 64, PRI)]
    scale = (MEM_W - 20) / 1024; x = MEM_X + 10
    xs = []
    for i, (lab, kb, col) in enumerate(parts):
        w = kb * scale
        pe = ease_back(clamp((t - (102.6 + i * 0.25)) / .5)); p = clamp(pe)
        block(cv, x + 2, MEM_Y + 10 + (1 - pe) * 50, w - 4, MEM_H - 20, "" if (i == 1 and t > 104.5) else lab, col, p, sub=f"{kb} KB" if prog(t, 107.48, .3) > 0 or i == 0 else None, size=20, fill_a=.08)
        xs.append((x, w)); x += w
    # process C 128 KB into partition 1 -> 384 KB wasted
    px, pw = xs[1]
    pp = prog(t, 104.5, .6)
    if pp > 0:
        block(cv, px + 6, MEM_Y + 16 - (1 - pp) * 120, 128 * scale - 8, MEM_H - 32, "Proceso C", SEC, pp, sub="128 KB", size=19, fill_a=.35)
    wa = prog(t, 106.0, .5) * (.7 + .3 * pulse(t, .8))
    if wa > 0:
        cv.rect(px + 128 * scale + 2, MEM_Y + 16, pw - 128 * scale - 10, MEM_H - 32, fill=with_a(WARN, .15 * wa), stroke=with_a(WARN, wa), lw=2, r=6)
        cv.text("384 KB sin usar", px + 128 * scale + (pw - 128 * scale) / 2, MEM_Y + MEM_H / 2, 18, with_a(WARN, wa), "JetBrains Mono", 700, align="center", anchor_v="middle")
        cv.text("fragmentación interna", px + pw / 2, MEM_Y + MEM_H + 16, 16, with_a(WARN, wa), "JetBrains Mono", 700, align="center")
    st = 113.68; sp = 115.24
    rows = [["1", "512 KB", ("ocupada", SEC) if t > st else "", "Proceso C" if t > sp else ""],
            ["2", "256 KB", ("libre", OK) if t > st else "", "—" if t > sp else ""],
            ["3", "128 KB", ("libre", OK) if t > st else "", "—" if t > sp else ""],
            ["4", "64 KB",  ("libre", OK) if t > st else "", "—" if t > sp else ""]]
    table(cv, 420, 590, ["PARTICIÓN", "TAMAÑO", "ESTADO", "PROCESO"], rows, t, 110.5, [110.9, 111.2, 111.5, 111.8], [240, 240, 280, 320], PRI)
    cv.pop()

def s_dynamic(cv, t):
    a = prog(t, 117.4, .5)
    cv.push(a)
    membar(cv, 1, "MEMORIA PRINCIPAL")
    scale = (MEM_W - 20) / 200.0
    x0 = MEM_X + 10
    upd = prog(t, 141.48, .6)          # J2 finishes, J4 enters the hole
    jobs = [("S.O.", 30, GRAY, 0), ("J1", 20, PRI, 120.34), ("J2", 40, PRI, 120.7), ("J3", 50, PRI, 121.06)]
    x = x0
    for lab, kb, col, st in jobs:
        w = kb * scale; p = prog(t, st, .5) if st else 1
        if lab == "J2": p *= (1 - upd)
        block(cv, x - (1 - prog(t, st, .5)) * 200 * (st > 0) + 2, MEM_Y + 10, w - 4, MEM_H - 20, lab, col, p, sub=f"{kb}K", size=20, fill_a=.22)
        if lab == "J2" and upd > 0:
            cv.rect(x + 2, MEM_Y + 10, w - 4, MEM_H - 20, fill=None, stroke=with_a(WARN, upd), lw=2, r=8)
            block(cv, x + 2, MEM_Y + 10, 20 * scale - 4, MEM_H - 20, "J4", SEC, prog(t, 142.7, .5), sub="20K", size=20, fill_a=.35)
        x += w
    free_x = x
    cv.rect(free_x + 2, MEM_Y + 10, MEM_X + MEM_W - 10 - free_x - 4, MEM_H - 20, fill=None, stroke=with_a(OK, prog(t, 136.6, .4)), lw=2, r=8)
    cv.text("libre", (free_x + MEM_X + MEM_W) / 2, MEM_Y + MEM_H / 2, 20, with_a(OK, prog(t, 136.6, .4)), "JetBrains Mono", 700, align="center", anchor_v="middle")
    tag(cv, "consecutivos → sin huecos", MEM_X, MEM_Y + MEM_H + 16, PRI, prog(t, 122.5, .4) * (1 - prog(t, 125.2, .3)), 16)
    u = t > 143.2
    rows = [["J1", "30K", "20K", ("activo", OK)],
            ["J2", "50K", "40K", ("terminado", WARN) if u else ("activo", OK)],
            ["J3", "90K", "50K", ("activo", OK)]]
    if u: rows.append(["J4", "50K", "20K", ("activo", SEC)])
    table(cv, 140, 600, ["ID", "BASE", "TAMAÑO", "ESTADO"], rows, t, 127.22,
          [128.36, 128.6, 128.84, 143.2], [130, 150, 170, 220], PRI, hl=(1, prog(t, 143.84, .3)) if u else None)
    frows = [["140K", "60K"]] + ([["70K", "20K"]] if u else [])
    table(cv, 1100, 600, ["BASE LIBRE", "TAMAÑO"], frows, t, 136.0, [138.96, 143.5], [300, 260], OK)
    if t > 132.6:
        cv.text("+ bloque de control del proceso (PCB)", 140, 905, 17, with_a(MUTED, prog(t, 133.42, .4)), "JetBrains Mono", 500)
    cv.pop()

SEGS = [("Código", PRI, 156.74), ("Pila", OK, 157.82), ("Datos", SEC, 158.9)]
def s_segment(cv, t):
    if t < 148.0:
        p = prog(t, 145.7, .5)
        cv.text("Segmentación", 960, 540, 90, with_a(TXT, p), "Inter", 900, align="center", anchor_v="middle")
        return
    a = prog(t, 148.0, .5)
    cv.push(a)
    # process (left)
    split = prog(t, 153.74, .7, ease_io)
    PX, PY, PW = 160, 330, 300
    hs = [170, 120, 150]
    cv.text("PROCESO", PX, PY - 34, 16, MUTED, "JetBrains Mono", 700)
    y = PY
    for i, ((lab, col, st), h) in enumerate(zip(SEGS, hs)):
        lit = prog(t, st, .3)
        block(cv, PX, y + i * 24 * split, PW, h, lab if split > .2 else "", col if split > .05 else GRAY, 1, size=24, fill_a=.12 + .25 * lit)
        y += h
    # memory (right), non-contiguous
    MX, MY, MW, MH = 1340, 260, 420, 680
    mp = prog(t, 150.2, .5)
    cv.push(mp)
    cv.rect(MX, MY, MW, MH, fill=PANEL, stroke=PRI, lw=2.5, r=10)
    cv.text("MEMORIA", MX, MY - 34, 16, MUTED, "JetBrains Mono", 700)
    block(cv, MX + 10, MY + 10, MW - 20, 90, "S.O.", GRAY, 1, size=20)
    block(cv, MX + 10, MY + 380, MW - 20, 80, "otro proceso", GRAY, 1, size=18)
    cv.pop()
    # MMU in middle
    mm = prog(t, 155.7, .4)
    cv.push(mm)
    cv.rect(760, 520, 260, 130, fill=with_a(PRI, .06 + .05 * pulse(t, .5)), stroke=PRI, lw=2.5 + 1.5 * pulse(t, .5), r=14)
    cv.text("MMU", 890, 585, 36, TXT, "Inter", 800, align="center", anchor_v="middle")
    cv.pop()
    if t > 156.0:
        fa = prog(t, 156.0, .5)
        cv.line(PX + PW + 10, 520, 750, 585, with_a(LINE, fa), 2); cv.line(1030, 585, MX - 10, 450, with_a(LINE, fa), 2)
        flow(cv, PX + PW + 10, 520, 750, 585, t, PRI, fa, n=3, speed=.7); flow(cv, 1030, 585, MX - 10, 450, t, PRI, fa, n=3, speed=.7)
    dest = {"Código": MY + 115, "Pila": MY + 475, "Datos": MY + 250}
    hmap = {"Código": 125, "Pila": 80, "Datos": 110}
    freed = prog(t, 168.24, .7)
    for (lab, col, st), h in zip(SEGS, hs):
        p = prog(t, st + .2, 1.0, ease_io)
        if p <= 0: continue
        al = 1.0
        if lab == "Pila": al = 1 - freed
        x = lerp(PX + 40, MX + 10, p); y = lerp(PY + 60, dest[lab], p); w = lerp(PW - 80, MW - 20, p)
        block(cv, x, y, w, hmap[lab], lab, col, al * prog(t, st, .3), size=20, fill_a=.3)
    # smaller than a partition
    if 159.5 < t < 167.9:
        b = win(t, 160.52, 167.9, .3)
        cv.line(MX - 30, MY + 110, MX - 30, MY + 470, with_a(WARN, b), 3)
        cv.text("1 partición", MX - 40, MY + 290, 17, with_a(WARN, b), "JetBrains Mono", 700, align="right", anchor_v="middle")
        cv.text("→ segmentos más pequeños", MX - 40, MY + 320, 17, with_a(TXT, prog(t, 166.4, .4) * b), "JetBrains Mono", 500, align="right", anchor_v="middle")
    if t > 168.0:
        tag(cv, "se libera solo un segmento", 560, 760, OK, prog(t, 168.24, .4), 18)
        check(cv, 1290, 800, OK, prog(t, 170.38, .4), 12) if False else None
        cv.text("el resto del proceso sigue en memoria", 560, 830, 18, with_a(MUTED, prog(t, 169.68, .4)), "JetBrains Mono", 500)
    # waiting segment takes the freed space
    if t > 173.0:
        p = prog(t, 176.66, 1.1, ease_io)
        x = lerp(760, MX + 10, p); y = lerp(880, MY + 475, p)
        block(cv, x, y, lerp(240, MW - 20, p), 80, "segmento en espera", WARN, prog(t, 173.3, .4), size=18, fill_a=.3)
        if p < .05: cv.text("COLA", 760, 850, 15, with_a(WARN, prog(t, 173.3, .4)), "JetBrains Mono", 700)
    cv.pop()

def s_outro(cv, t):
    a = prog(t, AUDIO_END + .2, .6)
    items = [("Principal", PRI), ("Secundaria", SEC), ("MMU", PRI), ("Estáticas", PRI), ("Dinámicas", PRI), ("Segmentación", PRI)]
    x = 960 - (len(items) * 250) / 2
    for i, (s, c) in enumerate(items):
        tag(cv, s, x + i * 250 + 125, 560, c, a * prog(t, AUDIO_END + .3 + i * .12, .4), 20, align="center")

SCENES = [(0.0, 13.9, s_intro), (13.9, 19.5, s_types), (19.5, 47.97, s_principal), (47.97, 61.53, s_secundaria),
          (61.53, 94.69, s_mmu), (94.69, 117.24, s_static), (117.24, 145.64, s_dynamic), (145.64, AUDIO_END, s_segment),
          (AUDIO_END, DURATION + 1, s_outro)]

def content(cv, t):
    for a, b, fn in SCENES:
        al = win(t, a, b, .45)
        if al <= 0: continue
        enter = ease_out(clamp((t - a) / .7)); leave = ease_io(clamp((t - (b - .45)) / .45))
        zoom = 1 + 0.018 * clamp((t - a) / max(b - a, 1))
        cv.push(al, dx=(1 - enter) * 60 - leave * 60, scale=zoom, cx=960, cy=620); fn(cv, t); cv.pop()

def frame(cv, t):
    background(cv, t)
    chrome(cv, t)
    content(cv, t)
    captions(cv, t)
