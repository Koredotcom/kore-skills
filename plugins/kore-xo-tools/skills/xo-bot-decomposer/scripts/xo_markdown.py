"""Readable static evidence from the same inventory used for JSON output."""
from __future__ import annotations

import html
import re
from urllib.parse import unquote

from xo_export_parser import _redact_text, _safe_filename, parse_condition
from xo_graph import walk


def prose(value):
    text = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|~-])", r"\\\1", text).replace("\n", " ")


def code(value, language="text"):
    text = str(value)
    fence = "`" * max(3, max((len(m[0]) + 1 for m in re.finditer(r"`+", text)), default=3))
    return [fence + language, text, fence, ""]


def inline(value):
    text = str(value)
    fence = "`" * max(1, max((len(m[0]) + 1 for m in re.finditer(r"`+", text)), default=1))
    return f"{fence} {text} {fence}"


def fields(value):
    """Expand exported fields without dropping unknown settings or empty containers."""
    lines = []
    for pointer, item in walk(value):
        if isinstance(item, (dict, list)) and item:
            continue
        label = pointer or "(root)"
        display = "null" if item is None else str(item).lower() if isinstance(item, bool) else str(item)
        if item == "":
            display = '""'
        key = pointer.rsplit("/", 1)[-1].lower()
        if isinstance(item, str) and key in ("script", "text", "preprocessor", "postprocessor", "retrycallback"):
            decoded = unquote(item)
            if decoded != item:
                label += " (URL-decoded)"
            display = _redact_text(decoded)
        if "\n" in display or len(display) > 140 or key in ("script", "preprocessor", "postprocessor", "retrycallback"):
            lines += [f"- **{prose(label)}:**", ""] + code(display)
        else:
            lines += [f"- **{prose(label)}:** {inline(display)}"]
    return lines + [""]


def transitions(occurrence, peers):
    raw = occurrence.get("transitions_raw", [])
    if not raw:
        return ["No transitions exported; terminal behavior is not established by this alone.", ""]
    if not isinstance(raw, list):
        return ["Unsupported transition shape; inspect the exported fields below.", ""] + fields(raw)
    lines = []
    for transition in raw:
        if not isinstance(transition, dict):
            lines += ["Unresolved transition:", ""] + fields(transition)
            continue
        condition = parse_condition(transition["if"]) if "if" in transition else "default" if "default" in transition else "unspecified condition"
        target = transition.get("then", transition.get("default"))
        candidates = [p for p in peers if p["node_id"] == target]
        local = [p for p in candidates if p["parent_chain"] == occurrence["parent_chain"]]
        candidates = local or candidates
        if target == "end":
            destination = "end (exported target)"
        elif len(candidates) == 1:
            destination = f"{candidates[0]['name']} [{target}]"
        else:
            destination = f"{target} (target unresolved or ambiguous)"
        lines += [f"- {prose(condition)} → {prose(destination)}", ""]
    # Preserve condition shape and transition settings not understood by the summary.
    return lines + ["Exported transition fields:", ""] + fields(raw)


