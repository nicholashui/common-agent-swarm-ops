import { AppShell } from "../components/AppShell";
import { DashboardHome } from "../components/DashboardHome";

function HomePage(): JSX.Element {
  return (
    <AppShell>
      <DashboardHome />
    </AppShell>
  );
}

export default HomePage;
