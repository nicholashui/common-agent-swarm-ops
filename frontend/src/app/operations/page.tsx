import { AppShell } from "../../components/AppShell";
import { OperatorConsole } from "../../components/OperatorConsole";

function OperationsPage(): JSX.Element {
  return <AppShell><div className="legacy-console"><OperatorConsole /></div></AppShell>;
}

export default OperationsPage;
