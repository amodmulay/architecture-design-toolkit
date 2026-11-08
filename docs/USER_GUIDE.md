# Architecture Design Toolkit — User Manual

This guide explains how to create, validate, generate, and refine architecture diagrams with the Architecture Design Toolkit.

- Repository: https://github.com/amodmulay/architecture-design-toolkit
- Diagram editor: https://app.diagrams.net/
- Main output: editable Draw.io (.drawio) XML
- Runtime: Python 3.10+; the current generator uses only the Python standard library.

## 1. What the toolkit does

The toolkit separates architecture design from diagram drawing:

1. Describe the system in a structured JSON architecture model.
2. Validate components, boundaries, and connections.
3. Generate an editable Draw.io diagram.
4. Open the result in diagrams.net to review and refine it.
5. Keep the JSON model as the source of truth and regenerate when the architecture changes.

The model is technology-neutral. It can describe cloud, enterprise, data, AI, embedded, and connected-vehicle systems. Vendor icons are optional.

## 2. Repository contents

| Location | What it is for |
|---|---|
| `schemas/architecture.schema.json` | Formal structure of an architecture model |
| `tools/diagram-generator/diagramgen.py` | Validates models and generates Draw.io XML |
| `tools/diagram-generator/README.md` | Generator-specific technical notes |
| `tools/icon-catalogue/` | Imports, normalizes, lists, and audits SVG assets |
| `icon-library/` | Local vendor and technology SVG catalogue |
| `examples/` | Ready-to-use example architecture models |
| `skills/` | Instructions for AI coding assistants and architecture workflows |

## 3. Set up

### Option A — Download the repository

1. Open the repository on GitHub.
2. Select **Code → Download ZIP**.
3. Extract the ZIP to a local folder.
4. Install Python 3.10 or newer if it is not already installed.

Alternatively, clone it:

```bash
git clone https://github.com/amodmulay/architecture-design-toolkit.git
cd architecture-design-toolkit
```

Check Python:

```bash
python3 --version
```

On Windows, use `py --version` and replace `python3` with `py` in the commands below if required.

No pip packages are required for the current diagram generator.

## 4. Generate your first diagram

From the repository root, run:

```bash
python3 tools/diagram-generator/diagramgen.py \
  examples/connected-vehicle-data-platform.json \
  --out architecture/connected-vehicle-data-platform.drawio
```

The command creates the `architecture/` folder if necessary and writes the editable Draw.io file.

Open the output:

1. Go to https://app.diagrams.net/.
2. Choose **Device** if asked where to save diagrams.
3. Select **Open Existing Diagram** or use **File → Open From → Device**.
4. Select `architecture/connected-vehicle-data-platform.drawio`.

The example describes a vehicle telemetry path from a vehicle gateway to cloud ingestion, event streaming, processing, and data lake storage. It is illustrative, not a production reference architecture.

## 5. Create your own architecture model

Start by copying the example:

```bash
cp examples/connected-vehicle-data-platform.json architecture/my-system.json
```

Edit `architecture/my-system.json` in a text editor or IDE. Keep valid JSON syntax: double quotes around property names and strings, commas between properties, and no trailing comma after the final item.

### 5.1 Top-level properties

| Property | Required | Description |
|---|---:|---|
| `name` | Yes | Diagram/system title |
| `description` | No | Short system description |
| `scope` | No | What the architecture includes |
| `assumptions` | No | Explicit assumptions |
| `boundaries` | No | Trust zones, systems, cloud accounts, or domains |
| `components` | Yes | Architecture building blocks |
| `connections` | Yes | Directed interactions between components |
| `metadata` | No | Additional scalar metadata |
| `views` | No | Named component subsets for future view generation |

### 5.2 Boundaries

Boundaries group components into visual lanes. Typical examples include Vehicle, Mobile App, Cloud Platform, OEM Backend, Supplier Domain, or On-Premises.

```json
{
  "id": "cloud",
  "title": "OEM Cloud Platform",
  "type": "cloud",
  "provider": "Microsoft Azure",
  "description": "OEM-managed cloud environment"
}
```

