@echo off
set url=%1
set download_path=%2
set extract_path=%3
set install_path=%4
echo starting download...
curl %url% --output %download_path%
echo extracting...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -Force -Path '%download_path%' -DestinationPath '%extract_path%'"
echo removing current installation...
rmdir /S /Q "%install_path%"
echo installing new version...
xcopy /e /h /i "%extract_path%" "%install_path%"
echo cleaning up...
rmdir /S /Q "%extract_path%"
del /s /q %download_path%
REM TODO: need shortcut creation?
start "" "%install_path%\main\main.exe"
pause
