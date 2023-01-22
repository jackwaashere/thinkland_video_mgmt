import csv
from urllib import parse

class PlaylistDB:
    def __init__(self, csvMeetingsFile):
        with open(csvMeetingsFile, mode='r') as file_in:
            self.allPlaylists = {}
            reader = csv.DictReader(file_in)
            PLAYLIST_URL = "YouTube Playlist Share URL"
            CLASS_ID = "Class ID"
            TEACHER_NAME = "Teacher Name"
            self.ambiguousClasses = set()
            for line in reader:
                class_id = line[CLASS_ID]
                teacher = line[TEACHER_NAME]
                plkey = "%s|%s" % (class_id, teacher)
                if line[PLAYLIST_URL]:
                    url = line[PLAYLIST_URL]
                    params = parse.parse_qs(parse.urlsplit(url).query)
                    playlist_id = params['list']
                    if plkey not in self.allPlaylists:
                        self.allPlaylists[plkey] = playlist_id
                    elif self.allPlaylists[plkey] != playlist_id:
                        self.ambiguousClasses.add(class_id)
                        print("Different playlists for the same classID:%s\nPL1:%s\nPL2:%s" %
                            (class_id, playlist_id, self.allPlaylists[class_id]))

    def getPlaylistId(self, classId, teacherName):
        plkey = "%s|%s" % (classId, teacherName)
        if plkey in self.ambiguousClasses:
            return None
        if plkey in self.classPlaylists:
            return self.classPlaylists[plkey]
        return None


if __name__ == '__main__':
    plDB = PlaylistDB("data/meetings.csv")
    print(len(plDB.allPlaylists))