# Full-page document viewer — step-by-step user guide

**Screen:** Document viewer  
**Route:** `/docs/view?path=/docs/...`  
**Who it’s for:** Anyone reading a full markdown document outside the side drawer.

---

## 1. Open from the shell

1. While on any authenticated screen, click the top-right **Documents** (book) icon.
2. You navigate to `/docs/view?path=...` with the primary markdown candidate for the current route.

---

## 2. Read the document

1. Wait for **Loading document…** to finish.
2. Read headings, lists, tables, and images.
3. Relative images resolve against the markdown file path under `/docs`.

---

## 3. Missing documents

1. If no file exists, you see a neutral empty or error message.
2. HTML SPA fallbacks are treated as missing docs (not as valid markdown).

---

## 4. Return

1. Click **← Back to console** to return to the shell (typically Dashboard).
2. Or use the browser back button.

---

## 5. Safety notes

- Only paths under `/docs/` are accepted.
- Path traversal (`..`) is rejected.
