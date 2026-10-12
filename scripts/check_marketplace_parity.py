#!/usr/bin/env python3
"""Check this repository's shared Codex/Claude packaging contract (not host schemas)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


SHARED_FIELDS = (
    "name", "version", "description", "author", "homepage", "repository",
    "keywords", "skills", "mcpServers",
)


def check_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    def read(path: Path) -> dict:
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict):
                raise ValueError("expected a JSON object")
            return data
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return {}

    catalogs = {
        "Codex": read(root / ".agents/plugins/marketplace.json"),
        "Claude": read(root / ".claude-plugin/marketplace.json"),
    }
    entries: dict[str, dict[str, dict]] = {}
    for host, catalog in catalogs.items():
        if catalog.get("name") != "kore-skills":
            errors.append(f"{host}: marketplace name must be kore-skills")
        entries[host] = {}
        plugins = catalog.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append(f"{host}: expected a nonempty plugins array")
            continue
        for entry in plugins:
            name = entry.get("name") if isinstance(entry, dict) else None
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                errors.append(f"{host}: invalid plugin entry name")
                continue
            if name in entries[host]:
                errors.append(f"{host}: duplicate plugin {name}")
            entries[host][name] = entry
            expected = f"./plugins/{name}"
            source = entry.get("source")
            wanted = {"source": "local", "path": expected} if host == "Codex" else expected
            if source != wanted:
                errors.append(f"{host}/{name}: source must reference shared root {expected}")
            if host == "Codex" and (
                entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
                or entry.get("category") != "Productivity"
            ):
                errors.append(f"Codex/{name}: preserve installation/authentication policy and category")

    if set(entries["Codex"]) != set(entries["Claude"]):
        errors.append("Codex and Claude plugin inventories differ")
    directories = {p.name for p in (root / "plugins").iterdir() if p.is_dir()}
    if directories != set(entries["Codex"]):
        errors.append("Plugin directories and catalog inventory differ")

    for name in sorted(set(entries["Codex"]) | set(entries["Claude"])):
        plugin = root / "plugins" / name
        if not plugin.resolve().is_relative_to((root / "plugins").resolve()) or not plugin.is_dir():
            errors.append(f"{name}: missing or external plugin directory")
            continue
        codex = read(plugin / ".codex-plugin/plugin.json")
        claude = read(plugin / ".claude-plugin/plugin.json")
        for key in SHARED_FIELDS:
            if codex.get(key) != claude.get(key):
                errors.append(f"{name}: {key} differs between manifests")
        for host, manifest in (("Codex", codex), ("Claude", claude)):
            if manifest.get("name") != name:
                errors.append(f"{host}/{name}: manifest name differs from catalog")
            if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
                errors.append(f"{host}/{name}: expected a release version")
            for field in ("skills", "mcpServers"):
                value = manifest.get(field)
                if value is None:
                    continue
                if not isinstance(value, str) or not value.startswith("./"):
                    errors.append(f"{host}/{name}: {field} must be a plugin-relative path")
                    continue
                path = (plugin / value).resolve()
                if not path.is_relative_to(plugin.resolve()) or not path.exists():
                    errors.append(f"{host}/{name}: missing or external {field} path")
                elif field == "skills" and (not path.is_dir() or not list(path.glob("*/SKILL.md"))):
                    errors.append(f"{host}/{name}: skills path contains no skills")
                elif field == "mcpServers" and path.is_file():
                    if not read(path).get("mcpServers"):
                        errors.append(f"{host}/{name}: empty MCP configuration")
                elif field == "mcpServers":
                    errors.append(f"{host}/{name}: MCP configuration must be a file")
        if not isinstance(codex.get("interface"), dict) or not codex["interface"].get("displayName"):
            errors.append(f"Codex/{name}: missing interface displayName")
        if "interface" in claude:
            errors.append(f"Claude/{name}: Codex interface metadata belongs in the Codex manifest")
        if entries["Claude"].get(name, {}).get("description") != codex.get("description"):
            errors.append(f"Claude/{name}: catalog description differs from manifest")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_repository(args.root)
    if errors:
        print("Marketplace parity failed:\n" + "\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("Marketplace parity passed: shared plugin roots, metadata, versions and resources agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
