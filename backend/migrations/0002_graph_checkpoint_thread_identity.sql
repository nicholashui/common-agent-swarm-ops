-- Target-local hardening migration. Apply only from an explicitly isolated fixture or deployment plan.
-- Preserve the application's unambiguous {organization_id}:{run_id} checkpoint identity at rest.
ALTER TABLE graph_checkpoints
    ADD CONSTRAINT graph_checkpoints_identifier_format_check
    CHECK (
        organization_id <> ''
        AND run_id <> ''
        AND position(':' IN organization_id) = 0
        AND position(':' IN run_id) = 0
    );
