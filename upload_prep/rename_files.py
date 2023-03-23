'''
Rename files by adding a prefix for the Zoom Account

Author: Yingjie Tong
Project: https://github.com/jackwaashere/video_upload


- Sample Input and Output

$ python3 rename_files.py --working_dir "my_folder/Z09-1223"

output> Renaming GMT20220812-183013_Recording_1760x820.mp4 to Z09-GMT20220812-183013_Recording_1760x820___2022-08-12___Summer AI005-36 Java L4 Fri 14:30-16:00 ET & Sun 19:30-21:00 ET___Ali Fakhry.mp4
output> Renaming GMT20221218-225935_Recording.transcript.vtt to Z09-GMT20221218-225935_Recording.transcript___2022-12-18___秋-AI005L2-18 Java 1on1 Sun 18:00-19:30 ET___Krishna Cheemalapati.vtt
output> Renaming GMT20220828-232944_Recording_1760x900.mp4 to Z09-GMT20220828-232944_Recording_1760x900___2022-08-28___Summer AI005-36 Java L4 Fri 14:30-16:00 ET & Sun 19:30-21:00 ET___Ali Fakhry.mp4
output> Renaming GMT20221204-200309_Recording_1686x768.mp4 to Z09-GMT20221204-200309_Recording_1686x768___2022-12-04___秋-Math202L1-1 AMC 10 Sun 15:00-16:00 ET___James Leung.mp4
output> NOT MATCHED
output> Renaming GMT20220908-195529_Recording.transcript.vtt to Z09-GMT20220908-195529_Recording.transcript.vtt
output> Completed!
output> 4/5 matched


- Another Example

$ python3 rename_files.py --working_dir "my_folder/Z5-1223"

output> The directory name is not a valid Zoom ID, but is similar to Z05. If this is not a mistake,
        type 'Y' to continue. Type anything else to terminate.
input>  no
output> Terminating code by user input
'''

import os
import os.path
import argparse
from zoneinfo import ZoneInfo
import csv
from datetime import datetime
from datetime import timedelta
import urllib.request


# Predefined Standard Zoom accounts used for matching purpose
ZOOM_ACCOUNTS = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'Z07', 'Z08', 'Z09',
    'Z10', 'Z11', 'Z12', 'Z13', 'Z14', 'Z16', 'Z17', 'Z18', 'Z19']

ZOOM_KEY = {
    "MNCCS.zoom.04@gmail.com": "Z12",
    "z1@thinklandai.com": "Z01",
    "z7@thinklandai.com": "Z07",
    "z3@thinklandai.com": "Z03",
    "z4@thinklandai.com": "Z04",
    "z9@thinklandai.com": "Z09",
    "teach@thinkland.ai": "Z06",
    "z11@thinklandai.com": "Z11",
    "cnscc16@chicagochinesecenter.com": "Z13",
    "z2@thinklandai.com": "Z02",
    "cnscc17@chicagochinesecenter.com": "Z14",
    "z5@thinklandai.com": "Z05",
    "z10@thinklandai.com": "Z10",
    "hcsgb_minor@hopechineseschool.org": "Z16",
    "z8@thinklandai.com": "Z08",
    "enrichmentclass3@tvcs.ngo": "Z19",
    "enrichmentclass2@tvcs.ngo": "Z18",
    "Z01-TL": "Z01",
    "Z02-TL": "Z02",
    "Z03-TL": "Z03",
    "Z04-TL": "Z04",
    "Z05-TL": "Z05",
    "Z06-TL0": "Z06",
    "Z07-TL": "Z07",
    "Z08-TL": "Z08",
    "Z09-TL": "Z09",
    "Z10-TL": "Z10",
    "Z11-TL": "Z11",
    "Z14-CNSCC17": "Z14",
    "Z13-CNSCC16": "Z13",
}
#"sqinga3@bostoncccc.org": "?",
#"teachersun.hxbg@gmail.com": "?",
#"aicode1@huaxiabh.org": "?",

SKIP_PAST = [
    "sqinga3@bostoncccc.org",
    "teachersun.hxbg@gmail.com",
    "aicode1@huaxiabh.org"
]