Every component's `boundary` value must match a boundary ID in the model. Components without a boundary are placed in a generated system lane.

### 5.3 Components

Each component needs a stable unique ID, title, and responsibility.

```json
{
  "id": "vehicle_gateway",
  "title": "Vehicle Gateway",
  "responsibility": "Collect and forward vehicle telemetry",
  "category": "device",
  "provider": "OEM",
  "technology": "AUTOSAR Adaptive",
  "boundary": "vehicle",
  "layer": "edge"
}
```

Useful optional properties:

- `category`: device, service, database, gateway, messaging, AI model, and so on.
- `provider`: vendor or organization.
- `technology`: selected product, framework, or standard.
- `icon_id`: local SVG path or unique SVG filename/stem.
- `boundary`: ID of the containing boundary.
- `layer`: logical layer such as edge, API, application, data, AI, or operations.
- `width` and `height`: optional node dimensions in pixels.

IDs must begin with a letter and may contain letters, numbers, underscores, and hyphens. Keep IDs stable when renaming a component; connections refer to IDs, not titles.

### 5.4 Connections

A connection is directional. Its source and target must be existing component IDs.

```json
{
  "id": "vehicle_to_ingestion",
  "source": "vehicle_gateway",
  "target": "ingestion_api",
  "label": "Telemetry",
  "protocol": "HTTPS / MQTT",
  "mode": "stream",
  "data_classification": "Vehicle operational data"
}
```

Supported modes:

| Mode | Meaning | Diagram treatment |
|---|---|---|
| `sync` | Synchronous request/response | Solid line |
| `async` | Asynchronous interaction | Dashed line |
| `batch` | Scheduled or bulk transfer | Dashed line |
| `stream` | Continuous event/data stream | Dashed line |
| `unknown` | Not yet decided | Solid line |

Use a clear label that explains what is exchanged. Add the protocol when known. Do not invent protocols or imply a direction that the system does not have.

## 6. Use vendor and technology icons

The icon catalogue contains official AWS and Azure architecture icon packs plus selected Simple Icons. Check the icon-library manifest and each vendor's terms before redistributing assets.

To find an icon:

```bash
python3 tools/icon-catalogue/iconctl.py list --help
python3 tools/icon-catalogue/iconctl.py list
```

Use the exact repository-relative path under `icon-library/` in `icon_id`, for example:

```json
"icon_id": "azure/10042-icon-service-api-management-services.svg"
```

You can also use a unique SVG filename or stem. If a filename is ambiguous, the generator deliberately omits the icon rather than choosing one arbitrarily.

Icons are embedded into the generated Draw.io file. The diagram therefore does not need to fetch icons from the internet when opened.

If an icon is missing:
1. Search the local catalogue.
2. Check the official vendor pack and its terms.
3. Import the asset using the icon catalogue CLI.
4. Audit the catalogue.
5. Regenerate the diagram.

## 7. Validate and generate

### Validate only

This checks model structure and references without creating a diagram:

```bash
python3 tools/diagram-generator/diagramgen.py \
  architecture/my-system.json --validate-only
```

A successful result reports the number of components and connections.

### Generate Draw.io

```bash
python3 tools/diagram-generator/diagramgen.py \
  architecture/my-system.json \
  --out architecture/my-system.drawio
```

### Generate with layout diagnostics

```bash
python3 tools/diagram-generator/diagramgen.py \
  architecture/my-system.json \
  --out architecture/my-system.drawio \
  --layout-report
```

The report includes component and connection counts and any layout warnings, such as cyclic connection graphs or connections between components assigned to the same rank.

## 8. How automatic layout works

The current generator improves on simple list-based placement:

- Assigns left-to-right ranks from the directed connection graph.
- Places downstream components to the right of upstream components for acyclic flows.
- Stacks parallel components vertically within a rank.
- Uses deterministic neighbor ordering to reduce avoidable connector crossings.
- Groups components into boundary lanes.
- Selects connector sides based on relative component positions.
- Adds orthogonal routing waypoints.
- Offsets parallel connections to reduce direct overlap.
- Draws connections behind component nodes.
- Uses dashed edges for asynchronous, batch, and streaming interactions.

