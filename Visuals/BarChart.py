import matplotlib.pyplot as plt

from financial_Tracker.databaseDAO.sqlConnector import get_connection

import numpy as np
import pandas as pd

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

    return result


def incoming_funds(amounts):
    total = 0
    for amount in amounts:
        if amount >= 0:
            total += amount
    return total


def outgoing_funds(amounts):
    total = 0
    for amount in amounts:
        if amount < 0:
            total += amount
    return total


def groupPlot_by_week(transactions):

    df = pd.DataFrame(transactions, columns=["Date", "Amount"])
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace= True)

    weekly = df.resample('W-MON').agg({
        'Amount': [outgoing_funds, incoming_funds]
    })

    weekly.columns = ['Income', 'Expenses']
    weekly = weekly.reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(weekly))
    width = 0.4
    ax.bar(x - width / 2, weekly['Income'], width, label='Income', color='green')
    ax.bar(x + width / 2, weekly['Expenses'], width, label='Expenses', color='red')

    ax.set_xlabel('Week Starting')
    ax.set_ylabel('Amount (kr)')
    ax.set_title('Weekly Income vs Expenses')
    ax.set_xticks(x)
    ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in weekly['date']], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# Usage
groupPlot_by_week(user_id=1, weeks=8)





