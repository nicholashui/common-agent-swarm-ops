/**
 * Screen UI action bridge: classify and perform real local/API intents.
 * Presentation homes emit ScreenUiAction; BoundScreenHome performs them.
 * Governed mutations without host action refs fail closed (honest feedback).
 */

import {
  proposeAgentImprovement,
  startAgentRollout,
} from "../api/product-commons";
import type { InteractionRuntime } from "./interaction-runtime";

export type ScreenUiAction =
  | { readonly kind: "feedback"; readonly message: string }
  | { readonly kind: "local.pause_swarm"; readonly swarmId: string }
  | { readonly kind: "local.layout"; readonly detail?: string }
  | { readonly kind: "local.save_prefs"; readonly screen: string; readonly summary: string }
  | { readonly kind: "local.mark_read"; readonly ids: readonly string[] }
  | { readonly kind: "knowledge.search"; readonly query: string }
  | { readonly kind: "eval.run_campaign" }
  | {
      readonly kind: "canvas.run";
      readonly workflowId?: string;
      readonly version?: string;
    }
  | { readonly kind: "canvas.dispatch"; readonly runId: string }
  | { readonly kind: "context.refresh" }
  | { readonly kind: "run.inspect"; readonly runId: string }
  | { readonly kind: "approval.load"; readonly approvalId: string }
  | {
      readonly kind: "approval.decide";
      readonly approvalId: string;
      readonly value: "approved" | "denied";
      readonly reason: string;
    }
  | { readonly kind: "topology.load"; readonly workflowId: string }
  | {
      readonly kind: "commons.propose";
      readonly agentId: string;
      readonly summary?: string;
    }
  | {
      readonly kind: "commons.rollout_ab";
      readonly agentId: string;
      readonly baselineVersion?: string;
      readonly candidateVersion?: string;
      readonly summary?: string;
    }
  | {
      readonly kind: "commons.rollout_safe";
      readonly agentId: string;
      readonly baselineVersion?: string;
      readonly candidateVersion?: string;
      readonly summary?: string;
    }
  | {
      readonly kind: "governed.fail_closed";
      readonly message: string;
      readonly actionHint?: string;
    };

/** Messages that previously faked authority — always fail closed when bridged. */
const GOVERNED_PATTERNS: readonly RegExp[] = [
  /requires\s+an?\s+authorized/i,
  /requires\s+authorized/i,
  /authorized\s+(projection|action|export|cancel|pin|graph|compose|template|settings|governance|eval|rollout|assist)/i,
  /merge\s+requires/i,
  /does not publish/i,
  /never activate production/i,
  /proposal\s*\+\s*approval/i,
  /canary.*rollback/i,
  /action reference/i,
];

export function isGovernedStubMessage(message: string): boolean {
  return GOVERNED_PATTERNS.some((pattern) => pattern.test(message));
}

/**
 * Map free-text announce stubs into structured actions so Homes can call
 * `onAction(classifyAnnounce(msg))` without inventing host authority.
 */
export function classifyAnnounce(message: string): ScreenUiAction {
  const m = message.trim();
  if (m.length === 0) {
    return { kind: "feedback", message: "Empty action." };
  }
  if (/auto\s*layout|layout is local/i.test(m)) {
    return { kind: "local.layout", detail: m };
  }
  if (/marked?\s+.*read|mark all read/i.test(m)) {
    // Prefer structured `local.mark_read` from Homes when ids are known;
    // free-text announce remains honest feedback.
    return { kind: "feedback", message: m };
  }
  if (/preferences saved locally|saved locally/i.test(m)) {
    return { kind: "local.save_prefs", screen: "session", summary: m };
  }
  if (/batch eval|run evaluation|eval campaign/i.test(m)) {
    return { kind: "eval.run_campaign" };
  }
  if (/run command|graph action|create run/i.test(m) && /run/i.test(m)) {
    return { kind: "canvas.run" };
  }
  if (isGovernedStubMessage(m)) {
    return {
      kind: "governed.fail_closed",
      message: m,
      actionHint:
        "Host must return an action reference before the browser may mutate governed state.",
    };
  }
  return { kind: "feedback", message: m };
}

