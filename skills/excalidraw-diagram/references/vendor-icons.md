# Vendor icons

When a diagram node is F5, Palo Alto Networks, NGINX, or Datadog, use the cached SVG for that product. Keep the product name as a caption and preserve the node's bindings and routes. These marks identify only those products. A generic load balancer, firewall, proxy, or monitoring service stays a labeled shape from `shape-and-layout.md`.

The skill bundles four unmodified SVGs from Simple Icons 16.0.0 at `assets/vendors/`. `assets/vendors/manifest.json` records the version, source, brand hex, and SHA-256 of each file. `assets/vendors/TERMS.md` records the use limit. No download is needed during drawing. The normal skill installer copies this asset directory with the rest of the skill.

## Find and embed

From the skill directory:

```bash
python3 references/vendor_icons.py search "Palo Alto"
python3 references/vendor_icons.py search "Datadog"
```

Choose an exact returned path. Create or reuse an Excalidraw `image` element with its own stable ID, coordinates, dimensions, `scale: [1, 1]`, `angle: 0`, and reciprocal arrow bindings. These icons are square (`viewBox="0 0 24 24"`), so a 64×64 node matches. Then embed the selected artwork:

```bash
python3 references/vendor_icons.py embed /path/to/diagram.excalidraw \
  --icon 'edge_icon=f5.svg' \
  --icon 'monitor_icon=datadog.svg'
```

The helper checks each cache checksum, resolves exact file names, and fills `files` entries with `mimeType: image/svg+xml` and a base64 `dataURL`. The stored SVG has no fill. The embedded copy sets `fill` on the root `<svg>` to the brand hex in the manifest and leaves the path data unchanged. It assigns each selected node a `fileId` derived from those filled bytes and saved status. It creates no nodes or connections and preserves coordinates, labels, bindings, and unrelated assets. Repeating an identical selection is a no-op. Invalid selections fail before writing the scene, including an image node whose width/height ratio differs from the icon viewBox by more than 2%. The scene is replaced atomically and keeps its file mode. The output diagram is self-contained and does not depend on the skill cache to render later.

## Visual and semantic checks

- Preserve the path artwork. The brand fill comes only from the manifest hex. Scale proportionally.
- Place the product name close to the icon, on the side that leaves its connection points and nearby routes clear. Captions need not all be below the icons.
- Group each icon with its caption. Bind relationship arrows to the image node, not to the caption; update both ends' `boundElements`.
- Use a product icon only for that product.
- Before delivery, verify every `fileId` resolves, then render and inspect the icons and their routes. Never treat successful base64 embedding as proof of a correct image render.

## Source and terms

[Simple Icons 16.0.0](https://github.com/simple-icons/simple-icons/releases/tag/16.0.0) is the source of the four files. The Simple Icons project is released under [CC0 1.0](https://github.com/simple-icons/simple-icons/blob/16.0.0/LICENSE.md). The [project disclaimer](https://github.com/simple-icons/simple-icons/blob/16.0.0/DISCLAIMER.md) says individual brand marks can still be trademarked. These four titles have no license field in that release's icon data. `assets/vendors/TERMS.md` is the use limit for this skill: architecture diagrams that identify F5, Palo Alto Networks, NGINX, or Datadog. Do not alter the path, and do not extract the files for a product logo, app icon, or general-purpose icon pack. This is the maintainers' reading of those terms, not legal advice.

The cache was retrieved on 2026-10-10 from the tag recorded in the manifest. It is a pinned snapshot, not a claim to be the latest set. Refresh only as an explicit maintenance action: download the same four files from the pinned tag, verify their source and checksums, update the files and manifest together, and run the helper tests. Never fetch or replace the cache while drawing.
