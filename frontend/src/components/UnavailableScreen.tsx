/**
 * @duty UnavailableScreen — authorized unavailable route shell
 * @role Compose AppShell + ScreenBoundary with empty capabilities so only the
 *       fixture/server unavailable error (and optional recovery) is shown.
 * @controls Recovery only if unavailable projection supplies ActionControl target.
 * @must Use screen-manifest definition/fixture; safe copy only.
 * @mustnot Probe health endpoints for tenancy/infra disclosure.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.1
 */
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
