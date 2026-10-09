#!/usr/bin/env python3
"""
XO Bot Export Parser (XO 10-and-earlier & XO 11)
--------------------------------
Parses a Kore.ai XO 10 or XO 11 bot definition JSON and writes one markdown file
per intent/dialog (plus a combined file and an index). The output is the same
human-readable dialog tree format the analyst uses to reason over flows.

This is an implementation module. Run `scripts/decompose_bot.py` as the stable
skill entry point instead of invoking this file directly.

Notes:
- Targets the standard Kore.ai single-file export shape with top-level keys:
  dialogs, dialogComponents, sentences, patterns. Both XO 10 (environment
  version 9.x) and XO 11 use this shape — the extractor handles both.
- For exports that nest the bot under a wrapper key (botDefinition,
  appDefinition, app, bot), the extractor unwraps automatically.
- The stable entry point preserves all system/support dialogs and recursive evidence.
- Sub-dialog invocations (an `intent` node whose component points to a
  different dialog via dialogId) are surfaced explicitly so they can be
  inlined into the parent flow during analysis.
"""

import argparse
import os
import re
import sys
import json
import urllib.parse
from collections import Counter
from xo_graph import discover_graph
from urllib.parse import unquote
from typing import Dict, Any, List, Tuple


REDACTED = "[REDACTED]"
SENSITIVE_FIELD_RE = re.compile(
    r"(?i)(?:^|[^a-z0-9])(?:authorization|proxy-authorization|api[-_ ]?key|"
    r"x-api-key|access[-_ ]?token|client[-_ ]?secret|token|secret|password|"
    r"cookie|set-cookie)(?:$|[^a-z0-9])"
)
SENSITIVE_JSON_VALUE_RE = re.compile(
    r'''(?ix)
    (?P<prefix>["'](?:authorization|proxy-authorization|api[-_ ]?key|x-api-key|
        access[-_ ]?token|client[-_ ]?secret|token|secret|password|cookie|set-cookie)
        ["']\s*:\s*["'])
    (?P<value>[^"']*)
    (?P<suffix>["'])
    '''
)
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r'''(?ix)
    (?P<prefix>\b(?:authorization|api[-_ ]?key|x-api-key|access[-_ ]?token|
        client[-_ ]?secret|token|secret|password|cookie)\b\s*=\s*["'])
    (?P<value>[^"']*)
    (?P<suffix>["'])
    '''
)
SENSITIVE_QUERY_RE = re.compile(
    r"(?i)([?&](?:api[-_]?key|access[-_]?token|client[-_]?secret|token|secret|password)=)([^&#\s]+)"
)
AUTH_SCHEME_RE = re.compile(r"(?i)\b(Bearer|Basic)\s+([^\s,;\"']+)")


def _is_portable_reference(value: object) -> bool:
    """Return true for unresolved configuration references rather than values."""
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(
        r"(?i)(?:(?:Bearer|Basic)\s+)?(?:\{\{[^{}]+\}\}|\$\{[^{}]+\})",
        value.strip(),
    ))


def _redact_text(value: object) -> str:
    """Redact common credential assignments while preserving variable references."""
    text = urllib.parse.unquote(str(value)) if value is not None else ""

    def replace_value(match: re.Match[str]) -> str:
        raw = match.group("value")
        if _is_portable_reference(raw):
            return match.group(0)
        return f"{match.group('prefix')}{REDACTED}{match.group('suffix')}"

    text = re.sub(
        r"(?i)(?P<prefix>\b(?:apiKey|accessToken|clientSecret|password|secret|token|authorization)\b\s*:\s*[\"'`])(?P<value>[^\"'`]*)(?P<suffix>[\"'`])",
        replace_value, text,
    )
    text = re.sub(
        r"(?i)(?P<prefix>\b(?:apiKey|accessToken|clientSecret|password|secret|token|authorization)\b\s*=\s*`)(?P<value>[^`]*)(?P<suffix>`)",
        replace_value, text,
    )
    text = re.sub(r"(?i)(https?://)[^/\s:@]+:[^/\s@]+@", r"\1[REDACTED]@", text)
    text = SENSITIVE_JSON_VALUE_RE.sub(replace_value, text)
    text = SENSITIVE_ASSIGNMENT_RE.sub(replace_value, text)
    text = SENSITIVE_QUERY_RE.sub(
        lambda match: match.group(0)
        if _is_portable_reference(match.group(2))
        else f"{match.group(1)}{REDACTED}",
        text,
    )
    text = AUTH_SCHEME_RE.sub(
        lambda match: match.group(0)
        if _is_portable_reference(match.group(2))
        else f"{match.group(1)} {REDACTED}",
        text,
    )
    return text


