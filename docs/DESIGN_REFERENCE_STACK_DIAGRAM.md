# Design reference: stack-diagram

Reference reviewed: https://github.com/caru-ini/stack-diagram

This document records product and engineering ideas worth adapting. It is not a specification to clone. Reuse ideas and patterns, not code, assets or vendor artwork without checking their licenses and terms.

## What the reference demonstrates well

- A low-friction prompt: describe the stack in a sentence and receive a diagram.
- A focused, agent-invokable skill with clear descriptions and scripts.
- A strong visual language: brand-logo tiles, labeled groups, hierarchy and orthogonal connectors.
- Vendor-aware icon selection and diagram conventions for AWS, Google Cloud and Azure.
- Self-contained HTML as a shareable source artifact, with PNG and React outputs derived from it.
- A mandatory render-and-inspect loop before delivery.
- Straightforward installation through a skill ecosystem command.

## Architecture Design Toolkit response

Our toolkit should preserve its stronger engineering model while adopting the reference's user experience.

| Area | Direction |
|---|---|
| User input | Accept one-sentence prompts, prose, requirements, existing diagrams, source repositories and infrastructure definitions |
| Architecture representation | Canonical, technology-neutral JSON remains the source of truth |
| Diagrams | Editable Draw.io is the primary engineering handover format |
| Presentation | Add self-contained HTML/SVG with light/dark variants as a second renderer |
| Previews | Render PNG from the same source and inspect it before calling the diagram complete |
| Icons | Official vendor product icons, official technology marks and neutral pictograms with full provenance |
| Semantics | Distinguish runtime, data, control-plane, CI/CD and deployment relationships |
| Engineering context | Support SDV, onboard/offboard, AI/agent, safety boundaries, data residency, OTA and fleet systems where evidence supports them |
| Agent interface | Keep `architecture-diagram` as the portable skill entry point, and let the skill orchestrate model, tools, renderers and QA |

## Proposed visual conventions

- White or neutral tiles for technology marks; never recolor vendor logos.
- Consistent role labels beneath nodes.
- Group boxes for ownership, runtime, cloud, network, trust and deployment boundaries.
- Accent flow for the primary path; neutral solid edges for secondary runtime integrations.
- Dashed edges for CI/CD, provisioning, scheduled jobs and deployment/control-plane relationships.
- Orthogonal connectors routed around full node boxes, including their labels.
- Vendor-specific grouping semantics for cloud accounts/projects, regions, VPC/VNets, subnets and zones.
- Light and dark themes using design tokens rather than scattered styles.
- A restrained layout density: split complex systems into multiple architecture views rather than shrinking all detail into one canvas.

## Proposed renderer sequence

1. Keep the current JSON model and Draw.io generator stable.
2. Add a reusable HTML/SVG renderer that consumes the same JSON model.
3. Create one template with data-driven nodes, groups and edges.
4. Embed only permitted icons/fonts as data URIs and record attribution.
5. Render both themes in headless Chromium, then run visual inspection.
6. Derive PNG from the HTML/SVG; optionally derive React/TSX as a portable presentation component.
7. Compare the two renderers against the same fixture models to prevent semantic drift.

## Engineering-specific extensions beyond the reference

Stack views alone are insufficient for engineering architecture. The model and skill should support additional views and metadata:

- Logical/system context, container, component, deployment, data-flow, integration, security/trust-boundary and operational views.
- Vehicle/edge, connectivity, OEM cloud, enterprise, supplier and external AI/model boundaries.
- Interface contracts, protocol, latency/availability assumptions, data classification and ownership.
- OTA update chains, vehicle telemetry, fleet commands, observability, diagnostics and data lifecycle.
- AI model lifecycle, inference placement, RAG/data paths, agent tools, policy enforcement, evaluation, human oversight and audit trails.
- Safety/security classifications only when established by source evidence; never infer compliance or certification from technology choice.

## Guardrails

- Do not copy the reference project's source code or bundled assets without an explicit license review.
- Do not assume vendor icon packs can be redistributed simply because their use in diagrams is allowed.
- Do not silently substitute approximate vendor icons for an exact product mark.
- Do not claim that a layout is collision-free or visually verified unless the rendered output was inspected.
- Preserve the user's technology decisions; flag unknowns and assumptions.
- Keep the JSON model renderer-independent so a change in presentation technology does not force an architecture-model redesign.

## Immediate next milestones

1. Establish a polished, consistent Draw.io visual style using the above conventions.
2. Build the browser-based HTML/SVG renderer and PNG render pipeline.
3. Add fixture diagrams for cloud, SaaS, AI platform, SDV vehicle-to-cloud and engineering toolchain topologies.
4. Add automated geometry checks and rendered-preview artifacts to CI.
5. Expand the visual icon catalog rules and its source/license audit.
