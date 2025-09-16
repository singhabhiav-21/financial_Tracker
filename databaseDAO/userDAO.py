from sqlConnector import get_connection
import hashlib
import os

conn = get_connection()
cursor = conn.cursor()

def register(name, email, password):
    query = "INSERT INTO users(name, email, password) VALUES (%s,%s,%s)"

    namecheck = nameChecker(name)
    emailcheck = isEmail(email)
    passwordcheck = checkpassword(password)
    if emailcheck is False:
        return emailcheck
    if passwordcheck is False:
        return passwordcheck
    if namecheck is False:
        return namecheck
    else:
        hashedpw = hashpassword(password)
        cursor.execute(query,(name, email, hashedpw,))
        conn.commit()
        return True,  "User registered successfully."


def isEmail(email):
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query,(email,))
    if cursor.fetchone() is not None:
        print("This email is already registered. Please use a new email or continue with the current one.")
        return False
    else:
        return True


def hashpassword(password):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt + ":" + hashed


def checkpassword(password):
    special = "!#€%&/()=?^*_:;©@£$∞§|[]≈±´~™''æ…‚§¶°"
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = "1234567890"

    if len(password) < 8:
        print("The password is too short, the password length should be larger than 8.")
        return False

    #Checks
    if not any(c in special for c in password):
        print("The password does not contain any special symbols e.g. '!#€...'. ")
        return False
    if not any(c in lower for c in password):
        print("The password does not contain any small letters e.g. 'abc...'.")
        return False
    if not any(c in upper for c in password):
        print("The password does not contain any capital letters e.g. 'ABC....'. ")
        return False
    if not any(c in num for c in password):
        print("The password does not contain any numbers e.g. '123....'. ")
        return False
    return True


def nameChecker(name):
    newname = name.lower().strip()

    if len(newname) < 5:
        print("The name is too short.")
        return False

    special = "!#€%&/()=?^*_:;©@£$∞§|[]≈±´~™''æ…‚§¶°"
    num = "1234567890"

    if any(c in special for c in newname):
        print("No special characters are allowed.")
        return False
    if any(c in num for c in newname):
        print("No numbers are allowed in Name.")
        return False
    return True


# Test user data
test_user = {
    "name": "JohnDoe",
    "email": "johndoe@example.com",
    "password": "Password123!"
}

result = register(test_user["name"], test_user["email"], test_user["password"])

print(result)


