"use client";

import { FormEvent, useMemo, useState } from "react";

import {
  ActionPreview,
  ApprovalDecision,
  ApprovalGate,
  ApprovalValue,
  GraphState,
  OperatorApi,
  RunProjection,
  createOperatorApi,
  operatorCorrection,
} from "../lib/contracts";

interface InspectionState {
  readonly run: RunProjection;
  readonly graph: GraphState;
}

export function OperatorConsole(): JSX.Element {
  const api = useMemo<OperatorApi>(() => createOperatorApi(), []);
  const [runId, setRunId] = useState("");
  const [approvalId, setApprovalId] = useState("");
  const [reason, setReason] = useState("");
  const [value, setValue] = useState<ApprovalValue>("approved");
  const [inspection, setInspection] = useState<InspectionState | null>(null);
  const [gate, setGate] = useState<ApprovalGate | null>(null);
  const [decision, setDecision] = useState<ApprovalDecision | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function inspectRun(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true); setError(null); setDecision(null);
    try {
      const [run, graph] = await Promise.all([api.getRun(runId), api.getGraphState(runId)]);
      setInspection({ run, graph });
    } catch (caught: unknown) { setError(operatorCorrection(caught)); }
    finally { setBusy(false); }
  }

  async function loadGate(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true); setError(null);
    try { setGate(await api.getApprovalGate(approvalId)); }
    catch (caught: unknown) { setError(operatorCorrection(caught)); }
    finally { setBusy(false); }
  }

  async function decide(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true); setError(null);
    try { setDecision(await api.submitApprovalDecision(approvalId, value, reason)); }
    catch (caught: unknown) { setError(operatorCorrection(caught)); }
    finally { setBusy(false); }
  }

  return <>
    <header><h1>Workflow operations</h1><p>Inspect redacted run state, review action previews, and record approval decisions.</p></header>
    {error ? <p className="error" role="alert">{error}</p> : null}
    <section><h2>Run and graph inspection</h2><form onSubmit={inspectRun}><label>Run ID<input required maxLength={100} value={runId} onChange={(event) => setRunId(event.target.value)} /></label><button disabled={busy}>Inspect redacted state</button></form>{inspection ? <InspectionView inspection={inspection} /> : null}</section>
    <section><h2>Approval decision</h2><form onSubmit={loadGate}><label>Approval ID<input required maxLength={100} value={approvalId} onChange={(event) => setApprovalId(event.target.value)} /></label><button disabled={busy}>Load action preview</button></form>{gate ? <ApprovalForm gate={gate} value={value} reason={reason} busy={busy} setValue={setValue} setReason={setReason} onSubmit={decide} /> : null}{decision ? <DecisionView decision={decision} /> : null}</section>
  </>;
}

interface ApprovalFormProps {
  readonly gate: ApprovalGate;
  readonly value: ApprovalValue;
  readonly reason: string;
  readonly busy: boolean;
  readonly setValue: (value: ApprovalValue) => void;
  readonly setReason: (reason: string) => void;
  readonly onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}

export function InspectionView({ inspection }: { readonly inspection: InspectionState }): JSX.Element {
  return <div><h3>Redacted run projection</h3><Details entries={[["Run", inspection.run.run_id], ["Workflow", `${inspection.run.workflow_id}@${inspection.run.workflow_version}`], ["Status", inspection.run.status], ["Engine", inspection.run.engine], ["Updated", inspection.run.updated_at], ["Failure", inspection.run.failure_code ?? "None"]]} /><PreviewList previews={[inspection.run.action_preview, ...inspection.graph.action_previews].filter((item): item is ActionPreview => item !== null)} /><h3>Graph state</h3><Details entries={[["Graph", inspection.graph.graph_id ?? "Not available"], ["Thread", inspection.graph.graph_thread_id ?? "Not available"], ["Effects", String(inspection.graph.tool_effects.length)]]} /><ul>{inspection.graph.tool_effects.map((effect) => <li key={effect.effect_digest}>{effect.adapter_id}: {effect.outcome} ({effect.reversible ? "reversible" : "irreversible"})</li>)}</ul></div>;
}

export function ApprovalForm({ gate, value, reason, busy, setValue, setReason, onSubmit }: ApprovalFormProps): JSX.Element {
  return <form onSubmit={onSubmit}><h3>Preview before decision</h3><Details entries={[["Run", gate.run_id], ["Risk tier", gate.risk_tier], ["Status", gate.gate_status]]} /><PreviewList previews={[gate.action_preview]} /><label>Decision<select value={value} onChange={(event) => setValue(event.target.value as ApprovalValue)}><option value="approved">Approve</option><option value="denied">Deny</option></select></label><label>Reason<textarea maxLength={2000} value={reason} onChange={(event) => setReason(event.target.value)} /></label><p className="meta">A submitted reason is retained by the Host. Reasons must contain 1–1,000 characters to be valid; denial keeps the run paused.</p><button disabled={busy}>Record decision</button></form>;
}

export function DecisionView({ decision }: { readonly decision: ApprovalDecision }): JSX.Element {
  return <div><h3>Recorded decision</h3><Details entries={[["Decision", decision.selected_value], ["Gate status", decision.gate_status], ["Reason valid", String(decision.reason_is_valid)], ["Value valid", String(decision.value_is_valid)], ["Resumed", String(decision.resumed)], ["Submitted", decision.submitted_at]]} /><PreviewList previews={[decision.action_preview]} /></div>;
}

export function PreviewList({ previews }: { readonly previews: readonly ActionPreview[] }): JSX.Element {
  return <>{previews.length > 0 ? <div>{previews.map((preview) => <section key={`${preview.action_id}:${preview.emitted_at}`}><h4>Action preview: {preview.summary}</h4><Details entries={[["Intended effect", preview.intended_effect], ["Emitted", preview.emitted_at], ["Rollback", preview.rollback_preview ?? "Not declared"], ["Confidence", preview.confidence?.toString() ?? "Not supplied"], ["Uncertainty", preview.uncertainty ?? "Not supplied"], ["Correction", preview.correction_control ?? "Not supplied"]]} /><p>Supporting evidence: {preview.supporting_evidence.join(", ") || "Not supplied"}</p></section>)}</div> : <p className="meta">No action preview is available for this redacted projection.</p>}</>;
}

export function Details({ entries }: { readonly entries: readonly (readonly [string, string])[] }): JSX.Element {
  return <dl>{entries.map(([term, description]) => <><dt key={`${term}-term`}>{term}</dt><dd key={`${term}-value`}>{description}</dd></>)}</dl>;
}
