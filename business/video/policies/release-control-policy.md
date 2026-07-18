# Video Release-Control Policy

## Release prerequisites
A video artifact may be released only after its immutable version lineage is known and acyclic, rights and consent are complete, provenance and final sign-off are present, every named L1/L2/L3 and Q1–Q6 quality check passes, and no blocker remains unresolved.

## Critique control
Critiques must conform to `business/schemas/critique-message.schema.json`. A `blocker`, including one issued by `video.compliance_agent`, prevents graph progress and release until a recorded resolution. A `major` finding permits no more than three refine/review attempts before JudgeAgent or human escalation. `minor` and `nit` findings remain logged for learning and cannot override a failed release gate.

## Denial behavior
Cyclic, ambiguous, missing, or unknown lineage; failed or absent named checks; incomplete rights/consent; missing provenance/sign-off; and unresolved blockers are release denials. The future release service must retain the request and return all unmet conditions.

## Boundary
This policy is declarative pack data. It does not invoke media providers, create a control-plane route, activate agents, or release artifacts.
