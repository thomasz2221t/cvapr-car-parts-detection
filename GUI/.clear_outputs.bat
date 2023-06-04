@echo off
:: Deletes all content of ./runs/ folder and any .pt files in GUI/ directory

IF EXIST *.pt ( del *.pt )
cd runs
for /F "delims=" %%i in ('dir /b') do (rmdir "%%i" /s/q || del "%%i" /s/q)
echo Cleared!
pause