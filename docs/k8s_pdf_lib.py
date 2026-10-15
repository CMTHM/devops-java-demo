"""Shared layout helpers for the TRISHA ACADEMY Kubernetes course PDFs."""
import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame,
                                KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import (Circle, Drawing, Line, Polygon, Rect,
                                       String)

FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Segoe", os.path.join(FONT_DIR, "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Bold", os.path.join(FONT_DIR, "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Italic", os.path.join(FONT_DIR, "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-BoldItalic", os.path.join(FONT_DIR, "segoeuiz.ttf")))
pdfmetrics.registerFont(TTFont("Consolas", os.path.join(FONT_DIR, "consola.ttf")))
pdfmetrics.registerFont(TTFont("Consolas-Bold", os.path.join(FONT_DIR, "consolab.ttf")))
pdfmetrics.registerFontFamily("Segoe", normal="Segoe", bold="Segoe-Bold",
                              italic="Segoe-Italic", boldItalic="Segoe-BoldItalic")
pdfmetrics.registerFontFamily("Consolas", normal="Consolas", bold="Consolas-Bold",
                              italic="Consolas", boldItalic="Consolas-Bold")

PAGE_W, PAGE_H = A4
LEFT = RIGHT = 40
TOP, BOTTOM = 58, 50
CONTENT_W = PAGE_W - LEFT - RIGHT

COURSE = "Kubernetes for Freshers"
ACADEMY = "TRISHA ACADEMY"

# ---------------------------------------------------------------- colours
NAVY = HexColor("#1B2A4A")
NAVY_DEEP = HexColor("#111C33")
BLUE = HexColor("#326CE5")          # Kubernetes blue
BLUE_DARK = HexColor("#1F4FB8")
BLUE_BG = HexColor("#E8F0FD")
TEAL = HexColor("#0F9D9A")
TEAL_BG = HexColor("#E3F6F5")
GOLD = HexColor("#F2A900")
GOLD_BG = HexColor("#FFF6DD")
INK = HexColor("#1F2937")
MUTED = HexColor("#6B7280")
LINE = HexColor("#D1D5DB")
ZEBRA = HexColor("#F5F7FB")
CODE_BG = HexColor("#F3F4F6")
GREEN = HexColor("#15803D")
GREEN_BG = HexColor("#E7F6EC")
RED = HexColor("#B91C1C")
RED_BG = HexColor("#FDECEC")
PURPLE = HexColor("#6D28D9")
PURPLE_BG = HexColor("#F1EAFE")
ORANGE = HexColor("#C2410C")
ORANGE_BG = HexColor("#FFF0E6")
GREY_BG = HexColor("#F3F4F6")
WHITE = colors.white


# ---------------------------------------------------------------- text
def rich(text):
    """Escape text but keep a small set of inline tags."""
    s = escape(text)
    for tag in ("b", "i", "u"):
        s = s.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    s = s.replace("&lt;br/&gt;", "<br/>")
    s = re.sub(r"`([^`]+)`", r'<font face="Consolas" color="#1F4FB8">\1</font>', s)
    return s


