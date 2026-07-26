import { AppShell } from "../../components/AppShell";
import { Registry } from "../../components/OperationalScreens";
import {
  LOCAL_PREVIEW_HANDLERS,
  LOCAL_REGISTRY_PROJECTION,
} from "../../lib/projections/local-preview";

function RegistryPage(): JSX.Element {
  return (
    <AppShell>
      <Registry
        projection={LOCAL_REGISTRY_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default RegistryPage;
