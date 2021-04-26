from datetime import datetime
from ClassRepo import ClassRepo
from SessionRepo import SessionRepo

class_repo = ClassRepo()
session_repo = SessionRepo()

class CoachService:

    def createClass(self, adultClass, coachID):
        return class_repo.createClass(adultClass, coachID)

    def getClasses(self, coachID):
        return class_repo.getClasses(coachID)

    def getAllClasses(self, classID):
        return class_repo.getAllClasses(classID)

    def createSession(self, classID, location, date, the_time):
        when = date + "-" + the_time
        f = '%Y-%m-%d-%H:%M'
        #date_time = time.strptime(when, f)
        date_time_obj = datetime.strptime(when, f)
        idOfSession = session_repo.createSession(classID,location,date_time_obj)
        if idOfSession is False:
            return False
        response = self.createAttendanceSheet(idOfSession, classID)
        return response

    def createAttendanceSheet(self, sessionID, classID):
       response = session_repo.createAttendence(sessionID, classID)
       return response

    def getAttendanceSheet(self, sessionID):
        response = session_repo.getAtendance(sessionID)
        return response

    def setAttendance(self, sessionID, attendanceSheet):
        response = session_repo.setAttendance(sessionID, attendanceSheet)
        return response

    def getClass(self, classID):
        response = session_repo.getClassDetails(classID)
        print(response)
        return response

