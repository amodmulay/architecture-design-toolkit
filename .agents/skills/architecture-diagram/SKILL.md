---
name: architecture-diagram
description: Create or update editable software, cloud, data, AI, embedded, and connected-vehicle architecture diagrams from a system concept. Use when asked to draw, visualize, map, or generate an architecture diagram; outputs Draw.io or Mermaid.
---

# Architecture Diagram

Create technically accurate, editable architecture diagrams from the user's concept and technology choices. Treat the canonical architecture JSON as the source of truth; diagrams are generated views, not the primary model.

## Workflow

1. Inspect the repository and supplied concept/specification files first.
2. Capture goal, actors, scope, requirements, technology choices, cloud/platform providers, integrations, protocols, data flows, trust boundaries, and desired output.
3. Ask only for missing decisions that materially affect the architecture. Mark assumptions explicitly.
4. Build a component inventory, boundary inventory, and connection list.
5. Create or update a canonical JSON model conforming to `schemas/architecture.schema.json`. If the toolkit is not present in the working repository, use the installed skill's bundled instructions and ask before adding toolkit files or downloading dependencies.
6. Validate IDs, required fields, boundary references, and connection endpoints before drawing.
7. If the toolkit repository is available, use `tools/diagram-generator/diagramgen.py` to generate editable Draw.io XML. Otherwise create valid Draw.io XML directly or use Mermaid if the user prefers text-first diagrams; do not assume relative toolkit paths exist.
8. Render, inspect, correct, and re-render the diagram. Do not claim visual verification unless performed.

## Canonical model

The model contains:
- System name, description, scope, assumptions, and optional metadata.
- Boundaries such as trust zones, cloud accounts, regions, networks, or organizational domains.
- Components with stable IDs, concise responsibility, category, provider, technology, optional icon ID, boundary, and layer.
- Directed connections with stable IDs, source/target component IDs, labels, protocol, interaction mode, and optional data classification.
- Optional named views for future filtered diagrams.

Keep IDs stable across revisions. Preserve user-selected technologies. Do not invent components or connections to fill visual space. Distinguish confirmed facts from assumptions.

## Icon sourcing

Use this order:
1. Official vendor architecture icon packs (AWS, Microsoft Azure, Google Cloud, Kubernetes, etc.).
2. Reputable brand icon catalogues such as Simple Icons or Iconify.
3. Consistent neutral pictograms when no suitable icon is available.

Fetch only icons actually used. Prefer SVG, preserve aspect ratio, and record source URL, retrieval date, license/terms, and attribution in `icon-library/manifest.json` or diagram-local `ASSETS.md`. Do not hotlink assets in final diagrams. Do not fabricate logos or imply a technology that is not in the design.

## Draw.io layout and routing

Use explicit coordinates and a consistent grid (20 px baseline). Typical node dimensions: 180–240 px wide and 90–120 px high. Keep boundaries as clear lanes and place components within the appropriate lane.

Edges must attach to node boundaries:
- Prefer right-to-left or bottom-to-top flow where it matches the architecture.
- Use orthogonal/elbow routing through reserved lanes.
- Never route through node text, icons, or node interiors.
- Put edge labels in clear lanes, away from junctions and node text.
- Keep edges behind nodes; avoid crossings and overlapping arrowheads.
- Use distinct routing lanes for multiple edges between the same components.

The current generator provides deterministic lane placement and orthogonal waypoints. Complex graphs may need manual layout refinement; do not claim collision-free routing until that capability is implemented and verified.

## Generate with the toolkit

From the toolkit repository root:

```bash
python3 tools/diagram-generator/diagramgen.py architecture/model.json --out architecture/system.drawio
```

Validate without generating:

```bash
python3 tools/diagram-generator/diagramgen.py architecture/model.json --validate-only
```

The generator embeds uniquely resolved local SVG icons. Use icon IDs as paths relative to `icon-library/` or as unique SVG filenames/stems. Unresolved or ambiguous icons are omitted rather than guessed.

## Mermaid output

Create valid Mermaid flowchart source with stable IDs, clear labels, and subgraphs for meaningful boundaries. Mermaid layout is renderer-controlled; do not promise pixel-perfect placement or edge anchoring. Use Mermaid when maintainability and text diffs matter more than exact geometry.

## Validation and visual inspection — mandatory

- Validate model structure and references.
- Validate emitted XML syntax.
- Render a PNG/SVG preview using an available compatible renderer.
- Open and visually inspect the rendered image.
- Check clipping, readability, alignment, edge anchoring, routing, crossings, labels, direction, and canvas margins.
- Fix defects, render again, and inspect again.
- If rendering or visual inspection is unavailable, state exactly what could not be verified.

## Deliverables

Save source, preview, and asset attribution in a clearly named directory such as `architecture/`. Include a short README describing format, assumptions, and editing instructions.
