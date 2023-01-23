import csv
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from thinkland.zoom_canonicalize import get_canonical_zoom_id
from thinkland.zoom_canonicalize import is_canonical

class Meeting:
    def __init__(self, startTime, endTime, className, classId, teacherName, rawZoomId, reported, video, title, description):#, vid_title, vid_desc):
        self.startTime = startTime
        self.endTime = endTime
        self.className = className
        self.classId = classId
        self.teacherName = teacherName
        self.rawZoomId = rawZoomId
        self.reported = reported
        self.video = video
        self.title = title
        self.description = description
        self.youtubeURL = None
        self.playlist = None

    def getCanonicalZoomId(self):
        return get_canonical_zoom_id(self.rawZoomId)


class MeetingDB:
    def __init__(self, csvFilePath, zoneInfo=ZoneInfo('US/Eastern')):
        allMeetingsDict = {}
        with open(csvFilePath, 'r') as file_in:
            reader = csv.DictReader(file_in)
            for line in reader:
                cur = {'date': line['Class Date'], 'stime': line['Start Time'],
                    'etime': line['End Time'], 'className': line['Class Name'],
                    'classId': line['Class ID'], 'teacher': line['Teacher Name'],
                    'title': line['YouTube Title'], 'description': line['YouTube Description'],
                    'rawZoom': line['Zoom ID'], 'reported': line['Reported'], 'video': ''}#line['Video']}
                key = cur['classId'] + '|' + cur['date']
                allMeetingsDict[key] = cur

        self.allMeetings = {}
        for meetingId in allMeetingsDict:
            a = allMeetingsDict[meetingId]
            sections_meet = a['date'].split('-')
            year = int(sections_meet[0])
            month = int(sections_meet[1])
            day = int(sections_meet[2])
            sections_time = a['stime'].split(':')
            hour = int(sections_time[0])
            mins = int(sections_time[1])
            sec = int(sections_time[2])
            startTime = datetime(year, month, day, hour, mins, sec, tzinfo=zoneInfo)

            sections_time = a['etime'].split(':')
            hour = int(sections_time[0])
            mins = int(sections_time[1])
            sec = int(sections_time[2])
            endTime = datetime(year, month, day, hour, mins, sec, tzinfo=zoneInfo)
            
            meetingObj = Meeting(startTime, endTime,
                                 a['className'], a['classId'], a['teacher'],
                                 a['rawZoom'], a['reported'], a['video'], a['title'], a['description'])#,
                                #  a['vid_title'], a['vid_desc'])
            if 'youtube_url' in a:
                meetingObj.youtubeURL = a['youtube_url']
            if 'playlist' in a:
                meetingObj.playlist = a['playlist']
            self.allMeetings[meetingId] = meetingObj
            

    def match(self, videoTitle, minutesAllow, zoneInfo=ZoneInfo('US/Eastern')):
        matches = list()
        sections = videoTitle.split(' ')
        if (len(sections) < 3 or len(sections[1]) < 11 or len(sections[2]) < 6 or
            not sections[1][3:].isdigit() or not sections[2].isdigit()):
            # TODO: print some error messages
            print('Video title error: %s' % videoTitle)
            return None
        year = int(sections[1][3:7])
        month = int(sections[1][7:9])
        day = int(sections[1][9:11])
        hour = int(sections[2][:2])
        mins = int(sections[2][2:4])
        sec = int(sections[2][4:6])
        video_dt = datetime(year, month, day, hour, mins, sec, tzinfo=ZoneInfo('UTC'))
        
        zoomId = sections[0]
        if not is_canonical(zoomId):
            print("Not a valid canonical ZoomID: %s" % videoTitle)
            return

        maxDif = timedelta(minutes=minutesAllow)
        for meetingId in self.allMeetings:
            meeting = self.allMeetings[meetingId]
            if zoomId != meeting.getCanonicalZoomId():
                continue
            
            time_diff = video_dt - meeting.startTime
            if meeting.startTime >= video_dt:
                time_diff = meeting.startTime - video_dt
            if time_diff <= maxDif:
                matches.append(meeting)

        if len(matches) == 0:
            return None
        elif len(matches) > 1:
            # TODO: print a warning
            # and select the closest meeting time
            pass

        return matches[0]


if __name__ == '__main__':
    meetingDB = MeetingDB("data/meetings.csv")
    print(len(meetingDB.allMeetings))