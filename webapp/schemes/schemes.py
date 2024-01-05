from marshmallow import Schema, fields


class UserSchema(Schema):
    name = fields.Str(required=True)


class CategorySchema(Schema):
    user_id = fields.Int(required=True)
    name = fields.Str(required=True)
    is_private = fields.Boolean(required=True)


class RecordSchema(Schema):
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    created_at = fields.DateTime()
    cost_amount = fields.Int(required=True)

