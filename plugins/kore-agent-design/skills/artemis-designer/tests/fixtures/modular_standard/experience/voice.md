<!-- kore-agent-design:voice-experience:v2 -->
# Voice Experience: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-003 |
| Document type | Voice Experience |
| Version | 0.1 |
| Status | In Review |
| Owner | Experience Design |
| Wave | Wave 1 |
| Canonical owner for | EXP-001 and AC-002 |
| Source evidence | Voice discovery |
| Last updated | 2026-09-21 |

## Voice Scope and Telephony Context

Voice supports [UC-001](../use-cases/UC-001-equipment-request.md) in English.

## Persona, Speaking Style, and Prompt Shape

Prompts use short sentences and avoid reading identifiers.

## Turn-Taking and Conversation Control

| ID | Situation | Expected behavior | Timing or limit | Applicable use cases |
|---|---|---|---|---|
| EXP-001 | Interruption | Stop playback and process the caller turn | Immediate | UC-001 |

## Recognition and Understanding

Two failed recognition attempts offer transfer.

## Confirmation and Sensitive Values

The agent confirms the requested item without speaking employee identifiers.

## Latency and Long-Running Actions

The call confirms submission; approval completes asynchronously.

## Transfer and Human Handoff

Repeated failure transfers with context.

## Errors, Degradation, and Recovery

Disconnect after submission does not cancel the durable request.

## Accessibility, Locale, and Compliance Constraints

Speakable English content and keypad fallback are required.

## Voice Acceptance Criteria

| ID | Scenario | Given | When | Then | Measurement or evidence |
|---|---|---|---|---|---|
| AC-002 | Caller interrupts | Playback is active | Caller speaks | Playback stops and the turn is processed | Voice test |

## Open Questions

No blocking voice question remains.
