from datetime import datetime

from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor


def create_catergory(user_id, name, type):
    now = datetime.now()

    query = "INSERT INTO category (user_id, name, type, created_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, name, type, now,))
    conn.commit()
    print("This category has been successfully created!")
    return True


def delete_category(category_id, user_id):
    query = "SELECT name FROM category WHERE category_id = %s AND user_id = %s"
    cursor.execute(query, (category_id, user_id))
    row = cursor.fetchone()
    if not row:
        print("The user does not have a category!")
        return False

    category_name = row[0]

    query1 = "DELETE FROM category WHERE category_id = %s AND user_id = %s"
    cursor.execute(query1, (category_id, user_id))
    conn.commit()
    print(f"The category {category_name} has been deleted!")
    return True


def update_category(category_id, user_id, name = None, type  = None):
    query = "SELECT category_id FROM category WHERE category_id = %s AND user_id = %s"
    cursor.execute(query, (category_id, user_id,))
    row = cursor.fetchone()
    if not row:
        print("The user does not have any category!")
        return False

    value = []
    update = []
    now = datetime.now()
    update.append("updated_on = %s")
    value.append(now)
    if name:
        update.append("name = %s")
        value.append(name)
    if type:
        update.append("type = %s")
        value.append(type)

    query = f"UPDATE category SET {', '.join(update)} WHERE category_id = %s AND user_id = %s"
    cursor.execute(query, (*value, category_id, user_id))
    conn.commit()
    print("This category has been successfully updated!")
    return True

