import { AppShell } from "../../components/AppShell";
import { SettingsHome } from "../../components/SettingsHome";

/**
 * Global Settings (ui_08). Local presentation landing — no secret values,
 * no client authority to change live policy without authorized actions.
 */
function SettingsPage(): JSX.Element {
  return (
    <AppShell>
      <SettingsHome />
    </AppShell>
  );
}

export default SettingsPage;
