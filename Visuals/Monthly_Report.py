import reportlab
import pandas as pd
from PyQt5.QtSql import transaction
from numba.scripts.generate_lower_listing import description
from sympy.physics.units import amount

from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor


def get_data(user_id, month):
    query = """
    SELECT transaction_date,
        amount,
        name,
        description
    FROM transactions
    WHERE user_id = %s AND DATE_FORMAT(transaction_date, '%Y-%m') = %s
    ORDER BY transaction_date
    """
    cursor.execute(query, (user_id, month))
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    if not result:
        print("The user has no data!(visual)")
        return False

    df = pd.DataFrame(result, columns=['transaction_date', 'name', 'amount', 'description'])
    return df


def get_spent(df):
    daily_spending = df.groupby('transaction_date')['amount'].sum().reset_index()
    sorted_df = daily_spending.sort_values(by='amount', ascending=False)
    max_row = sorted_df.iloc[0]
    formatted_max = {
        'transaction_date': max_row['transaction_date'],
        'name': max_row['name'],
        'amount': max_row['amount']
    }
    return formatted_max


def get_all_transactions(df):
    all_transactions = df.sort_values(by='transaction_date', ascending=True)
    formatted_all_transaction = {
        'transaction_date': all_transactions['transaction_date'],
        'name': all_transactions['name'],
        'amount': all_transactions['amount'],
        'description': all_transactions['description']
    }
    return formatted_all_transaction



