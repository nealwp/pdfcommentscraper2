set url=%1
set download_path=%userprofile%\AppData\Local\Temp\disabilitydude.zip
set extract_path=%userprofile%\AppData\Local\Temp\
set install_path=%userprofile%\AppData\Local\disabilitydude
taskkill /f /im disabilitydude.exe
echo starting download...
curl %url% --output %download_path%
echo extracting...
powershell -Command "Expand-Archive -Force -Path '%download_path%' -DestinationPath '%extract_path%'"
echo removing current installation...
rmdir /s /q %install_path% 
echo installing new version...
powershell -Command "Move-Item -Force -Path '%extract_path%\disabilitydude' -Destination '%install_path%'"
echo cleaning up...
rem rmdir /S /Q "%extract_path%"
rem del /s /q %download_path%
REM TODO: need shortcut creation?
start "" %install_path%\disabilitydude.exe