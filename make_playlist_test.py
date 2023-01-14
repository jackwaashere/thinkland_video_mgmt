#!/usr/bin/env python
#
# Test to make a playlist within a specific channel
#
# The OAuth2 part code uses the library from another project at
# https://github.com/tokland/youtube-upload
# Author: Arnau Sanchez <pyarnau@gmail.com>


import json
import os
import sys
import optparse
from io import open

import googleapiclient.errors

import auth
from auth import lib

from thinkland import classes
from thinkland.classes import log

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



def run_main(parser, options, args, output=sys.stdout):
    """Run the main scripts from the parsed options/args."""
    youtube = get_youtube_handler(options)
    if not youtube:
        raise AuthenticationError("Cannot get youtube resource")

    # request = youtube.playlists().insert(
    #     part='snippet,status',
    #     onBehalfOfContentOwner="yingjie.tong@aigolearning.org",
    #     onBehalfOfContentOwnerChannel="UCqyDa40nr2VfpVlZVDSDUGg",
    #     body={
    #         'snippet': {
    #             'title': "Sample playlist created via API",
    #             'description': "This is a sample playlist description.",
    #             'tags': [],
    #             'defaultLanguage': 'en'
    #         },
    #         'status': {
    #             'privacyStatus': 'unlisted'
    #         }
    #     }
    # )

    # request = youtube.channels().list(
    #     part="snippet,contentDetails,statistics,contentOwnerDetails",
    #     id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
    # )

    request = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        maxResults=25
    )

    # request = youtube.channels().list(
    #     part="snippet,contentDetails,statistics,contentOwnerDetails",
    #     mine=True
    # )
    response = request.execute()
    print(json.dumps(response, indent=4))
    


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
