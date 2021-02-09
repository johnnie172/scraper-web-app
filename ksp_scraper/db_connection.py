import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)

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
