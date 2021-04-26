
class Artist:

    def __init__(self):
        self.artistID = None
        self.birthdate = None
        self.email = None
        self.username = None
        self.resetPass = None

    def get_id(self):
        return self.artistID

    def set_id(self, artistID):
        self.artistID = artistID

    def get_birthdate(self):
        return self.birthdate

    def set_birthdate(self, birthdate):
        self.birthdate = birthdate

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_reset_pass_status(self):
        return self.resetPass

    def set_reset_pass_status(self, status):
        self.resetPass = status