

import csv
import json
import argparse

def main(class_list_csv_path, playlist_json_path):
    with open(class_list_csv_path, mode='r') as read:
        reader = csv.DictReader(read)
        edit = None
        with open(playlist_json_path, mode='r') as read_json:
            edit = json.load(read_json)
        for line in reader:
            if not line['Class ID'] in edit:
                edit[line['Class ID']] = {'Playlist ID': None, 'Playlist Title': line['YouTube Playlist Title']}
        with open(playlist_json_path, mode='w') as write:
            json.dump(edit, write, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--class_list_csv_path', default='data/Class_List.csv')
    parser.add_argument('--playlist_json_path', default='data/playlist.json')
    args = parser.parse_args()
    main(args.class_list_csv_path, args.playlist_json_path)
