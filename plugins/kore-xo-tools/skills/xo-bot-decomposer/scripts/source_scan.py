"""Bounded, dependency-free JavaScript lexical evidence, NOT an AST or data-flow proof.

Comments and string contents are excluded from executable-name matching. Templates,
computed calls, imports and registration guards require semantic source review.
"""
from __future__ import annotations

import re

TOKEN = re.compile(r"(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|(?P<string>'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`)|(?P<word>[A-Za-z_$][\w$]*)|(?P<number>\d+(?:\.\d+)?)|(?P<op>===|!==|=>|==|!=|&&|\|\||\?\.|\+=|-=|\+\+|--|[^\s])")
BUILTINS = set("if for while switch catch function return typeof delete void new super Number String Boolean Object Array JSON Math Date RegExp Error Promise Set Map parseInt parseFloat isNaN encodeURIComponent decodeURIComponent setTimeout clearTimeout require callback cb console context env koreUtil BotKit sdk process module exports Buffer fetch".split())


def tokens(text):
    return [{"v": m.group(), "kind": m.lastgroup, "start": m.start(), "end": m.end(), "line": text.count("\n", 0, m.start()) + 1}
            for m in TOKEN.finditer(text) if m.lastgroup != "comment"]


def paired(ts):
    stack, pairs = [], {}
    for i, t in enumerate(ts):
        v = t["v"]
        if t["kind"] == "string":
            continue
        if v in ("(", "[", "{"):
            stack.append((v, i))
        elif v in (")", "]", "}") and stack:
            if stack[-1][0] == {")": "(", "]": "[", "}": "{"}[v]:
                _, start = stack.pop()
                pairs[start] = i
                pairs[i] = start
    return pairs


