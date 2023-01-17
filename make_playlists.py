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
# import json
from io import open
import csv
import time

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

def make_playlist(youtube, plist_info, classId):
    title = plist_info['Playlist Title']
    desc = """###YJv1:%s###""" % (classId)

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
    log("Created a new playlist %s : %s" % (response['id'], title))
    return response['id']


def run_main(parser, options, args, output=sys.stdout):
    """Run the main scripts from the parsed options/args."""
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError("Cannot get youtube resource")

    playlist_json_file = options.playlist_json or 'data/playlist.json'
    playlistDB = classes.PlaylistDB(playlist_json_file)

    quota_usage = 0
    playlists_made = 0
    playlists_skipped = 0
    quota_exceeded = False
    for classId in playlistDB.allPlaylists:
        if playlistDB.getPlaylistId(classId) == None:
            if not quota_exceeded:
                time.sleep(0.5)
                pl_id = make_playlist(youtube, playlistDB.allPlaylists[classId], classId)
                quota_usage += 50
                playlists_made += 1
                playlistDB.updatePlaylistId(classId, pl_id)
                playlistDB.writeBack()
                if quota_usage >= DAILY_THRESHOLD:
                    log('Reached daily limit')
                    quota_exceeded = True
            else:
                playlists_skipped += 1


    # print some summaries, e.g. how many new playlists are created
    # and how many more playlists need to be created next time with new Daily quota
    log('Created %d playlists' % playlists_made)
    if playlists_skipped > 0:
        log('%d playlists need to be created next time with more YouTube daily quota' % playlists_skipped)
    else:
        log('Created all the playlists')

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