def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'_')
    return value

def is_canonical(id):
    for key in ZOOM_KEY:
        if id == ZOOM_KEY[key]:
            return True
    return False


def get_canonical_zoom_id(account):
    if account in ZOOM_KEY:
        return ZOOM_KEY[account]
    # check whether account is already a canonical zoom id
    # if not, return a warning
    
    if (not is_canonical(account)) and account not in SKIP_PAST:
        pass
        #print('Zoom ID "' + account + '" is not a key nor a canonical ID itself.', sys.stderr)
    return account

class Meeting:
    def __init__(self, startTime, endTime, className, classId, teacherName, rawZoomId, reported, video, title, description):
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
    def __init__(self, csvReader, zoneInfo=ZoneInfo('US/Eastern')):
        allMeetingsDict = {}
        first = True
        for line in csvReader:
            cur = {'date': line['Class Date'], 'stime': line['Start Time'],
                'etime': line['End Time'], 'className': line['Class Name'],
                'classId': line['Class ID'], 'teacher': line['Teacher Name'],
                'title': line['YouTube Title'], 'description': line['YouTube Description'],
                'rawZoom': line['Zoom ID'], 'reported': line['Reported'], 'video': ''}
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
        sections = videoTitle.split('_')[0].split('-')
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


def validFormat(prefix):
    '''create a prefix closer to the valid format'''
    changes = prefix
    if len(changes) > 0 and changes[0] == 'z':
        changes = 'Z' + changes[1:]

    if len(changes) == 2 and changes[1].isdigit():
        return changes[0] + '0' + changes[1]

    if len(changes) >= 3 and not changes[2].isdigit() and changes[1].isdigit():
        return changes[0] + '0' + changes[1]
    return changes[0:min(len(changes), 3)]

if __name__ == '__main__':
    url = 'https://tinyurl.com/thinkland-csv'
    response = urllib.request.urlopen(url)
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.DictReader(lines)

    parser = argparse.ArgumentParser()
    parser.add_argument('--working_dir', default='.',
        help='''the directory where the files that need to be renamed 
        are being stored, would be \'.\' if ran in the current directory''')
    args = parser.parse_args()

    wd = os.path.abspath(args.working_dir)
    # dirname = wd.split('/')[-1]
    dirname = os.path.basename(wd)
    zoomPrefix = dirname.split('-')[0]

    meetingDB = MeetingDB(cr)

    if zoomPrefix not in ZOOM_ACCOUNTS:
        ''' check if prefix is similar to a zoom account name '''
        edited = validFormat(zoomPrefix)
        valid = edited in ZOOM_ACCOUNTS
        if valid:
            res = input('The directory name is not a valid Zoom ID, but is similar to ' + edited +
            '. If this is not a mistake, type \'Y\' to continue. Type anything else to terminate.\n')
            if res != 'Y' and res != 'y':
                print('Terminating code by user input')
                exit()
        else:
            print('No valid Zoom ID was found in the directory name')
            exit()


    matched_cnt = 0
    total_cnt = 0
    for fname in os.listdir(wd):
        if len(fname) >= 3 and fname[0 : 3] == 'GMT':
            matched = meetingDB.match(zoomPrefix + '-' + fname, 15)
            newFile = zoomPrefix + '-' + fname
            if matched != None:
                matched_cnt += 1
                newFile = zoomPrefix + '-' + '.'.join(fname.split('.')[0:-1]) + '___' + str(matched.startTime)[0:10] + '___' + matched.className + '___' + matched.teacherName + '.' + fname.split('.')[-1]
            else:
                print('NOT MATCHED')
            newFile = remove(newFile, '\\/:*?"<>| ')
            oldPath = os.path.join(wd, fname)
            newPath = os.path.join(wd, newFile)
            print('Renaming ' + fname + ' to ' + newFile)
            total_cnt += 1
            
            os.rename(oldPath, newPath)

    print("Completed!")
    print(str(matched_cnt) + '/' + str(total_cnt) + ' matched')
