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


class SessionRepo:

    def createSession(self, classID, location, date):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('INSERT INTO session (date, classID, location) VALUES (%s, %s, %s)', (date, classID, location))
            idOfSession = cur.lastrowid
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return idOfSession

    # def createAttendence(self, sessionID, classID):
    #     pass


    def createAttendence(self, sessionID, classID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT artistID FROM artist WHERE classID=%s', classID)
            usersInClass = cur.fetchall()
            con.commit()
            val = []
            for id in usersInClass:
                val.append((sessionID, id[0]))
            cur.executemany("INSERT INTO attendance (sessionID, artistID) VALUES (%s, %s)", val)
        except:
            con.rollback()
            print("FAIL")
            return False
        finally:
            con.commit()
            con.close()
        return True

    def getAtendance(self, sessionID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT artist.username, attendance.artistID, attendance.status FROM attendance JOIN artist ON attendance.artistID = artist.artistID WHERE attendance.sessionID=%s', sessionID)
            results = cur.fetchall()
        except:
            con.rollback()
            print("ERROR fetching details")
            return False
        finally:
            con.commit()
            con.close()
        return results

    def setAttendance(self, sessionID, attendanceClass):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("DELETE FROM attendance WHERE sessionID=%s", sessionID)
            con.commit()
            val = []
            for i in attendanceClass:
                print(i.artistID)
                print(i.status)
                val.append((sessionID, i.artistID, i.status))
            cur.executemany("INSERT INTO attendance (sessionID, artistID, status) VALUES (%s, %s, %s)", val)
        except:
            con.rollback()
            print("FAIL")
            return False
        finally:
            con.commit()
            con.close()
        return True

    def getClassDetails(self, classID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT * FROM class WHERE classID=%s', classID)
            results = cur.fetchone()
        except:
            con.rollback()
            print("ERROR fetching details")
            return False
        finally:
            con.commit()
            con.close()
        return results
