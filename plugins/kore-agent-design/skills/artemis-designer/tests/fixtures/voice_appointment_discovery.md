# Synthetic discovery brief: employee repair appointments

This is a fictional evaluation fixture, not a customer record or product configuration.

## Agreed scope

- Wave 1 target: 30 working days. Foundation covers separate development, test, and production environments; identity integration; contact-center transfer; and operational monitoring.
- Wave 1 use case: an authenticated employee changes an existing laptop-repair appointment to an available slot. Booking a new appointment, cancelling a repair, and technician scheduling are excluded.
- The sponsor selected this use case based on value, likely implementation speed, and business readiness, but numeric priority scores were not supplied.
- Wave 1 voice is English for US employees. Spanish-language service is a later-wave candidate; the handling of a Spanish request during Wave 1 needs an owner decision.

## Callers and service rules

- Callers include employees who speak English with varied accents. Some call from noisy warehouse floors or shared spaces. Brand guidance is calm, direct, and helpful; no required synthetic voice or accent has been selected.
- Authenticate the employee before reading or changing appointment details. Never speak a full employee identifier or one-time code back to the caller. Identity and authentication policy details must be confirmed by the security owner.
- Retrieve the existing appointment, show only eligible available slots, confirm the selected change, and provide a reference the caller can safely retain. Eligibility rules and confirmation wording require business-owner review.
- If repeated understanding or authentication attempts fail, or no suitable slot exists, offer a human transfer. Transfer hours, queue, and context-sharing policy are not yet supplied.
- Slot search and confirmation may take several seconds. Required response-time targets, progress cues, and callback policy have not been agreed.
- A dropped call after a confirmed change must not create a duplicate appointment; the caller needs a safe way to learn whether the change completed.

## Available and missing evidence

- Available: this agreed-scope summary and the brand guidance above.
- Not yet supplied: actual call samples, listener research, telephony architecture, scheduling API contract, authentication policy detail, transfer policy, response-time objectives, and product-version evidence.
- No speech provider, channel adapter, voice, accent, speech rate, or endpointing threshold has been chosen. Recommend caller-visible behavior where possible; leave technical settings evidence-labelled.
