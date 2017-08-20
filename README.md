### What is this?

hdrctl is a proxy designed to swap out requests for DRM'd content with video output captured from a physical windows machine running the native HDHomeRunView application with changes to tuner channels done by emulating keystrokes on windows machine.

The longterm goal is for this setup to behave like a HDHR with one tuner to clients incapable of handling the DRM streams (plex, kodi, android tv channels, etc).

### What works?

* Autohotkey script that reads from a file and sends the commands to the HDHRView app running on Windows 10
* discover.py to replace your hdhr's discovery response with your proxy url (and reset tuners to 1)
* lineup.py to replace your hdhr's lineup with your real line up and generate a sources.json file for node-ffmpeg-mpegts-proxy
* channel.py which is invoked on a stream-open will write to the file that autohotkey on the windows machine is monitoring to change channels

### What doesn't work
* still not enough to trick Plex into thinking it's a real HDHR, may need to implement the discovery protocol on tcp/udp 65001

### Requirements
1. HDHR Hardware
2. Some kind of HDMI capture setup (I'm using a LKV373A)
3. Windows machine with windows 10 that can run the HDHRView app and receive DRM'd channels
4. Linux server (might be possible to run this on windows machine at your own risk), webserver running on port 80
5. node-ffmpeg-mpegts-proxy installed

### Directions (Don't actually work yet)

The LKV373A boots in multicast mode and it assigns itself 192.168.1.238, so plug it directly into an ethernet card on your linux machine and bring it up:
```
# bring up the captive interface
/sbin/ifconfig eth0 192.168.1.101
# kick the sender into unicast mode to the IP we just configured
/usr/bin/curl 'http://192.168.1.238/dev/info.cgi?action=streaminfo&rtp=on&multicast=on&mcastaddr=192.168.1.101'
# theoretically you don't need this if you can get rtp streaming to work
/sbin/iptables -t raw -A PREROUTING -p udp -m length --length 28 -j DROP
```

You might want to shove that into rc.local

Install channel.py into /usr/local/bin
run 
```
curl http://ipv4-api.hdhomerun.com/discover > api.json
```
Look in api.json and find "DiscoverURL" and "LineupURL" and grab those *substituting your URLs*:
```
curl  "http://192.168.0.41:80/discover.json" > discover.json
curl  "http://192.168.0.41:80/lineup.json" > lineup.json
```

Now rebuild the json files for the proxy *substituting your proxy ip*:
```
./discover.py rpi.rhp.org discover.json discover-out.json
./lineup.py rpi.rhp.org lineup.json lineup-out.json sources-out.json
```
And copy them to /var/www:
```
sudo cp discover-out.json /var/www/html/discover.json
sudo cp lineup-out.json /var/www/html/lineup.json
```

copy the sources-out.json to where you installed node-ffmpeg-mpegts-proxy:
```
cp sources-out.json ~/node-ffmpeg-mpegts-proxy/
```

run node-ffmpeg-mpegts-proxy *subsituting your ffmpeg/avconv location*:
```
cd ~/node-ffmpeg-mpegts-proxy
node ./node-ffmpeg-mpegts-proxy.js -p 5004 -s sources-out.json  -a /usr/local/bin/ffmpeg
```

/capability and /lineup_status.json:
Not sure what /capability is and why plex requests it, but it returns a 404 on my device.
lineup_status.json I think you can just copy unchanged
```
curl  "http://192.168.0.41:80/lineup_status.json" > /var/www/html/lineup.json
```


Proxy 65001 service (probably needed):
(TBD)


Proxy discovery api service (not sure if needed):

Host hack/DNS hijack ipv4-api.hdhomerun.com to point to your proxy and use discover-api.py to generate your /discover file 


Proxy the remaining ports (if needed):
(TBD)








