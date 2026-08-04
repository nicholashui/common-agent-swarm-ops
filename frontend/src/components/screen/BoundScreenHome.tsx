"use client";

/**
 * @duty BoundScreenHome — screen binder with code-split Homes
 * Each Home is next/dynamic so a route only downloads the active screen chunk
 * instead of one 6MB+ all-homes client graph.
 */
import type { ComponentType, ReactNode } from "react";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

import { useScreenParameters } from "../../lib/projections/use-screen-parameters";
import { resolveAgentDetailView } from "../../lib/projections/agent-detail-landing";
import {
  buildEmptyLiveDashboardShell,
} from "../../lib/projections/dashboard-live";
import type { DashboardLandingView } from "../../lib/projections/dashboard-landing";
import {
  loadLiveBlueprints,
  loadLiveCanvasLanding,
  loadLiveCollaboration,
  loadLiveCosts,
  loadLiveDashboard,
  loadLiveKnowledge,
  loadLiveMobile,
  loadLiveMonitoring,
  loadLiveNotifications,
  loadLiveProfile,
  loadLiveSettings,
} from "../../lib/projections/screen-live-loaders";
import { useInteractionRuntime } from "../../lib/ui/interaction-runtime";
import { useScreenActionBridge } from "../../lib/ui/use-screen-action";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";
import { SamplesBanner, SamplesToggle } from "../ui/SamplesToggle";
import { buildSampleApprovalProjection } from "../../lib/projections/operate-samples";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { GeneratedJsonObject } from "../../lib/api/client";

function useLiveView<T>(
  initial: T,
  loader: () => Promise<T>,
): T {
  const [view, setView] = useState(initial);
  useEffect(() => {
    let cancelled = false;
    void loader().then((next) => {
      if (!cancelled) setView(next);
    });
    return () => {
      cancelled = true;
    };
  }, [loader]);
  return view;
}

export type BoundScreenKey =
  | "activity"
  | "apiPortal"
  | "audit"
  | "blueprints"
  | "canvas"
  | "collaboration"
  | "composer"
  | "costs"
  | "dashboard"
  | "eval"
  | "knowledge"
  | "mobile"
  | "notifications"
  | "onboarding"
  | "orgChart"
  | "agentWorkflow"
  | "profile"
  | "registry"
  | "settings";

function LoadingHome(): JSX.Element {
  return (
    <p aria-busy="true" className="bound-screen-loading" role="status">
      Loading screen…
    </p>
  );
}

function lazyHome<P extends object>(
  loader: () => Promise<{ [key: string]: ComponentType<P> }>,
  exportName: string,
): ComponentType<P> {
  return dynamic(
    () =>
      loader().then((mod) => {
        const Comp = mod[exportName] as ComponentType<P>;
        return { default: Comp };
      }),
    { ssr: true, loading: () => <LoadingHome /> },
  );
}

const ActivityHome = lazyHome(
  () => import("../ActivityHome"),
  "ActivityHome",
);
const ApprovalGateScreen = lazyHome(
  () => import("../ApprovalRolloutScreens"),
  "ApprovalGateScreen",
);
const ApiPortalHome = lazyHome(
  () => import("../ApiPortalHome"),
  "ApiPortalHome",
);
const AuditHome = lazyHome(() => import("../AuditHome"), "AuditHome");
const BlueprintsHome = lazyHome(
  () => import("../BlueprintsHome"),
  "BlueprintsHome",
);
const CanvasHome = lazyHome(() => import("../CanvasHome"), "CanvasHome");
const CollaborationHome = lazyHome(
  () => import("../CollaborationHome"),
  "CollaborationHome",
);
const ComposerHome = lazyHome(() => import("../ComposerHome"), "ComposerHome");
const CostsHome = lazyHome(() => import("../CostsHome"), "CostsHome");
const DashboardHome = lazyHome(
  () => import("../DashboardHome"),
  "DashboardHome",
);
const EvalHome = lazyHome(() => import("../EvalHome"), "EvalHome");
const KnowledgeHome = lazyHome(
  () => import("../KnowledgeHome"),
  "KnowledgeHome",
);
const MonitoringHome = lazyHome(
  () => import("../MonitoringHome"),
  "MonitoringHome",
);
const MobileHome = lazyHome(() => import("../MobileHome"), "MobileHome");
const NotificationsHome = lazyHome(
  () => import("../NotificationsHome"),
  "NotificationsHome",
);
const OnboardingHome = lazyHome(
  () => import("../OnboardingHome"),
  "OnboardingHome",
);
const OrgChartHome = lazyHome(
  () => import("../OrgChartHome"),
  "OrgChartHome",
);
const AgentWorkflowHome = lazyHome(
  () => import("../AgentWorkflowHome"),
  "AgentWorkflowHome",
);
const ProfileHome = lazyHome(() => import("../ProfileHome"), "ProfileHome");
const RegistryHome = lazyHome(() => import("../RegistryHome"), "RegistryHome");
const SettingsHome = lazyHome(() => import("../SettingsHome"), "SettingsHome");
const AgentDetailHome = lazyHome(
  () => import("../AgentDetailHome"),
  "AgentDetailHome",
);
const OperationsConsole = lazyHome(
  () => import("../OperationsConsole"),
  "OperationsConsole",
);

