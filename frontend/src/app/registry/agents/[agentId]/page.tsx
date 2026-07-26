import { AppShell } from "../../../../components/AppShell";
import { CommonComponentDetail } from "../../../../components/OperationalScreens";
import {
  LOCAL_COMPONENT_DETAIL_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../../../lib/projections/local-preview";

interface AgentDetailPageProps {
  readonly params: {
    readonly agentId: string;
  };
}

function AgentDetailPage({ params }: AgentDetailPageProps): JSX.Element {
  void params;
  return (
    <AppShell>
      <CommonComponentDetail
        projection={LOCAL_COMPONENT_DETAIL_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default AgentDetailPage;
