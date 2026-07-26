import { AppShell } from "../../../../components/AppShell";
import { BoundAgentDetailHome } from "../../../../components/screen/BoundScreenHome";

interface AgentDetailPageProps {
  readonly params: {
    readonly agentId: string;
  };
}

/**
 * Agent detail binds the opaque route parameter and stored agentDetail
 * projection below the server-rendered authenticated shell.
 */
export default function AgentDetailPage({ params }: AgentDetailPageProps): JSX.Element {
  return (
    <AppShell>
      <BoundAgentDetailHome agentId={params.agentId} />
    </AppShell>
  );
}
