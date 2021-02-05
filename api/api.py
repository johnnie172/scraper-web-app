import sys
from functools import wraps
from flask import Flask, jsonify, request, render_template,make_response, redirect
from flask import g as flask_g
import logging
import psycopg2
sys.path.insert(0,'/Users/Johnnie172/PycharmProjects/ksp-scraper-api/ksp_scraper')
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
        response = make_response(redirect('/api/items'))
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
    #todo normal way to convert decimal/ to understand json and decimals
    items_witout_decimal = []
    for item in items:
        item = [x for x in item]
        item[3] = int(item[3])
        item[7] = int(item[7])
        logger.debug(item)

        items_witout_decimal.append(item)


    return jsonify(items=[items_witout_decimal]), 200


@app.route('/item-alert', methods=['POST'])
@require_user
def add_new_item():

    user_id = flask_g.user_id
    #ading new item for users items table
    return jsonify(items=[None]), 201


@app.route('/item-alert', methods=['DELETE'])
@require_user
def delete_item():

    user_id = flask_g.user_id
    #delete item from users items table
    return jsonify(data='Item deleted'), 200


@app.route('/item-alert', methods=['PUT'])
@require_user
def change_target_price():

    user_id = flask_g.user_id
    #changing target price for user item
    return jsonify(items=[None]), 201






# @app.route("/", methods=['GET'])
# def index():
#     return jsonify(data="Hello World"), 200

@app.route("/api/uin", methods=['GET'])
def view_uin():
    """Getting all active uin:"""
    records = db_queries.select_all_uin()
    return jsonify(records), 200

@app.route("/api/<int:user_id>", methods=['GET'])
def user_id(user_id):
    return jsonify(data=user_id), 200


@app.route("/api/<int:user_id>/add_item/<int:item_id>/<int:target_price>", methods=['GET', 'POST'])
def add_item(user_id, item_id, target_price):
    user_utilities = UserUtilities(db_queries)
    user_utilities.add_new_user_item(user_id, item_id, target_price)
    return jsonify(
        user_id=user_id,
        item_id=item_id,
        target_price=target_price
    ), 201


@app.route("/api/<int:user_id>/delete_item/<int:item_id>", methods=['GET', 'POST'])
def del_item(user_id, item_id):
    user_utilities = UserUtilities(db_queries)
    user_utilities.delete_user_item(user_id, item_id)
    return jsonify(
        user_id=user_id,
        item_id=item_id
    ), 201


@app.route("/api/<int:user_id>/change_target/<int:item_id>/<int:target_price>", methods=['GET', 'POST'])
def target_price(target_price, user_id, item_id):
    user_utilities = UserUtilities(db_queries)
    user_utilities.change_target_price(target_price, user_id, item_id)
    return jsonify(
        user_id=user_id,
        item_id=item_id,
        target_price=target_price
    ), 201


if __name__ == '__main__':
    app.run(debug=True)