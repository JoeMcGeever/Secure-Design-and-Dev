from datetime import date

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


class ArtistRepo:

    def getDetails(self, artistID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT username, email ,birthdate, classID FROM artist WHERE artistID=%s', artistID)
            results = cur.fetchone()
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return results

    def updateDetails(self, username, email, artistID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("UPDATE artist SET username=%s, email=%s WHERE artistID=%s", (username,email,artistID))
        except:
            con.rollback()
            return False
        finally:
            con.commit()
            con.close()
        return True

    def getUpcomingClasses(self, artistID):
        today = date.today()
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('SELECT * FROM session WHERE date >= %s AND sessionID IN (SELECT sessionID FROM attendance WHERE artistID=%s) LIMIT 3', (today, artistID))
            response = cur.fetchall()
            print(response)
        except:
            con.rollback()
            print("Error")
            return False
        finally:
            con.commit()
            con.close()
        return response


    def getAttendance(self, artistID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM attendance WHERE status!='n/a' AND artistID=%s", artistID)
            allClasses = cur.fetchone()[0]
            if(allClasses==0):
                return 0
            cur.execute("SELECT COUNT(*) FROM attendance WHERE status='present' AND artistID=%s", artistID)
            presentClasses = cur.fetchone()[0]
            attendance = 100*presentClasses/allClasses
        except:
            con.rollback()
            print("Error")
            return False
        finally:
            con.commit()
            con.close()
        return round(attendance)


    def getMissedSessions(self, artistID):
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM attendance WHERE status='unexplainedAbscence' AND artistID=%s", artistID)
            response = cur.fetchone()[0]
            print(response)
        except:
            con.rollback()
            print("Error")
            return False
        finally:
            con.commit()
            con.close()
        return response

