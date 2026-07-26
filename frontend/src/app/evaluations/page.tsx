"use client";

import { AppShell } from "../../components/AppShell";
import { EvalHome } from "../../components/EvalHome";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Screen parameters are read from the stored projection store (not hardcoded).
 * Update via setScreenParameters / updateScreenParameters when live projections connect.
 */
export default function Page(): JSX.Element {
  const view = useScreenParameters("eval");
  return (
    <AppShell>
      <EvalHome view={view} />
    </AppShell>
  );
}