def render_dialog(dialog, occurrences, definitions):
    lines = [f"# {prose(dialog['name'])}", "",
             f"Source ID: {prose(dialog['id'])}; source pointer: {prose(dialog['source_pointer'])}", "",
             f"Hidden: {dialog['is_hidden']}; follow-up: {dialog['is_follow_up']}; system-name hint: {dialog['ignored_system_intent']}", "",
             "Static evidence in export order. Every listed node is retained, including nodes without incoming transitions. "
             "Order and presence do not establish runtime reachability.", "",
             "## Invocation examples", ""]
    lines += fields({"sample_utterances": dialog["sample_utterances"], "sample_patterns": dialog["sample_patterns"]})
    for index, occurrence in enumerate(occurrences, 1):
        component = occurrence["component"]
        lines += [f"## Node {index}: {prose(occurrence['name'])} ({prose(occurrence['type'])})", ""]
        lines += fields({key: occurrence[key] for key in
                         ("node_id", "component_id", "source_pointer", "component_pointer", "occurrence_path", "parent_chain")})
        if not component:
            lines += ["Component definition missing or unresolved; inline node evidence is retained.", ""]
        lines += ["### Component configuration", ""] + fields(component)
        lines += ["### Node configuration", ""] + fields(occurrence["node"])
        lines += ["### Transitions", ""] + transitions(occurrence, occurrences)
    if not occurrences:
        lines += ["No dialog node occurrences expanded. Check the graph issues and unexpanded-node appendix.", ""]
    included = {o["component_pointer"] for o in occurrences if o["component_pointer"]}
    related = []
    # Follow exact-ID candidates only to display their definitions, never to create
    # executable node occurrences. A set bounds shared/cyclic composite references.
    while True:
        additions = [d for d in definitions if d["source_pointer"] not in included and any(
            ref["source_pointer"].startswith(pointer + "/")
            for ref in d["reference_candidates"] for pointer in included)]
        if not additions:
            break
        included.update(d["source_pointer"] for d in additions)
        related.extend(additions)
    if related:
        lines += ["## Referenced component definitions", "",
                  "Exact ID candidates from this dialog's components, including transitive references. "
                  "These definitions are evidence, not additional executable node occurrences; review composite membership and runtime use.", ""]
        for record in related:
            lines += [f"### {prose(record['definition'].get('name', record['component_id']))}", ""]
            lines += fields(record)
    lines += ["See [_components.md](_components.md) for every component definition, including definitions without dialog occurrences, "
              "and [_unexpanded_nodes.md](_unexpanded_nodes.md) for physical nodes whose dialog placement is unresolved. "
              "Exact structured evidence remains in [_inventory.json](_inventory.json).", ""]
    return "\n".join(lines)


def render_components(inventory):
    lines = ["# Component definitions", "",
             "All definitions are retained, including disconnected entities and composite members. "
             "No expanded dialog occurrence does not mean unused. Exact ID reference candidates preserve their source fields; "
             "they do not prove composite membership, execution order or runtime activation.", ""]
    for index, record in enumerate(inventory["component_definitions"], 1):
        component = record["definition"]
        lines += [f"## Component {index}: {prose(component.get('name', component.get('_id', 'Unnamed')))}", ""]
        lines += fields({key: record[key] for key in
                         ("component_id", "source_pointer", "placement", "occurrence_paths", "reference_candidates")})
        lines += ["### Exported definition", ""] + fields(component)
    if not inventory["component_definitions"]:
        lines += ["No component definitions exported.", ""]
    return "\n".join(lines)


def render_unexpanded(inventory):
    lines = ["# Unexpanded physical nodes and graph issues", "",
             "These physical nodes were discovered outside expanded dialog occurrences. Their bodies are preserved, "
             "but dialog placement and execution remain unresolved. Graph limits and unsupported shapes remain explicit gaps.", ""]
    for index, record in enumerate(inventory["unexpanded_nodes"], 1):
        lines += [f"## Physical node {index}: {prose(record['node'].get('nodeId', 'Unknown'))}", ""] + fields(record)
    if not inventory["unexpanded_nodes"]:
        lines += ["No unexpanded physical nodes discovered.", ""]
    lines += ["## Graph issues", ""] + fields(inventory["graph_issues"])
    return "\n".join(lines)


def write_dialog_markdown(inventory, output):
    index = ["# Expanded dialog index", "",
             "All dialogs and listed nodes retained, regardless of transition connectivity. Static evidence requires semantic review.", "",
             "| Dialog | ID | Evidence |", "|---|---|---|"]
    combined = []
    for number, dialog in enumerate(inventory["dialogs"], 1):
        filename = f"dialog_{number:04}_{_safe_filename(dialog['name'])}.md"
        occurrences = [o for o in inventory["node_occurrences"] if o["dialog_pointer"] == dialog["source_pointer"]]
        text = render_dialog(dialog, occurrences, inventory["component_definitions"])
        (output / filename).write_text(text, encoding="utf-8")
        combined.append(text)
        index.append(f"| {prose(dialog['name'])} | {prose(dialog['id'])} | [{filename}]({filename}) |")
    for filename, text in (("_components.md", render_components(inventory)),
                           ("_unexpanded_nodes.md", render_unexpanded(inventory))):
        (output / filename).write_text(text, encoding="utf-8")
        combined.append(text)
        index += ["", f"- [{filename}]({filename})"]
    index += ["", "- [_all_dialogs.md](_all_dialogs.md) — dialogs and both appendices",
              "- [_inventory.json](_inventory.json) — structured evidence", ""]
    (output / "_index.md").write_text("\n".join(index), encoding="utf-8")
    (output / "_all_dialogs.md").write_text("\n\n".join(combined), encoding="utf-8")
