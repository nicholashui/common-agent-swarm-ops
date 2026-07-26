import { AppShell } from "../../../components/AppShell";
import { ApiPortalHome } from "../../../components/ApiPortalHome";

/**
 * Developer / API Portal (ui_15). Local presentation landing until
 * generated OpenAPI, token service, and webhook projections connect.
 */
function DeveloperApiPage(): JSX.Element {
  return (
    <AppShell>
      <ApiPortalHome />
    </AppShell>
  );
}

export default DeveloperApiPage;
