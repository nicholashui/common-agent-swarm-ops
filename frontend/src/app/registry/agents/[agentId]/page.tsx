import { AppShell } from "../../../../components/AppShell";
import { AgentDetailHome } from "../../../../components/AgentDetailHome";

interface AgentDetailPageProps {
  readonly params: {
    readonly agentId: string;
  };
}

/**
 * Common Agent detail route (ui_05). Opaque agentId is reserved for authorized
 * projection lookup; local landing remains safe until that endpoint connects.
 */
function AgentDetailPage({ params }: AgentDetailPageProps): JSX.Element {
  return (
    <AppShell>
      <AgentDetailHome agentId={params.agentId} />
    </AppShell>
  );
}

export default AgentDetailPage;