export function BoundScreenHome({
  screen,
}: Readonly<{ screen: BoundScreenKey }>): JSX.Element {
  switch (screen) {
    case "activity":
      return <BoundActivityHome />;
    case "apiPortal":
      return <BoundApiPortalHome />;
    case "audit":
      return <BoundAuditHome />;
    case "blueprints":
      return <BoundBlueprintsHome />;
    case "canvas":
      return <BoundCanvasHome />;
    case "collaboration":
      return <BoundCollaborationHome />;
    case "composer":
      return <BoundComposerHome />;
    case "costs":
      return <BoundCostsHome />;
    case "dashboard":
      return <BoundDashboardHome />;
    case "eval":
      return <BoundEvalHome />;
    case "knowledge":
      return <BoundKnowledgeHome />;
    case "mobile":
      return <BoundMobileHome />;
    case "notifications":
      return <BoundNotificationsHome />;
    case "onboarding":
      return <BoundOnboardingHome />;
    case "orgChart":
      return <BoundOrgChartHome />;
    case "agentWorkflow":
      return <BoundAgentWorkflowHome />;
    case "profile":
      return <BoundProfileHome />;
    case "registry":
      return <BoundRegistryHomeLegacy />;
    case "settings":
      return <BoundSettingsHome />;
  }
}

function BoundShell({
  children,
  status,
}: Readonly<{
  children: ReactNode;
  status: ReturnType<typeof useInteractionRuntime>["status"];
}>): JSX.Element {
  return (
    <>
      <InteractionStatusBar status={status} />
      {children}
    </>
  );
}

