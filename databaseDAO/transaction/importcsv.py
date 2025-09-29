import csv
from financial_Tracker.databaseDAO.sqlConnector import get_connection
import pandas as pd
import hashlib


conn = get_connection()
cursor = conn.cursor

class bankImporter:
    def __init__(self, user_id):
        self.user_id = user_id
        self.processed_hashes = self._load_processed_hashes()

    def _load_processed_hashes(self):
        query = """
            SELECT DISTINCT CONCAT(description,'|' ,amount) as hash_key
            FROM transactions WHERE user_id = %s
        """
        try:
            cursor.execute(query,(self.user_id,))
            rows = cursor.fetchall()
            for row in rows:
                return self._generate_hash(row[0])
        except Exception as e:
            print(f"Error loading processed transactions: {e}")
            return set()

    def _generate_hash(self, transaction):
        return hashlib.sha256(transaction.encode()).hexdigest()[:16]

    def _clean_amount(self, amount):
        if pd.isna(amount):
            return 0.0
        amount_clean = str(amount).replace(',', '').strip()
        return float(amount_clean)

    def