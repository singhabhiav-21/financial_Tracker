from financial_Tracker.databaseDAO.sqlConnector import get_connection
import random
from datetime import datetime, timedelta
import hashlib
import os


def create_sample_user(name, email, password):
    """
    Create a sample user with hashed password

    Args:
        name: Name for the user
        email: Email for the user
        password: Plain text password (will be hashed)

    Returns:
        user_id if successful, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Generate salt and hash password (matching your userDAO format)
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    stored_password = salt + ":" + hashed

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"

    try:
        cursor.execute(query, (name, email, stored_password))
        conn.commit()

        # Get the newly created user_id
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]

        print(f"✓ User created: {name} (ID: {user_id})")
        print(f"  Email: {email}")
        print(f"  Password: {password}")

        cursor.close()
        conn.close()
        return user_id
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return None


def create_sample_categories(user_id):
    """
    Create sample categories for a user

    Args:
        user_id: The user ID to create categories for

    Returns:
        List of category IDs created
    """
    conn = get_connection()
    cursor = conn.cursor()

    categories = [
        {'name': 'Food & Groceries', 'type': 'expense'},
        {'name': 'Transportation', 'type': 'expense'},
        {'name': 'Entertainment', 'type': 'expense'},
        {'name': 'Shopping', 'type': 'expense'},
        {'name': 'Bills & Utilities', 'type': 'expense'},
    ]

    category_ids = []
    now = datetime.now()

    for cat in categories:
        query = """
        INSERT INTO category 
        (user_id, name, type, created_at) 
        VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(query, (
                user_id,
                cat['name'],
                cat['type'],
                now
            ))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            category_id = cursor.fetchone()[0]
            category_ids.append(category_id)

            print(f"  ✓ Category created: {cat['name']} (ID: {category_id})")
        except Exception as e:
            print(f"  ✗ Error creating category {cat['name']}: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    return category_ids


def create_sample_accounts(user_id):
    """
    Create sample accounts for a user

    Args:
        user_id: The user ID to create accounts for

    Returns:
        List of account IDs created
    """
    conn = get_connection()
    cursor = conn.cursor()

    accounts = [
        {
            'name': 'Main Checking',
            'type': 'current',
            'balance': 2500.00,
            'currency': 'USD',
            'platform': 'Chase Bank'
        },
        {
            'name': 'Savings Account',
            'type': 'savings',
            'balance': 15000.00,
            'currency': 'USD',
            'platform': 'Bank of America'
        },
        {
            'name': 'Investment Account',
            'type': 'stocks',
            'balance': 8500.00,
            'currency': 'USD',
            'platform': 'Robinhood'
        },
        {
            'name': 'Emergency Fund',
            'type': 'fixed deposit',
            'balance': 5000.00,
            'currency': 'USD',
            'platform': 'Wells Fargo'
        }
    ]

    account_ids = []

    for acc in accounts:
        query = """
        INSERT INTO account 
        (user_id, account_name, account_type, account_balance, currency, platform_name) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(query, (
                user_id,
                acc['name'],
                acc['type'],
                acc['balance'],
                acc['currency'],
                acc['platform']
            ))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            account_id = cursor.fetchone()[0]
            account_ids.append(account_id)

            print(f"  ✓ Account created: {acc['name']} (ID: {account_id}) - ${acc['balance']:.2f}")
        except Exception as e:
            print(f"  ✗ Error creating account {acc['name']}: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    return account_ids


def generate_sample_transactions(user_id, num_transactions=50):
    """
    Generate sample transaction data for testing

    Args:
        user_id: The user ID to create transactions for
        num_transactions: Number of transactions to create (default 50)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Sample transaction names by category
    transaction_templates = {
        1: [
            ("Walmart Grocery", 45.99, 120.00),
            ("Target Food", 32.50, 85.00),
            ("Whole Foods", 67.20, 150.00),
            ("McDonald's", 8.99, 25.00),
            ("Starbucks", 5.75, 15.00),
            ("Pizza Hut", 22.50, 45.00),
            ("Local Restaurant", 35.00, 80.00),
        ],
        2: [
            ("Gas Station", 45.00, 75.00),
            ("Uber", 15.50, 35.00),
            ("Public Transit", 2.75, 10.00),
            ("Parking", 12.00, 25.00),
            ("Car Wash", 20.00, 30.00),
        ],
        3: [
            ("Netflix", 15.99, 15.99),
            ("Movie Theater", 18.00, 40.00),
            ("Spotify", 9.99, 9.99),
            ("Concert Tickets", 75.00, 150.00),
            ("Gaming", 59.99, 79.99),
        ],
        4: [
            ("Amazon", 35.00, 200.00),
            ("Clothing Store", 89.99, 150.00),
            ("Electronics", 199.99, 500.00),
            ("Home Goods", 45.00, 120.00),
        ],
        5: [
            ("Electric Bill", 85.00, 120.00),
            ("Internet Bill", 65.00, 80.00),
            ("Phone Bill", 55.00, 75.00),
            ("Water Bill", 35.00, 50.00),
        ]
    }

    descriptions = [
        "Monthly expense",
        "Regular purchase",
        "One-time payment",
        "Weekly shopping",
        "Necessary expense",
        "Emergency purchase",
        "Planned spending",
        None,
    ]

    # Generate transactions for the last 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    print(f"\nGenerating {num_transactions} sample transactions...")

    for i in range(num_transactions):
        category_id = random.randint(1, 5)

        template = random.choice(transaction_templates.get(category_id, transaction_templates[1]))
        name = template[0]
        min_amount = template[1]
        max_amount = template[2]

        amount = round(random.uniform(min_amount, max_amount), 2)
        description = random.choice(descriptions)

        random_days = random.randint(0, 90)
        transaction_date = start_date + timedelta(days=random_days)
        transaction_date_str = transaction_date.strftime('%Y-%m-%d')

        query = """
        INSERT INTO transactions 
        (user_id, category_id, name, amount, description, transaction_date) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(query, (
                user_id,
                category_id,
                name,
                amount,
                description,
                transaction_date_str
            ))
            conn.commit()
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1}/{num_transactions} transactions...")
        except Exception as e:
            print(f"  ✗ Error creating transaction {i + 1}: {e}")
            conn.rollback()

    print(f"✓ Successfully generated {num_transactions} transactions")

    # Show summary
    cursor.execute("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_spent,
            AVG(amount) as avg_transaction
        FROM transactions 
        WHERE user_id = %s
    """, (user_id,))

    result = cursor.fetchone()
    if result:
        print(f"\n📊 Transaction Summary:")
        print(f"   Total Transactions: {result[0]}")
        print(f"   Total Spent: ${result[1]:.2f}")
        print(f"   Average Transaction: ${result[2]:.2f}")

    cursor.close()
    conn.close()


