import { AppShell } from "../../components/AppShell";
import { BoundMonitoringHome } from "../../components/screen/BoundScreenHome";

/**
 * Operations binds MonitoringHome and approval projections below the
 * server-rendered authenticated shell with useScreenParameters.
 */
export default function OperationsPage(): JSX.Element {
  return (
    <AppShell>
      <BoundMonitoringHome />
    </AppShell>
  );
}
