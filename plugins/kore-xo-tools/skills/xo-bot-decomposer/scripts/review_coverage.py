#!/usr/bin/env python3
"""Validate semantic dispositions and matching early warnings in completed documents.

This checks recorded evidence/accounting, not the truth of an analyst's conclusions.
"""
import argparse
import json
from pathlib import Path

from xo_coverage import coverage_section

DISPOSITIONS = {"analyzed", "evidence_only", "excluded_by_scope", "external_unavailable", "unresolved", "unsupported"}


def validate(ledger, documents):
    errors = []
    expected = coverage_section(ledger).strip()
    ids = [i["id"] for i in ledger["review_items"]]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate review item IDs")
    for key in ("artifacts", "bots", "node_occurrences", "component_definitions", "webhooks", "events", "bot_functions", "botkit_hooks", "review_items"):
        if ledger["counts"].get(key) != len(ledger[key]):
            errors.append(f"Count mismatch: {key}")
    item_ids = set(ids)
    discovered_occurrences = sum(d["expanded_occurrences"] for d in ledger["discovery"].values())
    discovered_components = sum(d["component_definitions"] for d in ledger["discovery"].values())
    if discovered_occurrences != len(ledger["node_occurrences"]) or discovered_components != len(ledger["component_definitions"]):
        errors.append("Discovery and normalized graph totals do not reconcile")
    for key in ("node_occurrences", "component_definitions", "events", "executable_evidence"):
        if any(record["id"] not in item_ids for record in ledger[key]):
            errors.append(f"Missing review dispositions for {key}")
    for key in ("bot_functions", "botkit_hooks"):
        if any(record.get("review_id") not in item_ids for record in ledger[key]):
            errors.append(f"Missing review dispositions for {key}")
    artifact_reviews = [i["source"] for i in ledger["review_items"] if i["kind"] == "artifact"]
    if sorted(artifact_reviews) != sorted(a["id"] for a in ledger["artifacts"]):
        errors.append("Artifact discovery and dispositions do not reconcile")
    occurrences = {o["id"] for o in ledger["node_occurrences"]}
    webhook_uses = [o["id"] for wh in ledger["webhooks"] for o in wh["occurrences"]]
    if any(o not in occurrences for o in webhook_uses) or ledger["counts"]["webhook_occurrences"] != len(webhook_uses):
        errors.append("Webhook occurrence accounting does not reconcile")
    by_name = {path.name: path for path in documents}
    for item in ledger["review_items"]:
        if item["disposition"] not in DISPOSITIONS or not item.get("reason") or item["reason"] == "Semantic review pending":
            errors.append(f"Unreviewed disposition: {item['id']}")
        if item["disposition"] == "excluded_by_scope" and not item.get("scope_decision"):
            errors.append(f"Missing scope decision: {item['id']}")
        if item["disposition"] == "analyzed":
            if not item.get("document_refs"):
                errors.append(f"Missing document references: {item['id']}")
            for ref in item.get("document_refs", []):
                filename, _, anchor = ref.partition("#")
                path = by_name.get(filename)
                if not path or not path.exists() or (anchor and anchor not in path.read_text()):
                    errors.append(f"Unverified document reference: {item['id']}: {ref}")
    for g in ledger["coverage_gaps"]:
        if g["status"] not in ("open", "deferred", "resolved"):
            errors.append(f"Invalid gap status: {g['id']}")
        if g["status"] == "resolved" and not (g.get("resolution_history") and g.get("resolution_evidence")):
            errors.append(f"Gap closure lacks evidence/history: {g['id']}")
    open_static = [g for g in ledger["coverage_gaps"] if g["status"] != "resolved" and g["severity"] != "runtime"]
    if open_static and ledger["status"]["implementation_dependencies"] not in ("partial", "pending_review", "pending_semantic_review"):
        errors.append("Open static gaps cannot be marked implementation-complete")
    if ledger["status"]["runtime_validation"] != "not_established" and not ledger.get("runtime_evidence"):
        errors.append("Runtime status needs independent evidence")
    for path in documents:
        text = path.read_text()
        title, separator, rest = text.partition("\n")
        if not title.startswith("# ") or not separator or not rest.lstrip().startswith(expected):
            errors.append(f"Missing, stale or misplaced coverage warning: {path.name}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--business", type=Path)
    parser.add_argument("--technical", type=Path)
    parser.add_argument("--system-review", type=Path)
    parser.add_argument("--render-warning", type=Path, help="Write the current shared warning for insertion immediately below each title")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    if args.render_warning:
        args.render_warning.write_text(coverage_section(ledger))
        return 0
    if not args.business or not args.technical or (ledger["universal"] and not args.system_review):
        parser.error("Both final documents and, for universal mode, the system review are required")
    errors = validate(ledger, [p for p in (args.business, args.technical, args.system_review) if p])
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
