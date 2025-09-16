class User:

    def __init__(self,userid,name,email, password, profilePhoto, dateAdded):
        self.userid = userid
        self.name = name
        self.email = email
        self.password = password
        self.profilePhoto = profilePhoto
        self.dateAdded = dateAdded

    def get_user_id(self):
        return self._user_id

    def get_name(self):
        return self._name

    def get_email(self):
        return self._email

    def get_password(self):
        return self._password

    def get_profile_photo(self):
        return self._profile_photo

    def get_date_added(self):
        return self._date_added


    def set_name(self, name):
        if len(name) > 0:
            self._name = name

    def set_email(self, email):
        if "@" in email:
            self._email = email

    def set_password(self, password):
            self._password = password

    def set_profile_photo(self, photo):
        self._profile_photo = photo