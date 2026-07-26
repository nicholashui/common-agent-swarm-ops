import { AppShell } from "../../components/AppShell";
import { CollaborationHome } from "../../components/CollaborationHome";

/**
 * Collaboration & Sharing (ui_18). Local presentation landing until
 * sharing permissions, comments, and co-edit sessions connect.
 * No peer execution channel.
 */
function CollaborationPage(): JSX.Element {
  return (
    <AppShell>
      <CollaborationHome />
    </AppShell>
  );
}

export default CollaborationPage;
