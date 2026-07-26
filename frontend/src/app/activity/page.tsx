import { AppShell } from "../../components/AppShell";
import { Activity } from "../../components/OperationalScreens";
import {
  LOCAL_ACTIVITY_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function ActivityPage(): JSX.Element {
  return (
    <AppShell>
      <Activity
        projection={LOCAL_ACTIVITY_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default ActivityPage;
