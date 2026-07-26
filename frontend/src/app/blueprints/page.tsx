import { AppShell } from "../../components/AppShell";
import { BlueprintsHome } from "../../components/BlueprintsHome";

/**
 * Blueprints & Templates Gallery (ui_20). Local presentation landing until
 * blueprint projections and authorized deploy/publish actions connect.
 */
function BlueprintsPage(): JSX.Element {
  return (
    <AppShell>
      <BlueprintsHome />
    </AppShell>
  );
}

export default BlueprintsPage;
