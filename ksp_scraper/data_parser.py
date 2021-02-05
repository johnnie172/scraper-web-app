import logging
import re
from re import sub
from decimal import Decimal
import consts

logger = logging.getLogger(__name__)


def get_title_and_price(source_text_beautiful):
    """Function that scraping for the price and title from a link, returning tuple of both."""
    try:
        price_div = source_text_beautiful.find(class_="div-options-prices")
        price = price_div.span.text
        logger.debug(f'The price is: {price}.')
        title_div = source_text_beautiful.find(class_="title-text")
        title = title_div.span.text
        logger.debug(f'The title is: {title}.')
        return (title, price)
    except AttributeError as e:
        logger.exception(e)
        sold_out_div = source_text_beautiful.find(class_="ims")
        logger.debug(f' Sold Out item: {sold_out_div}')
        sold_out = sold_out_div.text
        if 'אזל במלאי' in sold_out:
            logger.error(consts.ITEM_OUT_OF_STOCK_MESSAGE)
            return None
        else:
            logger.error(consts.GENERIC_ERROR_MESSAGE)
            return None


def change_price_from_str_to_decimal(item_price):
    """Function that converting string of price to decimal."""
    decimal_price = Decimal(sub(r'[^\d.]', '', item_price))
    logger.debug(f'The price is {item_price}.')

    return decimal_price


def parse_uin_from_url(url):
    """Checking for 'uin=' and returning the number after it."""
    regex = 'uin=(\d+)'
    match = re.search(regex, url)
    if match:
        return match.group()[4:]

    return False


# parse_uin_from_url old function
# def parse_uin_from_url(url):
#     """Getting uin instead of the entire url"""
#     uin = ''
#     i = url.find('uin=')
#     if i < 0:
#         logger.error(consts.UIN_ERROR_MESSAGE)
#         raise Exception(consts.UIN_ERROR_MESSAGE)
#     else:
#         for i in range(i + 4, len(url)):
#             if url[i].isnumeric() and i != len(url):
#                 uin += url[i]
#             else:
#                 logger.debug(f'The uin is:{uin}.')
#                 return uin
#         logger.debug(f'The uin is:{uin}.')
#         return uin
