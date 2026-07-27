"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { LoginScreen } from "../../components/LoginScreen";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Public session entry. Already-authenticated users are sent to the dashboard.
 * Login copy comes from stored screen parameters (not hardcoded in the page).
 */
export default function LoginPage(): JSX.Element {
  const view = useScreenParameters("login");
  const router = useRouter();

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const response = await fetch("/api/auth/session", {
          method: "GET",
          credentials: "same-origin",
          headers: { accept: "application/json" },
        });
        if (!response.ok || cancelled) return;
        const body = (await response.json()) as {
          readonly session?: { readonly authenticated?: boolean };
        };
        if (body.session?.authenticated === true && !cancelled) {
          router.replace("/");
        }
      } catch {
        // Stay on login if session probe fails.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  return <LoginScreen view={view} />;
}
