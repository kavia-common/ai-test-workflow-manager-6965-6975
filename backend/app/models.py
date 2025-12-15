from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


def _now_iso() -> str:
    """Return current UTC timestamp in ISO8601 format."""
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Suite:
    """In-memory representation of a test suite."""
    id: str
    name: str
    description: Optional[str] = ""
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunLog:
    """Single log record for a run."""
    timestamp: str
    level: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Run:
    """In-memory representation of a suite execution run."""
    id: str
    suite_id: str
    status: str = "pending"  # pending|running|success|failed|canceled
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    logs: List[RunLog] = field(default_factory=list)

    def append_log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Append a log entry to this run."""
        self.logs.append(RunLog(timestamp=_now_iso(), level=level, message=message, data=data or {}))
        self.updated_at = _now_iso()

    def set_status(self, status: str) -> None:
        """Set status and update timestamps accordingly."""
        allowed = {"pending", "running", "success", "failed", "canceled"}
        if status not in allowed:
            raise ValueError(f"Invalid status: {status}")
        self.status = status
        now = _now_iso()
        self.updated_at = now
        if status == "running" and not self.started_at:
            self.started_at = now
        if status in {"success", "failed", "canceled"}:
            self.finished_at = now


class InMemoryStore:
    """Simple in-memory store for suites and runs."""

    def __init__(self) -> None:
        self._suites: Dict[str, Suite] = {}
        self._runs: Dict[str, Run] = {}

    # PUBLIC_INTERFACE
    def list_suites(self) -> List[Suite]:
        """Return all suites in insertion order."""
        return list(self._suites.values())

    # PUBLIC_INTERFACE
    def get_suite(self, suite_id: str) -> Optional[Suite]:
        """Get a suite by id, or None."""
        return self._suites.get(suite_id)

    # PUBLIC_INTERFACE
    def create_suite(self, name: str, description: Optional[str] = "", metadata: Optional[Dict[str, Any]] = None) -> Suite:
        """Create a suite, ensuring unique id."""
        suite_id = str(uuid.uuid4())
        suite = Suite(id=suite_id, name=name, description=description or "", metadata=metadata or {})
        self._suites[suite_id] = suite
        return suite

    # PUBLIC_INTERFACE
    def update_suite(self, suite_id: str, name: Optional[str] = None, description: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Suite:
        """Update fields for an existing suite."""
        suite = self._suites.get(suite_id)
        if not suite:
            raise KeyError("Suite not found")
        if name is not None:
            suite.name = name
        if description is not None:
            suite.description = description
        if metadata is not None:
            suite.metadata = metadata
        suite.updated_at = _now_iso()
        return suite

    # PUBLIC_INTERFACE
    def delete_suite(self, suite_id: str) -> None:
        """Delete a suite and any associated runs."""
        if suite_id in self._suites:
            del self._suites[suite_id]
        # Cascade delete runs for suite
        to_delete = [rid for rid, run in self._runs.items() if run.suite_id == suite_id]
        for rid in to_delete:
            del self._runs[rid]

    # PUBLIC_INTERFACE
    def list_runs(self, suite_id: Optional[str] = None) -> List[Run]:
        """List runs, optionally filtered by suite id."""
        if suite_id:
            return [r for r in self._runs.values() if r.suite_id == suite_id]
        return list(self._runs.values())

    # PUBLIC_INTERFACE
    def get_run(self, run_id: str) -> Optional[Run]:
        """Get a run by id, or None."""
        return self._runs.get(run_id)

    # PUBLIC_INTERFACE
    def create_run(self, suite_id: str, parameters: Optional[Dict[str, Any]] = None, status: str = "pending") -> Run:
        """Create a run for a suite."""
        if suite_id not in self._suites:
            raise KeyError("Suite not found for run")
        run_id = str(uuid.uuid4())
        run = Run(id=run_id, suite_id=suite_id, parameters=parameters or {}, status=status)
        # Validate and normalize status
        run.set_status(status)
        self._runs[run_id] = run
        return run

    # PUBLIC_INTERFACE
    def append_run_log(self, run_id: str, level: str, message: str, data: Optional[Dict[str, Any]] = None) -> Run:
        """Append a log to a run and return updated run."""
        run = self._runs.get(run_id)
        if not run:
            raise KeyError("Run not found")
        run.append_log(level=level, message=message, data=data)
        return run

    # PUBLIC_INTERFACE
    def set_run_status(self, run_id: str, status: str) -> Run:
        """Update run status."""
        run = self._runs.get(run_id)
        if not run:
            raise KeyError("Run not found")
        run.set_status(status)
        return run


# Singleton store instance
store = InMemoryStore()
