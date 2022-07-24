set url=%1
set download_path=%userprofile%\AppData\Local\Temp\disabilitydude.zip
set extract_path=%userprofile%\AppData\Local\Temp\disabilitydude
set install_path=%userprofile%\AppData\Local\disabilitydude
echo starting download...
curl %url% --output %download_path%
echo extracting...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Force -Path '%download_path%' -DestinationPath '%extract_path%'"
echo removing current installation...
rmdir /S /Q "%install_path%"
echo installing new version...
xcopy /e /h /i "%extract_path%" "%install_path%"
echo cleaning up...
rem rmdir /S /Q "%extract_path%"
rem del /s /q %download_path%
REM TODO: need shortcut creation?
start "" %install_path%\main\main.exe
