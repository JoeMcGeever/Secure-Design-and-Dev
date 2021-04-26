from datetime import datetime, date, timedelta
from os import environ

import bcrypt
from flask import Flask
from flaskext.mysql import MySQL

mysql = MySQL()

# initializing a variable of Flask
app = Flask(__name__, template_folder="templates")

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''#environ.get('database_password') # password protected
if app.config['TESTING'] is True:
    app.config['MYSQL_DATABASE_DB'] = 'dance_club_test'
else:
    app.config['MYSQL_DATABASE_DB'] = 'dance_club'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


class ClassRepo:


    def createClass(self, adultClass, coachID):

        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('INSERT INTO class (coachID, adult) VALUES (%s, %s)', (coachID, adultClass))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def getClasses(self, coachID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT classID FROM class WHERE coachID=%s', coachID)
            results = cur.fetchall()
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return results

    def getAllClasses(self, classID):
        lastWeek = date.today() - timedelta(days=7)
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT * FROM session WHERE date> %s AND classID=%s', (lastWeek, classID))
            results = cur.fetchall()
        except:
            con.rollback()
            print("ERROR fetching details")
            return False
        finally:
            con.commit()
            con.close()
        return results

