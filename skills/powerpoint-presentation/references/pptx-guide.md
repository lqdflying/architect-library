# PowerPoint (.pptx) Presentation Guide

> Custom instruction for AI coding assistants (Cursor, Claude Code, etc.)
> Libraries: `pptxgenjs` for creation, raw XML for template editing
> License: MIT (this guide) | Libraries follow their own licenses

## Decision Matrix

| Task | Tool |
|------|------|
| Create new .pptx from scratch | `pptxgenjs` |
| Edit/populate an existing template | Unzip -> edit XML -> rezip |
| Read / extract text | `pandoc` or unzip + parse XML |
| Convert .pptx to PDF | LibreOffice headless |
| Convert slides to images | LibreOffice -> PDF -> `pdftoppm` |

---

## Part 1: Creating Presentations with PptxGenJS

### Install

```bash
npm install -g pptxgenjs
# For icons (optional):
npm install -g react-icons react react-dom sharp
```

### Minimal Example

```javascript
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Author Name";
pres.title = "Presentation Title";

const slide = pres.addSlide();
slide.addText("Hello World", {
  x: 0.5, y: 0.5, w: 9, h: 1,
  fontSize: 36, fontFace: "Arial", color: "363636", bold: true
});

pres.writeFile({ fileName: "output.pptx" });
```

### Slide Dimensions

All coordinates are in inches.

| Layout | Width | Height |
|--------|-------|--------|
| `LAYOUT_16x9` | 10" | 5.625" |
| `LAYOUT_16x10` | 10" | 6.25" |
| `LAYOUT_4x3` | 10" | 7.5" |
| `LAYOUT_WIDE` | 13.3" | 7.5" |

---

### Text

```javascript
// Basic text box
slide.addText("Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.8,
  fontSize: 36, fontFace: "Georgia", color: "1E2761",
  bold: true, align: "left", valign: "middle"
});

// Rich text (mixed formatting)
slide.addText([
  { text: "Bold part ", options: { bold: true } },
  { text: "and italic part", options: { italic: true } }
], { x: 0.5, y: 1.5, w: 9, h: 1 });

// Multi-line text (breakLine is required between lines)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 0.5, y: 2.5, w: 8, h: 2 });

// Character spacing (NOT letterSpacing, which is silently ignored)
slide.addText("SPACED TITLE", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });
```

**Padding tip:** Text boxes have internal margin by default. Set `margin: 0` when you need text edges to align precisely with shapes or icons at the same x-coordinate.

### Lists and Bullets

```javascript
// Bullet list
slide.addText([
  { text: "First point", options: { bullet: true, breakLine: true } },
  { text: "Second point", options: { bullet: true, breakLine: true } },
  { text: "Third point", options: { bullet: true } }
], { x: 0.5, y: 1, w: 8, h: 3, fontSize: 16 });

// Numbered list
slide.addText([
  { text: "Step one", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Step two", options: { bullet: { type: "number" } } }
], { x: 0.5, y: 1, w: 8, h: 2 });

// Sub-items (indented)
slide.addText([
  { text: "Main item", options: { bullet: true, breakLine: true } },
  { text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
], { x: 0.5, y: 1, w: 8, h: 2 });
```

Never use unicode bullet characters like `"* "` or `"\u2022 "` — this creates double bullets.

### Shapes

```javascript
// Rectangle
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.5, w: 4, h: 2.5,
  fill: { color: "1E2761" },
  line: { color: "CADCFC", width: 1 }
});

// Rounded rectangle
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  rectRadius: 0.1
});

// Line
slide.addShape(pres.shapes.LINE, {
  x: 0.5, y: 3, w: 9, h: 0,
  line: { color: "CCCCCC", width: 1, dashType: "dash" }
});

// Oval
slide.addShape(pres.shapes.OVAL, {
  x: 4, y: 1, w: 2, h: 2,
  fill: { color: "0088CC" }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 5.625,
  fill: { color: "000000", transparency: 40 }
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  shadow: {
    type: "outer", color: "000000", blur: 6,
    offset: 2, angle: 135, opacity: 0.15
  }
});
```

Shadow properties:

