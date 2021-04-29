from datetime import datetime, timedelta
from flask import Flask, session, request, abort, render_template, url_for
from werkzeug.utils import redirect
from DirectorService import DirectorService
from Staff import Staff
from UserService import UserService
from CoachService import CoachService
from ArtistService import ArtistService
from Attendance import Attendance
from EmailService import EmailService

# initializing a variable of Flask
app = Flask(__name__, template_folder="templates")


ip_ban_list = []

@app.before_request
def block_method():
    ip = request.environ.get('REMOTE_ADDR')
    if ip in ip_ban_list:
        print("IP is banned")
        emailService = EmailService()
        emailService.alert_director(session['loginFail'], ip)
        abort(403)

@app.route('/', methods=['GET']) #gets the login page
def base_url():
    if 'directorID' in session:
        return redirect(url_for('director_home'))
    elif 'coachID' in session:
        return redirect(url_for('coach_home'))
    elif 'artistID' in session:
        return redirect(url_for('artist_home'))
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', "POST"]) #gets the login page
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userType = request.form['userType']
        service = UserService()
        user = service.login(username, password, userType)
        if(user==None): #if the login has failed
            if 'loginFail' not in session:
                session['loginFail'] = [username]
            else:
                arrayOfFailedUsernames = session['loginFail']
                arrayOfFailedUsernames.append(username)
                if len(arrayOfFailedUsernames) >= 10:
                    arrayOfFailedUsernames = session['loginFail']
                    ip = request.environ.get('REMOTE_ADDR')
                    ip_ban_list.append(ip)
                    print(arrayOfFailedUsernames)
                    return redirect('/login')
                session['loginFail'] = arrayOfFailedUsernames
            return render_template('login.html', error="No user with these details")
        else:
            #clear session
            if 'loginFail' in session:
                session.pop('loginFail', None)
            if isinstance(user, Staff):
                if user.get_role() == "director":
                    session['directorID'] = user.get_id()
                    # authentication is used for least privilege principle
                    if user.get_reset_pass_status() == 1: # this means its the first time they logged in
                        return render_template('resetPass.html', userID=user.get_id(), role="director")# this means its the first time they logged in
                    return redirect(url_for('director_home'))
                else:
                    session['coachID'] = user.get_id()
                    if user.get_reset_pass_status() == 1: # this means its the first time they logged in
                        return render_template('resetPass.html', userID=user.get_id(), role="coach") # this means its the first time they logged in
                    return redirect(url_for('coach_home'))
            else:
                session['artistID'] = user.get_id()
                if user.get_reset_pass_status() == 1: # this means its the first time they logged in
                    return render_template('resetPass.html', userID=user.get_id(), role="artist") # this means its the first time they logged in
                return redirect(url_for('artist_home'))

    userType = request.args.get('user', None)
    if userType == "staff":
        staff = True
    else:
        staff = False
    return render_template('login.html', staff=staff) #if get, return template



@app.route('/logout')
def logout():
    # remove the session details
    session.clear()
    return redirect(url_for('login'))

@app.route('/reset_pass', methods=['POST'])
def reset_pass():
    if 'directorID' not in session and 'artistID' not in session and 'coachID' not in session:
        return redirect(url_for('login')) # this means this post request is only accessible through previously logging in
    newPass = request.form['password']
    userID = request.form['userID']
    role = request.form['role']
    service = UserService()
    error = service.passwordCheck(newPass)
    print(error)
    if error is not True:
        return render_template('resetPass.html', userID=userID,
                               role=role, error=error)  # this means its the first time they logged in
    if service.resetPass(userID, newPass, role):
        print("updated")
        return redirect(url_for(role + '_home')) # go to correct home page for the role
    else:
        return render_template('resetPass.html', userID=userID, role=role, error="There was an error, please contact the director")


@app.route('/director_home', methods=['GET', "POST"])
def director_home():
    if 'directorID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))

    service = DirectorService()

    artists = service.get_all_artists()
    staff = service.get_all_staff()


    return render_template('directorHome.html', artists=artists, staff=staff)


@app.route('/reset_pass_director', methods=["POST"])
def reset_pass_director():
    service = DirectorService()
    if request.form['isArtist'] == 'true':
        artistID = request.form['artistID']
        response = service.reset_password(artistID, 'artist')
    else:
        staffID = request.form['staffID']
        response = service.reset_password(staffID, 'staff')

    if response is True:
        return redirect(url_for('director_home'))
    else:
        print("ERROR")




@app.route('/coach_home', methods=['GET', "POST"])
def coach_home():
    if 'coachID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))

    service = CoachService()
    classes = service.getClasses(session['coachID'])

    return render_template('coachHome.html', classes=classes)


