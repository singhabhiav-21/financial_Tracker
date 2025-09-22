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
    cursor.execute(query, (email,))
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


def logIn(email, password):
    if "@" not in email:
        return False, "This is not an email."

    try:
        salt = passwordSalt(email)
        if not salt:
            print("The email or password is incorrect!")
            return False
        hashedPw = hashAgain(salt, password)

        query = "SELECT password FROM users WHERE email = %s"
        cursor.execute(query,(email,))
        realPw = cursor.fetchone()[0]
        _, realHashpw = realPw.split(":")

        if hashedPw == realHashpw:
            print("Login Successful")
            return True
        else:
            print("The email or password is incorrect")
            return False
    except Exception as e:
        print("Database error: ", str(e))
        return False


def passwordSalt(email):
    query = "SELECT password FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    if not result:
        return None
    password = cursor.fetchone()[0]
    salt,_ = password.split(":")
    return salt


def hashAgain(salt, password):
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed


def update_userinfo(email = None, name = None, new_email=None):
    query = "SELECT id FROM users WHERE = %s"
    cursor.fetchone(query, (email,))
    row = cursor.fetchone()
    if not row:
        print("The user does not exist")
        return False

    update = []
    value = []

    if name:
        if not nameChecker(name):
            print("invalid name")
            return nameChecker(name)
        update.append("name = %s")
        value.append(name)

    if new_email:
        if not isEmail(new_email):
            print("invalid email")
            return isEmail(new_email)
        update.append("email = %s")
        value.append(new_email)

    value.append(email)
    query = "UPDATE users SET { ', '.join(updates)} WHERE email = %s"
    cursor.execute(query, tuple(value))
    conn.commit()
    print("User information updated successfully.")
    return True
