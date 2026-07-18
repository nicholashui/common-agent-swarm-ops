# Video Rights and Consent Policy

## Purpose
Every release candidate must retain rights and consent data in its immutable artifact handoff. This policy is configuration guidance only; it cannot call tools, authorize a release, or add a route.

## Required evidence
- A non-empty license reference for every supplied or generated asset.
- Likeness and voice consent references for every identifiable person.
- At least one allowed territory and an explicit embargo state.
- A provenance reference, critique-log reference, final sign-off chain, and versioned model/prompt inputs.

## Fail-closed handling
Missing, ambiguous, expired, or contradictory rights or consent evidence is an unresolved release blocker. The later release service must retain the request and report every unmet condition; it must not infer approval from absent data.

## Governance boundary
Only Host governance and the Host tool broker may evaluate or act on a release request. Pack agents may supply evidence or blockers but cannot bypass approval, audit, quality, provenance, or lineage controls.
