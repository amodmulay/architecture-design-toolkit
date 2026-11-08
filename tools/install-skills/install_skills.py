#!/usr/bin/env python3
"""Install toolkit Agent Skills into supported coding-agent skill directories.

Examples:
  python3 tools/install-skills/install_skills.py --host all --scope project
  python3 tools/install-skills/install_skills.py --host claude --scope user
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

HOST_DIRS = {
    "claude": ".claude/skills",
    "copilot": ".github/skills",
    "codex": ".agents/skills",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["all", *HOST_DIRS], default="all")
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2],
                        help="Toolkit repository root (defaults to this checkout)")
    parser.add_argument("--home", type=Path, default=Path.home(),
                        help="Home directory used for user-scope installs")
    parser.add_argument("--force", action="store_true",
                        help="Replace existing installed skill folders")
    args = parser.parse_args()

    source_root = args.repo_root.resolve() / "skills"
    if not source_root.is_dir():
        parser.error(f"Cannot find canonical skills directory: {source_root}")

    hosts = HOST_DIRS if args.host == "all" else {args.host: HOST_DIRS[args.host]}
    target_root = Path.cwd().resolve() if args.scope == "project" else args.home.resolve()
    installed = []

    for host, relative in hosts.items():
        destination_root = target_root / relative if args.scope == "project" else target_root / (
            ".claude/skills" if host == "claude" else
            ".copilot/skills" if host == "copilot" else ".agents/skills"
        )
        for skill_source in sorted(p for p in source_root.iterdir() if p.is_dir()):
            skill_file = skill_source / "SKILL.md"
            if not skill_file.is_file():
                continue
            destination = destination_root / skill_source.name
            if destination.exists():
                if not args.force:
                    print(f"SKIP  {destination} (already exists; use --force to replace)")
                    continue
                shutil.rmtree(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(skill_source, destination)
            installed.append(destination)
            print(f"INSTALLED [{host}] {destination}")

    print(f"\nInstalled {len(installed)} skill folder(s).")
    if args.scope == "project":
        print("Open/reload the project in your coding assistant so it discovers the skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
