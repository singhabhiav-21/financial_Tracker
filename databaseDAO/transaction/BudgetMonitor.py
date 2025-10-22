from financial_Tracker.databaseDAO.sqlConnector import get_connection
import pandas as pd

conn = get_connection()
cursor = conn.cursor()


def get_budget(user_id):
    query = """
    SELECT budget_id 
    FROM budget
    WHERE user_id = %s
    """
    cursor.execute(query, user_id,)
    result = cursor.fetchone()
    if not result:
        print("The user has no budget selected!")
    return result


def set_budget(budget_id, amount, month, year, repeat:bool):
