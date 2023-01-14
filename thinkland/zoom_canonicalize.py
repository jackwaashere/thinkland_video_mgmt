import csv
import json
import argparse
import sys


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
    "Z02-TL": "Z02",
    "z8@thinklandai.com": "Z08",
    "Z10-TL": "Z10",
    "enrichmentclass3@tvcs.ngo": "Z19",
    "enrichmentclass2@tvcs.ngo": "Z18",
    "Z08-TL": "Z08",
    "Z11-TL": "Z11",
    "Z14-CNSCC17": "Z14",
    "Z06-TL0": "Z06",
    "Z13-CNSCC16": "Z13",
    "Z03-TL": "Z03",
    "Z01-TL": "Z01",
    "Z04-TL": "Z04",
    "Z05-TL": "Z05",
    "Z07-TL": "Z07"
}
#"sqinga3@bostoncccc.org": "?",
#"teachersun.hxbg@gmail.com": "?",
#"aicode1@huaxiabh.org": "?",
    

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
    
    if (not is_canonical(account)):
        print('Zoom ID "' + account + '" is not a key nor a canonical ID itself.', sys.stderr)
    return account


def read_dict_from_csv(file_path):
    ret = dict()
    with open(file_path, mode='r') as file_in:
        reader = csv.DictReader(file_in)
        for line in reader:
            ret[line['Zoom ID']] = line['Canonical Zoom Account']
    return ret

def write_key_into_json(zoomDict, file_path):
    with open(file_path, mode='w') as file_out:
        json.dump(zoomDict, file_out, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store_keys', action='store_true')
    parser.add_argument('--zoom_key_csv_file_path', default='data/zoom_key.csv', help='CSV file of the zoom email/id to alias.')
    parser.add_argument('--zoom_key_json_file_path', default='data/zoom_key.json', help='json file where the zoom account key is exported to')
    args = parser.parse_args()

    if args.store_keys:
        zoomDict = read_dict_from_csv(args.zoom_key_csv_file_path)
        write_key_into_json(zoomDict, args.zoom_key_json_file_path)
    else:
        x = input()
        while x != 'exit':
            print(get_canonical_zoom_id(x))
            x = input()
