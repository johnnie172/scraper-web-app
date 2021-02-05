from DataBase import DataBase
from DBQueries import DBQueries
import db_config

_database = None


def get_db_queries():
    global _database
    if _database is None:
        _database = DataBase(db_config)
        _database.get_connection()
    return DBQueries(_database)
