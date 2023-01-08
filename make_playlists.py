#!/usr/bin/env python
#
# Read from MeetingDB, create playlists for each class ID, write the playlistID back
# to the MeetingDB.json and/or MeetingDB.csv
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

class AuthenticationError(Exception):
    pass

class RequestError(Exception):
    pass

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
    '''Try to retrieve some unprocessed videos.
    
    Returns a list of (video_id, title, playlist_item_id) tuples.
    
    Because of the Youtube API quota. We need to limit to process up to N videos
    a day. N is set by flag (default = 10)
    '''
    pass

def process_video(video, meetingDB):
    '''Take a video, which is a (video_id, title, playlist_item_id) tuple.
    Extracts the canonical zoom account from title.
    Extracts GMT date time from title.
    Try to match to a meeting.
    If the meeting has not an associated video, call Youtube API to update the title and description
    of this video.
    Add the video into its destination playlist.
    Remove this video from the unprocessed playlist by hte given playlist_item_id.
    Set the video_id back to the meetingsDB.
    '''
    pass

def make_playlist(youtube, tlclass):
    title = tlclass.className + ' | ' + tlclass.teacherName
    desc = """###YJ1:%s:%s###""" % (tlclass.classId, tlclass.className)

    request = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': desc,
                'tags': [],
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': 'unlisted'
            }
        }
    )
    response = request.execute()
    return response['id']

def run_main(parser, options, args, output=sys.stdout):
    '''Run the main scripts from the parsed options/args.'''
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError('Cannot get youtube resource')

    with open('data/playlist_copy.json', 'w') as write:
        json.dump({}, write)

    for tlclass in meetingdb.get_classes_without_playlist():
        playlistId = make_playlist(youtube, tlclass)
        # playlistId = 'testalotoshivermetimburrs'
        # playlistId = 'aejmmnu'
        meetingdb.add_playlist(tlclass.classId, playlistId)
        # open a temp file if necessary, appending one row to the end of the temp file
        meetingdb.log('Add a new playlist: classId=' + tlclass.classId + ' - plid=' + playlistId)
    
    meetingdb.write_playlist_file()


    # print some summary to the user
    # # of videos processed

    # TODO(jacktongyj): add your business logic here
    #
    # Example: list playlist items

    # request = youtube.playlistItems().list(
    #     part="snippet,contentDetails",
    #     maxResults=100,
    #     playlistId="PLLoERmYbGOUn9r9pAke-3_pj-kEEj9cpl"
    # )

    # request = youtube.playlists().list(
    #     part="contentDetails",
    #     maxResults=100,
    #     channelId="UCrcb3-_rDP552yytnJp4_xw"
    # )

    # response = request.execute()
    # print(json.dumps(response, indent=4))
        


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
        response = bytes.decode(error.content, encoding=lib.get_encoding()).strip() # type: ignore 
        raise RequestError(u'Server response: {0}'.format(response))


if __name__ == '__main__':
    main(sys.argv[1:])
