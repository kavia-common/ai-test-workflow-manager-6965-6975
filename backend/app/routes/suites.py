from __future__ import annotations

import hashlib
import json
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from marshmallow import ValidationError

from .. import app  # for logger
from ..services import (
    list_suites as svc_list_suites,
    get_suite as svc_get_suite,
    create_suite as svc_create_suite,
    update_suite as svc_update_suite,
    delete_suite as svc_delete_suite,
    list_runs as svc_list_runs,
    get_run as svc_get_run,
    create_run as svc_create_run,
)
from ..schemas import SuiteCreateSchema, SuiteUpdateSchema, RunCreateSchema, RunSchema, SuiteSchema

blp = Blueprint(
    "Suites",
    "suites",
    url_prefix="/api",
    description="Manage test suites and related runs",
)

suite_schema = SuiteSchema()
suite_create_schema = SuiteCreateSchema()
suite_update_schema = SuiteUpdateSchema()
run_create_schema = RunCreateSchema()
run_schema = RunSchema()


def _json():
    """Safely get JSON body, returning {} when none provided."""
    return request.get_json(silent=True) or {}


def _handle_service_exceptions(fn):
    """Decorator to handle common service layer exceptions uniformly."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as ve:
            app.logger.warning("Validation error: %s", ve.messages)
            abort(400, message="Invalid request payload", errors=getattr(ve, "messages", None))
        except KeyError as ke:
            app.logger.info("Not found: %s", ke)
            abort(404, message=str(ke))
        except ValueError as ve:
            app.logger.warning("Bad request: %s", ve)
            abort(400, message=str(ve))
        except Exception:  # pragma: no cover - safety net
            app.logger.exception("Unhandled error")
            abort(500, message="Internal server error")
    wrapper.__name__ = fn.__name__
    return wrapper


# Suites collection
@blp.route("/suites", methods=["GET", "POST"])
class SuitesCollection(MethodView):
    @blp.response(200, SuiteSchema(many=True), description="List all suites")
    @_handle_service_exceptions
    def get(self):
        """List test suites."""
        return svc_list_suites()

    @blp.arguments(SuiteCreateSchema, location="json", as_kwargs=False)
    @blp.response(201, SuiteSchema, description="Create a new suite")
    @_handle_service_exceptions
    def post(self, payload):
        """Create a new test suite."""
        # Services perform validation again to ensure reusability; pass-through payload
        return svc_create_suite(payload)


# Suite item
@blp.route("/suites/<string:suite_id>", methods=["GET", "PUT", "DELETE"])
class SuiteItem(MethodView):
    @blp.response(200, SuiteSchema, description="Get a suite by id")
    @_handle_service_exceptions
    def get(self, suite_id: str):
        """Retrieve a suite by id."""
        return svc_get_suite(suite_id)

    @blp.arguments(SuiteUpdateSchema, location="json", as_kwargs=False)
    @blp.response(200, SuiteSchema, description="Update a suite by id")
    @_handle_service_exceptions
    def put(self, payload, suite_id: str):
        """Update a suite by id."""
        return svc_update_suite(suite_id, payload)

    @_handle_service_exceptions
    def delete(self, suite_id: str):
        """Delete a suite by id."""
        svc_delete_suite(suite_id)
        return {"message": "Deleted"}, 204


# Deterministic AI suggestion stub
def _deterministic_suggestion(input_data: dict) -> dict:
    """
    Produce a deterministic suggestion result by hashing canonical JSON of input.
    No external calls; purely deterministic for testing.
    """
    canonical = json.dumps(input_data, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    # Use digest to produce stable pseudo-suggestions
    title = f"Suggested Enhancements #{digest[:8]}"
    suggestions = [
        {"id": f"case-{digest[8:12]}", "title": "Add login flow regression", "priority": "high"},
        {"id": f"case-{digest[12:16]}", "title": "Verify error states", "priority": "medium"},
        {"id": f"case-{digest[16:20]}", "title": "Cross-browser smoke set", "priority": "low"},
    ]
    return {
        "id": f"sugg-{digest[:12]}",
        "title": title,
        "explanation": "Deterministic AI suggestion stub based on input hash; no external requests performed.",
        "hash": digest,
        "suggestions": suggestions,
        "input_echo": input_data,
    }


@blp.route("/suites/<string:suite_id>/ai/suggest", methods=["POST"])
class SuiteAISuggest(MethodView):
    @_handle_service_exceptions
    def post(self, suite_id: str):
        """Generate deterministic AI suggestions for a suite (stub, no external calls)."""
        # Ensure suite exists
        _ = svc_get_suite(suite_id)
        payload = _json()
        result = _deterministic_suggestion({"suite_id": suite_id, "payload": payload})
        return result, 200


# Runs related to suites
@blp.route("/suites/<string:suite_id>/runs", methods=["POST"])
class SuiteRunsCollection(MethodView):
    @blp.arguments(RunCreateSchema, location="json", as_kwargs=False)
    @blp.response(201, RunSchema, description="Create a run for a suite")
    @_handle_service_exceptions
    def post(self, payload, suite_id: str):
        """Create a run for the specified suite."""
        # Ensure the payload has the suite_id from the path
        payload = dict(payload or {})
        payload["suite_id"] = suite_id
        return svc_create_run(payload)


# Runs top-level collection and items
@blp.route("/runs", methods=["GET"])
class RunsCollection(MethodView):
    @blp.response(200, RunSchema(many=True), description="List runs, optionally filtered by suiteId")
    @_handle_service_exceptions
    def get(self):
        """List runs; optionally filter by suiteId query parameter."""
        suite_id = request.args.get("suiteId")
        return svc_list_runs(suite_id=suite_id)


@blp.route("/runs/<string:run_id>", methods=["GET"])
class RunItem(MethodView):
    @blp.response(200, RunSchema, description="Get a run by id")
    @_handle_service_exceptions
    def get(self, run_id: str):
        """Get a single run by id."""
        return svc_get_run(run_id)


@blp.route("/runs/<string:run_id>/logs", methods=["GET"])
class RunLogs(MethodView):
    @_handle_service_exceptions
    def get(self, run_id: str):
        """Get logs for a run."""
        run = svc_get_run(run_id)
        # Return only the logs array for convenience
        return {"runId": run_id, "logs": run.get("logs", [])}, 200
