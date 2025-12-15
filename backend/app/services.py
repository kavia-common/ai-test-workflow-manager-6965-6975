from __future__ import annotations

from typing import Any, Dict, List, Optional



from .models import store, Suite, Run
from .schemas import (
    SuiteSchema,
    SuiteCreateSchema,
    SuiteUpdateSchema,
    RunSchema,
    RunCreateSchema,
    RunStatusUpdateSchema,
    AppendLogSchema,
    validate_payload,
)


_suite_schema = SuiteSchema()
_run_schema = RunSchema()
_suite_list_schema = SuiteSchema(many=True)
_run_list_schema = RunSchema(many=True)


# PUBLIC_INTERFACE
def list_suites() -> List[Dict[str, Any]]:
    """Return serialized list of all suites."""
    return _suite_list_schema.dump(store.list_suites())


# PUBLIC_INTERFACE
def get_suite(suite_id: str) -> Dict[str, Any]:
    """Return serialized suite by id or raise KeyError."""
    suite = store.get_suite(suite_id)
    if not suite:
        raise KeyError("Suite not found")
    return _suite_schema.dump(suite)


# PUBLIC_INTERFACE
def create_suite(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input and create a new suite."""
    data = validate_payload(SuiteCreateSchema(), payload)
    suite: Suite = store.create_suite(name=data["name"], description=data.get("description"), metadata=data.get("metadata"))
    return _suite_schema.dump(suite)


# PUBLIC_INTERFACE
def update_suite(suite_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input and update suite."""
    data = validate_payload(SuiteUpdateSchema(), payload)
    suite: Suite = store.update_suite(suite_id, name=data.get("name"), description=data.get("description"), metadata=data.get("metadata"))
    return _suite_schema.dump(suite)


# PUBLIC_INTERFACE
def delete_suite(suite_id: str) -> None:
    """Delete a suite by id; cascades deletes of related runs."""
    store.delete_suite(suite_id)


# PUBLIC_INTERFACE
def list_runs(suite_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List serialized runs, optionally filtered by suite."""
    return _run_list_schema.dump(store.list_runs(suite_id=suite_id))


# PUBLIC_INTERFACE
def get_run(run_id: str) -> Dict[str, Any]:
    """Get a run by id, serialized."""
    run = store.get_run(run_id)
    if not run:
        raise KeyError("Run not found")
    return _run_schema.dump(run)


# PUBLIC_INTERFACE
def create_run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and create a run for a suite."""
    data = validate_payload(RunCreateSchema(), payload)
    run: Run = store.create_run(suite_id=data["suite_id"], parameters=data.get("parameters"), status=data.get("status", "pending"))
    return _run_schema.dump(run)


# PUBLIC_INTERFACE
def set_run_status(run_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and update a run status."""
    data = validate_payload(RunStatusUpdateSchema(), payload)
    run: Run = store.set_run_status(run_id, data["status"])
    return _run_schema.dump(run)


# PUBLIC_INTERFACE
def append_run_log(run_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and append a log entry to a run."""
    data = validate_payload(AppendLogSchema(), payload)
    run: Run = store.append_run_log(run_id, level=data["level"], message=data["message"], data=data.get("data"))
    return _run_schema.dump(run)
