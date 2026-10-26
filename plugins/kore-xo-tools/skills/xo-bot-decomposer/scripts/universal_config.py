"""Static universal-bot registry and event ownership, using exported identities.

IDs are the default; explicit name mode handles damaged registry identities.
No linked source is fetched or executed. A resolved source target does not prove an enabled runtime binding.
"""
from __future__ import annotations


def identifier(value):
    return value if isinstance(value, str) and value.strip() else None


def identities(data):
    return sorted({value for key in ("_id", "refId", "botId", "streamId", "id")
                   if (value := identifier(data.get(key))) is not None})


def bot_name(data, fallback):
    locales = data.get("localeData")
    english = locales.get("en") if isinstance(locales, dict) else None
    localized = english.get("name") if isinstance(english, dict) else None
    return identifier(data.get("name")) or identifier(data.get("botName")) or identifier(localized) or fallback


def parent_source(bot, parent_id):
    return bool(bot.get("is_universal") or parent_id and parent_id in (bot["id"], *bot.get("identity_aliases", [])))


def is_universal(data):
    kind = data.get("type")
    return bool(
        isinstance(kind, str) and kind.strip().casefold() == "universalbot"
        or data.get("isUniversal") is True
        or data.get("childBots")
        or isinstance(data.get("linkedBotsDetails"), list)
    )


