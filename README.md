# djtaytay
This is a little toy app made to explore Vue, brush up on my Python, and make a remote music collection accessable through a web interface. It has a rudimentary file browser. Additionally, it decodes files using `ffmpeg`, reencodes as webm vorbis and streams them to the browser.

This is an active work in progress. Notably, it needs better authentication, validation against the user input to ffmpeg, and better UI controls.

## How to set up a test environment
Prerequisites:
 * Linux (may work on OS X, untested)
 * Docker

Clone this repo, then
```
echo "export MUSIC_DIR=$YOUR_PATH_HERE" >> .env
echo "export SECRET_KEY=$(python -c 'import os; print(os.urandom(16))')" >> .env
echo "export ADMIN_PASSWORD='super secret password unicorn' >> .env"
./run.sh
```
and [click here](http://127.0.0.1:8000/); default username is `admin`, password is the `ADMIN_PASSWORD` variable above.

## Notes on production deployment
This service works by transcoding media files in memory and serving the content through an HTML5 `<audio>` tag. Some browsers will not even attempt to load most of the contents of a stream like this at once, instead opting to stream it in as needed. Long streams like this do not play nicely with Flask's debug webserver; it is highly recommended to run this behind a real WSGI server, like gunicorn. If you find that your streams are being served incompletely, set the `--timeout` value to a somewhat higher value, like 150 seconds.

Additionally, it is highly recommended to run this behind a real web server to buffer the data from the WSGI server to the client without keeping a WSGI worker busy all the time. Nginx has a similar configuration, `send_timeout`, that specifies how long a connection is allowed to stay idle before closing the connection. It is also recommended to increase this value to something higher, like 150 seconds as well.

Carefully consider these changes though; these configuration changes make a Denial of Service attack much easier to achieve, by creating a ton of very idle connections to the service. Even if you do not change your WSGI server's timeout and web server's client idle timeout, it is highly recommended to run this service with a real web server and WSGI server instead of the built-in debug server; it is much more performant, reliable, and handles large files much better.

## Todo
* add real users
* add nice playlist functionality
* handle failures better
* more style for this bad boy
