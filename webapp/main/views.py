import uuid

from flask import jsonify, render_template, request, abort
from webapp import app
from datetime import datetime, timedelta

database = {'users': {}, 'categories': {}, 'records': {}}
resource_deleted = {'deleted': True}


@app.route('/', methods=['GET'])
def base_url():
    return render_template('index.html')


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    ua_current_time = datetime.utcnow() + timedelta(hours=3)
    formatted_time = ua_current_time.strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'status': 'OK',
        'current_time': formatted_time
    }
    return jsonify(response), 200


@app.route('/user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    user_id = uuid.uuid4().hex
    user = {'id': user_id, **user_data}
    database['users'][user_id] = user
    return jsonify(user), 201


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    if user_id not in database['users']:
        abort(404)
    return jsonify(database['users'][user_id])


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id not in database['users']:
        abort(404)
    del database['users'][user_id]
    keys = [key for key, record in database['records'].items() if record['user_id'] == user_id]
    for key in keys:
        del database['records'][key]
    return jsonify(resource_deleted)


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(database['users'].values()))


@app.route('/category/<category_id>', methods=['GET'])
def get_category(category_id):
    if category_id not in database['categories']:
        abort(404)
    return jsonify(database['categories'][category_id])


@app.route('/category', methods=['POST'])
def create_category():
    category_data = request.get_json()
    category_id = uuid.uuid4().hex
    category = {'id': category_id, **category_data}
    database['categories'][category_id] = category
    return jsonify(category), 201


@app.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    if category_id not in database['categories']:
        abort(404)
    del database['categories'][category_id]
    keys = [key for key, record in database['records'].items() if record['category_id'] == category_id]
    for key in keys:
        del database['records'][key]
    return jsonify(resource_deleted)


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    if record_id not in database['records']:
        abort(404)
    return jsonify(database['records'][record_id])


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    if record_id not in database['records']:
        abort(404)
    del database['records'][record_id]
    return jsonify(resource_deleted)


@app.route('/record', methods=['POST'])
def create_record():
    record_data = request.get_json()
    record_id = uuid.uuid4().hex
    record = {'id': record_id, **record_data}
    database['records'][record_id] = record
    return jsonify(record), 201


@app.route('/record')
def get_records():
    u_id, c_id = request.args.get('user_id'), request.args.get('category_id')
    if u_id is None and c_id is None:
        abort(400)
    records = [r for r in database['records'].values()
               if (u_id is None or r['user_id'] == u_id) and (c_id is None or r['category_id'] == c_id)]
    return jsonify(records), 200
