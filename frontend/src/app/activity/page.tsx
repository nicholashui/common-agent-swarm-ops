import { AppShell } from "../../components/AppShell";
import { BoundActivityHome } from "../../components/screen/BoundActivityHome";

/**
 * Slim activity entry — BoundActivityHome only (avoids multi-home client graph).
 */
export default function Page(): JSX.Element {
  return (
    <AppShell>
      <BoundActivityHome />
    </AppShell>
  );
}
