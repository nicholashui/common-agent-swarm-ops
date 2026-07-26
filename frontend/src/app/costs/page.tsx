import { AppShell } from "../../components/AppShell";
import { CostsHome } from "../../components/CostsHome";

/**
 * Cost & Token Analytics (ui_19). Local presentation landing until
 * cost attribution projections and authorized budget actions connect.
 * No client-created budget authority.
 */
function CostsPage(): JSX.Element {
  return (
    <AppShell>
      <CostsHome />
    </AppShell>
  );
}

export default CostsPage;
