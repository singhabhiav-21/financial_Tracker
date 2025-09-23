from financial_Tracker.databaseDAO.sqlConnector import get_connection

conn = get_connection()
cursor = conn.cursor()


def addAccount(userid, name, type, balance, currency, platform_name):
    query = ("INSERT INTO account (user_id, account_name, account_type, account_balance, currency, platform__name) "
             "VALUES (%s,%s,%s,%s,%s)")
    balance = check_balance(balance)
    type = checkaccountType(type)
    cursor.execute(query, (userid, name, type, balance, currency, platform_name))
    conn.commit()
    return True


def check_balance(balance: int):
    if balance is not int:
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



def delete_account(accountId): return