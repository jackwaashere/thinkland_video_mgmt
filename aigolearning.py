import csv
import json
import argparse
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

parser = argparse.ArgumentParser()
parser.add_argument('-cmd', type=str, help='execute specific code', choices={'writeJSON', 'parseDates'})
parser.add_argument('-cname', type=str, help='class name for specific commands')
args = parser.parse_args()

class ZoomAccount:
    """
    id: Zoom ID
    email: the email linked to the zoom account
    meeting: the meeting ID
    url: the meeting url
    """
    def __init__(self, id, email, meeting, url):
        self.id = id
        self.email = email
        self.metting = meeting
        self.url = url

class ThinklandClass:
    """
    time: the number of minutes into a day this recording begins
    day: the day of the week this recording takes place on
    name: the name of this recording
    teacher: name of the teacher
    id: Zoom ID
    """
    def __init__(self, time, day, name, teacher, id, classDates):
        self.time = time
        self.day = day
        self.name = name
        self.teacher = teacher
        self.zoomId = id
        self.classDates = classDates

    def getZoomAccount():
        """Returns the zoom account part from the original zoom id.
        
        E.g. zoom id is "Z05-TL", returns a valid zoom account like "Z05".
        """
        pass

classList = list()

def readCSV():
    with open('test.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        firstRow = True

        for row in reader:
            if firstRow:
                firstRow = False
            else:
                newTLClass = ThinklandClass(row['Class Time (ET)'],
                    row['Day of Week'], row['Class Name'],
                    row['Teacher Name'], row['Zoom ID'], row['Class Date'])
                classList.append(newTLClass)

def writeJSON():
    with open('thinklandClassesData.json', mode='w') as output:
        ret = dict()
        for TLClass in classList:
            ret[TLClass.name] = {'time': TLClass.time, 'day': TLClass.day,
                'teacher': TLClass.teacher, 'zoomid': TLClass.zoomId, 'date': TLClass.classDates}
        json.dump(ret, output, indent=4)

def getStartEndDate():
    utc = ZoneInfo('UTC')
    et = ZoneInfo('US/Eastern')
    cname = args.cname
    fullDates = ''
    fullTime = ''
    with open('thinklandClassesData.json', mode='r') as in_put:
        read = json.loads(in_put.read())
        fullDates = read[cname]['date']
        fullTime = read[cname]['time']
    fullDate1 = fullDates.split('-')[0]
    fullDate2 = fullDates.split('-')[1]
    startDate = datetime(int(fullDate1.split('/')[2]),
        int(fullDate1.split('/')[0]), int(fullDate1.split('/')[1]),
        int(fullTime[4:6]), int(fullTime[7:9]), 0, 0, et).astimezone(utc)
    endDate = datetime(int(fullDate2.split('/')[2]),
        int(fullDate2.split('/')[0]), int(fullDate2.split('/')[1]),
        int(fullTime[4:6]), int(fullTime[7:9]), 0, 0, et).astimezone(utc)
    return [startDate, endDate]

def expandClassDates(classDateStr, classTimeStr, zoneinfo=ZoneInfo('US/Eastern')):
    """
    classDateStr: xxx, e.g. "09/16/2022-01/13/2023"
    classTimeStr: xxx, e.g. "Fri 19:00-20:00"

    returns a list of tuple (startDateTime, endDateTime) which covers all
    lessons in this class, ordered by startDateTime.
    The returned datetime objects will use the zoneinfo passed from the input.
    """
    ret = []
    delta = timedelta(days=7)

    classDateStrFirst = classDateStr.split('-')[0]
    classDateStrLast = classDateStr.split('-')[1]
    classDateYearFirst = int(classDateStrFirst.split('/')[2])
    classDateYearLast = int(classDateStrLast.split('/')[2])
    classDateMonthFirst = int(classDateStrFirst.split('/')[0])
    classDateMonthLast = int(classDateStrLast.split('/')[0])
    classDateDayFirst = int(classDateStrFirst.split('/')[1])
    classDateDayLast = int(classDateStrLast.split('/')[1])

    classTimeClean = classTimeStr.split(' ')[1]
    classTimeFirst = classTimeClean.split('-')[0]
    classTimeEnd = classTimeClean.split('-')[1]
    classTimeHourFirst = int(classTimeFirst.split(':')[0])
    classTimeHourEnd = int(classTimeEnd.split(':')[0])
    classTimeMinFirst = int(classTimeFirst.split(':')[1])
    classTimeMinEnd = int(classTimeEnd.split(':')[1])

    curClassBegin = datetime(classDateYearFirst, classDateMonthFirst,
        classDateDayFirst, classTimeHourFirst, classTimeMinFirst, tzinfo=zoneinfo)
    curClassEnd = datetime(classDateYearFirst, classDateMonthFirst,
        classDateDayFirst, classTimeHourEnd, classTimeMinEnd, tzinfo=zoneinfo)
    lastClassBegin = datetime(classDateYearLast, classDateMonthLast,
        classDateDayLast, classTimeHourFirst, classTimeMinFirst, tzinfo=zoneinfo)

    while curClassBegin <= lastClassBegin:
        ret.append((curClassBegin, curClassEnd))
        curClassBegin += delta
        curClassEnd += delta

    return ret


def matchClassVideos(thinklandClass, rootDir, threshold=timedelta(minutes=15)):
    """
    thinklandClass:
    rootDir: is a DirectoryNode for the root dir of the thinkland videos

    returns a list of all lessions with matched videos, when there are multiple matched videos,
    return all of them.
    Example:
    [(startTime1, endTime1, [video1, video2]),
    ...
     (startTimeN, endTimeN, [videoX])]
    When there is not a matched video, the third part of the tuple is an empty list.
    The video start time should with +threshold or -threshold of the expected start time.

    Assumption:
    Two layer structure in the directories.
    The first layer directory contains zoom account, e.g. "Z5-1223"
    """
    pass

def getZoomAccountFromDirectoryName(dirName):
    """
    convert something like "Z5-1223" to a valid ZoomAccount like "Z05"
    """
    pass



if __name__ == '__main__':
    if args.cmd == 'writeJSON':
        readCSV()
        writeJSON()
    elif args.cmd == 'parseDates':
        getStartEndDate()

