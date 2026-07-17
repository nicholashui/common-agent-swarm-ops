# Requirements

## Context
CASOPS is a local Node 20+ executable repository. It emits only Kiro and Claude Code project configuration, keeps downloaded references untrusted, and uses deterministic SDD gates. Profile: R2. Risk: medium.

## Acceptance Criteria
- REQ-1: When a permitted manifest is loaded, the system shall validate required source fields and confined targets.
- REQ-2: When sync is requested, the system shall plan or write only allowlisted Kiro and Claude Code paths.
- REQ-3: When a source download dry run is requested, the system shall validate selection without networking.
- REQ-4: When repository checks run, the system shall validate requirements, design, tasks, traceability, and evidence.
- REQ-5: The prohibited Gemini and Gemini CLI ecosystems shall be rejected by source and output policy validation.
- REQ-6: When a human approves an audited, licensed ECC skill, CASOPS shall install only a documentation-only curated adaptation to Kiro and Claude Code skill locations with pinned provenance.

## Non-goals
No global configuration, third-party-code execution, automatic imports, or native outputs for other tools.

## Approval
Bootstrap artifact reviewed by local deterministic gate; human approval remains required for high-impact changes.