def scan(text, source):
    ts = tokens(text)
    vs = [t["v"] for t in ts]
    pairs = paired(ts)
    functions, definition_parens = [], set()
    for i, t in enumerate(ts):
        name, paren, body = None, None, None
        if t["v"] == "function":
            if i + 2 < len(ts) and ts[i + 1]["kind"] == "word" and vs[i + 2] == "(":
                name, paren = vs[i + 1], i + 2
            elif i + 1 < len(ts) and vs[i + 1] == "(":
                paren = i + 1
                if i >= 2 and vs[i - 1] in ("=", ":"):
                    name = vs[i - 2].strip("'\"")
                else:
                    name = f"anonymous@{t['line']}:{t['start']}"
            if paren in pairs:
                body = pairs[paren] + 1
        elif t["v"] == "=>":
            prev = i - 1
            paren = pairs.get(prev) if prev >= 0 and vs[prev] == ")" else prev
            if paren is not None:
                before = paren - 1
                name = vs[before - 1].strip("'\"") if before >= 1 and vs[before] in ("=", ":") else f"arrow@{t['line']}:{t['start']}"
                body = i + 1
        elif t["kind"] in ("word", "string") and i + 1 < len(ts) and vs[i + 1] == "(" and i > 0 and vs[i - 1] in ("{", ","):
            p = i + 1
            if p in pairs and pairs[p] + 1 < len(ts) and vs[pairs[p] + 1] == "{":
                name, paren, body = t["v"].strip("'\""), p, pairs[p] + 1
        if name is None or body is None or body >= len(ts):
            continue
        if vs[body] == "{" and body in pairs:
            end = pairs[body]
        else:
            end = body
            while end + 1 < len(ts) and vs[end + 1] not in (";", "\n"):
                end += 1
        definition_parens.add(paren)
        start = ts[paren]["start"] if paren is not None else t["start"]
        functions.append({"name": name, "source": source, "line": t["line"], "start": t["start"], "end": ts[end]["end"],
                          "signature": text[start:ts[body]["start"]], "code": text[t["start"]:ts[end]["end"]],
                          "body": text[ts[body]["start"]:ts[end]["end"]], "confidence": "lexical_candidate",
                          "activation": "not_established", "callers": [], "callees": []})
    calls = []
    for i, t in enumerate(ts[:-1]):
        if t["kind"] != "word" or vs[i + 1] != "(" or i + 1 in definition_parens or t["v"] in ("function", "if", "for", "while", "switch", "catch"):
            continue
        start = i
        while start >= 2 and vs[start - 1] in (".", "?.") and ts[start - 2]["kind"] == "word":
            start -= 2
        name = "".join(vs[start:i + 1])
        end = pairs.get(i + 1, i + 1)
        owners = [f for f in functions if f["start"] <= t["start"] < f["end"]]
        owner = min(owners, key=lambda f: f["end"] - f["start"]) if owners else None
        category = "known_or_external" if name.split(".")[0] in BUILTINS or name.startswith("env.") else "custom_candidate"
        calls.append({"name": name, "source": source, "line": t["line"], "owner": owner["name"] if owner else None,
                      "arguments": text[ts[i + 1]["end"]:ts[end]["start"]], "category": category, "resolution": "unresolved"})
        if owner:
            owner["callees"].append(name)
    hooks = []
    for i, t in enumerate(ts[:-2]):
        event = t["v"].strip("'\"")
        if not event.startswith("on_") or vs[i + 1] not in (":", "("):
            continue
        handler = vs[i + 2]
        inline = next((f for f in functions if f["start"] == ts[i + 2]["start"] or f["name"] == event), None)
        if inline:
            handler = inline["name"]
        hooks.append({"event": event, "handler": handler, "source": source, "line": t["line"], "offset": t["start"], "registration": "unresolved", "deployment": "unverified"})
    registrations = []
    for call in calls:
        if call["name"].split(".")[-1] in ("registerBot", "register", "init"):
            args = call["arguments"]
            match = re.search(r"\bbotId\s*:\s*['\"]([^'\"]+)", args)
            registrations.append({**call, "bot_id": match.group(1) if match else None, "confidence": "lexical_candidate"})
            for hook in hooks:
                if re.search(r"\b" + re.escape(hook["event"]) + r"\b", args):
                    hook["registration"] = "registration_candidate"
                    hook["bot_id"] = match.group(1) if match else None
    states, env = [], []
    # Use tokens, not source regex, so comments/string examples do not become writes.
    for i, t in enumerate(ts):
        if t["v"] not in ("context", "env") or t["kind"] != "word":
            continue
        j, parts, dynamic = i + 1, [t["v"]], False
        while j < len(ts):
            if vs[j] in (".", "?.") and j + 1 < len(ts) and ts[j + 1]["kind"] == "word":
                parts.append(vs[j + 1]); j += 2
            elif vs[j] == "[" and j in pairs:
                end = pairs[j]
                if end == j + 2 and ts[j + 1]["kind"] == "string":
                    parts.append(vs[j + 1][1:-1])
                else:
                    parts.append("[dynamic]"); dynamic = True
                j = end + 1
            else:
                break
        if len(parts) < 2:
            continue
        record = {"field": ".".join(parts), "source": source, "line": t["line"], "dynamic": dynamic, "confidence": "lexical_candidate"}
        if parts[0] == "env":
            env.append(record)
        else:
            record["access"] = "write_or_replace" if j < len(ts) and vs[j] == "=" else "read_write" if j < len(ts) and vs[j] in ("+=", "-=", "++", "--") else "read"
            record["reset_and_lifetime"] = "requires_control_flow_review"
            states.append(record)
    templates = re.findall(r"\{\{\s*env\.([\w.-]+)", text)
    env.extend({"field": "env." + ref, "source": source, "line": None, "confidence": "template_reference"} for ref in templates)
    imports = [c for c in calls if c["name"] == "require"]
    return {"functions": functions, "calls": calls, "hooks": hooks, "registrations": registrations, "states": states,
            "environment": env, "imports": imports,
            "limits": ["Lexical candidates only; regex literals, template interpolation, computed dispatch, aliases, imports, guards and reachability require source review."]}
