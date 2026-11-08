# Install the Architecture Design Toolkit skills

The toolkit uses the open Agent Skills format: each skill is a folder containing a `SKILL.md` with YAML `name` and `description` metadata. The instructions are host-neutral; supported tools discover them from their own skill directories.

## One-command installation

Clone the repository, then run from the toolkit root:

```bash
python3 tools/install-skills/install_skills.py --host all --scope project
```

Run this command from the root of the project where you want the skills installed. If the toolkit checkout is elsewhere, call the installer by its full path and pass `--repo-root`:

| Host | Project skill directory |
|---|---|
| Claude Code | `.claude/skills/` |
| GitHub Copilot | `.github/skills/` |
| OpenAI Codex | `.agents/skills/` |

To install for one host only, replace `all` with `claude`, `copilot`, or `codex`.

To install into your user-level skill directory for use across projects:

```bash
python3 tools/install-skills/install_skills.py --host all --scope user
```

User-level destinations are `~/.claude/skills/`, `~/.copilot/skills/`, and `~/.agents/skills/` respectively.

Use `--force` to replace an existing installed copy. By default, existing skill folders are left untouched. The installer uses only the Python standard library.

## Install a single skill with GitHub CLI

GitHub CLI's skill command can install a skill directly from this repository (GitHub CLI 2.90.0+; preview feature):

```bash
gh skill preview amodmulay/architecture-design-toolkit architecture-diagram
gh skill install amodmulay/architecture-design-toolkit architecture-diagram --agent claude-code
```

Use `gh skill install --help` to see the current host names and options for your installed GitHub CLI version. Preview skills before installing them.

## Invoke a skill

Skill discovery and invocation syntax are controlled by the host, not by the toolkit:

| Host | How to invoke |
|---|---|
| Claude Code | `/architecture-diagram`, `/architecture-review`, `/technology-selection`, `/architecture-documentation` |
| GitHub Copilot | The same `/architecture-diagram` style slash commands in supported Copilot agent sessions; skills can also load automatically when relevant. |
| OpenAI Codex | Use `$architecture-diagram` (or select it from `/skills` in supported clients); other skills follow the same name. |

Examples:

- `/architecture-diagram Create a logical and deployment architecture for an AI-enabled vehicle data platform. Use Azure services and output an editable Draw.io diagram.`
- `/architecture-review Review this architecture for safety, cybersecurity, scalability, and operational gaps.`
- `/technology-selection Compare Kafka, Azure Event Hubs, and AWS Kinesis for vehicle telemetry ingestion.`
- `/architecture-documentation Create an HLD and ADRs for this solution.`

For Codex, use the corresponding `$skill-name` mention. Copilot's slash-command availability depends on the Copilot client/harness version; if the command is not listed, describe the task and Copilot can still select the skill by its description.

## Use inside the toolkit repository

The repository also includes host-discoverable copies under `.claude/skills/`, `.github/skills/`, and `.agents/skills/`. This lets supported agents discover the skills when the toolkit repository itself is opened as the workspace. The canonical editable sources remain under `skills/`.

## Important distinction

The Agent Skills format makes the **instructions portable**; it does not make every host's command interface identical. A skill named `architecture-diagram` can be explicitly invoked as `/architecture-diagram` in Claude Code, while Codex and Copilot may expose it through their own selector, mention, or automatic skill matching. Avoid assuming that a literal `/skill-name` command works in every coding assistant.
