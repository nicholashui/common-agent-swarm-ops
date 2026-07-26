import { AppShell } from "../../components/AppShell";
import { EvalHome } from "../../components/EvalHome";

/**
 * Eval & Self-Improvement Dashboard (ui_11). Local presentation landing until
 * eval aggregates, proposal workflow, and campaign actions connect.
 */
function EvaluationsPage(): JSX.Element {
  return (
    <AppShell>
      <EvalHome />
    </AppShell>
  );
}

export default EvaluationsPage;
