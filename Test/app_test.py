import unittest
from os import environ

from app import app
from flaskext.mysql import MySQL
from flask import session


class TestCaseExamples(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        # MySQL configurations
        app.config['MYSQL_DATABASE_USER'] = 'root'
        app.config['MYSQL_DATABASE_PASSWORD'] = environ.get('database_password') or ''
        app.config['MYSQL_DATABASE_DB'] = environ.get('database_name')
        app.config['MYSQL_DATABASE_HOST'] = 'localhost'
        app.secret_key = 'super secret key'  # needed for session storage usage
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        mysql = MySQL()
        mysql.init_app(app)
        mysql.connect()
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('DELETE FROM attendance')
        cur.execute('DELETE FROM session')
        cur.execute('DELETE FROM artist')
        cur.execute('DELETE FROM class')
        cur.execute('DELETE FROM staff')
        cur.execute('ALTER TABLE attendance AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE session AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE artist AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE class AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE staff AUTO_INCREMENT=1')
        con.commit()
        pass

    def test_reroute_to_login(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Login' in response.data)


    def test_logout(self):
        self.createDirectorAccount()
        response = self.login('director', 'director', 'staff')
        self.assertTrue(b'Director Home' in response.data)
        response = self.logout()
        self.assertTrue(b'Login' in response.data)
#director:
    def test_login_as_director(self):
        self.createDirectorAccount()
        response = self.login('director', 'director', 'staff')
        self.assertTrue(b'Director Home' in response.data)

    def test_create_coach(self):
        self.registerCoach('coach', 'josephmcgeever23@gmail.com', 'test')
        response = self.login('coach', 'test', 'staff')
        self.assertTrue(b'Reset Password' in response.data)
        # assert that the user has successfully logged in and must reset their password
        response = self.resetPasswordFirstLogin('updatedPassword@1!', 1, 'coach')
        self.assertTrue(b'Coach Home' in response.data)
        self.logout()
        response = self.login('coach', 'updatedPassword@1!', 'staff')
        self.assertTrue(b'Coach Home' in response.data)

    def test_create_artist(self):
        self.createClass(1) #create adult class
        self.registerArtist("test", "artist@artist.com", "temp", "1999-06-12", "3") #create adult account
        self.login("test", "temp", "artist")
        response = self.resetPasswordFirstLogin('updatedPassword@1!', 1, 'artist')
        self.assertTrue(b'Artist Home' in response.data)

    def test_invalid_email(self):
        self.createClass(1) #create adult class
        response = self.registerArtist("test", "invalid", "temp", "1999-06-12", "1") #create adult account
        self.assertTrue(b'Not a valid email' in response.data)

    def test_child_join_adult_class(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.createClass(1) #create adult class
        response = self.registerArtist("test", "artist@artist.com", "temp", "2009-06-12", "1") #create adult account
        self.assertTrue(b'This user is not the correct age to join this class' in response.data)

    def test_adult_join_child_class(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.createClass(0) #create child class
        response = self.registerArtist("test", "artist@artist.com", "temp", "1999-06-12", "1") #create adult account
        self.assertTrue(b'This user is not the correct age to join this class' in response.data)

    def test_director_reset_pass(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.login("test", "pass", "staff")
        self.resetPasswordFirstLogin('updatedPassword@1!', 1, 'coach')
        response = self.login("test", "updatedPassword@1!", "staff")
        self.assertTrue(b'Coach Home' in response.data)
        response = self.resetPasswordAsDirector(1, 0) # resets pass for a coach
        self.assertTrue(b'Director Home' in response.data)
        response = self.login("test", "pass", "artist")
        self.assertTrue(b'No user with these details' in response.data)

    #coach

    def test_reset_pass_no_special_char(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.login("test", "pass", "staff")
        response = self.resetPasswordFirstLogin('updatedPassword1', 1, 'coach')
        self.assertTrue(b'Password should have at least one of the symbols $@#' in response.data)


    def test_coach_create_session(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.login('test', 'pass', 'staff')
        self.resetPasswordFirstLogin('updatedPassword1@!', 1, 'coach')
        self.createClass(1)
        self.createSession("room 105", "2021-05-23", "18:03", 1)
        response = self.viewClass(1)
        self.assertTrue(b'room 105' in response.data)


    def test_coach_create_session_under18_incorrect_time(self):
        self.registerCoach('test', 'email@adm.com', 'pass')
        self.login('test', 'pass', 'staff')
        self.resetPasswordFirstLogin('updatedPassword1@!', 1, 'coach')
        self.createClass(0)
        response = self.createSession("room 105", "2021-05-23", "23:03", 1) # set time to 23:03
        self.assertTrue(b'Create a Session' in response.data) # should html error
        ########################################,

















#################################################
################helper methods###################
#################################################

    def createDirectorAccount(self):
        #creates a director staff account with 'director' as its password
        mysql = MySQL()
        mysql.init_app(app)
        mysql.connect()
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("INSERT INTO staff (`username`, `password`, `role`, `firstLogin`, `email`)VALUES('director', '$2b$10$L9KIpF/weBIq6MR5zY4OXe60HwH/75ckDkpwz7eN0b5t1l7kDn53i', 'director', '0', 'mcgeevej@uni.coventry.ac.uk')")
        con.commit()
        con.close()


    def registerCoach(self, username, email, password):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['directorID'] = 1 # mock being a logged in director
        return tester.post(
            '/create_coach',
            data=dict(username=username, email=email, password=password),
            follow_redirects=True
        )

    def registerArtist(self, username, email, password, birthdate, classID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['directorID'] = 1 # mock being a logged in director
        return tester.post(
            '/create_artist',
            data=dict(username=username, email=email, password=password, birthdate=birthdate, classID=classID),
            follow_redirects=True
        )

    def resetPasswordFirstLogin(self, newPass, userID, role):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess[role + 'ID'] = 1  # mock being a logged in as whatever role
        return tester.post(
            '/reset_pass',
            data=dict(password=newPass, userID=userID, role=role),
            follow_redirects=True
        )

    def resetPasswordAsDirector(self, userID, isArtist):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['directorID'] = 1  # mock being a logged in as director
        if isArtist:
            return tester.post(
                '/reset_pass_director',
                data=dict(isArtist=isArtist, artistID=userID),
                follow_redirects=True
            )
        else:
            return tester.post(
                '/reset_pass_director',
                data=dict(isArtist=isArtist, staffID=userID),
                follow_redirects=True
            )


    def login(self, username, password, userType):
        tester = app.test_client(self)
        return tester.post(
            '/login',
            data=dict(username=username, password=password, userType=userType),
            follow_redirects=True
        )


    def logout(self):
        tester = app.test_client(self)
        return tester.get(
            '/logout',
            follow_redirects=True
        )

    def createClass(self, adultClass):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['coachID'] = 1  # mock being a logged in as whatever role
        return tester.post(
            '/create_class',
            data=dict(adultClass=adultClass),
            follow_redirects=True
        )


    def createSession(self, location, day, time, classID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['coachID'] = 1  # mock being a logged in as whatever role
        return tester.post(
            '/create_session?classID=' + str(classID),
            data=dict(location=location, day=day, time=time, classID=classID),
            follow_redirects=True
        )

    def viewClass(self, classID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['coachID'] = 1  # mock being a logged in as whatever role
        return tester.get(
            '/class_details?classID=' + str(classID),#
            follow_redirects=True
        )



if __name__ == '__main__':
    unittest.main()
