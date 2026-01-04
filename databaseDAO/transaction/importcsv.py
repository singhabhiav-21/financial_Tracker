from ..sqlConnector import get_connection
import pandas as pd
import hashlib

from ..transaction.transaction_DAO import register_transaction

conn = get_connection()
cursor = conn.cursor()


class bankImporter:
    def __init__(self, user_id, default_category_id=1):
        self.user_id = user_id
        self.category_id = default_category_id

        # Initialize counters
        self.imported_count = 0
        self.duplicate_count = 0

    def _check_duplicate(self, transaction_hash):
        query = """
            SELECT COUNT(*)
            FROM transactions
            WHERE user_id = %s AND transaction_hash = %s
                """
        try:
            cursor.execute(query, (self.user_id, transaction_hash,))
            result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            print(f"Error loading processed transactions: {e}")
            return False

    def _generate_hash(self, transaction):
        return hashlib.sha256(transaction.encode()).hexdigest()[:16]

    def _clean_amount(self, amount):
        if pd.isna(amount):
            return 0.0
        amount_clean = str(amount).replace(',', '').strip()
        return float(amount_clean)

    def import_csv(self, file_path: str):
        try:
            file = pd.read_csv(file_path, sep=None, engine='python')
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

            # Reset counters
            self.imported_count = 0
            self.duplicate_count = 0

            for index, row in file.iterrows():
                try:
                    try:
                        if pd.isna(row['Text']) or str(row["Text"]).strip() == "":
                            print(f"Row {index}: Skipping - missing description")
                            continue
                        description = str(row["Text"]).strip()
                    except KeyError:
                        print(f"Row {index}: Missing 'Text' column")
                        continue
                    except Exception as e:
                        print(f"Row {index}: Error reading description - {e}")
                        continue
                    try:
                        if pd.isna(row['Amount']):
                            print(f"Row{index}:: Skipping - missing amount")
                            continue
                        amount = self._clean_amount(row['Amount'])
                    except KeyError:
                        print(f"Row {index}: Missing 'Amount' column")
                        continue
                    except (ValueError, TypeError) as e:
                        print(f"Row {index}: Invalid amount format for '{description[:30]}' - {e}")
                        continue
                    except Exception as e:
                        print(f"Row {index}: Error processing amount - {e}")
                        continue
                    try:
                        if pd.isna(row["Value date"]):
                            print(f"Row {index}: Skipping - missing date for '{description[:30]}'")
                            continue
                        transaction_date = row["Value date"]
                    except KeyError:
                        print(f"Row {index}: Missing 'Value date' column")
                        continue
                    except Exception as e:
                        print(f"Row {index}: Invalid date format for '{description[:30]}' - {e}")
                        continue

                    # Handle Balance column - it may not exist in all CSVs
                    try:
                        balance = self._clean_amount(row['Balance']) if 'Balance' in row else 0.0
                    except:
                        balance = 0.0

                    # Include user_id in the hash
                    hash_key = f"{self.user_id}|{description}|{amount:.2f}|{transaction_date}|{balance:.2f}"
                    transaction_hash = self._generate_hash(hash_key)
                    if self.imported_count < 5:  # Only show first 5 for testing
                        print(f"\n--- Row {index} ---")
                        print(f"Hash key: {hash_key}")
                        print(f"Hash: {transaction_hash}")

                    if self._check_duplicate(transaction_hash):
                        self.duplicate_count += 1
                        if self.imported_count < 5:
                            print(f"Is duplicate? Yes")
                        continue

                    if self.imported_count < 5:
                        print(f"Is duplicate? False (not in database)")

                    new_transaction = register_transaction(
                        user_id=self.user_id,
                        category_id=self.category_id,
                        name=description[:25],
                        amount=amount,
                        description=description[:225],
                        transaction_date=transaction_date,
                        balance=balance,
                        transaction_hash=transaction_hash,
                    )
                    if new_transaction:
                        self.imported_count += 1
                        print(f"{'CREDIT' if amount > 0 else 'DEBIT'}: {description[:40]} | {amount:.2f}kr")

                except Exception as e:
                    print(f"Error processing transaction: {e}")
                    continue

            print(f"\nImport Complete:")
            print(f"  Imported: {self.imported_count} transactions")
            print(f"  Duplicates skipped: {self.duplicate_count}")

            return True

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return False

        except Exception as e:
            print(f"Error: {e}")
            return False