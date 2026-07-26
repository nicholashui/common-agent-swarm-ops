"use client";

import { AppShell } from "../../components/AppShell";
import { ComposerHome } from "../../components/ComposerHome";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Screen parameters are read from the stored projection store (not hardcoded).
 * Update via setScreenParameters / updateScreenParameters when live projections connect.
 */
export default function Page(): JSX.Element {
  const view = useScreenParameters("composer");
  return (
    <AppShell>
      <ComposerHome view={view} />
    </AppShell>
  );
}