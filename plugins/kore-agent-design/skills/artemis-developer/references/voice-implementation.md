# Voice implementation

Read with [experience-implementation.md](experience-implementation.md) for voice, IVR or telephony. Adapt Designer's voice decisions into actual behavior and channel tests; do not assume that prompt wording configures the speech pipeline.

| Area | Implement and check |
|---|---|
| Listener and persona | Choose/retain the confirmed voice and accent for intelligibility and brand fit. Audition representative phrases with intended listeners; leave untested choices provisional. |
| Content | Use concise speakable chunks and clear choices. Verbalize dates, times, currency, names, acronyms and identifiers deliberately. Do not speak Markdown, raw URLs or long tables. Offer another channel when appropriate and supported. |
| Pacing | Adjust rate and pauses to information density and consequences. Support repeat/slower/help where feasible. Never impose a universal words-per-minute setting or rush an identifier to lower latency. |
| Recognition | Implement supported no-input/no-match, ambiguity, digit/spelling capture and recognition repair. Test noise, accent variation and hesitant speech; do not invent confidence fields. |
| Turn control | Verify barge-in, interruption recovery, pauses, cancellation and disconnect/resume behavior. Distinguish a thoughtful pause from a completed turn. |
| Consequential data | Confirm appropriately, mask sensitive values and avoid unnecessary repeated read-back. Corrections invalidate consent to changed consequential values. |
| Delay and transfer | Use proportionate progress/hold cues for real delays, with timeout recovery. Define what the caller hears when transfer is unavailable or fails and what context travels. |
| Language and access | Preserve confirmed locale/language choices and accessibility alternatives; verify actual switching and channel capabilities. |

Keep provider, adapter, synthesis, endpointing and interruption settings in technical configuration with current evidence. Do not inherit a demo voice, provider or threshold as a production default. Confirm whether the architecture uses realtime speech or an STT → model → TTS pipeline before interpreting telemetry.

Listen to rendered audio for pronunciation, rhythm, emphasis, number/data comprehension and comfortable pacing. Maintain an owned pronunciation list when needed. Trace voice acceptance to the corresponding use case and EXP/AC IDs. A compiler, prompt review or text debug run cannot establish audible quality, telephony behavior or end-of-speech-to-audio latency.

**Example:** a booking result may show a reference in chat but speak a concise confirmation and offer a supported delivery method. Confirm that the delivery actually occurs before saying it was sent.
