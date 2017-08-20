#!/usr/bin/env python3

import os
import subprocess
import sys
from urllib.parse import urlparse

OUTPUT_FILENAME = '/net/pris/Documents/keyspipe.txt'

def main(argv):
    url_param = argv[2]
    channel = url_param.split('/')[-1].split('?')[0][1:]
    print(channel)
    command = '{0}{{enter}}\r\n'.format(channel)
    with open(OUTPUT_FILENAME, 'w') as out:
        out.write(command)
        print(command)

if __name__ == '__main__':
    main(sys.argv)