import { AppShell } from "../../components/AppShell";
import { Evaluation } from "../../components/OperationalScreens";
import {
  LOCAL_EVALUATION_PROJECTION,
  LOCAL_PREVIEW_HANDLERS,
} from "../../lib/projections/local-preview";

function EvaluationsPage(): JSX.Element {
  return (
    <AppShell>
      <Evaluation
        projection={LOCAL_EVALUATION_PROJECTION}
        {...LOCAL_PREVIEW_HANDLERS}
      />
    </AppShell>
  );
}

export default EvaluationsPage;
