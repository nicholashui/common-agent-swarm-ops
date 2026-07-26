import { AppShell } from "../../components/AppShell";
import { NotificationsHome } from "../../components/NotificationsHome";

/**
 * Notifications Center (ui_12). Local presentation landing until
 * notification projections, preferences, and delivery channels connect.
 */
function NotificationsPage(): JSX.Element {
  return (
    <AppShell>
      <NotificationsHome />
    </AppShell>
  );
}

export default NotificationsPage;
