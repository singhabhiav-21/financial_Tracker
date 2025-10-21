from financial_Tracker.databaseDAO.sqlConnector import get_connection
import random
from datetime import datetime, timedelta

conn = get_connection()
cursor = conn.cursor()


def generate_sample_transactions(user_id, num_transactions=50):
    """
    Generate sample transaction data for testing

    Args:
        user_id: The user ID to create transactions for
        num_transactions: Number of transactions to create (default 50)
    """

    # Sample transaction names by category
    transaction_templates = {
        1: [  # Assuming category 1 is Food/Groceries
            ("Walmart Grocery", 45.99, 120.00),
            ("Target Food", 32.50, 85.00),
            ("Whole Foods", 67.20, 150.00),
            ("McDonald's", 8.99, 25.00),
            ("Starbucks", 5.75, 15.00),
            ("Pizza Hut", 22.50, 45.00),
            ("Local Restaurant", 35.00, 80.00),
        ],
        2: [  # Assuming category 2 is Transportation
            ("Gas Station", 45.00, 75.00),
            ("Uber", 15.50, 35.00),
            ("Public Transit", 2.75, 10.00),
            ("Parking", 12.00, 25.00),
            ("Car Wash", 20.00, 30.00),
        ],
        3: [  # Assuming category 3 is Entertainment
            ("Netflix", 15.99, 15.99),
            ("Movie Theater", 18.00, 40.00),
            ("Spotify", 9.99, 9.99),
            ("Concert Tickets", 75.00, 150.00),
            ("Gaming", 59.99, 79.99),
        ],
        4: [  # Assuming category 4 is Shopping
            ("Amazon", 35.00, 200.00),
            ("Clothing Store", 89.99, 150.00),
            ("Electronics", 199.99, 500.00),
            ("Home Goods", 45.00, 120.00),
        ],
        5: [  # Assuming category 5 is Bills/Utilities
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
        None,  # Some transactions without description
    ]

    # Generate transactions for the last 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    print(f"Generating {num_transactions} sample transactions...")

    for i in range(num_transactions):
        # Random category (1-5)
        category_id = random.randint(1, 5)

        # Get random transaction template for this category
        template = random.choice(transaction_templates.get(category_id, transaction_templates[1]))
        name = template[0]
        min_amount = template[1]
        max_amount = template[2]

        # Random amount within range
        amount = round(random.uniform(min_amount, max_amount), 2)

        # Random description
        description = random.choice(descriptions)

        # Random date within the last 3 months
        random_days = random.randint(0, 90)
        transaction_date = start_date + timedelta(days=random_days)
        transaction_date_str = transaction_date.strftime('%Y-%m-%d')

        # Insert transaction
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
            print(f"✓ Transaction {i + 1}/{num_transactions}: {name} - ${amount:.2f} on {transaction_date_str}")
        except Exception as e:
            print(f"✗ Error creating transaction {i + 1}: {e}")
            conn.rollback()

    print(f"\n✅ Successfully generated {num_transactions} transactions for user {user_id}")

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
        print(f"\n📊 Summary:")
        print(f"   Total Transactions: {result[0]}")
        print(f"   Total Spent: ${result[1]:.2f}")
        print(f"   Average Transaction: ${result[2]:.2f}")


def generate_monthly_data(user_id, year, month, transactions_per_day=2):
    """
    Generate transactions for a specific month with more control

    Args:
        user_id: The user ID
        year: Year (e.g., 2024)
        month: Month (1-12)
        transactions_per_day: Average transactions per day
    """
    from calendar import monthrange

    # Get number of days in month
    _, num_days = monthrange(year, month)

    transaction_templates = {
        1: [("Grocery Store", 30, 100), ("Restaurant", 15, 60), ("Coffee Shop", 4, 12)],
        2: [("Gas", 35, 70), ("Uber", 10, 30), ("Parking", 5, 20)],
        3: [("Subscription", 10, 20), ("Entertainment", 20, 80)],
        4: [("Shopping", 25, 150), ("Online Purchase", 15, 100)],
        5: [("Utility Bill", 50, 150), ("Phone Bill", 40, 80)],
    }

    print(f"Generating transactions for {year}-{month:02d}...")

    for day in range(1, num_days + 1):
        # Random number of transactions per day (0 to 2x average)
        num_trans = random.randint(0, transactions_per_day * 2)

        for _ in range(num_trans):
            category_id = random.randint(1, 5)
            template = random.choice(transaction_templates[category_id])
            name = template[0]
            amount = round(random.uniform(template[1], template[2]), 2)
            description = random.choice(["Daily expense", "Planned purchase", None])

            transaction_date = f"{year}-{month:02d}-{day:02d}"

            query = """
            INSERT INTO transactions 
            (user_id, category_id, name, amount, description, transaction_date) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            try:
                cursor.execute(query, (user_id, category_id, name, amount, description, transaction_date))
                conn.commit()
            except Exception as e:
                print(f"Error: {e}")
                conn.rollback()

    print(f"✅ Completed generating data for {year}-{month:02d}")


if __name__ == "__main__":
    # Option 1: Generate random transactions over 3 months
    generate_sample_transactions(user_id=1, num_transactions=50)

    # Option 2: Generate specific monthly data (uncomment to use)
    # generate_monthly_data(user_id=1, year=2024, month=10, transactions_per_day=3)
    # generate_monthly_data(user_id=1, year=2024, month=9, transactions_per_day=2)

    cursor.close()
    conn.close()