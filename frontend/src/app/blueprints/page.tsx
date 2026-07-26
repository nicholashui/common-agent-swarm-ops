import { AppShell } from "../../components/AppShell";
import { LocalDestinationPreview } from "../../components/LocalDestinationPreview";
import { LOCAL_DESTINATION_COPY } from "../../lib/projections/local-preview";

function BlueprintsPage(): JSX.Element {
  return (
    <AppShell>
      <LocalDestinationPreview copy={LOCAL_DESTINATION_COPY.blueprints} />
    </AppShell>
  );
}

export default BlueprintsPage;
