#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["reportlab==4.5.1"]
# ///
"""Build the IaC code scan report as a PDF.

Usage: uv run --script scripts/build_wiz_code_scan_report.py docs/<project>-wiz-code-scan-report.pdf

The report text lives in this script. Replace every <placeholder>, fill the level rows, then build. To issue a new version,
change the text, add an entry at the top of HISTORY, then rebuild. The title-block logo is pil-logo.png next to this script.

Text helpers escape XML. Write `name` for a monospace identifier, **text** for bold, [[key]] for the linked number of the
section with that key, and a newline for a line break in a table cell. A key is lower-case letters, digits and hyphens.
"""
import argparse
import glob
import pathlib
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, PageTemplate, Paragraph, Table, TableStyle

PROJECT = "<PROJECT>"
REPOSITORY = "<owner>/<repo>"
BRANCH = "main"
SENDER = "<team that owns the repository>"
RECIPIENT = "<team that requires the scan>"
SCAN_TIME = "<D Month YYYY> at <HH:MM> UTC"  # cicdScan.timestamp from list_code_repositories
SCANNED_COMMIT = "<commit>"  # head of BRANCH at SCAN_TIME
CURRENT_COMMIT = "<commit>"  # head of BRANCH that the cited file lines refer to; equal to SCANNED_COMMIT when unchanged
# Code that arrived after the scan, and whether it touches a setting any finding checks. Used only when the commits differ.
SCOPE_NOTE = "<Code merged after the scan, and the git diff result for the cited files.>"
SEVERITY = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 4, "LOW": 0, "INFORMATIONAL": 0}  # open findings from Wiz
PROVIDER = "<provider> <pinned version>"
SOURCES = "<Where contract rules and design choices come from, with file paths.>"
# One entry per version, newest first: (version, date, [one line per change, with the section it touches]).
HISTORY = [
    ("1.0", "<D Month YYYY>", ["First report."]),
]

# Each finding sits in exactly one level. A row is one Wiz rule and becomes a numbered subsection titled with the rule name,
# so write the name exactly as Wiz returns it (rule.name). The count is the number of that rule's findings in this level.
# The note qualifies the count, such as "one-click" or the roots the findings are in, and may be empty.
LEVEL_1 = [  # (Wiz rule name, count, note, file, change)
    ("<Wiz rule name>", 1, "", "`<path>:<line>`", "<In-place change, and the effect while it applies.>"),
]
LEVEL_1_WAITING = 0  # Level 1 findings that wait for the prerequisite in LEVEL_1_NOTE
LEVEL_1_NOTE = "<Prerequisite outside the repository and which findings wait for it, or empty.>"
LEVEL_2 = [  # (Wiz rule name, count, note, file, change)
    ("<Wiz rule name>", 1, "", "`<path>:<line>`", "<Change, and the risk it removes.>"),
]
LEVEL_2_NOTE = "<What the replacement disrupts, or empty.>"
LEVEL_3 = [  # (Wiz rule name, count, note, "Forces new" or "In place", why it is not needed, harmless in-place change)
    ("<Wiz rule name>", 1, "", "In place", "<Why the environment or the design does not need it.>", False),
]
LEVEL_4 = [  # (Wiz rule name, count, note, reason)
    ("<Wiz rule name>", 1, "", "<Contract rule, unsupported setting, conflicting rule, or renamed attribute.>"),
]

VERSION, REVISED, CHANGES = HISTORY[0]
ISSUED = HISTORY[-1][1]  # date of version 1.0
AUDIENCE = "Internal use"
HEADER = f"{PROJECT} IaC code scan report for {RECIPIENT}"
FOOTER = f"Prepared by {SENDER}, {ISSUED} · Version {VERSION}" + (f", revised {REVISED}" if REVISED != ISSUED else "")
LOGO = pathlib.Path(__file__).resolve().with_name("pil-logo.png")


def font(filename):
    found = glob.glob(f"/usr/share/fonts/**/{filename}", recursive=True)
    return found[0] if found else None


