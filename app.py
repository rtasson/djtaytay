import json
import os.path

from flask import Flask, request, Response

from util import error, get_complete_path, directory_listing, transcode

app = Flask(__name__)

try:
    root = os.path.abspath(os.environ['MUSIC_DIR'])
except:
    print("Must specify a MUSIC_DIR environment variable.")
    exit(1)

# TODO: Handle failure cases; see if path is safe to try to transcode
@app.route('/play')
def stream_file():
    if not request.args['path']:
        err_msg = "Not a streamable path: {}".format(requests.args['path'])
        return error(err_msg)

    # Validate path and construct an absolute path
    try:
        path = get_complete_path(request.args['path'], root)
    except Exception as e:
        return error(str(e))

    return Response(transcode(path), mimetype='audio/webm')


@app.route("/browse")
def file_listing():
    # Validate path and construct an absolute path
    try:
        path = get_complete_path(request.args.get("path", "/"), root)
    except Exception as e:
        return error(str(e))

    try:
        listing = json.dumps(directory_listing(path))
        return Response(listing, mimetype='application/json')
    except Exception as e:
        return error(str(e))


if __name__ == '__main__':
    app.run(debug=True)
