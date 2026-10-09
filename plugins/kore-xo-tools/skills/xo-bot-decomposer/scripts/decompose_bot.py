#!/usr/bin/env python3
"""Inventory selected XO exports and companion sources without executing them.

Python 3.10+; no third-party runtime dependencies. XO 10 includes earlier releases;
XO 11 routing is not a claim of support for every subsequent export schema.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

# Also supports direct import by source-tree test runners.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from xo_coverage import build, digest, gap, write
from xo_graph import unwrap
from xo_export_parser import build_inventory, write_inventory_files, write_metadata_file, _redact_structure, _redact_text, _safe_filename

SKILL_ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 256 * 1024 * 1024
MAX_FILES = 20000


def safe_extract(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        if len(members) > MAX_FILES or sum(m.file_size for m in members) > MAX_BYTES:
            raise ValueError("Archive exceeds static intake limits (20,000 members / 256 MiB)")
        seen = set()
        for member in members:
            target = (destination / member.filename).resolve()
            if destination != target and destination not in target.parents:
                raise ValueError("Unsafe archive member path")
            if "\\" in member.filename or stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("Archive symlinks and backslash paths are unsupported")
            if target in seen:
                raise ValueError("Duplicate archive member path")
            seen.add(target)
        zf.extractall(destination)


def choose_definition(root: Path) -> Path:
    if root.is_file() and root.suffix.lower() == ".json":
        return root
    candidates = []
    for path in sorted(root.rglob("*.json")):
        if path.is_symlink():
            continue
        try:
            data, _ = unwrap(json.loads(path.read_text()))
        except (ValueError, OSError, UnicodeError):
            continue
        if data is not None:
            candidates.append(path)
    if len(candidates) != 1:
        raise ValueError(f"Expected one definition; found {len(candidates)}. Select definitions explicitly.")
    return candidates[0]


def major_version(value: object) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        return int(match.group()) if match else None
    return None


def detect_version(definition: Path, requested: str | None) -> int:
    if requested:
        version = major_version(requested)
        if version is None:
            raise ValueError("Invalid XO version")
        return 11 if version >= 11 else 10
    try:
        raw = json.loads(definition.read_text(encoding="utf-8"))
        data, _ = unwrap(raw)
        for layer in (raw, data):
            if isinstance(layer, dict):
                for key in ("xoVersion", "platformVersion"):
                    version = major_version(layer.get(key))
                    if version is not None:
                        return 11 if version >= 11 else 10
    except (OSError, UnicodeError, ValueError):
        raw = {}
    if definition.name.lower() == "appdefinition.json":
        return 11
    if definition.name.lower() == "botdefinition.json":
        return 10
    version = major_version(raw.get("version")) if isinstance(raw, dict) else None
    return 11 if version is not None and version >= 11 else 10


def discover(source, group, kind):
    paths = sorted(source.rglob("*")) if source.is_dir() else [source]
    if len(paths) > MAX_FILES:
        raise ValueError("Source directory exceeds intake member limit")
    artifacts = []
    total = 0
    for p in paths:
        if p.is_dir() and not p.is_symlink():
            continue
        relative = p.relative_to(source).as_posix() if source.is_dir() else p.name
        record = {"id": f"{group}/{relative}", "source_group": group, "source_kind": kind, "logical_source": relative, "supplied": True,
                  "role": "unsupported", "parse_status": "not_parsed", "analysis_status": "pending", "reason": "Unsupported source format"}
        if p.is_symlink():
            record.update(role="unsupported", reason="Symlink not followed", size=None, source_hash=None)
            artifacts.append(record)
            continue
        size = p.stat().st_size
        total += size
        if total > MAX_BYTES:
            raise ValueError("Source directory exceeds 256 MiB intake limit")
        raw = p.read_bytes()
        record.update(size=size, source_hash=digest(raw), _path=p)
        ext = p.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2"):
            record.update(role="asset", parse_status="excluded", analysis_status="excluded", reason="Non-executable display asset; not copied")
        elif ext in (".js", ".mjs", ".cjs", ".json", ".md", ".txt", ".yaml", ".yml", ".env") or p.name == ".env":
            try:
                text = raw.decode("utf-8")
                record["_text"] = text
                if ext == ".json":
                    obj = json.loads(text)
                    record["_json"] = obj
                    data, prefix = unwrap(obj)
                    role = "definition" if data is not None or p.name.lower() in ("appdefinition.json", "botdefinition.json") else "contract" if kind == "contracts" else "configuration"
                    record.update(role=role, parse_status="parsed", reason="Static JSON evidence")
                    if data is not None and (any(not isinstance(d, dict) or not isinstance(d.get("nodes", []), list) for d in data["dialogs"]) or not isinstance(data.get("dialogComponents", []), list) or any(not isinstance(c, dict) for c in data.get("dialogComponents", []))):
                        data = None
                        record.update(parse_status="unsupported", reason="Unsupported dialog/component collection shape")
                    if data is not None:
                        record.update(_definition=data, _prefix=prefix)
                    record["sanitized_hash"] = digest(json.dumps(_redact_structure(obj), sort_keys=True))
                elif ext in (".js", ".mjs", ".cjs"):
                    record.update(role="javascript", parse_status="lexical", reason="Lexical candidates; semantic review required", sanitized_hash=digest(_redact_text(text)))
                else:
                    record.update(reason="Text companion retained in manifest; requires targeted format review", sanitized_hash=digest(_redact_text(text)))
            except (UnicodeError, ValueError):
                record.update(parse_status="unsupported", reason="Malformed JSON or unsupported text encoding")
        artifacts.append(record)
    return artifacts


def render_export(data, name, route, output, inventory=None):
    output.mkdir(parents=True, exist_ok=True)
    inventory = _redact_structure(inventory if inventory is not None else build_inventory(data, name, route))
    write_inventory_files(inventory, str(output))
    write_metadata_file(_redact_structure(data), str(output))
    index = ["# Extracted dialog index", "", "All dialogs retained; classification is separate from implementation coverage.", "", "| Dialog | ID | Evidence |", "|---|---|---|"]
    combined = []
    for i, dialog in enumerate(inventory["dialogs"], 1):
        filename = f"dialog_{i:04}_{_safe_filename(dialog['name'])}.md"
        lines = [f"# {dialog['name']}", "", f"Source ID: `{dialog['id']}`", f"Hidden: {dialog['is_hidden']}; system-name hint: {dialog['ignored_system_intent']}", "",
                 "```json", json.dumps(dialog, indent=2, ensure_ascii=False), "```", "", "See _inventory.json node_occurrences for full sanitized node/component bodies and original/expanded pointers."]
        text = "\n".join(lines) + "\n"
        (output / filename).write_text(text)
        combined.append(text)
        index.append(f"| {dialog['name']} | {dialog['id']} | [{filename}]({filename}) |")
    (output / "_index.md").write_text("\n".join(index) + "\n")
    (output / "_all_dialogs.md").write_text("\n".join(combined))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--xo-version")
    parser.add_argument("--additional-export", action="append", type=Path, default=[])
    parser.add_argument("--botkit", action="append", type=Path, default=[])
    parser.add_argument("--companion-source", action="append", type=Path, default=[])
    parser.add_argument("--contracts", action="append", type=Path, default=[])
    parser.add_argument("--definition", action="append", default=[], help="Exact manifest artifact ID to select; repeatable")
    parser.add_argument("--all-definitions", action="store_true", help="Explicitly analyze all definitions within supplied export inputs")
    parser.add_argument("--defer", action="append", default=[])
    parser.add_argument("--scope", choices=("full", "goals-only"), default="full")
    parser.add_argument("--universal", action="store_true")
    parser.add_argument("--parent-id")
    args = parser.parse_args()
    inputs = [(args.export, "export")] + [(p, "export") for p in args.additional_export] + [(p, "botkit") for p in args.botkit] + [(p, "companion") for p in args.companion_source] + [(p, "contracts") for p in args.contracts]
    inputs = [(p.expanduser().absolute(), kind) for p, kind in inputs]
    output = args.output.expanduser().resolve() if args.output else Path(tempfile.mkdtemp(prefix="xo-evidence-"))
    for path, _ in inputs:
        if not path.exists() or path.is_symlink():
            parser.error("Input is absent or a symlink")
        resolved = path.resolve()
        if output == resolved or output in resolved.parents or (resolved.is_dir() and resolved in output.parents):
            parser.error("Source and output must not overlap")
    if output.exists() and any(output.iterdir()):
        parser.error("Use a fresh output directory; existing evidence is not overwritten")
    output.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="xo-intake-") as temp:
            artifacts, exports, intake_gaps = [], [], []
            for i, (source, kind) in enumerate(inputs, 1):
                group = f"source_{i:03}"
                if source.suffix.lower() == ".zip":
                    extracted = Path(temp) / group
                    safe_extract(source, extracted)
                    source = extracted
                found = discover(source, group, kind)
                artifacts.extend(found)
                candidates = [a for a in found if a["role"] == "definition"]
                if kind != "export":
                    for candidate in candidates:
                        candidate.update(parse_status="unselected", reason="Definition discovered in companion source; capability scope not selected")
                        intake_gaps.append(("awaiting_scope_decision", candidate["id"], "Companion contains a bot definition; select explicitly as an export to analyze its capability slice."))
                    continue
                chosen = [a for a in candidates if a["id"] in args.definition] if args.definition else candidates if len(candidates) == 1 or args.all_definitions else []
                for a in candidates:
                    if a not in chosen:
                        a.update(parse_status="unselected", reason="Multiple or unselected definitions require explicit selection")
                        intake_gaps.append(("awaiting_scope_decision", a["id"], "Definition not selected; no whole-archive completeness claim is valid."))
                    elif "_definition" not in a:
                        a.update(parse_status="unsupported", reason="No supported dialogs array")
                        intake_gaps.append(("unsupported_parse", a["id"], "Definition shape is unsupported."))
                    else:
                        version = detect_version(a["_path"], args.xo_version)
                        route = "XO 10 or earlier" if version == 10 else "XO 11"
                        try:
                            inventory = build_inventory(a["_definition"], a["id"], route)
                        except (AttributeError, TypeError, KeyError, ValueError, RecursionError):
                            a.update(parse_status="unsupported", reason="Unsupported field shape in definition")
                            intake_gaps.append(("unsupported_parse", a["id"], "Definition has unsupported field shapes; supported peers remain analyzed."))
                            continue
                        exports.append({"data": a["_definition"], "prefix": a["_prefix"], "artifact_id": a["id"], "version_route": route, "inventory": inventory})
                if not candidates:
                    intake_gaps.append(("unsupported_parse", group, "No supported definition discovered in selected export input."))
            unknown_selections = set(args.definition) - {a["id"] for a in artifacts}
            if unknown_selections:
                raise ValueError("Selected definition ID not found in manifest")
            universal = args.universal or bool(args.parent_id) or any(e["data"].get("isUniversal") or e["data"].get("childBots") for e in exports)
            ledger = build(artifacts, exports, args.scope, universal, args.parent_id, args.defer)
            for category, source, reason in intake_gaps:
                gap(ledger, category, [source], [], reason, "Select manifest definition IDs, pass --all-definitions, or provide a supported source.")
            if intake_gaps:
                ledger["status"]["implementation_dependencies"] = "partial"
            for i, export in enumerate(exports, 1):
                destination = output if len(exports) == 1 else output / f"bot_{i:03}"
                render_export(export["data"], export["artifact_id"], export["version_route"], destination, export["inventory"])
            write(_redact_structure(ledger), output)
            print(f"Static intake complete: {len(artifacts)} artifacts, {len(exports)} selected definitions, {len(ledger['coverage_gaps'])} gaps. Semantic review and runtime validation are separate.")
            return 0
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"Intake rejected: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
