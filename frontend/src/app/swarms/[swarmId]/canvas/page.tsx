"use client";

import { AppShell } from "../../../../components/AppShell";
import { CanvasHome } from "../../../../components/CanvasHome";
import { useScreenParameters } from "../../../../lib/projections/use-screen-parameters";

interface SwarmCanvasPageProps {
  readonly params: {
    readonly swarmId: string;
  };
}

/**
 * Canvas reads stored canvas parameters. swarmId is reserved for authorized
 * projection scope when live graph contracts connect.
 */
export default function SwarmCanvasPage({ params }: SwarmCanvasPageProps): JSX.Element {
  void params;
  const view = useScreenParameters("canvas");
  return (
    <AppShell>
      <CanvasHome view={view} />
    </AppShell>
  );
}
