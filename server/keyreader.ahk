#persistent

lastFileContent := ""
setTimer, checkFile, 20
return

; adapted from https://stackoverflow.com/a/30598600/89548

checkFile:
    ; may not work if the user documents directory has moved
    fileread newFileContent, %userprofile%\documents\keyspipe.txt
    if(newFileContent != lastFileContent) {
        lastFileContent := newFileContent
        if (newFileContent != "") {
            ; this is super dangerous
            SendInput %newFileContent%
        }
    }
return

