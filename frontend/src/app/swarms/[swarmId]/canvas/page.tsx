import { AppShell } from "../../../../components/AppShell";
import { CanvasHome } from "../../../../components/CanvasHome";

interface SwarmCanvasPageProps {
  readonly params: {
    readonly swarmId: string;
  };
}

/**
 * Canonical canvas route. Opaque swarmId is reserved for authorized projection
 * lookup; local canvas landing remains safe until that endpoint is connected.
 */
function SwarmCanvasPage({ params }: SwarmCanvasPageProps): JSX.Element {
  void params;
  return (
    <AppShell>
      <CanvasHome />
    </AppShell>
  );
}

export default SwarmCanvasPage;
