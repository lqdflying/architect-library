#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["reportlab==4.5.1"]
# ///
"""Build the <PROJECT ENV> infrastructure handoff as a PDF.

Usage: uv run --script scripts/build_<env>_handoff.py docs/<project>-<env>-handoff.pdf [--diagram design-docs/<topology>.png]

The handoff text lives in this script. To issue a new version, change the text, add an entry at the top of HISTORY, then rebuild.
The title-block logo is pil-logo.png next to this script. Never put a secret value in the handoff.

Text helpers escape XML. Write `name` for a monospace identifier, **text** for bold, [[key]] for the linked number of the
section with that key, and a newline for a line break in a table cell. A key is lower-case letters, digits and hyphens.
"""
import argparse
import glob
import pathlib
import re
import textwrap
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ENV = "<PROJECT> <ENV>"
SCOPE = "<workload in a few words>"
REGION = "<region>"
SENDER = "<platform team>"
RECIPIENT = "<application vendor or developer team>"
# One entry per version, newest first: (version, date, [one line per change, with the section it touches]).
HISTORY = [
    ("1.0", "<D Month YYYY>", ["First handoff."]),
]
VERSION, REVISED, CHANGES = HISTORY[0]
ISSUED = HISTORY[-1][1]  # date of version 1.0
AUDIENCE = "Internal and vendor use"
HEADER = f"{PROJECT_ENV} infrastructure handoff for {RECIPIENT}"
FOOTER = f"Prepared by {SENDER}, {ISSUED} · Version {VERSION}" + (f", revised {REVISED}" if REVISED != ISSUED else "")
DIAGRAM_CAPTION = "<What the diagram shows. Addresses shown are the <ENV> allocations.>"
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
CODE_BG = colors.HexColor("#f3f5f7")
CODE_BORDER = colors.HexColor("#c9cfd6")
CODE_INK = colors.HexColor("#1f2933")
NOTE_BG = colors.HexColor("#fff3dc")
NOTE_BORDER = colors.HexColor("#d4900f")
NOTE_HEAD = colors.HexColor("#8a5a00")

MARGIN = 18 * mm
W = A4[0] - 2 * MARGIN
LOGO_H = 14 * mm
MONO_SIZE = 6.8

BODY = ParagraphStyle("body", fontName=SANS, fontSize=9.4, leading=13, textColor=INK, spaceAfter=5)
TITLE = ParagraphStyle("title", parent=BODY, fontName=SANS_BOLD, fontSize=21, leading=26, textColor=NAVY, spaceAfter=2)
SUBTITLE = ParagraphStyle("subtitle", parent=BODY, fontSize=11, leading=14, textColor=MUTED, spaceAfter=8)
VERSION_LINE = ParagraphStyle("version", parent=BODY, fontSize=8.4, textColor=MUTED, spaceAfter=4)
H2 = ParagraphStyle("h2", parent=BODY, fontName=SANS_BOLD, fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle("h3", parent=BODY, fontName=SANS_BOLD, fontSize=9.8, leading=13, textColor=NAVY, spaceBefore=6, spaceAfter=3)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=8.8, leading=12, textColor=MUTED)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.2, leading=10.8, spaceAfter=0)
CELL_HEAD = ParagraphStyle("cellhead", parent=CELL, fontName=SANS_BOLD)
CODE = ParagraphStyle("code", fontName=MONO, fontSize=7.6, leading=10.4, textColor=CODE_INK)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=12, bulletIndent=3, bulletFontName=SANS, spaceAfter=3)
BOX_HEAD = ParagraphStyle("boxhead", parent=BODY, fontName=SANS_BOLD, fontSize=10.5, leading=14, textColor=NOTE_HEAD, spaceAfter=3)
BOX_BODY = ParagraphStyle("boxbody", parent=BODY, fontSize=8.9, leading=12.4, spaceAfter=4)


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


def note(text):
    return P(text, NOTE)


def bullets(items):
    return [Paragraph(fmt(t), BULLET, bulletText="•") for t in items]


def numbered(items):
    return [Paragraph(fmt(t), BULLET, bulletText=f"{i}.") for i, t in enumerate(items, 1)]


def keep(*flow):
    """Keep a lead-in line on the same page as the block or list it introduces."""
    return KeepTogether(list(flow))


