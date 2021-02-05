import os

# DATABASE_NAME = os.environ.get('DATABASE_NAME')
# DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
# DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
# DATABASE_HOST = os.environ.get('DATABASE_HOST')
# DATABASE_PORT = os.environ.get('DATABASE_PORT')
# DATABASE_TABLES_SETUP_FILE = os.environ.get('DATABASE_TABLES_SETUP_FILE')
# DATABASE_NAME = 'scraper_db'
# DATABASE_USERNAME = 'postgres'
# DATABASE_PASSWORD = 'Post5432'
# DATABASE_HOST = '127.0.0.1'
# DATABASE_PORT = '5432'
# DATABASE_TABLES_SETUP_FILE = 'create_tables.sql'

EMAIL_MESSAGE_TITLE = "KSP scraper notify"

URL_TO_ADD_UIN = 'https://ksp.co.il/?uin='

USER_EMAIL_ERROR_MESSAGE = 'You have entered invalid Email address'
EMAIL_ALREADY_EXISTS_MESSAGE = 'Email is in our system, please try again.'

UNMATCHED_PASSWORD_MESSAGE = 'You have entered unmatched passwords!'

LINK_ERROR_MESSAGE = 'Sorry we cannot use this link, Please try again.'
TARGET_PRICE_ERROR_MESSAGE = 'Sorry the target price is not valid, please make sure you entered numbers only(not ' \
                             'decimal). '
UIN_ERROR_MESSAGE = 'Sorry, cannot find uin.'
ITEM_OUT_OF_STOCK_MESSAGE = 'The item is out of stock!'
GENERIC_ERROR_MESSAGE = 'An error occurred!'
