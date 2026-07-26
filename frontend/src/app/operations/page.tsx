"use client";

import { AppShell } from "../../components/AppShell";
import { ApprovalGateScreen } from "../../components/ApprovalRolloutScreens";
import { MonitoringHome } from "../../components/MonitoringHome";
import { LOCAL_PREVIEW_HANDLERS } from "../../lib/projections/local-preview";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Operations surface: monitoring + approvals from stored screen parameters.
 */
export default function OperationsPage(): JSX.Element {
  const monitoring = useScreenParameters("monitoring");
  const approval = useScreenParameters("approval");
  return (
    <AppShell>
      <div className="responsive-stack">
        <MonitoringHome view={monitoring} />
        <ApprovalGateScreen
          projection={approval}
          {...LOCAL_PREVIEW_HANDLERS}
        />
      </div>
    </AppShell>
  );
}
