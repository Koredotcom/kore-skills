# Reference map and maintenance

Read at entry. This library translates public design principles into implementation decisions and evidence. The confirmed user/design scope governs the outcome; current verified platform constraints govern execution. Surface a conflict and propose an alternative instead of silently changing either. Heuristics are not platform capability claims.

| Before this work | Read |
|---|---|
| Intake or architecture confirmation | [Build and design intake](build-and-design-intake.md) |
| Scaffold, select next slice, delegate or resume | [Incremental build and delegation](incremental-build-and-delegation.md) |
| Target-specific discovery or writes | [Platform build contract](platform-build-contract.md) |
| Select responsibilities, execution mode or routing | [Agent architecture and ABL](agent-architecture-and-abl.md) |
| State, correction, cancellation or confirmation | [State and conversation control](state-and-conversation-control.md) |
| Tool types, contracts, transformations or API actions | [Tools and integrations](tools-and-integrations.md) |
| Identity, permissions or sensitive data | [Security and identity](security-and-identity.md) |
| Any user-facing path | [Shared experience](experience-implementation.md) |
| Voice/telephony | [Voice implementation](voice-implementation.md) |
| Web, mobile or asynchronous messaging | [Digital implementation](digital-implementation.md) |
| Architecture tradeoffs or latency changes | [Performance and observability](performance-and-observability.md) |
| Application, tests or repair | [Validation, delivery and repair](validation-delivery-and-repair.md) |

Load just the relevant category before acting and record material decisions/evidence in the run. A reference-read checklist is not proof of applied behavior. In a repair, include affected shared contracts and regression boundaries, not only the changed line.

## Sources and drift

Designer owns canonical design principles/formats; Developer owns their implementation applications and synthetic verification examples. The installed Developer references are self-contained. They do not require a separate Designer installation or source checkout to run.

[source-provenance.json](source-provenance.json) records public bundled Designer source paths, SHA-256 content hashes, adapted categories and review date. Paths are relative to the containing plugin root and used for maintenance only. No live project evidence is bundled. Hashes identify reviewed content even when a rename/release has not yet been committed.

Maintainers changing a listed source must review the mapped Developer references and tests in the same change. Update the hash only after reconciliation, recording substantive adaptations here or in the relevant reference. `tests/test_reference_provenance.py` detects stale sources; it does not certify semantic alignment. Shared/voice/digital adaptations preserve the principles while replacing design-document templates with implementation and acceptance checks. Architecture, integrations, security and operations adaptations retain boundaries and traceability without duplicating Designer's workflow.

Platform guidance is obtained at execution through the user's available public toolkit/documentation. The embedded project-build playbook was inspected on 2026-10-09; it is a discovery starting point, not current target-runtime evidence. Re-verify mutable syntax, models, channel support and semantics during a build. Keep retrieved runtime evidence in the user's build workspace, not in this skill's references.
