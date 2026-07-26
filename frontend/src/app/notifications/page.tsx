import { AppShell } from "../../components/AppShell";
import { Notifications } from "../../components/OperationalScreens";
import {
  LOCAL_NOTIFICATIONS_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function NotificationsPage(): JSX.Element {
  return (
    <AppShell>
      <Notifications
        projection={LOCAL_NOTIFICATIONS_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default NotificationsPage;
