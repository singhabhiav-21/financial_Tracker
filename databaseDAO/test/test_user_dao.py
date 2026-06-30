import unittest
from databaseDAO.userDAO import register, logIn, update_userinfo, update_password
from databaseDAO.sqlConnector import get_connection


class TestUserManagement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This runs once before all tests
        cls.conn = get_connection()
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name    VARCHAR(50) NOT NULL ,
            email   VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            profile_photo VARCHAR(255) NUll,
            date_added DATETIME DEFAULT current_timestamp
        ); """)
        cls.cursor.execute("""CREATE TABLE IF NOT EXISTS category(
            category_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            type VARCHAR (50) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );""")
        cls.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
            transaction_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            category_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            description VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            transaction_date DATE,
            balance decimal(15,2),
            transaction_hash VARCHAR(250) NULL,
            CONSTRAINT uniq_user_tx UNIQUE (user_id, transaction_hash),
            FOREIGN KEY (user_id) references users(user_id),
            FOREIGN KEY (category_id) references category(category_id)
            );""")
        cls.conn.commit()
        cls.cursor.execute(
            "DELETE FROM transactions WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE '%example.com')"
        )
        cls.cursor.execute(
            "DELETE FROM account WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE '%@example.com')")
        cls.cursor.execute("DELETE FROM users WHERE email LIKE '%@example.com' ")
        cls.conn.commit()
        cls.cursor.close()
        cls.conn.close()

    def test_register_valid_user(self):
        result = register("AliceTest", "alice@example.com", "Password123!")
        self.assertEqual(result[0], True)

    def test_register_short_name(self):
        result = register("Al", "al@example.com", "Password123!")
        self.assertFalse(result[0])

    def test_register_invalid_email_duplicate(self):
        register("BobTest", "bob@example.com", "Password123!")
        result = register("BobTest2", "bob@example.com", "Password123!")
        self.assertFalse(result[0])

    def test_register_invalid_password(self):
        result = register("CharlieTest", "charlie@example.com", "pass")
        self.assertFalse(result[0])

    def test_login_successful(self):
        register("DaveTest", "dave@example.com", "Password123!")
        result = logIn("dave@example.com", "Password123!")
        self.assertTrue(result[0])

    def test_login_wrong_password(self):
        register("EveTest", "eve@example.com", "Password123!")
        result = logIn("eve@example.com", "WrongPassword!")
        self.assertFalse(result[0])

    def test_update_userinfo_name(self):
        register("FrankTest", "frank@example.com", "Password123!")
        result = update_userinfo(email="frank@example.com", name="FrankNew")
        self.assertTrue(result)

    def test_update_userinfo_email(self):
        register("GraceTest", "grace@example.com", "Password123!")
        result = update_userinfo(email="grace@example.com", new_email="grace2@example.com")
        self.assertTrue(result)

    def test_update_password_success(self):
        register("HankTest", "hank@example.com", "Password123!")
        result = update_password("hank@example.com", "Password123!", "NewPassword123!", "NewPassword123!")
        self.assertTrue(result)

    def test_update_password_wrong_old(self):
        register("IvyTest", "ivy@example.com", "Password123!")
        result = update_password("ivy@example.com", "WrongOldPassword!", "NewPassword123!", "NewPassword123!")
        self.assertFalse(result)

    def test_update_password_mismatch(self):
        register("JackTest", "jack@example.com", "Password123!")
        result = update_password("jack@example.com", "Password123!", "NewPassword123!", "Mismatch123!")
        self.assertFalse(result)

    def tearDown(cls):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE '%@example.com')")
        cursor.execute(
            "DELETE FROM account WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE '%@example.com')")
        cursor.execute("DELETE FROM users WHERE email LIKE '%@example.com'")
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    unittest.main()
