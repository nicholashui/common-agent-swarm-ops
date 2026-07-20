import { AgentDetail } from "../../../../components/AgentDetail";
import { AppShell } from "../../../../components/AppShell";

function AgentDetailPage({ params }: { readonly params: { readonly agentId: string } }): JSX.Element {
  return <AppShell><AgentDetail agentId={params.agentId} /></AppShell>;
}

export default AgentDetailPage;
