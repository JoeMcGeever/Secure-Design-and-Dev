from Artist import Artist
from Staff import Staff
from UserRepo import UserRepo
import bcrypt

repo = UserRepo()


class UserService:

    def login(self, username, password, usertype):
        data = repo.checkDetails(username, password, usertype)
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
        return repo.passIsSet(userID, decodedHash, usertype)
