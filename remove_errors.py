#!/usr/bin/env python
#
# This program is a Youtube Client that removes some videos from the Unprocessed playlist

import os
import sys
import optparse
import json
from io import open
import csv

import googleapiclient.errors

import auth
from auth import lib

# from thinkland import classes
from thinkland.classes import log
from thinkland.classes import appendProcessedVideo
from thinkland.playlist import PlaylistDB
from thinkland.meeting import MeetingDB

unprocessed_playlist = 'PLzr1p9rMdhyAPAN1c6O-AeoJPUk4LkQj2'

UNPROCESSED_LIMIT = 50


class AuthenticationError(Exception): pass

class RequestError(Exception): pass

def get_youtube_handler(options):
    """Return the API Youtube object."""
    home = os.path.expanduser("~")
    default_credentials = os.path.join(home, ".youtube-upload-credentials.json")
    client_secrets = options.client_secrets or os.path.join(home, ".client_secrets.json")
    credentials = options.credentials_file or default_credentials
    lib.debug("Using client secrets: {0}".format(client_secrets))
    lib.debug("Using credentials file: {0}".format(credentials))
    get_code_callback = (auth.browser.get_code
                         if options.auth_browser else auth.console.get_code)
    return auth.get_resource(client_secrets, credentials,
                             get_code_callback=get_code_callback)


def get_unprocessed_videos(youtube, playlistDB, meetingDB, process_limit, minutesAllow=15):
    next_page_token = ''
    ret = list()
    eligible = 0
    page = 1
    while eligible < process_limit:
        print("start Unprocessed Page %d" % page)
        page += 1
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            maxResults=UNPROCESSED_LIMIT,
            pageToken=next_page_token,
            playlistId=unprocessed_playlist
        )
        pl_items_list = request.execute()

        # print(json.dumps(pl_items_list, indent=4))

        for item in pl_items_list['items']:
            video = {
                    'id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'desc': item['snippet']['description'],
                    'itemId': item['id']
                }

            if errorVideo(video):
                ret.append(video)
                eligible += 1
                if eligible >= process_limit:
                    break
            
        if "nextPageToken" in pl_items_list:
            next_page_token = pl_items_list['nextPageToken']
        else:
            break
    return ret


def errorVideo(video):
    sections = video['title'].split(' ')
    if (len(sections) < 3 or len(sections[1]) < 11 or len(sections[2]) < 6 or
            not sections[1][3:].isdigit() or not sections[2].isdigit()):
        return True
    return False


def dry_run(youtube, playlistDB, meetingDB, processLimit, minutesAllow=15):
    unprocessed_videos = get_unprocessed_videos(youtube, playlistDB, meetingDB, processLimit)

    count_matched = 0
    count_valid = 0
    for video in unprocessed_videos:
        if errorVideo(video):
            # TODO: print some error messages
            print('Video title error: %s' % video['title'])
            original_title = video["desc"].split("\n")[-1]
            print("oritinal title: %s" % original_title)
            meeting = meetingDB.match(original_title, minutesAllow)
            if not meeting:
                print("not found meeting")
                continue

            playlist = playlistDB.getPlaylistId(meeting.classId, meeting.teacherName)
            if not playlist:
                print("not found playlist")
                continue

            next_page_token = ""
            found = False
            while not found:
                request = youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    maxResults=UNPROCESSED_LIMIT,
                    pageToken=next_page_token,
                    playlistId=playlist
                )
                pl_items_list = request.execute()

                for item in pl_items_list['items']:
                    if item['contentDetails']['videoId'] != video['id']:
                        continue

                    # request = youtube.playlistItems().delete(id=video['itemId'])
                    # request.execute()
                    # log('Removed video %s from unprocessed playlist' % video['id'])
                    print("The video is already in the target playlist.")
                    found = True
                    break

                if "nextPageToken" in pl_items_list:
                    next_page_token = pl_items_list['nextPageToken']
                else:
                    break



def run_main(parser, options, args, output=sys.stdout, minutesAllow=15):
    """Run the main scripts from the parsed options/args."""
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError("Cannot get youtube resource")

    meeting_csv_file = options.meeting_csv or 'data/meetings.csv'
    playlistDB = PlaylistDB(meeting_csv_file)
    meetingDB = MeetingDB(meeting_csv_file)
    processedCSV = options.processed_csv or 'data/processed.csv'

    process_limit = options.process_limit or 50

    if not options.dry_run_off:
        dry_run(youtube, playlistDB, meetingDB, process_limit)
        return
    
    unprocessed_videos = get_unprocessed_videos(youtube, playlistDB, meetingDB, process_limit)
    youtube_points = 1
    v_processed = 0
    skip_processed = 0

    for video in unprocessed_videos:
        if errorVideo(video):
            # TODO: print some error messages
            print('Video title error: %s' % video['title'])
            original_title = video["desc"].split("\n")[-1]
            print("oritinal title: %s" % original_title)
            meeting = meetingDB.match(original_title, minutesAllow)
            if not meeting:
                print("not found meeting")
                continue

            playlist = playlistDB.getPlaylistId(meeting.classId, meeting.teacherName)
            if not playlist:
                print("not found playlist")
                continue

            next_page_token = ""
            found = False
            while not found:
                request = youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    maxResults=UNPROCESSED_LIMIT,
                    pageToken=next_page_token,
                    playlistId=playlist
                )
                pl_items_list = request.execute()

                for item in pl_items_list['items']:
                    if item['contentDetails']['videoId'] != video['id']:
                        continue

                    print("The video is already in the target playlist.")
                    request = youtube.playlistItems().delete(id=video['itemId'])
                    request.execute()
                    log('Removed video %s from unprocessed playlist' % video['id'])
                    found = True
                    break

                if "nextPageToken" in pl_items_list:
                    next_page_token = pl_items_list['nextPageToken']
                else:
                    break


def main(arguments):
    usage = """TODO(jackwaashere): Add usage"""
    parser = optparse.OptionParser(usage)

    # Authentication
    parser.add_option('', '--client-secrets', dest='client_secrets',
                      type="string", help='Client secrets JSON file')
    parser.add_option('', '--credentials-file', dest='credentials_file',
                      type="string", help='Credentials JSON file')
    parser.add_option('', '--auth-browser', dest='auth_browser', action='store_true',
                      help='Open a GUI browser to authenticate if required')

    # Business specific flags
    parser.add_option('', '--meeting_csv', dest='meeting_csv',
                      type="string", help='path to the csv file of meetingDB')
    parser.add_option('', '--processed_csv', dest='processed_csv',
                      type='string', help='path to the csv file for processed vidoes')
    parser.add_option('', '--dry_run_off', dest='dry_run_off', action='store_true',
                      help='Turns off dry run mode')
    parser.add_option('', '--process_limit', dest='process_limit',
                      type='int', help='Limit the maximum number of videos to process')

    options, args = parser.parse_args(arguments)

    try:
        run_main(parser, options, args)
    except googleapiclient.errors.HttpError as error:
        response = bytes.decode(error.content).strip()
        raise RequestError(u"Server response: {0}".format(response))


if __name__ == '__main__':
    main(sys.argv[1:])
