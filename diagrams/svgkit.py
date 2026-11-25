"""svgkit: a tiny helper for the README diagrams. Standard library only.

Use from a script in this directory (run as `python3 diagrams/<name>.py`;
the script directory is already on sys.path, so `from svgkit import *` works).

    from svgkit import Canvas, T
    c = Canvas(1600, 900, "Title", "Long description for screen readers")
    c.text(800, 60, "Heading", size=44, weight="bold", anchor="middle")
    c.box(40, 100, 300, 200, stroke=T["you"], fill=T["panel"])      # rounded box
    c.wrapped(60, 140, "a long line that is wrapped by itself", 270, size=22)
    c.arrow([(100, 300), (100, 360), (400, 360), (400, 420)])       # polyline + head
    c.pill(60, 500, "/dmtix go", color=T["you"])                    # mono label
    c.legend(1300, 40)                                              # you / agents
    c.save("skills/dmtix/dmtix.svg")                                # paths: repo root

Functions (all coordinates in px, y grows downward; every call appends one
element, so z-order is call order):
  Canvas(w, h, title, desc)         creates <title> and <desc> and a white page
  c.text(x, y, s, size=22, weight="normal", fill=T["ink"], anchor="start",
         mono=False)                 one line; y is the baseline; returns y
  c.lines(x, y, lines, size, lh=None, **kw)   several lines; returns next y
  c.wrapped(x, y, s, width, size=22, lh=None, **kw)
                                     wraps s to width px (estimate), returns next y
  c.box(x, y, w, h, stroke, fill, rx=14, sw=2, dash=None)
  c.arrow(points, color=T["agent"], sw=3, dash=None, head=True)
  c.pill(x, y, s, color, size=22, mono=True)   rounded tag; returns its width
  c.legend(x, y)                     "you" (accent) and "agents" (grey)
  c.save(path)                       writes the file with a trailing newline
Output is deterministic: no timestamps, no random ids.
Theme T: light palette. you = accent orange, agents = grey/black.
"""
import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

T = {
    "bg": "#ffffff", "ink": "#222222", "strong": "#111111", "muted": "#55555a",
    "you": "#b45309",        # text and lines for what the human does
    "you_fill": "#e68e0d",   # accent fill (dots, tints)
    "you_tint": "#fdf3e3",
    "agent": "#555555", "agent_dark": "#222222",
    "panel": "#f7f7f7", "panel2": "#f2f2f2", "line": "#b0b0b0", "dash": "#8a8a8a",
    "sans": "Calibri, 'Liberation Sans', Arial, sans-serif",
    "mono": "Consolas, 'JetBrainsMono NF', 'Liberation Mono', monospace",
}
CHAR = 0.52  # average glyph width / font size for the sans stack (safe side)
MONO = 0.62


def _n(v):
    return str(int(v)) if float(v) == int(v) else ("%.1f" % v)


class Canvas:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.out = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"'
            ' role="img" font-family="%s" fill="%s">' % (w, h, w, h, T["sans"], T["ink"]),
            "<title>%s</title>" % escape(title),
            "<desc>%s</desc>" % escape(desc),
            '<rect width="%d" height="%d" fill="%s"/>' % (w, h, T["bg"]),
        ]

    def text(self, x, y, s, size=22, weight="normal", fill=None, anchor="start", mono=False):
        a = ' font-size="%s"' % _n(size)
        if weight != "normal":
            a += ' font-weight="%s"' % weight
        if anchor != "start":
            a += ' text-anchor="%s"' % anchor
        if mono:
            a += ' font-family="%s"' % T["mono"]
        if fill:
            a += ' fill="%s"' % fill
        self.out.append('<text x="%s" y="%s"%s>%s</text>' % (_n(x), _n(y), a, escape(s.replace(" ", "\u00a0") if s.startswith(" ") else s)))
        return y

    def lines(self, x, y, lines, size=22, lh=None, **kw):
        lh = lh or round(size * 1.35)
        for s in lines:
            self.text(x, y, s, size=size, **kw)
            y += lh
        return y

    def wrapped(self, x, y, s, width, size=22, lh=None, **kw):
        per = max(4, int(width / (size * (MONO if kw.get("mono") else CHAR))))
        rows, cur = [], ""
        for word in s.split():
            if cur and len(cur) + 1 + len(word) > per:
                rows.append(cur)
                cur = word
            else:
                cur = (cur + " " + word).strip()
        if cur:
            rows.append(cur)
        return self.lines(x, y, rows, size=size, lh=lh, **kw)

    def box(self, x, y, w, h, stroke=None, fill="none", rx=14, sw=2, dash=None):
        a = ' stroke="%s" stroke-width="%s"' % (stroke or T["agent"], sw)
        if dash:
            a += ' stroke-dasharray="%s"' % dash
        self.out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"%s/>'
                        % (_n(x), _n(y), _n(w), _n(h), _n(rx), fill, a))

    def arrow(self, points, color=None, sw=3, dash=None, head=True):
        color = color or T["agent"]
        pts = list(points)
        d = "M" + " L".join("%s %s" % (_n(x), _n(y)) for x, y in pts)
        a = ' stroke-dasharray="%s"' % dash if dash else ""
        self.out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s/>' % (d, color, sw, a))
        if head:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            dx, dy = x1 - x0, y1 - y0
            n = (dx * dx + dy * dy) ** 0.5 or 1
            ux, uy = dx / n, dy / n
            L, H = 16, 8
            bx, by = x1 - ux * L, y1 - uy * L
            p = [(x1, y1), (bx - uy * H, by + ux * H), (bx + uy * H, by - ux * H)]
            self.out.append('<polygon points="%s" fill="%s"/>'
                            % (" ".join("%s,%s" % (_n(a_), _n(b_)) for a_, b_ in p), color))

    def pill(self, x, y, s, color=None, size=22, mono=True):
        color = color or T["you"]
        w = len(s) * size * (MONO if mono else CHAR) + 24
        self.box(x, y, w, size + 16, stroke=color, fill=T["bg"], rx=(size + 16) / 2, sw=2)
        self.text(x + 12, y + size + 1, s, size=size, fill=color, mono=mono)
        return w

    def legend(self, x, y):
        self.out.append('<circle cx="%s" cy="%s" r="9" fill="%s"/>' % (_n(x), _n(y), T["you_fill"]))
        self.text(x + 20, y + 8, "you", size=22, fill=T["you"])
        self.out.append('<circle cx="%s" cy="%s" r="9" fill="%s"/>' % (_n(x + 90), _n(y), T["agent_dark"]))
        self.text(x + 110, y + 8, "agents", size=22)

    def save(self, path):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full = path if os.path.isabs(path) else os.path.join(root, path)
        with open(full, "w", encoding="utf-8") as f:
            f.write("\n".join(self.out + ["</svg>"]) + "\n")
