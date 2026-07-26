import { AppShell } from "../../../../components/AppShell";
import { Canvas } from "../../../../components/Canvas";

interface SwarmCanvasPageProps {
  readonly params: {
    readonly swarmId: string;
  };
}

/**
 * Canonical canvas route. The opaque swarmId is reserved for the future
 * authorized projection lookup; local default canvas is safe to render meanwhile.
 */
function SwarmCanvasPage({ params }: SwarmCanvasPageProps): JSX.Element {
  void params;
  return (
    <AppShell>
      <Canvas />
    </AppShell>
  );
}

export default SwarmCanvasPage;
