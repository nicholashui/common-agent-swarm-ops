export interface ActionPreview {
  readonly action_id: string;
  readonly summary: string;
  readonly intended_effect: string;
  readonly emitted_at: string;
  readonly rollback_preview: string | null;
  readonly supporting_evidence: readonly string[];
  readonly confidence: number | null;
  readonly uncertainty: string | null;
  readonly correction_control: string | null;
}

export interface RunProjection {
  readonly run_id: string;
  readonly workflow_id: string;
  readonly workflow_version: string;
  readonly status: string;
  readonly engine: string;
  readonly correlation_id: string;
  readonly updated_at: string;
  readonly failure_code: string | null;
  readonly action_preview: ActionPreview | null;
}

export interface ToolEffect {
  readonly adapter_id: string;
  readonly outcome: string;
  readonly effect_digest: string;
  readonly completed_at: string;
  readonly reversible: boolean;
  readonly compensation_reference: string | null;
}

export interface GraphState {
  readonly run_id: string;
  readonly status: string;
  readonly engine: string;
  readonly graph_id: string | null;
  readonly graph_thread_id: string | null;
  readonly updated_at: string;
  readonly failure_code: string | null;
  readonly tool_effects: readonly ToolEffect[];
  readonly action_previews: readonly ActionPreview[];
}

export interface ApprovalGate {
  readonly approval_id: string;
  readonly run_id: string;
  readonly risk_tier: string;
  readonly gate_status: string;
  readonly created_at: string;
  readonly action_preview: ActionPreview;
}

export type ApprovalValue = "approved" | "denied";

export interface ApprovalDecision {
  readonly approval_id: string;
  readonly run_id: string;
  readonly actor_id: string;
  readonly selected_value: string;
  readonly reason_is_valid: boolean;
  readonly value_is_valid: boolean;
  readonly resumed: boolean;
  readonly gate_status: string;
  readonly submitted_at: string;
  readonly action_preview: ActionPreview;
}

export interface ApiErrorDetail {
  readonly code: string;
  readonly correlationId: string | null;
  readonly retryable: boolean;
  readonly status: number;
}

export class OperatorApiError extends Error {
  public constructor(message: string, public readonly detail: ApiErrorDetail) {
    super(message);
    this.name = "OperatorApiError";
  }
}

export interface FetchLike {
  (input: RequestInfo | URL, init?: RequestInit): Promise<Response>;
}

export interface OperatorApi {
  getRun(runId: string): Promise<RunProjection>;
  getGraphState(runId: string): Promise<GraphState>;
  getApprovalGate(approvalId: string): Promise<ApprovalGate>;
  submitApprovalDecision(approvalId: string, value: ApprovalValue, reason: string): Promise<ApprovalDecision>;
}

interface ClientOptions {
  readonly baseUrl?: string;
  readonly fetchImpl?: FetchLike;
}

type JsonRecord = Record<string, unknown>;
type JsonParser<T> = (value: unknown) => T;

const API_PREFIX = "/api/v1/";

export function createOperatorApi(options: ClientOptions = {}): OperatorApi {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
  const baseUrl = normalizeBaseUrl(options.baseUrl ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "");
  return {
    getRun: (runId: string): Promise<RunProjection> => request(fetchImpl, baseUrl, runPath(runId), undefined, parseRunProjection),
    getGraphState: (runId: string): Promise<GraphState> => request(fetchImpl, baseUrl, `${runPath(runId)}/graph-state`, undefined, parseGraphState),
    getApprovalGate: (approvalId: string): Promise<ApprovalGate> => request(fetchImpl, baseUrl, approvalPath(approvalId), undefined, parseApprovalGate),
    submitApprovalDecision: (approvalId: string, value: ApprovalValue, reason: string): Promise<ApprovalDecision> => request(
      fetchImpl, baseUrl, `${approvalPath(approvalId)}/decision`, { method: "POST", body: JSON.stringify({ selected_value: value, reason }) }, parseApprovalDecision,
    ),
  };
}

