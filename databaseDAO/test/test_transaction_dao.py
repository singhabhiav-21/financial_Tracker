import unittest
from unittest.mock import MagicMock, patch
from databaseDAO.transaction.transaction_DAO import (
    register_transaction,
    delete_transaction,
    update_transaction,
    get_transaction, get_all_transactions
)


class TestTransactionDAO(unittest.TestCase):
    def setUp(self):
        self.db_patcher = patch('databaseDAO.transaction.transaction_DAO.db')
        self.mock_db = self.db_patcher.start()

        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_db_cm = MagicMock()
        mock_db_cm.__enter__ = MagicMock(return_value=(self.mock_conn, self.mock_cursor))
        mock_db_cm.__exit__ = MagicMock(return_value=False)
        self.mock_db.return_value = mock_db_cm

    def test_register_transaction_success(self):
        result = register_transaction(
            user_id=1,
            category_id=2,
            name="Grocery",
            amount=50.00,
            description="Weekly groceries",
            transaction_date="2025-10-15"
        )
        self.assertTrue(result)

    def test_register_transaction_without_date(self):
        result = register_transaction(
            user_id=1,
            category_id=2,
            name="Grocery",
            amount=50.00,
            description="Weekly groceries"
        )
        self.assertTrue(result)

    def test_delete_transaction_success(self):
        result = delete_transaction(transaction_id=1, user_id=1)
        self.assertTrue(result)


    def test_update_transaction_success(self):
        self.mock_cursor.fetchone.return_value = (1, 1, 2, "Old Name", 50.00, "Old desc", "2025-10-15", "2025-10-15")

        result = update_transaction(
            transaction_id=1,
            user_id=1,
            name="New Name",
            amount=75.00
        )

        self.assertTrue(result)


    def test_update_transaction_not_found(self):
        self.mock_cursor.fetchone.return_value = None

        result = update_transaction(
            transaction_id=999,
            user_id=1,
            name="New Name"
        )

        self.assertFalse(result)


    def test_update_transaction_no_changes(self):
        self.mock_cursor.fetchone.return_value = (1, 1, 2, "Name", 50.00, "desc", "2025-10-15", "2025-10-15")

        result = update_transaction(
            transaction_id=1,
            user_id=1
        )

        self.assertFalse(result)


    def test_update_transaction_invalid_amount(self):
        self.mock_cursor.fetchone.return_value = (1, 1, 2, "Name", 50.00, "desc", "2025-10-15", "2025-10-15")

        result = update_transaction(
            transaction_id=1,
            user_id=1,
            amount="invalid"
        )

        self.assertFalse(result)

    def test_get_transaction_success(self):
        self.mock_cursor.fetchone.return_value = ("Grocery", 50.00, "Weekly groceries", "2025-10-15")

        result = get_transaction(transaction_id=1, user_id=1)

        self.assertEqual(result[0], "Grocery")
        self.assertEqual(result[1], 50.00)
        self.assertNotEqual(result, False)

    def test_get_transaction_not_found(self):
        self.mock_cursor.fetchone.return_value = None

        result = get_transaction(transaction_id=999, user_id=1)

        self.assertFalse(result)

    def test_get_transaction_for_correct_user(self):
        user1_data = [{"transaction_id": 1, "user_id": 1, "name": "Grocery", "amount": 50.00},
                      {"transaction_id": 2, "user_id": 1, "name": "Gas", "amount": 30.00}]

        user2_data = [{"transaction_id": 3, "user_id": 2, "name": "Coffee", "amount": 5.00}]

        self.mock_cursor.fetchall.return_value = user1_data
        check1 = get_all_transactions(user_id=1)
        self.assertEqual(check1, user1_data)
        self.assertNotIn({"transaction_id": 3, "user_id": 2, "name": "Coffee", "amount": 5.00}, check1)

    def tearDown(self):
        self.db_patcher.stop()


if __name__ == '__main__':
    unittest.main()