import { AppShell } from "../../../components/AppShell";
import { BoundScreenHome } from "../../../components/screen/BoundScreenHome";

/**
 * Agent Workflow — production scale + DNA call flowcharts.
 */
export default function AgentWorkflowPage(): JSX.Element {
  return (
    <AppShell>
      <BoundScreenHome screen="agentWorkflow" />
    </AppShell>
  );
}
