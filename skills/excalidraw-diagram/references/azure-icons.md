# Official Azure Icons

Every Azure diagram uses the official icon for each Azure service it shows, including when you edit an existing diagram that drew those services as boxes. Keep the service name as a caption and preserve the node's bindings and routes. If `search` finds no icon for a service after retrying a distinctive word and the service's former name (for example, Azure AI Search is filed as Cognitive-Search), use a labeled box for that service and name the gap in your reply. The skill bundles Microsoft's unmodified V24 SVG archive at `assets/azure/Azure_Public_Service_Icons_V24.zip`; `assets/azure/manifest.json` records the source, version and SHA-256. No download or extraction is needed for normal use. The normal skill installer copies this asset directory with the rest of the skill.

## Find And Embed

From the skill directory:

```bash
python3 references/azure_icons.py search "Databricks"
python3 references/azure_icons.py search "Private Endpoints"
```

Choose an exact returned path; category duplicates are not different services. Create or reuse an Excalidraw `image` element with its own stable ID, coordinates, dimensions, `scale: [1, 1]`, `angle: 0` and reciprocal arrow bindings. Then embed the selected artwork:

```bash
python3 references/azure_icons.py embed /path/to/diagram.excalidraw \
  --icon 'workspace_icon=analytics/10787-icon-service-Azure-Databricks.svg' \
  --icon 'endpoint_icon=other/02579-icon-service-Private-Endpoints.svg'
```

The helper checks the cache checksum, resolves exact archive paths and fills `files` entries with `mimeType: image/svg+xml` and a base64 `dataURL`. It assigns each selected node the content-derived `fileId` and saved status. It creates no nodes or connections and preserves coordinates, labels, bindings and unrelated assets. Repeating an identical selection is a no-op. Invalid selections fail before writing the scene, including an image node whose width/height ratio differs from the icon's viewBox by more than 2%. The scene is replaced atomically and keeps its file mode. Search matches service file names first and falls back to category paths such as `networking`. The output diagram is self-contained and does not depend on the skill cache to render later.

## Visual And Semantic Checks

- Preserve the official artwork: no recoloring, cropping, flipping, rotation or distortion. Scale proportionally using the SVG's viewBox or width/height ratio.
- Place the service name close to the icon, on the side that leaves its connection points and nearby routes clear. Captions need not all be below the icons.
- Group each icon with its caption. Bind relationship arrows to the image node, not to the caption; update both ends' `boundElements`.
- Use a service icon only for that actual service. Do not use a familiar icon to imply unverified infrastructure or runtime behavior.
- Before delivery, verify every `fileId` resolves, then render and inspect the icons and their routes. Never treat successful base64 embedding as proof of a correct image render.

## Source And Terms

[Microsoft Azure architecture icons](https://learn.microsoft.com/azure/architecture/icons/) permits copying, distributing and displaying the icons for architectural diagrams, training materials and documentation; other rights are reserved. The original `Microsoft_Terms_of_Use.pdf` is retained inside the archive. This permission is not a general-purpose license for branding or representing your own product. Do not alter Microsoft's artwork.

**Why the archive is bundled.** This skill exists to draw architecture diagrams, which is the use Microsoft permits. The archive ships unmodified, with Microsoft's terms and FAQ, so diagrams can be drawn offline and every diagram embeds the same checksum-verified artwork. Bundling adds no rights: icons copied out of this skill remain under Microsoft's terms. Do not extract them for any other purpose, such as a product logo, app icon or general-purpose icon pack. This is the maintainers' reading of those terms, not legal advice.

The cache was retrieved on 2026-10-06 from the versioned URL recorded in the manifest. It is a pinned snapshot, not a claim to be the latest package. Refresh only as an explicit maintenance action: download the official versioned archive, verify its source and terms, update the archive and manifest together, and run the helper tests plus a rendered icon check. Never fetch or replace the cache automatically while drawing.