import { AppShell } from "../../../../components/AppShell";
import { BoundSwarmCanvasHome } from "../../../../components/screen/BoundScreenHome";

interface SwarmCanvasPageProps {
  /** Next.js 16+: params is a Promise — must await before reading swarmId. */
  readonly params: Promise<{
    readonly swarmId: string;
  }>;
}

/**
 * Canvas binds the opaque swarmId route parameter and stored canvas projection
 * below the server-rendered authenticated shell.
 */
export default async function SwarmCanvasPage({
  params,
}: SwarmCanvasPageProps): Promise<JSX.Element> {
  const { swarmId: rawId } = await params;
  let swarmId = (rawId ?? "").trim();
  try {
    swarmId = decodeURIComponent(swarmId);
  } catch {
    /* keep raw */
  }
  return (
    <AppShell>
      <BoundSwarmCanvasHome swarmId={swarmId} />
    </AppShell>
  );
}
