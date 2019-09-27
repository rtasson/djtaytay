import os
import sys
import json
import ffmpeg
import tempfile

from flask import Flask, request, Response, stream_with_context
from flask_restful import Resource, Api

from util import error, get_parent_path

app = Flask(__name__)
api = Api(app, prefix="/api/v1")

# TODO: Handle failure cases; see if path is safe to try to transcode
@app.route('/play')
def stream_file():
    def generate():
        handle, tmp = tempfile.mkstemp(prefix='djtaytay')
        os.close(handle)
        process = (
            ffmpeg
                .input(request.args['path'])
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


class FileListing(Resource):
    def get(self):
        if not os.path.isdir(request.args['path']):
            return error("Not a directory")
        listing = [
          {
            "name": "..", 
            "path": get_parent_path(request.args['path']),
            "type": "dir"
          }
        ]
        try:
            # TODO: omit hidden files
            for i in os.scandir(path=request.args['path']):
                type = "file" if i.is_file() else "dir"
                file = {
                    "name": i.name,
                    "path": i.path,
                    "type": type
                }
                listing.append(file)
            return json.dumps(listing)
        except Exception as e:
            return json.dumps({"error": "Unknown error"}), 400

api.add_resource(FileListing, '/browse')

if __name__ == '__main__':
    app.run(debug=True)
