from ArtistRepo import ArtistRepo



class ArtistService:

    repo = ArtistRepo()

    def get_details(self, artistID):
        return self.repo.getDetails(artistID)

    def update_details(self, username, email, artistID):
        return self.repo.updateDetails(username, email, artistID)

    def get_upcoming_classes(self, artistID):
        return self.repo.getUpcomingClasses(artistID)

    def get_attendance(self, artistID):
        response = self.repo.getAttendance(artistID)
        return response

    def get_missed_sessions(self, atristID):
        response = self.repo.getMissedSessions(atristID)
        return response