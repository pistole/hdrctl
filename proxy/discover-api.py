#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import pprint


def main(argv):
    proxy_host = argv[1]
    print("proxy " + proxy_host)
    print("input " + argv[2])
    print("output " + argv[3])
    with open(argv[2], 'r') as inp:
        data = json.load(inp)
        data = data[0]
    data["DeviceID"] = data["DeviceID"] + str("251")
    data["LocalIP"] = proxy_host 
    data["BaseURL"] = "http://{0}:80".format(proxy_host) 
    data["LineupURL"] = data["BaseURL"] + "/lineup.json"
    data["DiscoverURL"] = data["BaseURL"] + "/discover.json"
    pprint.pprint(data)
    with open(argv[3], 'w') as out:
        json.dump([data], out)

if __name__ == '__main__':
    main(sys.argv)