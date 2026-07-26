import { AppShell } from "../../components/AppShell";
import { MobileHome } from "../../components/MobileHome";

/**
 * Mobile / PWA Companion (ui_17). Local presentation landing until
 * responsive shells, service worker, and push delivery connect.
 */
function MobilePage(): JSX.Element {
  return (
    <AppShell>
      <MobileHome />
    </AppShell>
  );
}

export default MobilePage;
