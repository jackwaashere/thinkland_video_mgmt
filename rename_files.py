'''
Rename files by adding a prefix for the Zoom Account

Author: Yingjie Tong
Project: https://github.com/jackwaashere/video_upload




$ python3 rename_files.py --working_dir "my_folder/Z5-1223"

output> The directory name is not a valid Zoom ID, but is similar to Z05. If this is not a mistake, type 'Y' to continue. Type anything else to terminate.
input>  no
output> Terminating code by user input



- Sample Input and Output



$ python3 rename_files.py --working_dir "my_folder/Z09-1223"

output> Renaming GMT20220812-183013_Recording_1760x820.mp4 to Z09-GMT20220812-183013_Recording_1760x820.mp4
output> Renaming GMT20221218-225935_Recording.transcript.vtt to Z09-GMT20221218-225935_Recording.transcript.vtt
output> Renaming GMT20220828-232944_Recording_1760x900.mp4 to Z09-GMT20220828-232944_Recording_1760x900.mp4
output> Renaming GMT20221204-200309_Recording_1686x768.mp4 to Z09-GMT20221204-200309_Recording_1686x768.mp4
output> Renaming GMT20221008-202855_Recording_1760x900.mp4 to Z09-GMT20221008-202855_Recording_1760x900.mp4
output> Renaming GMT20220828-190822_Recording.transcript.vtt to Z09-GMT20220828-190822_Recording.transcript.vtt
output> Renaming GMT20221023-005552_Recording.transcript.vtt to Z09-GMT20221023-005552_Recording.transcript.vtt
output> Renaming GMT20220808-195529_Recording.transcript.vtt to Z09-GMT20220808-195529_Recording.transcript.vtt

(too much output)...

output> Renaming GMT20220916-220003_Recording_1920x1030.mp4 to Z09-GMT20220916-220003_Recording_1920x1030.mp4
output> Renaming GMT20221101-230107_Recording_3026x1872.mp4 to Z09-GMT20221101-230107_Recording_3026x1872.mp4
output> Completed!





$ python3 rename_files.py --working_dir "my_folder/Z10-1223"

Renaming GMT20220717-152718_Recording_1920x1080.mp4 to Z10-GMT20220717-152718_Recording_1920x1080.mp4
Renaming GMT20220810-125023_Recording_3840x2300.mp4 to Z10-GMT20220810-125023_Recording_3840x2300.mp4
Renaming GMT20220907-230058_Recording_1920x1080.mp4 to Z10-GMT20220907-230058_Recording_1920x1080.mp4
Renaming GMT20221114-230124_Recording_1920x1020.mp4 to Z10-GMT20221114-230124_Recording_1920x1020.mp4
Renaming GMT20221102-215507_Recording.transcript.vtt to Z10-GMT20221102-215507_Recording.transcript.vtt

(too much output)...

Renaming GMT20221024-220114_Recording_gallery_1920x1080.mp4 to Z10-GMT20221024-220114_Recording_gallery_1920x1080.mp4
Renaming GMT20220904-191702_Recording_gallery_1920x1058.mp4 to Z10-GMT20220904-191702_Recording_gallery_1920x1058.mp4
Renaming GMT20221010-215814_Recording.txt to Z10-GMT20221010-215814_Recording.txt
Renaming GMT20221204-232414_Recording_1920x1080.mp4 to Z10-GMT20221204-232414_Recording_1920x1080.mp4
Completed!
'''

import os
import os.path
import argparse

# Predefined Standard Zoom accounts used for matching purpose
ZOOM_ACCOUNTS = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'Z07', 'Z08', 'Z09',
    'Z10', 'Z11', 'Z12', 'Z13', 'Z14', 'Z16', 'Z17', 'Z18', 'Z19']

def validFormat(prefix):
    '''create a prefix closer to the valid format'''
    changes = prefix
    if len(changes) > 0 and changes[0] == 'z':
        changes = 'Z' + changes[1:]

    if len(changes) == 2 and changes[1].isdigit():
        return changes[0] + '0' + changes[1]

    if len(changes) >= 3 and not changes[2].isdigit() and changes[1].isdigit():
        return changes[0] + '0' + changes[1]
    return changes[0:min(len(changes), 3)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--working_dir', default='.',
        help='''the directory where the files that need to be renamed 
        are being stored, would be \'.\' if ran in the current directory''')
    args = parser.parse_args()

    wd = os.path.abspath(args.working_dir)
    dirname = wd.split('/')[-1]
    zoomPrefix = dirname.split('-')[0]

    valid = False
    for zacc in ZOOM_ACCOUNTS:
        if zacc == zoomPrefix:
            valid = True
            break
    
    if not valid:
        ''' check if prefix is similar to a zoom account name '''
        edited = validFormat(zoomPrefix)
        for zacc in ZOOM_ACCOUNTS:
            if zacc == edited:
                valid = True
                break
        if valid:
            res = input('The directory name is not a valid Zoom ID, but is similar to ' + edited +
            '. If this is not a mistake, type \'Y\' to continue. Type anything else to terminate.\n')
            if res != 'Y' and res != 'y':
                print('Terminating code by user input')
                exit()
        else:
            print('No valid Zoom ID was found in the directory name')
            exit()

    for file in os.listdir(wd):
        if len(file) >= 3 and file[0 : 3] == 'GMT':
            newFile = zoomPrefix + '-' + file
            oldPath = os.path.join(wd, file)
            newPath = os.path.join(wd, newFile)
            print('Renaming ' + file + ' to ' + newFile)
            os.rename(oldPath, newPath)

    print("Completed!")

