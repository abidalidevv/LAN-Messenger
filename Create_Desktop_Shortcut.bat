@echo off
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
set TARGET="%~dp0LANMessenger.exe"
set SHORTCUT="%USERPROFILE%\Desktop\LAN Messenger.lnk"
set ICON="%~dp0assets\app_icon.ico"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%SHORTCUT%" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %TARGET% >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "LAN Messenger - Local Fast Chat & File Share" >> %SCRIPT%
echo oLink.IconLocation = %ICON% >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo [DONE] Desktop Shortcut created successfully on your Desktop!
pause