def S(name, **kw):
    base = dict(fontName="Segoe", fontSize=10.2, leading=14.6, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


ST = {
    "h1": S("h1", fontName="Segoe-Bold", fontSize=17, leading=22, textColor=NAVY,
            spaceBefore=10, spaceAfter=6, keepWithNext=1),
    "h2": S("h2", fontName="Segoe-Bold", fontSize=13, leading=17, textColor=BLUE_DARK,
            spaceBefore=9, spaceAfter=4, keepWithNext=1),
    "h3": S("h3", fontName="Segoe-Bold", fontSize=11, leading=15, textColor=NAVY,
            spaceBefore=6, spaceAfter=2, keepWithNext=1),
    "body": S("body", spaceAfter=5),
    "bullet": S("bullet", leftIndent=14, bulletIndent=3, spaceAfter=2),
    "th": S("th", fontName="Segoe-Bold", fontSize=9.2, leading=12, textColor=WHITE),
    "td": S("td", fontSize=9.2, leading=12.4),
    "td_bold": S("td_bold", fontName="Segoe-Bold", fontSize=9.2, leading=12.4),
    "code": S("code", fontName="Consolas", fontSize=8.6, leading=11.4, textColor=INK),
    "callout_title": S("ct", fontName="Segoe-Bold", fontSize=10.2, leading=14),
    "callout_body": S("cb", fontSize=9.6, leading=13.6),
    "q": S("q", fontName="Segoe-Bold", fontSize=10, leading=14, textColor=NAVY,
           spaceBefore=6, spaceAfter=1),
    "a": S("a", fontSize=9.6, leading=13.6, leftIndent=12, spaceAfter=3),
    "q_only": S("q_only", fontSize=10.2, leading=15.5, leftIndent=18, firstLineIndent=-18,
                spaceAfter=3),
    "caption": S("caption", fontName="Segoe-Italic", fontSize=8.8, leading=12,
                 textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=8),
    "toc0": S("toc0", fontName="Segoe-Bold", fontSize=11, leading=16, textColor=NAVY,
              spaceBefore=5),
    "toc1": S("toc1", fontSize=9.6, leading=13, leftIndent=16, textColor=INK),
}


def P(text, style="body"):
    return Paragraph(rich(text), ST[style] if isinstance(style, str) else style)


def bullet(text):
    return Paragraph(rich(text), ST["bullet"], bulletText="\u2022")


def bullets(items):
    return [bullet(t) for t in items]


def gap(h=6):
    return Spacer(1, h)


# ---------------------------------------------------------------- blocks
def code(text, title=None):
    lines = text.strip("\n").split("\n")
    body = "<br/>".join(escape(l).replace(" ", "&nbsp;") if l else "&nbsp;" for l in lines)
    cell = []
    if title:
        cell += [Paragraph(f'<font color="#6B7280">{escape(title)}</font>',
                           S("ctl", fontName="Segoe-Bold", fontSize=8.2, leading=10)), gap(5)]
    cell.append(Paragraph(body, ST["code"]))
    t = Table([[cell]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    t.spaceAfter = 6
    return t


def callout(title, body, bg, accent):
    parts = [Paragraph(f'<font color="{accent.hexval().replace("0x", "#")}">{rich(title)}</font>',
                       ST["callout_title"])]
    if isinstance(body, str):
        parts.append(Paragraph(rich(body), ST["callout_body"]))
    else:
        for item in body:
            parts.append(Paragraph(rich(item), S("cbb", parent=ST["callout_body"],
                                                 leftIndent=12, bulletIndent=2),
                                   bulletText="\u2022"))
    t = Table([[parts]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    t.spaceAfter = 8
    return t


def story(body):
    return callout("Ravi's story", body, PURPLE_BG, PURPLE)


def real(body, title="Everyday example"):
    return callout(title, body, GOLD_BG, ORANGE)


def tryit(body, title="Try it yourself"):
    return callout(title, body, GREEN_BG, GREEN)


def mistake(body, title="Common mistake"):
    return callout(title, body, RED_BG, RED)


def funfact(body, title="Did you know?"):
    return callout(title, body, TEAL_BG, TEAL)


def remember(body, title="Remember"):
    return callout(title, body, BLUE_BG, BLUE)


def table(headers, rows, widths, bold_first=True):
    total = sum(widths)
    if abs(total - CONTENT_W) > 1:
        raise ValueError(f"table widths sum {total} != {CONTENT_W}")
    data = [[Paragraph(rich(h), ST["th"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(rich(c), ST["td_bold"] if (i == 0 and bold_first) else ST["td"])
                     for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(style))
    return [t, gap(8)]


def cols(*fractions):
    """Column widths from fractions that add up to 1."""
    w = [round(CONTENT_W * f, 2) for f in fractions]
    w[-1] = round(CONTENT_W - sum(w[:-1]), 2)
    return w


def figure(drawing, caption):
    return KeepTogether([gap(4), drawing, Paragraph(rich(caption), ST["caption"])])


# ---------------------------------------------------------------- diagram primitives
def text(d, x, y, s, size=9, color=INK, bold=False, anchor="middle", font=None):
    d.add(String(x, y, s, fontName=font or ("Segoe-Bold" if bold else "Segoe"),
                 fontSize=size, fillColor=color, textAnchor=anchor))


def box(d, x, y, w, h, lines, fill=WHITE, stroke=NAVY, color=INK, size=9,
        bold_first=True, radius=6, dashed=False, font=None, stroke_width=1.1, sub_color=None):
    r = Rect(x, y, w, h, rx=radius, ry=radius, fillColor=fill, strokeColor=stroke,
             strokeWidth=stroke_width)
    if dashed:
        r.strokeDashArray = [4, 3]
    d.add(r)
    if isinstance(lines, str):
        lines = [lines]
    lh = size + 3
    top = y + h / 2 + (len(lines) - 1) * lh / 2 - size / 3
    for i, ln in enumerate(lines):
        text(d, x + w / 2, top - i * lh, ln, size=size if i == 0 else size - 1,
             color=color if i == 0 else (sub_color or (MUTED if color == INK else color)),
             bold=(i == 0 and bold_first), font=font)


def arrow(d, x1, y1, x2, y2, color=NAVY, width=1.3, label=None, label_dx=0, label_dy=4,
          label_size=7.8, dashed=False, head=True):
    ln = Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=width)
    if dashed:
        ln.strokeDashArray = [4, 3]
    d.add(ln)
    if head:
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        L, Wd = 7, 3.6
        bx, by = x2 - L * math.cos(ang), y2 - L * math.sin(ang)
        px, py = -math.sin(ang) * Wd, math.cos(ang) * Wd
        d.add(Polygon([x2, y2, bx + px, by + py, bx - px, by - py],
                      fillColor=color, strokeColor=color, strokeWidth=0.5))
    if label:
        text(d, (x1 + x2) / 2 + label_dx, (y1 + y2) / 2 + label_dy, label,
             size=label_size, color=color)


def frame(d, x, y, w, h, title=None, fill=GREY_BG, stroke=LINE, title_color=NAVY,
          dashed=False, title_size=9):
    r = Rect(x, y, w, h, rx=8, ry=8, fillColor=fill, strokeColor=stroke, strokeWidth=1.1)
    if dashed:
        r.strokeDashArray = [5, 3]
    d.add(r)
    if title:
        text(d, x + 8, y + h - 13, title, size=title_size, color=title_color, bold=True,
             anchor="start")


def badge(d, x, y, n, fill=GOLD, color=NAVY, r=8):
    d.add(Circle(x, y, r, fillColor=fill, strokeColor=fill))
    text(d, x, y - 3.2, str(n), size=8.5, color=color, bold=True)


def pod_icon(d, x, y, w=46, h=26, label="pod", fill=BLUE_BG, stroke=BLUE, size=7.5):
    box(d, x, y, w, h, [label], fill=fill, stroke=stroke, size=size, radius=5)


def drawing(h):
    return Drawing(CONTENT_W, h)


# ---------------------------------------------------------------- course blocks
class Bookmark(Flowable):
    """Invisible marker: adds a PDF outline entry and a level-0 contents line."""

    def __init__(self, key, title, level=0):
        super().__init__()
        self.key, self.title, self.level = key, title, level
        self.width = self.height = 0

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        c = self.canv
        c.bookmarkPage(self.key)
        c.addOutlineEntry(self.title, self.key, level=self.level, closed=False)


class Rule(Flowable):
    def __init__(self, color=LINE, width=None, thickness=0.8):
        super().__init__()
        self.color, self.w, self.t = color, width, thickness

    def wrap(self, aw, ah):
        self.w = self.w or aw
        return self.w, 6

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.t)
        self.canv.line(0, 3, self.w, 3)


def day_banner(day, title, outcome, minutes="60-90 minutes"):
    kicker = Paragraph(f'<font color="#F2A900">K8S · CLASS {day:02d}</font>'
                       f'<font color="#C9D6F5">   ·   {minutes}</font>',
                       S("kick", fontName="Segoe-Bold", fontSize=9, leading=12))
    head = Paragraph(f'<font color="#FFFFFF">{rich(title)}</font>',
                     S("dt", fontName="Segoe-Bold", fontSize=19, leading=24))
    sub = Paragraph(f'<font color="#DCE6FB">{rich(outcome)}</font>',
                    S("ds", fontSize=10, leading=14))
    t = Table([[[kicker, gap(3), head, gap(4), sub]]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LINEBEFORE", (0, 0), (0, -1), 6, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return [Bookmark(f"day{day}", f"Class {day}: {title}"), t, gap(10)]


def covers(items, plan):
    """'What you will learn' plus the class time plan."""
    out = [P("What you will learn today", "h2")] + bullets(items)
    out.append(gap(4))
    out += table(["Part", "Topic", "Time"], plan, cols(0.12, 0.7, 0.18))
    return out


def interview(day, items):
    if len(items) != 20:
        raise ValueError(f"Class {day} has {len(items)} interview questions, expected 20")
    out = [PageBreak(), P(f"Class {day} - Top 20 interview questions", "h1"),
           P("Try answering each question aloud before you read the model answer. "
             "Interviewers look for a clear definition, one real example, and one trade-off.")]
    for i, (q, a) in enumerate(items, 1):
        out.append(KeepTogether([P(f"Q{i}. {q}", "q"), P(a, "a")]))
    return out


# ---------------------------------------------------------------- page decoration
def _k8s_wheel(c, cx, cy, r, color, inner=None, lw=None):
    import math
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(lw or r * 0.12)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.circle(cx, cy, r * 0.28, stroke=1, fill=0)
    for k in range(7):
        a = math.pi / 2 + k * 2 * math.pi / 7
        c.line(cx + r * 0.28 * math.cos(a), cy + r * 0.28 * math.sin(a),
               cx + r * 1.0 * math.cos(a), cy + r * 1.0 * math.sin(a))
        c.circle(cx + r * 1.0 * math.cos(a), cy + r * 1.0 * math.sin(a), r * 0.09,
                 stroke=1, fill=1 if inner else 0)
    c.restoreState()


def draw_cover(title, subtitle, tagline, chips):
    def _draw(c, doc):
        c.saveState()
        c.setFillColor(NAVY_DEEP)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, PAGE_H - 12, PAGE_W, 12, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)
        _k8s_wheel(c, PAGE_W - 120, PAGE_H - 250, 150, HexColor("#22335A"), lw=10)
        _k8s_wheel(c, 95, 520, 30, BLUE, inner=True, lw=4)
        c.setFillColor(GOLD)
        c.setFont("Segoe-Bold", 13)
        c.drawString(60, PAGE_H - 90, ACADEMY)
        c.setFillColor(HexColor("#9FB4E0"))
        c.setFont("Segoe", 10)
        c.drawString(60, PAGE_H - 106, "DevOps Career Track · Student Notes")
        c.setFillColor(WHITE)
        c.setFont("Segoe-Bold", 34)
        y = 440
        for line in title.split("\n"):
            c.drawString(60, y, line)
            y -= 42
        c.setFillColor(HexColor("#C9D6F5"))
        c.setFont("Segoe", 14)
        c.drawString(60, y - 6, subtitle)
        c.setFont("Segoe-Italic", 11)
        c.setFillColor(HexColor("#9FB4E0"))
        c.drawString(60, y - 30, tagline)
        x, cy = 60, y - 80
        c.setFont("Segoe-Bold", 9)
        for chip in chips:
            w = pdfmetrics.stringWidth(chip, "Segoe-Bold", 9) + 18
            if x + w > PAGE_W - 60:
                x, cy = 60, cy - 26
            c.setFillColor(HexColor("#22335A"))
            c.roundRect(x, cy, w, 19, 9, fill=1, stroke=0)
            c.setFillColor(HexColor("#DCE6FB"))
            c.drawString(x + 9, cy + 6, chip)
            x += w + 8
        c.setFillColor(HexColor("#9FB4E0"))
        c.setFont("Segoe", 9)
        c.drawString(60, 40, "For students of TRISHA ACADEMY · Keep these notes for revision and interviews")
        c.restoreState()
    return _draw


def draw_header_footer(c, doc):
    c.saveState()
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(LEFT, PAGE_H - 38, PAGE_W - RIGHT, PAGE_H - 38)
    c.setFont("Segoe-Bold", 8.5)
    c.setFillColor(BLUE_DARK)
    c.drawString(LEFT, PAGE_H - 31, ACADEMY)
    c.setFont("Segoe", 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - RIGHT, PAGE_H - 31, COURSE)
    c.line(LEFT, 34, PAGE_W - RIGHT, 34)
    c.drawString(LEFT, 22, "Student notes · Practise every command on your own laptop")
    c.setFont("Segoe-Bold", 8.5)
    c.setFillColor(NAVY)
    c.drawRightString(PAGE_W - RIGHT, 22, f"Page {doc.page}")
    c.restoreState()


class TocDoc(BaseDocTemplate):
    def beforeDocument(self):
        self._toc_seq = 0
        self._last_bookmark = None

    def afterFlowable(self, f):
        if isinstance(f, Bookmark):
            self._last_bookmark = f.title
            self.notify("TOCEntry", (0, f.title, self.page, f.key))
        elif isinstance(f, Paragraph) and f.style.name in ("h1",):
            txt = f.getPlainText()
            if txt == "Contents" or txt == self._last_bookmark:
                return
            self._toc_seq += 1
            key = f"toc{self._toc_seq}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (1, txt, self.page, key))


def toc_block():
    toc = TableOfContents()
    toc.levelStyles = [ST["toc0"], ST["toc1"]]
    toc.dotsMinLevel = 0
    return [P("Contents", "h1"), Rule(BLUE, thickness=1.5), gap(6), toc, PageBreak()]


def new_doc(out, title, subject, cover_fn):
    doc = TocDoc(out, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP,
                 bottomMargin=BOTTOM, title=title, author=ACADEMY, subject=subject)
    body = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, id="body",
                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover], onPage=cover_fn),
        PageTemplate(id="body", frames=[body], onPage=draw_header_footer),
    ])
    return doc


def start_story():
    return [NextPageTemplate("body"), PageBreak()] + toc_block()


__all__ = [n for n in dir() if not n.startswith("_")] + ["CondPageBreak", "PageBreak",
                                                          "KeepTogether", "Spacer"]
