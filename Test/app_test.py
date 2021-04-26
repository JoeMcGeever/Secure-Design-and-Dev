import unittest
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
        app.config['MYSQL_DATABASE_PASSWORD'] = ''  # environ.get('database_password') # password protected
        app.config['MYSQL_DATABASE_DB'] = 'dance_club_test'
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

    def test_login_as_director(self):
        self.createDirectorAccount()
        response = self.login('director', 'director', 'staff')
        self.assertTrue(b'Director Home' in response.data)

    def test_create_coach(self):
        self.registerCoach('coach', 'josephmcgeever23@gmail.com', 'test')
        response = self.login('coach', 'test', 'staff')
        self.assertTrue(b'Reset Password' in response.data)
        # assert that the user has successfully logged in and must reset their password
        response = self.resetPasswordFirstLogin('updatedPassword', 1, 'coach')
        self.assertTrue(b'Coach Home' in response.data)
        self.logout()
        response = self.login('coach', 'updatedPassword', 'staff')
        self.assertTrue(b'Coach Home' in response.data)



    def test_create_artist(self):
        print('hi')






















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

    def registerArtist(self, username, email, password):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['directorID'] = 1 # mock being a logged in director
        return tester.post(
            '/create_artist',
            data=dict(username=username, email=email, password=password),
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




if __name__ == '__main__':
    unittest.main()
