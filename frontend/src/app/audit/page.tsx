import { AppShell } from "../../components/AppShell";
import { BoundScreenHome } from "../../components/screen/BoundScreenHome";

/**
 * AuditHome reads stored parameters through useScreenParameters below the
 * server-rendered authenticated shell.
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <BoundScreenHome screen="audit" />
    </AppShell>
  );
}