def _redact_structure(value: Any, field_name: str = "") -> Any:
    """Recursively redact values associated with credential-like field names."""
    if field_name and SENSITIVE_FIELD_RE.search(field_name):
        if _is_portable_reference(value):
            return value
        return REDACTED
    if isinstance(value, dict):
        # Exported variables often use {name/key, value}, even with isSecured=false.
        secret_name = value.get("name", value.get("key", ""))
        if isinstance(secret_name, str) and SENSITIVE_FIELD_RE.search(secret_name):
            value = {key: (REDACTED if key in ("value", "defaultValue", "default") and not _is_portable_reference(item) else item) for key, item in value.items()}
        return {key: _redact_structure(item, str(key)) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_structure(item) for item in value]
    if isinstance(value, str):
        return _redact_text(value)
    return value


# Configuration for intents to ignore during processing
IGNORED_INTENTS = {
    "welcome task",
    "fallback task",
    "follow up task",
    "multiintent",
    "answer generation",
    "answergeneration",
    "custom feedback survey",
    "default agenttransfer",
    "defaultagenttransfer",
    "deflectionprocess",
    "interaction intents",
    "interactionintents",
    "satwaitforuserinput",
    "onconnect",
    "on connect",
}


def extract_sample_utterances_and_patterns(
    dialog_task: Dict[str, Any],
    component_details: Dict[str, Any],
    all_sentences: List[Dict],
    all_patterns: List[Dict],
    max_samples: int = 10,
    default_bot_lang: str = "en",
) -> Tuple[List[str], List[str]]:
    """Extract sample utterances and patterns for a given dialog/intent."""
    task_id = dialog_task.get("_id")

    # Find the component for this dialog
    component_id = None
    component_ref_id = None
    for comp_id, component in component_details.items():
        comp_type = component.get("type")
        comp_dialog_id = component.get("dialogId")
        if (comp_type == "intent" or comp_type == "dialog") and comp_dialog_id == task_id:
            component_id = comp_id
            component_ref_id = component.get("refId")
            break

    # Sentences keyed by component_id
    sentences_set = set()
    if all_sentences and component_id:
        for sentence_obj in all_sentences:
            if (
                sentence_obj.get("taskId") == component_id
                and sentence_obj.get("sentence")
                and sentence_obj.get("language") == default_bot_lang
            ):
                sentences_set.add(sentence_obj["sentence"])

    # Patterns keyed by refId
    patterns_set = set()
    if all_patterns and component_ref_id:
        for pattern_obj in all_patterns:
            if pattern_obj.get("taskType") in ("dialog", "intent"):
                if pattern_obj.get("refId") == component_ref_id:
                    entries = (
                        pattern_obj.get("localeData", {})
                        .get(default_bot_lang, {})
                        .get("patterns", [])
                    )
                    for entry in entries:
                        val = entry.get("value")
                        if val:
                            patterns_set.add(val)

    # Stable ordering makes repeated runs byte-for-byte comparable. Sampling here
    # used to be random, which needlessly changed the evidence supplied to Codex.
    sampled_sentences = sorted(sentences_set, key=str.casefold)[:max_samples]
    sampled_patterns = sorted(patterns_set, key=str.casefold)[:max_samples]
    return sampled_sentences, sampled_patterns


def get_message_text(component):
    """Extracts message text from a component, handling different structures."""
    message_text = "N/A"
    if component.get("message") and isinstance(component["message"], list) and component["message"]:
        msg_container = component["message"][0]
        if msg_container.get("localeData", {}).get("en", {}):
            msg_content = msg_container["localeData"]["en"]
            if "text" in msg_content:
                text_value = msg_content["text"]
                try:
                    decoded_text = unquote(text_value)
                except Exception:
                    decoded_text = text_value

                if msg_content.get("type") in ("uxmap", "js"):
                    message_text = f"JavaScript: {decoded_text}"
                elif msg_content.get("type") == "basic":
                    message_text = f"Text: {decoded_text}"
                else:
                    message_text = f"{msg_content.get('type', 'UnknownType')}: {decoded_text}"
            elif msg_content.get("type") == "EXTERNAL_MESSAGE_REFERENCE":
                message_text = f"External Message: {msg_content.get('refId', 'N/A')}"
    return message_text


def extract_entity_allowed_values(component):
    """Extract allowed values for list_of_values entities."""
    try:
        locale_data = component.get("localeData", {}).get("en", {})
        return locale_data.get("allowedValues", {}).get("values", [])
    except Exception:
        return []


def extract_web_channel_messages(component):
    """Extract web channel specific messages for entities."""
    try:
        web_channel_info = ""
        for message in component.get("message", []):
            channel = message.get("channel", "default")
            if channel != "default":
                locale_text = message.get("localeData", {}).get("en", {}).get("text", "")
                if locale_text:
                    try:
                        decoded_text = unquote(locale_text)
                    except Exception:
                        decoded_text = locale_text
                    web_channel_info += f", {channel.upper()} Channel: {decoded_text}"
        return web_channel_info
    except Exception:
        return ""


