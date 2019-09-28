import os
import sys
import json
import ffmpeg
import os.path
import tempfile

from flask import Flask, request, Response, stream_with_context

from util import error, get_parent_path, get_complete_path

app = Flask(__name__)

# TODO: Handle failure cases; see if path is safe to try to transcode
@app.route('/play')
def stream_file():
    if not request.args['path']:
        err_msg = "Not a streamable path: {}".format(requests.args['path'])
        print(err_msg)
        return error(err_msg)
    path = get_complete_path(request.args['path'], root)
    def generate():
        handle, tmp = tempfile.mkstemp(prefix='djtaytay')
        os.close(handle)
        process = (
            ffmpeg
                .input(path)
                .output(tmp, format='webm', acodec='libvorbis', ac=1, ar='196k')
                .overwrite_output()
                .run_async()
        )
        file = open(tmp, mode='rb')
        while True:
            data = file.read(128)
            if not data:
                process.poll()
                if process.returncode == None:
                    continue
                else:
                    file.close()
                    os.remove(tmp)
                    break
            yield data
            
    return Response(stream_with_context(generate()), mimetype='audio/webm')

@app.route("/browse")
def file_listing():
    path = get_complete_path(request.args.get("path", "/"), root)
    try:
        # if the computed path is not in the root path...
        if os.path.commonpath([path, root]) != root:
            err_msg = "Path {} is not in {}".format(path, root)
            print(err_msg)
            return error(err_msg)
    except:
        # if paths contains both absolute and relative paths
        err_msg = "Set MUSIC_DIR to an absolute path."
        print(err_msg)
        return error(err_msg)
    if not os.path.isdir(path):
        err_msg = "Not a directory: {}".format(path)
        print(err_msg)
        return error(err_msg)
    listing = [
      {
        "name": "..",
        "path": get_parent_path(path)[len(root):],
        "type": "dir"
      }
    ]
    try:
        # TODO: omit hidden files
        for i in os.scandir(path=path):
            type = "file" if i.is_file() else "dir"
            file = {
                "name": i.name,
                "path": i.path[len(root):],
                "type": type
            }
            listing.append(file)
        return json.dumps(listing)
    except Exception as e:
        return json.dumps({"error": "Unknown error"}), 400

if __name__ == '__main__':
    if not os.environ.get('MUSIC_DIR'):
        print("Must specify a MUSIC_DIR environment variable.")
        exit(1)
    global root
    root = os.environ.get('MUSIC_DIR').rstrip('/')
    app.run(debug=True)
