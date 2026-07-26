import { AppShell } from "../../components/AppShell";
import { Canvas } from "../../components/Canvas";

/**
 * Non-inventing Swarm Canvas menu entry. Does not fabricate a swarm identifier.
 * Uses the canvas component's built-in local default projection until a
 * server-authorized swarm projection is connected.
 */
function LegacyCanvasPage(): JSX.Element {
  return (
    <AppShell>
      <Canvas />
    </AppShell>
  );
}

export default LegacyCanvasPage;