function BoundActivityHome(): JSX.Element {
  const view = useScreenParameters("activity");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <ActivityHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundApiPortalHome(): JSX.Element {
  const view = useScreenParameters("apiPortal");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <ApiPortalHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundAuditHome(): JSX.Element {
  const view = useScreenParameters("audit");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <AuditHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundBlueprintsHome(): JSX.Element {
  const fallback = useScreenParameters("blueprints");
  const view = useLiveView(fallback, loadLiveBlueprints);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <BlueprintsHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundCanvasHome(): JSX.Element {
  const fallback = useScreenParameters("canvas");
  const view = useLiveView(fallback, loadLiveCanvasLanding);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <CanvasHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundCollaborationHome(): JSX.Element {
  const fallback = useScreenParameters("collaboration");
  const view = useLiveView(fallback, loadLiveCollaboration);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <CollaborationHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundComposerHome(): JSX.Element {
  const view = useScreenParameters("composer");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <ComposerHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundCostsHome(): JSX.Element {
  const fallback = useScreenParameters("costs");
  const view = useLiveView(fallback, loadLiveCosts);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <CostsHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundDashboardHome(): JSX.Element {
  const bridge = useScreenActionBridge();
  const [view, setView] = useState<DashboardLandingView>(() =>
    buildEmptyLiveDashboardShell(),
  );

  useEffect(() => {
    let cancelled = false;
    void loadLiveDashboard().then((next) => {
      if (!cancelled) setView(next);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <BoundShell status={bridge.runtime.status}>
      <DashboardHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
        onPause={(swarmId) => {
          void bridge.onAction({ kind: "local.pause_swarm", swarmId });
        }}
      />
    </BoundShell>
  );
}

function BoundEvalHome(): JSX.Element {
  const view = useScreenParameters("eval");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <EvalHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundKnowledgeHome(): JSX.Element {
  const fallback = useScreenParameters("knowledge");
  const view = useLiveView(fallback, loadLiveKnowledge);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <KnowledgeHome
        view={view}
        statusMessage={bridge.statusMessage}
        onSearch={(query) =>
          void bridge.onAction({ kind: "knowledge.search", query })
        }
        onAction={bridge.onAction}
      />
    </BoundShell>
  );
}

function BoundMobileHome(): JSX.Element {
  const fallback = useScreenParameters("mobile");
  const view = useLiveView(fallback, loadLiveMobile);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <MobileHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundNotificationsHome(): JSX.Element {
  const fallback = useScreenParameters("notifications");
  const view = useLiveView(fallback, loadLiveNotifications);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <NotificationsHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundOnboardingHome(): JSX.Element {
  const view = useScreenParameters("onboarding");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <OnboardingHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundOrgChartHome(): JSX.Element {
  const view = useScreenParameters("orgChart");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <OrgChartHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundAgentWorkflowHome(): JSX.Element {
  const view = useScreenParameters("agentWorkflow");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <AgentWorkflowHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundProfileHome(): JSX.Element {
  const fallback = useScreenParameters("profile");
  const view = useLiveView(fallback, loadLiveProfile);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <ProfileHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundRegistryHomeLegacy(): JSX.Element {
  const view = useScreenParameters("registry");
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <RegistryHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

function BoundSettingsHome(): JSX.Element {
  const fallback = useScreenParameters("settings");
  const view = useLiveView(fallback, loadLiveSettings);
  const bridge = useScreenActionBridge();
  return (
    <BoundShell status={bridge.runtime.status}>
      <SettingsHome
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

/** Pack agent detail — loads AgentDetailHome + pack catalog only on this route. */
export function BoundAgentDetailHome({
  agentId,
}: Readonly<{ agentId: string }>): JSX.Element {
  const bridge = useScreenActionBridge();
  const view = resolveAgentDetailView(agentId);
  return (
    <BoundShell status={bridge.runtime.status}>
      <AgentDetailHome
        agentId={agentId}
        view={view}
        onAction={bridge.onAction as (action: ScreenUiAction) => void}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

export function BoundSwarmCanvasHome({
  swarmId,
}: Readonly<{ swarmId: string }>): JSX.Element {
  return <BoundLiveSwarmCanvas swarmId={swarmId} />;
}

/**
 * Loads Host swarm draft by id and overlays real members onto canvas projection.
 * Menu /canvas still uses the static demo landing; this route is for live drafts.
 */
function BoundLiveSwarmCanvas({
  swarmId,
}: Readonly<{ swarmId: string }>): JSX.Element {
  const baseView = useScreenParameters("canvas");
  const bridge = useScreenActionBridge();
  const [liveView, setLiveView] = useState(baseView);
  const [loadNote, setLoadNote] = useState<string>(
    `Loading Host swarm ${swarmId}…`,
  );
  const [spineBusy, setSpineBusy] = useState(false);
  const [spineNote, setSpineNote] = useState<string | null>(null);
  const [spineSteps, setSpineSteps] = useState<
    readonly {
      id: string;
      agentId: string;
      status: string;
      humanGateRequired: boolean;
      artifactRef: string | null;
    }[]
  >([]);
  const [spineStatus, setSpineStatus] = useState<string | null>(null);
  const [spineApprovalId, setSpineApprovalId] = useState<string | null>(null);
  const [spineActions, setSpineActions] = useState<
    readonly { id: string; kind: string; label: string }[]
  >([]);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const { getSwarm } = await import("../../lib/api/product-swarms");
      const result = await getSwarm(swarmId);
      if (cancelled) return;
      if (!result.ok) {
        setLoadNote(result.message);
        setLiveView({
          ...baseView,
          swarmName: `Missing: ${swarmId}`,
          patternBadge: "Host draft not found",
          commonsSummary: "0 members · process-local façade",
          nodes: [],
          groups: [],
          edges: [],
          footerNote: result.message,
        });
        return;
      }
      const { swarm } = result;
      const memberNodes =
        swarm.members.length > 0
          ? swarm.members
          : swarm.nodes
              .filter((n) => n.agentId)
              .map((n) => ({
                nodeId: n.id,
                agentId: n.agentId ?? n.id,
                agentVersion: n.agentVersion ?? "current",
              }));
      const spineByAgent = new Map(
        (swarm.spine?.steps ?? []).map((s) => [s.agentId, s]),
      );
      const nodes = memberNodes.map((m, index) => {
        const agentId = m.agentId;
        const isGate =
          /judge|gate|verif|qa|compliance/i.test(agentId) ||
          /judge|gate|verif|qa|compliance/i.test(m.nodeId);
        const spineHit = spineByAgent.get(agentId);
        const phase1 = /orchestrator|planner|producer/i.test(agentId);
        return {
          id: m.nodeId || `node_${index}`,
          label: agentId,
          kind: (isGate ? "verifier" : "common") as
            | "common"
            | "verifier"
            | "supervisor"
            | "router"
            | "custom",
          versionLabel: m.agentVersion || "current",
          status: (
            spineHit?.status === "completed"
              ? "done"
              : spineHit?.status === "waiting_for_approval"
                ? "blocked"
                : spineHit?.status === "denied"
                  ? "failed"
                  : "idle"
          ) as
            | "idle"
            | "done"
            | "blocked"
            | "failed"
            | "running"
            | "complete",
          statusLabel: spineHit
            ? `Spine · ${spineHit.status}`
            : phase1
              ? "Phase-1 Intent & Planning"
              : "Draft member",
          metrics: spineHit
            ? `stub · ${spineHit.id}${spineHit.artifactRef ? ` · ${spineHit.artifactRef}` : ""}`
            : "Host draft · inspect on workflow diagram",
          linked: true,
        };
      });
      const edgeList = nodes.slice(0, -1).map((node, index) => ({
        id: `e-${node.id}-${nodes[index + 1]!.id}`,
        from: node.id,
        to: nodes[index + 1]!.id,
        label: "handoff",
        style: "solid" as const,
      }));
      const completedSteps =
        swarm.spine?.steps.filter((s) => s.status === "completed").length ?? 0;
      const totalSteps = swarm.spine?.steps.length ?? 0;
      const progressPercent =
        totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;
      setSpineSteps(swarm.spine?.steps ?? []);
      setSpineStatus(swarm.spine?.status ?? null);
      setSpineApprovalId(swarm.spine?.approvalId ?? null);
      setSpineActions(swarm.actions);
      setLiveView({
        ...baseView,
        viewMode: "inspect",
        swarmName: swarm.name,
        patternBadge: swarm.spine
          ? `Spine ${swarm.spine.workflowId} · stub · not production media`
          : swarm.patternRef
            ? `From Plan · pattern ${swarm.patternRef}`
            : `From Plan · ${swarm.status} · rev ${swarm.revision}`,
        commonsSummary: swarm.brief
          ? `${memberNodes.length} member(s) · brief ${swarm.brief.briefId.slice(0, 12)}… · ${swarm.brief.scaleProfile ?? "scale —"} / ${swarm.brief.archetype ?? "arch —"}`
          : `${memberNodes.length} member(s) · workflow diagram · draft ${swarm.id}`,
        instanceId: swarm.id,
        instanceStatus: swarm.spine?.status ?? swarm.status,
        instanceRevision: swarm.revision,
        sourceLabel: swarm.spine
          ? "Plan ACC · video spine stub"
          : "Plan ACC · AI-pick",
        fromCompose: true,
        nodes,
        groups: [],
        edges: edgeList,
        footerNote: swarm.spine
          ? `Live Host draft ${swarm.id} · spine ${swarm.spine.status} · ${swarm.spine.note}. Package always HITL.`
          : `Live Host draft ${swarm.id} · revision ${swarm.revision} · ${swarm.status}. Orchestration board · Agent Workflow style. Production fail-closed.`,
        runBar: {
          ...baseView.runBar,
          statusLabel: swarm.spine?.status ?? swarm.status,
          activeNodesLabel: swarm.spine
            ? `${totalSteps} spine steps · ${completedSteps} done`
            : `${memberNodes.length} agents (draft)`,
          progressLabel: swarm.spine
            ? swarm.spine.status === "waiting_for_approval"
              ? "Package waiting for human approval"
              : `Stub dry-run · ${progressPercent}%`
            : "Not run · inspect workflow",
          progressPercent,
        },
      });
      setLoadNote(
        `Loaded draft ${swarm.id}: ${swarm.name} (${memberNodes.length} member(s), rev ${swarm.revision})${
          swarm.spine ? ` · spine ${swarm.spine.status}` : ""
        }.`,
      );
    })();
    return () => {
      cancelled = true;
    };
  }, [baseView, swarmId, reloadToken]);

  const advanceSpine = async (): Promise<void> => {
    if (spineBusy) return;
    const action = spineActions.find((a) => a.kind === "run_spine_step");
    if (!action) {
      setSpineNote("No run_spine_step action — reload draft or re-materialize video brief.");
      setReloadToken((n) => n + 1);
      return;
    }
    setSpineBusy(true);
    setSpineNote("Advancing spine stub step…");
    try {
      const { runSpineStep } = await import("../../lib/api/product-swarms");
      const result = await runSpineStep(swarmId, action.id);
      if (!result.ok) {
        setSpineNote(result.message);
        return;
      }
      if (result.spine?.status === "waiting_for_approval") {
        setSpineNote(
          `Package gate open · approval ${result.approvalId ?? "—"} · stub · not production media`,
        );
      } else {
        setSpineNote(`Spine advanced · status ${result.spine?.status ?? "ok"}`);
      }
      setReloadToken((n) => n + 1);
    } finally {
      setSpineBusy(false);
    }
  };

  const decidePackage = async (decision: "approved" | "denied"): Promise<void> => {
    if (spineBusy) return;
    const action = spineActions.find((a) => a.kind === "decide_package");
    if (!action) {
      setSpineNote("No decide_package action — advance spine to package first.");
      setReloadToken((n) => n + 1);
      return;
    }
    setSpineBusy(true);
    try {
      const { decidePackageGate } = await import("../../lib/api/product-swarms");
      const result = await decidePackageGate(
        swarmId,
        action.id,
        decision,
        decision === "approved"
          ? "Operator approved package stub for inspection only"
          : "Operator denied package — fail closed",
      );
      if (!result.ok) {
        setSpineNote(result.message);
        return;
      }
      setSpineNote(`Package ${decision} · spine ${result.status}`);
      setReloadToken((n) => n + 1);
    } finally {
      setSpineBusy(false);
    }
  };

  return (
    <BoundShell status={bridge.runtime.status}>
      <p className="bound-swarm-canvas__banner" role="status">
        {loadNote}{" "}
        <a className="registry-home__linkish" href="/registry">
          ← Registry drafts
        </a>
      </p>
      {spineSteps.length > 0 ? (
        <div
          className="bound-swarm-canvas__spine"
          style={{
            margin: "0.5rem 1rem",
            padding: "0.75rem 1rem",
            border: "1px solid var(--border, #333)",
            borderRadius: 8,
            fontSize: "0.85rem",
          }}
        >
          <strong>Video spine (stub · not production media)</strong>
          {spineStatus ? (
            <span> · status <code>{spineStatus}</code></span>
          ) : null}
          {spineApprovalId ? (
            <span>
              {" "}
              · approval <code>{spineApprovalId}</code>
            </span>
          ) : null}
          {" · "}
          <a
            className="registry-home__linkish"
            href="/registry/agent-workflow?template=video.host.wf_video_spine_v1"
          >
            Open spine template
          </a>
          <ol style={{ margin: "0.5rem 0 0.75rem", paddingLeft: "1.25rem" }}>
            {spineSteps.map((s) => (
              <li key={s.id}>
                <code>{s.id}</code> · {s.agentId} · <em>{s.status}</em>
                {s.humanGateRequired ? " · human gate" : ""}
                {s.artifactRef ? ` · art ${s.artifactRef}` : ""}
              </li>
            ))}
          </ol>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <button
              disabled={spineBusy || spineStatus === "waiting_for_approval" || spineStatus === "completed" || spineStatus === "denied"}
              onClick={() => void advanceSpine()}
              type="button"
            >
              {spineBusy ? "…" : "Run next spine step"}
            </button>
            {spineStatus === "waiting_for_approval" ? (
              <>
                <button
                  disabled={spineBusy}
                  onClick={() => void decidePackage("approved")}
                  type="button"
                >
                  Approve package
                </button>
                <button
                  disabled={spineBusy}
                  onClick={() => void decidePackage("denied")}
                  type="button"
                >
                  Deny package
                </button>
              </>
            ) : null}
          </div>
          {spineNote ? (
            <p role="status" style={{ margin: "0.5rem 0 0" }}>
              {spineNote}
            </p>
          ) : null}
        </div>
      ) : null}
      <CanvasHome
        view={liveView}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

/**
 * Binds monitoring and approval projections on the client while keeping the
 * authenticated shell server-rendered.
 */
export function BoundMonitoringHome(): JSX.Element {
  const monitoringFallback = useScreenParameters("monitoring");
  const monitoring = useLiveView(monitoringFallback, loadLiveMonitoring);
  const approval = useScreenParameters("approval");
  const runtime = useInteractionRuntime();
  const bridge = useScreenActionBridge();
  const hostApprovalId =
    typeof approval.approval_id === "string" ? approval.approval_id : "";
  const hostApprovalEmpty =
    !hostApprovalId || hostApprovalId.includes("local") || hostApprovalId === "";
  const [showApprovalSamples, setShowApprovalSamples] =
    useState(hostApprovalEmpty);
  const approvalProjection: GeneratedJsonObject = showApprovalSamples
    ? buildSampleApprovalProjection()
    : approval;

  useEffect(() => {
    setShowApprovalSamples(hostApprovalEmpty);
  }, [hostApprovalEmpty]);

  return (
    <div className="operations-page responsive-stack">
      <InteractionStatusBar status={runtime.status} />
      <OperationsConsole />
      <MonitoringHome
        view={monitoring}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
      <section
        aria-label="Approvals and rollouts samples control"
        className="operations-approvals-wrap"
      >
        <div className="page-title-row operations-approvals-wrap__head">
          <h2 className="operations-approvals-wrap__title">
            Approvals &amp; Rollouts
          </h2>
          <SamplesToggle
            show={showApprovalSamples}
            onToggle={() => setShowApprovalSamples((v) => !v)}
            labelShow="Show sample approval gate"
            labelHide="Hide sample approval gate"
          />
        </div>
        {showApprovalSamples ? (
          <SamplesBanner>
            Sample approval gate on · decisions disabled · not a Host approval
            id. Toggle ▦ to hide.
          </SamplesBanner>
        ) : null}
        <ApprovalGateScreen
          projection={approvalProjection}
          onAction={(action) => {
            if (showApprovalSamples) {
              runtime.setInfo(
                "Sample approval actions are display-only. Load a live Host approval id to decide.",
              );
              return;
            }
            const id = typeof action.id === "string" ? action.id : "";
            const kind = typeof action.kind === "string" ? action.kind : "";
            if (kind.includes("approve") || id.includes("approve")) {
              void runtime.decideApproval(
                String(approval.approval_id ?? ""),
                "approved",
                "Approved from returned gate action.",
              );
              return;
            }
            if (kind.includes("deny") || id.includes("deny")) {
              void runtime.decideApproval(
                String(approval.approval_id ?? ""),
                "denied",
                "Denied from returned gate action.",
              );
              return;
            }
            runtime.setInfo(
              `Action “${id || kind || "unknown"}” invoked. Load a live approval id in Operations Console to submit governed decisions.`,
            );
          }}
          onEvidence={() =>
            runtime.setInfo("Evidence reference selected (opaque id only).")
          }
          onReference={() =>
            runtime.setInfo("Reference resolved for display only.")
          }
        />
      </section>
    </div>
  );
}
