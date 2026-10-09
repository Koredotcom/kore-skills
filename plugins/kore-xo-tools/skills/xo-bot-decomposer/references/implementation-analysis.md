# Implementation dependency analysis

Read when the source has executable code, SDK hooks, event behavior or routes. The Python scanner deliberately has no JavaScript runtime dependency. Its token-based lexical records exclude comments and ordinary strings from declaration/call scans, but are **not an AST, import graph, reachability proof or alias-aware data-flow analysis**. Regex literals, template interpolation, dynamic properties, module indirection and registrations outside supported literal shapes require manual inspection. Use an already available trusted syntax parser if useful; do not install or execute the supplied application's dependencies.

## Registration before handler matching

Start at package/entrypoint configuration and the actual bootstrap. Trace imports into project registration, selected bot IDs, event map, callback implementation and guards. Distinguish SDK capabilities, unregistered samples, dead/commented paths and imported-but-uncalled code from active project behavior. Custom routes and infrastructure stay inventoried; decide relevance against the requested capability slice.

For every hook, inspect trigger/envelope, ordering, switches, text/NLP effects, context reads/writes, services, injected routes, callback/forward completion and failure/interruption. An `on_agent_transfer` callback that only forwards is pass-through; investigate scripts/channel markup for the real handoff. Global message or end-dialog hooks may affect every child even without child webhook nodes.

Resolve webhooks against **actual dispatch**:

- Generic callback: if the component-name argument is unused and bot/event registration is established, multiple SDK components may resolve to one handler. Record one implementation and all use sites.
- Exact names/IDs: preserve exact comparisons, casing and owner. Case-insensitive, suffix/pattern and registry matching require source evidence; do not infer them from similar names.
- Dynamic selection: record predicate/input/state, candidate results, null behavior and missing runtime values. Keep unresolved when no source-backed match exists.

Record `handler_status=matched_static` only after inspecting and linking registration and dispatcher evidence. Close the corresponding missing-source/review gap with evidence/history. Keep backend schemas, timeout/continuation semantics and effective registration separate. Disabled/unknown bot registration does not become an active match.

## Helpers, state and events

Inspect function declarations, expressions, arrows, object/module exports and inline code. Match calls within the owning bot/module scope; distinguish built-ins/platform APIs, imported external functions, missing custom helpers and computed calls. Availability in another child is not scope-compatible execution. Follow reachable helpers, annotate uncalled definitions and link shared implementation once to all callers.

Inspect event configuration and target IDs before interpreting name hints. Preserve support implementations even if hidden or without utterances. Locate initializers across all selected sources; a located producer closes only the source question, not startup binding/order.

Build focused state contracts with producer, consumers, initial/reset value, trigger, replacement versus merge, failure flags, persistence and schema. Follow aliases, brackets and dynamic cache keys manually where lexical evidence is incomplete. Preserve exact key case and namespace. Review failure → retry → success, stale flags, full-object replacement and terminal suppression. Label a suspected mismatch as a lead unless source control flow establishes it.

## Cross-source and provider contracts

Compare exported configuration, companion config, mounted/deployment overrides and runtime evidence without inferring effective values. Direct `env.NAME`, bracket and templated references all matter; missing local definitions may be provided by deployment. Product versions, parser routes and BotKit release names are separate identities; differing numbering alone is not incompatibility.

For each route, identify actual target predicate, destination owner and entry/return state. Finding a missing task in another child resolves source availability only; wrong owner or mismatched saved-question/child fields remain independent gaps. Narrow dependency inspection does not authorize that child's full domain.

For every service/hook, list observed request/response consumer fields versus supplied provider schemas/fixtures. Compare node timeout, client budgets and serial sequencing only with established units. Preserve unknown units (a raw `4` is not automatically four seconds). Document success, empty/malformed response, timeout, ineligible, failure/retry/success, cancellation and callback continuation from evidence or mark open. Client code cannot establish backend policy, external model prompts/tools or telephony contracts.

## Ledger decisions

The generated ledger is an evidence baseline. Add semantic facts and new gap records with stable IDs and evidence; retain original identities/pointers. For a resolved record, add `resolution_evidence`, append a dated `resolution_history` entry, and set status to `resolved`. Deferred records stay visible. Mark review items `analyzed`, `evidence_only`, `excluded_by_scope`, `external_unavailable`, `unresolved` or `unsupported`, with a specific reason. Analyzed items need delivered `document_refs`; exclusions need `scope_decision`. Do not blanket-resolve every lexical review gap merely because source files exist.
