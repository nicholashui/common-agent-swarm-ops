"use client";

/**
 * @duty DemoModeBanner — non-authority / demo session banner
 * @role Announce demo/local preview mode so fixtures are not treated as production.
 * @controls Exit Demo button → same-origin logout then /login (session only).
 * @must State demo/local preview; disable button while busy; surface safe error text.
 * @mustnot Claim production activation, live media success, or host authority.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.1
 */
import React, { useState } from "react";
import { useRouter } from "next/navigation";

export function DemoModeBanner(): JSX.Element {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const exitDemo = async (): Promise<void> => {
    setBusy(true);
    setError(undefined);
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "same-origin",
      });
      if (!response.ok) {
        setError("Could not exit demo mode.");
        setBusy(false);
        return;
      }
      router.replace("/login");
      router.refresh();
    } catch {
      setError("Could not exit demo mode.");
      setBusy(false);
    }
  };

  return (
    <div className="demo-mode-banner" role="status">
      <div className="demo-mode-banner__copy">
        <strong>You are in Demo mode.</strong>
        <span>
          Common Agents &amp; Patterns are preloaded. Run swarms safely with local
          preview data.
        </span>
        {error ? <span className="demo-mode-banner__error">{error}</span> : null}
      </div>
      <button
        className="demo-mode-banner__exit"
        disabled={busy}
        onClick={() => {
          void exitDemo();
        }}
        type="button"
      >
        {busy ? "Exiting…" : "Exit Demo"}
      </button>
    </div>
  );
}
