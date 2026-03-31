from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date
from ..models.task import VALID_STATUSES, VALID_PRIORITIES


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=1000), load_default=None)
    status = fields.Str(
        validate=validate.OneOf(VALID_STATUSES),
        load_default="todo",
    )
    priority = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_PRIORITIES),
    )
    due_date = fields.Date(load_default=None)
    project_id = fields.Int(load_default=None, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("due_date")
    def due_date_not_in_past(self, value):
        if value and value < date.today():
            raise ValidationError("due_date cannot be in the past.")


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