def get_node_metadata(node_in_flow, component, component_details=None, current_dialog_id=None, dialog_id_to_name=None):
    """Extracts metadata based on node type.

    Extra args (used for XO 10/11 sub-dialog detection):
      component_details   — full component map (for resolving sub-dialog targets)
      current_dialog_id   — the dialog this node lives in (so we can tell whether
                            an 'intent' node is the entry intent vs a sub-dialog call)
      dialog_id_to_name   — map of dialog _id -> human-readable name
    """
    node_type = node_in_flow.get("type")
    metadata_str = "N/A"

    # --- Sub-dialog invocation ---------------------------------------------
    # In XO 10/11, calling another dialog appears as an 'intent' node whose
    # component is of type 'intent' (or 'dialog') with a `dialogId` pointing
    # to the called dialog. The dialog's own entry intent also looks like
    # this but its component.dialogId == current dialog _id, so we exclude it.
    if node_type == "intent":
        linked_dialog_id = component.get("dialogId")
        if (
            linked_dialog_id
            and current_dialog_id
            and linked_dialog_id != current_dialog_id
        ):
            linked_name = (
                (dialog_id_to_name or {}).get(linked_dialog_id, linked_dialog_id)
            )
            return (
                f"Sub-dialog invocation -> {linked_name} "
                f"(inline this dialog's steps at this point during analysis)"
            )
        # Otherwise, it's the entry intent of the current dialog — no extra metadata.
        return "Entry intent for this dialog"

    if node_type == "script":
        script_content = component.get("script", "N/A")
        try:
            metadata_str = f"Script: {_redact_text(unquote(script_content))}"
        except Exception:
            metadata_str = f"Script: {_redact_text(script_content)}"

    elif node_type in ("message", "dialogAct"):
        metadata_str = get_message_text(component)

    elif node_type == "entity":
        entity_type = component.get("entityType", "N/A")
        prompt_msg = get_message_text(component)
        error_msg_list = []
        if (
            component.get("errorMessage")
            and isinstance(component["errorMessage"], list)
            and component["errorMessage"]
        ):
            err_container = component["errorMessage"][0]
            if err_container.get("localeData", {}).get("en", {}):
                err_content = err_container["localeData"]["en"]
                if "text" in err_content:
                    err_text = err_content.get("text", "N/A")
                    try:
                        err_text = unquote(err_text)
                    except Exception:
                        pass
                    error_msg_list.append(f"Error Prompt: {err_text}")
        error_prompts = "; ".join(error_msg_list) if error_msg_list else "N/A"

        allowed_values_info = ""
        if entity_type == "list_of_values":
            allowed = extract_entity_allowed_values(component)
            if allowed:
                vals = [f"{v.get('title', v.get('value', 'N/A'))}" for v in allowed]
                allowed_values_info = f", Allowed Values: [{', '.join(vals)}]"

        web_channel_info = extract_web_channel_messages(component)

        metadata_str = (
            f"Entity Type: {entity_type}, Prompt: {prompt_msg}, {error_prompts}"
            f"{allowed_values_info}{web_channel_info}"
        )
        metadata_str += "\n" + "Implicit Output Context: context.entities." + component.get("name", "N/A")

    elif node_type == "service":
        service_node_type = component.get("serviceNodeType", "N/A")
        ep = component.get("endPoint", {})
        endpoint_str = _redact_text(
            f"{ep.get('method', 'GET').upper()} "
            f"{ep.get('protocol', 'https')}://{ep.get('host', '')}{ep.get('path', '')}"
        )
        auth_required = component.get("authRequired", False)
        idp = component.get("idp", "none")
        auth_str = f"Required: {auth_required} (IDP: {idp})"
        headers_raw = component.get("headers", {}).get("value", "{}")
        try:
            headers_data = _redact_structure(json.loads(headers_raw))
            headers_str = ", ".join(f"{k}: {v}" for k, v in headers_data.items())
        except Exception:
            headers_str = _redact_text(headers_raw)
        payload_raw = component.get("payload", {}).get("value", "")
        payload_body = _redact_text(payload_raw)
        pre_processor = _redact_text(component.get("preProcessor", "None"))
        post_processor = _redact_text(component.get("postProcessor", "None"))

        metadata_str = (
            f"Node Type: {service_node_type}\n"
            f"Endpoint: {endpoint_str}\n"
            f"Auth: {auth_str}\n"
            f"Headers: {headers_str}\n"
            f"Payload: {payload_body}\n"
            f"Pre-Processor: {pre_processor}\n"
            f"Post-Processor: {post_processor}"
        )

    elif node_type in ("generativeai", "searchai"):
        gen_ai_config = component.get("generativeAI", {})
        prompt = gen_ai_config.get("prompt", "N/A")
        try:
            prompt = _redact_text(unquote(prompt))
        except Exception:
            prompt = _redact_text(prompt)
        settings = gen_ai_config.get("settings", {})
        if node_type == "searchai":
            search_config = gen_ai_config.get("searchConfig", {})
            metadata_str = (
                f"SearchAI - Query Type: {search_config.get('type')}, "
                f"Query: {search_config.get('query', 'N/A')}, Prompt: {prompt}"
            )
        else:
            metadata_str = (
                f"GenerativeAI - Prompt: {prompt}, "
                f"Model: {settings.get('displayName', settings.get('model', 'N/A'))}"
            )

    elif node_type == "dynamicIntent":
        metadata_str = f"Dynamic Intent Path: {component.get('intentPath', 'N/A')}"
    elif node_type == "botAction":
        # XO 10/11 BotAction: a named action that wraps backend logic (often an
        # API call sequence). The component itself usually just carries a name +
        # description; the actual steps may live in a linked flow elsewhere.
        action_name = component.get("name", "N/A")
        action_desc = (
            component.get("localeData", {}).get("en", {}).get("desc", "")
        ).strip() or "N/A"
        metadata_str = f"Bot Action: {action_name}\nDescription: {action_desc}"
    elif node_type == "agentTransfer":
        metadata_str = "Agent Transfer Node"
    elif node_type == "logic":
        metadata_str = "Logic Node (rules define behavior)"

    return metadata_str


