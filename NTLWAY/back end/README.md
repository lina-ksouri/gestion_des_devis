# Backend 


This repo is functionality complete — PR's and issues welcome!

## Installation ( On Linux )

1. Clone this repository
```bash
git clone <url> 
```

2. Install Python Requirements
```bash
pip install -r requirements.txt
```

## Installation ( On Windows )

to launch the app on windows, we need to install some additional tools ( weasyprint library cannot works on windows unless we install them )

1. Download and Install python 3 ( 64bit ) from this website : https://www.python.org/downloads/release/python-392/

    Or just click [here](https://www.python.org/ftp/python/3.9.2/python-3.9.2-amd64.exe )

2. Download and Install the GTK runtime for windows with this link 
 https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

    Or just click [here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2021-01-30/gtk2-runtime-2.24.33-2021-01-30-ts-win64.exe)

## Launch Application

to launch the application, if everything is ok it will start the web server on localhost:8000

```bash
python manage.py runserver

Watching for file changes with StatReloader
Performing system checks...

System check identified some issues:


System check identified 1 issue (0 silenced).
November 29, 2020 - 19:44:47
Django version 3.1.3, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Notes

for the admin dashboard, go to http://localhost:8000/admin

credentials:
username: admin
password: rootroot


## NB :
for more information you can visit https://www.djangoproject.com/start/
