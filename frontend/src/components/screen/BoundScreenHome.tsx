"use client";

/**
 * @duty BoundScreenHome — screen binder with code-split Homes
 * Each Home is next/dynamic so a route only downloads the active screen chunk
 * instead of one 6MB+ all-homes client graph.
 */
import type { ComponentType, ReactNode } from "react";
import dynamic from "next/dynamic";

import { useScreenParameters } from "../../lib/projections/use-screen-parameters";
import { resolveAgentDetailView } from "../../lib/projections/agent-detail-landing";
import { useInteractionRuntime } from "../../lib/ui/interaction-runtime";
import { useScreenActionBridge } from "../../lib/ui/use-screen-action";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";

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
  const view = useScreenParameters("blueprints");
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
  const view = useScreenParameters("canvas");
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
  const view = useScreenParameters("collaboration");
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
  const view = useScreenParameters("costs");
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
  const view = useScreenParameters("dashboard");
  const bridge = useScreenActionBridge();
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
  const view = useScreenParameters("knowledge");
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
  const view = useScreenParameters("mobile");
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
  const view = useScreenParameters("notifications");
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

function BoundProfileHome(): JSX.Element {
  const view = useScreenParameters("profile");
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
  const view = useScreenParameters("settings");
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
  void swarmId;
  const view = useScreenParameters("canvas");
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

/**
 * Binds monitoring and approval projections on the client while keeping the
 * authenticated shell server-rendered.
 */
export function BoundMonitoringHome(): JSX.Element {
  const monitoring = useScreenParameters("monitoring");
  const approval = useScreenParameters("approval");
  const runtime = useInteractionRuntime();
  const bridge = useScreenActionBridge();

  return (
    <div className="responsive-stack">
      <InteractionStatusBar status={runtime.status} />
      <OperationsConsole />
      <MonitoringHome
        view={monitoring}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
      <ApprovalGateScreen
        projection={approval}
        onAction={(action) => {
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
    </div>
  );
}