export function operatorCorrection(error: unknown): string {
  if (!(error instanceof OperatorApiError)) return "The operator request could not be completed. Retry after checking the console configuration.";
  const corrections: Record<string, string> = {
    approval_pending: "The run remains paused. Review the preview and submit a valid decision.",
    authorization_denied: "You do not have authority for this operation. Request the appropriate role or scope.",
    validation_failed: "Correct the indicated input and resubmit the decision.",
    prohibited_operation: "This requested operation is not permitted. No production change was made.",
  };
  return corrections[error.detail.code] ?? "The Host rejected the request. Use the correlation ID when escalating.";
}

async function request<T>(fetchImpl: FetchLike, baseUrl: string, path: string, init: RequestInit | undefined, parser: JsonParser<T>): Promise<T> {
  const response = await fetchImpl(apiUrl(baseUrl, path), { credentials: "include", headers: { Accept: "application/json", ...(init?.body ? { "Content-Type": "application/json" } : {}) }, ...init });
  const payload: unknown = await response.json().catch((): null => null);
  if (!response.ok) throw parseError(payload, response.status);
  try { return parser(payload); }
  catch (error: unknown) { throw clientError("invalid_response", response.status, error instanceof Error ? error.message : "The Host response was not usable."); }
}

function parseRunProjection(value: unknown): RunProjection {
  const record = objectValue(value, "run projection");
  return { run_id: stringValue(record, "run_id"), workflow_id: stringValue(record, "workflow_id"), workflow_version: stringValue(record, "workflow_version"), status: stringValue(record, "status"), engine: stringValue(record, "engine"), correlation_id: stringValue(record, "correlation_id"), updated_at: stringValue(record, "updated_at"), failure_code: nullableString(record, "failure_code"), action_preview: nullablePreview(record, "action_preview") };
}

function parseGraphState(value: unknown): GraphState {
  const record = objectValue(value, "graph state");
  return { run_id: stringValue(record, "run_id"), status: stringValue(record, "status"), engine: stringValue(record, "engine"), graph_id: nullableString(record, "graph_id"), graph_thread_id: nullableString(record, "graph_thread_id"), updated_at: stringValue(record, "updated_at"), failure_code: nullableString(record, "failure_code"), tool_effects: arrayValue(record, "tool_effects", parseToolEffect), action_previews: arrayValue(record, "action_previews", parseActionPreview) };
}

function parseApprovalGate(value: unknown): ApprovalGate {
  const record = objectValue(value, "approval gate");
  return { approval_id: stringValue(record, "approval_id"), run_id: stringValue(record, "run_id"), risk_tier: stringValue(record, "risk_tier"), gate_status: stringValue(record, "gate_status"), created_at: stringValue(record, "created_at"), action_preview: parseActionPreview(record.action_preview) };
}

function parseApprovalDecision(value: unknown): ApprovalDecision {
  const record = objectValue(value, "approval decision");
  return { approval_id: stringValue(record, "approval_id"), run_id: stringValue(record, "run_id"), actor_id: stringValue(record, "actor_id"), selected_value: stringValue(record, "selected_value"), reason_is_valid: booleanValue(record, "reason_is_valid"), value_is_valid: booleanValue(record, "value_is_valid"), resumed: booleanValue(record, "resumed"), gate_status: stringValue(record, "gate_status"), submitted_at: stringValue(record, "submitted_at"), action_preview: parseActionPreview(record.action_preview) };
}

