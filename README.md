# djtaytay
This is a little toy app made to explore Vue, brush up on my Python, and make a remote music collection accessable through a web interface. It has a rudimentary file browser. Additionally, it decodes files using `ffmpeg`, reencodes as webm vorbis and streams them to the browser.

This is an active work in progress. Notably, it does not handle large files well, needs better authentication, validation against the user input to ffmpeg, and better UI controls.

## How to set up a test environment
Clone this repo, then
```
apt install ffmpeg
virtualenv --python=python3 virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
export MUSIC_DIR=$YOUR_PATH_HERE
export SECRET_KEY="$(python -c 'import os; print(os.urandom(16))')"
export ADMIN_PASSWORD="super secret password unicorn"
python ./djtaytay.py
```
and [click here](http://127.0.0.1:5000/); default username is `admin`, password is the `ADMIN_PASSWORD` variable above.

## Todo
* add authentication
* add nice playlist functionality
* stick it in a docker file, with specific volumes mounted
* handle failures better
* actually style this bad boy
