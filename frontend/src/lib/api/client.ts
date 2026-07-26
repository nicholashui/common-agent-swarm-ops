import type {
  GeneratedOperationData,
  GeneratedOperationId,
  GeneratedOperationRequest,
  GeneratedOperationResult,
} from "./generated";
import {
  PublicApiTransport,
  type PublicApiRequestOptions,
  type PublicApiTransportOptions,
} from "./transport";

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
export { PublicApiTransport, type PublicApiRequestOptions } from "./transport";

/** Application import surface for generated Public API request functions. */
export interface PublicApiClient {
  request<TId extends GeneratedOperationId>(
    operationId: TId,
    request: GeneratedOperationRequest<TId>,
    options?: PublicApiRequestOptions,
  ): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>>;
}

export function createPublicApiClient(options: PublicApiTransportOptions = {}): PublicApiClient {
  const transport = new PublicApiTransport(options);
  return {
    request: <TId extends GeneratedOperationId>(
      operationId: TId,
      request: GeneratedOperationRequest<TId>,
      requestOptions: PublicApiRequestOptions = {},
    ): Promise<GeneratedOperationResult<GeneratedOperationData<TId>>> =>
      transport.executeWithOptions(operationId, request, requestOptions),
  };
}
