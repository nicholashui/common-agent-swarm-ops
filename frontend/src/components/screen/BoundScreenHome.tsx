"use client";

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
import { LOCAL_PREVIEW_HANDLERS } from "../../lib/projections/local-preview";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

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

function BoundActivityHome(): JSX.Element {
  const view = useScreenParameters("activity");
  return <ActivityHome view={view} />;
}

function BoundApiPortalHome(): JSX.Element {
  const view = useScreenParameters("apiPortal");
  return <ApiPortalHome view={view} />;
}

function BoundAuditHome(): JSX.Element {
  const view = useScreenParameters("audit");
  return <AuditHome view={view} />;
}

function BoundBlueprintsHome(): JSX.Element {
  const view = useScreenParameters("blueprints");
  return <BlueprintsHome view={view} />;
}

function BoundCanvasHome(): JSX.Element {
  const view = useScreenParameters("canvas");
  return <CanvasHome view={view} />;
}

function BoundCollaborationHome(): JSX.Element {
  const view = useScreenParameters("collaboration");
  return <CollaborationHome view={view} />;
}

function BoundComposerHome(): JSX.Element {
  const view = useScreenParameters("composer");
  return <ComposerHome view={view} />;
}

function BoundCostsHome(): JSX.Element {
  const view = useScreenParameters("costs");
  return <CostsHome view={view} />;
}

function BoundDashboardHome(): JSX.Element {
  const view = useScreenParameters("dashboard");
  return <DashboardHome view={view} />;
}

function BoundEvalHome(): JSX.Element {
  const view = useScreenParameters("eval");
  return <EvalHome view={view} />;
}

function BoundKnowledgeHome(): JSX.Element {
  const view = useScreenParameters("knowledge");
  return <KnowledgeHome view={view} />;
}

function BoundMobileHome(): JSX.Element {
  const view = useScreenParameters("mobile");
  return <MobileHome view={view} />;
}

function BoundNotificationsHome(): JSX.Element {
  const view = useScreenParameters("notifications");
  return <NotificationsHome view={view} />;
}

function BoundOnboardingHome(): JSX.Element {
  const view = useScreenParameters("onboarding");
  return <OnboardingHome view={view} />;
}

function BoundProfileHome(): JSX.Element {
  const view = useScreenParameters("profile");
  return <ProfileHome view={view} />;
}

function BoundRegistryHome(): JSX.Element {
  const view = useScreenParameters("registry");
  return <RegistryHome view={view} />;
}

function BoundSettingsHome(): JSX.Element {
  const view = useScreenParameters("settings");
  return <SettingsHome view={view} />;
}

/** Binds the route parameter and stored agent detail projection on the client. */
export function BoundAgentDetailHome({ agentId }: Readonly<{ agentId: string }>): JSX.Element {
  const view = useScreenParameters("agentDetail");
  return <AgentDetailHome agentId={agentId} view={view} />;
}

/** Binds stored canvas parameters for the canonical swarm canvas route. */
export function BoundSwarmCanvasHome({ swarmId }: Readonly<{ swarmId: string }>): JSX.Element {
  void swarmId;
  const view = useScreenParameters("canvas");
  return <CanvasHome view={view} />;
}

/**
 * Binds monitoring and approval projections on the client while keeping the
 * authenticated shell server-rendered.
 */
export function BoundMonitoringHome(): JSX.Element {
  const monitoring = useScreenParameters("monitoring");
  const approval = useScreenParameters("approval");

  return (
    <div className="responsive-stack">
      <MonitoringHome view={monitoring} />
      <ApprovalGateScreen projection={approval} {...LOCAL_PREVIEW_HANDLERS} />
    </div>
  );
}
