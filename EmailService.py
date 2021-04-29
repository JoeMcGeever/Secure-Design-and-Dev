import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:

    def reset_password(self, randomPassword, emailAddress):
        message = Mail(
            from_email='josephmcgeever@hotmail.co.uk',
            to_emails=emailAddress,
            subject='Password reset',
            html_content="Your password has been updated,"
                         + " please login with this temporary password to reset your account"
                         + "<br> <b>" + str(randomPassword) + "</br>")
        try:
            if os.environ.get('database_name') == "dance_club_test":
                print("IN TEST MODE")
                return True
            sg = SendGridAPIClient(os.environ.get('email'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return True
        except Exception as e:
            print(e.body)
            return False

    def alert_director(self, usernames, ip):
        message = Mail(
            from_email='josephmcgeever@hotmail.co.uk',
            to_emails='mcgeevej@uni.coventry.ac.uk',
            subject='10 incorrect attempts',
            html_content="Client with IP: ," + str(ip)
                         + ". Has made 10 incorrect logging attempts and has been frozen"
                         + " from entering the system. The following usernames were used:"
                         + "<br> <b> " + str(usernames))
        try:
            sg = SendGridAPIClient(os.environ.get('email'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return True
        except Exception as e:
            print(e.body)
            return False


