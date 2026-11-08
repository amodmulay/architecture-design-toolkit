# Install the Architecture Design Toolkit skills

The toolkit uses the open Agent Skills format: each skill is a folder containing a `SKILL.md` with YAML `name` and `description` metadata. The same instructions can be discovered by multiple coding assistants.

## One-command installation

Clone the toolkit:

```bash
git clone https://github.com/amodmulay/architecture-design-toolkit.git
```

Run the installer from the **root of the project where you want the skills installed**.

If you are installing into the toolkit checkout itself:

```bash
cd architecture-design-toolkit
python3 tools/install-skills/install_skills.py --host all --scope project
```

If you want to install into a different project, run the toolkit installer from that project's root and point it to the toolkit checkout:

```bash
cd /path/to/your-project
python3 /path/to/architecture-design-toolkit/tools/install-skills/install_skills.py \
  --repo-root /path/to/architecture-design-toolkit --host all --scope project
```

The installer copies all four skills into the host-specific project directories:

| Host | Project skill directory |
|---|---|
| Claude Code | `.claude/skills/` |
| GitHub Copilot | `.github/skills/` |
| OpenAI Codex | `.agents/skills/` |

To install for one host only, replace `all` with `claude`, `copilot`, or `codex`.

For user-level installation across projects, run:

```bash
python3 /path/to/architecture-design-toolkit/tools/install-skills/install_skills.py \
  --repo-root /path/to/architecture-design-toolkit --host all --scope user
```

User-level destinations are `~/.claude/skills/`, `~/.copilot/skills/`, and `~/.agents/skills/` respectively.

Use `--force` to replace an existing installed copy. By default, existing skill folders are left untouched. The installer uses only the Python standard library.

## Install a single skill with GitHub CLI

GitHub CLI's `gh skill` command can install a skill directly from this repository (GitHub CLI 2.90.0+; preview feature):

```bash
gh skill preview amodmulay/architecture-design-toolkit architecture-diagram
gh skill install amodmulay/architecture-design-toolkit architecture-diagram --agent claude-code
```

Use `gh skill install --help` to see the current host names and options for your installed GitHub CLI version. Preview skills before installing them.

## Invoke a skill

The skill name is the command name. Invocation syntax is host-dependent:

| Host | Example invocation |
|---|---|
| Claude Code | `/architecture-diagram`, `/architecture-review`, `/technology-selection`, `/architecture-documentation` |
| GitHub Copilot | The same `/architecture-diagram` style slash commands in supported Copilot agent sessions; skills can also load automatically when relevant. |
| OpenAI Codex | Use `$architecture-diagram` (or select it from `/skills` in supported clients); other skills follow the same name. |

Examples:

- `/architecture-diagram Create a logical and deployment architecture for an AI-enabled vehicle data platform. Use Azure services and output an editable Draw.io diagram.`
- `/architecture-review Review this architecture for safety, cybersecurity, scalability, and operational gaps.`
- `/technology-selection Compare Kafka, Azure Event Hubs, and AWS Kinesis for vehicle telemetry ingestion.`
- `/architecture-documentation Create an HLD and ADRs for this solution.`

For Codex, use the corresponding `$skill-name` mention. Copilot's slash-command availability depends on the client and harness version; if a command is not listed, describe the task and Copilot can still select the skill by its description.

## Use inside the toolkit repository

The repository also includes host-discoverable copies under `.claude/skills/`, `.github/skills/`, and `.agents/skills/`. This lets supported agents discover the skills when the toolkit repository itself is opened as the workspace. The canonical editable sources remain under `skills/`.

## Important distinction

The Agent Skills format makes the **instructions portable**; it does not make every host's command interface identical. A skill named `architecture-diagram` can be explicitly invoked as `/architecture-diagram` in Claude Code and supported Copilot clients, while Codex commonly uses `$architecture-diagram` or its skill selector.
