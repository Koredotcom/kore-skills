"""Source-preserving graph discovery. No application code is executed."""
from __future__ import annotations

from collections import Counter

KNOWN_TYPES = {"intent", "entity", "service", "script", "message", "botaction",
               "digitalformnode", "form", "sdkwebhook", "webhook", "agenttransfer",
               "logic", "confirmation", "dialog", "end"}


def walk(value, pointer=""):
    """Yield every JSON value with its original RFC 6901 pointer."""
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, pointer + "/" + str(key).replace("~", "~0").replace("/", "~1"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{pointer}/{index}")


def unwrap(data):
    if not isinstance(data, dict):
        return None, ""
    if isinstance(data.get("dialogs"), list):
        return data, ""
    for key in ("botDefinition", "appDefinition", "app", "bot"):
        inner = data.get(key)
        if isinstance(inner, dict) and isinstance(inner.get("dialogs"), list):
            return inner, "/" + key
    return None, ""


def discover_graph(data, prefix=""):
    components = data.get("dialogComponents", [])
    lookup = {}
    issues = []
    for i, component in enumerate(components):
        cid = component.get("_id")
        if str(component.get("type", "unknown")).lower() not in KNOWN_TYPES:
            issues.append({"kind": "unsupported_component_type", "pointer": f"{prefix}/dialogComponents/{i}", "component_id": cid, "type": component.get("type")})
        if cid in lookup:
            issues.append({"kind": "duplicate_component_id", "pointer": f"{prefix}/dialogComponents/{i}", "component_id": cid})
        else:
            lookup[cid] = (component, f"{prefix}/dialogComponents/{i}")
    occurrences = []
    limit = 50000

    def visit(nodes, pointer, dialog, parents=(), active=(), expansion=""):
        if len(parents) > 80 or len(occurrences) >= limit:
            issues.append({"kind": "expansion_limit", "pointer": pointer, "dialog_id": dialog.get("_id")})
            return
        for i, node in enumerate(nodes):
            if len(occurrences) >= limit:
                issues.append({"kind": "expansion_limit", "pointer": pointer, "dialog_id": dialog.get("_id")})
                break
            loc = f"{pointer}/{i}"
            if not isinstance(node, dict):
                issues.append({"kind": "unsupported_node_shape", "pointer": loc})
                continue
            cid = node.get("componentId")
            component, cptr = lookup.get(cid, ({}, ""))
            ntype = node.get("type", component.get("type", "unknown"))
            path = f"{expansion}/{i}"
            occurrence = {"dialog_id": dialog.get("_id"), "dialog_name": dialog.get("localeData", {}).get("en", {}).get("name", dialog.get("name", "Unnamed")),
                          "node_id": node.get("nodeId"), "component_id": cid, "type": ntype,
                          "name": component.get("name", node.get("name", ntype)), "parent_chain": list(parents),
                          "source_pointer": loc, "component_pointer": cptr,
                          "occurrence_path": path, "transitions_raw": node.get("transitions", []),
                          "node": node, "component": component, "disposition": "evidence_only", "reason": "Semantic review pending"}
            occurrences.append(occurrence)
            if str(ntype).lower() not in KNOWN_TYPES:
                issues.append({"kind": "unsupported_node_type", "pointer": loc, "type": ntype, "dialog_id": dialog.get("_id")})
            if not cid or not component:
                # Inline action wrappers still preserve missing/null references explicitly.
                issues.append({"kind": "unresolved_component", "pointer": loc, "component_id": cid, "dialog_id": dialog.get("_id")})
            chain = parents + (node.get("nodeId") or loc,)
            if isinstance(node.get("nodes"), list):
                visit(node["nodes"], loc + "/nodes", dialog, chain, active, path + "/inline")
            # Referenced component children can be direct or nested in an action container.
            for child_ptr, child in walk(component, cptr):
                if child_ptr.endswith("/nodes") and isinstance(child, list):
                    # Descendants of these children are handled by visit, once.
                    if "/nodes/" in child_ptr[len(cptr):]:
                        continue
                    if cid in active:
                        issues.append({"kind": "component_cycle", "pointer": child_ptr, "dialog_id": dialog.get("_id"), "component_id": cid})
                    else:
                        visit(child, child_ptr, dialog, chain, active + (cid,), path + "/component")

    for i, dialog in enumerate(data.get("dialogs", [])):
        visit(dialog.get("nodes", []), f"{prefix}/dialogs/{i}/nodes", dialog, expansion=f"/dialogs/{i}")
    # Independent physical discovery catches node arrays our expansion did not reach.
    physical = [(p, v) for p, v in walk(data, prefix) if isinstance(v, dict) and "nodeId" in v]
    reached = {o["source_pointer"] for o in occurrences}
    for pointer, node in physical:
        if pointer not in reached:
            issues.append({"kind": "unexpanded_node", "pointer": pointer, "node_id": node.get("nodeId")})
    return {"node_occurrences": occurrences, "graph_issues": issues,
            "discovery": {"physical_nodes": len(physical), "outer_nodes": sum(len(d.get("nodes", [])) for d in data.get("dialogs", [])),
                          "expanded_occurrences": len(occurrences), "component_definitions": len(components),
                          "node_types": dict(sorted(Counter(str(v.get("type", "unknown")) for _, v in physical).items()))}}
