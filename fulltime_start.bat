@echo off
:restart
echo Starting Python script...
python runlink.py

echo.
echo Python script ended or crashed. Waiting 5 seconds before restarting...
timeout /t 5 /nobreak >nul

goto restart