'''
Copyright 2019 Ryan Tasson <rjt@lowhangingfru.it>

This file is part of djtaytay.

djtaytay is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

djtaytay is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with djtaytay.  If not, see <https://www.gnu.org/licenses/>.
'''

import json
import flask
import os.path
import werkzeug

from typing import Union
from dotenv import load_dotenv

from flask import Flask, request, Response, session, redirect, url_for
from flask import render_template, abort

from util import error, get_complete_path, directory_listing, transcode
from util import valid_login, get_metadata, login_required

app = Flask(__name__)
app.config.from_object(__name__)
app.config['APPLICATION_ROOT'] = os.getenv('APPLICATION_ROOT', '')
load_dotenv()

try:
    root = os.path.abspath(os.environ['MUSIC_DIR'])
except:
    print("Must specify a MUSIC_DIR environment variable.")
    exit(1)

# Session setup
PREMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds
try:
    app.secret_key = os.environ['SECRET_KEY']
except:
    print("Must specify a SECRET_KEY environment variable.")
    exit(1)

@app.route('/')
def index() -> Union[werkzeug.wrappers.Response, flask.wrappers.Response]:
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    else:
        return Response(render_template('index.html.j2'))

@app.route('/login', methods=['GET', 'POST'])
def login() ->  Union[werkzeug.wrappers.Response, flask.wrappers.Response]:
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['authenticated'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return Response(render_template('login.html.j2'))

# TODO: Handle failure cases; see if path is safe to try to transcode
@app.route('/play')
@login_required
def stream_file() -> Response:
    if not request.args['path']:
        log_msg = "Not a streamable path: {}".format(request.args['path'])
        app.logger.warning(log_msg)
        return error("Could not stream")

    # Validate path and construct an absolute path
    try:
        path = get_complete_path(request.args['path'], root)
    except Exception as e:
        log_msg = "Error in get_complete_path: {}".format(str(e))
        app.logger.warning(log_msg)
        return error("Could not stream")

    return Response(transcode(path), mimetype='audio/webm')


@app.route("/browse")
@login_required
def file_listing() -> Response:
    # Validate path and construct an absolute path
    try:
        path = get_complete_path(request.args.get("path", "/"), root)
    except Exception as e:
        msg = "Error in get_complete_path: {}".format(str(e))
        app.logger.warning(msg)
        return error("Could not browse")

    try:
        listing = json.dumps(directory_listing(path, root))
        return Response(listing, mimetype='application/json')
    except Exception as e:
        msg = "Error in directory_listing: {}".format(str(e))
        app.logger.error(msg)
        msg = "path: {}, root: {}".format(path, root)
        app.logger.error(msg)
        return error("Could not browse")

@app.route("/metadata")
@login_required
def metadata() -> Response:
    # Validate path and construct an absolute path
    try:
        path = get_complete_path(request.args.get("path", "/"), root)
    except Exception as e:
        msg = "Error in get_complete_path: {}".format(str(e))
        app.logger.warning(msg)
        return error("Could not browse")

    try:
        result = json.dumps(get_metadata(path))
        return Response(result, mimetype='application/json')
    except Exception as e:
        msg = "Error getting metadata: {}".format(str(e))
        app.logger.error(msg)
        return error("Could not retrieve metadata")

if __name__ == '__main__':
    if os.getenv('DEBUG', False) == 'True':
        debug = True
    else:
        debug = False
    app.run(debug=debug)
