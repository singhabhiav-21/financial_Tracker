from databaseDAO.sqlConnector import get_connection
from mysql.connector import Error
import pandas as pd
import hashlib
from decimal import Decimal,InvalidOperation

from transaction.transaction_DAO import register_transaction

conn = get_connection()
cursor = conn.cursor()


class bankImporter:
    def __init__(self, user_id, default_category_id=1):
        self.user_id = user_id
        self.category_id = default_category_id

        # Initialize counters
        self.imported_count = 0
        self.duplicate_count = 0

    def _generate_hash(self, transaction):
        return hashlib.sha256(transaction.encode()).hexdigest()

    def _clean_amount(self, amount):
        if pd.isna(amount):
            raise ValueError("Amount is missing")
        amount_clean = str(amount).replace(',', '').strip()
        return amount_clean

    def import_csv(self, file_path: str):
        try:
            # Read CSV with flexible parsing - handle various delimiters and quoted headers
            file = pd.read_csv(file_path, sep=None, engine='python', skipinitialspace=True, quotechar='"')

            # Strip whitespace and quotes from column names
            file.columns = file.columns.str.strip().str.strip('"\'')

            print(f"DEBUG: All CSV columns detected: {list(file.columns)}")
            print(f"DEBUG: Total rows read by pandas: {len(file)}")

            # Show first few rows for debugging
            if len(file) > 0:
                print(f"DEBUG: First row data:")
                print(file.head(1).to_dict('records'))

            # Check for required columns (but allow extra columns)
            required_columns = ['Value date', 'Text', 'Amount']
            missing_columns = []

            for col in required_columns:
                if col not in file.columns:
                    missing_columns.append(col)

            if missing_columns:
                print(f"Error: Missing required columns: {missing_columns}")
                print(f"Available columns: {list(file.columns)}")
                print(f"Expected columns: {required_columns}")
                return None

            print(f"DEBUG: All required columns found! Extra columns will be ignored.")

            # Check for NA values in required columns before dropping
            print(f"DEBUG: NA counts in required columns:")
            for col in required_columns:
                na_count = file[col].isna().sum()
                print(f"  {col}: {na_count} NA values")

            initial_count = len(file)
            file = file.dropna(subset=required_columns)
            dropped_count = initial_count - len(file)

            if dropped_count > 0:
                print(f"DEBUG: Dropped {dropped_count} rows with missing data in required columns")

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
                        get_description = str(row["Text"])
                        try:
                            description = " ".join(get_description.lower().split())
                        except Exception as e:
                            print(f"Row {index}: Error reading description - {e}")
                            continue
                    except KeyError:
                        print(f"Row {index}: Missing 'Text' column")
                        continue
                    try:
                        if pd.isna(row['Amount']):
                            print(f"Row{index}:: Skipping - missing amount")
                            continue
                        get_amount = self._clean_amount(row['Amount'])
                        try:
                            amount = Decimal(str(get_amount)).quantize(Decimal("0.01"))
                        except (InvalidOperation, ValueError) as e:
                            print(f"Row {index}: Invalid amount '{raw_amount}' - {e}")
                            continue
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
                        date = row["Value date"]
                        try:
                            transaction_date = pd.to_datetime(date, errors="raise").strftime("%Y-%m-%d")
                        except Exception:
                            print(f"Invalid date format: {date}")
                            continue
                    except KeyError:
                        print(f"Row {index}: Missing 'Value date' column")
                        continue
                    except Exception as e:
                        print(f"Row {index}: Invalid date format for '{description[:30]}' - {e}")
                        continue
                    try:
                        balance = self._clean_amount(row['Balance']) if 'Balance' in row else 0.0
                    except:
                        balance = 0.0

                    # Include user_id in the hash
                    hash_key = f"{self.user_id}|{description}|{amount:.2f}|{transaction_date}"
                    transaction_hash = self._generate_hash(hash_key)

                    if self.imported_count < 5:  # Only show first 5 for testing
                        print(f"\n--- Row {index} ---")
                        print(f"Hash key: {hash_key}")
                        print(f"Hash: {transaction_hash}")

                    try:
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
                    except Error as e:
                        if e.errno == 1062:
                            self.duplicate_count += 1
                            print(f"Duplicate transaction skipped (DB constraint): {description[:40]}")
                        else:
                            print(f"Database error for transaction '{description[:40]}': {e}")
                            raise

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
            raise
