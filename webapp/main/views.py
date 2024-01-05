from flask import jsonify, render_template, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from webapp import app, db
from datetime import datetime, timedelta

from webapp.models import UserModel, CategoryModel, RecordModel
from webapp.schemes import UserSchema, CategorySchema, RecordSchema

with app.app_context():
    db.create_all()
    db.session.commit()


@app.get('/')
def base_url():
    return render_template('index.html')


@app.get('/healthcheck')
def healthcheck():
    ua_current_time = datetime.utcnow() + timedelta(hours=3)
    formatted_time = ua_current_time.strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'status': 'OK',
        'current_time': formatted_time
    }
    return jsonify(response), 200


@app.post('/user')
def create_user():
    user_data = request.get_json()
    try:
        UserSchema().load(user_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    user = UserModel(name=user_data['name'])
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': 'An error occurred while saving the user'}), 400

    return jsonify({'id': user.id, 'name': user.name}), 201


@app.get('/user/<user_id>')
def get_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name})


@app.delete('/user/<user_id>')
def delete_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User with id {user_id} has been deleted'})


@app.get('/users')
def get_users():
    return list({'id': user.id, 'name': user.name} for user in UserModel.query.all())


@app.get('/category/<category_id>')
def get_category(category_id):
    user_id = request.args['user_id']
    category = CategoryModel.query.get_or_404(category_id)

    if category.is_private and category.user_id != int(user_id):
        return jsonify({'error': 'You`ve not permitted to view this category'}), 403

    return jsonify({
        'id': category.id,
        'name': category.name,
        'created_by': category.user_id,
        'total_spent': category.total_spent,
        'is_private': category.is_private
    })


@app.post('/category')
def create_category():
    category_data = request.get_json()

    try:
        CategorySchema().load(category_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    category_name = category_data['name']
    is_private = category_data['is_private']
    user_id = category_data['user_id']

    existing_category = CategoryModel.query.filter_by(name=category_name, is_private=is_private).first()
    if existing_category:
        return jsonify({'error': f'Category with name `{category_name}` already exists'}), 409

    category = CategoryModel(name=category_name, is_private=is_private, user_id=user_id, total_spent=0)
    db.session.add(category)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': 'An error occurred while saving the category'}), 400

    return jsonify({
         'id': category.id,
         'name': category.name,
         'total_spent': 0,
         'is_private': category.is_private
    }), 201


@app.get('/categories')
def get_categories():
    categories = CategoryModel.query.filter_by(is_private=False).all()
    categories_list = [{'id': c.id, 'name': c.name, 'user_id': c.user_id, 'total_spent': c.total_spent} for c in categories]
    return jsonify(categories_list)


@app.get('/categories/<user_id>')
def get_user_categories(user_id):
    categories = CategoryModel.query.filter_by(user_id=user_id).all()
    categories_list = [{'id': c.id, 'name': c.name, 'user_id': c.user_id, 'total_spent': c.total_spent} for c in categories]
    return jsonify(categories_list)


@app.delete('/category/<category_id>')
def delete_category(category_id):
    user_id = request.args['user_id']
    if user_id is None:
        return jsonify({'error': 'User ID is required'}), 400

    category = CategoryModel.query.get_or_404(category_id)
    if category.user_id != int(user_id):
        return jsonify({'error': 'You`ve not permitted to delete this category'}), 403

    RecordModel.query.filter_by(category_id=category_id).delete()
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'})


@app.get('/record/<record_id>')
def get_record(record_id):
    record = RecordModel.query.get_or_404(record_id)
    return jsonify({
        'id': record.id,
        'user_id': record.user_id,
        'category_id': record.category_id,
        'created_at': record.created_at,
        'cost_amount': record.cost_amount
    })


@app.delete('/record/<record_id>')
def delete_record(record_id):
    user_id = request.args['user_id']
    record = RecordModel.query.get_or_404(record_id)

    if record.user_id != int(user_id):
        return jsonify({'error': 'You`ve not permitted to delete this record'}), 403

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Record deleted'})


@app.post('/record')
def create_record():
    record_data = request.get_json()
    try:
        RecordSchema().load(record_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    category_id = record_data['category_id']
    user_id = record_data['user_id']

    category = CategoryModel.query.get_or_404(category_id)

    if category.is_private and category.user_id != user_id:
        return jsonify({'error': 'You`ve not permitted to create record in private category'}), 403

    record = RecordModel(
        user_id=user_id,
        category_id=category_id,
        cost_amount=record_data['cost_amount']
    )

    category.total_spent += record.cost_amount
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'id': record.id,
        'user_id': user_id,
        'category_id': category_id,
        'created_at': record.created_at,
        'cost_amount': record.cost_amount
    }), 201


@app.get('/record')
def get_records():
    u_id = request.args.get('user_id')
    c_id = request.args.get('category_id')

    if u_id is None and c_id is None:
        return jsonify({'error': 'Query parameters user_id or category_id (or both) must be provided'}), 400

    query = RecordModel.query
    if u_id is not None:
        query = query.filter(RecordModel.user_id == int(u_id))
    if c_id is not None:
        query = query.filter(RecordModel.category_id == int(c_id))

    records = []
    for record in query.all():
        category = CategoryModel.query.get(record.category_id)
        if category.is_private:
            if u_id is None or category.user_id != int(u_id):
                continue
        records.append(record)

    records_response = [{'id': r.id, 'user_id': r.user_id, 'category_id': r.category_id,
                         'created_at': r.created_at, 'cost_amount': r.cost_amount} for r in records]
    return jsonify(records_response)

