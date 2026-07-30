import { AppShell } from "../../../components/AppShell";
import { OrgChartHome } from "../../../components/OrgChartHome";

/**
 * Registry Org Chart — non-special business pack hierarchy (e.g. business/video).
 * Fills the main content area under the Registry menu.
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <OrgChartHome />
    </AppShell>
  );
}
