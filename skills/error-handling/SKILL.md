# Error Handling

Use this skill when defining failure behaviour, handling external dependency failures, or reviewing error paths.

## Principles

- Treat expected failures as part of the API contract.
- Use structured, typed error information where the language supports it.
- Validate inputs at trust boundaries and preserve useful context for operators.
- Separate safe user-facing messages from diagnostic details; never expose secrets, internals, or stack traces to users.
- Handle, rethrow, or safely record every caught error. Do not swallow failures.
- Retry only explicitly transient failures with bounded attempts, backoff, and cancellation support.

## Review checklist

- [ ] Failure modes and error codes are documented where consumers depend on them.
- [ ] Unknown errors have a safe fallback response.
- [ ] Retries cannot amplify load or repeat unsafe, non-idempotent operations.
- [ ] Logs contain useful context without credentials or sensitive payloads.
- [ ] Tests cover invalid input, dependency failure, and user-safe output.

## Provenance

Curated adaptation of ECC `skills/error-handling/SKILL.md` at commit `ed387446052dfbc6b52de149406b70efa65edc59`, MIT License. No executable ECC examples, dependencies, or tooling were imported.