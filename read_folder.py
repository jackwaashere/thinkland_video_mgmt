import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--load', help='Load from json file', action='store_true')
parser.add_argument('--directory', help='The starting directory')
parser.add_argument('outputFile', help='Output FileName')
parser.add_argument('--intputFile', help='Input FileName')
args = parser.parse_args()

IS_DIR = "isDir"


if args.directory == None:
    args.directory = '.'

class DirectoryNode:
    def __init__(self, type, name, size):
        # self.dirStr = dirStr
        self.type = type
        self.name = name
        self.size = size
        self.childNodes = list()

def constructDirTree(dirStr, name=''):
    if os.path.isdir(dirStr):
        ret = DirectoryNode(True, name, 0)
        curDirStr = ''
        if dirStr != '.':
            curDirStr = dirStr + '/'
        for d in os.listdir(dirStr):
            if d[0] == '.':
                continue
            ret.childNodes.append(constructDirTree(curDirStr + d, d))
        return ret
    else:
        ret = DirectoryNode(False, name, os.path.getsize(dirStr))
        return ret

def outputChildren(curDirectory):
    cur = {IS_DIR: True}
    for d in curDirectory.childNodes:
        if d.type == 0:
            cur[d.name] = {IS_DIR: False, 'fsize': d.size}
        else:
            cur[d.name] = outputChildren(d)
    return cur

def reconstructDirTree(curDict, name=''):
    ret = DirectoryNode(curDict['isDir'], name, 0)
    if ret.type == 0:
        ret.size = curDict['fsize']
        return ret
    else:
        for d in curDict:
            if d == IS_DIR:
                continue
            ret.childNodes.append(reconstructDirTree(curDict[d], d))
        return ret

if __name__ == '__main__':
    if args.load:
        with open(args.inputFile, mode='r') as read:
            data = json.load(read)
            copy = reconstructDirTree(data)
            with open(args.outputFile, mode='w') as write:
                json.dump(outputChildren(copy), write, indent=4)
    else:
        cur = constructDirTree(args.directory)
        with open(args.outputFile, mode='w') as write:
            json.dump(outputChildren(cur), write, indent=4)
