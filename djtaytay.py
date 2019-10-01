import json
import os.path

from flask import Flask, request, Response, session, redirect, url_for
from flask import render_template, abort

from util import error, get_complete_path, directory_listing, transcode
from util import valid_login

app = Flask(__name__)
app.config.from_object(__name__)

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
def index():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('index.html.j2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template('login.html.j2')
    return render_template('login.html.j2')

# TODO: Handle failure cases; see if path is safe to try to transcode
@app.route('/play')
def stream_file():
    if 'authenticated' not in session:
        return abort(401)
    else:
        if not request.args['path']:
            err_msg = "Not a streamable path: {}".format(requests.args['path'])
            app.logger.warning(err_msg)
            return error(err_msg)

        # Validate path and construct an absolute path
        try:
            path = get_complete_path(request.args['path'], root)
        except Exception as e:
            app.logger.warning(str(e))
            return error(str(e))

        return Response(transcode(path), mimetype='audio/webm')


@app.route("/browse")
def file_listing():
    if 'authenticated' not in session:
        app.logger.warning("Unauthenticated file_listing() call")
        return error("It appears you've been logged out; please log back in.", 401)
    else:
        # Validate path and construct an absolute path
        try:
            path = get_complete_path(request.args.get("path", "/"), root)
        except Exception as e:
            app.logger.warning(str(e))
            return error(str(e))

        try:
            listing = json.dumps(directory_listing(path, root))
            return Response(listing, mimetype='application/json')
        except Exception as e:
            app.logger.error(str(e))
            return error(str(e))


if __name__ == '__main__':
    app.run(debug=True)
