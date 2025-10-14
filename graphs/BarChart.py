from financial_Tracker.databaseDAO.sqlConnector import get_connection
import matplotlib as mb

conn = get_connection()
cursor = conn.cursor


def weekly_expenses(user, weeks=12):
    query = ("""
            SELECT DATE(transaction_date) as date,amount 
             FROM transactions 
             WHERE user_id = %s
             AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL %s WEEK )
             ORDER BY transaction_date ASC
             """)
    cursor.execute(query, (user, weeks))
    result = cursor.fetchall()
    if not result:
        print("User not Found!")
        return False

    dates = [row[0] for row in result]
    amounts = [float(row[1]) for row in result]

    return dates, amounts


def group_by_week(user, weeks=21):



