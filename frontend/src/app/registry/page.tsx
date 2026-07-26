import { AppShell } from "../../components/AppShell";
import { RegistryHome } from "../../components/RegistryHome";

/**
 * Common Registry Hub (ui_07). Local presentation landing until generated
 * commons registry projections and governance actions connect.
 */
function RegistryPage(): JSX.Element {
  return (
    <AppShell>
      <RegistryHome />
    </AppShell>
  );
}

export default RegistryPage;
