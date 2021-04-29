from datetime import datetime
from os import environ

import bcrypt
from flask import Flask
from flaskext.mysql import MySQL


mysql = MySQL()

# initializing a variable of Flask
app = Flask(__name__, template_folder="templates")

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = environ.get('database_password') or ''
app.config['MYSQL_DATABASE_DB'] =  environ.get('database_name')
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


class UserRepo:


    def checkDetails(self, username, password, usertype):
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        if (usertype == "staff"):  # if staff, check the staff table
            cur.execute("SELECT * FROM staff WHERE username=%s", username)
        else:  # otherwise check the artist table
            cur.execute("SELECT * FROM artist WHERE username=%s", username)
        result = cur.fetchone()
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            if (usertype == "staff"):  # if staff, check the staff table
                cur.execute("SELECT * FROM staff WHERE username=%s", username)
            else:  # otherwise check the artist table
                cur.execute("SELECT * FROM artist WHERE username=%s", username)
            result = cur.fetchone()
        except:
            con.rollback()
        finally:
            con.commit()
            con.close()
        if result is None:
            return None
        if bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            print("password match")
            return result
        return None


    def createCoach(self, username, password, email):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("INSERT INTO staff (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def createArtist(self, username, password, birthdate, email, classID):

        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("INSERT INTO artist (username, password, birthdate, email, classID) VALUES (%s, %s, %s, %s, %s)", (username, password, birthdate, email, classID))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def resetPass(self, userID, password, usertype):

        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            if (usertype == "artist"):  # if staff, check the staff table
                cur.execute('UPDATE artist SET password=%s, firstLogin=1 WHERE artistID=%s', (password, userID))
            else:
                cur.execute('UPDATE staff SET password=%s, firstLogin=1 WHERE staffID=%s', (password, userID))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def passIsSet(self, userID, password, usertype):

        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            if (usertype == "artist"):  # if staff, check the staff table
                cur.execute('UPDATE artist SET password=%s, firstLogin=0 WHERE artistID=%s', (password, userID))
            else:
                cur.execute('UPDATE staff SET password=%s, firstLogin=0 WHERE staffID=%s', (password, userID))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def checkClassCompatibility(self, classID, birthdate):
        today = datetime.now()
        dateOfBirth = datetime.strptime(birthdate, '%Y-%m-%d')
        time_difference = today - dateOfBirth
        difference_in_years = time_difference.days / 365.25 # conver to years

        print(difference_in_years, "years old")
        if difference_in_years >=18:
            print("Is adult")
            isAdult = True
        else:
            print("Is not adult")
            isAdult = False


        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT adult FROM class WHERE classID=%s", classID)
            isAdultClass = cur.fetchone()
            if isAdultClass is None:
                return "No class with the id of " + classID
            if isAdultClass[0] == isAdult:
                return True
            else:
                return "This user is not the correct age to join this class"
        except:
            con.rollback()
        finally:
            con.commit()
            con.close()
        return "Error creating account. Try again later"



    def getAllClasses(self):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT class.classID, class.adult, staff.username FROM class JOIN staff ON class.coachID = staff.staffID")
            response = cur.fetchall()
        except:
            con.rollback()
            response = None
        finally:
            con.commit()
            con.close()
        return response


    def getAllArtists(self):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT username, email, birthdate, classID, artistID FROM artist")
            response = cur.fetchall()
        except:
            con.rollback()
            response = False
        finally:
            con.commit()
            con.close()
        return response

    def getAllStaff(self):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT staffID, username, role FROM staff")
            response = cur.fetchall()
        except:
            con.rollback()
            response = False
        finally:
            con.commit()
            con.close()
        return response

    def getUserEmail(self, userID, role):
        print("This users role:")
        print(role)
        print("This users id:" + str(userID))
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            if(role=="artist"):
                cur.execute("SELECT email FROM artist WHERE artistID=%s", userID)
            else:
                cur.execute("SELECT email FROM staff WHERE staffID=%s", userID)
            response = cur.fetchone()[0]
        except:
            con.rollback()
            print("Fail")
            response = False
        finally:
            con.commit()
            con.close()
        return response
