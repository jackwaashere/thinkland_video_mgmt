#!/usr/bin/env python
#
# This program is a Youtube Client for the AigoLearning video management
# project.
#
#
# Dependency:
# Need to run this problem with python 3.11+
# pip3 install --upgrade google-api-python-client oauth2client
#
# TODO(jacktongyj): add more documentation
#
# The OAuth2 part code uses the library from another project at
# https://github.com/tokland/youtube-upload
# Author: Arnau Sanchez <pyarnau@gmail.com>


import os
import sys
import optparse
import json
from io import open
import csv

import googleapiclient.errors

import auth
from auth import lib

from thinkland import meetingdb
import make_playlists


unprocessed_id = 'PLLoERmYbGOUn9r9pAke-3_pj-kEEj9cpl'
meetingdb_json = 'data/meetingdb.json'
playlist_json = 'data/playlist.json'

DAILY_THRESHOLD = 9000

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

def get_some_unprocessed_videos(youtube):
    """Try to retrieve some unprocessed videos.
    
    Returns a list of (video_id, title, playlist_item_id) tuples.
    
    Because of the Youtube API quota. We need to limit to process up to N videos
    a day. N is set by flag (default = 10)
    """
    request = youtube.playlistItems().list(
        part='snippet,contentDetails',
        maxResults=25, # TODO: Change maxResults to flag
        playlistId=unprocessed_id
    )
    pl_items_list = request.execute()
    ret = list()
    for item in pl_items_list['items']:
        ret.append((item['contentDetails']['videoId'], item['snippet']['title'], item['id']))
    return ret

def process_video(video, meeting, youtube):
    """Take a video, which is a (video_id, title, playlist_item_id) tuple.
    Extracts the canonical zoom account from title.
    Extracts GMT date time from title. EDIT: GMT date from meetingdb, meeting is pre-input
    Try to match to a meeting.
    If the meeting has not an associated video, call Youtube API to update the title and description
    of this video.
    Add the video into its destination playlist.
    Remove this video from the unprocessed playlist by the given playlist_item_id.
    Set the video_id back to the meetingsDB.
    """
    can_zid = video[1].split(' ')[0]  # better to get it from meeting object
    recording_start = meeting.meetingDate + meeting.startTime
    new_title = meeting.className + ' ' + meeting.teacherName + ' ' + str(recording_start)
    new_desc = '###' + can_zid + '|' + meeting.classId + '|' + str(recording_start) + '|' + meeting.teacherName + '|' + meeting.className + '###\n###YJv1###\n' + video[1]
    request = youtube.videos().update(
        part='snippet',
        body={
            'id': video[0],
            'snippet': {
                'description': new_desc,
                'title': new_title,
                'categoryId': 22
            }
        }
    )
    request.execute()
    meetingdb.log("Updated video %s %s" % (video[0], new_title))
    print(video[2])
    request = youtube.playlistItems().delete(id=video[2])
    request.execute()
    meetingdb.log("Removed video %s from unprocessed playlist" % video[0])

    # TODO: use an in-memory PlaylistManager in stead of reading file everytime.
    pl_open = open(playlist_json, mode='r')
    read = json.load(pl_open)
    pl_open.close()
    pl_id = read[meeting.classId]
    # TODO: if pl_id is None, create a new playlist

    request = youtube.playlistItems().insert(
        part='snippet',
        body={
            'snippet': {
                'playlistId': pl_id,
                # 'position': 0,
                'resourceId': {
                'kind': 'youtube#video',
                'videoId': video[0]
                }
            }
        }
    )
    request.execute()
    meetingdb.log("Add video %s %s into playlist %s" % (video[0], new_title, pl_id))



def run_main(parser, options, args, output=sys.stdout):
    """Run the main scripts from the parsed options/args."""
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError("Cannot get youtube resource")

    # call thinkland module to load the meetingDB object
    # meetingDB = None  # placeholder
    # playlistManager = None
    
    unprocessed_videos = get_some_unprocessed_videos(youtube)
    youtube_points = 0
    v_processed = 0
    for video in unprocessed_videos:
        meeting = meetingdb.match(video[1], meetingdb_json, 20, False)
        if meeting is None:
            meetingdb.log("Meeting not found: " + video[1])            
            # TODO: update the video descritiop, and move to a ErrorProcessing playlist
            continue
        
        process_video(video, meeting, youtube)
        v_processed += 1
    
        youtube_points += 160
        if youtube_points > DAILY_THRESHOLD:
            break

    # meetingdb.write_back()

    print('Videos processed: ')
    print(v_processed)        


def main(arguments):
    usage = """TODO(jacktongyj): Add usage"""
    parser = optparse.OptionParser(usage)

    # Authentication
    parser.add_option('', '--client-secrets', dest='client_secrets',
                      type="string", help='Client secrets JSON file')
    parser.add_option('', '--credentials-file', dest='credentials_file',
                      type="string", help='Credentials JSON file')
    parser.add_option('', '--auth-browser', dest='auth_browser', action='store_true',
                      help='Open a GUI browser to authenticate if required')

    options, args = parser.parse_args(arguments)

    try:
        run_main(parser, options, args)
    except googleapiclient.errors.HttpError as error:
        response = bytes.decode(error.content).strip()
        raise RequestError(u"Server response: {0}".format(response))


if __name__ == '__main__':
    main(sys.argv[1:])
