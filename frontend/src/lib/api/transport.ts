import {
  GENERATED_API_BASE_PATH,
  buildGeneratedRequest,
  type GeneratedActionReference,
  type GeneratedJsonValue,
  type GeneratedOperationData,
  type GeneratedOperationExecutor,
  type GeneratedOperationId,
  type GeneratedOperationRequest,
  type GeneratedOperationResult,
} from "./generated";

export interface FetchLike {
  (input: RequestInfo | URL, init?: RequestInit): Promise<Response>;
}

export interface PublicApiTransportOptions {
  readonly fetchImpl?: FetchLike;
  readonly readRetryLimit?: number;
}

type JsonRecord = Record<string, unknown>;

/** The sole browser transport for generated same-origin Public API operations. */
export class PublicApiTransport implements GeneratedOperationExecutor {
  private readonly fetchImpl: FetchLike;
  private readonly readRetryLimit: number;

  public constructor(options: PublicApiTransportOptions = {}) {
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch.bind(globalThis);
    this.readRetryLimit = validateReadRetryLimit(options.readRetryLimit ?? 1);
  }

  public async execute<TId extends GeneratedOperationId>(
    operationId: TId,
    request: GeneratedOperationRequest<TId>,
  ): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>> {
    const generatedRequest = buildGeneratedRequest(operationId, request);
    assertSameOriginVersionedPath(generatedRequest.path);
    const retryLimit = generatedRequest.method === "GET" ? this.readRetryLimit : 0;
    for (let attempt = 0; attempt <= retryLimit; attempt += 1) {
      const outcome = await this.perform<GeneratedOperationData<TId>>(generatedRequest);
      if (outcome.ok || !outcome.retryable || attempt === retryLimit) return outcome;
    }
    return invalidResponse();
  }

  private async perform<TData>(request: { readonly method: string; readonly path: string; readonly body?: unknown }): Promise<GeneratedOperationResult<TData>> {
    let response: Response;
    try {
      response = await this.fetchImpl(request.path, {
        method: request.method,
        credentials: "include",
        cache: "no-store",
        headers: { Accept: "application/json", ...(request.body === undefined ? {} : { "Content-Type": "application/json" }) },
        ...(request.body === undefined ? {} : { body: JSON.stringify(request.body) }),
      });
    } catch {
      return { ok: false, code: "transport_unavailable", message: "The public API request could not be completed.", retryable: true };
    }
    const payload = await response.json().catch((): null => null);
    if (response.ok) return parseSuccess<TData>(payload);
    return parseError(payload, response.headers.get("Retry-After"));
  }
}

function parseSuccess<TData>(payload: unknown): GeneratedOperationResult<TData> {
  const envelope = asRecord(payload);
  const meta = envelope === undefined ? undefined : asRecord(envelope.meta);
  if (envelope === undefined || !("data" in envelope) || meta === undefined || typeof meta.correlation_id !== "string") return invalidResponse();
  return { ok: true, data: envelope.data as TData, correlationId: meta.correlation_id };
}

function parseError(payload: unknown, retryAfterHeader: string | null): GeneratedOperationResult<never> {
  const root = asRecord(payload);
  const error = root === undefined ? undefined : asRecord(root.error);
  if (error === undefined || typeof error.code !== "string" || typeof error.message !== "string" || typeof error.retryable !== "boolean") return invalidResponse();
  const correlationId = optionalString(error.correlation_id);
  const retryAfterSeconds = optionalRetryAfter(error.retry_after) ?? optionalRetryAfter(retryAfterHeader);
  const actionReference = isGeneratedActionReference(error.action_reference) ? error.action_reference : undefined;
  return { ok: false, code: error.code, message: error.message, retryable: error.retryable, ...(correlationId === undefined ? {} : { correlationId }), ...(retryAfterSeconds === undefined ? {} : { retryAfterSeconds }), ...(actionReference === undefined ? {} : { actionReference }) };
}

function asRecord(value: unknown): JsonRecord | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as JsonRecord : undefined;
}

function optionalString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function optionalRetryAfter(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isFinite(value) && value >= 0) return value;
  if (typeof value === "string" && /^\d+$/.test(value)) return Number(value);
  return undefined;
}

function isGeneratedActionReference(value: unknown): value is GeneratedActionReference {
  return isGeneratedJsonValue(value) && typeof value === "object" && value !== null && !Array.isArray(value);
}

function isGeneratedJsonValue(value: unknown): value is GeneratedJsonValue {
  if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") return true;
  if (Array.isArray(value)) return value.every(isGeneratedJsonValue);
  const record = asRecord(value);
  return record !== undefined && Object.values(record).every(isGeneratedJsonValue);
}

function assertSameOriginVersionedPath(path: string): void {
  if (!path.startsWith(`${GENERATED_API_BASE_PATH}/`) || path.startsWith("//") || /^[a-z][a-z\d+.-]*:/i.test(path)) throw new Error("Public API requests must use generated same-origin /api/v1 paths.");
}

function validateReadRetryLimit(value: number): number {
  if (!Number.isInteger(value) || value < 0 || value > 3) throw new Error("The read retry limit must be an integer from zero through three.");
  return value;
}

function invalidResponse(): GeneratedOperationResult<never> {
  return { ok: false, code: "invalid_public_response", message: "The public API returned an unusable response.", retryable: false };
}
