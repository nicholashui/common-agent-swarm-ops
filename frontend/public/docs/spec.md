# Console shell specification

This is a **generic** specification document for the application shell.

| Concern | Behavior |
|---------|----------|
| Docs root | `/docs/<route>/<type>.md` |
| Fallback | Param-stripped route path |
| Soft miss | 404 / HTML fallback |

---

Relative assets resolve against this file's path.