# Liberation Sans is metric-compatible with Helvetica, so the built-in fonts keep the layout when it is missing.
SANS, SANS_BOLD, MONO = "Helvetica", "Helvetica-Bold", "Courier"
if font("LiberationSans-Regular.ttf") and font("LiberationSans-Bold.ttf"):
    pdfmetrics.registerFont(TTFont("Sans", font("LiberationSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Sans-Bold", font("LiberationSans-Bold.ttf")))
    pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")
    SANS, SANS_BOLD = "Sans", "Sans-Bold"
if font("DejaVuSansMono.ttf"):
    pdfmetrics.registerFont(TTFont("Mono", font("DejaVuSansMono.ttf")))
    MONO = "Mono"

INK = colors.HexColor("#111111")
NAVY = colors.HexColor("#1f3a5f")
MUTED = colors.HexColor("#5f6b7a")
RULE = colors.HexColor("#c7d0da")
HEAD_BG = colors.HexColor("#e8eef6")

MARGIN = 18 * mm
W = A4[0] - 2 * MARGIN
LOGO_H = 14 * mm
MONO_SIZE = 6.8

BODY = ParagraphStyle("body", fontName=SANS, fontSize=9.4, leading=13, textColor=INK, spaceAfter=5)
TITLE = ParagraphStyle("title", parent=BODY, fontName=SANS_BOLD, fontSize=21, leading=26, textColor=NAVY, spaceAfter=2)
SUBTITLE = ParagraphStyle("subtitle", parent=BODY, fontSize=11, leading=14, textColor=MUTED, spaceAfter=8)
VERSION_LINE = ParagraphStyle("version", parent=BODY, fontSize=8.4, textColor=MUTED, spaceAfter=4)
H2 = ParagraphStyle("h2", parent=BODY, fontName=SANS_BOLD, fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle("h3", parent=BODY, fontName=SANS_BOLD, fontSize=9.8, leading=13, textColor=NAVY, spaceBefore=5, spaceAfter=3)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.2, leading=10.8, spaceAfter=0)
CELL_HEAD = ParagraphStyle("cellhead", parent=CELL, fontName=SANS_BOLD)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=3, bulletFontName=SANS, spaceAfter=3)


NUMBER = {}  # section key -> number, in the order of the section() calls
KEYS = []  # every section() key, in call order; main() rejects a repeat
REFS = set()  # keys named by [[key]] references


def link(match):
    key = match.group(1)
    REFS.add(key)
    return f'<a href="#{key}" color="{NAVY.hexval()}">{NUMBER.get(key, "?")}</a>'


def fmt(text):
    text = escape(text).replace("\n", "<br/>")
    text = re.sub(r"`([^`]+)`", f'<font name="{MONO}" size="{MONO_SIZE}">\\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"\[\[(.+?)\]\]", link, text)


def P(text, style=BODY):
    return Paragraph(fmt(text), style)


def bullets(items):
    return [Paragraph(fmt(t), BULLET, bulletText="•") for t in items]


GRID = [
    ("GRID", (0, 0), (-1, -1), 0.5, RULE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
]


def table(rows, widths):
    """rows[0] is the header. widths are fractions of the text width and sum to 1."""
    data = [[P(c, CELL_HEAD if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[W * f for f in widths], repeatRows=1, hAlign="LEFT", spaceAfter=5)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD_BG), *GRID]))
    return t


def title_block():
    """Logo on the left; title, subtitle and version line on the right."""
    iw, ih = ImageReader(str(LOGO)).getSize()
    logo_w = LOGO_H * iw / ih
    text = [
        P(f"{PROJECT} IaC Code Scan Report", TITLE),
        P(f"Wiz findings of medium severity and above · {SENDER} to {RECIPIENT} · {BRANCH} at {SCANNED_COMMIT}", SUBTITLE),
        P(f"Version {VERSION} · {REVISED}", VERSION_LINE),
    ]
    t = Table([[Image(str(LOGO), width=logo_w, height=LOGO_H), text]], colWidths=[logo_w + 6 * mm, W - logo_w - 6 * mm], hAlign="LEFT", spaceAfter=4)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def heading(key, text):
    """A heading that [[key]] links to and that ReportDoc adds to the PDF bookmarks."""
    p = Paragraph(f'<a name="{key}"/>{fmt(text)}', H2)
    p.bookmark = (text.replace("`", ""), key)
    return p


