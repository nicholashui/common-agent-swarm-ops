import { AppShell } from "../../components/AppShell";
import { Audit } from "../../components/OperationalScreens";
import {
  LOCAL_AUDIT_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function AuditPage(): JSX.Element {
  return (
    <AppShell>
      <Audit projection={LOCAL_AUDIT_PROJECTION} {...LOCAL_PREVIEW_HANDLERS} />
    </AppShell>
  );
}

export default AuditPage;
