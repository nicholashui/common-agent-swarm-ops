import { AppShell } from "../../components/AppShell";
import { KnowledgeArtifactScreen } from "../../components/KnowledgeArtifactScreens";
import {
  LOCAL_KNOWLEDGE_IMPORT_PROJECTION,
  LOCAL_KNOWLEDGE_REQUIREMENTS,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function KnowledgePage(): JSX.Element {
  return (
    <AppShell>
      <KnowledgeArtifactScreen
        importProjection={LOCAL_KNOWLEDGE_IMPORT_PROJECTION}
        ingestionRequirementsProjection={LOCAL_KNOWLEDGE_REQUIREMENTS}
        kind="knowledge"
        onResolveReference={LOCAL_PREVIEW_HANDLERS.onReference}
      />
    </AppShell>
  );
}

export default KnowledgePage;