function parseActionPreview(value: unknown): ActionPreview {
  const record = objectValue(value, "action preview");
  const confidence = record.confidence;
  if (confidence !== null && confidence !== undefined && (typeof confidence !== "number" || !Number.isFinite(confidence) || confidence < 0 || confidence > 1)) throw new Error("Invalid preview confidence.");
  return { action_id: stringValue(record, "action_id"), summary: stringValue(record, "summary"), intended_effect: stringValue(record, "intended_effect"), emitted_at: stringValue(record, "emitted_at"), rollback_preview: nullableString(record, "rollback_preview"), supporting_evidence: arrayValue(record, "supporting_evidence", (item: unknown): string => stringItem(item, "supporting evidence")), confidence: confidence ?? null, uncertainty: nullableString(record, "uncertainty"), correction_control: nullableString(record, "correction_control") };
}

function parseToolEffect(value: unknown): ToolEffect {
  const record = objectValue(value, "tool effect");
  return { adapter_id: stringValue(record, "adapter_id"), outcome: stringValue(record, "outcome"), effect_digest: stringValue(record, "effect_digest"), completed_at: stringValue(record, "completed_at"), reversible: booleanValue(record, "reversible"), compensation_reference: nullableString(record, "compensation_reference") };
}

function objectValue(value: unknown, description: string): JsonRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error(`Invalid ${description}.`);
  return value as JsonRecord;
}

function stringValue(record: JsonRecord, field: string): string {
  return stringItem(record[field], field);
}

function stringItem(value: unknown, field: string): string {
  if (typeof value !== "string" || value.length === 0) throw new Error(`Missing ${field}.`);
  return value;
}

function nullableString(record: JsonRecord, field: string): string | null {
  const value = record[field];
  if (value === null || value === undefined) return null;
  return stringItem(value, field);
}

function booleanValue(record: JsonRecord, field: string): boolean {
  const value = record[field];
  if (typeof value !== "boolean") throw new Error(`Invalid ${field}.`);
  return value;
}

function arrayValue<T>(record: JsonRecord, field: string, parser: JsonParser<T>): readonly T[] {
  const value = record[field];
  if (!Array.isArray(value)) throw new Error(`Invalid ${field}.`);
  return value.map((item: unknown): T => parser(item));
}

function nullablePreview(record: JsonRecord, field: string): ActionPreview | null {
  const value = record[field];
  return value === null || value === undefined ? null : parseActionPreview(value);
}

function parseError(value: unknown, status: number): OperatorApiError {
  const root = objectValue(value, "error response");
  const detail = typeof root.detail === "object" && root.detail !== null && !Array.isArray(root.detail) ? root.detail as JsonRecord : root;
  const code = typeof detail.code === "string" ? detail.code : "request_failed";
  const correlationId = typeof detail.correlation_id === "string" ? detail.correlation_id : null;
  const retryable = detail.retryable === true;
  return new OperatorApiError("The Host rejected the request.", { code, correlationId, retryable, status });
}

function clientError(code: string, status: number, message: string): OperatorApiError {
  return new OperatorApiError(message, { code, correlationId: null, retryable: false, status });
}

function runPath(runId: string): string {
  return `${API_PREFIX}workflow-runs/${encodeURIComponent(identifier(runId, "run ID"))}`;
}

function approvalPath(approvalId: string): string {
  return `${API_PREFIX}approvals/${encodeURIComponent(identifier(approvalId, "approval ID"))}`;
}

function identifier(value: string, name: string): string {
  const normalized = value.trim();
  if (normalized.length === 0 || normalized.length > 100) throw clientError("validation_failed", 0, `Invalid ${name}.`);
  return normalized;
}

function normalizeBaseUrl(value: string): string {
  if (value.length === 0) return "";
  let url: URL;
  try { url = new URL(value); }
  catch { throw clientError("client_configuration", 0, "Invalid API base URL."); }
  if ((url.protocol !== "http:" && url.protocol !== "https:") || url.pathname !== "/" || url.search || url.hash) throw clientError("client_configuration", 0, "Invalid API base URL.");
  return url.origin;
}

function apiUrl(baseUrl: string, path: string): string {
  if (!path.startsWith(API_PREFIX)) throw clientError("client_configuration", 0, "Only /api/v1 paths are permitted.");
  return `${baseUrl}${path}`;
}
