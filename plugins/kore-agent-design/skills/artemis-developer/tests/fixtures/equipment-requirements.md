# Synthetic equipment assistant requirements

A community workshop wants a web-chat assistant, with voice planned later, to find available equipment and reserve it for a member. Members can also ask questions about workshop policy.

- UC-001: search availability by item category and date; reuse details in the initial message. Offer available results and handle none available.
- UC-002: reserve a selected item for an authenticated member after showing item/date and receiving confirmation. Allow corrections and cancellation before submission. The backend enforces ownership and availability.
- UC-003: answer questions from approved workshop policy, identify missing evidence, and return to the main conversation for a booking request.
- Existing business services provide availability lookup and reservation submission/status. API contracts and target credentials will be supplied later. No custom execution service is requested.
- Prefer native ABL and API tools. Keep the experience concise, helpful and tolerant of interruptions. The interaction must not claim a successful booking when the backend refuses it or the result is unknown.
- First implementation slice is availability plus the shared routing/context foundation; reservation follows. Web rendering and future voice quality require their own tests.
- There is no existing approved agent architecture, target project or platform export.

This is a synthetic fixture, not a real deployment or API contract.