def with_heading(head, flow):
    """Keep a heading on the same page as its first flowable."""
    first = flow[0]
    if getattr(first, "repeatRows", 0):
        # A table() splits by row. Reserve room for the heading and the first 60 mm of the table, so a long table starts on
        # this page and continues on the next one.
        room = head.style.spaceBefore + head.style.leading + head.style.spaceAfter + min(first.wrap(W, A4[1])[1], 60 * mm)
        return [CondPageBreak(room), head, *flow]
    group = first._content if isinstance(first, KeepTogether) else [first]
    return [KeepTogether([head, *group]), *flow[1:]]


def section(key, title, *flow):
    """Numbered section. The number is the position of this call among the section() calls. [[key]] links to it."""
    if not re.fullmatch(r"[a-z0-9-]+", key):
        raise SystemExit(f"section key must be lower-case letters, digits and hyphens: {key}")
    KEYS.append(key)
    NUMBER.setdefault(key, len(NUMBER) + 1)
    return with_heading(heading(key, f"{NUMBER[key]}. {title}"), flow)


def total(rows):
    return sum(r[1] for r in rows)


def level(key, title, labels, rows, note=""):
    """Level section: the note, then one numbered subsection per Wiz rule, titled with the rule name.

    A row is the Wiz rule name, the finding count, a note on the count, then exactly one value per label.
    """
    flow = [P(note)] if note else []
    if not rows:
        flow.append(P("No finding is in this level."))
    for n, (name, count, count_note, *values) in enumerate(rows, 1):
        if len(values) != len(labels):
            raise SystemExit(f"{key} row {n} ({name}): expected {len(labels)} values after the name, count and note "
                             f"({', '.join(labels)}), found {len(values)}")
        head = Paragraph(fmt(f"{NUMBER.get(key, '?')}.{n} {name}"), H3)
        fields = [("Findings", f"{count} ({count_note})" if count_note else str(count)), *zip(labels, values)]
        t = Table([[P(k, CELL_HEAD), P(v, CELL)] for k, v in fields], colWidths=[W * 0.22, W * 0.78], hAlign="LEFT", spaceAfter=5)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HEAD_BG), *GRID]))
        flow.append(KeepTogether([head, t]))
    return section(key, title, *flow)


def story():
    n1, n2, n3, n4 = (total(rows) for rows in (LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4))
    reported = n1 + n2 + n3 + n4
    fixable, stay = n1 + n2, n3 + n4
    for n, r in enumerate(LEVEL_3, 1):
        if len(r) != 6:  # so that r[5] is the harmless flag and r[:5] is the row level() shows
            raise SystemExit(f"level-3 row {n} ({r[0]}): expected 6 values (name, count, note, change type, why, harmless flag), "
                             f"found {len(r)}")
    harmless = sum(r[1] for r in LEVEL_3 if r[5])
    high = SEVERITY["CRITICAL"] + SEVERITY["HIGH"]
    severe = (f"{SEVERITY['HIGH']} are high and {SEVERITY['CRITICAL']} are critical." if high else
              "No finding is high or critical.")
    skipped = SEVERITY["LOW"] + SEVERITY["INFORMATIONAL"]
    scope = (f"Wiz scans the code in the repository, whether or not it is applied. It scanned `{BRANCH}` on {SCAN_TIME}, "
             f"at commit `{SCANNED_COMMIT}`.")
    if CURRENT_COMMIT != SCANNED_COMMIT:
        scope += f" File lines in this report refer to `{CURRENT_COMMIT}`, the current head of `{BRANCH}`. {SCOPE_NOTE}"

    s = [
        title_block(),
        P(
            f"{RECIPIENT} requires code scanning of infrastructure code. {SENDER} read the open Wiz IaC code-scan findings "
            f"for `{REPOSITORY}` on {ISSUED} and placed every finding of medium severity or above in one of four fix levels. "
            f"**{fixable} of the {reported} findings can be fixed** (Levels 1 and 2), and {stay} stay. {severe}"
            + (f" The {skipped} low and informational findings are out of scope." if skipped else "")
        ),
        P(scope),
    ]

    if len(HISTORY) > 1:
        s += [P(f"**New in version {VERSION}**:"), *bullets(CHANGES)]

    level_1 = str(n1) + (f" ({n1 - LEVEL_1_WAITING} now, {LEVEL_1_WAITING} after the prerequisite in section [[level-1]])"
                         if LEVEL_1_WAITING else "")
    summary = [f"Levels 1 and 2 done: {fixable} fixed, {stay} left.", f"Level 1 only: {n1} fixed, {stay + n2} left."]
    if harmless:
        summary.append(f"{harmless} Level 3 findings are harmless in-place changes. Fixing them only lowers the Wiz count, to "
                       f"{stay - harmless} left.")
    s += section(
        "summary", "Summary",
        table([
            ["Level", "Meaning", "Findings"],
            ["1", "In-place update, low risk", level_1],
            ["2", "Forces a new resource, but recommended", str(n2)],
            ["3", "Not necessary", str(n3)],
            ["4", "Not possible or not supported", str(n4)],
        ], [0.1, 0.42, 0.48]),
        *bullets(summary),
    )

    s += level("level-1", "Level 1: in-place update, low risk", ("File", "Change"), LEVEL_1, LEVEL_1_NOTE)
    s += level("level-2", "Level 2: forces a new resource, but recommended", ("File", "Change"), LEVEL_2, LEVEL_2_NOTE)
    # The harmless flag at the end of a Level 3 row feeds the summary and is not a field of the subsection.
    s += level("level-3", "Level 3: not necessary", ("Change type", "Why it is not needed"), [r[:5] for r in LEVEL_3])
    s += level("level-4", "Level 4: not possible or not supported", ("Reason",), LEVEL_4)

    s += section(
        "method", "How the findings were classified",
        *bullets([
            f"Counts and file paths come from the Wiz IaC findings for `{REPOSITORY}`, read on {ISSUED}. The open counts by "
            "severity match the repository analytics in Wiz.",
            "A finding counts once. A finding in a module is one finding, however many roots call the module.",
            f"Whether a change is in place or forces a new resource comes from the {PROVIDER} provider documentation, the "
            "version this repository pins.",
            SOURCES,
            "Each rule's Terraform check (`regoCode`) was read where the finding's cause was not clear from the code.",
        ]),
    )

    if len(HISTORY) > 1:
        s += section(
            "history", "Version history",
            table([["Version", "Date", "Changes"], *[[v, d, "\n".join(c)] for v, d, c in HISTORY]], [0.1, 0.2, 0.7]),
        )
    return s


