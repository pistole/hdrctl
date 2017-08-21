### What is this?

hdrctl is a proxy designed to swap out requests for DRM'd content with video output captured from a physical windows machine running the native HDHomeRunView application with changes to tuner channels done by emulating keystrokes on windows machine.

The goal is for this setup to behave like a HDHR with one tuner to clients incapable of handling the DRM streams, specifically for the plex dvr functionality.

### What works?

* Autohotkey script that reads from a file and sends the commands to the HDHRView app running on Windows 10
* discover.py to replace your hdhr's discovery response with your proxy url (and reset tuners to 1)
* lineup.py to replace your hdhr's lineup with your real line up and generate a sources.json file for node-ffmpeg-mpegts-proxy
* channel.py which is invoked on a stream-open will write to the file that autohotkey on the windows machine is monitoring to change channels

### What doesn't work

* This is enough to trick plex into thinking it's a real tuner and view live channels, but I haven't tried recording with it.
* Sometimes plex just fails when trying to open the stream and I'm not sure why.
* I'm pretty sure the buffering options hardcoded in lineup.py are probably too cautious and are introducing a lot of latency
* The path to the keyspipe.txt file is hardcoded in channel.py

### Requirements
1. HDHR Hardware
2. Some kind of HDMI capture setup (I'm using a LKV373A)
3. Windows machine with windows 10 that can run the HDHRView app and receive DRM'd channels. You probably can't use it for anything else, so do not use your primary computer.
4. Linux server (might be possible to run this on windows machine at your own risk), webserver running on port 80
5. node-ffmpeg-mpegts-proxy installed. I'm using a raspberry pi 3, which is probably overkill.

### Directions

#### Windows 10 Setup

1. Install Auto-hotkey and the official HDHR client from the Windows store.
2. Edit the keyreader.ahk file to point to a file somewhere you have shared on the network that you can access from your linux server.
3. Make sure the file exists (default is c:\users\<yourusername>\Documents\keyspipe.txt)
4. Start the script
5. Start the HDHR client and fullscreen it

#### Connections

1. Connect the HDMI output from your windows machine to your HDMI capture setup. You may need to do something about HDCP, but that is beyond the scope of this document.

#### Linux Setup

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

Follow the directions on https://blog.danman.eu/new-version-of-lenkeng-hdmi-over-ip-extender-lkv373a/ or https://www.yodeck.com/news/any-hdmi-device-asvideo-infor-yodeck/ to re-flash the firmware to stick it into unicast mode permanantly

Instead of the iptables command, you can recompile ffmpeg with this patch: https://github.com/danielkucera/FFmpeg/commit/3abb8bc887afd7c595669342978428fea22113ee but you're on your own if you try.

Once you've permantly forced the TX unit into unicast mode, you can (probably) safely plug it into your network without all the multicast stuff.

Configure a webserver (apache, nginx, whatever) that can serve static files on port 80. You'll need it later. For the purposes of my example the webroot is at /var/www/html, but it will vary depending on distro and server.


mount the directory with the keyspipe.txt file from the windows machine on your server. I recommend seting up autofs to make sure it always mounts. Make sure the file is writeable by the user you'll be running the proxy as. 

try doing:
```
echo '2{enter}' > /path/to/keyspipe.txt
```
and verify that the autohotkey script changes the channel on your windows machine to 2.


Install channel.py into /usr/local/bin, and edit it to reference the path to the keyspipe.txt file.

run 
```
curl http://ipv4-api.hdhomerun.com/discover > api.json
```
Look in api.json and find "DiscoverURL" and "LineupURL" and grab those *substituting your URLs*
If your HDHR had the IP 192.168.0.41, you'd do:
```
curl  "http://192.168.0.41:80/discover.json" > discover.json
curl  "http://192.168.0.41:80/lineup.json" > lineup.json
```

Now rebuild the json files for the proxy *substituting your proxy ip*:
```
./discover.py 192.168.0.41 discover.json discover-out.json
./lineup.py 192.168.0.41 lineup.json lineup-out.json sources-out.json
```
And copy them to /var/www/html (or wherever your webroot is):
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

You should now be able to log into your plex server's web console and go to Settings -> Server -> Live TV & DVR. Click Add Device. You will probably need to add your proxy manually by IP. Plex should see the proxy and let you add it. Follow the rest of the steps as normal.

Congratulations, you (hopefully) have Plex acting as a dvr against your proxy. 