Layout is deterministic for the same input model. Cycles are supported with an approximate rank fallback and are reported in the layout diagnostics.

**Important limitation:** this is a lightweight heuristic layout engine, not a full graph-optimization solver. Complex topologies can still contain connector crossings, crowded labels, or routes that need manual refinement. Always inspect the generated diagram in Draw.io. Do not assume that a successful XML generation means the diagram is visually perfect.

## 9. Review and edit in Draw.io

After opening the diagram:

1. Use **View → Zoom → Fit** to inspect the complete canvas.
2. Check that components are in the correct boundary.
3. Check arrow direction and labels.
4. Check that connectors attach to node edges and do not cover text or icons.
5. Move nodes or adjust connector waypoints where needed.
6. Resize nodes if text is clipped.
7. Save the edited file.

Keep the JSON model as the authoritative architecture definition. If you make important structural changes directly in Draw.io, update the JSON model as well. Otherwise, the next generation will overwrite those manual changes.

## 10. Run the automated tests

From the repository root:

```bash
python3 -m unittest discover \
  -s tools/diagram-generator \
  -p 'test_*.py' -v
```

The tests cover model validation, unknown connection references, duplicate IDs, invalid boundaries, XML generation, graph ranking, parallel component placement, and cyclic graph diagnostics.

GitHub Actions runs the same validation, generation, and test sequence when relevant files change.

## 11. Common problems

| Problem | Likely cause | What to do |
|---|---|---|
| Missing required property | Model omits name, components, or connections | Add the required property |
| Duplicate component ID | Two components share an ID | Give each component a unique stable ID |
| Unknown component reference | A connection source or target does not exist | Correct the connection endpoint |
| Unknown boundary | Component refers to an undefined boundary | Add the boundary or correct its ID |
| Icon does not appear | Wrong path, missing file, or ambiguous filename | Use an exact local path or unique SVG filename |
| Diagram is crowded | Many components share a rank or have dense connections | Split into logical views/boundaries or refine positions in Draw.io |
| Cycle warning | A feedback loop or cyclic dependency exists | Confirm the loop is intentional; review routing manually |
| JSON parse error | Missing comma, quote, or brace | Validate JSON in your editor |
| Diagram edits disappear on regeneration | Changes were made only in Draw.io | Apply structural changes to the JSON source model too |

## 12. Recommended modelling workflow

For engineering and mobility architectures, use this sequence:

1. Define system scope and external actors.
2. Identify trust, ownership, and deployment boundaries.
3. List major components before selecting detailed technologies.
4. Add the interfaces and data flows between components.
5. Add protocols, synchronous/asynchronous behavior, and data classification.
6. Validate the model.
7. Generate the diagram.
8. Review it with engineering, security, operations, and product stakeholders.
9. Update the model based on review decisions.
10. Regenerate and retain the reviewed JSON and Draw.io artefacts together.

For Software-Defined Vehicle and AI-defined Vehicle architectures, useful boundaries may include vehicle/edge, connectivity, OEM cloud, enterprise IT, supplier services, and external AI/model services. Separate safety-critical onboard functions from non-safety-critical and offboard services, and make trust boundaries explicit.

## 13. Current scope and roadmap

Available now:
- Canonical JSON architecture model and schema.
- Model and reference validation.
- Graph-aware deterministic layout heuristics.
- Editable Draw.io XML generation.
- Local SVG icon embedding.
- Unit tests and GitHub Actions checks.

Not yet included:
- Mermaid generation from the same model.
- Full JSON Schema validation in the CLI.
- Automated Draw.io rendering and visual regression checks.
- Advanced collision and edge-crossing optimization.
- Multiple filtered views generated from the `views` property.
- Round-trip synchronization from manual Draw.io edits back to JSON.

Treat generated diagrams as engineering artefacts that require review, not as automatically approved architecture decisions.
