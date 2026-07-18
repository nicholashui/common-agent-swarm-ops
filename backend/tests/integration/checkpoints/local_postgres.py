"""Pinned, in-process Postgres fixture for checkpoint repository integration tests.

The fixture implements only the fixed ``graph_checkpoints`` contract used by the
repository.  It has no DSN, does not start a service, and cannot contact a
shared or remote database.  Each test receives a new fixture instance.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

CheckpointRow = tuple[object, ...]


@dataclass
class IsolatedLocalPostgres:
    """A transaction-aware local model of the pinned graph-checkpoint table."""

    available: bool = True
    rows: list[CheckpointRow] = field(default_factory=list)
    connections_opened: int = 0
    lookup_calls: int = 0

    def connection_factory(self) -> LocalPostgresConnection:
        """Open an isolated local connection or simulate a configured-store outage."""
        if not self.available:
            raise OSError("isolated local Postgres is unavailable")
        self.connections_opened += 1
        return LocalPostgresConnection(self)

    def latest(
        self, organization_id: str, run_id: str, thread_id: str
    ) -> CheckpointRow | None:
        """Return the highest-sequence row for the exact repository lookup scope."""
        self.lookup_calls += 1
        matching = [
            row
            for row in self.rows
            if row[1] == organization_id and row[2] == run_id and row[3] == thread_id
        ]
        if not matching:
            return None
        return max(matching, key=self._sequence)

    @staticmethod
    def _sequence(row: CheckpointRow) -> int:
        """Read the fixed sequence column stored by the repository insert."""
        sequence = row[5]
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            raise AssertionError("local Postgres fixture received an invalid checkpoint sequence")
        return sequence


@dataclass
class LocalPostgresConnection:
    """One local transaction used by ``PostgresCheckpointRepository``."""

    database: IsolatedLocalPostgres
    pending_rows: list[CheckpointRow] = field(default_factory=list)
    committed: bool = False
    rolled_back: bool = False
    closed: bool = False

    def cursor(self) -> LocalPostgresCursor:
        """Open a cursor limited to the checkpoint table contract."""
        return LocalPostgresCursor(self)

    def commit(self) -> None:
        """Make checkpoint writes visible to connections created after a restart."""
        self.database.rows.extend(self.pending_rows)
        self.pending_rows.clear()
        self.committed = True

    def rollback(self) -> None:
        """Discard uncommitted local writes on a simulated repository failure."""
        self.pending_rows.clear()
        self.rolled_back = True

    def close(self) -> None:
        """Close this isolated local connection."""
        self.closed = True


@dataclass
class LocalPostgresCursor:
    """Cursor that accepts only the repository's pinned insert and resume query."""

    connection: LocalPostgresConnection
    selected_row: CheckpointRow | None = None
    closed: bool = False

    def execute(self, operation: str, parameters: Sequence[object] = ()) -> None:
        """Execute the fixed checkpoint insert or exact-scope resume lookup."""
        if "INSERT INTO graph_checkpoints" in operation:
            self._insert(parameters)
            return
        if "FROM graph_checkpoints" in operation:
            self._select(parameters)
            return
        raise AssertionError("local Postgres fixture received an unsupported statement")

    def fetchone(self) -> CheckpointRow | None:
        """Return the selected latest checkpoint row, if one exists."""
        return self.selected_row

    def close(self) -> None:
        """Close this isolated local cursor."""
        self.closed = True

    def _insert(self, parameters: Sequence[object]) -> None:
        """Stage one fixed-shape graph-checkpoint row for commit."""
        row = tuple(parameters)
        if len(row) != 13:
            raise AssertionError("local Postgres fixture received an invalid insert shape")
        self.connection.pending_rows.append(row)

    def _select(self, parameters: Sequence[object]) -> None:
        """Select only by the organization, run, and tenant thread identity."""
        if len(parameters) != 3:
            raise AssertionError("local Postgres fixture received an invalid resume lookup")
        organization_id, run_id, thread_id = parameters
        if not (
            isinstance(organization_id, str)
            and isinstance(run_id, str)
            and isinstance(thread_id, str)
        ):
            raise AssertionError("local Postgres fixture received an invalid resume lookup")
        self.selected_row = self.connection.database.latest(organization_id, run_id, thread_id)
