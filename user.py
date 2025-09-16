class User:

    def __init__(self,userid,name,email, password, profilePhoto, dateAdded):
        self.userid = userid
        self.name = name
        self.email = email
        self.password = password
        self.profilePhoto = profilePhoto
        self.dateAdded = dateAdded

    # Getter and Setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    # Getter and Setter for email
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("Invalid email")
        self._email = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value