def decorate(canvas, doc):
    pw, ph = canvas._pagesize
    canvas.saveState()
    canvas.setFont(SANS, 7.6)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, ph - 10 * mm, HEADER)
    canvas.drawRightString(pw - MARGIN, ph - 10 * mm, AUDIENCE)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, ph - 11.5 * mm, pw - MARGIN, ph - 11.5 * mm)
    canvas.line(MARGIN, 13 * mm, pw - MARGIN, 13 * mm)
    canvas.drawString(MARGIN, 9.5 * mm, FOOTER)
    canvas.drawRightString(pw - MARGIN, 9.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


class ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, "bookmark"):
            self.canv.addOutlineEntry(*flowable.bookmark, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", help="output PDF path, for example docs/<project>-wiz-code-scan-report.pdf")
    args = parser.parse_args()

    placed = sum(total(rows) for rows in (LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4))
    expected = SEVERITY["CRITICAL"] + SEVERITY["HIGH"] + SEVERITY["MEDIUM"]
    if placed != expected:
        raise SystemExit(f"the levels hold {placed} findings, but Wiz reports {expected} of medium severity or above")

    doc = ReportDoc(
        args.out,
        pagesize=A4,
        title=f"{PROJECT} IaC code scan report, version {VERSION}",
        author=SENDER,
        subject=f"{PROJECT} IaC code scan report for {RECIPIENT}: Wiz findings for {REPOSITORY}, version {VERSION}",
    )
    pw, ph = A4
    frame = Frame(MARGIN, 16 * mm, pw - 2 * MARGIN, ph - 32 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="portrait", frames=[frame], onPage=decorate, pagesize=A4)])
    story()  # The first pass numbers the sections, so the second pass resolves [[key]] references to later sections.
    repeated = sorted({k for k in KEYS if KEYS.count(k) > 1})
    if repeated:
        raise SystemExit(f"section key used more than once: {', '.join(repeated)}")
    flow = story()
    if REFS - NUMBER.keys():
        raise SystemExit(f"[[key]] names no section: {', '.join(sorted(REFS - NUMBER.keys()))}")
    doc.build(flow)
    print(args.out)


if __name__ == "__main__":
    main()
