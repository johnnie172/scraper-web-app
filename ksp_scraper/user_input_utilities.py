import logging
import consts, UserUtilities
import re

logger = logging.getLogger(__name__)


def input_link():
    """Function that asked user input for link to scrap."""
    answer_item_link = input(str("Please enter KSP product link(starting with https://) : "))

    if answer_item_link[0:8] == 'https://':
        logger.info('The answer_item_link is: {}'.format(answer_item_link))
        return answer_item_link
    else:
        logger.error(f'user answer_item_link is invalid the input was: {answer_item_link}.')
        raise Exception(consts.LINK_ERROR_MESSAGE)


def input_target_price():
    """Function that asked user input for target price."""
    answer_target_price = input(str('Please enter the target price that you would like to be notify of:'))
    if answer_target_price.isnumeric() or answer_target_price.isdecimal():
        answer_target_price = float(answer_target_price)
        logger.debug(f'The answer_target_price is: {answer_target_price}')
        return answer_target_price
    else:
        logger.error(f'user answer_target_price is invalid the input was: {answer_target_price}.')
        raise Exception(consts.TARGET_PRICE_ERROR_MESSAGE)


def input_user_email():
    """Function that asked user input for Email."""
    answer_user_email = input(str('Please enter Email: '))
    if check_valid_email(answer_user_email):
        logger.debug(f'User Email is: {answer_user_email}.')
        return answer_user_email
    else:
        logger.error(f'{consts.USER_EMAIL_ERROR_MESSAGE} email was: {answer_user_email}.')
        raise Exception(consts.USER_EMAIL_ERROR_MESSAGE)


def check_valid_email(email):
    """Function that validate Email address."""
    regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    if (re.search(regex, email)):
        return True

    return False


def input_user_password():
    """Function that asked user input for password for login."""
    answer_user_pass = input(str('Please enter password: '))
    return answer_user_pass


def input_user_password_sign_up():
    """Function that asked user input for password for the first time."""
    answer_user_pass = input(str('Please enter password: '))
    answer_user_pass_1 = input(str('Please enter password again: '))
    if answer_user_pass == answer_user_pass_1:
        hashed_password = UserUtilities.hash_password(answer_user_pass)
        return hashed_password
    else:
        logger.debug(consts.UNMATCHED_PASSWORD_MESSAGE)
        raise Exception(consts.UNMATCHED_PASSWORD_MESSAGE)
