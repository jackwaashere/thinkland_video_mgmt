import json
import csv
import sys
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from thinkland.zoom_canonicalize import get_canonical_zoom_id
from thinkland.zoom_canonicalize import is_canonical

log_file = 'data/log.txt'

# class Meeting:
#     def __init__(self, startTime, endTime, className, classId, teacherName, rawZoomId, reported, video, title, description):#, vid_title, vid_desc):
#         self.startTime = startTime
#         self.endTime = endTime
#         self.className = className
#         self.classId = classId
#         self.teacherName = teacherName
#         self.rawZoomId = rawZoomId
#         self.reported = reported
#         self.video = video
#         self.title = title
#         self.description = description
#         # self.vid_title = vid_title
#         # self.vid_desc = vid_desc
#         self.youtubeURL = None
#         self.playlist = None

#     def getCanonicalZoomId(self):
#         return get_canonical_zoom_id(self.rawZoomId)


# class MeetingDB:
#     def __init__(self, jsonFilePath, playlistDB, zoneInfo=ZoneInfo('US/Eastern')):
#         self.jsonFilePath = jsonFilePath
#         self.playlistDB = playlistDB
#         allMeetingsDict = {}
#         with open(jsonFilePath, 'r') as file_in:
#             allMeetingsDict = json.load(file_in)
#         self.allMeetings = {}
#         for meetingId in allMeetingsDict:
#             a = allMeetingsDict[meetingId]
#             sections_meet = a['date'].split('-')
#             year = int(sections_meet[0])
#             month = int(sections_meet[1])
#             day = int(sections_meet[2])
#             sections_time = a['stime'].split(':')
#             hour = int(sections_time[0])
#             mins = int(sections_time[1])
#             sec = int(sections_time[2])
#             startTime = datetime(year, month, day, hour, mins, sec, tzinfo=zoneInfo)

#             sections_time = a['etime'].split(':')
#             hour = int(sections_time[0])
#             mins = int(sections_time[1])
#             sec = int(sections_time[2])
#             endTime = datetime(year, month, day, hour, mins, sec, tzinfo=zoneInfo)
            
#             meetingObj = Meeting(startTime, endTime,
#                                  a['className'], a['classId'], a['teacher'],
#                                  a['rawZoom'], a['reported'], a['video'], a['title'], a['description'])#,
#                                 #  a['vid_title'], a['vid_desc'])
#             if 'youtube_url' in a:
#                 meetingObj.youtubeURL = a['youtube_url']
#             if 'playlist' in a:
#                 meetingObj.playlist = a['playlist']
#             if not meetingObj.playlist:
#                 meetingObj.playlist = playlistDB.getPlaylistId(meetingObj.classId)
#             self.allMeetings[meetingId] = meetingObj
            

#     def match(self, videoTitle, minutesAllow, zoneInfo=ZoneInfo('US/Eastern')):
#         matches = list()
#         sections = videoTitle.split(' ')
#         if (len(sections) < 3 or len(sections[1]) < 11 or len(sections[2]) < 6 or
#             not sections[1][3:].isdigit() or not sections[2].isdigit()):
#             # TODO: print some error messages
#             return None
#         year = int(sections[1][3:7])
#         month = int(sections[1][7:9])
#         day = int(sections[1][9:11])
#         hour = int(sections[2][:2])
#         mins = int(sections[2][2:4])
#         sec = int(sections[2][4:6])
#         video_dt = datetime(year, month, day, hour, mins, sec, tzinfo=ZoneInfo('UTC'))
        
#         zoomId = sections[0]
#         if not is_canonical(zoomId):
#             print("Not a valid canonical ZoomID: %s" % videoTitle)
#             return

#         maxDif = timedelta(minutes=minutesAllow)
#         for meetingId in self.allMeetings:
#             meeting = self.allMeetings[meetingId]
#             if zoomId != meeting.getCanonicalZoomId():
#                 continue
            
#             # if meeting.video != None:
#             #     continue

#             time_diff = video_dt - meeting.startTime
#             if meeting.startTime >= video_dt:
#                 time_diff = meeting.startTime - video_dt
#             if time_diff <= maxDif:
#                 matches.append(meeting)

