@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (echo Run as Administrator & pause & exit /b 1)
set LOG=%~dp0logs\maintenance_%date:~-4%%date:~3,2%%date:~0,2%.txt
if not exist "%~dp0logs" mkdir "%~dp0logs"
echo Maintenance started %date% %time% > "%LOG%"
echo [1/6] Cleaning TEMP...
del /q /f /s "%TEMP%\*" 2>>"%LOG%"
echo [2/6] Cleaning Windows Temp...
del /q /f /s "C:\Windows\Temp\*" 2>>"%LOG%"
echo [3/6] Emptying Recycle Bin...
powershell -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
echo [4/6] Flushing DNS...
ipconfig /flushdns >> "%LOG%"
echo [5/6] Resetting Winsock...
netsh winsock reset >> "%LOG%"
echo [6/6] Running SFC...
sfc /scannow >> "%LOG%"
echo Done! Log: %LOG%
pause
