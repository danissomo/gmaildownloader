curl https://www.python.org/ftp/python/3.7.2/python-3.7.2.exe --output pythoninstaller.exe
.\pythoninstaller.exe
pause
python -m pip install --upgrade pip google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install Plyer
python .\main.py