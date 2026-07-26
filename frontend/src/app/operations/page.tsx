import { AppShell } from "../../components/AppShell";
import { ApprovalGateScreen } from "../../components/ApprovalRolloutScreens";
import { Monitoring } from "../../components/OperationalScreens";
import {
  LOCAL_APPROVAL_PROJECTION,
  LOCAL_MONITORING_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function OperationsPage(): JSX.Element {
  return (
    <AppShell>
      <div className="responsive-stack">
        <Monitoring
          projection={LOCAL_MONITORING_PROJECTION}
          {...LOCAL_PREVIEW_HANDLERS}
        />
        <ApprovalGateScreen
          projection={LOCAL_APPROVAL_PROJECTION}
          {...LOCAL_PREVIEW_HANDLERS}
        />
      </div>
    </AppShell>
  );
}

export default OperationsPage;