| Property | Type | Notes |
|----------|------|-------|
| `type` | `"outer"` or `"inner"` | |
| `color` | 6-char hex | No `#` prefix, no 8-char hex |
| `blur` | 0-100 | Points |
| `offset` | 0-200 | Must be non-negative (negative corrupts file) |
| `angle` | 0-359 | 135 = bottom-right, 270 = upward |
| `opacity` | 0.0-1.0 | Use this for transparency, never encode in color |

Upward shadow: use `angle: 270` with positive offset. Never use negative offset.

### Images

```javascript
// From file path
slide.addImage({ path: "photo.jpg", x: 1, y: 1, w: 5, h: 3 });

// From URL
slide.addImage({ path: "https://example.com/img.jpg", x: 1, y: 1, w: 5, h: 3 });

// From base64 (no file I/O, faster)
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });

// Sizing modes
slide.addImage({ path: "img.jpg", x: 1, y: 1, w: 4, h: 3,
  sizing: { type: "contain", w: 4, h: 3 }  // fit inside, keep ratio
});
slide.addImage({ path: "img.jpg", x: 1, y: 1, w: 4, h: 3,
  sizing: { type: "cover", w: 4, h: 3 }    // fill area, may crop
});

// Circular crop
slide.addImage({ path: "avatar.jpg", x: 1, y: 1, w: 1.5, h: 1.5, rounding: true });
```

Preserve aspect ratio when calculating dimensions:
```javascript
const origW = 1978, origH = 923, maxH = 3.0;
const calcW = maxH * (origW / origH);
const centerX = (10 - calcW) / 2;
slide.addImage({ path: "img.png", x: centerX, y: 1.2, w: calcW, h: maxH });
```

### Icons (react-icons -> PNG -> slide)

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuf.toString("base64");
}

// Usage
const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.5, h: 0.5 });
```

Use rasterization size >= 256 for crisp icons. The `size` param controls render resolution, not display size on slide (that's `w`/`h`).

Available icon sets: `react-icons/fa` (Font Awesome), `react-icons/md` (Material), `react-icons/hi` (Heroicons), `react-icons/bi` (Bootstrap).

### Backgrounds

```javascript
slide.background = { color: "1E2761" };                        // solid
slide.background = { color: "FF3399", transparency: 50 };      // with transparency
slide.background = { path: "https://example.com/bg.jpg" };     // image URL
slide.background = { data: "image/png;base64,iVBORw0KGgo..." }; // image base64
```

### Tables

```javascript
slide.addTable([
  [
    { text: "Header 1", options: { fill: { color: "1E2761" }, color: "FFFFFF", bold: true } },
    { text: "Header 2", options: { fill: { color: "1E2761" }, color: "FFFFFF", bold: true } }
  ],
  ["Row 1 Col 1", "Row 1 Col 2"],
  ["Row 2 Col 1", "Row 2 Col 2"]
], {
  x: 0.5, y: 1, w: 9, colW: [4.5, 4.5],
  border: { pt: 1, color: "CCCCCC" },
  fontSize: 14
});

