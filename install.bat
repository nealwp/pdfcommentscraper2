REM set url=%1
REM set download_path=%userprofile%\AppData\Local\Temp\disabilitydude.zip
REM set extract_path=%userprofile%\AppData\Local\Temp
REM set install_path=%userprofile%\AppData\Local
REM taskkill /f /im disabilitydude.exe
REM echo starting download...
REM curl %url% --output %download_path%
REM echo extracting...
REM powershell -Command "Expand-Archive -Path '%download_path%' -DestinationPath '%extract_path%'"
REM REM echo removing current installation...Y
REM rmdir /s /q %install_path%\disabilitydude 
REM mkdir %install_path%\disabilitydude
REM xcopy /e /i /q %extract_path%\disabilitydude %install_path%\disabilitydude
REM echo installing new version...
REM REM echo cleaning up...
REM rmdir /s /q %extract_path%\disabilitydude
REM del /s /q %download_path%
REM REM TODO: need shortcut creation?
REM start "" %install_path%\disabilitydude\disabilitydude.exe