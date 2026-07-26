import { AppShell } from "../../components/AppShell";
import { ActivityHome } from "../../components/ActivityHome";

/**
 * Activity & Ops Intelligence (ui_06). Local presentation landing until
 * generated activity projections and authorized run actions connect.
 */
function ActivityPage(): JSX.Element {
  return (
    <AppShell>
      <ActivityHome />
    </AppShell>
  );
}

export default ActivityPage;
