import { AppShell } from "../../components/AppShell";
import { BoundComposerHome } from "../../components/screen/BoundComposerHome";

/**
 * Slim composer entry — BoundComposerHome only (avoids multi-home client graph).
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <BoundComposerHome />
    </AppShell>
  );
}
