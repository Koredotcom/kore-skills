# Equipment assistant — synthetic requirements

Review revision sample-v1 for web chat and voice. Users can check equipment availability and reserve an item after confirming the exact item, collection date and location. Reuse supplied details, allow corrections before confirmation, and cancel without creating a reservation. A change to confirmed details invalidates confirmation. Only claim success after a successful reservation result. An unavailable item should lead to an alternative choice.

Availability is read-only. Reservations use a mock inventory. This fixture permits offline analysis only; no live calls or writes. No identity, platform connection, actual audio, rendered chat or client-side timing is supplied. All IDs/data are synthetic. `project.txt` is a simplified control-flow export for source review, not executable platform ABL. `conversations.json` and `traces.json` record synthetic debug sessions for this exact revision.