def setup_complete_user():
    """
    Create a complete sample user with accounts and transactions
    """
    print("=" * 60)
    print("Creating Sample User with Complete Data")
    print("=" * 60)

    # Check if user already exists
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = %s", ("john.doe@example.com",))
    existing_user = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_user:
        print("\n⚠️  User 'john.doe@example.com' already exists!")
        print(f"   Existing User ID: {existing_user[0]}")

        choice = input(
            "\nWhat would you like to do?\n1. Use existing user\n2. Delete and recreate\n3. Exit\nChoice (1/2/3): ")

        if choice == "1":
            user_id = existing_user[0]
            print(f"\n✓ Using existing user (ID: {user_id})")
        elif choice == "2":
            print("\n🗑️  Deleting existing user data...")
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # Delete in correct order (foreign key constraints)
                cursor.execute("DELETE FROM transactions WHERE user_id = %s", (existing_user[0],))
                cursor.execute("DELETE FROM account WHERE user_id = %s", (existing_user[0],))
                cursor.execute("DELETE FROM category WHERE user_id = %s", (existing_user[0],))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (existing_user[0],))
                conn.commit()
                print("✓ Deleted existing user and related data")
            except Exception as e:
                print(f"✗ Error deleting user: {e}")
                conn.rollback()
                cursor.close()
                conn.close()
                return
            cursor.close()
            conn.close()

            # Create new user
            user_id = create_sample_user(
                name="John Doe",
                email="john.doe@example.com",
                password="Password123!"
            )
        else:
            print("Exiting...")
            return
    else:
        # Create user
        user_id = create_sample_user(
            name="John Doe",
            email="john.doe@example.com",
            password="Password123!"
        )

    if not user_id:
        print("Failed to create user!")
        return

    print("\n" + "-" * 60)
    print("Creating Categories...")
    print("-" * 60)

    # Create categories FIRST
    category_ids = create_sample_categories(user_id)

    if not category_ids:
        print("Failed to create categories!")
        return

    print("\n" + "-" * 60)
    print("Creating Accounts...")
    print("-" * 60)

    # Create accounts
    account_ids = create_sample_accounts(user_id)

    if account_ids:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(account_balance) FROM account WHERE user_id = %s", (user_id,))
        total_balance = cursor.fetchone()[0]
        print(f"\n💰 Total Balance Across All Accounts: ${total_balance:.2f}")
        cursor.close()
        conn.close()

    print("\n" + "-" * 60)
    print("Creating Transactions...")
    print("-" * 60)

    # Create transactions
    generate_sample_transactions(user_id, num_transactions=50)

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(f"\nLogin Credentials:")
    print(f"  Name: John Doe")
    print(f"  Email: john.doe@example.com")
    print(f"  Password: Password123!")
    print(f"  User ID: {user_id}")
    print(f"\nYou can now use this user to test your financial tracker!")


if __name__ == "__main__":
    setup_complete_user()