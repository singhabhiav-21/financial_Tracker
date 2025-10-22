from financial_Tracker.databaseDAO.sqlConnector import get_connection
import pandas as pd

conn = get_connection()
corsor = conn.cursor()

def set_budget(user_id, budget):
    query = "SELECT"