@app.route('/class_details', methods=['GET'])
def class_details():
    if 'coachID' not in session:  # authentication - least authorized principle
        return redirect(url_for('login'))
    classID = request.args.get('classID', None)
    if classID == None:
        return redirect(url_for('coach_home'))

    service = CoachService()
    details = service.getAllClasses(classID)


    return render_template('classDetails.html', classID=classID, details=details)




@app.route('/attendance', methods=['GET', "POST"])
def attendance():
    if 'coachID' not in session:  # authentication - least authorized principle
        return redirect(url_for('login'))
    if request.method=='POST':
        updatedAttendance = []
        sessionID = request.form['sessionID']
        for i in request.form:
            if i == "sessionID":
                sessionID=request.form[i]
                continue
            artistID = i[0]
            status = request.form[i[0]]
            attendanceInstance = Attendance(artistID, status)
            updatedAttendance.append(attendanceInstance)
        service = CoachService()
        response = service.setAttendance(sessionID, updatedAttendance)
        if response is False:
            print("Error")
    else:
        sessionID = request.args.get('sessionID', None)
    service = CoachService()
    attendance = service.getAttendanceSheet(sessionID)
    return render_template('attendanceSheet.html', attendance=attendance, sessionID = sessionID)


@app.route('/artist_home', methods=['GET', "POST"])
def artist_home():
    if 'artistID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    artistID = session['artistID']
    service = ArtistService()
    upcomingClasses = service.get_upcoming_classes(artistID)
    attendance = service.get_attendance(artistID)
    missedSessions = service.get_missed_sessions(artistID)

    return render_template('artistHome.html', classes = upcomingClasses, attendance=attendance, missedSessions=missedSessions)


@app.route('/create_artist', methods=['GET', "POST"])
def create_artist():
    if 'directorID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    error = None
    service = DirectorService()
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        birthdate = request.form['birthdate']
        email = request.form['email']
        userService = UserService()
        if userService.checkEmail(email) is False:
            error = "Not a valid email"
        else:
            classID = request.form['classID']
            response = service.register_artist(username, password, birthdate, email, classID)
            if response != True:
                error = response
            else:
                return redirect(url_for('director_home'))
    classDetails = service.get_all_class_details()
    date = datetime.date(datetime.today()) - timedelta(days=7*365)
    return render_template('registerArtist.html', minAge=date, error=error, classDetails=classDetails)


@app.route('/create_coach', methods=['GET', "POST"])
def create_coach():
    if 'directorID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        userService = UserService()
        if userService.checkEmail(email) is False:
            return render_template('registerCoach.html', error="Email is not valid")
        service = DirectorService()
        response = service.register_coach(username, password, email)
        if response == False:
            return render_template('registerCoach.html', error="There was an error creating the profile")
        return redirect(url_for('director_home'))
    return render_template('registerCoach.html')


@app.route('/create_class', methods=["POST"])
def create_class():
    if 'coachID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    try:
        adultClass = request.form['adultClass']
    except:
        return redirect(url_for('coach_home'))
    coachID = session['coachID']
    service = CoachService()
    response = service.createClass(adultClass, coachID)
    if response is False:
        print("Error")
    return redirect(url_for('coach_home'))

@app.route('/create_session', methods=["GET", "POST"])
def create_session():
    error = None
    if request.method =="POST":
        location = request.form['location']
        print("AHAHAIAHJHAJAHJA")
        day = request.form['day']
        time = request.form['time']
        classID = request.form['classID']
        service = CoachService()
        response = service.createSession(classID, location, day, time)
        if response is False:
            error = "Error creating session. Please contact the director"

    if 'coachID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    classID = request.args.get('classID', None)
    if classID is None:
        print("no class ID")
        return redirect(url_for('coach_home'))
    service = CoachService()
    response = service.getClass(classID)
    if response is False or None: # if the response shows no class with that id
        print("no class details")
        return redirect(url_for('coach_home')) # return home
    if response[1] != session['coachID']: # if this coach is not the coach of this class
        return redirect(url_for('coach_home')) # deny access.
        # Fail securely principle: always deny if in doubt
    today = datetime.date(datetime.today())
    return render_template('createSession.html', error=error, classID=classID, isAdult=response[2], today=today)


@app.route('/artist_edit', methods=["GET", "POST"])
def artist_edit():
    if 'artistID' not in session: #authentication - least authorized principle
        return redirect(url_for('login'))
    artistID = session['artistID']
    service = ArtistService()
    error=None
    if request.method=="POST":
        newUsername = request.form['username']
        newEmail = request.form['email']
        userService = UserService()
        if userService.checkEmail(newEmail) is False:
            error = "Not a valid email"
        else:
            response = service.update_details(newUsername,newEmail, artistID)
            if response is False:
                error="Error editing data. Please contact the director"
    response = service.get_details(artistID)
    if response is None:
        return redirect(url_for('artist_home'))
    return render_template('artistDetails.html', data=response, error=error)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()
