import { AppShell } from "../../components/AppShell";
import { BoundRegistryHome } from "../../components/screen/BoundRegistryHome";

/**
 * Registry uses BoundRegistryHome (getScreenParameters("registry") inside)
 * rather than BoundScreenHome, so the client graph stays small enough for
 * search / facets / Cards|Table|Graph to hydrate and work.
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <BoundRegistryHome />
    </AppShell>
  );
}
