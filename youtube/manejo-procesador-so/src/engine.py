"""Minimal 2D motion engine: cairo + pango -> raw frames -> ffmpeg.
Free deps only: cairocffi, pangocffi, pangocairocffi, numpy, ffmpeg."""
import math, subprocess, os
import cairocffi as cairo
import pangocffi, pangocairocffi as pc

W, H, FPS = 1920, 1080, 25

def hexrgb(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255, a)

# Palette
BG    = hexrgb('05070d'); PANEL = hexrgb('0c1120'); LINE = hexrgb('1c2440')
TXT   = hexrgb('e8ecf6'); MUTED = hexrgb('7a86a8')
BLUE  = hexrgb('3b82f6'); FUC = hexrgb('ec4899'); MINT = hexrgb('34d399')
AMBER = hexrgb('f59e0b'); RED = hexrgb('ef4444')

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x + 2) ** 3 / 2
def prog(t, start, dur=0.5, ease=ease_out): return ease((t - start) / dur) if dur > 0 else float(t >= start)
def lerp(a, b, p): return a + (b - a) * p
def mix(c1, c2, p): return tuple(lerp(a, b, p) for a, b in zip(c1, c2))
def with_a(c, a): return (c[0], c[1], c[2], c[3] * a)

class Canvas:
    def __init__(self, w=None, h=None):
        self.w, self.h = (w or W), (h or H)
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        self.c = cairo.Context(self.surf)
    def clear(self, col=BG):
        self.c.set_source_rgba(*col); self.c.paint()
    def rect(self, x, y, w, h, fill=None, stroke=None, lw=2, r=10):
        c = self.c; c.new_path()
        if r > 0:
            r = min(r, w/2, h/2)
            c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
            c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 3*math.pi/2); c.close_path()
        else: c.rectangle(x, y, w, h)
        if fill: c.set_source_rgba(*fill); c.fill_preserve() if stroke else c.fill()
        if stroke: c.set_source_rgba(*stroke); c.set_line_width(lw); c.stroke()
    def line(self, x1, y1, x2, y2, col, lw=2, dash=None):
        c = self.c; c.set_source_rgba(*col); c.set_line_width(lw)
        c.set_dash(dash or []); c.move_to(x1, y1); c.line_to(x2, y2); c.stroke(); c.set_dash([])
    def arrow(self, x1, y1, x2, y2, col, lw=3, p=1.0, head=14):
        if p <= 0: return
        xe, ye = lerp(x1, x2, p), lerp(y1, y2, p)
        self.line(x1, y1, xe, ye, col, lw)
        ang = math.atan2(y2 - y1, x2 - x1); c = self.c
        c.set_source_rgba(*col); c.move_to(xe, ye)
        c.line_to(xe - head*math.cos(ang - .45), ye - head*math.sin(ang - .45))
        c.line_to(xe - head*math.cos(ang + .45), ye - head*math.sin(ang + .45)); c.close_path(); c.fill()
    def circle(self, x, y, r, fill=None, stroke=None, lw=2):
        c = self.c; c.new_path(); c.arc(x, y, r, 0, 2*math.pi)
        if fill: c.set_source_rgba(*fill); c.fill_preserve() if stroke else c.fill()
        if stroke: c.set_source_rgba(*stroke); c.set_line_width(lw); c.stroke()
    def text(self, s, x, y, size=32, col=TXT, font="Inter", weight=400, align="left",
             width=None, spacing=0, anchor_v="top", markup=False):
        """Draw text; returns (w, h). align: left/center/right relative to x."""
        c = self.c; l = pc.create_layout(c)
        fd = pangocffi.FontDescription(); fd.family = font
        fd.weight = pangocffi.Weight(weight); fd.size = pangocffi.units_from_double(size)
        l.font_description = fd
        if width: l.width = pangocffi.units_from_double(width); l.alignment = {"left": pangocffi.Alignment.LEFT, "center": pangocffi.Alignment.CENTER, "right": pangocffi.Alignment.RIGHT}[align]
        if markup: l.apply_markup(s)
        else: l.text = s
        _, log = l.get_extents()
        w, h = pangocffi.units_to_double(log.width), pangocffi.units_to_double(log.height)
        ox = x
        if not width:
            if align == "center": ox = x - w/2
            elif align == "right": ox = x - w
        else:
            if align == "center": ox = x - width/2
            elif align == "right": ox = x - width
        oy = y - (h/2 if anchor_v == "middle" else h if anchor_v == "bottom" else 0)
        c.save(); c.move_to(ox, oy); c.set_source_rgba(*col); pc.show_layout(c, l); c.restore()
        return w, h
    def measure(self, s, size=32, font="Inter", weight=400):
        l = pc.create_layout(self.c); fd = pangocffi.FontDescription(); fd.family = font
        fd.weight = pangocffi.Weight(weight); fd.size = pangocffi.units_from_double(size); l.font_description = fd; l.text = s
        _, log = l.get_extents(); return pangocffi.units_to_double(log.width), pangocffi.units_to_double(log.height)
    def push(self, alpha=1.0, dx=0, dy=0, scale=1.0, cx=W/2, cy=H/2):
        c = self.c; c.save(); c.translate(dx, dy)
        if scale != 1.0: c.translate(cx, cy); c.scale(scale, scale); c.translate(-cx, -cy)
        c.push_group(); self._alpha = getattr(self, '_alpha', []); self._alpha.append(alpha)
    def pop(self):
        c = self.c; a = self._alpha.pop(); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
    def bgra(self):
        self.surf.flush(); return bytes(self.surf.get_data())

def render(scene_fn, duration, out_path, audio=None, start=0.0, end=None, crf=18, size=None):
    end = duration if end is None else end
    w, h = size or (W, H)
    n0, n1 = int(round(start*FPS)), int(round(end*FPS))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cv = Canvas(w, h)
    for f in range(n0, n1):
        cv.clear(); scene_fn(cv, f / FPS); p.stdin.write(cv.bgra())
    p.stdin.close(); p.wait()

def still(scene_fn, t, path):
    cv = Canvas(); cv.clear(); scene_fn(cv, t); cv.surf.write_to_png(path)

def ease_back(x, s=1.4):
    x = clamp(x); x -= 1; return 1 + x * x * ((s + 1) * x + s)
