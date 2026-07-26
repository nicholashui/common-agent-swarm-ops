import { AppShell } from "../../components/AppShell";
import { OnboardingHome } from "../../components/OnboardingHome";

/**
 * Onboarding, Help & Documentation (ui_16). Local presentation landing until
 * tour progress preferences and docs CMS connect.
 */
function OnboardingPage(): JSX.Element {
  return (
    <AppShell>
      <OnboardingHome />
    </AppShell>
  );
}

export default OnboardingPage;
