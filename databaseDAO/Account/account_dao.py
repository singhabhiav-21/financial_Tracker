from holoviews.examples.gallery.apps.bokeh.nytaxi_hover import vline

from financial_Tracker.databaseDAO.sqlConnector import get_connection
from financial_Tracker.databaseDAO.userDAO import hashAgain

conn = get_connection()
cursor = conn.cursor()


def addAccount(userid, name, type, balance, currency, platform_name):
    query = ("INSERT INTO account (user_id, account_name, account_type, account_balance, currency, platform_name) "
             "VALUES (%s,%s,%s,%s,%s)")
    balance, msg = check_balance(balance)
    type, msg = checkaccountType(type)
    cursor.execute(query, (userid, name, type, balance, currency, platform_name))
    conn.commit()
    return True


def check_balance(balance: int):
    if not isinstance(balance, int):
        return False, "The input should be an integer"
    elif 0 > balance or balance > 10000000:
        return False, "The balance should be between 0 and 10000000"
    else:
        return balance, "Balance added!"


def checkaccountType(actype: str):
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
        return False, "Account Type invalid!"
    else:
        return True, "Account Type acceptable!"


def delete_account(accountId, password):
    query = "SELECT user_id FROM account WHERE account_id = %s"
    cursor.execute(query,(accountId,))
    row = cursor.fetchone()
    if not row:
        return False, "No account associated with this user."
    user_id = row[0]

    cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    storedPw = row[0]
    salt, realhashPw = storedPw.split(":")
    Password_hash = hashAgain(salt, password)

    if realhashPw == Password_hash:
        query = "DELETE FROM account WHERE account_id = %s"
        cursor.execute(query, (accountId,))
        conn.commit()
        print("The account has been deleted!")
        return True
    else:
        print("The password is incorrect!")
        return False


def update_account(account_id, userid,name = None, accountType = None, balance = None, currency = None, platform_name = None):
    query = "SELECT * FROM account WHERE account_id = %s AND user_id = %s"
    cursor.execute(query,(account_id, userid))
    row = cursor.fetchone()
    if not row:
        print("No account associated with this user")
        return False

    update = []
    value = []

    if name:
        update.append("account_name = %s")
        value.append(name)
    if accountType:
        if not checkaccountType(accountType):
            print("Check account type")
            return False
        update.append("account_type = %s")
        value.append(accountType)
    if balance:
        if not check_balance(balance):
            print("Incorrect Balance input")
            return False
        update.append("account_balance = %s")
        value.append(balance)
    if currency:
        update.append("currency = %s")
        value.append(currency)
    if platform_name:
        update.append("platform_name = %s")
        value.append(platform_name)

    if not update:
        print("No changes were made/given.")
        return False

    query = f"UPDATE account SET {', '.join(update)} where account_id = %s"
    cursor.execute(query, tuple(value))
    conn.commit()
    print("The changes were successfully made")
    return True


def add_money(user_id, account_id, credits: int):
    if not isinstance(credits, int):
        print("Please enter an integer!")
        return False
    if credits < 0 or 10000000 < credits:
        print("The amount added can only be between 0 and 10 million!")
    else:
        query = "UPDATE account SET account_balance = account_balance + %s WHERE account_id = %s AND user_id = %s "
        cursor.execute(query, (credits, account_id, user_id))
        conn.commit()
        print("The balance has been updated")
        return True


def transfer_money(user_id, account_id1, account_id2 ,credits: int):
    query = "SELECT account_balance FROM account WHERE account_id = %s AND user_id = %s"
    cursor.execute(query, (account_id1,user_id))
    row = cursor.fetchone()
    if not row:
        print("The user has no accounts")
        return False

    balance = row[0]
    if balance < credits:
        print("This account does not have enough funds!!")
        return False

    query1 = "UPDATE account SET account_balance = account_balance - %s WHERE account_id = %s AND user_id = %s"
    cursor.execute(query1,(credits,account_id1,user_id))

    query2 = "UPDATE account SET account_balance  = account_balance  + %s WHERE account_id = %s AND user_id = %s"
    cursor.execute(query2,(credits, account_id2, user_id))
    conn.commit()
    print("Transfer successful")
    return True

