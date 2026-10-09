# Voice experience guide

Read this reference with [experience-design-guide.md](experience-design-guide.md) when voice, IVR, or telephony is in scope. Create `experience/voice.md` and keep it focused on caller-visible behavior that differs from text or asynchronous channels. Apply the shared customer-review summary, critical journeys, decision records, and coverage review before the voice-specific sections below.

## Required structure

```markdown
<!-- kore-agent-design:voice-experience:v2 -->
# Voice Experience: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Experience Summary

<Use the shared experience guide. Show the recommended caller experience, decisions to confirm, and evidence status.>

## Critical Journeys

<Show material Wave 1 success and recovery journeys using the shared experience guide.>

## Voice Scope and Telephony Context

<Applicable use cases and waves, inbound/outbound direction, entry points, channel dependencies, authentication context, target listener groups, languages, locales, call environments, operating hours, and exclusions.>

## Voice Selection and Speaking Style

<Recommended voice character and accent, target-listener rationale, proposed speech rate and pause pattern by content type, tone, vocabulary, disclosure, pronunciation needs, and representative-listener validation. Separate confirmed brand constraints from assumptions.>

## Spoken Content and Data Verbalization

<Rules for concise spoken chunks, lists, complex explanations, names, acronyms, dates, times, currency, identifiers, numbers, ambiguous characters, and content better sent through another channel. Include pronunciation ownership.>

## Turn-Taking and Conversation Control

| EXP reference | Situation | Expected behavior | Timing or limit | Applicable use cases |
|---|---|---|---|---|
| EXP-### | <opening, listening, interruption, pause, repair, closing> | <behavior> | <threshold or TBD> | UC-### |

## Recognition and Understanding

<ASR assumptions, confidence handling, no-input/no-match behavior, accent/noise considerations, spelling and digit capture, language detection, and fallback.>

## Confirmation and Sensitive Values

<What requires implicit or explicit confirmation; normalization and read-back for dates, times, currency, identifiers, and numbers; masking and rules against speaking sensitive values.>

## Latency and Long-Running Actions

<Response-time targets, progress cues, silence prevention, hold behavior, asynchronous completion, callback or notification, and timeout recovery.>

## Transfer and Human Handoff

<Transfer triggers, destination, hours and availability, queue behavior, context package, warm/cold transfer, failure handling, and what the caller hears.>

## Errors, Degradation, and Recovery

<Telephony failure, recognition failure, backend delay, repeated misunderstanding, disconnect, reconnect or callback, and safe termination.>

## Accessibility, Locale, and Compliance Constraints

<Supported accessibility needs, locale-specific phrasing and formats, recording or consent requirements supplied by the user, and retention or disclosure constraints.>

## Voice Acceptance Criteria

| ID | Scenario | Given | When | Then | Measurement or evidence |
|---|---|---|---|---|---|

## Experience Decisions

<Use the shared experience guide to define EXP decisions with rationale, evidence and confirmation status.>

## Experience Coverage

<Show functional, technical, and test coverage for critical journeys and EXP decisions without duplicating the use-case SOP.>

## Open Questions

| ID | Question | Affected use cases | Owner or evidence needed | Blocking? |
|---|---|---|---|---|
```

## Category rules

- Choose a voice and accent for intelligibility with target listeners, appropriate persona, and brand fit—not a stereotyped or universal “best” accent. Audition candidates using representative phrases and listeners; record results or mark the choice provisional until tested.
- Adapt tone across greeting, clarification, frustration, sensitive outcomes, escalation, and closure. Show situational understanding without generic empathy preambles or reassurance the agent cannot substantiate.
- Set speaking rate and pauses by task stakes and information density. Slow down around unfamiliar choices, consequential details, and identifiers; allow repeat, slower delivery, help, or another channel where feasible. Do not impose a universal words-per-minute value.
- Listen to rendered audio for pronunciation, emphasis, rhythm, and comprehension. A written prompt review alone does not validate speech quality. Maintain a pronunciation list for names, brands, acronyms, and domain terms, with an owner.
- Specify no-input, no-match, barge-in, interruption recovery, and disconnect behavior; happy-path prompts alone are insufficient.
- Design prompts for listening: one main idea at a time, concise chunks, clear choices, and progressive disclosure. Do not read tables, markup, long identifiers, or raw URLs aloud; choose a speakable rendering or another channel.
- Define confirmation proportional to consequence. Avoid repeatedly speaking sensitive values.
- Distinguish a thoughtful pause from end-of-turn silence. Design recognition repair for noise, accent variation, hesitant or slow speakers, and ambiguity; make help or human transfer available where the service requires it.
- State latency and silence thresholds only when confirmed or technically validated. When unknown, mark them `TBD` and define the experience during delay.
- Treat language switching, local number/date formats, and accessibility as caller-experience choices; verify actual channel support before promising them.
- Trace each `EXP-###` and voice `AC-###` to applicable `UC-###` identifiers.
- Keep pipeline, provider, channel adapter, synthesis settings, endpointing, and other implementation controls in technical documents. Do not import a demo provider, adapter, voice preset, or numeric setting as a production default.

These are design heuristics, not fixed product settings or compliance guarantees. See [Google's voice-persona audition guidance](https://developers.google.com/assistant/conversation-design/create-a-persona) and [W3C WAI's supplemental voice-menu accessibility pattern](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o6p04-voice-menus/) for useful review lenses; test the actual proposed service with its intended callers.
