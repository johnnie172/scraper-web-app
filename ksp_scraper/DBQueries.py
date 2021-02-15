from DataBase import DataBase
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from psycopg2.extras import NamedTupleCursor
from psycopg2.errors import UniqueViolation
import logging

logger = logging.getLogger(__name__)


class DBQueries:

    def __init__(self, database):
        self.db = database

    """Run queries for DataBase"""

    def select_row_with_condition(self, query, vars):
        """Run a SQL query to select row with WHERE condition."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, vars)
            logger.debug(f'Query is: {query}.')
            record = cur.fetchone()
            logger.info(f"{cur.rowcount} rows affected.")
            return record

    def select_rows(self, query):
        """Run a SQL query to select rows from table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            records = [row for row in cur.fetchall()]
            logger.info(f"{cur.rowcount} rows affected.")
            return records

    def select_row(self, query):
        """Run a SQL query to select row from table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            logger.debug(f'Query is: {query}.')
            record = cur.fetchone()
            logger.info(f"{cur.rowcount} rows affected.")
            return record

    def select_row_with_vars(self, query, vars):
        """Run a SQL query to select row from table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, vars)
            logger.debug(f'Query is: {query}.')
            record = cur.fetchone()
            logger.info(f"{cur.rowcount} rows affected.")
            return record

    def select_rows_dict_cursor(self, query):
        """Run a SELECT query and return list of dicts."""
        self.db.get_connection()
        with self.db.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            records = cur.fetchall()
            return records

    def _update_rows(self, query):
        """Run a SQL query to update rows in table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected.")

    def _insert(self, query, vars):
        """Run a SQL query to insert rows in table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, vars)
            count = cur.rowcount
            self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected.")
            if count:
                return count
            else:
                return False

    def _delete(self, query, vars):
        """Run a SQL query to delete rows in table."""
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, vars)
            count = cur.rowcount
            self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected.")
            if count:
                return count
            else:
                return False


    def _insert_and_return_id(self, query, vars, select_id_command):
        """Run a SQL query to insert rows in table and return id."""
        self.db.get_connection()
        query = query + ' RETURNING id'
        with self.db.conn.cursor() as cur:
            try:
                cur.execute(query, vars)
                id = cur.fetchone()[0]
                self.db.conn.commit()
            except(UniqueViolation):
                logger.debug('There is UniqueViolation error preforming rollback and returning id')
                self.db.conn.rollback()
                cur.execute(select_id_command, (vars[0],))
                id = cur.fetchone()[0]
                self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected, the id is:{id} ")
            return id

    def add_user(self, user_email, user_password):
        """Run an INSERT query to add new user and returning id."""
        query = "INSERT INTO users (email, password) VALUES (%s, %s) RETURNING id"
        vars = (user_email, user_password)
        with self.db.conn.cursor() as cur:
            try:
                cur.execute(query, vars)
                id = cur.fetchone()[0]
                self.db.conn.commit()
            except(UniqueViolation):
                self.db.conn.rollback()
                logger.debug('There is UniqueViolation error!')
                return None
            logger.info(f"{cur.rowcount} rows affected, the id is:{id} ")
            return id

    def select_user(self, email):
        """Run SELECT to get user info."""
        query = "SELECT id, email, password FROM users WHERE email = %s"
        vars = (email,)
        records = self.select_row_with_condition(query, vars)
        logger.debug(f'Records are: {records}.')
        return records

    def add_item(self, item_title, item_uin, lowest=None):
        """Run an INSERT query to insert new item and returning id."""
        # getting 3 values(title, url, lowest) and forming them into a tuple.
        query = "INSERT INTO items (title, uin, lowest) VALUES (%s, %s, %s) RETURNING id"
        vars = (item_title, item_uin, lowest)
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            try:
                cur.execute(query, vars)
                id = cur.fetchone()[0]
                self.db.conn.commit()
            except(UniqueViolation):
                logger.debug('There is UniqueViolation error preforming rollback and returning id')
                self.db.conn.rollback()
                select_id_command = "SELECT id FROM items WHERE title = %s"
                cur.execute(select_id_command, (vars[0],))
                id = cur.fetchone()[0]
                self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected, the id is:{id} ")
            return id

    def add_price(self, item_id, price):
        """Run an INSERT query to insert new price."""
        # getting 2 values(item_id, price) and forming them into a tuple auto add timestamp.
        vars = (item_id, price)
        insert_command = "INSERT INTO prices (item_id, price) VALUES (%s, %s)"
        self._insert(insert_command, vars)
        logger.debug(f'Query is: {insert_command}, the vars are{vars}.')

    def add_user_item(self, user_id, item_id, target_price):
        """Run an INSERT query to insert new user item if not exist."""
        # getting 3 values(user_id, item_id, target_price) and forming them into a tuple.
        vars = (user_id, item_id, target_price, user_id, item_id)
        insert_command = '''INSERT INTO users_items(user_id, item_id, target_price)
                            SELECT %s, %s, %s
                            WHERE NOT EXISTS (
                            SELECT 1 FROM users_items WHERE user_id = %s and item_id = %s
                            )'''
        count =self._insert(insert_command, vars)
        logger.debug(f'Query is: {insert_command}, the vars are{vars}.')
        if count:
            return count
        return False

    def delete_user_item(self, user_id, item_id):
        """Run an DELETE query to delete user item."""
        # getting 2 values(user_id, item_id) and forming them into a tuple.
        vars = (user_id, item_id)
        delete_command = "DELETE FROM users_items WHERE user_id = %s AND item_id = %s"
        count = self._delete(delete_command, vars)
        logger.debug(f'Query is: {delete_command}, the vars are{vars}.')
        if count:
            return count
        else:
            return False

    def change_target_price(self, target_price, user_id, item_id):
        """Run an UPDATE query to update user item target price."""
        # getting 3 values(user_id, item_id, target_price) and forming them into a tuple.
        vars = (target_price, user_id, item_id)
        update_command = '''UPDATE users_items
                            SET target_price = %s
                            WHERE user_id = %s AND item_id = %s'''
        count = self._insert(update_command, vars)
        logger.debug(f'Query is: {update_command}, the vars are{vars}.')
        if count:
            return count
        else:
            return False

    def check_for_target_price(self, item_id, target_price):
        """Run SELECT query for checking if target price isn`t higher then current price."""
        vars = (item_id, target_price)
        select_command = '''SELECT price
                            FROM prices
                            WHERE item_id = %s AND price > %s
                            ORDER BY time_stamp DESC LIMIT 1'''
        count = self.select_row_with_condition(select_command, vars)
        logger.debug(f'Query is: {select_command}, the vars are{vars}.')
        if count:
            return count
        else:
            return False

    def select_max_target_price(self, item_id):
        """Run SELECT query for checking if target price isn`t higher then current price."""
        vars = (item_id,)
        select_command = '''SELECT price
                            FROM prices
                            WHERE item_id = %s
                            ORDER BY time_stamp DESC'''
        record = self.select_row_with_vars(select_command, vars)
        logger.debug(f'Query is: {select_command}, the vars are{vars}.')
        if record:
            return record
        else:
            return False

    def select_all_uin(self):
        """Run SELECT all rows of in stock items from items to get a dict of id's and uin's."""
        query = "SELECT id, uin FROM items WHERE in_stock = true"
        records = self.select_rows(query)
        logger.debug(f'Records are: {records}.')
        return records

    def add_prices(self, item_id_and_price_list):
        """Run INSERT query for a list of tuples to add prices."""
        # getting 2 values (id, price).
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            for record in item_id_and_price_list:
                query = "INSERT INTO prices (item_id, price) VALUES (%s, %s)"
                vars = (record[0], record[1])
                cur.execute(query, vars)
                logger.debug(f"{cur.rowcount} rows about to be committed.")
            self.db.conn.commit()
            logger.debug("Committed function.")

    def check_for_lowest_price_and_update(self):
        """Run SELECT command for checking lowest price, if resulted with changes update lowest."""
        query = '''SELECT DISTINCT id, price
                    FROM items INNER JOIN prices ON item_id = id
                    WHERE price < lowest 
                    ORDER BY id'''
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            logger.debug(f'Query is: {query}.')
            records = cur.fetchall()

        if len(records) > 0:
            logger.debug(f'Len of records is {len(records)}.')
            with self.db.conn.cursor() as cur:
                for record in records:
                    vars = (record[1], record[0])
                    query = "UPDATE items SET lowest = %s WHERE id = %s"
                    cur.execute(query, vars)
                    logger.debug(f'Updating lowest price in items.')
                    logger.info(f'{cur.rowcount} rows affected.')
            self.db.conn.commit()
        logger.debug("Committed function.")

    def change_to_out_of_stock(self, item_id_list):
        """Run update for in stock column in items table."""
        query = '''UPDATE items 
                    SET in_stock = false
                    WHERE id in %s'''
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, (tuple(item_id_list),))
            self.db.conn.commit()
            logger.info(f"{cur.rowcount} rows affected.")

    def select_all_user_items(self, user_id):
        """Run SELECT query to get all the user items by user_id, returning list of dict objects."""
        # todo needs to get all items from items table after getting all items id ny user id
        query = '''SELECT i.id, i.in_stock AS stock, i.lowest AS lowest, ui.target_price AS target,
                    i.title AS description
                    FROM items AS i
                    LEFT JOIN users_items AS ui ON i.id = ui.item_id
                    WHERE ui.user_id = %s
                    ORDER BY id DESC'''
        vars = (user_id,)
        self.db.get_connection()
        with self.db.conn.cursor(cursor_factory=RealDictCursor) as cur:
            logger.debug(f'Query is: {query}.')
            cur.execute(query, vars)
            records = cur.fetchall()
            logger.info(f"{cur.rowcount} rows fetched.")

        return records

    def check_users_target_prices(self, item_id_list):
        """Run select query for checking if target price is reached, returns user_id, item_id for those who met
         the conditions."""
        query = '''SELECT DISTINCT ui.user_id,ui.item_id 
                    FROM users_items AS ui 
                    LEFT JOIN prices AS p ON p.item_id = ui.item_id 
                    WHERE ui.item_id in %s AND ui.target_price <= p.price 
                    ORDER BY ui.item_id'''
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            cur.execute(query, (tuple(item_id_list),))
            logger.debug(f'Query is: {query}.')
            records = cur.fetchall()
            logger.info(f"{cur.rowcount} rows fetched.")

        return records

    def check_users_for_out_of_stock_item(self, item_id):
        """Run select query for all the users to notify, returns the list."""
        query = "SELECT user_id FROM users_items WHERE item_id = %s"
        vars = (item_id,)
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            logger.debug(f'Query is: {query}.')
            cur.execute(query, vars)
            records = cur.fetchall()
            logger.info(f"{cur.rowcount} rows fetched.")

        return records

    def select_emails_to_notify(self, users_id_list):
        """Run select query to get users mails from id's."""
        query = 'SELECT email FROM users WHERE id IN %s'
        self.db.get_connection()
        with self.db.conn.cursor() as cur:
            logger.debug(f'Query is: {query}.')
            cur.execute(query, (tuple(users_id_list),))
            records = cur.fetchall()
            logger.info(f"{cur.rowcount} rows fetched.")

        return records

    def select_emails_for_out_of_stock_items(self, items_id_list):
        """Run SELECT query to get users email and item title for each out of stock item id,
        returning tuples with .title and .emails."""
        query = '''SELECT DISTINCT i.title, string_agg(u.email, ', ') AS emails FROM items AS i
                    LEFT JOIN users_items AS ui ON ui.item_id = i.id
                    LEFT JOIN users AS u ON u.id = ui.user_id
                    WHERE i.id IN %s AND u.email IS NOT null
                    GROUP BY i.title'''
        self.db.get_connection()
        with self.db.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute(query, (tuple(items_id_list),))
            logger.debug(f'Query is: {query}.')
            records = cur.fetchall()
            logger.info(f"{cur.rowcount} rows fetched.")

        return records
