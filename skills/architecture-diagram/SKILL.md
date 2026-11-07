---
name: architecture-diagram
description: Create technically accurate, editable architecture diagrams from a system concept and chosen technologies, platforms, and cloud providers. Supports draw.io XML and Mermaid.
---

# Architecture Diagram

Create technically accurate, editable architecture diagrams from the user's concept and technology choices.

## Workflow

1. Inspect the repository and supplied concept/specification files first.
2. Capture goal, actors, scope, requirements, technology choices, cloud/platform providers, integrations, protocols, data flows, trust boundaries, and desired output.
3. Ask only for missing decisions that materially affect the architecture. Mark assumptions explicitly.
4. Build a component inventory and connection list before drawing.
5. Choose draw.io when precise placement and routing matter; choose Mermaid for text-first, version-controlled diagrams.
6. Generate, validate, render, inspect, correct, and inspect again.

## Component model

Each component must have a stable ID, title, concise responsibility text, category/provider, optional icon reference, and boundary membership.

Each connection must have source and target IDs, direction, purpose/protocol label, sync/async classification, and optional security/data classification.

Use relevant layers such as users/channels, edge/API, application/services, data, AI/ML, integrations, and operations/security. Do not force irrelevant layers into a design.

## Icon sourcing

Use this order:
1. Official vendor architecture icon packs (AWS, Microsoft Azure, Google Cloud, Kubernetes, etc.).
2. Reputable brand icon catalogues such as Simple Icons or Iconify.
3. Consistent neutral pictograms when no suitable icon is available.

Fetch only icons actually used. Prefer SVG, preserve aspect ratio, and record source URL, retrieval date, license/terms, and attribution in `icon-library/manifest.json` or diagram-local `ASSETS.md`. Do not hotlink assets in final diagrams. Do not fabricate logos or imply a technology that is not in the design.

## Layout and routing — mandatory for draw.io

Use explicit coordinates and a consistent grid (20 px baseline). Typical node dimensions: 180–240 px wide and 90–120 px high, with 48–64 px gaps. Adapt to content, but align placements to the grid.

Every node has a title with responsibility text underneath. Keep text concise and inside the node.

Edges must attach to node boundaries:
- Vertical flow: source bottom boundary to target top boundary.
- Horizontal flow: source right boundary to target left boundary.
- Use orthogonal/elbow routing through reserved lanes.
- Never route through node text, icons, or node interiors.
- Put edge labels in clear lanes, away from junctions and node text.
- Keep edges behind nodes; avoid crossings and overlapping arrowheads.
- Use distinct routing lanes for multiple edges between the same components.

## Draw.io output

Create valid diagrams.net XML with stable cell IDs, explicit geometry, edge source/target references, and orthogonal waypoints where needed. Keep icons embedded or referenced locally. Provide the editable `.drawio` file and a preview when possible.

## Mermaid output

Create valid Mermaid flowchart source with stable IDs, clear labels, and subgraphs for meaningful boundaries. Mermaid layout is renderer-controlled; do not promise pixel-perfect placement or edge anchoring. Use Mermaid when maintainability and text diffs matter more than exact geometry.

## Validation and visual inspection — mandatory

- Validate XML or Mermaid syntax.
- Render a PNG/SVG preview using an available compatible renderer.
- Open and visually inspect the rendered image.
- Check clipping, readability, alignment, edge anchoring, routing, crossings, labels, direction, and canvas margins.
- Fix defects, render again, and inspect again.
- If rendering or visual inspection is unavailable, say exactly what could not be verified. Never claim visual inspection without performing it.

## Deliverables

Save source, preview, and any asset attribution in a clearly named directory such as `architecture/`. Include a short README describing format, assumptions, and editing instructions.
