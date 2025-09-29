import csv
from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor

def get_csv(filepath):
    with open(filepath, newline="") as r:
        reader = csv.DictReader(r)
        for row in reader:
            return None