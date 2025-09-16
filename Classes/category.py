class Category:
    def __init__(self, category_id, user_id, name, type, created_at=None, updated_on=None):
        self._category_id = category_id
        self._user_id = user_id
        self._name = name
        self._type = type
        self._created_at = created_at
        self._updated_on = updated_on
