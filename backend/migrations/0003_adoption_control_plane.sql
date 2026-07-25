-- Adoption control-plane durability constraints.
-- Apply only from an explicitly isolated Postgres fixture or deployment plan.

CREATE TABLE IF NOT EXISTS adoption_pack_registrations (
    registration_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    pack_id TEXT NOT NULL,
    immutable_version TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    signer_id TEXT NOT NULL,
    host_compatibility_range JSONB NOT NULL,
    alc_compatibility_range JSONB NOT NULL,
    validation_result BOOLEAN NOT NULL,
    policy_passed BOOLEAN NOT NULL DEFAULT TRUE,
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
    compatibility_status TEXT NOT NULL
        CHECK (compatibility_status IN ('compatible', 'incompatible', 'not_evaluated')),
    host_contract_version TEXT,
    alc_version TEXT,
    asset_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    failed_validation_categories JSONB NOT NULL DEFAULT '[]'::jsonb,
    reproduction_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    superseded BOOLEAN NOT NULL DEFAULT FALSE,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT adoption_pack_registration_identity_unique
        UNIQUE (pack_id, immutable_version),
    CONSTRAINT adoption_pack_registration_approval_check
        CHECK (
            decision <> 'approved'
            OR (validation_result AND policy_passed)
        ),
    CONSTRAINT adoption_pack_registration_superseded_check
        CHECK (
            NOT superseded
            OR (host_contract_version IS NOT NULL AND alc_version IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS adoption_invocation_associations (
    association_id TEXT PRIMARY KEY,
    invocation_id TEXT NOT NULL UNIQUE,
    organization_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    pack_version TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS adoption_evidence (
    evidence_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    evidence_kind TEXT NOT NULL,
    subject_reference TEXT NOT NULL,
    evidence_reference TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT adoption_evidence_reference_only_check
        CHECK (length(trim(evidence_reference)) > 0),
    CONSTRAINT adoption_evidence_content_digest_check
        CHECK (length(trim(content_digest)) > 0)
);

CREATE TABLE IF NOT EXISTS adoption_learning_episodes (
    episode_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL,
    organization_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    pack_version TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    terminal_outcome TEXT NOT NULL
        CHECK (terminal_outcome IN ('completed', 'failed', 'blocked', 'retried', 'escalated')),
    outcome_reference TEXT NOT NULL,
    retrieval_record_id TEXT,
    evidence_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    blocked_for_recovery BOOLEAN NOT NULL DEFAULT FALSE,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT adoption_learning_episode_attempt_unique UNIQUE (attempt_id),
    CONSTRAINT adoption_learning_episode_reference_only_check
        CHECK (length(trim(outcome_reference)) > 0)
);

CREATE TABLE IF NOT EXISTS adoption_release_readiness_decisions (
    decision_id TEXT PRIMARY KEY,
    pack_id TEXT NOT NULL,
    immutable_version TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('eligible', 'blocked', 'failed')),
    integration_coverage_complete BOOLEAN NOT NULL,
    evidence_references JSONB NOT NULL,
    unmet_gate_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    failure_evidence_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    terminal BOOLEAN NOT NULL DEFAULT TRUE,
    organization_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT adoption_release_decision_terminal_check CHECK (terminal),
    CONSTRAINT adoption_release_decision_identity_unique
        UNIQUE (pack_id, immutable_version, workflow_id),
    CONSTRAINT adoption_release_decision_failure_evidence_check
        CHECK (
            status = 'eligible'
            OR jsonb_array_length(unmet_gate_references) > 0
            OR jsonb_array_length(failure_evidence_references) > 0
        )
);

CREATE INDEX IF NOT EXISTS adoption_pack_registrations_lookup_idx
    ON adoption_pack_registrations (pack_id, immutable_version);
CREATE INDEX IF NOT EXISTS adoption_invocation_associations_scope_idx
    ON adoption_invocation_associations (organization_id, domain_id, run_id);
CREATE INDEX IF NOT EXISTS adoption_learning_episodes_attempt_lookup_idx
    ON adoption_learning_episodes (organization_id, attempt_id);
CREATE INDEX IF NOT EXISTS adoption_release_decisions_lookup_idx
    ON adoption_release_readiness_decisions (pack_id, immutable_version, workflow_id);

CREATE OR REPLACE FUNCTION adoption_reject_immutable_row_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'adoption evidence records are immutable';
END;
$$;

DROP TRIGGER IF EXISTS adoption_evidence_immutable_trigger ON adoption_evidence;
CREATE TRIGGER adoption_evidence_immutable_trigger
    BEFORE UPDATE OR DELETE ON adoption_evidence
    FOR EACH ROW EXECUTE FUNCTION adoption_reject_immutable_row_update();

DROP TRIGGER IF EXISTS adoption_learning_episode_immutable_trigger ON adoption_learning_episodes;
CREATE TRIGGER adoption_learning_episode_immutable_trigger
    BEFORE UPDATE OR DELETE ON adoption_learning_episodes
    FOR EACH ROW EXECUTE FUNCTION adoption_reject_immutable_row_update();

DROP TRIGGER IF EXISTS adoption_release_decision_immutable_trigger
    ON adoption_release_readiness_decisions;
CREATE TRIGGER adoption_release_decision_immutable_trigger
    BEFORE UPDATE OR DELETE ON adoption_release_readiness_decisions
    FOR EACH ROW EXECUTE FUNCTION adoption_reject_immutable_row_update();

DROP TRIGGER IF EXISTS adoption_registration_immutable_trigger ON adoption_pack_registrations;
CREATE TRIGGER adoption_registration_immutable_trigger
    BEFORE UPDATE OR DELETE ON adoption_pack_registrations
    FOR EACH ROW EXECUTE FUNCTION adoption_reject_immutable_row_update();
