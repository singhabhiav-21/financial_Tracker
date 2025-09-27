from financial_Tracker.databaseDAO.sqlConnector import get_connection
import datetime
conn = get_connection()
cursor = conn.cursor

def register_transaction(user_id, name, amount, description):
    now = datetime.datetime
    query = "INSERT INTO (user_id, name, amount, description, created_at)"
    cursor.execute(query, (user_id, name, amount, description, now))
    conn.commit()
    print("transaction registered!")
    return True

