import { AppShell } from "../../components/AppShell";
import { LocalDestinationPreview } from "../../components/LocalDestinationPreview";
import { LOCAL_DESTINATION_COPY } from "../../lib/projections/local-preview";

function CostsPage(): JSX.Element {
  return (
    <AppShell>
      <LocalDestinationPreview copy={LOCAL_DESTINATION_COPY.costs} />
    </AppShell>
  );
}

export default CostsPage;
