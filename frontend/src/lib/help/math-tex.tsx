"use client";

/**
 * Client-side KaTeX renderer for agent SPEC / help markdown.
 * Mutates a host node via katex.render (no dangerouslySetInnerHTML).
 * KaTeX is loaded dynamically so unit tests without a CSS loader stay clean.
 */
import React, { useEffect, useRef } from "react";

export function MathTex({
  tex,
  display = false,
  className,
}: Readonly<{
  tex: string;
  display?: boolean;
  className?: string;
}>): JSX.Element {
  const hostRef = useRef<HTMLElement | null>(null);
  const trimmed = tex.trim();

  useEffect(() => {
    const el = hostRef.current;
    if (!el) return;
    let cancelled = false;

    void (async () => {
      try {
        const katex = (await import("katex")).default;
        if (cancelled || !hostRef.current) return;
        const host = hostRef.current;
        while (host.firstChild) host.removeChild(host.firstChild);
        if (!trimmed) return;
        katex.render(trimmed, host, {
          displayMode: display,
          throwOnError: false,
          strict: "ignore",
          trust: false,
          output: "html",
        });
      } catch {
        if (!cancelled && hostRef.current) {
          hostRef.current.textContent = trimmed;
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [trimmed, display]);

  const classes = [
    display ? "help-md__math-block" : "help-md__math-inline",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  // No React children — KaTeX owns the host after effect. data-tex for SSR/tests.
  if (display) {
    return (
      <div
        className={classes}
        data-math="display"
        data-tex={trimmed}
        ref={hostRef as React.RefObject<HTMLDivElement>}
        suppressHydrationWarning
      />
    );
  }

  return (
    <span
      className={classes}
      data-math="inline"
      data-tex={trimmed}
      ref={hostRef as React.RefObject<HTMLSpanElement>}
      suppressHydrationWarning
    />
  );
}
