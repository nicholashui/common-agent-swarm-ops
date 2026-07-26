import { AppShell } from "../../components/AppShell";
import { CanvasHome } from "../../components/CanvasHome";

/**
 * Non-inventing Swarm Canvas menu entry (ui_04).
 * Does not fabricate a swarm identifier; local graph landing is safe to render.
 */
function LegacyCanvasPage(): JSX.Element {
  return (
    <AppShell>
      <CanvasHome />
    </AppShell>
  );
}

export default LegacyCanvasPage;
