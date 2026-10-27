#!/usr/bin/env python3
"""Deterministically merge worker handoffs without treating local success as global closure."""
import argparse
import json
from pathlib import Path

from xo_coverage import gap
from xo_export_parser import _redact_structure
from universal_config import parent_source

REQUIRED = {"source_identity", "capability_scope", "goals_events", "entry_assumptions", "routes_returns", "state_contracts", "dependencies", "exclusions", "gap_ids", "quality"}
STAGES = {"entry", "identity_authorization", "dispatch", "child_execution", "shared_hooks", "errors_retries", "interrupt_resume", "completion_transfer"}


def validate_assignments(ledger, handoffs, plan):
    """Check declared work ownership, not worker filesystem access or source truth."""
    policy = plan.get("ownership_policy", {})
    revision, refs = policy.get("shared_contract_revision"), policy.get("shared_contract_refs")
    if policy.get("assignments_locked") is not True or not isinstance(revision, str) or not revision.strip() or not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise ValueError("Lock assignments and publish a versioned shared contract before accepting delegated handoffs")
    if policy.get("workers_may_expand_scope") is not False or policy.get("workers_may_delegate") is not False:
        raise ValueError("Workers cannot independently expand scope or delegate")
    if policy.get("shared_ledger_writer") != "coordinator" or policy.get("dependency_requests_to") != "coordinator":
        raise ValueError("Shared-ledger changes and dependency requests must go through the coordinator")
    artifacts = {a["id"]: a for a in ledger["artifacts"]}
    packages, owners = {}, {}
    for package in plan.get("work_packages", []):
        pid = package["id"]
        if pid in packages:
            raise ValueError("Duplicate work package ID")
        packages[pid] = package
        for aid in package.get("owned_artifact_ids", []):
            if aid not in artifacts or aid in owners:
                raise ValueError("Unknown or multiply owned artifact in work plan")
            owners[aid] = pid
    required = {b["artifact_id"] for b in ledger["bots"]} | {
        a["id"] for a in ledger["artifacts"] if a["role"] not in ("definition", "asset") and a.get("source_hash")}
    if not required <= owners.keys():
        raise ValueError("Selected bot or companion source lacks an assigned owner")
    for package in packages.values():
        if any(pid not in packages for pid in package.get("depends_on", [])):
            raise ValueError("Work package depends on an unknown package")
    seen_packages, claims = set(), {}
    for handoff in handoffs:
        pid = handoff.get("work_package_id")
        if pid not in packages or pid in seen_packages:
            raise ValueError("Unknown or duplicate work package handoff")
        seen_packages.add(pid)
        if handoff.get("shared_contract_revision") != policy["shared_contract_revision"]:
            raise ValueError("Stale or missing shared contract revision in handoff")
        inspected = handoff.get("analyzed_artifacts")
        if not isinstance(inspected, list) or not inspected:
            raise ValueError("Handoff must declare the source artifacts analyzed")
        for record in inspected:
            if not isinstance(record, dict):
                raise ValueError("Analyzed artifact must be an identity/hash record")
            aid = record.get("artifact_id")
            if owners.get(aid) != pid or aid in claims:
                raise ValueError("Out-of-assignment or duplicate source analysis claim")
            if not record.get("source_hash") or record["source_hash"] != artifacts[aid].get("source_hash"):
                raise ValueError("Analyzed artifact hash does not match manifest")
            claims[aid] = pid
        if handoff.get("source_identity", {}).get("artifact_id") not in {r["artifact_id"] for r in inspected}:
            raise ValueError("Primary source must be included in the assigned analysis claim")
    return owners, claims


def reconcile(ledger, handoffs, plan=None):
    result = {"schema_version": 2, "parents": [], "children": [], "shared_handoffs": [], "shared_runtime": "pending_review", "end_to_end": "pending_review",
              "global_status": "partial", "coverage_gaps": list(ledger["coverage_gaps"]), "routes_returns": [], "state_contracts": [], "journeys": []}
    result.update(linked_source_dependencies=ledger.get("linked_bots", []), event_bindings=ledger.get("event_bindings", []))
    if plan is not None:
        owners, claims = validate_assignments(ledger, handoffs, plan)
        result["ownership_validation"] = "declared_assignments_checked"
        result["shared_contract_revision"] = plan["ownership_policy"]["shared_contract_revision"]
        for aid in sorted(set(owners) - set(claims)):
            gap(result, "present_but_not_inspected", [aid], [owners[aid]], "Assigned source has no analysis handoff.", "Complete the owning package; do not have another worker absorb it without reassignment.")
    else:
        result["ownership_validation"] = "not_checked_legacy_handoffs"
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
        if plan is not None:
            seen.update(record["artifact_id"] for record in handoff["analyzed_artifacts"])
        parent = aid in expected and parent_source(expected[aid], ledger.get("parent_id"))
        result["parents" if parent else "children" if aid in expected else "shared_handoffs"].append(handoff)
        result["routes_returns"].extend(handoff["routes_returns"])
        result["state_contracts"].extend(handoff["state_contracts"])
        for journey in handoff.get("journeys", []):
            covered = {s.get("stage") for s in journey.get("stages", []) if s.get("evidence") and (s.get("owner") or s.get("gap_id"))}
            journey["status"] = "source_accounted_runtime_unverified" if STAGES <= covered else "partial"
            result["journeys"].append(journey)
    for aid in sorted(set(expected) - seen):
        role = "Parent" if parent_source(expected[aid], ledger.get("parent_id")) else "Child"
        gap(result, "present_but_not_inspected", [aid], [expected[aid]["id"]], f"{role} work package has no validated handoff.", "Complete the selected source pass, including local goals and event behavior.")
    goal_owners = {}
    for handoff in result["parents"] + result["children"]:
        for goal in handoff["goals_events"]:
            # Same wording is a lead only; outcomes and registry precedence need review.
            name = goal.get("name") if isinstance(goal, dict) else str(goal)
            goal_owners.setdefault(name, set()).add(handoff["source_identity"].get("bot_id", "shared"))
    for name, owners in sorted(goal_owners.items(), key=lambda pair: str(pair[0])):
        if len(owners) > 1:
            gap(result, "routing_overlap", sorted(owners), [name], "Several sources expose the same goal label; outcomes and routing priority may differ.", "Compare trigger/registry semantics and record the scope or precedence decision.")
    # Even fully accounted children do not close a parent, hook or journey gap.
    gap(result, "present_but_not_inspected", ["coordinator"], ["selected-system"], "Merged handoffs require independent coordinator reconciliation.", "Review responsibilities, exact target owners, entry/return state, resets, hooks, terminal loops and journey edge evidence.")
    return _redact_structure(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("handoffs", nargs="+", type=Path)
    parser.add_argument("--plan", type=Path, help="Required for coordinated subagent runs: check exclusive source ownership and shared-contract revision")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new reconciliation output file")
    try:
        result = reconcile(json.loads(args.ledger.read_text()), [json.loads(p.read_text()) for p in args.handoffs], json.loads(args.plan.read_text()) if args.plan else None)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
