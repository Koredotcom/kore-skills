# Build intake and architecture confirmation

Read at entry and when requirements or scope change. Keep the user's goal, not the supplied export's accidental behavior, as the acceptance source.

## Enough design for the next slice

Record the business outcome, actors/identity, supported channels/languages, use cases in scope, consequential actions, required integrations, recovery and measurable acceptance. Preserve existing UC/FR/BR/EXP/AC IDs or use the supplied equivalent. Keep functional behavior separate from technical allocation. Missing details that do not affect the next slice can stay explicitly provisional.

For thin input, invoke available Designer with the known evidence and destination, then return with its design. Resolve material unknowns in small batches. Do not require every enterprise document to be complete before drafting the architecture brief. In a repair, distinguish intended behavior, observed behavior and the proposed correction; an inferred description of the current build is not proof of business intent.

## Reviewable direction

Use the bundled architecture brief asset. Aim for one–two pages including a legible graph, a few grouped responsibilities, choices and tradeoffs. Every agent needs a reason to exist; map use cases to owners rather than creating an agent per use case. Describe execution mode separately from routing pattern. State where ABL controls the sequence, where tools act and where authoritative permission/business checks live.

Label proposed assumptions and latency expectations. If a platform feature is unverified, identify the missing evidence and a viable alternative; do not present it as available. Put any Code Tool exception and consequential change in the decision table.

Ask the user to confirm this concrete direction and implementation scope. Existing explicit approval of the same architecture can be reused; link the decision, revision and conditions. Do not infer approval from silence or a generic build request. When pausing, say that this skill requires confirmation of the presented architecture before implementation and show the brief. Read-only investigation can continue.

## Continuity and scope

Maintain `BUILD_CONTEXT.md` with source/design references and hashes, confirmed target, architecture decision, permission scope, channels, available capabilities, credential-profile identifiers, permitted API effects, test limits, open decisions and relevant documentation versions. Record no raw credentials. Reuse facts already established in the conversation or authoritative artifacts; ask again only when conflicting/stale evidence matters.

Map each use case to source components and acceptance evidence in the build register. Technical implementation changes must not silently alter business rules or confirmed experience. Return material design changes to Designer if available and obtain the needed user decision once; ordinary implementation choices remain the Developer's job.

**Example:** a repair to a date formatter within an approved booking flow needs a linked diff and regression evidence. Replacing the flow's ownership checks with a reasoning agent changes the control model and needs a reviewed architecture delta before implementation.
