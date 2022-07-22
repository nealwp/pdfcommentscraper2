@echo off
set url=%1
set download_path=%2
set extract_path=%3
set install_path=%4
curl %url% --output %download_path%
powershell -Command "Expand-Archive -Force -Path '%download_path%' -DestinationPath '%extract_path%'"
del /s /q %download_path%
rmdir /S /Q "%install_path%"
xcopy /e /h /i /q "%extract_path%" "%install_path%"
rmdir /S /Q "%extract_path%"
REM TODO: need shortcut creation?
start "" "%install_path%\main\main.exe"