def table(rows, widths):
    """rows[0] is the header. widths are fractions of the text width and sum to 1."""
    data = [[P(c, CELL_HEAD if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[W * f for f in widths], repeatRows=1, hAlign="LEFT", spaceAfter=5)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t


def code(text):
    t = Table([[Preformatted(textwrap.dedent(text).strip("\n"), CODE)]], colWidths=[W], hAlign="LEFT", spaceAfter=6)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, CODE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def note_box(head, paragraphs):
    inner = [P(head, BOX_HEAD)] + [P(p, BOX_BODY) for p in paragraphs]
    t = Table([[inner]], colWidths=[W], hAlign="LEFT", spaceAfter=4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
        ("BOX", (0, 0), (-1, -1), 1, NOTE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def title_block():
    """Logo on the left; title, subtitle and version line on the right."""
    iw, ih = ImageReader(str(LOGO)).getSize()
    logo_w = LOGO_H * iw / ih
    text = [
        P(f"{PROJECT_ENV} Infrastructure Handoff", TITLE),
        P(f"{SCOPE} · {SENDER} to {RECIPIENT} · {REGION}", SUBTITLE),
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
    """A heading that [[key]] links to and that HandoffDoc adds to the PDF bookmarks."""
    p = Paragraph(f'<a name="{key}"/>{fmt(text)}', H2)
    p.bookmark = (text.replace("`", ""), key)
    return p


def with_heading(head, flow):
    """Keep a heading on the same page as its first flowable, or as a whole first keep() group."""
    first = flow[0]
    if getattr(first, "repeatRows", 0):
        # A table() splits by row. Reserve room for the heading and the first 60 mm of the table, so a long table starts on
        # this page and continues on the next one. Only table() repeats a header row; code() and note_box() do not.
        room = head.style.spaceBefore + head.style.leading + head.style.spaceAfter + min(first.wrap(W, A4[1])[1], 60 * mm)
        return [CondPageBreak(room), head, *flow]
    # A KeepTogether nested in another one reports an oversized height and always starts a new page, so merge a first keep() group.
    group = first._content if isinstance(first, KeepTogether) else [first]
    return [KeepTogether([head, *group]), *flow[1:]]


def section(key, title, *flow):
    """Numbered section. The number is the position of this call among the section() calls. [[key]] links to it."""
    if not re.fullmatch(r"[a-z0-9-]+", key):
        raise SystemExit(f"section key must be lower-case letters, digits and hyphens: {key}")
    KEYS.append(key)
    NUMBER.setdefault(key, len(NUMBER) + 1)
    return with_heading(heading(key, f"{NUMBER[key]}. {title}"), flow)


def subsection(title, *flow):
    """Unnumbered subsection inside a section."""
    return with_heading(P(title, H3), flow)


def story():
    s = [
        title_block(),
        P(
            f"{SENDER} has provisioned the {PROJECT_ENV} environment and verified it on <date>. This document hands it "
            "over: <every topic below, in section order>. <Environments not provisioned yet.> Secret values are not included."
        ),
        P("**Not ready yet:** <item>, <item>. See section [[not-ready]]."),
    ]

    if len(HISTORY) > 1:
        s += [P(f"**New in version {VERSION}**, applied on {REVISED}:"), *bullets(CHANGES)]

    s += [Spacer(1, 3), note_box("Before you start", [
        "**1. <Cluster or VM> access: sign in to <jump host or privileged-access tool> as `<account>`.** <What is private "
        "and the only place the reader works from.> See section [[sign-in]].",
        "**2. Access from your own devices: request <client VPN> from <network team>.** The private endpoints in section "
        "[[endpoints]] are not reachable from the public internet. <What to request, and from which team.>",
        "**3. <Shared service>: contact <owning team>.** <What that team handles.>",
        "**4. Integration troubleshooting: allow time.** Network and access changes go through the owning teams. Work with "
        "<team> on integration issues.",
    ])]

    s += section(
        "environment", "Environment",
        table([
            ["Item", "Value"],
            ["Subscription", "`<subscription name>`"],
            ["Tenant ID", "`<tenant id>`"],
            ["Region", "<region> (`<region code>`)"],
            ["Resource group", "`<resource group>`"],
            ["<Jump host or entry address>", "`<host>` (`<ip>`), <account or port>"],
        ], [0.3, 0.7]),
    )

    s += section(
        "resources", "Provisioned resources",
        table([
            ["Purpose", "Name", "Configuration"],
            ["<Purpose>", "`<resource name>`", "<Version, size and the security settings the reader relies on>. <Detail> (section [[secrets]])"],
        ], [0.17, 0.29, 0.54]),
        P("Public network access is disabled on <resources>. <Resource> is not provisioned yet (section [[not-ready]])."),
    )

    s += section(
        "endpoints", "Private endpoints and host names",
        keep(
            P("Each host name below resolves to its private address through the central private DNS zones. Use the normal "
              "host names, not the `privatelink` names."),
            table([
                ["Host name", "Address", "Port"],
                ["`<host name>`", "`<ip>`", "TCP <port>"],
            ], [0.56, 0.15, 0.29]),
        ),
        P(f"<Workload> traffic leaves from `<egress address or range>`. Request any other destination your services need "
          f"from {SENDER}."),
    )

    s += section(
        "identities", "Identities and access",
        table([
            ["Identity", "Used by", "Access granted"],
            ["`<sign-in account>`\n<where it signs in>", "<who uses it>", "<What it can do.> See section [[sign-in]]"],
            ["`<workload identity>`\nClient ID `<guid>`", "<application component>", "<Role> on `<scope>`"],
        ], [0.32, 0.23, 0.45]),
        *bullets([
            "<What fails without the identity, for example: access keys and connection strings fail; use the workload identity.>",
            f"Request any additional Azure role assignment from {SENDER}.",
        ]),
    )

    s += section(
        "sign-in", "Sign in and check access",
        keep(
            P("<Steps to sign in, in order, with the exact host and account.>"),
            code("""
                <command the reader runs>
                <command that proves the access works>
                """),
        ),
        keep(
            P("What `<account>` can do:"),
            *bullets([
                "<Allowed action, with the exact scope.>",
                "It cannot <withheld action>.",
            ]),
        ),
    )

    s += section(
        "task", "<Task in the reader's work order>",
        P("<What to do, with the exact names.>"),
        keep(
            P("Example <object>:"),
            code("""
                <copy-ready manifest or command with real names; <placeholder> only for values the reader chooses>
                """),
        ),
        keep(
            P("After a change, check <what>. <Expected result.>"),
            code("<check command>"),
        ),
        P("`<wrong value>` is denied because <reason>."),
    )

    s += section(
        "guardrails", "Guardrails",
        table([
            ["Object", "Rule"],
            ["<Object type>", "<What is denied, on which operation, and what to use instead.>"],
        ], [0.25, 0.75]),
    )

    s += section(
        "secrets", "Secrets",
        note_box("To add or change any secret in `<vault>`, submit a <request type> to <team>.", [
            "<team> enters the value.",
        ]),
        P("<Who supplies the values and who enters them.> Values are only in the vault. They are not in this document."),
        table([
            ["Secret name", "Purpose", "Readable by", "Status"],
            ["`<secret name>`", "<purpose>", "<identity>", "Entered"],
            ["`<secret name>`", "<purpose>", "<identity>", "Waiting for your value"],
        ], [0.34, 0.28, 0.2, 0.18]),
    )

    s += section(
        "settings", "Settings you own",
        P("<Which settings the IaC sets once and the reader then owns.>"),
        *bullets([
            "Do not change <IaC-managed properties>. The next apply reverts them. Ask <team> instead.",
            "If <resource> is recreated, it receives only <the IaC settings>. Restore your settings before it serves traffic.",
        ]),
    )

    s += section(
        "first-deployment", "Order before the first deployment",
        *numbered([
            "<Who> <does what>.",
            "<Who> <does what>, then confirms <result>.",
        ]),
        P("Rollback: <who reverts what, until when>."),
    )

    s += section(
        "not-ready", "What is not ready yet",
        *bullets(["<Item>. Until <team> confirms it, <effect on the reader>."]),
    )

    s += section(
        "not-included", "What this document does not include",
        P("<Secret values, admin credentials and permissions that are withheld.>"),
        P(f"Reply to {SENDER} if <each failure point the reader can hit> fails."),
    )

    s += section(
        "contacts", "Whom to contact",
        table([
            ["Need", "Team"],
            ["<request>", "<team>"],
        ], [0.78, 0.22]),
    )

    if len(HISTORY) > 1:
        s += section(
            "history", "Version history",
            table([["Version", "Date", "Changes"], *[[v, d, "\n".join(c)] for v, d, c in HISTORY]], [0.1, 0.2, 0.7]),
        )
    return s


def appendix(diagram):
    lw, lh = landscape(A4)
    max_w, max_h = lw - 2 * MARGIN, lh - 32 * mm - 24 * mm
    iw, ih = ImageReader(diagram).getSize()
    scale = min(max_w / iw, max_h / ih)
    return [
        NextPageTemplate("landscape"),
        PageBreak(),
        heading("APPENDIX", "Appendix: topology"),  # upper case, so no section key can collide with it
        Image(diagram, width=iw * scale, height=ih * scale),
        Spacer(1, 6),
        note(DIAGRAM_CAPTION),
    ]


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


class HandoffDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, "bookmark"):
            self.canv.addOutlineEntry(*flowable.bookmark, 0)


def template(name, pagesize):
    pw, ph = pagesize
    frame = Frame(MARGIN, 16 * mm, pw - 2 * MARGIN, ph - 32 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    return PageTemplate(id=name, frames=[frame], onPage=decorate, pagesize=pagesize)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", help="output PDF path, for example docs/<project>-<env>-handoff.pdf")
    parser.add_argument("--diagram", help="topology PNG for a landscape appendix page")
    args = parser.parse_args()

    doc = HandoffDoc(
        args.out,
        pagesize=A4,
        title=f"{PROJECT_ENV} infrastructure handoff, version {VERSION}",
        author=SENDER,
        subject=f"{PROJECT_ENV} infrastructure handoff for {RECIPIENT}, version {VERSION}",
    )
    doc.addPageTemplates([template("portrait", A4), template("landscape", landscape(A4))])
    story()  # The first pass numbers the sections, so the second pass resolves [[key]] references to later sections.
    repeated = sorted({k for k in KEYS if KEYS.count(k) > 1})
    if repeated:
        raise SystemExit(f"section key used more than once: {', '.join(repeated)}")
    flow = story()
    if args.diagram:
        flow += appendix(args.diagram)
    if REFS - NUMBER.keys():
        raise SystemExit(f"[[key]] names no section: {', '.join(sorted(REFS - NUMBER.keys()))}")
    doc.build(flow)
    print(args.out)


if __name__ == "__main__":
    main()
