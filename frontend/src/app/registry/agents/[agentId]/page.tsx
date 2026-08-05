import { AppShell } from "../../../../components/AppShell";
import { BoundAgentDetailHome } from "../../../../components/screen/BoundScreenHome";

interface AgentDetailPageProps {
  /** Next.js 16+: params is a Promise — must await before reading agentId. */
  readonly params: Promise<{
    readonly agentId: string;
  }>;
}

/**
 * Agent detail binds the opaque route parameter and pack-backed projection
 * below the server-rendered authenticated shell.
 */
export default async function AgentDetailPage({
  params,
}: AgentDetailPageProps): Promise<JSX.Element> {
  const { agentId: rawId } = await params;
  let agentId = (rawId ?? "").trim();
  try {
    agentId = decodeURIComponent(agentId);
  } catch {
    /* keep raw */
  }
  return (
    <AppShell>
      <BoundAgentDetailHome agentId={agentId} />
    </AppShell>
  );
}
