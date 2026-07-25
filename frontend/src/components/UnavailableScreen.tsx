import { getScreenDefinition, getScreenFixture, type ScreenId } from "../lib/screens/screen-manifest";
import { AppShell } from "./AppShell";
import { ScreenBoundary } from "./ScreenBoundary";

export function UnavailableScreen({ screenId }: { readonly screenId: ScreenId }): JSX.Element {
  const definition = getScreenDefinition(screenId);
  const fixture = getScreenFixture(screenId);
  return <AppShell><ScreenBoundary
    capabilities={[]}
    definition={definition}
    shell={null}
    unavailableState={{ error: fixture.unavailableError }}
  >
    <></>
  </ScreenBoundary></AppShell>;
}
