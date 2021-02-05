import sys
from functools import wraps
from flask import Flask, jsonify, request, render_template, make_response, redirect
from flask import g as flask_g
import logging
import psycopg2

sys.path.insert(0, '/Users/Johnnie172/PycharmProjects/ksp-scraper-api/ksp_scraper')
import db_connection
from UserUtilities import UserUtilities

logging.basicConfig(filename='flask.log', level=10
                    , format='%(asctime)s: %(module)s: %(funcName)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
db_queries = db_connection.get_db_queries()
app = Flask(__name__)
user_utilities = UserUtilities(db_queries)


def require_user(api_method):
    @wraps(api_method)
    def check_user_id(*args, **kwargs):

        user_id = request.cookies.get('user_id')
        if user_id:
            flask_g.user_id = user_id
            return api_method(*args, **kwargs)
        else:
            return redirect('/')

    return check_user_id


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/set")
def set_cookie():
    response = make_response('setting cookie!')
    response.set_cookie('framework', 'flask')

    return response


@app.route("/get")
def get_cookie():
    framework = request.cookies.get('framework')
    return 'The framework is' + framework


@app.route('/sign-up', methods=['POST'])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    user_id = user_utilities.user_signup(email, password, password2)

    if user_id:
        response = make_response('setting cookie!')
        response.set_cookie('user_id', f'{user_id}')
        logger.debug(f'User ID: {user_id}')
        return response

    logger.debug(f'User exists')
    return jsonify(items=['Error']), 401


@app.route('/sign-in', methods=['POST'])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")
    user_id_and_email = user_utilities.user_login(email, password)

    if user_id_and_email:
        user_id = user_id_and_email[0]
        response = make_response(redirect('/items'))
        response.set_cookie('user_id', f'{user_id}')
        logger.debug(f'User ID: {user_id}')
        return response

    logger.debug(f'Wrong password')
    return jsonify(items=['Error']), 401


@app.route('/log-out', methods=['GET', 'POST'])
@require_user
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('user_id', max_age=0)
    return response


@app.route('/api/items', methods=['GET'])
@require_user
def get_items():
    user_id = flask_g.user_id
    logger.debug(f'user id: {user_id}')
    items = db_queries.select_all_user_items(user_id)
    logger.debug(items)
    # todo normal way to convert decimal/ to understand json and decimals
    items_witout_decimal = []
    for item in items:
        item = [x for x in item]
        item[3] = int(item[3])
        item[7] = int(item[7])
        logger.debug(item)

        items_witout_decimal.append(item)

    return jsonify(items=items_witout_decimal), 200


@app.route('/item-alert', methods=['POST'])
@require_user
def add_new_item():
    user_id = flask_g.user_id
    # ading new item for users items table
    return jsonify(items=[None]), 201


@app.route('/item-alert', methods=['DELETE'])
@require_user
def delete_item():
    user_id = flask_g.user_id
    # delete item from users items table
    return jsonify(data='Item deleted'), 200


@app.route('/item-alert', methods=['PUT'])
@require_user
def change_target_price():
    user_id = flask_g.user_id
    # changing target price for user item
    return jsonify(items=[None]), 201


@app.route('/items', methods=['GET'])
@require_user
def view_items():
    return render_template('view_items.html')

if __name__ == '__main__':
    app.run(debug=True)
