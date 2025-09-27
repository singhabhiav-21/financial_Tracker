from financial_Tracker.databaseDAO.sqlConnector import get_connection
import datetime
conn = get_connection()
cursor = conn.cursor

def register_transaction(user_id, category_id,name, amount, description):
    now = datetime.datetime
    query = "INSERT INTO (user_id, category_id, name, amount, description, created_at) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query, (user_id,category_id,name, amount, description, now))
    conn.commit()
    print("transaction registered!")
    return True


def delete_transaction(transaction_id, user_id):
    query = "DELETE transaction_id WHERE transaction_id = %s AND user_id = %s"
    cursor.execute(query, (transaction_id, user_id,))
    conn.commit()
    print("The transaction has been deleted!!")
    return True


def update_transaction(transaction_id, user_id, category_id=None, name=None, amount=None, description=None):
    query = "SELECT * FROM transactions WHERE transaction_id = %s AND user_id = %s"
    cursor.execute(query, (transaction_id, user_id,))
    row = cursor.fetchone()
    if not row:
        print("No transaction found for this user.")
        return False

    updates = []
    values = []

    if category_id is not None:
        updates.append("category_id = %s")
        values.append(category_id)
    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if amount is not None:
        if not isinstance(amount, (int, float)) or amount <= 0:
            print("Invalid amount.")
            return False
        updates.append("amount = %s")
        values.append(amount)
    if description is not None:
        updates.append("description = %s")
        values.append(description)

    if not updates:
        print("No changes were provided!")
        return False

    query = f"UPDATE transactions SET {', '.join(updates)} WHERE transaction_id = %s AND user_id = %s"
    values.extend([transaction_id, user_id])

    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        print("Transaction updated successfully.")
        return True
    except Exception as e:
        conn.rollback()
        print("Error updating transaction:", e)
        return False


def get_transaction(transaction_id, user_id):
    query = "SELECT * FROM transactions WHERE transaction_id = %s AND user_id = %s"
    cursor.execute(query, (transaction_id, user_id))
    rows = cursor.fetchall
    if not rows:
        print("No transaction found for this user.")
        return False
    return rows