def parse_condition(condition_obj):
    """Render known boolean structure without inventing absent operators."""
    if isinstance(condition_obj, list):
        return "[unspecified conjunction: " + "; ".join(parse_condition(c) for c in condition_obj) + "]"
    if not isinstance(condition_obj, dict) or not condition_obj:
        return "Unresolved condition: " + json.dumps(condition_obj, sort_keys=True)
    if "tests" in condition_obj:
        op = str(condition_obj.get("conjoin", "UNRESOLVED CONJUNCTION")).upper()
        if op not in ("AND", "OR"):
            op = "UNRESOLVED CONJUNCTION " + op
        return "(" + (" " + op + " ").join(parse_condition(c) for c in condition_obj["tests"]) + ")"
    field = condition_obj.get("context", condition_obj.get("field", condition_obj.get("dialogAct", condition_obj.get("intent"))))
    op = condition_obj.get("op")
    if field is None or op is None:
        return "Unresolved condition: " + json.dumps(condition_obj, sort_keys=True)
    if op == "exists":
        return f"{field} exists"
    return f"{field} { {'eq': '=='}.get(op, op) } {condition_obj.get('value', '[value not supplied]')}"


def parse_transitions(transitions, node_id_to_name_map):
    if not transitions:
        return ["End of dialog"]
    result = []
    for transition in transitions:
        if not isinstance(transition, dict):
            result.append("Unresolved transition: " + json.dumps(transition))
            continue
        target = transition.get("then", transition.get("default"))
        condition = parse_condition(transition["if"]) if "if" in transition else "default" if "default" in transition else "unresolved"
        name = "End of dialog" if target == "end" else node_id_to_name_map.get(target, target)
        result.append(f"{condition} -> {name or 'DestinationUnclear'} [{target}]")
    return result


