# Architecture Design Toolkit

A modular, agent-friendly toolkit for designing, documenting, reviewing, and validating software, cloud, data, integration, and AI architectures.

Works as a shared foundation for Claude Code, Codex, and other coding agents. The repository separates agent instructions (skills), reusable utilities, architecture schemas, diagram templates, and attributed vendor icon assets.

## Repository structure

- `skills/` — reusable architecture workflows
- `icon-library/` — local SVG catalogue and asset provenance
- `tools/icon-catalogue/` — Python CLI for download, normalization, deduplication, and audits
- `tools/diagram-generator/` — canonical architecture JSON validation and editable Draw.io generation
- `tools/` — reusable scripts for validation and asset management
- `schemas/` — technology-neutral architecture data contracts
- `templates/` — editable draw.io and Mermaid starters
- `examples/` — sample architecture models and outputs

## Skills

| Skill | Purpose |
|---|---|
| [Architecture diagram](skills/architecture-diagram/SKILL.md) | Generate editable draw.io or Mermaid diagrams |
| [Architecture review](skills/architecture-review/SKILL.md) | Review quality, risks, gaps, and trade-offs |
| [Technology selection](skills/technology-selection/SKILL.md) | Compare technologies against requirements |
| [Architecture documentation](skills/architecture-documentation/SKILL.md) | Produce HLDs, C4 views, interface docs, and ADRs |

## Getting started

Read the relevant skill's `SKILL.md`. Model the architecture using [the JSON Schema](schemas/architecture.schema.json), then generate a Draw.io diagram:

```bash
python3 tools/diagram-generator/diagramgen.py examples/connected-vehicle-data-platform.json --out architecture/connected-vehicle-data-platform.drawio
```

Run the generator's tests:

```bash
python3 -m unittest discover -s tools/diagram-generator -p 'test_*.py' -v
```

## Icon catalogue

Run `python3 tools/icon-catalogue/iconctl.py --help` for icon management. A starter list of common technology brand marks is in `icon-library/collections/architecture-starter.json`. Official AWS and Azure icon packs and selected Simple Icons are stored locally. Review vendor terms before redistributing assets.

## Design principles

1. Model the architecture before drawing it.
2. Preserve user-selected technologies; make assumptions explicit.
3. Prefer official vendor icons and record provenance and license.
4. Use coordinate-based layouts and boundary-anchored orthogonal edges for draw.io.
5. Render and visually inspect diagrams before calling them complete.
6. Keep the architecture model vendor-neutral and renderers replaceable.
7. Keep skills focused and tools reusable across agents.

## Icon policy

The icon catalogue is curated. Add only assets used by diagrams. Check redistribution terms and retain source/attribution metadata. Third-party icons and trademarks retain their own licenses and terms; see the icon manifest and source terms.

## Contributing

Keep skills agent-agnostic where possible. Utilities should have documented inputs, outputs, and dependencies. Examples should be small and runnable. Third-party assets require source and license metadata.

## License

Original toolkit text and scripts are MIT licensed. Third-party icons and trademarks retain their own licenses and terms; see the icon manifest and source terms.
