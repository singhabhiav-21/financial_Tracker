import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from databaseDAO.transaction.importcsv import bankImporter

from databaseDAO.transaction.importcsv import bankImporter

class Test_importCSV(unittest.TestCase):
    def test_import(self):
        user_id = 52
        importer = bankImporter(user_id=user_id, default_category_id=1)
        csv_path = "/Users/abhinavsingh/Money_tracker/financial_Tracker/databaseDAO/test/minkontoutdrag"
        print(f"Starting import for user {user_id}...")
        importer.import_csv(csv_path)

    def test_generate_hash_is_correct(self):
        importer = bankImporter(user_id=1)
        check1 = importer._generate_hash("1|grocery|-50.00|2025-10-15")
        check2 = importer._generate_hash("1|grocery|-50.00|2025-10-15")
        self.assertEqual(check1, check2)

    def test_generate_hash_is_different_for_different_values(self):
        importer = bankImporter(user_id=1)
        fail1 = importer._generate_hash("1|grocery|-50.00|2025-10-15")
        fail2 = importer._generate_hash("1|grocery|-90.00|2025-10-15")
        self.assertNotEqual(fail1, fail2)

    @patch("databaseDAO.transaction.importcsv.add_transaction_batch")
    @patch("databaseDAO.transaction.importcsv.pd.read_csv")
    def test_add_transaction_batch_is_zero(self, mock_csv, mock_batch):
        mock_csv.return_value = pd.DataFrame({
            'Value date': ['2025-10-15', '2025-10-16', '2025-10-17'],
            'Text': ['grocery store', 'gas station', 'coffee shop'],
            'Amount': ['-50.00', '-30.00', '-5.00']
        })
        mock_batch.return_value = 0
        importer = bankImporter(user_id=1)
        importer.import_csv("fake.csv")
        self.assertEqual(importer.imported_count, 0)
        self.assertEqual(importer.duplicate_count, 3)
