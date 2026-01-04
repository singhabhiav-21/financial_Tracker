from databaseDAO.sqlConnector import get_connection
from databaseDAO.userDAO import hashAgain

conn = get_connection()
cursor = conn.cursor()


def addAccount(userid, name, type, balance, currency, platform_name):
    """Add a new account for a user"""
    balance, balance_msg = check_balance(balance)
    if balance is False:
        print(f"Balance validation failed: {balance_msg}")
        return False

    type, type_msg = checkaccountType(type)
    if type is False:
        print(f"Account type validation failed: {type_msg}")
        return False

    try:
        query = ("INSERT INTO account (user_id, account_name, account_type, account_balance, currency, platform_name) "
                 "VALUES (%s,%s,%s,%s,%s,%s)")
        cursor.execute(query, (userid, name, type, balance, currency, platform_name))
        conn.commit()
        print(f"Account '{name}' added successfully for user {userid}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding account: {e}")
        return False


def check_balance(balance):
    """Validate account balance"""
    # Accept both int and float
    if not isinstance(balance, (int, float)):
        return False, "The balance must be a number"
    elif balance < 0 or balance > 10000000:
        return False, "The balance should be between 0 and 10,000,000"
    else:
        return float(balance), "Balance valid"


def checkaccountType(actype: str):
    """Validate account type"""
    accountType = ["savings",
                   "current",
                   "fixed deposit",
                   "recurring deposit",
                   "joint",
                   "student",
                   "basic/zero-balance",
                   "stocks",
                   "crypto"
                   ]
    if actype.lower() not in accountType:
        return False, f"Invalid account type. Must be one of: {', '.join(accountType)}"
    return actype.lower(), "Account type valid"


def delete_account(accountId, password):
    """Delete an account after password verification"""
    try:
        query = "SELECT user_id FROM account WHERE account_id = %s"
        cursor.execute(query, (accountId,))
        row = cursor.fetchone()

        if not row:
            print(f"No account found with ID {accountId}")
            return False

        user_id = row[0]

        cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()

        if not row:
            print(f"No user found with ID {user_id}")
            return False

        storedPw = row[0]
        salt, realhashPw = storedPw.split(":")
        password_hash = hashAgain(salt, password)

        if realhashPw == password_hash:
            query = "DELETE FROM account WHERE account_id = %s"
            cursor.execute(query, (accountId,))
            conn.commit()
            print(f"Account {accountId} deleted successfully")
            return True
        else:
            print("Incorrect password")
            return False

    except Exception as e:
        conn.rollback()
        print(f"Error deleting account: {e}")
        return False


def update_account(account_id, userid, name=None, accountType=None, balance=None, currency=None, platform_name=None):
    """Update an existing account"""
    try:
        query = "SELECT * FROM account WHERE account_id = %s AND user_id = %s"
        cursor.execute(query, (account_id, userid))
        row = cursor.fetchone()

        if not row:
            print(f"No account found with ID {account_id} for user {userid}")
            return False

        update = []
        value = []

        if name:
            update.append("account_name = %s")
            value.append(name)

        if accountType:
            validated_type, type_msg = checkaccountType(accountType)
            if validated_type is False:
                print(f"Account type validation failed: {type_msg}")
                return False
            update.append("account_type = %s")
            value.append(validated_type)

        if balance is not None:
            validated_balance, balance_msg = check_balance(balance)
            if validated_balance is False:
                print(f"Balance validation failed: {balance_msg}")
                return False
            update.append("account_balance = %s")
            value.append(validated_balance)

        if currency:
            update.append("currency = %s")
            value.append(currency)

        if platform_name:
            update.append("platform_name = %s")
            value.append(platform_name)

        if not update:
            print("No changes provided to update")
            return False

        # Add account_id to the end of values for WHERE clause
        value.append(account_id)

        query = f"UPDATE account SET {', '.join(update)} WHERE account_id = %s"
        cursor.execute(query, tuple(value))
        conn.commit()
        print(f"Account {account_id} updated successfully")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error updating account: {e}")
        return False


def add_money(user_id, account_id, credits: int):
    """Add money to an account"""
    if not isinstance(credits, (int, float)):
        print("Amount must be a number")
        return False

    if credits < 0 or credits > 10000000:
        print("Amount must be between 0 and 10,000,000")
        return False

    try:
        query = "UPDATE account SET account_balance = account_balance + %s WHERE account_id = %s AND user_id = %s"
        cursor.execute(query, (credits, account_id, user_id))
        conn.commit()
        print(f"Added {credits} to account {account_id}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding money: {e}")
        return False


def transfer_money(user_id, account_id1, account_id2, credits: int):
    try:
        query = "SELECT account_balance FROM account WHERE account_id = %s AND user_id = %s"
        cursor.execute(query, (account_id1, user_id))
        row = cursor.fetchone()

        if not row:
            print(f"Source account {account_id1} not found")
            return False

        balance = row[0]
        if balance < credits:
            print(f"Insufficient funds. Balance: {balance}, Required: {credits}")
            return False

        query1 = "UPDATE account SET account_balance = account_balance - %s WHERE account_id = %s AND user_id = %s"
        cursor.execute(query1, (credits, account_id1, user_id))

        query2 = "UPDATE account SET account_balance = account_balance + %s WHERE account_id = %s AND user_id = %s"
        cursor.execute(query2, (credits, account_id2, user_id))
        conn.commit()
        print(f"Transferred {credits} from account {account_id1} to {account_id2}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error transferring money: {e}")
        return False