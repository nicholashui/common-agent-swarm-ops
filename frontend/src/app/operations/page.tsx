import { AppShell } from "../../components/AppShell";
import { ApprovalGateScreen } from "../../components/ApprovalRolloutScreens";
import { MonitoringHome } from "../../components/MonitoringHome";
import {
  LOCAL_APPROVAL_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

/**
 * Operations surface: ui_09 monitoring landing plus approvals/rollouts
 * projection (menu shares /operations until a dedicated approvals route exists).
 */
function OperationsPage(): JSX.Element {
  return (
    <AppShell>
      <div className="responsive-stack">
        <MonitoringHome />
        <ApprovalGateScreen
          projection={LOCAL_APPROVAL_PROJECTION}
          {...LOCAL_PREVIEW_HANDLERS}
        />
      </div>
    </AppShell>
  );
}

export default OperationsPage;
