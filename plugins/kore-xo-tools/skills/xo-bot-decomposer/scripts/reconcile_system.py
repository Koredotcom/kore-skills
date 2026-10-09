#!/usr/bin/env python3
"""Deterministically merge worker handoffs without treating local success as global closure."""
import argparse
import json
from pathlib import Path

from xo_coverage import gap
from xo_export_parser import _redact_structure

REQUIRED = {"source_identity", "capability_scope", "goals_events", "entry_assumptions", "routes_returns", "state_contracts", "dependencies", "exclusions", "gap_ids", "quality"}
STAGES = {"entry", "identity_authorization", "dispatch", "child_execution", "shared_hooks", "errors_retries", "interrupt_resume", "completion_transfer"}


def reconcile(ledger, handoffs):
    result = {"schema_version": 2, "children": [], "shared_handoffs": [], "shared_runtime": "pending_review", "end_to_end": "pending_review",
              "global_status": "partial", "coverage_gaps": list(ledger["coverage_gaps"]), "routes_returns": [], "state_contracts": [], "journeys": []}
    expected = {b["artifact_id"]: b for b in ledger["bots"]}
    hashes = {a["id"]: a["source_hash"] for a in ledger["artifacts"]}
    seen = set()
    for handoff in sorted(handoffs, key=lambda h: h.get("source_identity", {}).get("artifact_id", "")):
        if not REQUIRED <= handoff.keys():
            raise ValueError("Incomplete child/shared handoff")
        identity = handoff["source_identity"]
        aid = identity.get("artifact_id")
        if aid not in hashes or hashes[aid] != identity.get("source_hash") or aid in seen:
            raise ValueError("Unknown, changed or duplicate source identity in handoff")
        if aid in expected and identity.get("bot_id") != expected[aid]["id"]:
            raise ValueError("Child identity does not match manifest")
        if not handoff.get("capability_scope"):
            raise ValueError("Handoff requires an explicit capability slice")
        seen.add(aid)
        result["children" if aid in expected else "shared_handoffs"].append(handoff)
        result["routes_returns"].extend(handoff["routes_returns"])
        result["state_contracts"].extend(handoff["state_contracts"])
        for journey in handoff.get("journeys", []):
            covered = {s.get("stage") for s in journey.get("stages", []) if s.get("evidence") and (s.get("owner") or s.get("gap_id"))}
            journey["status"] = "source_accounted_runtime_unverified" if STAGES <= covered else "partial"
            result["journeys"].append(journey)
    for aid in sorted(set(expected) - seen):
        gap(result, "present_but_not_inspected", [aid], [expected[aid]["id"]], "Child work package has no validated handoff.", "Complete the selected child pass.")
    goal_owners = {}
    for handoff in result["children"]:
        for goal in handoff["goals_events"]:
            # Same wording is a lead only; outcomes and registry precedence need review.
            name = goal.get("name") if isinstance(goal, dict) else str(goal)
            goal_owners.setdefault(name, set()).add(handoff["source_identity"].get("bot_id", "shared"))
    for name, owners in sorted(goal_owners.items(), key=lambda pair: str(pair[0])):
        if len(owners) > 1:
            gap(result, "routing_overlap", sorted(owners), [name], "Several children expose the same goal label; outcomes and routing priority may differ.", "Compare trigger/registry semantics and record the scope or precedence decision.")
    # Even fully accounted children do not close a parent, hook or journey gap.
    gap(result, "present_but_not_inspected", ["coordinator"], ["selected-system"], "Merged handoffs require independent coordinator reconciliation.", "Review responsibilities, exact target owners, entry/return state, resets, hooks, terminal loops and journey edge evidence.")
    return _redact_structure(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("handoffs", nargs="+", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new reconciliation output file")
    try:
        result = reconcile(json.loads(args.ledger.read_text()), [json.loads(p.read_text()) for p in args.handoffs])
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
