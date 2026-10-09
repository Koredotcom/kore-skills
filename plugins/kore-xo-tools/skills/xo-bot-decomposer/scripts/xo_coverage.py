"""Build a versioned, conservative coverage ledger from selected static sources."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from source_scan import scan
from xo_graph import discover_graph, walk
from xo_export_parser import _redact_structure, _redact_text


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def stable_id(prefix, *values):
    return prefix + "-" + digest(json.dumps(values, sort_keys=True))[:12]


def gap(ledger, category, evidence, affected, consequence, next_input, severity="blocking"):
    record = {"id": stable_id("GAP", category, evidence, affected), "category": category, "severity": severity,
              "evidence": evidence, "affected": affected, "consequence": consequence, "next_input": next_input,
              "status": "open", "decision": "unresolved", "resolution_history": []}
    if not any(g["id"] == record["id"] for g in ledger["coverage_gaps"]):
        ledger["coverage_gaps"].append(record)
    return record


def build(artifacts, exports, scope="full", universal=False, parent_id=None, deferred=()):
    ledger = {"schema_version": 2, "scope": scope, "universal": universal, "parent_id": parent_id,
              "artifacts": [], "bots": [], "node_occurrences": [], "component_definitions": [], "webhooks": [], "events": [],
              "bot_functions": [], "calls": [], "botkit_hooks": [], "registrations": [], "configuration": [],
              "state_contracts": [], "routing_dependencies": [], "executable_evidence": [], "coverage_gaps": [],
              "review_items": [], "discovery": {}, "status": {"parser_execution": "completed", "static_document_coverage": "pending_review",
              "implementation_dependencies": "pending_review", "source_release_compatibility": "unverified", "runtime_validation": "not_established"}}
    scans = []

    def review_item(kind, source, location, owners):
        item = {"id": stable_id("ITEM", kind, source, location), "kind": kind, "source": source, "location": location,
                "owners": owners, "disposition": "evidence_only", "reason": "Semantic review pending", "document_refs": []}
        if not any(r["id"] == item["id"] for r in ledger["review_items"]):
            ledger["review_items"].append(item)
        return item["id"]

    def scan_code(code, source, pointer, owner):
        evidence = source + "#" + pointer
        result = scan(code, evidence)
        scans.append((source, result))
        ledger["executable_evidence"].append({"id": review_item("executable", source, pointer, owner), "source": evidence,
                                              "code": _redact_text(code), "analysis_method": "lexical", "limits": result["limits"]})
        ledger["bot_functions"].extend(result["functions"])
        ledger["calls"].extend(result["calls"])
        ledger["botkit_hooks"].extend(result["hooks"])
        ledger["registrations"].extend(result["registrations"])
        ledger["state_contracts"].extend(result["states"])
        for ref in result["environment"]:
            ledger["configuration"].append({**ref, "kind": "reference", "effective_value": "unknown"})
        for imp in result["imports"]:
            review_item("import", source, f"{pointer}:line{imp['line']}", owner)
        gap(ledger, "present_but_not_inspected", [evidence], owner, "Executable source has lexical inventory; activation, aliases, registration and control flow need semantic review.", "Review sanitized source and bootstrap/dispatcher; record findings and dispositions.")
        # Explicit literal call targets are candidates only: do not infer custom helper semantics.
        for call in result["calls"]:
            if call["name"].split(".")[-1] in ("executeTask", "startDialog", "invokeDialog", "triggerIntent", "routeToBot"):
                strings = re.findall(r"['\"]([^'\"]+)['\"]", call["arguments"])
                ledger["routing_dependencies"].append({"source": evidence, "line": call["line"], "mechanism": call["name"],
                    "requested_owner": strings[0] if len(strings) >= 2 else None, "target": strings[-1] if strings else None,
                    "comparison": "unverified_call_signature", "status": "unresolved", "return_contract": "unverified"})
        if any(c["name"].split(".")[-1] in ("fetch", "get", "post", "request", "axios") for c in result["calls"]):
            gap(ledger, "unknown_backend_semantics", [evidence], owner, "Client calls establish consumer expectations, not provider policy or schema.", "Matching provider contracts, sanitized success/error fixtures and timeout units.")

    for artifact in artifacts:
        public = {k: v for k, v in artifact.items() if not k.startswith("_")}
        ledger["artifacts"].append(public)
        aid, role = artifact["id"], artifact["role"]
        review_item("artifact", aid, "", [])
        if role == "javascript" and artifact.get("_text") is not None:
            scan_code(artifact["_text"], aid, "", [])
        elif artifact.get("_json") is not None and role != "definition":
            for pointer, value in walk(artifact["_json"]):
                if not isinstance(value, (dict, list)):
                    ledger["configuration"].append({"source": aid, "pointer": pointer, "kind": "definition",
                        "field": pointer.rsplit("/", 1)[-1], "value": _redact_structure(value, pointer.rsplit("/", 1)[-1]),
                        "provenance": artifact["source_group"], "effective_value": "unknown"})
            if role == "contract":
                gap(ledger, "present_but_not_inspected", [aid], [], "Supplied contract is inventoried; endpoint/version/schema applicability is not established.", "Map provider schema and fixtures to each consuming service/hook.")
        elif role not in ("asset", "definition"):
            gap(ledger, "unsupported_parse", [aid], [], "Companion artifact was discovered but not parsed.", "Inspect this source format or provide a supported equivalent.")

    webhook_map = {}
    for export in exports:
        data, aid = export["data"], export["artifact_id"]
        bot_id = str(data.get("_id") or data.get("botId") or data.get("id") or aid)
        bot = {"id": bot_id, "artifact_id": aid, "name": data.get("name", data.get("botName", bot_id)),
               "version": data.get("xoVersion", data.get("platformVersion", data.get("version"))), "version_route": export["version_route"],
               "dialogs": [{"id": d.get("_id"), "name": d.get("localeData", {}).get("en", {}).get("name", d.get("name"))} for d in data.get("dialogs", [])]}
        ledger["bots"].append(bot)
        graph = discover_graph(data, export.get("prefix", ""))
        ledger["discovery"][aid] = graph["discovery"]
        for issue in graph["graph_issues"]:
            gap(ledger, "unsupported_parse" if "unsupported" in issue["kind"] or "limit" in issue["kind"] else "unresolved_reference", [aid + "#" + issue["pointer"]], [issue.get("dialog_id")], issue["kind"], "Inspect source shape/reference and account for the affected execution path.")
        for occurrence in graph["node_occurrences"]:
            o = {**occurrence, "bot_id": bot_id, "artifact_id": aid}
            o["id"] = review_item("node_occurrence", aid, o["occurrence_path"], [o["dialog_id"]])
            ledger["node_occurrences"].append(o)
            c, n = o["component"], o["node"]
            if str(o["type"]).lower() in ("sdkwebhook", "webhook") or str(c.get("type", "")).lower() == "sdkwebhook":
                key = (aid, o["component_id"] or o["source_pointer"])
                if key not in webhook_map:
                    webhook_map[key] = {"id": stable_id("WH", *key), "bot_id": bot_id, "artifact_id": aid,
                        "component_id": o["component_id"], "name": o["name"], "type": o["type"], "occurrences": [],
                        "definition": c, "handler_status": "missing_source", "handler_candidates": [], "provider_contract": "unverified", "runtime_binding": "unverified"}
                timeout = n.get("webhookTimeout", c.get("webhookTimeout"))
                webhook_map[key]["occurrences"].append({"id": o["id"], "dialog_id": o["dialog_id"], "source_pointer": o["source_pointer"],
                    "parent_chain": o["parent_chain"], "timeout_value": timeout, "timeout_unit": n.get("webhookTimeoutUnit", c.get("webhookTimeoutUnit", "unknown")),
                    "transitions": o["transitions_raw"], "parameters": n.get("parameters", c.get("parameters", "not_exported"))})
            if n.get("type") == "intent" and c.get("dialogId") and c.get("dialogId") != o["dialog_id"]:
                ledger["routing_dependencies"].append({"source": aid + "#" + o["source_pointer"], "mechanism": "dialogId",
                    "requested_owner": c.get("botId", bot_id), "target": c["dialogId"], "comparison": "exact_id", "status": "unresolved", "return_contract": "unverified"})
        for i, c in enumerate(data.get("dialogComponents", [])):
            cid = c.get("_id")
            ledger["component_definitions"].append({"id": review_item("component", aid, f"/dialogComponents/{i}", []), "artifact_id": aid, "component_id": cid,
                "type": c.get("type"), "definition": c, "occurrences": [o["id"] for o in ledger["node_occurrences"] if o["artifact_id"] == aid and o["component_id"] == cid]})
            if str(c.get("type", "")).lower() in ("sdkwebhook", "webhook") and (aid, cid) not in webhook_map:
                webhook_map[(aid, cid)] = {"id": stable_id("WH", aid, cid), "bot_id": bot_id, "artifact_id": aid,
                    "component_id": cid, "name": c.get("name"), "type": c.get("type"), "occurrences": [],
                    "definition": c, "handler_status": "uncalled_definition", "handler_candidates": [], "provider_contract": "unverified", "runtime_binding": "unverified"}
            if c.get("type") == "service":
                gap(ledger, "unknown_backend_semantics", [aid + f"#/dialogComponents/{i}"], [cid], "Service export documents a client, not verified backend policy and response contract.", "Provider schema/fixtures, timeout units, retries, failure and continuation behavior.")
        for pointer, value in walk(data, export.get("prefix", "")):
            key = pointer.rsplit("/", 1)[-1]
            if isinstance(value, (dict, list)) and re.search(r"event|taskend|onconnect|transfer|fallback", key, re.I):
                ledger["events"].append({"id": review_item("event", aid, pointer, [bot_id]), "bot_id": bot_id,
                    "source": aid + "#" + pointer, "configuration": value, "record_kind": "binding_candidate" if isinstance(value, dict) and any(k in value for k in ("target", "taskId", "dialogId", "enabled", "enable")) else "configuration_container", "binding": "exported_only"})
            if isinstance(value, str):
                # Capture every potentially executable string, including encoded script/message callbacks.
                from urllib.parse import unquote
                code = unquote(value)
                if re.search(r"script|processor|validation|callback|retry", key, re.I) or re.search(r"\b(?:context\.|env\.|function\s|(?:const|let|var)\s)|=>|<vxml|AgentTransfer", code):
                    scan_code(code, aid, pointer, [bot_id])
                    if re.search(r"AgentTransfer|<vxml|<transfer", code, re.I):
                        ledger["events"].append({"id": review_item("scripted_transfer", aid, pointer, [bot_id]), "bot_id": bot_id,
                            "source": aid + "#" + pointer, "record_kind": "scripted_transfer_candidate", "mechanism": "script_or_markup_candidate", "code": code, "binding": "unverified"})
            if re.search(r"environment|variables|config", key, re.I) and isinstance(value, (dict, list)):
                ledger["configuration"].append({"source": aid, "pointer": pointer, "kind": "exported_container", "value": value, "effective_value": "unknown"})
        for i, d in enumerate(data.get("dialogs", [])):
            review_item("dialog", aid, f"/dialogs/{i}", [d.get("_id")])
            if d.get("isHidden") or d.get("isFollowUp"):
                ledger["events"].append({"id": review_item("support_dialog", aid, f"/dialogs/{i}", [d.get("_id")]), "bot_id": bot_id,
                    "source": aid + f"#/dialogs/{i}", "dialog_id": d.get("_id"), "record_kind": "support_dialog", "binding": "requires_event_configuration_review"})

    # Names are scoped to the source group. Equal hashes identify copies, not execution ownership.
    group_by_id = {a["id"]: a["source_group"] for a in artifacts}
    companion_ids = {a["id"] for a in artifacts if a.get("source_kind") == "companion"}
    for fn in ledger["bot_functions"]:
        fn["id"] = stable_id("FN", fn["source"], fn["start"])
        fn["implementation_hash"] = digest(fn["code"])
        fn["review_id"] = review_item("function", fn["source"].split("#")[0], f"{fn['source']}:{fn['line']}:{fn['start']}:{fn['name']}", [])
    for call in ledger["calls"]:
        source_id = call["source"].split("#")[0]
        matches = [f for f in ledger["bot_functions"] if f["name"] == call["name"] and group_by_id.get(f["source"].split("#")[0]) == group_by_id.get(source_id)]
        if not matches and len(exports) == 1:
            # An explicitly supplied companion can support the sole selected export;
            # multiple-bot companion ownership must be reviewed rather than guessed.
            matches = [f for f in ledger["bot_functions"] if f["name"] == call["name"] and f["source"].split("#")[0] in companion_ids]
        call["definition_candidates"] = [f["id"] for f in matches]
        if matches:
            call["resolution"] = "source_candidate" if len(matches) == 1 else "ambiguous"
            for f in matches:
                f["callers"].append({"source": call["source"], "line": call["line"]})
        elif call["category"] == "custom_candidate":
            gap(ledger, "unresolved_helper", [call["source"] + f":{call['line']}"], [call["name"]], "Custom/external call has no scoped definition candidate; lexical analysis cannot establish activation.", "Matching helper source or evidence that this is a platform/external API; review imports and dynamic aliases.")
    for hook in ledger["botkit_hooks"]:
        candidates = [f for f in ledger["bot_functions"] if f["name"] == hook["handler"] and f["source"] == hook["source"]]
        hook["definition_candidates"] = [f["id"] for f in candidates]
        hook["dispatch"] = "unresolved"
        if len(candidates) == 1:
            body = candidates[0]["body"]
            hook["dispatch"] = "component_name_candidate" if re.search(r"\bcomponentName\b", body) else "generic_candidate"
        hook["review_id"] = review_item("hook", hook["source"].split("#")[0], f"{hook['source']}:{hook['line']}:{hook['offset']}:{hook['event']}", [hook.get("bot_id")])
    for wh in webhook_map.values():
        if not wh["occurrences"]:
            continue
        candidates = [h for h in ledger["botkit_hooks"] if "webhook" in h["event"].lower() and h["registration"] == "registration_candidate" and h.get("bot_id") in (wh["bot_id"], parent_id) and h.get("bot_id") is not None]
        wh["handler_candidates"] = candidates
        if candidates:
            wh["handler_status"] = "source_candidate_requires_dispatch_review"
        gap(ledger, "present_but_not_inspected" if candidates else "missing_source", [wh["id"]], [o["dialog_id"] for o in wh["occurrences"]],
            "SDK implementation/dispatch is unverified." if candidates else "Required SDK handler/registration source is missing or not resolved.", "Review matching bootstrap, bot registration, dispatch, callback and state contract.")
        gap(ledger, "unknown_backend_semantics", [wh["id"]], [wh["name"]], "A handler source match cannot establish backend schemas, timeout units, callback completion or telephony semantics.", "Provider contracts/fixtures and node/handler timeout units; reconcile success, malformed, timeout, retry and failure continuations.")
        gap(ledger, "unverified_runtime_binding", [wh["id"]], [wh["name"]], "Effective SDK registration and callback delivery are not established by source.", "Deployment/version and runtime trace evidence.", "runtime")
    ledger["webhooks"] = list(webhook_map.values())
    for route in ledger["routing_dependencies"]:
        exact = [(b, d) for b in ledger["bots"] for d in b["dialogs"] if route["target"] and route["target"] in (d["id"], d["name"])]
        own = [(b, d) for b, d in exact if route["requested_owner"] in (b["id"], b["name"])]
        route["source_candidates"] = [{"bot_id": b["id"], "dialog_id": d["id"]} for b, d in exact]
        route["status"] = "matched_source" if len(own) == 1 and route["comparison"] == "exact_id" else "owner_mismatch" if exact and route["requested_owner"] and not own else "dynamic_or_unverified"
        if route["status"] != "matched_source":
            gap(ledger, "incompatible_artifact_set" if route["status"] == "owner_mismatch" else "unresolved_dynamic_target", [route["source"]], [route["target"]],
                "Target source availability does not establish requested owner, dispatcher semantics or resume-state compatibility.", "Confirm exact registry/dispatch semantics and entry/return state contract; preserve intended scope.")
    for name in deferred:
        gap(ledger, "missing_source", ["user-deferred"], [name], "Required or proposed input is deferred; its behavior has not been inferred.", "Supply input or record an explicit replacement/exclusion decision.")
    if universal:
        gap(ledger, "present_but_not_inspected" if parent_id else "missing_source", ["selected-system"], [parent_id or "parent/registry"], "Child completion does not establish shared runtime, parent registry or end-to-end journeys.", "Review parent registry/bootstrap, scoped child handoffs and shared hooks; reconcile ownership, state, route overlap, return and terminal journeys.")
    if scope == "goals-only":
        gap(ledger, "intentionally_excluded", ["requested-goals-only-scope"], [f"{len(ledger['events'])} event records", f"{len(ledger['botkit_hooks'])} hook candidates", f"{len(ledger['executable_evidence'])} executable records"],
            "Technical support behavior remains inventoried but a goal-only report is not a full implementation specification.", "Expand scope if implementation parity is required.")
    # Case differences are leads, not proof of a bug; alias/lifetime review stays explicit.
    fields = {}
    for s in ledger["state_contracts"]:
        fields.setdefault(s["field"].casefold(), set()).add(s["field"])
    for variants in fields.values():
        if len(variants) > 1:
            gap(ledger, "state_contract_ambiguity", sorted(variants), sorted(variants), "Case-distinct state paths may describe different keys; producer/consumer compatibility needs review.", "Trace exact keys, aliases, initialization, resets and failure-to-success paths.")
    ledger["counts"] = {key: len(ledger[key]) for key in ("artifacts", "bots", "node_occurrences", "component_definitions", "webhooks", "events", "bot_functions", "botkit_hooks", "review_items")}
    ledger["counts"]["event_binding_candidates"] = sum(e.get("record_kind") == "binding_candidate" for e in ledger["events"])
    ledger["counts"]["event_configuration_containers"] = sum(e.get("record_kind") == "configuration_container" for e in ledger["events"])
    ledger["counts"]["webhook_occurrences"] = sum(len(w["occurrences"]) for w in ledger["webhooks"])
    ledger["counts"]["unique_function_implementations"] = len({f["implementation_hash"] for f in ledger["bot_functions"]})
    ledger["status"]["implementation_dependencies"] = "partial" if ledger["coverage_gaps"] else "pending_semantic_review"
    return _redact_structure(ledger)


def coverage_section(ledger):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["## Coverage and missing inputs", "", f"**Boundary:** {ledger['scope']}; {len(ledger['artifacts'])} selected artifacts; universal system: {ledger['universal']}.",
             f"**Static document coverage:** {ledger['status']['static_document_coverage']}. **Implementation dependencies:** {ledger['status']['implementation_dependencies']}.",
             f"**Source-release compatibility:** {ledger['status']['source_release_compatibility']}. **Runtime validation:** {ledger['status']['runtime_validation']}.",
             "", "Inventory is not semantic analysis or deployed behavior. Executable-source matches are lexical candidates until reviewed.", "",
             "| Gap ID | Status | Affected behavior | Consequence | Next input/decision |", "|---|---|---|---|---|"]
    for g in ledger["coverage_gaps"]:
        if g["status"] != "resolved":
            lines.append("| " + " | ".join(cell(v) for v in (g["id"], g["status"], ", ".join(str(a) for a in g["affected"]), g["consequence"], g["next_input"])) + " |")
    if not ledger["coverage_gaps"]:
        lines.append("No blocking missing implementation detected by discovery within the inspected boundary; semantic review is pending. External hooks may exist independently of webhook nodes.")
    lines.extend(["", f"**Coverage counts:** {json.dumps(ledger['counts'], sort_keys=True)}. Analyzed dispositions: {sum(i['disposition'] == 'analyzed' for i in ledger['review_items'])}/{len(ledger['review_items'])}.",
                  "**Inspected source inventory and full register:** [_coverage.json](_coverage.json); [_artifact_manifest.json](_artifact_manifest.json).", ""])
    return "\n".join(lines)


def write(ledger, output):
    output = Path(output)
    for name, data in (("_coverage.json", ledger), ("_artifact_manifest.json", {"schema_version": 2, "artifacts": ledger["artifacts"]})):
        (output / name).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    section = coverage_section(ledger)
    (output / "_coverage.md").write_text("# Dependency and coverage register\n\n" + section)
    for name, title in (("_analysis_draft.md", "Business goal decomposition"), ("_technical_reference_draft.md", "Technical reference")):
        (output / name).write_text(f"# {title}\n\n{section}\n**Source:** selected artifact manifest\n\nThis is an evidence-backed draft boundary. Complete semantic analysis and item dispositions before delivery.\n")
    if ledger["universal"]:
        plan = {"schema_version": 2, "manifest": "_artifact_manifest.json", "parent_id": ledger["parent_id"],
            "work_packages": [{"id": f"child_{i:03}", "bot_id": b["id"], "artifact_id": b["artifact_id"], "output_directory": f"children/child_{i:03}", "status": "pending"} for i, b in enumerate(ledger["bots"], 1)] +
                [{"id": "shared_runtime", "output_directory": "shared_runtime", "status": "pending"}, {"id": "coordinator", "output_directory": "system_review", "status": "pending"}],
            "execution": "Sequential or delegated with identical handoff schema; sources read-only; one tooling owner.",
            "handoff_required": ["source_identity", "capability_scope", "goals_events", "entry_assumptions", "routes_returns", "state_contracts", "dependencies", "exclusions", "gap_ids", "quality"],
            "journey_required": ["entry", "identity_authorization", "dispatch", "child_execution", "shared_hooks", "errors_retries", "interrupt_resume", "completion_transfer"]}
        (output / "_system_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
        (output / "_system_review_draft.md").write_text("# Universal system review\n\n" + section + "\nComplete coordinator reconciliation: responsibility map, route/entry-return matrix, shared-state lifecycle, implementation ledger, journey coverage and scope decisions. Child, shared-runtime and end-to-end statuses remain separate.\n")
