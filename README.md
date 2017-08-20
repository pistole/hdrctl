### What is this?

hdrctl is a proxy designed to swap out requests for DRM'd content with video output captured from a physical windows machine running the native HDHomeRunView application with changes to tuner channels done by emulating keystrokes on windows machine.

The longterm goal is for this setup to behave like a HDHR with one tuner to clients incapable of handling the DRM streams (plex, kodi, android tv channels, etc).

### What works?

* Autohotkey script that reads from a file and sends the commands to the HDHRView app running on Windows 10


