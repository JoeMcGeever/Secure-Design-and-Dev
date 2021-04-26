
class Staff:

    def __init__(self):
        self.staffID = None
        self.username = None
        self.role = None
        self.resetPass = None

    def get_id(self):
        return self.staffID

    def set_id(self, staffID):
        self.staffID = staffID

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_role(self):
        return self.role

    def set_role(self, role):
        self.role = role

    def get_reset_pass_status(self):
        return self.resetPass

    def set_reset_pass_status(self, status):
        self.resetPass = status