-- Target-local migration. Apply only from an explicitly isolated Postgres fixture or deployment plan.
CREATE TABLE IF NOT EXISTS graph_checkpoints (
    record_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    checkpoint_namespace TEXT NOT NULL,
    sequence BIGINT NOT NULL CHECK (sequence >= 1),
    checkpoint JSONB NOT NULL,
    snapshot_reference TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    version BIGINT NOT NULL CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT graph_checkpoints_thread_scope_check
        CHECK (thread_id = organization_id || ':' || run_id),
    CONSTRAINT graph_checkpoints_sequence_scope_unique
        UNIQUE (organization_id, run_id, checkpoint_namespace, sequence)
);

CREATE INDEX IF NOT EXISTS graph_checkpoints_resume_lookup_idx
    ON graph_checkpoints (organization_id, run_id, sequence DESC);
