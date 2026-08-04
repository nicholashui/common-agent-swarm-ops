"use client";

/**
 * @duty OperationsConsole — live control-plane operator panel
 * @role Inspect runs, load approvals, submit decisions, refresh context via /api/v1 runtime.
 * @controls Refresh button; run id input + inspect; approval id, decision select, reason textarea, submit.
 * @must Use interaction runtime (idempotent decisions); show InteractionStatusBar.
 * @mustnot Store API keys; approve without host gate/action path.
 * @redesign docs/frontend_redesign/common-style.html · ui_09_monitoring.md
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
  const [legacyOpen, setLegacyOpen] = useState(false);

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
    <section
      aria-label="Live operations console"
      className="operations-console"
    >
      <header className="operations-console__header">
        <div className="operations-console__intro">
          <p className="eyebrow">OPERATIONS · LIVE API</p>
          <h1 className="operations-console__title">Control-plane actions</h1>
          <p className="lede operations-console__lede">
            Inspect runs, load approval gates, and submit decisions through the
            Host API. Same-origin <code className="operations-console__code">/api/v1</code>
            {" · "}fail-closed without eligible action references.
          </p>
        </div>
        <div className="operations-console__header-actions">
          <span className="operations-console__live" role="status">
            <span aria-hidden="true" className="operations-console__live-dot" />
            Live · Host session
          </span>
          <button
            className="operations-console__btn operations-console__btn--primary"
            disabled={runtime.busy}
            onClick={() => void runtime.refreshContext()}
            type="button"
          >
            Refresh context
          </button>
        </div>
      </header>

      <InteractionStatusBar status={runtime.status} />

      <div className="operations-console__grid">
        <form
          className="operations-console__card"
          onSubmit={(e) => void onInspect(e)}
        >
          <div className="operations-console__card-head">
            <span className="operations-console__card-kicker">RUN</span>
            <h2>Inspect run</h2>
            <p>Load redacted run + graph projection by opaque id.</p>
          </div>
          <label className="operations-console__field">
            <span>Run ID</span>
            <input
              maxLength={100}
              onChange={(event) => setRunId(event.target.value)}
              placeholder="run-…"
              required
              value={runId}
            />
          </label>
          <button
            className="operations-console__btn operations-console__btn--primary"
            disabled={runtime.busy}
            type="submit"
          >
            Load run + graph
          </button>
        </form>

        <form
          className="operations-console__card"
          onSubmit={(e) => void onLoadApproval(e)}
        >
          <div className="operations-console__card-head">
            <span className="operations-console__card-kicker">GATE</span>
            <h2>Load approval gate</h2>
            <p>Fetch gate preview before recording a decision.</p>
          </div>
          <label className="operations-console__field">
            <span>Approval ID</span>
            <input
              maxLength={100}
              onChange={(event) => setApprovalId(event.target.value)}
              placeholder="approval-…"
              required
              value={approvalId}
            />
          </label>
          <button
            className="operations-console__btn operations-console__btn--primary"
            disabled={runtime.busy}
            type="submit"
          >
            Load gate
          </button>
        </form>

        <form
          className="operations-console__card"
          onSubmit={(e) => void onDecide(e)}
        >
          <div className="operations-console__card-head">
            <span className="operations-console__card-kicker">DECISION</span>
            <h2>Submit decision</h2>
            <p>Idempotent approve/deny · Host retains reason.</p>
          </div>
          <label className="operations-console__field">
            <span>Decision</span>
            <select
              onChange={(event) =>
                setDecision(event.target.value as "approved" | "denied")
              }
              value={decision}
            >
              <option value="approved">Approve</option>
              <option value="denied">Deny</option>
            </select>
          </label>
          <label className="operations-console__field">
            <span>Reason</span>
            <textarea
              maxLength={2000}
              onChange={(event) => setReason(event.target.value)}
              required
              rows={3}
              value={reason}
            />
          </label>
          <button
            className="operations-console__btn operations-console__btn--primary"
            disabled={runtime.busy || approvalId.trim().length === 0}
            type="submit"
          >
            Record decision
          </button>
        </form>
      </div>

      <div className="operations-console__legacy">
        <button
          aria-expanded={legacyOpen}
          className="operations-console__legacy-toggle"
          onClick={() => setLegacyOpen((open) => !open)}
          type="button"
        >
          <span>
            <strong>Full operator console</strong>
            <span className="operations-console__legacy-hint">
              Extended inspect / gate forms (same Host contracts)
            </span>
          </span>
          <span aria-hidden="true">{legacyOpen ? "⌃" : "⌄"}</span>
        </button>
        {legacyOpen ? (
          <div className="operations-console__legacy-body">
            <OperatorConsole />
          </div>
        ) : null}
      </div>
    </section>
  );
}