def parse_kore_ai_dialog_flow(app_def_data: Dict[str, Any]) -> str:
    """Parses the XO 11 JSON and returns the dialog flow as a single string."""
    output_lines = []
    default_bot_lang = app_def_data.get("defaultLanguage", "en")
    component_details = {comp["_id"]: comp for comp in app_def_data.get("dialogComponents", [])}
    dialog_tasks = app_def_data.get("dialogs", [])
    all_sentences = app_def_data.get("sentences", [])
    all_patterns = app_def_data.get("patterns", [])

    # Map dialog _id -> human-readable name; used to resolve sub-dialog invocations.
    dialog_id_to_name = {
        dlg.get("_id"): dlg.get("localeData", {}).get("en", {}).get("name", "Unnamed Dialog Task")
        for dlg in dialog_tasks
    }

    if not dialog_tasks:
        return "No dialogs found in the app definition."

    for dialog_task in dialog_tasks:
        dialog_name = (
            dialog_task.get("localeData", {}).get("en", {}).get("name", "Unnamed Dialog Task")
        )
        dialog_id = dialog_task.get("_id")
        is_follow_up = dialog_task.get("isFollowUp", False)
        is_hidden = dialog_task.get("isHidden", False)

        header = f"\nINTENT: {dialog_name} (ID: {dialog_id})"
        if is_follow_up:
            header += " [SUB-INTENT]"
        if is_hidden:
            header += " [HIDDEN - NOT USER INVOKABLE]"
        output_lines.append(header)

        sampled_sentences, sampled_patterns = extract_sample_utterances_and_patterns(
            dialog_task,
            component_details,
            all_sentences,
            all_patterns,
            max_samples=10,
            default_bot_lang=default_bot_lang,
        )
        output_lines.append(f"  Sample Utterances to invoke this intent: {sampled_sentences}")
        output_lines.append(f"  Sample patterns to invoke this intent: {sampled_patterns}")

        nodes_in_dialog = dialog_task.get("nodes", [])
        if not nodes_in_dialog:
            output_lines.append("  No nodes in this dialog.")
            continue

        # Build node_id -> name map for readable transitions
        node_id_to_name_map = {}
        for n in nodes_in_dialog:
            cid = n.get("componentId")
            if cid and cid in component_details:
                node_id_to_name_map[n["nodeId"]] = component_details[cid].get("name", "UnnamedNode")
            else:
                node_id_to_name_map[n["nodeId"]] = f"UnknownComponent ({cid})"

        for node_in_flow in nodes_in_dialog:
            component_id = node_in_flow.get("componentId")
            node_id_str = node_in_flow.get("nodeId", "UnknownNodeId")

            if not component_id or component_id not in component_details:
                output_lines.append(
                    f"  Node: Type UNKNOWN (Component ID {component_id} not found or missing)"
                )
                output_lines.append(f"    Node ID in flow: {node_id_str}")
                continue

            actual_component = component_details[component_id]
            node_type_in_flow = node_in_flow.get("type", "N/A")
            node_name = actual_component.get("name", "N/A")
            display_name = node_name
            if node_name == "N/A" or node_name.lower() == node_type_in_flow.lower():
                display_name = node_type_in_flow

            output_lines.append(
                f"    Node: {node_type_in_flow.capitalize()} ({display_name}) "
                f"[ID: {node_id_str}, CompID: {component_id}]"
            )

            description = actual_component.get("localeData", {}).get("en", {}).get("desc", "N/A")
            if not description or description.strip() == "":
                description = "N/A"
            output_lines.append(f"      Description: {description}")

            metadata = get_node_metadata(
                node_in_flow,
                actual_component,
                component_details=component_details,
                current_dialog_id=dialog_id,
                dialog_id_to_name=dialog_id_to_name,
            )
            output_lines.append(f"      Metadata: {metadata}")

            transitions = node_in_flow.get("transitions", [])
            for t_str in parse_transitions(transitions, node_id_to_name_map):
                output_lines.append(f"      Transition: {t_str}")
            output_lines.append("-" * 20)

    return "\n".join(output_lines)


def extract_intents_from_flow_analysis(flow_analysis_text: str) -> Dict[str, str]:
    """Split the combined flow text into a dict of {intent_name: intent_text}."""
    intent_pattern = r"INTENT: ([^\(]+) \(ID: ([^\)]+)\)(.*?)(?=\n\nINTENT: |$)"
    matches = re.findall(intent_pattern, flow_analysis_text, re.DOTALL)

    intents_dict = {}
    for match in matches:
        intent_name = match[0].strip()
        if intent_name.lower() in IGNORED_INTENTS:
            print(f"Skipping ignored intent: {intent_name}", file=sys.stderr)
            continue
        intent_id = match[1].strip()
        intent_content = match[2].strip()
        intents_dict[intent_name] = f"INTENT: {intent_name} (ID: {intent_id})\n{intent_content}"
    return intents_dict


def write_metadata_file(data: Dict[str, Any], output_dir: str) -> None:
    """Write _metadata.md with languages, channels, PII config, and digital forms."""
    lines = ["# Bot Metadata\n"]

    # Languages
    lines.append("## Languages")
    lines.append(f"- **Default:** {data.get('defaultLanguage', 'N/A')}")
    supported = data.get("supportedLanguages", [])
    if supported:
        lines.append(f"- **Supported:** {', '.join(supported)}")
    lc = data.get("languageConfigurations", {})
    enabled_langs = [k for k, v in lc.items() if isinstance(v, dict) and v.get("enabled")]
    if enabled_langs:
        lines.append(f"- **Enabled configurations:** {', '.join(enabled_langs)}")
    lines.append("")

    # Channels
    lines.append("## Channels")
    channels = data.get("channels", [])
    if channels:
        for c in channels:
            lines.append(
                f"- {c.get('type', 'unknown')} — {c.get('displayName', '')} | enabled: {c.get('enable', 'N/A')}"
            )
    else:
        lines.append("- No channel configuration found in export.")
    lines.append("")

    # PII Redaction
    lines.append("## PII Redaction")
    pii = (
        data.get("piiRedaction")
        or data.get("piiData")
        or data.get("piiSettings")
        or data.get("botSettings", {}).get("piiRedaction")
    )
    for key in ("piiRedaction", "piiData", "piiSettings"):
        if key in data:
            pii = data[key]
            break
    if pii is not None:
        lines.append("- **Global:** Exported configuration; effective deployment state is unverified.")
        lines.append(f"```json\n{json.dumps(pii, indent=2)}\n```")
    else:
        lines.append("- No global PII configuration found in this export; deployed behavior is unverified.")
    lines.append("- **Local overrides:** Inspect relevant entity/intent configuration before claiming coverage.")
    lines.append("")

    # Digital Forms — scan components for form-type nodes
    lines.append("## Digital Forms")
    components = data.get("dialogComponents", [])
    form_nodes = [
        c for c in components
        if c.get("type") == "digitalFormNode"
        or "form" in c.get("type", "").lower()
        or c.get("formId")
    ]
    if form_nodes:
        for fn in form_nodes:
            form_id = fn.get("formId", fn.get("_id", "N/A"))
            name = fn.get("name", "unnamed")
            lines.append(f"- **{name}** (formId: {form_id})")
    else:
        lines.append("- No digital forms found.")
    lines.append("")

    out_path = os.path.join(output_dir, "_metadata.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Metadata: {out_path}")


