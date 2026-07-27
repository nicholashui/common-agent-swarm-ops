# Knowledge — functional specification

**Route:** `/knowledge` · **Auth:** required · **Component:** `KnowledgeHome`

## Functional requirements

### FR-KNW-001 Search
- Search SHALL call `knowledge.search` via action bridge when wired.
- Results are redacted projections only.

### FR-KNW-002 Detail tabs
- Detail tabs switch projected knowledge facets.

### FR-KNW-003 Ingestion
- Ingestion UI disabled without generated authorized contract.
- Client validation non-authoritative; no browser-fetch of untrusted import URLs as security boundary.

### FR-KNW-004 Help
- `/docs/knowledge/{userguide,func_spec,test_scenario}.md`
