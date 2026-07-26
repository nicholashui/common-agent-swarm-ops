import { AppShell } from "../../components/AppShell";
import { AuditHome } from "../../components/AuditHome";

/**
 * Governance & Audit Trail (ui_14). Local presentation landing —
 * append-only redacted log until authorized audit projections connect.
 */
function AuditPage(): JSX.Element {
  return (
    <AppShell>
      <AuditHome />
    </AppShell>
  );
}

export default AuditPage;
