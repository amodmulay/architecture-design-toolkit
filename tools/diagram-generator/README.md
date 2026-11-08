# Diagram Generator

Generate an editable diagrams.net (Draw.io) XML diagram from the toolkit's canonical architecture JSON. The implementation currently uses Python's standard library only.

## Usage

From the repository root:

    python3 tools/diagram-generator/diagramgen.py examples/connected-vehicle-data-platform.json --out architecture/connected-vehicle-data-platform.drawio

Validate the model without generating output:

    python3 tools/diagram-generator/diagramgen.py examples/connected-vehicle-data-platform.json --validate-only

Run tests:

    python3 -m unittest discover -s tools/diagram-generator -p 'test_*.py' -v

## Model

See [the JSON Schema](../../schemas/architecture.schema.json) and [the example](../../examples/connected-vehicle-data-platform.json).

Components have stable IDs, titles, responsibilities, optional technology/provider/icon metadata, and optional boundary membership. Connections reference component IDs and include labels and optional protocol/mode metadata. Boundaries group components into horizontal lanes.

## Icon lookup

icon_id may be a repository-relative path under icon-library/, or a unique SVG filename/stem within the icon catalogue. Icons are embedded in the Draw.io XML as base64 SVG; diagrams do not hotlink to the repository. If an icon cannot be resolved unambiguously, the component is generated without it.

## Current layout behavior and limitations

- Deterministic horizontal placement within each boundary lane.
- Components use explicit geometry and stable cell IDs.
- Connections attach to source/target cells and use orthogonal routing waypoints.
- Asynchronous, batch, and stream connections are dashed.
- The initial version does not yet perform graph-based collision avoidance, edge-crossing minimization, or automatic label-lane optimization. Review the rendered diagram for dense or complex topologies.
- The generator validates model structure and references; it does not yet validate against every JSON Schema constraint.

The output is editable in diagrams.net. Open the generated .drawio file in https://app.diagrams.net.
