#
# Read the original file from a CSV
# Dump the data into a JSON
# You can also dump data into a new CSV
#
# MeetingDB needs to frequently write data into disk whenever you make changes to the Youtube account.
# How do you make the change?
#   Always write to a temp file first. The temp file could live in the same directory, 
# with XXX.v###.json as file name
#
# For example, you read data from XXX.json
# If there is any changes, you write to XXX.v001.json
# If you make another change, you write to XXX.v002.json
# In the end, if everything goes well, you write back to XXX.json. Then remove the temp files.

import os
import csv
import json
import argparse
import sys
from thinkland.classes import Meeting
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from thinkland.zoom_canonicalize import get_canonical_zoom_id

playlist_file_path = 'data/playlist.json'
playlist_holder_file_path = 'data/playlist_copy.json'

def read_csv(inputFilePath):
    meetingsList = dict()
    with open(inputFilePath, mode='r') as fileIn:
        reader = csv.DictReader(fileIn)
        firstLine = True
        for line in reader:
            cur = {'date': line['Class Date'], 'stime': line['Start Time'],
                'etime': line['End Time'], 'className': line['Class Name'],
                'classId': line['Class ID'], 'teacher': line['Teacher'],
                'rawZoom': line['Zoom ID']}
            key = cur['classId'] + '|' + cur['date']
            meetingsList[key] = cur
    return meetingsList

def write_json(meetingsList, outputFilePath):
    with open(outputFilePath, mode='w') as fileOut:
        json.dump(meetingsList, fileOut, indent=4)

def load_meetings_from_json_file(jsonFilePath):
    ret = list()
    with open(jsonFilePath, mode='r') as fileIn:
        reader = json.load(fileIn)
        for curMeeting in reader:
            dateSections = reader[curMeeting]['date'].split('-')
            year = int(dateSections[0])
            month = int(dateSections[1])
            day = int(dateSections[2])
            tzone = ZoneInfo('US/Eastern')
            # meetingDate = datetime(year, month, day, tzinfo=tzone)

            sTimeSections = reader[curMeeting]['stime'].split(':')
            shour = int(sTimeSections[0])
            smin = int(sTimeSections[1])
            ssec = int(sTimeSections[2])
            stime = datetime(year, month, day, shour, smin, ssec, tzinfo=tzone)

            eTimeSections = reader[curMeeting]['etime'].split(':')
            ehour = int(eTimeSections[0])
            emin = int(eTimeSections[1])
            esec = int(eTimeSections[2])
            etime = datetime(year, month, day, ehour, emin, esec, tzinfo=tzone)

            thisMeeting = Meeting(stime, etime, reader[curMeeting]['className'],
                reader[curMeeting]['classId'], reader[curMeeting]['teacher'], reader[curMeeting]['rawZoom'])
            ret.append(thisMeeting)
    return ret

def print_meeting_db(meetingDict):
    for curMeeting in meetingDict:
        print(curMeeting + ':')
        info = meetingDict[curMeeting]
        print('  Date: \t' + str(info.meetingDate))
        print('  Start: \t' + str(info.startTime))
        print('  End:  \t' + str(info.endTime))
        print('  Class Name: \t' + info.className)
        print('  Class ID: \t' + info.classId)
        print('  Teacher: \t' + info.teacherName)
        print('  Raw Zoom ID: \t' + info.rawZoomId + '\n')

def get_classes_without_playlist():
    '''TODO: Change this function to check if classes have already been added to playlists'''
    possible_ret = load_meetings_from_json_file('data/meetingdb.json')
    if os.stat(playlist_file_path).st_size == 0:
        return possible_ret
    ret = list()
    with open(playlist_file_path, mode='r') as read:
        plists = json.load(read).keys()
        for possible in possible_ret:
            if not possible.classId in plists:
                ret.append(possible)
    return ret

def add_playlist(classId, playlistId):
    '''TODO: Implement temp files (playlist_temp/001.json, playlist_temp/002.json, etc)'''
    read_file_path = playlist_holder_file_path
    with open(read_file_path, mode='r') as file_in:
        edit = json.load(file_in)
        edit[classId] = playlistId
        with open(playlist_holder_file_path, mode='w') as file_out:
            json.dump(edit, file_out, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['write_json', 'read_json'])
    parser.add_argument('--csv_input_file', help='The file of the CSV input', default='data/meetings.csv')
    parser.add_argument('--json_io_file', help='The file of the json input/output', default='data/meetingdb.json')
    args = parser.parse_args()

    mode = args.mode
    if mode == 'write_json':
        meetingsList = read_csv(args.csv_input_file)
        write_json(meetingsList, args.json_io_file)
    elif mode == 'read_json':
        meetingDict = load_meetings_from_json_file(args.json_io_file)
        print_meeting_db(meetingDict)

