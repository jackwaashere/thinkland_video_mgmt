#!/usr/bin/env python
#
# Rollback the videos in the ErrorProcessing playlist to the Unprocessed Playlist
# Also remove the first line of the description of the video
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

from thinkland import classes
from thinkland.classes import log


unprocessed_playlist = 'PLzr1p9rMdhyAPAN1c6O-AeoJPUk4LkQj2'
error_processing_playlist = 'PLzr1p9rMdhyCZ-wxUPEUy7plgIWP_l-cI'

#unprocessed_playlist = 'PLLoERmYbGOUn9r9pAke-3_pj-kEEj9cpl'
#error_processing_playlist = 'PLLoERmYbGOUkL5PX69LpM4bUiMYjhzOk2'

DAILY_THRESHOLD = 5999 # 9000

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

def get_some_error_processing_videos(youtube):
    """Try to retrieve some unprocessed videos.
    
    Returns a list of (video_id, title, playlist_item_id) tuples.
    EDIT: {'id': video_id, 'title': video_title, 'desc': video_description, 'itemId': playlist_item_id} dict
    
    Because of the Youtube API quota. We need to limit to process up to N videos
    a day. N is set by flag (default = 10)
    """
    request = youtube.playlistItems().list(
        part='snippet,contentDetails',
        maxResults=25, # TODO: Change maxResults to flag
        playlistId=error_processing_playlist
    )
    pl_items_list = request.execute()
    ret = list()
    for item in pl_items_list['items']:
        ret.append(
            {
                'id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'desc': item['snippet']['description'],
                'itemId': item['id']
            }
        )
    return ret
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
    can_zid = video['title'].split(' ')[0]  # better to get it from meeting object
    recording_start = meeting.startTime
    # new_title = meeting.className + ' ' + meeting.teacherName + ' ' + str(recording_start)
    # if "gallery" in video['title']:
    #     new_title = new_title + " Gallery"

    # new_desc = '###' + can_zid + '|' + meeting.classId + '|' + str(recording_start) + '|' + meeting.teacherName + '|' + meeting.className + '###\n###YJv1###\n' + video['title']
    request = youtube.videos().update(
        part='snippet',
        body={
            'id': video['id'],
            'snippet': {
                'description': '',
                'title': video['title'],
                'categoryId': 22
            }
        }
    )
    request.execute()
    log("Updated video %s %s" % (video['id'], new_title))

    request = youtube.playlistItems().insert(
        part='snippet',
        body={
            'snippet': {
                'playlistId': meeting.playlist,
                'resourceId': {
                'kind': 'youtube#video',
                'videoId': video['id']
                }
            }
        }
    )
    request.execute()
    log("Add video %s %s into playlist %s" % (video['id'], new_title, meeting.playlist))

    request = youtube.playlistItems().delete(id=video['itemId'])
    request.execute()
    log("Removed video %s from unprocessed playlist" % video['id'])

def process_video(youtube, video):
    # first, remove the first line of the description
    desc = video['desc'].split('\n')
    new_desc = video['desc']
    if len(desc) > 0:
        new_desc = '\n'.join(desc[1:])

    request = youtube.videos().update(
        part='snippet',
        body={
            'id': video['id'],
            'snippet': {
                'title': video['title'],
                'description': new_desc,
                'categoryId': 22
            }
        }
    )
    request.execute()
    log('Updated video %s description' % video["id"])
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": unprocessed_playlist,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video['id']
                }
            }
        }
    )
    request.execute()
    log('Added video %s to unprocessing playlist' % video['id'])
    request = youtube.playlistItems().delete(id=video['itemId'])
    request.execute()
    log('Removed video %s from error-processing playlist' % video['id'])



def run_main(parser, options, args, output=sys.stdout):
    """Run the main scripts from the parsed options/args."""
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError("Cannot get youtube resource")
    
    unprocessed_videos = get_some_error_processing_videos(youtube)
    youtube_points = 1
    v_processed = 0

    for video in unprocessed_videos:
        process_video(youtube, video)
        
        v_processed += 1
        youtube_points += 160
        if youtube_points > DAILY_THRESHOLD:
            print('Videos processed: ' + str(v_processed))
            print("Reached daily youtube points threshold: %d" % youtube_points)
            break

    print('Videos processed: ' + str(v_processed))
    print('Used daily youtube points: %d' % youtube_points)


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

    # Business specific flags
    parser.add_option('', '--meeting_json', dest='meeting_json',
                      type="string", help='path to the json file of meetingDB')
    parser.add_option('', '--playlist_json', dest = 'playlist_json',
                      type='string', help='path to the json file of playlistDB')

    options, args = parser.parse_args(arguments)

    try:
        run_main(parser, options, args)
    except googleapiclient.errors.HttpError as error:
        response = bytes.decode(error.content).strip()
        raise RequestError(u"Server response: {0}".format(response))


if __name__ == '__main__':
    main(sys.argv[1:])
