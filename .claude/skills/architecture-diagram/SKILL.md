---
name: architecture-diagram
description: Create architecture, system, cloud, infrastructure, technology-stack, AI and connected-vehicle diagrams from natural-language descriptions, existing specs or code. Use for diagramming requests even when no output format is specified. Produces editable Draw.io and, when suitable, self-contained HTML or PNG previews.
---

# Architecture Diagram

Create technically accurate, clear and visually polished architecture diagrams. The user's experience should be simple: describe the system in natural language, and the skill handles architecture extraction, icon selection, layout, generation and verification.

Treat the canonical architecture JSON as the source of truth; diagrams are generated views, not the primary model.

## Experience contract

- Accept a one-sentence stack description, longer narrative, requirements/specification, existing diagram, repository code or infrastructure files.
- Do not require users to hand-author JSON. Build or update the canonical model as an implementation detail.
- If the request is clear, proceed without a questionnaire. Ask only when a missing fact could materially change architecture semantics or create a misleading diagram.
- Infer reasonable groupings and primary/secondary flows from context. Mark inferred details as assumptions in the model rather than presenting them as confirmed facts.
- Default deliverables: editable Draw.io plus PNG preview. Also provide self-contained HTML when the available renderer supports it.
- Save outputs under a predictable directory such as `architecture/<system-name>/`, including the model, diagram, preview and asset attribution.

Example:
```text
/architecture-diagram Create the architecture for an AI-enabled vehicle telemetry platform. Vehicle gateways send signals over MQTT to Azure ingestion, stream through Event Hubs, process with Databricks, and expose fleet insights through an AI assistant using retrieval-augmented generation.
```

## Diagram content semantics

Build three inventories before layout:

- **Nodes:** systems, services, applications, devices, data stores, AI models/agents, gateways and operational tools. Give each a clear name and short responsibility.
- **Groups:** runtime, deployment, ownership, cloud/provider, vehicle/offboard, network, repository or trust boundaries. Nest at most one level unless the system genuinely requires more.
- **Edges:** primary runtime/data flow, secondary integration, and development/deployment/control-plane relationships. Label edges with protocol, data or action where known.

Use a coherent visual hierarchy:
- Make the primary user or data journey visually prominent.
- Use neutral styling for secondary integrations.
- Use dashed lines for CI/CD, provisioning, scheduled jobs or other non-runtime relationships.
- Keep labels concise and avoid lines crossing text or node tiles.
- Show vehicle vs cloud, OEM vs supplier, safety-related vs non-safety-related, trusted vs external, and production vs engineering boundaries when relevant and supported by evidence.

For SDV and AI-defined Vehicle diagrams, distinguish onboard/edge, connectivity, OEM cloud, enterprise, supplier and external AI services. Identify safety-relevant paths, data residency boundaries, OTA and fleet-management flows where supported. Never infer safety certification or functional-safety classification from product names alone.


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

## Icon sourcing and visual rules

Use official vendor architecture icons for cloud services wherever the vendor publishes them. For general technologies, use official brand marks or a reputable source with clear provenance. Use neutral pictograms for abstract concepts (queue, user, device, scheduler, trust boundary) rather than inventing a logo.

Rules:
- Never recolor, redraw, crop, rotate or distort a brand logo.
- Preserve aspect ratio. Use a dark tile or neutral backing when a light logo would disappear; do not alter the logo itself.
- Do not represent a specific vendor product with a generic or incorrect icon. Where no exact product icon exists, use the vendor's prescribed category icon or a neutral pictogram and retain the accurate product label.
- Use full vendor product names when abbreviations could create ambiguity.
- For AWS, Azure and Google Cloud, follow providers' diagram conventions for resource groups, regions, VPCs/VNets, subnets and availability zones.
- Source only icons used. Record source URL, retrieval date, license/terms and attribution in `icon-library/manifest.json` or diagram-local `ASSETS.md`. Keep vendor packs and downloaded logos out of redistributed artefacts when vendor terms do not permit bundling them.
- Never hotlink icons in the final diagram. Embed permitted assets; otherwise explain external asset requirements.
- Do not invent logos or imply a technology is present when it is not.


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

## Visual renderer and outputs

The canonical model is renderer-independent. Prefer editable Draw.io for engineering handover and self-contained HTML/SVG for polished sharing when a compatible renderer is available. PNG is a derived preview, not the source of truth.

For HTML/SVG rendering, use a reusable template with design tokens for typography, colors, node tiles, group panels, arrowheads, edge labels, light/dark themes and spacing. Keep node, group and edge data separate from the template. Inline permitted icons, fonts and CSS where practical so HTML can open offline.

If the toolkit has no suitable HTML renderer yet, do not fake one or claim it exists: use the current Draw.io generator, deliver its editable file, and note that HTML rendering is a planned renderer.

## Mermaid output

Create valid Mermaid flowchart source with stable IDs, clear labels, and subgraphs for meaningful boundaries. Mermaid layout is renderer-controlled; do not promise pixel-perfect placement or edge anchoring. Use Mermaid when maintainability and text diffs matter more than exact geometry.

## Validation and visual inspection — mandatory

- Validate model structure, references and semantic assumptions.
- Validate emitted Draw.io XML or HTML/SVG syntax.
- Render using the target renderer. For browser-based HTML/SVG, use headless Chromium when available; for Draw.io, use a compatible diagrams.net renderer.
- Inspect the actual rendered image, not just source code.
- Check clipping, readability, alignment, edge anchoring, connector crossings, labels, arrow direction, group containment, icon visibility and canvas margins.
- Check both light and dark themes when both are produced.
- Fix defects, re-render and inspect again.
- If no compatible renderer is available, state exactly what was validated and what visual properties could not be checked. Never claim visual QA from XML parsing alone.

## Deliverables

Default:
- Canonical architecture model JSON.
- Editable Draw.io file.
- PNG preview after successful visual inspection.
- Asset attribution/provenance file.
- Brief README with assumptions and editing instructions.

Optional on request or where supported:
- Self-contained HTML/SVG diagram, including light/dark variants.
- React/TSX component.
- Mermaid source.
- C4 context/container/component views or separate deployment/data-flow/security views.

Build once from the canonical model and derive alternate formats from that model. Do not create unrelated copies with divergent content.
