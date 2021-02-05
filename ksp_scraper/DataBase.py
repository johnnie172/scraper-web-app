import psycopg2
from psycopg2.extras import DictCursor
import consts
import db_config
import logging

logger = logging.getLogger(__name__)


class DataBase:
    """PostgreSQL Database class."""

    def __init__(self, db_config):
        self.host = db_config.DATABASE_HOST
        self.username = db_config.DATABASE_USERNAME
        self.password = db_config.DATABASE_PASSWORD
        self.port = db_config.DATABASE_PORT
        self.dbname = db_config.DATABASE_NAME
        self.conn = None

    def _db_setup(self):
        """Set up the postgres database."""
        self.get_connection()
        sql_file = open(db_config.DATABASE_TABLES_SETUP_FILE, 'r')
        with self.conn.cursor() as cur:
            cur.execute(sql_file.read())
            self.conn.commit()
        logger.info(f'The script {db_config.DATABASE_TABLES_SETUP_FILE} has run.')

    def _connect(self):
        """Connect to a Postgres database."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                port=self.port,
                dbname=self.dbname
            )
        except psycopg2.DatabaseError as e:
            logger.error(e)
            raise e
        logger.info('Connection opened successfully.')

    def get_connection(self):
        """Returning connection item if None is exist"""
        if self.conn is None or self.conn.closed != 0:
            self._connect()
        logger.debug(f'The connection object is: {self.conn}.')
        return self.conn
