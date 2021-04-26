from UserRepo import UserRepo
from EmailService import EmailService
from random_word import RandomWords
import bcrypt
repo = UserRepo()


class DirectorService:

    def register_coach(self, username, password, email):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password, salt)
        decodedHash = hashed.decode('utf-8')
        repo.createCoach(username, decodedHash, email)

    def register_artist(self, username, password, birthdate, email, classID):
        response = repo.checkClassCompatibility(classID, birthdate)
        if response != True:
            print(response)
            return response

        password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password, salt)
        decodedHash = hashed.decode('utf-8')
        if repo.createArtist(username, decodedHash, birthdate, email, classID) is False:
            return "Error inserting user details"
        else:
            return True


    def get_all_artists(self):
        return repo.getAllArtists()

    def get_all_staff(self):
        return repo.getAllStaff()


    def get_all_class_details(self):
        return repo.getAllClasses()


    def reset_password(self, userID, role):
        rawPass = self.__random_password_gen__()
        password = rawPass.encode('utf-8')
        salt = bcrypt.gensalt(rounds=10)
        hashed = bcrypt.hashpw(password, salt)
        decodedHash = hashed.decode('utf-8')
        repo = UserRepo()
        response = repo.resetPass(userID, decodedHash, role)
        if response is False:
            print("ERROR in resetting pass")
        emailAddress = repo.getUserEmail(userID, role)
        print(emailAddress)
        service = EmailService()
        response = service.reset_password(rawPass, emailAddress)
        if response is False:
            print("ERROR in emailing")

        return response

    def __random_password_gen__(self):
        r = RandomWords()
        randomWords=r.get_random_words()
        print(randomWords)
        password = randomWords[0] + "-" + randomWords[1] + "-" + randomWords[2] + "-" + randomWords[3]
        return password