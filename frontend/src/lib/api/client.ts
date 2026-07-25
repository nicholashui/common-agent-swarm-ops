import {
  requestGeneratedOperation,
  type GeneratedOperationData,
  type GeneratedOperationId,
  type GeneratedOperationRequest,
  type GeneratedOperationResult,
} from "./generated";
import { PublicApiTransport, type PublicApiTransportOptions } from "./transport";

export type {
  GeneratedActionReference,
  GeneratedJsonObject,
  GeneratedJsonValue,
  GeneratedOperationData,
  GeneratedOperationId,
  GeneratedOperationRequest,
  GeneratedOperationResponse,
  GeneratedOperationResult,
} from "./generated";
export { PublicApiTransport } from "./transport";

/** Application import surface for generated Public API request functions. */
export interface PublicApiClient {
  request<TId extends GeneratedOperationId>(
    operationId: TId,
    request: GeneratedOperationRequest<TId>,
  ): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>>;
}

export function createPublicApiClient(options: PublicApiTransportOptions = {}): PublicApiClient {
  const transport = new PublicApiTransport(options);
  return {
    request: <TId extends GeneratedOperationId>(operationId: TId, request: GeneratedOperationRequest<TId>): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>> => requestGeneratedOperation(transport, operationId, request),
  };
}
