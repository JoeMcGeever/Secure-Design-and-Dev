from ArtistRepo import ArtistRepo

repo = ArtistRepo()

class ArtistService:

    def get_details(self, artistID):
        return repo.getDetails(artistID)

    def update_details(self, username, email, artistID):
        return repo.updateDetails(username, email, artistID)

    def get_upcoming_classes(self, artistID):
        return repo.getUpcomingClasses(artistID)

    def get_attendance(self, artistID):
        response = repo.getAttendance(artistID)
        return response

    def get_missed_sessions(self, atristID):
        response = repo.getMissedSessions(atristID)
        return response