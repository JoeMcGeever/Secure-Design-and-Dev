import re

from Artist import Artist
from Staff import Staff
from UserRepo import UserRepo
import bcrypt



class UserService:
    repo = UserRepo()

    def login(self, username, password, usertype):
        data = self.repo.checkDetails(username, password, usertype)
        if data is None:
            return None
        print(data)
        if usertype == "staff":
            user = Staff()
            user.set_id(data[0])
            user.set_username(data[1])
            user.set_role(data[3])
            user.set_reset_pass_status(data[4])
            return user
        else:
            user = Artist()
            user.set_id(data[0])
            user.set_birthdate(data[1])
            user.set_email(data[3])
            user.set_username(data[4])
            user.set_reset_pass_status(data[5])
            return user

    def resetPass(self, userID, password, usertype):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password, salt)
        decodedHash = hashed.decode('utf-8')
        return self.repo.passIsSet(userID, decodedHash, usertype)

    def passwordCheck(self, passwd):
        SpecialSym = ['$', '@', '#', '%', '!', '?']
        if len(passwd) < 8:
            return "length should be at least 8"
        if not any(char.isdigit() for char in passwd):
             return "Password should have at least one numeral"
        if not any(char.isupper() for char in passwd):
            return "Password should have at least one uppercase letter"
        if not any(char.islower() for char in passwd):
            return "Password should have at least one lowercase letter"
        if not any(char in SpecialSym for char in passwd):
            return "Password should have at least one of the symbols $@#"
        return True

    def checkEmail(self, email):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if (re.search(regex, email)):
            return True
        else:
            return False