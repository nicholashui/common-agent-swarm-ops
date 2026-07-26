"use client";

import { AppShell } from "../../../../components/AppShell";
import { AgentDetailHome } from "../../../../components/AgentDetailHome";
import { useScreenParameters } from "../../../../lib/projections/use-screen-parameters";

interface AgentDetailPageProps {
  readonly params: {
    readonly agentId: string;
  };
}

/**
 * Agent detail reads stored agentDetail parameters (not hardcoded fixtures).
 * agentId is reserved for future authorized projection scope.
 */
export default function AgentDetailPage({ params }: AgentDetailPageProps): JSX.Element {
  const view = useScreenParameters("agentDetail");
  return (
    <AppShell>
      <AgentDetailHome agentId={params.agentId} view={view} />
    </AppShell>
  );
}
