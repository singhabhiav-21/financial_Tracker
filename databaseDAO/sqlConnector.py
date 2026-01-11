import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', os.environ.get("MYSQL_USER")),
        password=os.getenv('DB_PASSWORD', os.environ.get("MYSQL_PASSWORD")),
        database=os.getenv('DB_NAME', os.environ.get("MYSQL_DB"))
    )