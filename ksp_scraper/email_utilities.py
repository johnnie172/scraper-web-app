import consts
import smtp_config
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_smtp_client = None


def get_smtp_service():
    global _smtp_client
    if _smtp_client is None:
        _smtp_client = smtplib.SMTP(host=smtp_config.SMTP_HOST, port=587)
        _smtp_client.starttls()
        _smtp_client.login(smtp_config.SMTP_ADDRESS, smtp_config.SMTP_PASSWORD)
        logger.debug(f'_smtp_client is created')
    return _smtp_client


def send_target_price_mail(email, item_uin):
    msg = MIMEMultipart()
    message = f'The item that you wanted is now at the target price, item link: {consts.URL_TO_ADD_UIN + item_uin}.'
    msg['From'] = smtp_config.SMTP_ADDRESS
    msg['To'] = email
    msg['Subject'] = consts.EMAIL_MESSAGE_TITLE
    msg.attach(MIMEText(message, 'plain'))
    get_smtp_service().send_message(msg)
    logger.debug(f'Sending email to: {email}, about target price to uin:{item_uin}.')

    del msg


def send_out_of_stock_mail(email, item_title):
    msg = MIMEMultipart()
    message = f'The item that you wanted is now out of stock, item title: {item_title}.'
    msg['From'] = smtp_config.SMTP_ADDRESS
    msg['To'] = email
    msg['Subject'] = consts.EMAIL_MESSAGE_TITLE
    msg.attach(MIMEText(message, 'plain'))
    get_smtp_service().send_message(msg)
    logger.debug(f'Sending email to: {email}, about out of stock item to item:{item_title}.')

    del msg
