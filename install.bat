set url=%1
set download_path=%userprofile%\AppData\Local\Temp\disabilitydude.zip
set extract_path=%userprofile%\AppData\Local\Temp
set install_path=%userprofile%\AppData\Local
taskkill /f /im disabilitydude.exe
echo starting download...
curl %url% --output %download_path%
echo extracting...
powershell -Command "Expand-Archive -Path '%download_path%' -DestinationPath '%extract_path%'"
REM echo removing current installation...Y
rmdir /s /q %install_path%\disabilitydude 
mkdir %install_path%\disabilitydude
xcopy /e /i /q %extract_path%\disabilitydude %install_path%\disabilitydude
echo installing new version...
REM echo cleaning up...
rmdir /s /q %extract_path%\disabilitydude
del /s /q %download_path%
REM TODO: need shortcut creation?
start "" %install_path%\disabilitydude\disabilitydude.exe