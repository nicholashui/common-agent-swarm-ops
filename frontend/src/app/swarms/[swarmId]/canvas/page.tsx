import { AppShell } from "../../../../components/AppShell";
import { BoundSwarmCanvasHome } from "../../../../components/screen/BoundScreenHome";

interface SwarmCanvasPageProps {
  readonly params: {
    readonly swarmId: string;
  };
}

/**
 * Canvas binds the opaque swarmId route parameter and stored canvas projection
 * below the server-rendered authenticated shell.
 */
export default function SwarmCanvasPage({ params }: SwarmCanvasPageProps): JSX.Element {
  return (
    <AppShell>
      <BoundSwarmCanvasHome swarmId={params.swarmId} />
    </AppShell>
  );
}