// Merged cells
[{ text: "Spans two columns", options: { colspan: 2, align: "center" } }]
```

### Charts

Use native charts whenever PowerPoint supports the chart type. Only fall back to rendered images for chart types PowerPoint cannot represent (Sankey, network graphs, etc.).

```javascript
// Bar / Column
slide.addChart(pres.charts.BAR, [{
  name: "Revenue",
  labels: ["Q1", "Q2", "Q3", "Q4"],
  values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.8, w: 9, h: 4, barDir: "col",
  showTitle: true, title: "Quarterly Revenue",
  chartColors: ["0D9488"],
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showValue: true,
  dataLabelPosition: "outEnd",
  dataLabelColor: "1E293B",
  showLegend: false
});

// Line
slide.addChart(pres.charts.LINE, [{
  name: "Temperature",
  labels: ["Jan", "Feb", "Mar", "Apr"],
  values: [32, 35, 42, 58]
}], { x: 0.5, y: 1, w: 6, h: 3, lineSize: 3, lineSmooth: true });

// Pie
slide.addChart(pres.charts.PIE, [{
  name: "Market Share",
  labels: ["Product A", "Product B", "Other"],
  values: [35, 45, 20]
}], { x: 6, y: 1, w: 4, h: 4, showPercent: true });
```

Available native types: `BAR`, `LINE`, `AREA`, `PIE`, `DOUGHNUT`, `SCATTER`, `BUBBLE`, `RADAR`. For combo charts, pass an array of `{type, data, options}` objects.

For trendlines: compute the regression series yourself and add as a second `LINE` or `SCATTER` data series. Do not render to image.

### Slide Masters

```javascript
pres.defineSlideMaster({
  title: "TITLE_SLIDE",
  background: { color: "1E2761" },
  objects: [{
    placeholder: {
      options: { name: "title", type: "title", x: 1, y: 2, w: 8, h: 2 }
    }
  }]
});

const titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("Welcome", { placeholder: "title", color: "FFFFFF" });
```

---

## Part 2: Editing Existing Presentations (Template Workflow)

When you have an existing .pptx to modify (e.g., branded template):

### Step 1: Analyze

Convert to thumbnails for visual overview, then extract text to see placeholder content.

```bash
# Visual overview
libreoffice --headless --convert-to pdf template.pptx
pdftoppm -jpeg -r 100 template.pdf thumb

# Text extraction
pandoc template.pptx -t plain -o content.txt
```

### Step 2: Plan Slide Mapping

Map your content sections to template slide layouts. Prioritize layout variety:
- Title slides for section openers
- Multi-column layouts for comparisons
- Image + text combos for features
- Stat callout slides for key numbers
- Quote/testimonial slides

Avoid repeating the same text-heavy bullet layout on every slide.

### Step 3: Unpack

```bash
mkdir unpacked && cd unpacked
unzip ../template.pptx
```

Key structure:
- `ppt/presentation.xml` — slide order (`<p:sldIdLst>`)
- `ppt/slides/slide1.xml`, `slide2.xml`, ... — individual slides
- `ppt/slideLayouts/` — layout definitions
- `ppt/slideMasters/` — master slide definitions
- `ppt/media/` — embedded images
- `ppt/_rels/presentation.xml.rels` — relationships

### Step 4: Structural Changes

All structural changes (add/remove/reorder slides) must be done before content editing.

**Reorder slides:** Rearrange `<p:sldId>` elements in `<p:sldIdLst>` within `ppt/presentation.xml`.

**Delete slides:** Remove the `<p:sldId>` entry, then delete the orphaned slide XML, its rels file, and its entry in `[Content_Types].xml`.

**Duplicate slides:** Copy `slideN.xml` to a new filename, create its `.rels` file, add entries in `[Content_Types].xml` and `presentation.xml.rels`, then add a `<p:sldId>` entry.

### Step 5: Edit Content

For each slide XML, identify text placeholders and replace content.

**Formatting rules:**
- Bold all titles and inline labels: set `b="1"` on `<a:rPr>`
- Never use unicode bullets `\u2022` — use `<a:buChar>` or `<a:buAutoNum>`
- For multi-item content, create separate `<a:p>` elements, never concatenate into one string
- Copy `<a:pPr>` from the original paragraph to preserve line spacing
- Use smart quote XML entities: `&#x201C;`, `&#x201D;`, `&#x2018;`, `&#x2019;`
- Add `xml:space="preserve"` on `<a:t>` elements with leading/trailing whitespace

Example of properly structured multi-item content:
```xml
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="2400"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="1800" b="1"/><a:t>Step 1: Setup</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="2400"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="1800"/><a:t>Install dependencies and configure the environment.</a:t></a:r>
</a:p>
```

### Step 6: Repack

```bash
cd unpacked
zip -r ../output.pptx . -x "*.DS_Store"
```

### Template Adaptation Pitfalls

- **Template has more slots than your data:** Remove excess elements entirely (shapes, images, text boxes), not just clear text. Empty shapes leave visual holes.
- **Content longer than template expects:** May overflow or wrap unexpectedly. Reduce font size, split across slides, or enlarge the container.
- **XML namespace corruption:** Use a DOM parser that preserves namespaces (`defusedxml.minidom`, not `xml.etree.ElementTree`).

---

## Part 3: Visual Design Principles

### Color Palette Selection

Pick colors that match your specific topic. A palette that works for any presentation is too generic.

**The 60-30-10 rule:** One dominant color (60%), one supporting color (30%), one accent (10%). Never give all colors equal weight.

**Background strategy:** Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium look.

Example palettes:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Midnight Executive | `1E2761` | `CADCFC` | `FFFFFF` |
| Forest & Moss | `2C5F2D` | `97BC62` | `F5F5F5` |
| Coral Energy | `F96167` | `F9E795` | `2F3C7E` |
| Warm Terracotta | `B85042` | `E7E8D1` | `A7BEAE` |
| Ocean Gradient | `065A82` | `1C7293` | `21295C` |
| Charcoal Minimal | `36454F` | `F2F2F2` | `212121` |
| Teal Trust | `028090` | `00A896` | `02C39A` |
| Berry & Cream | `6D2E46` | `A26769` | `ECE2D0` |
| Cherry Bold | `990011` | `FCF6F5` | `2F3C7E` |

### Typography

Choose a distinctive header font paired with a clean body font:

| Header | Body |
|--------|------|
| Georgia | Calibri |
| Arial Black | Arial |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Palatino | Garamond |

Size guide:

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt, muted color |

### Layout Variety

Every slide needs at least one visual element (image, chart, icon, or shape). Pure text slides are forgettable.

**Layout options to rotate through:**
- Two-column: text left, visual right
- Icon + text rows: icon in colored circle, bold header, description below
- Grid: 2x2 or 2x3 content blocks
- Half-bleed image: full-height image on one side, content on other
- Large stat callout: big number (60-72pt) with label below
- Comparison columns: before/after, pros/cons
- Timeline or process flow: numbered steps with connecting elements

**Pick ONE visual motif and repeat it** across slides (e.g., rounded image frames, icons in colored circles, thick left-border accent bars).

### Spacing

- 0.5" minimum margins from slide edges
- 0.3-0.5" between content blocks, consistent throughout
- Leave breathing room; do not fill every inch

### Common Design Mistakes

- Repeating the same layout on every slide
- Center-aligning body text (left-align paragraphs; center only titles)
- Weak size contrast between title and body
- Defaulting to blue without considering topic
- Inconsistent spacing between elements
- Styling one slide but leaving others plain
- Low contrast: light text on light background, or dark icons on dark background
- Text boxes too narrow, causing excessive wrapping
- Text overflowing its container (always verify fit)
- Using decorative accent lines under titles (reads as AI-generated)
- Adding full-width colored bars/stripes as decoration without purpose
- Using cream/beige as default background when white would be cleaner

---

## Part 4: QA Workflow

### Content Verification

After generating slides, extract text and check for:
- Missing content
- Wrong order
- Typos
- Leftover placeholder text from templates

```bash
pandoc output.pptx -t plain | grep -iE "lorem|ipsum|TODO|\[insert|xxx"
```

### Visual Verification

Use the shared thumbnail tool first (see `layout-preview.md`):

```bash
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview --cols 4
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview \
  --per-slide /tmp/deck-slides --dpi 150 --no-grid
```

Manual fallback:

```bash
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

**Checklist for each slide:**
- Text fits within its container (no overflow or clipping)
- No overlapping elements
- Elements maintain at least 0.3" gap
- Minimum 0.5" margin from slide edges
- Consistent alignment across similar elements
- Adequate contrast for both text and icons
- No stale placeholder content

### Fix Cycle

1. Generate → validate → `thumbnail` grid + `--per-slide` JPEGs → **view images**
2. Fix issues in pptxgenjs source or unpacked XML
3. Re-preview only affected slides
4. Stop after one fix cycle unless new user-visible defects appear (overlap, overflow, missing content)
5. Do not iterate on sub-pixel positioning or minor cosmetic tweaks

---

## Critical Rules Summary (PptxGenJS)

1. **Never use `#` in hex colors** — causes file corruption (`"FF0000"` not `"#FF0000"`)
2. **Never encode opacity in hex color string** — 8-char colors like `"00000020"` corrupt the file; use `opacity` property
3. **Use `bullet: true`** — never unicode bullet characters
4. **Use `breakLine: true`** between text array items for multi-line text
5. **Avoid `lineSpacing` with bullets** — causes excess gaps; use `paraSpaceAfter`
6. **New instance per presentation** — never reuse `pptxgen()` objects
7. **Never reuse option objects across calls** — PptxGenJS mutates them in-place (e.g., converts shadow values to EMU); use factory functions
8. **Do not pair `ROUNDED_RECTANGLE` with rectangular accent overlays** — the overlay won't cover rounded corners; use `RECTANGLE` instead
9. **Shadow offset must be non-negative** — negative values corrupt the file
10. **Gradient fills are not supported** — use a gradient image as background instead
