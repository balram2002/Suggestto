import sqlite3
from flask import g

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the current directory
db_path = os.path.join(BASE_DIR, "employee.db") 

def connect_to_Database():
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row 
    return sql

def get_database():
    if not hasattr(g, "employee_db"):
        g.employee_db = connect_to_Database()
    return g.employee_db    
