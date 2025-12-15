from __future__ import annotations

from typing import Any, Dict

from marshmallow import Schema, fields, validate, ValidationError, post_dump


class SuiteSchema(Schema):
    id = fields.String(required=True, metadata={"description": "Suite identifier"})
    name = fields.String(required=True, validate=validate.Length(min=1), metadata={"description": "Suite name"})
    description = fields.String(allow_none=True, metadata={"description": "Suite description"})
    created_at = fields.String(required=True, metadata={"description": "Creation timestamp"})
    updated_at = fields.String(required=True, metadata={"description": "Update timestamp"})
    metadata = fields.Dict(keys=fields.String(), values=fields.Raw(), metadata={"description": "Arbitrary metadata"})

    @post_dump
    def drop_none(self, data, many, **kwargs):
        return {k: v for k, v in data.items() if v is not None}


class SuiteCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1), metadata={"description": "Suite name"})
    description = fields.String(allow_none=True, metadata={"description": "Suite description"})
    metadata = fields.Dict(keys=fields.String(), values=fields.Raw(), allow_none=True,
                           metadata={"description": "Arbitrary metadata"})


class SuiteUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1))
    description = fields.String(allow_none=True)
    metadata = fields.Dict(keys=fields.String(), values=fields.Raw(), allow_none=True)


class RunLogSchema(Schema):
    timestamp = fields.String(required=True)
    level = fields.String(required=True, validate=validate.OneOf(["debug", "info", "warn", "error"]))
    message = fields.String(required=True, validate=validate.Length(min=1))
    data = fields.Dict(keys=fields.String(), values=fields.Raw())


class RunSchema(Schema):
    id = fields.String(required=True)
    suite_id = fields.String(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["pending", "running", "success", "failed", "canceled"]))
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)
    started_at = fields.String(allow_none=True)
    finished_at = fields.String(allow_none=True)
    parameters = fields.Dict(keys=fields.String(), values=fields.Raw())
    result = fields.Dict(keys=fields.String(), values=fields.Raw())
    logs = fields.List(fields.Nested(RunLogSchema))

    @post_dump
    def drop_none(self, data, many, **kwargs):
        return {k: v for k, v in data.items() if v is not None}


class RunCreateSchema(Schema):
    suite_id = fields.String(required=True)
    parameters = fields.Dict(keys=fields.String(), values=fields.Raw(), allow_none=True)
    status = fields.String(load_default="pending", validate=validate.OneOf(["pending", "running", "success", "failed", "canceled"]))


class RunStatusUpdateSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["pending", "running", "success", "failed", "canceled"]))


class AppendLogSchema(Schema):
    level = fields.String(required=True, validate=validate.OneOf(["debug", "info", "warn", "error"]))
    message = fields.String(required=True, validate=validate.Length(min=1))
    data = fields.Dict(keys=fields.String(), values=fields.Raw(), allow_none=True)


# PUBLIC_INTERFACE
def validate_payload(schema: Schema, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and deserialize input payload using the provided schema."""
    try:
        return schema.load(payload)
    except ValidationError as err:
        # Re-raise with a consistent message; caller can map to HTTP layer later.
        raise ValidationError({"message": "Invalid request payload", "errors": err.messages})
