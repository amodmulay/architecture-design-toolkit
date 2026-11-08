# Architecture Design Toolkit

A modular, agent-friendly toolkit for designing, documenting, reviewing, and validating software, cloud, data, integration, embedded, and AI architectures.

The toolkit uses the open Agent Skills format. Its architecture workflows can be installed into Claude Code, GitHub Copilot, OpenAI Codex, and other compatible coding assistants. Skills provide the instructions; reusable scripts, schemas, and icon assets provide the engineering utilities.

## Repository structure

- `skills/` — canonical, reusable Agent Skills
- `.claude/skills/`, `.github/skills/`, `.agents/skills/` — host-discoverable skill copies
- `tools/install-skills/` — cross-platform Python skill installer
- `icon-library/` — local SVG catalogue and asset provenance
- `tools/icon-catalogue/` — Python CLI for download, normalization, deduplication, and audits
- `tools/diagram-generator/` — canonical architecture JSON validation and editable Draw.io generation
- `docs/DESIGN_REFERENCE_STACK_DIAGRAM.md` — design direction inspired by the stack-diagram reference
- `schemas/` — technology-neutral architecture data contracts
- `templates/` — editable Draw.io and Mermaid starters
- `examples/` — sample architecture models and outputs

## Skills

| Skill | Purpose | Claude Code command |
|---|---|---|
| [architecture-diagram](skills/architecture-diagram/SKILL.md) | Generate editable Draw.io or Mermaid diagrams | `/architecture-diagram` |
| [architecture-review](skills/architecture-review/SKILL.md) | Review quality, risks, gaps, and trade-offs | `/architecture-review` |
| [technology-selection](skills/technology-selection/SKILL.md) | Compare technologies against requirements | `/technology-selection` |
| [architecture-documentation](skills/architecture-documentation/SKILL.md) | Produce HLDs, C4 views, interface docs, and ADRs | `/architecture-documentation` |

## Install the skills

Clone the repository and run from its root:

```bash
python3 tools/install-skills/install_skills.py --host all --scope project
```

This installs skills into the current project for Claude Code, Copilot, and Codex. Use `--host claude`, `--host copilot`, or `--host codex` to target one host. Use `--scope user` for user-level installation across projects.

See [Installing and invoking skills](docs/INSTALLING_SKILLS.md) for detailed instructions and host-specific invocation syntax.

## Use the diagram generator

Model the architecture using [the JSON Schema](schemas/architecture.schema.json), then generate a Draw.io diagram:

```bash
python3 tools/diagram-generator/diagramgen.py examples/connected-vehicle-data-platform.json --out architecture/connected-vehicle-data-platform.drawio
```

Run the generator's tests:

```bash
python3 -m unittest discover -s tools/diagram-generator -p 'test_*.py' -v
```

See the [User Manual](docs/USER_GUIDE.md) for setup, model authoring, icon selection, diagram generation, Draw.io editing, validation, and troubleshooting. See the [visual design reference](docs/DESIGN_REFERENCE_STACK_DIAGRAM.md) for the planned renderer and diagram experience.

## Icon catalogue

Run `python3 tools/icon-catalogue/iconctl.py --help` for icon management. A starter list of common technology brand marks is in `icon-library/collections/architecture-starter.json`. Review vendor terms before redistributing assets.

## Design principles

1. Model the architecture before drawing it.
2. Preserve user-selected technologies; make assumptions explicit.
3. Prefer official vendor architecture icons and record provenance and license.
4. Use coordinate-based layouts and boundary-anchored orthogonal edges for Draw.io.
5. Render and visually inspect diagrams before calling them complete.
6. Keep the architecture model vendor-neutral and renderers replaceable.
7. Keep skills focused and utilities reusable across agents.

## Contributing

Edit the canonical skills under `skills/`. Keep the host-specific copies in sync. Utilities should have documented inputs, outputs, and dependencies. Examples should be small and runnable. Third-party assets require source and license metadata.

## License

Original toolkit text and scripts are MIT licensed. Third-party icons and trademarks retain their own licenses and terms; see the icon manifest and source terms.
