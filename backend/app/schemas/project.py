from marshmallow import Schema, fields, validate


class ProjectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=255), load_default=None)
    created_at = fields.DateTime(dump_only=True)


project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
