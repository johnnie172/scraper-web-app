import user_input_utilities
import consts
import email_utilities
import orchestrator
import logging
import hashlib
import binascii
import os
import re


class UserUtilities:

    def __init__(self, db_queries):
        self.logger = logging.getLogger(__name__)
        self.db_queries = db_queries



    def user_login(self, email, password):
        """Login user, returning the id and email after verifying password"""
        user = self.db_queries.select_user(email)
        id = user[0]
        email = user[1]
        stored_password = user[2]

        if self.verify_password(password, stored_password):
            self.logger.debug(f'User with email:{email} is logged in!')
            return (id, email)
        else:
            self.logger.debug('Password not matches!')
            print('Wrong password!')
            return False

    def user_signup(self, email, password, password2):
        """Signup user, adding to db_queries instance and returning user_id"""

        user_id = None

        if password == password2 and self.check_valid_email(email):
            hashed_password = self.hash_password(password)

            user_id = self.db_queries.add_user(email, hashed_password)

        else:
            self.logger.debug(consts.UNMATCHED_PASSWORD_MESSAGE)
            raise Exception(consts.UNMATCHED_PASSWORD_MESSAGE)

        if user_id == None:
            print(consts.EMAIL_ALREADY_EXISTS_MESSAGE)
            self.logger.debug(f'{consts.EMAIL_ALREADY_EXISTS_MESSAGE}, email is: {email}.')
            return False

        self.logger.debug(f'New user is added, user id is:{user_id}')
        return user_id

    def user_log_out(self):
        pass

    def scrap_for_new_item(self,user_id, item_url):
        """Scraping for new item by url, adding it to items table(returning id),
        adding it to prices table,
        adding it to users items table with target of 0."""
        new_item_dict = orchestrator.get_new_item(item_url)
        item_price = new_item_dict.get("item_price")
        item_title = new_item_dict.get("item_title")
        item_uin = new_item_dict.get("item_uin")
        lowest= new_item_dict.get("lowest")

        item_id = self.db_queries.add_item(item_title, item_uin, lowest)
        new_item_dict['item_id'] = item_id

        self.db_queries.add_price(item_id, item_price)
        user_item = self.db_queries.add_user_item(user_id, item_id, target_price=0)

        if user_item:
            new_item_dict['alert_for_target'] = True
        else:
            new_item_dict['alert_for_target'] = False

        return new_item_dict

    def delete_user_item(self,user_id,item_id):
        """Delete user item."""
        self.logger.debug(f'user_id: {user_id}, item_id: {item_id}.')
        if self.db_queries.delete_user_item(user_id, item_id):
            return True

        return False

    def change_target_price(self,target_price, user_id, item_id):
        """Changing user item target price."""
        self.logger.debug(f'user_id: {user_id}, item_id: {item_id}, target_price: {target_price}.')
        if self.db_queries.check_for_target_price(item_id, target_price):
            if self.db_queries.change_target_price(target_price, user_id, item_id):
                return True

        return False

    def notify_out_of_stock(self, users_emails, item_title):
        """Notify users that item is out of stock."""
        email_utilities.send_out_of_stock_mail(users_emails, item_title)

    def notify_target_price(self, users_id_records):
        """Notify users that item is at the target price."""
        self.logger.debug(f'users_id_records are:{users_id_records}')

        users_list = []
        current_item_id = users_id_records[0][1]
        items_users_dict = {}

        for user in users_id_records:
            self.logger.debug(f'user is:{user}')
            user_id = user[0]
            item_id = user[1]

            if current_item_id == item_id:
                items_users_dict = {}
                items_users_dict[item_id] = users_list
                users_list.append(user_id)
                self.logger.debug(f'items_users_dict is: {items_users_dict}')
            else:
                users_list = []
                self.logger.debug(f'users_list is: {users_list}')
                items_users_dict[item_id] = users_list
                users_list.append(user_id)
                self.logger.debug(f'items_users_dict is: {items_users_dict}')

        for item in items_users_dict:

            self.logger.debug(f'item is: {item}')
            item_uin = self.db_queries.select_row(f'SELECT uin FROM items WHERE id = {item}')

            current_users_ids = items_users_dict[item]
            self.logger.debug('-------------------------------------------------------')
            self.logger.debug(f'current_users_ids is: {current_users_ids}')
            current_users_ids_to_notify = self.db_queries.check_target_price_notify(current_users_ids, item)
            self.logger.debug(f'current_users_ids_to_notify is: {current_users_ids_to_notify}')

            if current_users_ids_to_notify:
                current_users_ids_to_notify_list = [r[0] for r in current_users_ids_to_notify]

                self.logger.debug(f'current_users_ids_to_notify_list is: {current_users_ids_to_notify_list}')

                email_records = self.db_queries.select_emails_to_notify(tuple(current_users_ids_to_notify_list))
                self.logger.debug(f'email_records are: {email_records}')

                emails_to_send = ""
                for email in email_records:
                    self.logger.debug(f'email is: {email}')
                    self.logger.debug(f'uin is: {item_uin}')
                    emails_to_send += (f', {email[0]}')

                email_utilities.send_target_price_mail(emails_to_send, item_uin[0])

    def hash_password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        self.logger.debug('Hashing password.')
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, password, stored_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                      password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        self.logger.debug('Verifying password.')
        return pwdhash == stored_password

    def check_valid_email(self, email):
        """Function that validate Email address."""
        regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        if (re.search(regex, email)):
            return True

        return False