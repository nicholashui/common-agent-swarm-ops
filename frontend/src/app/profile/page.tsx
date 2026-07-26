import { AppShell } from "../../components/AppShell";
import { Profile } from "../../components/OperationalScreens";
import {
  LOCAL_PREVIEW_HANDLERS,
  LOCAL_PROFILE_PROJECTION,
} from "../../lib/projections/local-preview";

function ProfilePage(): JSX.Element {
  return (
    <AppShell>
      <Profile
        projection={LOCAL_PROFILE_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default ProfilePage;
