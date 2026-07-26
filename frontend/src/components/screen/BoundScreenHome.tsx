"use client";

import type { ReactNode } from "react";

import { AgentDetailHome } from "../AgentDetailHome";
import { ActivityHome } from "../ActivityHome";
import { ApprovalGateScreen } from "../ApprovalRolloutScreens";
import { ApiPortalHome } from "../ApiPortalHome";
import { AuditHome } from "../AuditHome";
import { BlueprintsHome } from "../BlueprintsHome";
import { CanvasHome } from "../CanvasHome";
import { CollaborationHome } from "../CollaborationHome";
import { ComposerHome } from "../ComposerHome";
import { CostsHome } from "../CostsHome";
import { DashboardHome } from "../DashboardHome";
import { EvalHome } from "../EvalHome";
import { KnowledgeHome } from "../KnowledgeHome";
import { MonitoringHome } from "../MonitoringHome";
import { MobileHome } from "../MobileHome";
import { NotificationsHome } from "../NotificationsHome";
import { OnboardingHome } from "../OnboardingHome";
import { ProfileHome } from "../ProfileHome";
import { RegistryHome } from "../RegistryHome";
import { SettingsHome } from "../SettingsHome";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";
import { resolveAgentDetailView } from "../../lib/projections/agent-detail-landing";
import { useInteractionRuntime } from "../../lib/ui/interaction-runtime";
import { useScreenActionBridge } from "../../lib/ui/use-screen-action";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";
import { OperationsConsole } from "../OperationsConsole";

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

/**
 * Binds a serializable screen key to its client-side projection hook and
 * presentation home. Server pages must not pass component functions as props.
 * Every bound home receives the real action bridge (API + session + fail-closed).
 */
export function BoundScreenHome({ screen }: Readonly<{ screen: BoundScreenKey }>): JSX.Element {
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
      return <BoundRegistryHome />;
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
        onSearch={(query) => void bridge.onAction({ kind: "knowledge.search", query })}
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

function BoundRegistryHome(): JSX.Element {
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

/** Binds the route parameter and pack-backed agent settings on the client. */
export function BoundAgentDetailHome({ agentId }: Readonly<{ agentId: string }>): JSX.Element {
  const bridge = useScreenActionBridge();
  const view = resolveAgentDetailView(agentId);
  return (
    <BoundShell status={bridge.runtime.status}>
      <AgentDetailHome
        agentId={agentId}
        view={view}
        onAction={bridge.onAction}
        statusMessage={bridge.statusMessage}
      />
    </BoundShell>
  );
}

/** Binds stored canvas parameters for the canonical swarm canvas route. */
export function BoundSwarmCanvasHome({ swarmId }: Readonly<{ swarmId: string }>): JSX.Element {
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
        onEvidence={() => runtime.setInfo("Evidence reference selected (opaque id only).")}
        onReference={() => runtime.setInfo("Reference resolved for display only.")}
      />
    </div>
  );
}
