# Executive brief guide

Create `00-business-brief.md` as the first file in the package and first link presented to business readers. Title it **Executive brief: <agent name>**. Keep it to one page in the intended export (roughly 400–500 words in Markdown), using plain customer language.

## Required content

1. **Problem:** who needs help, what is difficult today, and why it matters.
2. **Success measures:** each business outcome and its KPI, baseline, target and measurement source, summarized from the agent definition. Preserve evidence labels and unknowns.
3. **Wave 1 scope:** the first release's user goals and necessary setup, in plain words.
4. **Exclusions:** what this release will not handle.
5. **Top risks and kickoff blockers:** the most consequential risks, customer decisions or access actions, and their impact.
6. **Readiness verdict:** the current verdict explained in ordinary words, what can happen next, and what still blocks it. Distinguish design completion from permission to build.

## Governance without IDs

This is a derived business summary, not a second source of design facts. Use **no IDs**, including document, use-case, requirement, integration or API codes. Do not add a category marker or Document Metadata block. Keep the brief's document ID, version, status, wave and owner in the index register only; use the type `Executive Brief`. Link to canonical documents through the index's reading map rather than embedding ID-bearing paths in the brief.

Draft the brief with the first governed increment even when evidence is thin. Say “not yet known” or “proposed” where appropriate; never invent a baseline, target, approval or readiness verdict. Refresh it after material scope, outcome, risk or readiness changes and before handoff/finalization. Check consistency against canonical files and verify one-page length in any requested export. Keep detailed use cases, experience decisions and technical contracts in their separate files.
