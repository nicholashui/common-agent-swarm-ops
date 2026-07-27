# API Portal — functional specification

**Route:** `/developer/api` · **Auth:** required · **Component:** `ApiPortalHome`

## Functional requirements

### FR-API-001 Navigation
- Section nav switches portal areas from projection.

### FR-API-002 Explorer
- Endpoint list/search local filter; sample tabs switch samples.

### FR-API-003 Try-it
- Only when authorized host contract exists; otherwise fail-closed.

### FR-API-004 Tokens/webhooks
- Lists are projections; create/rotate require host portal actions.
- MUST NOT store API keys in browser durable storage from this UI.

### FR-API-005 Help
- `/docs/developer/api/{userguide,func_spec,test_scenario}.md`
