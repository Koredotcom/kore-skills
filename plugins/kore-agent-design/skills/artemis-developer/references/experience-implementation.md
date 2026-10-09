# Shared experience implementation

Read for any user-facing build. Adapted from Designer's shared experience principles; source hashes and maintenance mapping are in [source-provenance.json](source-provenance.json).

## Turn confirmed experience into behavior

Map each relevant EXP/AC or equivalent requirement to its journey, source component, channel dependency and observable test. Keep the functional use case authoritative for business behavior; implement channel presentation without duplicating or changing that logic. If a recommendation remains proposed, do not present it as a confirmed requirement.

| Practice | Build treatment | Verification |
|---|---|---|
| Start from the user's goal | Preserve intent and supplied facts through routing and tool use | Complete and partial first-turn requests |
| Keep interaction efficient | Ask for material missing/ambiguous facts; offer focused choices or progressive detail | Count repeated questions and user effort through completion |
| Adapt tone to the situation | Use appropriate wording for clarification, frustration, bad news and completion | Review representative turns, not just a greeting |
| Make recovery usable | Explain what happened, retained state and the available next step | Failed tool, misunderstanding and failed transfer |
| Report truthful outcomes | Ground completion in current business-result evidence | Business refusal inside an otherwise successful HTTP response |
| Preserve context | Pass needed facts to the next agent or human without over-sharing | Handoff, return, correction and subsequent task |

Avoid generic empathy preambles, repeated acknowledgements, unnecessary confirmations and filler that merely makes a timing metric look better. Concise output still needs the information required to understand and act on the result. Do not pressure users into faster answers or hide uncertainty.

Read [voice-implementation.md](voice-implementation.md) or [digital-implementation.md](digital-implementation.md) for the applicable channel. Validate critical success, failure and recovery paths against the confirmed design. Record limitations where actual audio, rendering, accessibility or delivery cannot be exercised. A fluent debug transcript is only evidence for the observed text interaction.
