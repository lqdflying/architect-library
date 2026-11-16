# Layout And Style

Load before placing any element. Coordinates are Excalidraw scene units with the origin at the top left. The canvas is 2470 wide; its height follows the endpoint rows.

## Zone Map

```text
+----------------------------------------------------------------------------------+
| Title                                                             Route legend   |
| Subtitle                                                                         |
+----------------------------------------------------------------------------------+
| EXISTING SHARED PLATFORM  registry | private DNS | Log Analytics | cert vault    |
+----------------------------------------------------------------------------------+
      ^ dashed dependency lanes ^                   ^                 ^
 Users   +------------------+            VNet label          +--------------------+
   |     | Compute region   |           +-------------+      | PROJECT PaaS       |
   v     |  subnet boxes    |   Palo    | subnet box  |      |                    |
  F5 --->|  ingress > work ===> Alto ==+==> endpoint ---port->  service, caption  |
         |                  |    |      |   endpoint -------->  service, caption  |
 Datadog +------------------+    |      +-------------+      +--------------------+
           identities            v  \______________
+---------------------------------------------+   +-------------------------------+
| EXTERNAL DEPENDENCIES                       |   | Central AI service            |
| integration estate | other cloud | internet |   | endpoint > APIM > Foundry     |
+---------------------------------------------+   +-------------------------------+
```

The reader's eye runs left to right along one line: users, edge, compute, firewall, private endpoint, service. Shared platform services sit above that line. External systems and the central AI service sit below it, so no dependency arrow crosses the main flow.

## Zones

