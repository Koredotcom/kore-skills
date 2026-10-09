# Validation, application and repair

Read before project application, runtime tests or remediation. Preserve the baseline and exact design/source versions for every claim.

## Verify a bounded increment

1. Inspect the source/configuration diff and requirement mapping. Check identifiers, references, tool contracts, state ownership, incomplete routes and sensitive values. Use the platform compiler/package validators available for this artifact. Local structure checks are advisory.
2. Follow [platform-build-contract.md](platform-build-contract.md): prefer guarded resource edits for a normal edit; validate and preview a whole package when import is appropriate. Compare the current target with the baseline, reconcile drift and verify uncertain prior outcomes before any repeat write.
3. Apply only authorized changes, preserving unrelated resources. Read back exact source/configuration and relevant operation status. A transport acknowledgement is not proof of effective runtime behavior.
4. Exercise the use case's positive outcome, material correction/cancel, refusal and failure recovery. Verify actual tool side effects/status, not only conversational claims. Recheck affected already-working paths when shared state, routing, prompt or tool contracts changed.
5. Save a checkpoint with inputs, diff, actual results, limits and next action. Classify unavailable/unrun checks clearly and continue the next ready authorized slice.

Before runtime work, state a bounded plan with scenario IDs, permitted identities/records and effects, maximum conversations/turns and elapsed test allowance. Reuse an existing plan/budget; when none exists, propose suitable bounds with the concrete architecture/test scope before execution. Count setup attempts, retries and all workers against the shared allowance. Stop at the first applicable limit, report partial coverage, and do not auto-reset it. Prior authorization for these bounded tests carries forward without another approval round.

## Evidence that supports the result

Record `requirement/scenario → source snapshot/component → session/turn → trace/tool result → outcome → finding/next action`. Preserve Pass, Fail, Blocked and Not tested as distinct outcomes. Include negative guards and passing controls; a workaround does not erase a failed normal path. Debug text does not certify voice or rendered web behavior. Compare useful latency and experience using [performance guidance](performance-and-observability.md).

The snapshot helper inventories regular files and reports content changes. Run it against a stable exported folder; put its JSON output elsewhere. It neither preserves a backup by itself nor guarantees a transactionally consistent live snapshot. Keep the actual baseline files and use platform concurrency guards independently.

## Repair and independent review

Carry the original finding ID, expected behavior, evidence confidence, implementation constraints and verification criterion into each repair. Work on a separate copy, keep the diff and resulting snapshot, and retest the affected plus relevant regression journeys. Do not broaden the fix into an unapproved architecture or Code Tool change.

For a requested independent review, read the bundled [Artemis Reviewer](../../artemis-reviewer/SKILL.md), preferably assign a separate agent, and pass build/design context, findings, exact source/evidence and remaining test limits. Retain build ownership and assign review only. If Reviewer initiated the repair, return to that coordinator without recursive handoff. Default to one repair batch and one linked verification within the authorized allowance; another skill or run ID does not reset limits. If independent review is unavailable, deliver useful self-test evidence with that gap disclosed. Never invent a reviewer or use its status field as proof. A review request alone does not authorize repair or live business effects.

Rollback must follow the agreed scope and consider new backend state/in-flight work. An older source import is not automatically a safe rollback. Deployment, promotion, tickets and external sharing require explicit authority; deliver artifacts and a useful scoped result when these are outside scope.
