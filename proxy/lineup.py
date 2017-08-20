#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import pprint
from urllib.parse import urlparse


def main(argv):
    proxy_host = argv[1]
    print("proxy " + proxy_host)
    print("input " + argv[2])
    print("lineup " + argv[3])
    print("sources " + argv[4])
    with open(argv[2], 'r') as inp:
        data = json.load(inp)
#    pprint.pprint(data)

    lineup_objs = []
    sources_objs = []

    for channel in data:
        channel.pop("DRM", None)
        channel_url = urlparse(channel['URL'])
        channel['URL'] = channel_url.scheme + "://"+ proxy_host + ":5004" + channel_url.path
        lineup_objs.append(channel)
        source = {
            "name": channel["GuideName"],
            "url": channel_url.path,
            "source": "udp://localhost:5004/?fifo_size=50000000&overrun_nonfatal=1",
            "prescript": "/usr/local/bin/channel.py",
            "avconvOptions": { "output": ["-bsf:v", "h264_mp4toannexb"]}   
        }

        sources_objs.append(source)

    with open(argv[3], 'w') as lineup:
        json.dump(lineup_objs, lineup)

    with open(argv[4], 'w') as sources:
        json.dump(sources_objs, sources)


if __name__ == '__main__':
    main(sys.argv)