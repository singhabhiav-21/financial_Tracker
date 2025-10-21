from financial_Tracker.databaseDAO.sqlConnector import get_connection
import pandas as pd
import hashlib

from financial_Tracker.databaseDAO.transaction.transaction_DAO import register_transaction

conn = get_connection()
cursor = conn.cursor


class bankImporter:
    def __init__(self, user_id, default_category_id=1):
        self.user_id = user_id
        self.processed_hashes = self._load_processed_hashes()
        self.category_id = default_category_id

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

    def import_csv(self, file_path: str):
        try:
            file = pd.read_csv(file_path)
            required_columns = ['Value date', 'Text', 'Amount']
            missing_column = []
            for col in required_columns:
                if col not in file.columns:
                    missing_column.append(col)

            if missing_column:
                print(f"Error missing columns:  {missing_column} Expected (Value date, Text, Amount)")
                return None

            file = file.dropna(subset=required_columns)
            print(f"Processing {len(file)} transactions...")

            imported_c = 0
            duplicate_c = 0

            for index,row in file.iterrows():
                try:
                    description = str(row["Text"]).strip()
                    amount = self._clean_amount(row['amount'])
                    transaction_date = row["Value date"]

                    hash_key = f"{description}|{amount}"
                    transaction_hash = self._generate_hash(hash_key)

                    if transaction_hash in self.processed_hashes:
                        duplicate_c += 1
                        continue

                    new_transaction = register_transaction(
                        user_id=self.user_id,
                        category_id=self.category_id,
                        name=description[:25],
                        amount=amount,
                        description=description[:225],
                        transaction_date=transaction_date,
                    )
                    if new_transaction:
                        self.processed_hashes.add(transaction_hash)
                        imported_c += 1
                        print(f"{'CREDIT' if amount > 0 else 'DEBIT'}: {description[:40]} | {amount:.2f}kr")

                except Exception as e:
                    print(f"Error processing transaction: {e}")
                    continue

                print(f"\nImport Complete:")
                print(f"  Imported: {imported_c} transactions")
                print(f"  Duplicates skipped: {duplicate_c}")

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return 0

        except Exception as e:
            print(f"Error: {e}")
            return 0


