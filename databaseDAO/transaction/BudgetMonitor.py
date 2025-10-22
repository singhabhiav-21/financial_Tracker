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


def set_budget(user_id, category_id, amount, month, year, repeat: bool):
    query = """
    INSERT INTO budget(category_id, amount, month, year) VALUES (%s,%s,%s,%s)
    WHERE budget_id = %s
    """
    if amount <= 0:
        print("the amount cannot be less than or equal to 0")
        return False
    if month > 12 and month < 1:
        print("The month cannot be less than 1 or greater than 12")
        return False
    budget_id = get_budget(user_id)
    cursor.execute(query, (category_id, amount, month, year, budget_id))
    if repeat:
        repeat_budget(budget_id, category_id, amount)
    else:
        pass
    return True


def repeat_budget(budget_id, category_id, amount):



