#!/usr/bin/env python3
"""PP legibility check for HubSpot modules built with inline styles.

Usage:  python3 tools/pp-legibility-check.py file.html [file2.html ...]

Fails (exit 1) when any visible text is
  - smaller than 13px (a clamp() is judged by its minimum, which is what phones get), or
  - below WCAG AA contrast: 4.5:1, or 3:1 for large text (24px+, or 18.66px+ bold).

Reads inline style="" attributes only. Colours inherit down the tree; rgba() is
composited over the nearest background. A gradient is judged by its lightest and
darkest stop. Elements marked aria-hidden="true" are skipped (decorative glyphs).
It cannot see the HubSpot theme stylesheet, so text with no inline colour or size
is judged against the defaults below.
"""
import re
import sys
from html.parser import HTMLParser

MIN_PX = 13
DEFAULT_FG = (45, 62, 82)      # navy; theme default unknown
DEFAULT_BG = (255, 255, 255)
DEFAULT_PX = 16.0
VOID = {"br", "img", "link", "meta", "input", "hr", "source", "wbr"}
SKIP = {"script", "style"}


def parse_colours(value):
    """Every colour in a CSS value, as (r, g, b, a)."""
    out = []
    for m in re.finditer(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b|rgba?\(([^)]*)\)", value):
        if m.group(1):
            h = m.group(1)
            if len(h) == 3:
                h = "".join(c * 2 for c in h)
            out.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0))
        else:
            p = [x.strip() for x in m.group(2).split(",")]
            if len(p) >= 3:
                a = float(p[3]) if len(p) > 3 else 1.0
                out.append((float(p[0]), float(p[1]), float(p[2]), a))
    return out


def over(c, bg):
    a = c[3]
    return tuple(c[i] * a + bg[i] * (1 - a) for i in range(3))


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def font_px(value, parent_px):
    value = value.strip()
    m = re.match(r"clamp\(\s*([\d.]+)px", value)
    if m:
        return float(m.group(1))
    m = re.match(r"([\d.]+)px", value)
    if m:
        return float(m.group(1))
    m = re.match(r"([\d.]+)r?em", value)
    if m:
        return float(m.group(1)) * (DEFAULT_PX if "rem" in value else parent_px)
    return parent_px


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        # frame: tag, fg(rgba), bgs(list of opaque rgb), px, bold, hidden
        self.stack = [("root", DEFAULT_FG + (1.0,), [DEFAULT_BG], DEFAULT_PX, False, False)]
        self.findings = []
        self.count = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        _, fg, bgs, px, bold, hidden = self.stack[-1]
        style = {}
        for decl in (a.get("style") or "").split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1)
                style[k.strip().lower()] = v.strip()
        if "color" in style:
            c = parse_colours(style["color"])
            if c:
                fg = c[0]
        bgval = style.get("background") or style.get("background-color")
        if bgval:
            cols = parse_colours(bgval)
            if cols:
                bgs = [over(c, b) for c in cols for b in bgs]
        if "font-size" in style:
            px = font_px(style["font-size"], px)
        w = style.get("font-weight", "")
        if w:
            bold = w in ("bold", "bolder") or (w.isdigit() and int(w) >= 700)
        if tag in ("strong", "b"):
            bold = True
        if a.get("aria-hidden") == "true" or "display:none" in (a.get("style") or "").replace(" ", ""):
            hidden = True
        if tag not in VOID:
            self.stack.append((tag, fg, bgs, px, bold, hidden))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        text = " ".join(data.split())
        tag, fg, bgs, px, bold, hidden = self.stack[-1]
        if not text or hidden or any(f[0] in SKIP for f in self.stack):
            return
        self.count += 1
        large = px >= 24 or (bold and px >= 18.66)
        need = 3.0 if large else 4.5
        worst = min(ratio(over(fg, b), b) for b in bgs)
        problems = []
        if px < MIN_PX:
            problems.append("size %gpx < %dpx" % (px, MIN_PX))
        if worst < need:
            problems.append("contrast %.2f < %.1f" % (worst, need))
        if problems:
            line = self.getpos()[0]
            self.findings.append((line, "; ".join(problems), text[:60]))


def main(paths):
    bad = 0
    for path in paths:
        c = Checker()
        with open(path, encoding="utf-8") as fh:
            c.feed(fh.read())
        seen = set()
        rows = [f for f in c.findings if not (f[1:] in seen or seen.add(f[1:]))]
        status = "FAIL" if rows else "ok"
        print("%s  %s  (%d text runs, %d problems)" % (status, path, c.count, len(c.findings)))
        for line, why, text in rows:
            print("   line %-4d %-34s %s" % (line, why, text))
        bad += len(rows)
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
