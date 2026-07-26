/**
 * Fail-closed presentation mapping for pack agent activation fields
 * (migration_redesign + adoption: no silent production activation).
 */

export interface PackAgentActivationSource {
  readonly agent_id?: string | null;
  readonly production_activation_denied?: boolean;
  readonly production_active?: boolean | null;
  readonly status?: string | null;
}

export interface PackAgentActivationView {
  readonly agentId: string | null;
  readonly status: string | null;
  /** Always false when activation is denied or migration remains non-active. */
  readonly productionActive: boolean;
  readonly productionActivationDenied: boolean;
  readonly activationLabel: string;
  readonly mayOfferActivationControl: boolean;
}

/**
 * Maps a generated PackAgentResponse (or equivalent) without inventing active
 * production state. Denial and missing status fail closed.
 */
export function mapPackAgentActivation(source: PackAgentActivationSource): PackAgentActivationView {
  const agentId = typeof source.agent_id === "string" && source.agent_id.trim().length > 0
    ? source.agent_id.trim()
    : null;
  const status = typeof source.status === "string" && source.status.trim().length > 0
    ? source.status.trim()
    : null;
  const productionActivationDenied = source.production_activation_denied !== false;
  const rawProductionActive = source.production_active === true;
  const statusLooksActive = status !== null && /^(active|production_active|prod_active)$/i.test(status);
  const productionActive = !productionActivationDenied && rawProductionActive && statusLooksActive;
  const activationLabel = productionActive
    ? "active"
    : status ?? (productionActivationDenied ? "registered · production activation denied" : "non_active");

  return {
    agentId,
    status,
    productionActive,
    productionActivationDenied,
    activationLabel,
    mayOfferActivationControl: false,
  };
}