def _decoded(value: Any) -> str:
    """Return URL-decoded text without guessing at its meaning."""
    if value is None:
        return ""
    return urllib.parse.unquote(str(value))


def _environment_references(value: Any) -> List[str]:
    text = urllib.parse.unquote(json.dumps(value, ensure_ascii=False))
    refs = re.findall(r"\benv\.([A-Za-z0-9_.-]+)", text)
    refs += re.findall(r"\benv\[\s*['\"]([^'\"]+)['\"]\s*\]", text.replace('\\"', '"'))
    return sorted({"env." + r for r in refs}, key=str.casefold)


def _component_dialog_map(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    result = {}
    for o in discover_graph(data)["node_occurrences"]:
        if o["component_id"]:
            result.setdefault(o["component_id"], []).append({
                "dialog_id": o["dialog_id"], "dialog_name": o["dialog_name"], "node_id": o["node_id"],
                "node_type": o["type"], "source_pointer": o["source_pointer"], "occurrence_path": o["occurrence_path"],
                "parent_chain": o["parent_chain"],
            })
    return result


def build_inventory(data: Dict[str, Any], source_name: str, version_route: str) -> Dict[str, Any]:
    """Build deterministic evidence used by both business and technical analysis.

    This deliberately records facts, not inferred business purpose. Goal boundaries,
    names, and descriptions remain reasoning tasks for the analyst.
    """
    components = data.get("dialogComponents", [])
    component_by_id = {component.get("_id"): component for component in components}
    component_usage = _component_dialog_map(data)
    graph = discover_graph(data)
    dialog_name_by_id = {
        dialog.get("_id"): dialog.get("localeData", {}).get("en", {}).get("name", "Unnamed Dialog Task")
        for dialog in data.get("dialogs", [])
    }
    default_language = data.get("defaultLanguage", "en")
    sentences = data.get("sentences", [])
    patterns = data.get("patterns", [])

    dialogs: List[Dict[str, Any]] = []
    subdialog_calls: List[Dict[str, Any]] = []
    for dialog in data.get("dialogs", []):
        name = dialog_name_by_id.get(dialog.get("_id"), "Unnamed Dialog Task")
        node_name_by_id = {
            node.get("nodeId"): component_by_id.get(node.get("componentId"), {}).get(
                "name", node.get("type", "unnamed")
            )
            for node in dialog.get("nodes", [])
        }
        utterances, dialog_patterns = extract_sample_utterances_and_patterns(
            dialog,
            component_by_id,
            sentences,
            patterns,
            max_samples=10,
            default_bot_lang=default_language,
        )
        nodes: List[Dict[str, Any]] = []
        for occurrence in [o for o in graph["node_occurrences"] if o["dialog_id"] == dialog.get("_id")]:
            node = occurrence["node"]
            component = component_by_id.get(node.get("componentId"), {})
            linked_dialog_id = component.get("dialogId") if node.get("type") == "intent" else None
            linked_dialog_name = None
            if linked_dialog_id and linked_dialog_id != dialog.get("_id"):
                linked_dialog_name = dialog_name_by_id.get(linked_dialog_id, linked_dialog_id)
                subdialog_calls.append(
                    {
                        "caller_dialog": name,
                        "caller_dialog_id": dialog.get("_id"),
                        "node_name": component.get("name", node.get("type", "unnamed")),
                        "called_dialog": linked_dialog_name,
                        "called_dialog_id": linked_dialog_id,
                    }
                )
            nodes.append(
                {
                    "source_pointer": occurrence["source_pointer"],
                    "occurrence_path": occurrence["occurrence_path"],
                    "parent_chain": occurrence["parent_chain"],
                    "transitions_raw": node.get("transitions", []),
                    "node_id": node.get("nodeId"),
                    "component_id": node.get("componentId"),
                    "type": node.get("type", "unknown"),
                    "name": component.get("name", node.get("type", "unnamed")),
                    "description": component.get("localeData", {}).get("en", {}).get("desc", ""),
                    "called_dialog": linked_dialog_name,
                    "transitions": parse_transitions(node.get("transitions", []), node_name_by_id),
                }
            )
        dialogs.append(
            {
                "id": dialog.get("_id"),
                "name": name,
                "ignored_system_intent": name.casefold() in IGNORED_INTENTS,
                "is_hidden": bool(dialog.get("isHidden", False)),
                "is_follow_up": bool(dialog.get("isFollowUp", False)),
                "sample_utterances": utterances,
                "sample_patterns": dialog_patterns,
                "node_count": len(nodes),
                "node_type_counts": dict(sorted(Counter(node["type"] for node in nodes).items())),
                "nodes": nodes,
            }
        )

    services: List[Dict[str, Any]] = []
    entities: List[Dict[str, Any]] = []
    scripts: List[Dict[str, Any]] = []
    forms: List[Dict[str, Any]] = []
    for component in components:
        component_type = component.get("type", "unknown")
        base = {
            "component_id": component.get("_id"),
            "name": component.get("name", "unnamed"),
            "used_in": component_usage.get(component.get("_id"), []),
            "environment_references": _environment_references(component),
        }
        if component_type == "service":
            endpoint = component.get("endPoint", {})
            protocol = _decoded(endpoint.get("protocol", "")).strip() or "https"
            host = _decoded(endpoint.get("host", ""))
            path = _decoded(endpoint.get("path", ""))
            headers = component.get("headers", {}).get("value", "")
            try:
                headers = _redact_structure(json.loads(headers)) if headers else {}
            except (TypeError, json.JSONDecodeError):
                headers = _redact_text(headers)
            services.append(
                {
                    **base,
                    "service_node_type": component.get("serviceNodeType"),
                    "method": str(endpoint.get("method", "GET")).upper(),
                    "url": _redact_text(f"{protocol}://{host}{path}"),
                    "authentication": {
                        "required": component.get("authRequired"),
                        "idp": component.get("idp", "not_exported"),
                    },
                    "headers": headers,
                    "request_body": _redact_text(component.get("payload", {}).get("value", "")),
                    "pre_processor": _redact_text(component.get("preProcessor", "")),
                    "post_processor": _redact_text(component.get("postProcessor", "")),
                }
            )
        elif component_type == "entity":
            entities.append(
                {
                    **base,
                    "entity_type": component.get("entityType"),
                    "allowed_values": extract_entity_allowed_values(component),
                    "prompt": get_message_text(component),
                    "error_prompts": [
                        get_message_text({"message": [message]})
                        for message in component.get("errorMessage", [])
                    ],
                }
            )
        elif component_type == "script":
            scripts.append({**base, "code": _redact_text(component.get("script", ""))})
        elif component_type == "digitalFormNode" or "form" in component_type.casefold() or component.get("formId"):
            forms.append(
                {
                    **base,
                    "type": component_type,
                    "form_id": component.get("formId", component.get("_id")),
                    "definition": component,
                }
            )

    channels = [
        {
            "type": channel.get("type", "unknown"),
            "display_name": channel.get("displayName", ""),
            "enabled": channel.get("enable"),
        }
        for channel in data.get("channels", [])
    ]
    pii = (
        data.get("piiRedaction")
        or data.get("piiData")
        or data.get("piiSettings")
        or data.get("botSettings", {}).get("piiRedaction")
    )
    analysis_dialogs = [dialog for dialog in dialogs if not dialog["ignored_system_intent"]]
    candidate_user_goals = [
        dialog
        for dialog in analysis_dialogs
        if not dialog["is_hidden"] and not dialog["is_follow_up"]
    ]
    return {
        "schema_version": 2,
        "discovery": graph["discovery"],
        "node_occurrences": graph["node_occurrences"],
        "graph_issues": graph["graph_issues"],
        "source": source_name,
        "version_route": version_route,
        "summary": {
            "dialogs_total": len(dialogs),
            "dialogs_after_system_filter": len(analysis_dialogs),
            "candidate_user_goal_dialogs": len(candidate_user_goals),
            "system_events": sum(dialog["ignored_system_intent"] for dialog in dialogs),
            "nodes_total": sum(dialog["node_count"] for dialog in dialogs),
            "services": len(services),
            "entities": len(entities),
            "scripts": len(scripts),
            "forms": len(forms),
            "subdialog_calls": len(subdialog_calls),
        },
        "languages": {
            "default": default_language,
            "supported": data.get("supportedLanguages", []),
        },
        "channels": channels,
        "pii_redaction": pii,
        "environment_references": _environment_references(data),
        "dialogs": dialogs,
        "subdialog_calls": subdialog_calls,
        "services": services,
        "entities": entities,
        "scripts": scripts,
        "forms": forms,
    }


def write_inventory_files(inventory: Dict[str, Any], output_dir: str) -> None:
    """Write structured evidence and a compact survey; semantic coverage is separate."""
    json_path = os.path.join(output_dir, "_inventory.json")
    with open(json_path, "w", encoding="utf-8") as stream:
        json.dump(inventory, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")

    summary = inventory["summary"]
    lines = [
        "# Deterministic Bot Inventory",
        "",
        f"- **Source:** `{inventory['source']}`",
        f"- **Version route:** {inventory['version_route']}",
        f"- **Dialogs:** {summary['dialogs_total']} total; {summary['dialogs_after_system_filter']} after system filtering; {summary['candidate_user_goal_dialogs']} non-hidden/non-follow-up candidates",
        f"- **Nodes:** {summary['nodes_total']}",
        f"- **Technical components:** {summary['services']} services; {summary['entities']} entities; {summary['scripts']} scripts; {summary['forms']} forms",
        f"- **Sub-dialog calls:** {summary['subdialog_calls']}",
        "",
        "## Dialog Coverage",
        "",
        "| Dialog | Classification | Nodes | Node types |",
        "|---|---|---:|---|",
    ]
    for dialog in inventory["dialogs"]:
        labels = []
        if dialog["ignored_system_intent"]:
            labels.append("system event")
        if dialog["is_hidden"]:
            labels.append("hidden")
        if dialog["is_follow_up"]:
            labels.append("sub-intent")
        classification = ", ".join(labels) or "requires semantic classification"
        node_types = ", ".join(
            f"{node_type}: {count}" for node_type, count in dialog["node_type_counts"].items()
        ) or "none"
        lines.append(f"| {dialog['name']} | {classification} | {dialog['node_count']} | {node_types} |")

    lines.extend(["", "## Sub-dialog Calls", ""])
    if inventory["subdialog_calls"]:
        lines.extend(["| Caller | Node | Called dialog |", "|---|---|---|"])
        for call in inventory["subdialog_calls"]:
            lines.append(f"| {call['caller_dialog']} | {call['node_name']} | {call['called_dialog']} |")
    else:
        lines.append("- No sub-dialog calls found.")

    lines.extend(["", "## Technical Evidence", ""])
    for label, key in (("Services", "services"), ("Entities", "entities"), ("Scripts", "scripts"), ("Forms", "forms")):
        names = [item["name"] for item in inventory[key]]
        lines.append(f"- **{label} ({len(names)}):** {', '.join(names) if names else 'None'}")
    env_refs = inventory["environment_references"]
    lines.append(f"- **Environment references ({len(env_refs)}):** {', '.join(env_refs) if env_refs else 'None'}")
    lines.extend(
        [
            "",
            "Use `_inventory.json` for exact service, entity, script, form, transition, and dialog records.",
            "Business goal boundaries and purpose descriptions are intentionally not inferred here.",
        ]
    )
    markdown_path = os.path.join(output_dir, "_inventory.md")
    with open(markdown_path, "w", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
        stream.write("\n")
    print(f"Inventory: {markdown_path}")
    print(f"Structured inventory: {json_path}")


def _safe_filename(name: str, max_len: int = 80) -> str:
    """Filesystem-safe filename derived from intent name."""
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_")
    return safe[:max_len] or "unnamed_intent"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("definition", help="Central botDefinition.json or appDefinition.json")
    parser.add_argument("output", nargs="?", default="xo_extracted")
    parser.add_argument("--version-route", default="XO 10 or earlier")
    args = parser.parse_args()

    input_path = args.definition
    output_dir = args.output

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Some XO exports nest the app definition under a top-level key.
    # Detect by looking for the keys we actually need.
    if "dialogs" not in data:
        for candidate_key in ("botDefinition", "appDefinition", "app", "bot"):
            if candidate_key in data and isinstance(data[candidate_key], dict):
                inner = data[candidate_key]
                if "dialogs" in inner:
                    data = inner
                    break

    if "dialogs" not in data:
        print(
            "ERROR: Unsupported export shape: the selected central JSON has no 'dialogs' array. "
            "Provide a complete single-definition XO export or extend the bundled parser; do not "
            "replace it with a one-off analysis script.",
            file=sys.stderr,
        )
        sys.exit(2)

    os.makedirs(output_dir, exist_ok=True)

    write_metadata_file(data, output_dir)
    inventory = build_inventory(data, os.path.basename(input_path), args.version_route)
    write_inventory_files(inventory, output_dir)

    full_text = parse_kore_ai_dialog_flow(data)
    combined_path = os.path.join(output_dir, "_all_dialogs.md")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    intents = extract_intents_from_flow_analysis(full_text)

    index_lines = [
        "# Extracted Intent Index",
        "",
        f"Source: `{os.path.basename(input_path)}`",
        f"Intents extracted (after filtering system intents): **{len(intents)}**",
        "",
        "| # | Intent | File |",
        "|---|--------|------|",
    ]

    for i, (intent_name, intent_text) in enumerate(intents.items(), start=1):
        fname = f"{_safe_filename(intent_name)}.md"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            f.write(intent_text)
        index_lines.append(f"| {i} | {intent_name} | `{fname}` |")

    with open(os.path.join(output_dir, "_index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

    print(f"Extracted {len(intents)} intents to {output_dir}")
    print(f"Index: {output_dir}/_index.md")
    print(f"Combined: {combined_path}")


if __name__ == "__main__":
    main()
