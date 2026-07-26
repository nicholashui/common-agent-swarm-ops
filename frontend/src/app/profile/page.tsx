import { AppShell } from "../../components/AppShell";
import { ProfileHome } from "../../components/ProfileHome";

/**
 * User Profile & Preferences (ui_13). Local presentation landing — no
 * credentials, no other users' artifacts, server-derived role only.
 */
function ProfilePage(): JSX.Element {
  return (
    <AppShell>
      <ProfileHome />
    </AppShell>
  );
}

export default ProfilePage;
