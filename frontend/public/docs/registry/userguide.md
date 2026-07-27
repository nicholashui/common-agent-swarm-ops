# Registry Hub — step-by-step user guide

**Screen:** Common Registry  
**Route:** `/registry`  
**Who it’s for:** Operators discovering pack agents (video + specials) and patterns.

---

## 1. Open Registry

1. Sign in → **COMMON** → **Registry Hub**, or open `/registry`.
2. Confirm header **Common Registry**, search box, view modes, and facet chips.

---

## 2. Search agents

1. Click the search box (placeholder like “Search agent id, name, pack, role…”).
2. Type tokens, e.g. `orchestrator` or `video.`.
3. Watch the line **Showing X of 133 agents** update.
4. Clear search (or use **Clear filters**) to restore the full list.

**Tips**

- Multiple words are AND (all tokens must match).
- Search covers id, name, description, badges, domains, usage, version.

---

## 3. Use facet tags

1. Click a chip under the search bar, e.g. `video`, `specials`, `draft`, `registered`.
2. Active chips highlight; count updates.
3. Domain chips (`video` / `specials`) combine with **OR**.
4. Other chips (e.g. `draft`) combine with **AND**.
5. Click an active chip again to turn it off.
6. **Clear filters** removes search + all facets.

---

## 4. Switch view mode

1. **Cards** — grid of agent cards (default).
2. **Table** — compact table with name, version, usage, actions.
3. **Graph viz** — local layout of matching agents (up to 48); click a node to inspect summary.

---

## 5. Work with an agent card

1. Read name, version pill, description, badges, metrics.
2. **Add to Swarm** / **Propose** — fail closed without host action references.
3. **Detail** — opens `/registry/agents/<agent-id>` for full settings.

---

## 6. Patterns and proposals

1. Scroll to **Core Common Swarm Patterns**.
2. Open **Instantiate in Canvas** or **Fork Pattern** (fork fails closed without authority).
3. **Pending proposals** section is pack-catalog honest (no demo proposal authority).

---

## 7. Specials catalog

1. Scroll to **Special Agents Pack**.
2. Search specials by id/title in that panel’s search.
3. **View agent settings** opens detail; **Inspect activation policy** remains fail-closed (draft/non-active).

---

## 8. Help

1. Top-right **Help** loads this guide for `/registry`.
2. Nested agent routes fall back to `/docs/registry/agents/userguide.md` after param strip.

---

## 9. Safety notes

- Catalog is self-contained pack data; **never** production activation from this screen.
- Browser is non-authority for mutate intents.
