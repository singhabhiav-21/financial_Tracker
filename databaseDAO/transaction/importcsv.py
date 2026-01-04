from ..sqlConnector import get_connection
import pandas as pd
import hashlib

from ..transaction.transaction_DAO import register_transaction

conn = get_connection()
cursor = conn.cursor()


class bankImporter:
    def __init__(self, user_id, default_category_id=1):
        self.user_id = user_id
        self.processed_hashes = self._load_processed_hashes()
        print(
            f"DEBUG: processed_hashes type: {type(self.processed_hashes)}, value: {self.processed_hashes}")  # ADD THIS
        self.category_id = default_category_id

    def _load_processed_hashes(self):
        query = """
             SELECT DISTINCT CONCAT(description, '|', CAST(amount AS DECIMAL(12,2)), '|', transaction_date, '|', balance) as hash_key
        FROM transactions 
        WHERE user_id = %s
        """
        try:
            cursor.execute(query,(self.user_id,))
            rows = cursor.fetchall()
            hashes = set()
            print(f"\n=== LOADING EXISTING HASHES ===")
            print(f"Found {len(rows)} existing transactions in database")

            for row in rows:
                hash_key = row[0]
                if hash_key is None:
                    print(f"WARNING: Skipping None hash_key")
                    continue
                hash_value = self._generate_hash(hash_key)
                hashes.add(hash_value)
                if len(hashes) <= 5:
                    print(f"  Hash key: {hash_key}")
                    print(f"  Hash: {hash_value}")

            print(f"Total hashes loaded: {len(hashes)}\n")
            return hashes
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

            imported_c = 0
            duplicate_c = 0

            for index,row in file.iterrows():
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
                    balance = self._clean_amount(row['Balance'])

                    hash_key = f"{description}|{amount:.2f}|{transaction_date}|{balance:.2f}"
                    transaction_hash = self._generate_hash(hash_key)

                    if imported_c < 5:  # Only show first 5 for testing
                        print(f"\n--- Row {index} ---")
                        print(f"Hash key: {hash_key}")
                        print(f"Hash: {transaction_hash}")
                        print(f"Is duplicate? {transaction_hash in self.processed_hashes}")

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
                        balance=balance,
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


