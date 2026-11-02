@echo off
echo ===================================================
echo Adding Windows Firewall Rules for LAN Messenger...
echo ===================================================

netsh advfirewall firewall delete rule name="LANMessenger_TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="LANMessenger_UDP" >nul 2>&1

netsh advfirewall firewall add rule name="LANMessenger_TCP" dir=in action=allow protocol=TCP localport=9876
netsh advfirewall firewall add rule name="LANMessenger_UDP" dir=in action=allow protocol=UDP localport=9877

echo.
echo [DONE] Firewall rules added successfully for port 9876 (TCP) and 9877 (UDP)!
pause

