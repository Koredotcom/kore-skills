# Digital channel implementation

Read with [experience-implementation.md](experience-implementation.md) for web chat, mobile, messaging or asynchronous channels. Group channels only when their interaction and capability constraints materially match.

- Map confirmed formatting, cards, forms, attachments, citations and navigation requirements to supported payloads and renderer behavior. Always define an appropriate text or alternate fallback for unavailable rich features.
- Keep messages scannable, show the next meaningful action and reveal detail progressively. Avoid long internal implementation explanations in the end-user flow.
- Reuse session facts appropriately across corrections and handoffs. Define inactivity, restart, cross-device and resume behavior from actual identity/state support, not from a UI assumption.
- For asynchronous delivery, handle ordering, duplicates, delayed work and notification failure explicitly. An email or delayed message is not a live chat turn.
- Apply masking, shared-device and reauthentication requirements. Verify links/attachments and accessibility with the real channel where available, without claiming a compliance audit from a transcript.
- Pass the permitted context to human/agent handoffs and make failure/retry behavior visible. Never say an attachment or notification was delivered from a configuration-only check.

**Verify:** success in the intended renderer, narrow/mobile layout where relevant, unsupported rich content, reconnect/duplicate input, delayed response ordering, privacy and unavailable transfer. Keep semantic response correctness separate from delivery/rendering acceptance.

**Example:** offer selectable search results when the channel supports them, with numbered plain-text alternatives otherwise. Preserve the same item identifiers and confirmation behavior in both paths; formatting must not change the business contract.
