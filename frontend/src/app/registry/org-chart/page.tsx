import { AppShell } from "../../../components/AppShell";
import { BoundScreenHome } from "../../../components/screen/BoundScreenHome";

/**
 * Registry Org Chart — non-special business pack hierarchy (e.g. business/video).
 * Stored projection parameters and action handling are bound below the shell.
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <BoundScreenHome screen="orgChart" />
    </AppShell>
  );
}