| Zone | x | y | Size | Contents |
|---|---|---|---|---|
| Title | 40 | 24 | | One line |
| Subtitle | 40 | 72 | Two lines at most | Status and scope |
| Legend | 1900 | 24 | One line per route family, 22 apart | Colored text, no boxes |
| Shared-platform band | 40 | 140 | 2430 x 230 | Title at (65, 154). Icons at y 232, x 120, 700, 1330, 1900. Caption 84 right of each icon at y 224 |
| Dependency lanes | | 380 to 430 | | Horizontal runs of the dashed arrows at y 390 and y 405 |
| Entry column | 20 to 270 | | | User ellipse at (57, 815), 174 x 76. Edge icon at (112, ingress row - 32). Monitoring icon below the edge caption |
| Compute region | 350 | 440 | 650 wide | Title at (375, 458). Subnet boxes at x 375, 600 wide |
| Firewall node | 1090 | ingress row - 32 | 64 icon | Caption above, centered on the icon |
| Trunk | 1260 | | | The vertical run every endpoint arrow shares |
| Endpoint subnets | 1450 | from 495 | 310 wide | VNet label 32 above the first box of each VNet. Endpoint icon at x 1475 |
| Project PaaS box | 1820 | 440 | 650 wide | Header at (1840, 454), three lines. Service icon at x 1850, caption at x 1935 |
| External band | 40 | 70 below the lower of the lowest box bottom and the identities block (icon and caption) | 1360 x 240 | Title 14 below the top edge. Three item slots at x 80, 560, 960, icons 92 below the top edge. Caption 84 right of an icon. A boxed item is 170 x 68 with its caption 16 right of the box |
| Central AI service box | 1450 | same top as the external band | 1020 x 330 | See [Central AI Service Box](#central-ai-service-box) |

Icon sizes: 64 for services, compute, edge, firewall, and band items. 48 for private endpoints.

Without a central AI service, the external band is 2430 wide with four item slots at x 100, 700, 1330, 1880. Without external systems, the Central AI service box keeps its place and the band is dropped.

### Rows

An endpoint and its service share one row. Place the endpoint rows first.

| Element | Position |
|---|---|
| First row in a subnet box | Row center = box top + 88 |
| Next row in the same box | + 131 |
| Subnet box bottom | Last row center + 94 |
| Next subnet box, same VNet | 20 below the previous box |
| Next subnet box, new VNet | 55 below, with the VNet label in the gap |
| Subnet header | (box x + 18, box top + 12), two lines: subnet name, CIDR |
| Endpoint icon | (1475, row - 24) |
| Endpoint caption | (1468, row + 34), two lines |
| Port label | (1640, row - 26) |
| Service icon | (1850, row - 32) |
| Service caption | (1935, row - 40) for four lines, (1935, row - 30) for three |
| PaaS box bottom | Last subnet box bottom + 15 |

The ingress row is the y of the single horizontal line from the edge icon to the firewall icon. In the default AKS region it is compute region top + 584.

### Compute Region, AKS

Offsets from the region origin (350, 440). The default region is 650 x 890.

| Element | Offset | Notes |
|---|---|---|
| Region title | (25, 18) | Two lines at 20px: subscription, VNet name |
| Pending note | (340, 20) | Amber. Only when the subnet pair or the cluster is not allocated |
| API subnet box | (25, 95), 600 x 180 | Header at (45, 109): subnet name and CIDR, then "Delegated API subnet" |
| Cluster icon and caption | (80, 180), caption (170, 182) | "Private AKS control plane", cluster name, API server mode |
| Node subnet box | (25, 310), 600 x 465 | Header at (45, 324): subnet name and CIDR, then the network mode |
| System pool icon and caption | (80, 388), caption (170, 390) | Pool name, node count, VM size |
| Ingress load balancer icon | (80, 552) | Caption below at (45, 624) |
| Gateway box | (220, 545), 170 x 78 | Fill `#dbeafe`. Routing label above at (180, 518), add-on caption below at (220, 632) |
| Workload pool icon | (440, 552) | Pool caption above at (385, 462) |
| Workload list | (45, 690) | Component names, one or two lines |
| Region footer | (45, 804) | Node resource group, pod and service CIDRs, DNS service IP, Kubernetes version |
| Identities icon and caption | (110, 945), caption (195, 935) | Below the region. One line per identity role |

### Central AI Service Box

Draw this box when the project calls a shared AI gateway. Offsets from the box origin (1450, T), where T is the top it shares with the external band.

| Element | Offset | Notes |
|---|---|---|
| Title | (150, 14) | 18px. Starts right of the incoming arrow |
| Subtitle | (150, 40) | Which environments the service covers, and that another team manages it |
| Gateway endpoint icon | (50, 80), 48 | Caption at (20, 138), three lines: `AI gateway endpoint`, address, subnet |
| API Management icon | (340, 72), 64 | Caption centered below at y 146: `API Management`, `AI gateway` |
| Foundry icon | (690, 72), 64 | Caption centered below at y 146: `Shared Foundry account`, account kind, how callers are separated |
| Endpoint to API Management | Row y 104 | Green arrow, port label at (170, 78) |
| API Management to Foundry | Row y 104 | Green arrow, label `To <PROJECT> project` at (474, 78) |
| Call panel | (220, 220), 440 x 58 | Two lines: `Host: <gateway hostname>` and `<header>: <what the caller sends>`. A description, never a key value |
| Panel note | (676, 220) | Where the key is kept and who enters it |
| Pending line | (20, 292) | Amber. Only when the authentication method or the service for this environment is not settled |

The endpoint address and subnet come from a live read or the owning team's design, not from another project's drawing.

### Other Compute

- **App Service or Functions.** The region holds the VNet integration subnet box with the plan and the apps. Each app's inbound private endpoint is a row at the top of the endpoint column, and the edge arrow ends on that endpoint, not on the app.
- **Virtual machine.** The VM icon sits in its subnet box inside the region. Its caption carries the hostname, static address, size, and image.
- **No Kubernetes.** Drop the API subnet box and move the remaining boxes up.

## Style Tokens

All text is `fontFamily: 3`. All shapes are `roughness: 0`, `opacity: 100`, sharp corners (no `roundness`).

| Element | Token |
|---|---|
| Title | 30px, `#1e40af` |
| Subtitle | 16px, `#64748b` |
| Band title | 18px, `#1e40af`, upper-case zone name first |
| Region title | 20px, `#1e40af` |
| VNet label | 16px, `#1e40af` |
| Subnet header, endpoint caption, secondary note | 16px, `#64748b` |
| Service, compute, and band item caption | 16px, `#374151` |
| PaaS box header | 16px, `#047857` |
| Port label | 16px, `#047857` |
| Pending text | 16px, `#b45309` |
| Compute region boundary | `#1e3a5f`, solid, width 2, no fill |
| Subnet box | `#3b82f6`, dashed, width 1, no fill |
| Project PaaS box | `#047857`, solid, width 2, no fill |
| Shared-platform band | `#1e40af`, dashed, width 2, no fill |
| External band, Central AI service box | `#64748b`, dashed, width 2, no fill |
| Call panel | Box `#1e293b`, width 1, fill `#1e293b`, text 16px `#22c55e` |
| In-region component box | `#1e3a5f`, solid, width 1, fill `#dbeafe` |
| Non-Azure system without a cached icon | Box `#c2410c`, solid, width 2, fill `#fed7aa`, text `#374151` |
| User actor | Ellipse `#1e3a5f`, width 2, fill `#93c5fd`, text `#374151` |

Boundaries carry no fill. Color is on strokes, routes, and text.

## Route Key

| Family | Arrow | Legend line |
|---|---|---|
| Workload path: users to edge, edge to ingress, workload to firewall, firewall to each endpoint, firewall to the AI gateway endpoint, firewall to the external band | `#1e3a5f`, solid, width 2. The workload-to-firewall segment is width 3 | `Navy solid: workload path through the Palo Alto pair` |
| Private endpoint to its service, including the two arrows inside the Central AI service box | `#047857`, solid, width 2 | `Green solid: private endpoint to its service` |
| Deployment or administration: apply host, kubectl host, CI runner | `#c2410c`, solid, width 2 | `Orange solid: deployment and admin access` |
| Logical or shared-platform dependency: image pull, DNS zone, zone groups, diagnostics, identity federation, monitoring agent | `#64748b`, dashed, width 1 | `Gray dashed: logical or shared-platform dependency` |
| Pending or conditional path | `#b45309`, dashed, width 2 | `Amber: pending decision or NetOps request` |

Each legend line is text in its own family color. List only the families the drawing uses. Reword a legend line to name the real firewall or the real owner of the pending item.

## Routing

- **Ingress row.** One straight horizontal line: edge icon, ingress load balancer, gateway box, workload icon, firewall icon. Labels sit above the line.
- **Firewall fan-out.** One arrow per endpoint. Every arrow leaves the right side of the firewall icon, runs to the trunk at x 1260, turns to its row, and ends on the endpoint icon. The shared first segment is intended.
- **Endpoint to service.** One straight arrow on the row, with the port label above it.
- **Shared-platform dependencies.** Dashed arrows leave the top edge of the compute region, of the first endpoint subnet box, and of the PaaS box. They fold in the lanes at y 390 and y 405 and enter the band icon from below. Give two arrows that end on one icon separate x positions 32 apart. Check that no two of these arrows cross.
- **External band.** One vertical arrow from the bottom of the firewall icon, 16 left of its center, to the top edge of the band, bound to the band rectangle. Its label is right-aligned on the left of the arrow, 80 above the band and below the last trunk turn.
- **Central AI service.** One arrow from the bottom of the firewall icon, 16 right of its center. It runs down to a lane 30 above the box, right to the center of the gateway endpoint icon, and down into that icon. Its label sits above the lane. Inside the box the two arrows are straight on one row.
- **Identities.** A dashed arrow from the identities icon up to the bottom edge of the compute region.
- **Monitoring agent.** A dashed arrow from the left edge of the compute region to the monitoring icon in the entry column.

## Text Templates

| Element | Template |
|---|---|
| Title | `<PROJECT> <env> \| Private Azure infrastructure` |
| Subtitle, line 1 | `<design status> \| <region> \| <what is still pending and who allocates it>` |
| Subtitle, line 2 | How the other environments differ, when the design has more than one |
| Shared-platform band title | `EXISTING SHARED PLATFORM \| <subscription> \| resolve by name; no remote state or duplicate services` |
| External band title | `EXTERNAL DEPENDENCIES \| reached through the <firewall> \| owned outside this repository` |
| Central AI service box title | `Central AI service \| <owning team>` |
| Central AI service box subtitle | `Shared <nonPROD or PROD> service \| managed outside this repository` |
| PaaS box header | `PROJECT PaaS \| <SUBSCRIPTION>` / resource group name / `Public network access OFF \| outside VNets` |
| Subnet header | Subnet name / CIDR |
| Endpoint caption | `<Service> private endpoint` / static address, or `<endpoint short name> \| IP pending` |
| Port label | Protocol and port: `TLS 5432`, `HTTPS 443`, `AMQPS 5671`, `NFS 2049` |
| Service caption | Service and tier / resource name / the two settings a reviewer checks first, such as availability, authentication, SKU / what is pending |
| Band item caption | Role and owner / resource name or address / what this project uses / what it must not create or what is pending |
| Edge caption | `Existing F5 edge` / `TLS termination` / published hostnames / `Hostnames: proposed` until agreed |
| Firewall caption | `Existing Palo Alto pair` / hub VNet / `Spoke-to-spoke access` / `and external egress` |

Use `|` to separate facts on one line. Keep a caption to four lines; move the rest to the design document.

## Not On This Drawing

- A tall bar, swim lane, or bus standing in for the firewall. The firewall is one icon.
- Rounded boundaries, filled boundaries, warning callouts.
- A dark panel anywhere except the call panel of the Central AI service box.
- A shared AI gateway drawn as a single icon in the external band.
- A color per arrow, or a color outside the route key.
- Placeholder tokens such as `{env}` or `<N>` where the real value is known. A value that is not allocated yet is written as pending, in amber.
- Apply order, phases, role assignments, or a list of open questions.
