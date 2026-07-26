import { AppShell } from "../../components/AppShell";
import { LocalDestinationPreview } from "../../components/LocalDestinationPreview";
import { LOCAL_DESTINATION_COPY } from "../../lib/projections/local-preview";

function SettingsPage(): JSX.Element {
  return (
    <AppShell>
      <LocalDestinationPreview copy={LOCAL_DESTINATION_COPY.settings} />
    </AppShell>
  );
}

export default SettingsPage;
