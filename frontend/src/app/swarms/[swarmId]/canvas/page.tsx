import { UnavailableScreen } from "../../../../components/UnavailableScreen";

interface SwarmCanvasPageProps {
  readonly params: {
    readonly swarmId: string;
  };
}

function SwarmCanvasPage({ params }: SwarmCanvasPageProps): JSX.Element {
  // The opaque route parameter identifies the requested resource; the generated
  // projection and capability are intentionally resolved by the server boundary.
  void params;
  return <UnavailableScreen screenId="ui_04_canvas" />;
}

export default SwarmCanvasPage;
