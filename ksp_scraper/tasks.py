import db_connection
import orchestrator
from UserUtilities import UserUtilities
from celery import Celery
import logging

app = Celery()
app.config_from_object('celery_config')
logger = logging.getLogger(__name__)


@app.task
def celery_main_task():

    db_queries = db_connection.get_db_queries()
    user_utilities = UserUtilities(db_queries)
    items_list = orchestrator.get_items_data(db_queries=db_connection.get_db_queries())

    items_to_store = items_list[0]
    out_of_stock_items = items_list[1]

    if out_of_stock_items:
        orchestrator.out_of_stock_manger(db_queries=db_queries, user_utilities=user_utilities,
                                        out_of_stock_items=tuple(out_of_stock_items))

    target_price_list = orchestrator.storing_and_sorting_items_data(db_queries, items_to_store)
    user_utilities.notify_target_price(target_price_list)