#!/usr/bin/env python3
"""Advisory structural preflight for Artemis Designer packages and legacy files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


LEGACY_MARKER = "<!-- kore-agent-design-template:v1 -->"
LEGACY_FUNCTIONAL_HEADINGS = [
    "Document Control",
    "Agent Purpose and Business Outcome",
    "Agent Type and Operating Model",
    "Users, Stakeholders, and Roles",
    "Scope",
    "Channels, Languages, and Experience Constraints",
    "Assumptions and Dependencies",
    "User Goals and Use-Case Inventory",
    "Functional SOPs",
    "Long-Running Workflows, Human Tasks, and Approvals",
    "Knowledge and Content Requirements",
    "Functional Integration Requirements",
    "Human Handoff and Escalation",
    "Guardrails, Privacy, and Compliance",
    "Non-Functional Requirements",
    "Success Measures and Acceptance Criteria",
    "Risks, Decisions, and Open Questions",
]
LEGACY_TECHNICAL_HEADINGS = [
    "Document Control",
    "Functional Design Traceability",
    "Solution Context and Architecture",
    "Kore.ai Product and Component Mapping",
    "Environments and Deployment Model",
    "Conversation and Workflow Orchestration",
    "Channel and Locale Design",
    "Knowledge and Retrieval Design",
    "Prompt, Model, Tool, and Guardrail Design",
    "Integration Architecture",
    "Authentication and Authorization",
    "Data, Context, and Session State",
    "Workflow Persistence and Resumption",
    "Human Tasks and Approval Architecture",
    "Error Handling, Retries, and Recovery",
    "Human Handoff Design",
    "Security, Privacy, and Compliance",
    "Observability and Operational Support",
    "Testing Strategy",
    "Release and Rollback Plan",
    "Technical Risks, Decisions, and Open Questions",
]

MARKER_RE = re.compile(r"<!--\s*kore-agent-design:([a-z-]+):v2\s*-->")
PREFIXES = ("DOC", "FND", "UC", "FR", "BR", "EXP", "NFR", "INT", "API", "AC", "TD", "OQ", "CHG")
PREFIX_ALT = "|".join(PREFIXES)
ID_RE = re.compile(rf"\b({PREFIX_ALT})-(\d{{3}})\b")
ID_ANY_DIGITS_RE = re.compile(rf"\b({PREFIX_ALT})-(\d+)\b")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
VERSION_RE = re.compile(r"^\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WAVE_RE = re.compile(r"^(?:All|Proposed|Not applicable|Wave [1-9]\d*)$")
ALLOWED_STATUSES = {"Working Draft", "In Review", "Approved", "Superseded"}
REQUIRED_METADATA = [
    "document id",
    "document type",
    "version",
    "status",
    "owner",
    "wave",
    "canonical owner for",
    "source evidence",
    "last updated",
]
CATEGORY_TYPES = {
    "index": "Design Index",
    "agent-definition": "Agent Definition",
    "use-case": "Use Case",
    "voice-experience": "Voice Experience",
    "digital-experience": "Digital Experience",
    "architecture": "Architecture",
    "connectivity-integrations": "Connectivity and Integrations",
    "use-case-apis": "Use-Case APIs",
    "data-security": "Data and Security",
    "operations-testing-release": "Operations, Testing, and Release",
    "review": "Design Review",
}
HEADING_DEFINITION_PREFIXES = {
    "use-case": {"UC"},
    "architecture": {"TD"},
    "connectivity-integrations": {"INT", "TD"},
    "use-case-apis": {"API", "TD"},
    "data-security": {"TD"},
    "operations-testing-release": {"TD"},
}
TABLE_DEFINITION_SECTIONS = {
    "index": {
        "FND": "Foundation Register",
        "CHG": "Decisions and Changes",
        "OQ": "Risks, Dependencies, and Open Questions",
    },
    "agent-definition": {
        "BR": "Universal Guardrails and Business Rules",
        "NFR": "Shared Non-Functional Requirements",
        "OQ": "Shared Assumptions and Open Questions",
    },
    "use-case": {
        "FR": "Functional Requirements",
        "BR": "Business Rules",
        "AC": "Acceptance Criteria",
        "OQ": "Risks, Dependencies, and Open Questions",
    },
    "voice-experience": {
        "EXP": "Turn-Taking and Conversation Control",
        "AC": "Voice Acceptance Criteria",
        "OQ": "Open Questions",
    },
    "digital-experience": {
        "EXP": "Channel Variations",
        "AC": "Experience Acceptance Criteria",
        "OQ": "Open Questions",
    },
    "architecture": {
        "TD": "Architecture Decisions",
        "OQ": "Risks and Open Questions",
    },
    "connectivity-integrations": {
        "TD": "Integration Decisions and Open Questions",
        "OQ": "Integration Decisions and Open Questions",
    },
    "use-case-apis": {"OQ": "Open Questions"},
    "data-security": {
        "TD": "Security Decisions and Open Questions",
        "OQ": "Security Decisions and Open Questions",
    },
    "operations-testing-release": {
        "NFR": "Service Objectives and Operational Ownership",
        "TD": "Operational Decisions and Open Questions",
        "OQ": "Operational Decisions and Open Questions",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run advisory structural checks on a modular design package or legacy v1 files."
    )
    parser.add_argument("--package", type=Path, help="Modular design package directory")
    parser.add_argument("--functional", type=Path, help="Legacy functional design Markdown")
    parser.add_argument("--technical", type=Path, help="Legacy technical design Markdown")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if not args.package and not args.functional and not args.technical:
        parser.error("provide --package, --functional, or --technical")
    if args.package and (args.functional or args.technical):
        parser.error("--package cannot be combined with legacy file options")
    return args


def markdown_h2_sections(text: str) -> tuple[list[str], dict[str, list[str]]]:
    headings: list[str] = []
    sections: dict[str, list[str]] = {}
    current: str | None = None
    fence: str | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            if current is not None:
                sections[current].append(raw_line)
            continue
        if fence is None:
            match = re.match(r"^##\s+(.+?)\s*$", raw_line)
            if match:
                current = match.group(1).strip()
                headings.append(current)
                sections.setdefault(current, [])
                continue
        if current is not None:
            sections[current].append(raw_line)
    return headings, sections


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_tables(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[dict[str, str]]]] = []
    index = 0
    while index + 1 < len(lines):
        if lines[index].lstrip().startswith("|") and lines[index + 1].lstrip().startswith("|"):
            headers = split_table_row(lines[index])
            separator = split_table_row(lines[index + 1])
            if len(headers) == len(separator) and is_separator_row(separator):
                rows: list[dict[str, str]] = []
                cursor = index + 2
                while cursor < len(lines) and lines[cursor].lstrip().startswith("|"):
                    cells = split_table_row(lines[cursor])
                    if len(cells) == len(headers):
                        rows.append({headers[i].strip(): cells[i] for i in range(len(headers))})
                    cursor += 1
                tables.append((headers, rows))
                index = cursor
                continue
        index += 1
    return tables


def section_text(text: str, heading: str) -> str:
    _, sections = markdown_h2_sections(text)
    return "\n".join(sections.get(heading, []))


def first_table_in_section(text: str, heading: str) -> tuple[list[str], list[dict[str, str]]] | None:
    tables = parse_tables(section_text(text, heading))
    return tables[0] if tables else None


def normalize_metadata(rows: list[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in rows:
        values = list(row.values())
        if len(values) >= 2:
            result[values[0].strip().lower()] = values[1].strip()
    return result


def markdown_link_target(value: str) -> str | None:
    match = LINK_RE.search(value)
    if not match:
        return None
    target = match.group(1).strip().strip("<>")
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return target.split("#", 1)[0]


def local_link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        if " " in target:
            target = target.split(" ", 1)[0]
        target = target.split("#", 1)[0]
        if target:
            targets.append(target)
    return targets


def id_tokens(text: str) -> set[str]:
    return {f"{prefix}-{digits}" for prefix, digits in ID_RE.findall(text)}


def malformed_id_tokens(text: str) -> set[str]:
    return {
        f"{prefix}-{digits}"
        for prefix, digits in ID_ANY_DIGITS_RE.findall(text)
        if len(digits) != 3
    }


def definition_token_occurrences(text: str, category: str, metadata: dict[str, str]) -> list[str]:
    definitions: list[str] = []
    document_id = metadata.get("document id", "")
    if re.fullmatch(r"DOC-\d{3}", document_id):
        definitions.append(document_id)

    heading_allowed = HEADING_DEFINITION_PREFIXES.get(category, set())
    for match in re.finditer(rf"^#{{1,4}}\s+(({PREFIX_ALT})-\d{{3}})\b", text, re.MULTILINE):
        if match.group(2) in heading_allowed:
            definitions.append(match.group(1))

    for prefix, section in TABLE_DEFINITION_SECTIONS.get(category, {}).items():
        tables = parse_tables(section_text(text, section))
        if category in {"voice-experience", "digital-experience"} and prefix == "EXP":
            preferred = first_table_in_section(text, "Experience Decisions")
            if preferred and preferred[1]:
                # New packages define EXP IDs in the decision table. Older v2
                # packages keep their canonical definitions in the variation table.
                tables = [preferred]
        for _, rows in tables:
            for row in rows:
                for value in row.values():
                    if re.fullmatch(rf"{prefix}-\d{{3}}", value.strip()):
                        definitions.append(value.strip())
    return definitions


def inspect_modular_document(path: Path, package: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    marker = MARKER_RE.search(text)
    category = marker.group(1) if marker else "unrecognized"
    warnings: list[str] = []
    if marker is None:
        warnings.append("Missing modular v2 category marker")
    elif category not in CATEGORY_TYPES:
        warnings.append(f"Unknown document category: {category}")

    metadata_table = first_table_in_section(text, "Document Metadata")
    metadata = normalize_metadata(metadata_table[1]) if metadata_table else {}
    if not metadata_table:
        warnings.append("Missing Document Metadata table")
    missing_metadata = [field for field in REQUIRED_METADATA if not metadata.get(field)]
    if missing_metadata:
        warnings.append("Missing metadata fields: " + ", ".join(missing_metadata))

    document_id = metadata.get("document id", "")
    if document_id and not re.fullmatch(r"DOC-\d{3}", document_id):
        warnings.append(f"Invalid Document ID: {document_id}")
    version = metadata.get("version", "")
    if version and not VERSION_RE.fullmatch(version):
        warnings.append(f"Invalid version: {version}")
    status = metadata.get("status", "")
    if status and status not in ALLOWED_STATUSES:
        warnings.append(f"Invalid status: {status}")
    wave = metadata.get("wave", "")
    if wave and not WAVE_RE.fullmatch(wave):
        warnings.append(f"Invalid wave: {wave}")
    last_updated = metadata.get("last updated", "")
    if last_updated and not DATE_RE.fullmatch(last_updated):
        warnings.append(f"Invalid last-updated date: {last_updated}")
    expected_type = CATEGORY_TYPES.get(category)
    actual_type = metadata.get("document type", "")
    if expected_type and actual_type and actual_type.casefold() != expected_type.casefold():
        warnings.append(f"Document type '{actual_type}' does not match marker category '{expected_type}'")

    broken_links: list[str] = []
    escaping_links: list[str] = []
    package_root = package.resolve()
    for target in local_link_targets(text):
        resolved = (path.parent / target).resolve()
        if not resolved.is_relative_to(package_root):
            escaping_links.append(target)
        elif not resolved.exists():
            broken_links.append(target)
    if broken_links:
        warnings.append("Broken local links: " + ", ".join(sorted(set(broken_links))))
    if escaping_links:
        warnings.append("Local links escape the design package: " + ", ".join(sorted(set(escaping_links))))

    definition_occurrences = definition_token_occurrences(text, category, metadata)
    duplicate_local_definitions = sorted(
        {
            item
            for item in definition_occurrences
            if definition_occurrences.count(item) > 1
        }
    )
    if duplicate_local_definitions:
        warnings.append(
            "Identifiers defined more than once in this document: "
            + ", ".join(duplicate_local_definitions)
        )
    definitions = set(definition_occurrences)
    identifiers = id_tokens(text)
    malformed = malformed_id_tokens(text)
    if malformed:
        warnings.append("Identifiers do not use three digits: " + ", ".join(sorted(malformed)))

    return {
        "path": path.relative_to(package).as_posix(),
        "category": category,
        "metadata": metadata,
        "status": "WARN" if warnings else "PASS",
        "warnings": warnings,
        "identifiers": sorted(identifiers),
        "definitions": sorted(definitions),
        "links": sorted(set(local_link_targets(text))),
        "text": text,
    }


def rows_by_normalized_header(table: tuple[list[str], list[dict[str, str]]] | None) -> list[dict[str, str]]:
    if not table:
        return []
    normalized: list[dict[str, str]] = []
    for row in table[1]:
        normalized.append({key.strip().lower(): value.strip() for key, value in row.items()})
    return normalized


def row_value_starting(row: dict[str, str], prefix: str) -> str:
    for key, value in row.items():
        if key.startswith(prefix):
            return value
    return ""


def first_identifier(value: str, prefix: str) -> str | None:
    for found_prefix, digits in ID_RE.findall(value):
        if found_prefix == prefix:
            return f"{found_prefix}-{digits}"
    return None


def validate_manifest(package: Path, documents: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    index_doc = next((doc for doc in documents if doc["path"] == "00-design-index.md"), None)
    if not index_doc:
        return ["Missing required 00-design-index.md"]

    register_rows = rows_by_normalized_header(
        first_table_in_section(index_doc["text"], "Document Register")
    )
    if not register_rows:
        return ["Index has no Document Register rows"]

    registered_paths: dict[str, dict[str, str]] = {}
    registered_ids: dict[str, str] = {}
    for row in register_rows:
        document_id = row.get("document id", "")
        target = markdown_link_target(row.get("document", ""))
        if not document_id:
            warnings.append("Document Register row has no Document ID")
        elif document_id in registered_ids:
            warnings.append(f"Duplicate Document Register ID: {document_id}")
        if target:
            normalized = Path(target).as_posix()
            if normalized in registered_paths:
                warnings.append(f"Duplicate Document Register path: {normalized}")
            registered_paths[normalized] = row
            registered_ids[document_id] = normalized
        else:
            warnings.append(f"Document Register entry {document_id or '<unknown>'} has no Markdown link")

    for doc in documents:
        if doc["path"] == "00-design-index.md":
            continue
        row = registered_paths.get(doc["path"])
        if not row:
            warnings.append(f"Document absent from index: {doc['path']}")
            continue
        metadata = doc["metadata"]
        comparisons = {
            "document id": "document id",
            "type": "document type",
            "version": "version",
            "status": "status",
            "wave": "wave",
        }
        for register_key, metadata_key in comparisons.items():
            registered = row.get(register_key, "")
            actual = metadata.get(metadata_key, "")
            if registered and actual and registered.casefold() != actual.casefold():
                warnings.append(
                    f"Manifest mismatch for {doc['path']}: {register_key} is '{registered}' in index and '{actual}' in document"
                )

    actual_paths = {doc["path"] for doc in documents}
    for registered_path in registered_paths:
        if registered_path not in actual_paths:
            warnings.append(f"Index references missing document: {registered_path}")

    wave_rows = rows_by_normalized_header(first_table_in_section(index_doc["text"], "Wave Plan"))
    wave_by_uc: dict[str, str] = {}
    wave_row_by_uc: dict[str, dict[str, str]] = {}
    for row in wave_rows:
        use_case_id = first_identifier(row.get("use case", ""), "UC")
        if use_case_id:
            if use_case_id in wave_by_uc:
                warnings.append(f"Duplicate Wave Plan entry: {use_case_id}")
            wave_by_uc[use_case_id] = row.get("wave", "")
            wave_row_by_uc[use_case_id] = row

    wave_one_use_cases = {
        use_case_id for use_case_id, wave in wave_by_uc.items() if wave.casefold() == "wave 1"
    }
    if not wave_one_use_cases:
        warnings.append("Wave Plan has no Wave 1 use case")

    foundation_rows = rows_by_normalized_header(
        first_table_in_section(index_doc["text"], "Foundation Register")
    )
    foundation_ids = {
        item
        for row in foundation_rows
        if (item := first_identifier(row.get("id", ""), "FND"))
    }
    wave_one_foundations = {
        item
        for row in foundation_rows
        if row.get("wave", "").casefold() == "wave 1"
        if (item := first_identifier(row.get("id", ""), "FND"))
    }
    if not wave_one_foundations:
        warnings.append("Foundation Register has no Wave 1 foundation item")

    priority_rows = rows_by_normalized_header(
        first_table_in_section(index_doc["text"], "Use-Case Prioritization")
    )
    priority_by_uc: dict[str, dict[str, str]] = {}
    for row in priority_rows:
        use_case_id = first_identifier(row.get("use case", ""), "UC")
        if not use_case_id:
            continue
        if use_case_id in priority_by_uc:
            warnings.append(f"Duplicate prioritization entry: {use_case_id}")
        priority_by_uc[use_case_id] = row

    for use_case_id in sorted(wave_one_use_cases):
        priority = priority_by_uc.get(use_case_id)
        if not priority:
            warnings.append(f"Wave 1 use case has no prioritization row: {use_case_id}")
        else:
            scores: dict[str, int] = {}
            for dimension in ("value", "speed", "readiness"):
                raw = row_value_starting(priority, dimension)
                try:
                    score = int(raw)
                except ValueError:
                    if raw.strip().casefold() in {"tbd", "not verifiable", "not available"}:
                        warnings.append(f"{use_case_id} has unresolved {dimension} score: {raw}")
                    else:
                        warnings.append(f"{use_case_id} has invalid {dimension} score: {raw or '<missing>'}")
                    continue
                if not 1 <= score <= 5:
                    warnings.append(f"{use_case_id} has {dimension} score outside 1–5: {score}")
                    continue
                scores[dimension] = score
            raw_total = priority.get("score", "")
            if len(scores) == 3:
                expected_total = scores["value"] * scores["speed"] * scores["readiness"]
                try:
                    claimed_total = int(raw_total)
                except ValueError:
                    warnings.append(f"{use_case_id} has invalid prioritization score: {raw_total or '<missing>'}")
                else:
                    if claimed_total != expected_total:
                        warnings.append(
                            f"{use_case_id} prioritization score is {claimed_total}; expected {expected_total}"
                        )
            if not priority.get("selection rationale", ""):
                warnings.append(f"{use_case_id} has no selection rationale")
            if not priority.get("evidence status", ""):
                warnings.append(f"{use_case_id} has no prioritization evidence status")

        wave_row = wave_row_by_uc[use_case_id]
        dependency_ids = {
            f"{prefix}-{digits}"
            for prefix, digits in ID_RE.findall(wave_row.get("foundation dependency", ""))
            if prefix == "FND"
        }
        if not dependency_ids:
            warnings.append(f"{use_case_id} has no Foundation Register dependency")
        elif not dependency_ids <= foundation_ids:
            missing = sorted(dependency_ids - foundation_ids)
            warnings.append(f"{use_case_id} references unknown foundation items: {', '.join(missing)}")
        elif not dependency_ids <= wave_one_foundations:
            later_wave = sorted(dependency_ids - wave_one_foundations)
            warnings.append(
                f"{use_case_id} depends on foundation items outside Wave 1: {', '.join(later_wave)}"
            )
        if not wave_row.get("customer agreement", ""):
            warnings.append(f"{use_case_id} has no customer-agreement evidence")

    baseline = section_text(index_doc["text"], "Scope Baseline")
    target = re.search(r"^\*\*Target:\*\*\s*(.+)$", baseline, re.MULTILINE)
    if not target or not target.group(1).strip():
        warnings.append("Scope Baseline has no delivery target")

    for doc in documents:
        if doc["category"] != "use-case":
            continue
        use_cases = [item for item in doc["definitions"] if item.startswith("UC-")]
        if len(use_cases) != 1:
            warnings.append(f"Use-case document must define exactly one UC ID: {doc['path']}")
            continue
        use_case_id = use_cases[0]
        if use_case_id not in wave_by_uc:
            warnings.append(f"Use case absent from Wave Plan: {use_case_id}")
        else:
            document_wave = doc["metadata"].get("wave", "")
            if document_wave and wave_by_uc[use_case_id].casefold() != document_wave.casefold():
                warnings.append(
                    f"Wave mismatch for {use_case_id}: '{wave_by_uc[use_case_id]}' in index and '{document_wave}' in document"
                )
    return warnings


def validate_traceability(documents: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    warnings: list[str] = []
    definitions: dict[str, set[str]] = defaultdict(set)
    occurrences: dict[str, set[str]] = defaultdict(set)
    for doc in documents:
        for item in doc["definitions"]:
            definitions[item].add(doc["path"])
        for item in doc["identifiers"]:
            occurrences[item].add(doc["path"])

    duplicate = sorted(item for item, paths in definitions.items() if len(paths) > 1)
    undefined = sorted(set(occurrences) - set(definitions))
    orphaned: list[str] = []
    for item, paths in definitions.items():
        if item == "DOC-000":
            continue
        if not (occurrences[item] - paths):
            orphaned.append(item)

    if duplicate:
        warnings.append("Identifiers defined in multiple documents: " + ", ".join(duplicate))
    if undefined:
        warnings.append("Referenced identifiers without canonical definitions: " + ", ".join(undefined))
    if orphaned:
        warnings.append("Canonical identifiers with no cross-document reference: " + ", ".join(sorted(orphaned)))

    index_doc = next((doc for doc in documents if doc["category"] == "index"), None)
    if index_doc:
        summary = first_table_in_section(index_doc["text"], "Experience Decision Summary")
        if summary:
            summary_ids = {
                identifier
                for row in rows_by_normalized_header(summary)
                if (identifier := first_identifier(row.get("experience id", ""), "EXP"))
            }
            experience_ids = {item for item in definitions if item.startswith("EXP-")}
            missing = sorted(experience_ids - summary_ids)
            stale = sorted(summary_ids - experience_ids)
            if missing:
                warnings.append("Experience decisions absent from index summary: " + ", ".join(missing))
            if stale:
                warnings.append("Index experience summary references undefined decisions: " + ", ".join(stale))

    for doc in documents:
        if doc["category"] not in {"connectivity-integrations", "use-case-apis"}:
            continue
        prefix = "INT" if doc["category"] == "connectivity-integrations" else "API"
        pattern = re.compile(
            rf"^###\s+({prefix}-\d{{3}})\b(.*?)(?=^#{{1,3}}\s+|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        for match in pattern.finditer(doc["text"]):
            block = match.group(2)
            if not re.search(r"\b(UC|FR|NFR|AC)-\d{3}\b", block):
                warnings.append(f"{match.group(1)} has no functional or non-functional trace")
            if prefix == "API" and not re.search(r"\bINT-\d{3}\b", block):
                warnings.append(f"{match.group(1)} has no integration reference")

    for doc in documents:
        if doc["category"] != "architecture":
            continue
        component_rows = rows_by_normalized_header(
            first_table_in_section(doc["text"], "Kore.ai Product and Component Mapping")
        )
        if not component_rows:
            warnings.append(f"{doc['path']} has no product/component mapping rows")
            continue
        for row in component_rows:
            functional_ids = row.get("functional ids", "")
            component = row.get("proposed component or pattern", "<unknown component>")
            if not re.search(r"\b(UC|FR|NFR)-\d{3}\b", functional_ids):
                warnings.append(
                    f"Architecture component '{component}' has no functional or non-functional trace"
                )

    inventory = {
        "definitionCount": len(definitions),
        "referenceCount": len(occurrences),
        "duplicateDefinitions": duplicate,
        "undefinedReferences": undefined,
        "orphanedDefinitions": sorted(orphaned),
    }
    return warnings, inventory


def inspect_package(package: Path) -> dict[str, Any]:
    if not package.is_dir():
        raise OSError(f"package directory not found: {package}")
    paths = sorted(path for path in package.rglob("*.md") if not any(part.startswith(".") for part in path.parts))
    documents = [inspect_modular_document(path, package) for path in paths]
    warnings: list[str] = []
    if not paths:
        warnings.append("Package contains no Markdown documents")
    if not any(doc["path"] == "01-agent-definition.md" for doc in documents):
        warnings.append("Missing required 01-agent-definition.md")
    warnings.extend(validate_manifest(package, documents))
    trace_warnings, trace_inventory = validate_traceability(documents)
    warnings.extend(trace_warnings)
    for doc in documents:
        warnings.extend(f"{doc['path']}: {warning}" for warning in doc["warnings"])

    for doc in documents:
        doc.pop("text", None)

    return {
        "path": str(package),
        "status": "WARN" if warnings else "PASS",
        "warnings": warnings,
        "documents": documents,
        "inventory": {
            "documentCount": len(documents),
            "categories": sorted({doc["category"] for doc in documents}),
            **trace_inventory,
        },
    }


def inspect_legacy(path: Path, kind: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    headings, _ = markdown_h2_sections(text)
    expected = LEGACY_FUNCTIONAL_HEADINGS if kind == "functional" else LEGACY_TECHNICAL_HEADINGS
    declared = re.search(r"\*\*Document type:\*\*\s*(Functional|Technical)\b", text, re.I)
    declared_matches = bool(declared and declared.group(1).lower() == kind)
    overlap = len(set(headings) & set(expected)) / len(expected)
    recognized = bool(
        (LEGACY_MARKER in text and declared_matches)
        or (declared_matches and overlap >= 0.6)
        or overlap >= 0.8
    )
    if not recognized:
        return {
            "path": str(path),
            "documentType": kind,
            "status": "UNRECOGNIZED_FORMAT",
            "warnings": [],
            "inventory": {},
        }

    missing = [heading for heading in expected if heading not in headings]
    found = [heading for heading in headings if heading in expected]
    warnings: list[str] = []
    if missing:
        warnings.append("Missing required headings: " + ", ".join(missing))
    if found != [heading for heading in expected if heading in headings]:
        warnings.append("Required headings are not in the template order")
    malformed = malformed_id_tokens(text)
    if malformed:
        warnings.append("Identifiers do not use three digits: " + ", ".join(sorted(malformed)))
    return {
        "path": str(path),
        "documentType": kind,
        "status": "WARN" if warnings else "PASS",
        "warnings": warnings,
        "inventory": {"identifiers": sorted(id_tokens(text))},
    }


def add_legacy_traceability(functional: dict[str, Any], technical: dict[str, Any]) -> dict[str, Any]:
    if functional["status"] == "UNRECOGNIZED_FORMAT" or technical["status"] == "UNRECOGNIZED_FORMAT":
        return {"status": "NOT_CHECKED", "reason": "both legacy documents must use a recognized format"}
    prefixes = {"UC", "FR", "BR", "NFR", "INT", "AC"}
    functional_ids = {
        item for item in functional["inventory"]["identifiers"] if item.split("-", 1)[0] in prefixes
    }
    technical_ids = {
        item for item in technical["inventory"]["identifiers"] if item.split("-", 1)[0] in prefixes
    }
    unreferenced = sorted(functional_ids - technical_ids)
    orphaned = sorted(technical_ids - functional_ids)
    warnings: list[str] = []
    if unreferenced:
        warnings.append("Functional identifiers not referenced technically: " + ", ".join(unreferenced))
    if orphaned:
        warnings.append("Technical references absent from the functional design: " + ", ".join(orphaned))
    return {"status": "WARN" if warnings else "PASS", "warnings": warnings}


def human_report(report: dict[str, Any]) -> str:
    lines = ["Artemis Designer structural preflight"]
    if report.get("mode") == "package":
        package = report["package"]
        lines.append(f"Package: {package['status']} — {package['path']}")
        lines.append(f"  Documents: {package['inventory']['documentCount']}")
        for warning in package["warnings"]:
            lines.append(f"  Warning: {warning}")
    else:
        for key in ("functional", "technical"):
            item = report.get(key)
            if not item:
                continue
            lines.append(f"{key.capitalize()}: {item['status']} — {item['path']}")
            for warning in item["warnings"]:
                lines.append(f"  Warning: {warning}")
        if report.get("traceability"):
            lines.append(f"Traceability: {report['traceability']['status']}")
            for warning in report["traceability"].get("warnings", []):
                lines.append(f"  Warning: {warning}")
    lines.append("Advisory only: complete semantic review is still required.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report: dict[str, Any] = {"schemaVersion": "2.0", "advisory": True}
    try:
        if args.package:
            report["mode"] = "package"
            report["package"] = inspect_package(args.package)
        else:
            report["mode"] = "legacy"
            if args.functional:
                report["functional"] = inspect_legacy(args.functional, "functional")
            if args.technical:
                report["technical"] = inspect_legacy(args.technical, "technical")
            if "functional" in report and "technical" in report:
                report["traceability"] = add_legacy_traceability(
                    report["functional"], report["technical"]
                )
    except (OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(human_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
