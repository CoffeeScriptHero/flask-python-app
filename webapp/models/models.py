from sqlalchemy import func

from webapp import db


class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=False, nullable=False)

    category = db.relationship('CategoryModel', back_populates='user', lazy='dynamic')
    record = db.relationship('RecordModel', back_populates='user', lazy='dynamic')


class CategoryModel(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    total_spent = db.Column(db.Integer, unique=False, nullable=False)
    is_private = db.Column(db.Boolean, unique=False, nullable=False)

    user = db.relationship('UserModel', back_populates='category')
    record = db.relationship('RecordModel', back_populates='category', lazy='dynamic')


class RecordModel(db.Model):
    __tablename__ = 'record'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), unique=False, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    cost_amount = db.Column(db.Integer, unique=False, nullable=False)

    user = db.relationship('UserModel', back_populates='record')
    category = db.relationship('CategoryModel', back_populates='record')

