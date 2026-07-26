import { AppShell } from "../../components/AppShell";
import { KnowledgeHome } from "../../components/KnowledgeHome";

/**
 * Knowledge Management Hub (ui_10). Local presentation landing until
 * knowledge projections, sync jobs, and contribution governance connect.
 */
function KnowledgePage(): JSX.Element {
  return (
    <AppShell>
      <KnowledgeHome />
    </AppShell>
  );
}

export default KnowledgePage;