#         # print(matches)
#         if len(matches) == 0:
#             return None
#         elif len(matches) > 1:
#             # TODO: print a warning
#             # and select the closest meeting time
#             pass

#         return matches[0]

#     # def writeBack(self):
#     #     # first convert self.allMeetings back dict
#     #     allMeetingsDict = dict()
#     #     for meetingId in self.allMeetings:
#     #         curMeeting = self.allMeetings[meetingId]
#     #         day = str(curMeeting.startTime)[:10]
#     #         stime = str(curMeeting.startTime)[11:19]
#     #         etime = str(curMeeting.endTime)[11:19]
#     #         d = {
#     #             'date': day,
#     #             'stime': stime,
#     #             'etime': etime,
#     #             'className': curMeeting.className,
#     #             'classId': curMeeting.classId,
#     #             'teacher': curMeeting.teacherName,
#     #             'rawZoom': curMeeting.rawZoomId,
#     #             'reported': curMeeting.reported,
#     #             'video': curMeeting.video
#     #         }
#     #         if curMeeting.youtubeURL:
#     #             d['youtube_url'] = curMeeting.youtubeURL
#     #         if curMeeting.playlist:
#     #             d['playlist'] = curMeeting.playlist
#     #         allMeetingsDict[meetingId] = d

#     #     with open(self.jsonFilePath, 'w') as write:
#     #         json.dump(allMeetingsDict, write, indent=4)

# '''
# class PlaylistDB:
#     def __init__(self, jsonPlaylistFile):
#         # classID => playlistID mapping
#         with open(jsonPlaylistFile, 'r') as file_in:
#             self.allPlaylists = json.load(file_in)
#         self.jsonPlaylistFile = jsonPlaylistFile

#     def getPlaylistId(self, classId):
#         if classId in self.allPlaylists:
#             return self.allPlaylists[classId]['Playlist ID']
#         return None
# '''

# class PlaylistDB:
#     def __init__(self, csvPlaylistFile):
#         with open(csvPlaylistFile, mode='r') as file_in:
#             self.allPlaylists = {}
#             reader = csv.DictReader(file_in)
#             for line in reader:
#                 if line['Playlist ID'] is not None:
#                     self.allPlaylists[line['Class ID']] = line['Playlist ID']
#         self.csvPlaylistFile = csvPlaylistFile
    
#     def getPlaylistId(self, classId):
#         if classId in self.allPlaylists:
#             return self.allPlaylists[classId]
#         return None

# '''
#     def updatePlaylistId(self, classId, playlistID):
#         """assumes that classId is already in the allPlaylists"""
#         if classId not in self.allPlaylists:
#             log('Class ID was not found in PlaylistDB, classId=%s, playlistId=%s' % (classId, playlistID))
#             return

#         if self.allPlaylists[classId]['Playlist ID'] != None:
#             # log('Playlist found but being overwritten; PlaylistID: ' + self.allPlaylists[tlClass.classId] +
#             #     '; Class ID: ' + tlClass.classId, True)
#             log('Playlist found but being overwritten; PlaylistID: ' + self.allPlaylists[classId]['Playlist ID'] +
#                 '; Class ID: ' + classId, True)

#         self.allPlaylists[classId]['Playlist ID'] = playlistID

#     def writeBack(self):
#         with open(self.jsonPlaylistFile, 'w') as file_out:
#             json.dump(self.allPlaylists, file_out, indent=4)
# '''

def log(message, printOnScreen=True):
    with open(log_file, mode='a') as file_out:
        file_out.write(str(datetime.now()) + ' ' + message + '\n')
    if printOnScreen:
        print(message, sys.stderr)



def appendProcessedVideo(csvFile, meeting, videoId):
    with open(csvFile, 'a') as file_out:
        date = str(meeting.startTime)[:10]
        stime = str(meeting.startTime)[11:19]
        line = '%s,%s,%s,%s,%s\n' % (meeting.classId, date, stime, meeting.teacherName, videoId)
        file_out.write(line)