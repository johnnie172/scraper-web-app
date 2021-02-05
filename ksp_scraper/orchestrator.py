import logging
import consts
import request_utilities
import data_parser

logger = logging.getLogger(__name__)


def get_items_data(db_queries):
    """Getting all in stock items from items table, returning tuple of two lists."""
    list_of_items = db_queries.select_all_uin()
    items_to_store_and_notify = []
    out_of_stock_items = []
    logger.debug(f'List of uin to check: {list_of_items}.')

    for uin in list_of_items:
        item_id = uin[0]
        logger.debug(f'The url is: {consts.URL_TO_ADD_UIN}{uin[1]}.')
        text = request_utilities.get_text_from_url(consts.URL_TO_ADD_UIN + uin[1])
        try:
            title_and_price = data_parser.get_title_and_price(text)

            if title_and_price:
                logger.debug(f'Title and price are: {title_and_price}.')
                price = data_parser.change_price_from_str_to_decimal(title_and_price[1])
                items_to_store_and_notify.append((item_id, price))
            else:
                out_of_stock_items.append(item_id)

        except:
            logger.error(consts.GENERIC_ERROR_MESSAGE)
            print(consts.GENERIC_ERROR_MESSAGE)

    return (items_to_store_and_notify, out_of_stock_items)


def storing_and_sorting_items_data(db_queries, items_to_store):
    """Sorting and storing items that in stock, returning items that hits target price."""
    db_queries.add_prices(items_to_store)
    db_queries.check_for_lowest_price_and_update()

    id_list_to_pass = [(item[0],) for item in items_to_store]
    logger.debug(f'id_list_to_pass: {id_list_to_pass}')
    target_price_list = db_queries.check_target_prices(id_list_to_pass)

    return target_price_list


def out_of_stock_manger(db_queries, user_utilities, out_of_stock_items):
    """Changing to out of stock and notifying users."""

    records = db_queries.select_emails_for_out_of_stock_items(out_of_stock_items)

    db_queries.change_to_out_of_stock(out_of_stock_items)

    for record in records:
        logger.debug(f'record is: {record}')
        item_title = record.title
        emails_to_send = record.emails
        user_utilities.notify_out_of_stock(emails_to_send, item_title)
