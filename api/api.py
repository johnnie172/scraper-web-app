import sys
import os
import inspect
from functools import wraps
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, flash
from flask import g as flask_g
import logging
import psycopg2

#todo path change
# sys.path.insert(0, '/Users/Johnnie172/PycharmProjects/scraper-web-app/ksp_scraper')

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from ksp_scraper import db_connection
from ksp_scraper.UserUtilities import UserUtilities

logging.basicConfig(filename='flask.log', level=10
                    , format='%(asctime)s: %(module)s: %(funcName)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
db_queries = db_connection.get_db_queries()
app = Flask(__name__)
#todo CHANGE secret key!!
app.secret_key = 'To Change this'
user_utilities = UserUtilities(db_queries)


def require_user(api_method):
    @wraps(api_method)
    def check_user_id(*args, **kwargs):

        user_id = request.cookies.get('user_id')
        if user_id:
            flask_g.user_id = user_id
            return api_method(*args, **kwargs)
        else:
            return redirect(url_for('index'))

    return check_user_id


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


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
    return jsonify(data=['Error']), 401


@app.route('/sign-in', methods=['POST'])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")
    user_id_and_email = user_utilities.user_login(email, password)

    if user_id_and_email:
        user_id = user_id_and_email[0]
        response = make_response(redirect(url_for('view_items')))
        response.set_cookie('user_id', f'{user_id}')
        logger.debug(f'User ID: {user_id}')
        return response

    logger.debug(f'Wrong password')
    return jsonify(items=['Error']), 401


@app.route('/log-out', methods=['GET', 'POST'])
@require_user
def logout():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('user_id', max_age=0)
    return response


@app.route('/api/items', methods=['GET'])
@require_user
def get_items():
    user_id = flask_g.user_id
    logger.debug(f'user id: {user_id}')
    items = db_queries.select_all_user_items(user_id)
    logger.debug(items)
    for item in items:
        item['Delete'] = f'/delete-item/{item["id"]}'
        item['Change'] = f'/change-item/{item["id"]}'
        item['Reset'] = f'/reset-notify-count/{item["id"]}'

    return jsonify(items), 200


@app.route('/item-alert', methods=['POST'])
@require_user
def add_new_item():

    req = request.get_json()
    logger.debug(f'req is: {req}')
    item_url = req['url']
    user_id = flask_g.user_id
    res = make_response(jsonify({"message": "JSON recived"}), 200)

    new_item = user_utilities.scrap_for_new_item(user_id, item_url)

    if new_item:
        if new_item["alert_for_target"]:
            flash(f'Please enter target price for: {new_item["item_title"]}!')
            flash(new_item["Change"])

        return res

    return jsonify(items=['Error']), 401


@app.route('/item-alert', methods=['DELETE'])
@require_user
def delete_item():

    req = request.get_json()
    logger.debug(f'req is: {req}')
    item_id = req['item_id']
    user_id = flask_g.user_id
    res = make_response(jsonify({"message": "JSON recived"}), 200)
    delete_item = db_queries.delete_user_item(user_id, item_id)

    if delete_item:
        return res

    return jsonify(items=['Error']), 401


# @app.route('/delete-item/<int:item_id>')
# @require_user
# def delete_item(item_id):
#     user_id = flask_g.user_id
#
#     deleted_item = db_queries.delete_user_item(user_id, item_id)
#     logger.debug(f'Delete is: {deleted_item}')
#
#     if deleted_item:
#         return redirect(url_for('view_items'))
#
#     return jsonify(items=['Error']), 401


@app.route('/reset-notify-count/<int:item_id>')
@require_user
def reset_notify_count(item_id):
    user_id = flask_g.user_id

    reset_item = db_queries.reset_alert_count_for_item(user_id, item_id)
    logger.debug(f'Reset is: {reset_item}')

    if reset_item:
        return redirect(url_for('view_items'))

    return jsonify(items=['Error']), 401


@app.route('/change-item/<int:item_id>', methods=['GET'])
@require_user
def change_item_view(item_id):

    max_target_price = int(db_queries.select_max_target_price(item_id)[0])

    if max_target_price:
        return render_template('change_item_target.html', max_target_price=max_target_price)
    else:
        return jsonify(items=['Error']), 401


@app.route('/change-item/<int:item_id>', methods=['POST'])
@require_user
def change_item(item_id):
    user_id = flask_g.user_id
    target_price = request.form.get("target_price")
    Changed_item = user_utilities.change_target_price(target_price, user_id, item_id)
    logger.debug(f'Changed is: {Changed_item}')

    if Changed_item:
        return redirect(url_for('view_items'))

    return jsonify(data=['Error']), 401


@app.route('/items', methods=['GET'])
@require_user
def view_items():
    return render_template('view_items.html')

if __name__ == '__main__':
    app.run(debug=True)