export async function performScreenAction(
  runtime: InteractionRuntime,
  action: ScreenUiAction,
): Promise<boolean> {
  switch (action.kind) {
    case "feedback":
      runtime.setInfo(action.message);
      return true;
    case "local.pause_swarm":
      runtime.patchScreen("dashboard", {
        footerNote: `Session pause toggle for ${action.swarmId} · ${new Date().toISOString()}`,
      });
      runtime.setSuccess(`Swarm ${action.swarmId}: pause state updated in session.`);
      return true;
    case "local.layout":
      runtime.setSuccess(action.detail ?? "Layout applied locally (no host mutation).");
      return true;
    case "local.save_prefs":
      runtime.setSuccess(action.summary);
      return true;
    case "local.mark_read":
      runtime.setSuccess(
        action.ids.length === 0
          ? "No notifications to mark."
          : `Marked ${action.ids.length} notification(s) read in session.`,
      );
      return true;
    case "knowledge.search":
      return runtime.retrieveMemory(action.query);
    case "eval.run_campaign":
      return runtime.runEvaluation({});
    case "canvas.run":
      return runtime.createAndDispatchRun(
        action.workflowId ?? "default",
        action.version ?? "1",
      );
    case "canvas.dispatch":
      return runtime.dispatchRun(action.runId);
    case "context.refresh":
      return runtime.refreshContext();
    case "run.inspect":
      return runtime.inspectRun(action.runId);
    case "approval.load":
      return runtime.loadApproval(action.approvalId);
    case "approval.decide":
      return runtime.decideApproval(action.approvalId, action.value, action.reason);
    case "topology.load":
      return runtime.loadTopology(action.workflowId);
    case "commons.propose": {
      runtime.setInfo(`Submitting proposal for ${action.agentId}…`);
      const result = await proposeAgentImprovement(action.agentId, {
        summary: action.summary,
      });
      if (!result.ok) {
        runtime.setError(result.message);
        return false;
      }
      runtime.setSuccess(
        `Proposal ${result.proposalId} ${result.status} for ${result.targetId}.`,
      );
      return true;
    }
    case "commons.rollout_ab": {
      runtime.setInfo(`Starting A/B canary for ${action.agentId}…`);
      const result = await startAgentRollout(action.agentId, {
        type: "ab_test",
        baselineVersion: action.baselineVersion,
        candidateVersion: action.candidateVersion,
        summary: action.summary,
      });
      if (!result.ok) {
        runtime.setError(result.message);
        return false;
      }
      runtime.setSuccess(
        `A/B canary ${result.rolloutId} ${result.status} for ${result.agentId} ` +
          `(${result.candidateVersion} vs ${result.baselineVersion}). ` +
          "Sandbox only — production activation remains false.",
      );
      return true;
    }
    case "commons.rollout_safe": {
      runtime.setInfo(`Starting safe rollout canary for ${action.agentId}…`);
      const result = await startAgentRollout(action.agentId, {
        type: "safe_rollout",
        baselineVersion: action.baselineVersion,
        candidateVersion: action.candidateVersion,
        summary: action.summary,
      });
      if (!result.ok) {
        runtime.setError(result.message);
        return false;
      }
      runtime.setSuccess(
        `Safe rollout canary ${result.rolloutId} ${result.status} for ${result.agentId}. ` +
          "Sandbox only — production activation remains false.",
      );
      return true;
    }
    case "governed.fail_closed": {
      const hint = action.actionHint
        ? ` ${action.actionHint}`
        : " Provide a host action reference; the browser will not invent one.";
      runtime.setError(`${action.message}${hint}`);
      return false;
    }
    default: {
      const _exhaustive: never = action;
      void _exhaustive;
      runtime.setError("Unknown screen action.");
      return false;
    }
  }
}
