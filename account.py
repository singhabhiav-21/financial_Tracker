class Account:
    def __init__(self, account_id, user_id, account_name, account_type, account_balance, currency, created_at=None):
        self.account_id = account_id
        self.user_id = user_id
        self.account_name = account_name
        self.account_type = account_type
        self.account_balance = account_balance
        self.currency = currency
        self.created_at = created_at
