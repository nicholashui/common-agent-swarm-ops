"use client";

/**
 * @duty OperationsConsole — live control-plane operator panel
 * @role Inspect runs, load approvals, submit decisions, refresh context via /api/v1 runtime.
 * @controls Refresh button; run id input + inspect; approval id, decision select, reason textarea, submit.
 * @must Use interaction runtime (idempotent decisions); show InteractionStatusBar.
 * @mustnot Store API keys; approve without host gate/action path.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.4
 *
 * Real operations surface: live operator API console plus context refresh.
 * Uses browser fetch to /api/v1 (proxied when BACKEND_API_ORIGIN is set).
 */
import { FormEvent, useState } from "react";

import { useInteractionRuntime } from "../lib/ui/interaction-runtime";
import { InteractionStatusBar } from "./ui/InteractionStatusBar";
import { OperatorConsole } from "./OperatorConsole";

export function OperationsConsole(): JSX.Element {
  const runtime = useInteractionRuntime();
  const [runId, setRunId] = useState("");
  const [approvalId, setApprovalId] = useState("");
  const [reason, setReason] = useState("Operator reviewed evidence.");
  const [decision, setDecision] = useState<"approved" | "denied">("approved");

  const onInspect = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    await runtime.inspectRun(runId);
  };

  const onLoadApproval = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    await runtime.loadApproval(approvalId);
  };

  const onDecide = async (event: FormEvent): Promise<void> => {
    event.preventDefault();
    await runtime.decideApproval(approvalId, decision, reason);
  };

  return (
    <section aria-label="Live operations console" className="operations-console">
      <header className="operations-console__header">
        <div>
          <p className="eyebrow">OPERATIONS · LIVE API</p>
          <h1>Control-plane actions</h1>
          <p className="lede">
            Inspect runs, load approval gates, and submit decisions through the real
            Host API. Requires backend reachability via same-origin <code>/api/v1</code>.
          </p>
        </div>
        <button
          className="operations-console__action"
          disabled={runtime.busy}
          onClick={() => void runtime.refreshContext()}
          type="button"
        >
          Refresh authenticated context
        </button>
      </header>

      <InteractionStatusBar status={runtime.status} />

      <div className="operations-console__grid">
        <form className="operations-console__card" onSubmit={(e) => void onInspect(e)}>
          <h2>Inspect run</h2>
          <label>
            Run ID
            <input
              maxLength={100}
              onChange={(event) => setRunId(event.target.value)}
              placeholder="run-…"
              required
              value={runId}
            />
          </label>
          <button disabled={runtime.busy} type="submit">
            Load run + graph
          </button>
        </form>

        <form className="operations-console__card" onSubmit={(e) => void onLoadApproval(e)}>
          <h2>Load approval gate</h2>
          <label>
            Approval ID
            <input
              maxLength={100}
              onChange={(event) => setApprovalId(event.target.value)}
              placeholder="approval-…"
              required
              value={approvalId}
            />
          </label>
          <button disabled={runtime.busy} type="submit">
            Load gate
          </button>
        </form>

        <form className="operations-console__card" onSubmit={(e) => void onDecide(e)}>
          <h2>Submit decision</h2>
          <label>
            Decision
            <select
              onChange={(event) => setDecision(event.target.value as "approved" | "denied")}
              value={decision}
            >
              <option value="approved">Approve</option>
              <option value="denied">Deny</option>
            </select>
          </label>
          <label>
            Reason
            <textarea
              maxLength={2000}
              onChange={(event) => setReason(event.target.value)}
              required
              rows={3}
              value={reason}
            />
          </label>
          <button disabled={runtime.busy || approvalId.trim().length === 0} type="submit">
            Record decision
          </button>
        </form>
      </div>

      <div className="operations-console__legacy">
        <h2>Full operator console</h2>
        <OperatorConsole />
      </div>
    </section>
  );
}
