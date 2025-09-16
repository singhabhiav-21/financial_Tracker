class Transaction:
    def __init__(self, transaction_id, user_id, category_id, name, amount, description=None, created_at=None):
        self._transaction_id = transaction_id
        self._user_id = user_id
        self._category_id = category_id
        self._name = name
        self._amount = amount
        self._description = description
        self._created_at = created_at
