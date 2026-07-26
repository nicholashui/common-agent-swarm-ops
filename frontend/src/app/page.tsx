import { AppShell } from "../components/AppShell";
import { Dashboard } from "../components/OperationalScreens";
import {
  LOCAL_DASHBOARD_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../lib/projections/local-preview";

function HomePage(): JSX.Element {
  return (
    <AppShell>
      <Dashboard
        projection={LOCAL_DASHBOARD_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default HomePage;