def pointer_key(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def registry_groups(data, prefix="", identity_mode="id"):
    """Preserve occurrences; group by the explicitly selected identity basis."""
    entries, groups = [], {}
    raw = data.get("linkedBotsDetails", [])
    if not isinstance(raw, list):
        return entries, []
    for index, value in enumerate(raw):
        loc = f"{prefix}/linkedBotsDetails/{index}"
        linked_id = identifier(value.get("_id")) if isinstance(value, dict) else None
        entry = {"source_pointer": loc, "linked_bot_id": linked_id, "definition": value}
        entries.append(entry)
        name = identifier(value.get("name")) if isinstance(value, dict) else None
        identity_key = name if identity_mode == "name" else linked_id
        group = groups.setdefault(("value", identity_key) if identity_key else ("pointer", loc), {
            "linked_bot_id": linked_id, "identity_aliases": [], "registry_id_values": [],
            "identity_mode": identity_mode, "identity_key": identity_key,
            "names": [], "registry_pointers": [], "identity_evidence": [],
        })
        if linked_id and linked_id not in group["registry_id_values"]:
            group["registry_id_values"].append(linked_id)
            group["identity_aliases"].append(linked_id)
        group["registry_pointers"].append(loc)
        if isinstance(value, dict) and identifier(value.get("name")) and value["name"] not in group["names"]:
            group["names"].append(value["name"])
    # These are observed ID/stream mappings, not an inferred fallback execution order.
    for field in ("fallbackDetails", "inclusiveDetails"):
        values = data.get(field, [])
        if not isinstance(values, list):
            continue
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                continue
            linked_id = identifier(value.get("_id"))
            key = identifier(value.get("name")) if identity_mode == "name" else linked_id
            group = groups.get(("value", key))
            if group is None or linked_id not in group["registry_id_values"]:
                continue
            alias = identifier(value.get("streamId"))
            if alias and alias not in group["identity_aliases"]:
                group["identity_aliases"].append(alias)
            group["identity_evidence"].append({"source_pointer": f"{prefix}/{field}/{index}", "definition": value})
    for group in groups.values():
        group["overlapping_registry_ids"] = [other["linked_bot_id"] for other in groups.values() if other is not group
            and set(group["identity_aliases"]).intersection(other["identity_aliases"])]
    return entries, list(groups.values())


def group_matches(group, aliases, name):
    if not group["identity_key"]:
        return False
    if group["identity_mode"] == "name":
        return name == group["identity_key"]
    return bool(set(group["identity_aliases"]).intersection(aliases))


def ambiguous_group(group):
    return len(group["registry_id_values"]) > 1 if group["identity_mode"] == "name" else bool(group["overlapping_registry_ids"])


def select_linked(candidates, selected, identity_mode="id"):
    """Expand already selected parents to unambiguous linked exports in intake only."""
    selected = list(selected)
    selected_ids = {a["id"] for a in selected}
    for parent in selected:  # Added nested parents are processed; IDs bound cycles.
        data = parent.get("_definition", {})
        if not is_universal(data):
            continue
        _, groups = registry_groups(data, identity_mode=identity_mode)
        for group in groups:
            if ambiguous_group(group):
                continue
            matches = [a for a in candidates if group_matches(group, identities(a.get("_definition", {})), bot_name(a.get("_definition", {}), None))]
            if len(matches) == 1 and matches[0]["id"] not in selected_ids:
                selected.append(matches[0])
                selected_ids.add(matches[0]["id"])
    return selected_ids


def enrich(ledger, exports, review_item, gap):
    """Add registry, configuration, event and default-task records to coverage."""
    ledger.update(universal_parents=[], registry_entries=[], linked_bots=[], event_bindings=[], universal_discovery={})
    bots = ledger["bots"]
    bot_by_artifact = {b["artifact_id"]: b for b in bots}
    selected_ids = set(bot_by_artifact)
    all_sources = ledger["artifacts"]

    identity_mode = ledger.get("linked_identity_mode", "id")

    def source_matches(group):
        return [b for b in bots if group_matches(group, b["identity_aliases"], b["exported_name"])]

    def unselected_matches(group):
        return [a["id"] for a in all_sources if a["id"] not in selected_ids
                and group_matches(group, a.get("definition_identity_aliases", []), a.get("definition_name"))]

    def task_matches(owner, task):
        if not identifier(task):
            return []
        return [d for d in owner["dialogs"] if task in (d["id"], d.get("ref_id"))]

    def target_record(owner, dialog):
        return {"bot_id": owner["id"], "artifact_id": owner["artifact_id"],
                "dialog_id": dialog["id"], "dialog_ref_id": dialog.get("ref_id"), "dialog_name": dialog["name"]}

    def resolve(parent, groups, owner_id, task, owner_basis="event_configuration"):
        result = {"requested_owner": owner_id, "target": task, "owner_basis": owner_basis,
                  "owner_scope": "unresolved", "owner_candidates": [], "source_candidates": [],
                  "task_found_elsewhere": [], "status": "unresolved"}
        if owner_id is not None and not isinstance(owner_id, str):
            result["status"] = "unsupported_owner_reference"
            return result
        if not identifier(owner_id) or owner_id in parent["identity_aliases"]:
            owners, owner_scope = [parent], "parent"
            if not identifier(owner_id) and owner_basis == "event_configuration":
                result["owner_basis"] = "no_linked_owner_parent_local_lookup"
        else:
            registry = [g for g in groups if owner_id in g["identity_aliases"]]
            result["registry_owner_candidates"] = [{"identity_mode": g["identity_mode"], "identity_key": g["identity_key"], "names": g["names"]} for g in registry]
            if len(registry) != 1:
                result["status"] = "ambiguous_owner" if registry else "unregistered_owner"
                return result
            if ambiguous_group(registry[0]):
                result["status"] = "ambiguous_registry_identity"
                return result
            owners = source_matches(registry[0])
            result["owner_source_identity_mode"] = identity_mode
            result["owner_source_identity_key"] = registry[0]["identity_key"]
            result["unselected_artifact_ids"] = unselected_matches(registry[0])
            owner_scope = "linked_bot"
        result["owner_scope"] = owner_scope
        result["owner_candidates"] = [{"bot_id": b["id"], "artifact_id": b["artifact_id"]} for b in owners]
        result["task_found_elsewhere"] = [target_record(b, d) for b in bots if b not in owners for d in task_matches(b, task)]
        if len(owners) != 1:
            unselected = result.get("unselected_artifact_ids", [])
            result["status"] = "ambiguous_owner_source" if owners or len(unselected) > 1 else "owner_source_unselected" if unselected else "missing_owner_source"
            return result
        if not identifier(task):
            result["status"] = "missing_task_reference"
            return result
        if "{{" in task or "${" in task:
            result["status"] = "dynamic_task_reference"
            return result
        matches = task_matches(owners[0], task)
        result["source_candidates"] = [target_record(owners[0], d) for d in matches]
        result["status"] = ("matched_source" if len(matches) == 1 else "ambiguous_task" if matches
                            else "task_owner_mismatch" if result["task_found_elsewhere"] else "missing_task_source")
        return result

    def record_binding(parent, pointer, event_name, config, resolution, enabled, action, basis=None):
        aid = parent["artifact_id"]
        item_id = review_item("event_binding", aid, pointer, [parent["id"]])
        record = {"id": item_id, "source": aid + "#" + pointer, "bot_id": parent["id"],
                  "event_name": event_name, "configuration": config, "enabled": enabled, "action": action,
                  "record_kind": "binding_candidate", "runtime_binding": "unverified", **resolution}
        if basis:
            record["related_evidence"] = basis
        ledger["event_bindings"].append(record)
        ledger["events"].append(record)
        if record["status"] in ("disabled", "non_dialog_action"):
            return record
        route = {"source": record["source"], "event_binding_id": item_id, "mechanism": "default_dialog" if event_name == "defaultDialogId" else "bot_event",
                 "comparison": "exact_exported_id_or_refId", "return_contract": "unverified", "resolution_method": "universal_configuration", **resolution}
        ledger["routing_dependencies"].append(route)
        if enabled is None:
            gap(ledger, "unverified_event_setting", [record["source"]], [parent["id"], event_name],
                "Event enabled state is not explicit; source target resolution does not establish activation.", "Inspect the matching event/deployment setting.")
        if record["status"] != "matched_source":
            gap(ledger, "unresolved_event_target", [record["source"]], [parent["id"], event_name],
                f"Configured task cannot be resolved to one supplied implementation under its owner ({record['status']}).",
                "Supply the configured owner's export and exact task ID/refId, or reconcile registry/setting evidence; do not substitute a same-name task.")
        return record

    for export in exports:
        data, aid, prefix = export["data"], export["artifact_id"], export.get("prefix", "")
        parent = bot_by_artifact[aid]
        entries, groups = registry_groups(data, prefix, identity_mode)
        if parent["is_universal"]:
            config_fields = ("type", "isUniversal", "childBots", "linkedBotsDetails", "fallbackDetails", "inclusiveDetails", "defaultDialogId", "assignAllChildBots", "universalBotVersion", "interruptOptions", "recentBotLimit", "isCsMatchEnabled")
            configuration = {k: data[k] for k in config_fields if k in data}
            ledger["universal_parents"].append({"id": review_item("universal_parent", aid, prefix, [parent["id"]]),
                "bot_id": parent["id"], "artifact_id": aid, "source_pointer": prefix,
                "configuration": configuration, "local_dialog_ids": [d["id"] for d in parent["dialogs"]]})
            raw = data.get("linkedBotsDetails")
            if not isinstance(raw, list):
                gap(ledger, "unsupported_parse" if "linkedBotsDetails" in data else "missing_source", [aid + "#" + prefix + "/linkedBotsDetails"], [parent["id"]],
                    "Universal registry is absent or not a supported list; linked-source coverage is unknown.", "Provide the linkedBotsDetails registry or inspect the alternate registry format.")
            for entry in entries:
                entry.update(parent_bot_id=parent["id"], artifact_id=aid,
                    id=review_item("linked_registry_entry", aid, entry["source_pointer"], [parent["id"], entry["linked_bot_id"]]))
                ledger["registry_entries"].append(entry)
            for group in groups:
                candidates = source_matches(group)
                unselected = unselected_matches(group)
                status = ("unresolved_identity" if not group["identity_key"] else "ambiguous_registry_identity" if ambiguous_group(group) else "self_reference" if parent in candidates
                          else "matched_source" if len(candidates) == 1 else "ambiguous_source" if candidates or len(unselected) > 1 else "source_unselected" if unselected else "missing_source")
                row = {**group, "parent_bot_id": parent["id"], "parent_artifact_id": aid,
                       "id": review_item("linked_bot", aid, group["registry_pointers"][0] + "/identity", [parent["id"], group["linked_bot_id"]]),
                       "source_candidates": [{"bot_id": b["id"], "artifact_id": b["artifact_id"]} for b in candidates],
                       "unselected_artifact_ids": unselected, "status": status}
                ledger["linked_bots"].append(row)
                if len(group["names"]) > 1 or group["overlapping_registry_ids"] or len(group["registry_id_values"]) > 1:
                    gap(ledger, "registry_identity_disagreement", [aid + "#" + p for p in group["registry_pointers"]], [parent["id"], group["identity_key"]],
                        "Registry names and IDs do not map one-to-one. Identity groups are not a verified bot count; ID-only routes can remain ambiguous even when sources match by name.",
                        "Reconcile against child exports/platform configuration; retain the selected temporary identity basis and every registry entry.")
                if status != "matched_source":
                    gap(ledger, "missing_source" if status == "missing_source" else "unresolved_linked_bot", [aid + "#" + p for p in group["registry_pointers"]], [parent["id"], group["identity_key"]],
                        f"Linked bot registry is accounted for, but its implementation is not uniquely selected ({status}).",
                        "Supply/select the exact linked-bot export, resolve identity ambiguity, or record an explicit capability-scope decision.")
            raw_entries = raw if isinstance(raw, list) else []
            ledger["universal_discovery"][aid] = {
                "registry_entries": len(raw_entries), "linked_bot_identities": len(groups), "identity_mode": identity_mode,
                "distinct_id_values": len({r["_id"] for r in raw_entries if isinstance(r, dict) and identifier(r.get("_id"))}),
                "distinct_name_values": len({r["name"] for r in raw_entries if isinstance(r, dict) and identifier(r.get("name"))}),
            }
        events = data.get("botEvents", {})
        if not isinstance(events, dict):
            gap(ledger, "unsupported_parse", [aid + "#" + prefix + "/botEvents"], [parent["id"]], "botEvents is not a supported event mapping.", "Inspect the supplied event format.")
            events = {}
        for name, config in events.items():
            pointer = prefix + "/botEvents/" + pointer_key(name)
            if not isinstance(config, dict):
                record_binding(parent, pointer, name, config, {"status": "unsupported_event_shape", "requested_owner": None, "target": None}, None, None)
                continue
            enabled = config.get("enabled") if isinstance(config.get("enabled"), bool) else None
            action = config.get("action")
            if enabled is False:
                resolution = {"status": "disabled", "requested_owner": config.get("linkedBotStreamId"), "target": config.get("task")}
            elif action == "triggerDialog":
                resolution = resolve(parent, groups, config.get("linkedBotStreamId"), config.get("task"))
            elif action in ("showMsg", "runScript"):
                resolution = {"status": "non_dialog_action", "requested_owner": config.get("linkedBotStreamId"), "target": config.get("task")}
            else:
                resolution = {"status": "unsupported_event_action", "requested_owner": config.get("linkedBotStreamId"), "target": config.get("task")}
            record_binding(parent, pointer, name, config, resolution, enabled, action)
        default = data.get("defaultDialogId")
        if default is not None and not isinstance(default, str):
            gap(ledger, "unsupported_parse", [aid + "#" + prefix + "/defaultDialogId"], [parent["id"]],
                "Default-dialog setting is not a string task identifier.", "Inspect the exported default-dialog representation.")
        if identifier(default):
            fallback = events.get("INTENT_UNIDENTIFIED", {})
            basis = []
            if isinstance(fallback, dict) and fallback.get("action") == "triggerDialog" and fallback.get("task") == default:
                resolution = resolve(parent, groups, fallback.get("linkedBotStreamId"), default, "matching_fallback_event")
                basis = [aid + "#" + prefix + "/botEvents/INTENT_UNIDENTIFIED"]
                # This is a setting cross-reference, never proof of runtime precedence.
                enabled = fallback.get("enabled") if isinstance(fallback.get("enabled"), bool) else None
                if enabled is False:
                    resolution["status"] = "fallback_activation_unverified"
            else:
                enabled = None
                resolution = resolve(parent, groups, None, default, "parent_local_default_lookup")
                if resolution["status"] != "matched_source":
                    resolution["status"] = "default_owner_unverified"
                if isinstance(fallback, dict) and fallback.get("enabled") is True and fallback.get("action") == "triggerDialog" and identifier(fallback.get("task")):
                    gap(ledger, "configuration_disagreement", [aid + "#" + prefix + "/defaultDialogId", aid + "#" + prefix + "/botEvents/INTENT_UNIDENTIFIED"], [parent["id"], "fallback"],
                        "defaultDialogId and the enabled unidentified-intent event name different task IDs; effective precedence is not inferred.", "Review both settings and any version-specific precedence before choosing a fallback implementation.")
            record_binding(parent, prefix + "/defaultDialogId", "defaultDialogId", {"defaultDialogId": default}, resolution, enabled, "default_setting", basis)
        if parent["is_universal"]:
            ledger["universal_discovery"][aid]["configured_events"] = len(events)
            ledger["universal_discovery"][aid]["default_settings"] = int(bool(identifier(default)))
