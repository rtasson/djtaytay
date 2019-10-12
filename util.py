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
import ffmpeg
import os.path

from pathlib import Path
from functools import wraps
from tinytag import TinyTag
from dotenv import load_dotenv
from typing import List, Dict, Any
from flask import abort, session, Response

load_dotenv()

try:
    admin_password = os.environ['ADMIN_PASSWORD']
except:
    print("Must specify an ADMIN_PASSWORD environment variable.")
    exit(1)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if 'authenticated' not in session:
               abort(401)
            return f(*args, **kwargs)
    return decorated_function

def error(message: str, code: int = 400) -> Response:
    """

    Helper function to print to stdout and return `message` in
    a JSON blob in a Flask Response.

    """
    # TODO: use Flask's logging
    response = json.dumps({"error": message})
    return Response(response, code, mimetype='application/json')

def get_complete_path(path: str, root: str) -> str:
    """

    This function generates an absolute path from the base directory
    and the provided path and validates that it is within the base
    directory. It returns the complete path as a string if successful
    and raises a ValueError if unsuccessful.

    """
    raw_path = root + "/" + path.lstrip('/')
    real_path = str(Path(raw_path).resolve())

    # if the computed path is not in the root path...
    if os.path.commonpath([real_path, root]) != root:
        err_msg = "Path {} is not in {}".format(path, root)
        ex = ValueError(err_msg)
        raise ex

    return real_path

# TODO: Flask's type annotations for the Response object don't include
# the Generator type, but that's what this function is; dig into this.
def transcode(path: str):
    """

    This function is a generator. It will asyncronously begin transcoding
    the file at `path` to its stdout and then yield the contents
    of the pipe 128 bytes at a time. If there is nothing to read,
    the transcoder is checked to see if it has exited, and if it has
    the function returns.

    """
    process = (
        ffmpeg
            .input(path)
            .output('pipe:', format='webm', acodec='libvorbis', aq='6')
            .run_async(pipe_stdout=True)
    )
    while True:
        data = process.stdout.read(128)
        if not data:
            process.poll()
            if process.returncode == None:
                continue
            elif process.returncode != 0:
                # TODO: Do something better here :(
                return
            else:
                break
        yield data
    process.communicate()

def directory_listing(path: str, root: str) -> List[Dict[str, str]]:
    """

    This function constructs a dict representing a directory's
    contents and returns it. If the path is not a directory,
    a ValueError is raised.

    """
    if not os.path.isdir(path):
        ex = ValueError("Not a directory: {}".format(path))
        raise ex

    listing = [
      {
        "name": "..",
        "path": os.path.dirname(path)[len(root):],
        "type": "dir"
      }
    ]

    # TODO: omit hidden files
    for i in os.scandir(path=path):
        type = "file" if i.is_file() else "dir"
        file = {
            "name": i.name,
            "path": i.path[len(root):],
            "type": type
        }
        listing.append(file)
    return listing

def valid_login(username: str, password: str) -> bool:
    if username == "admin" and password == admin_password:
        return True
    else:
        return False

def get_metadata(file: str) -> Dict[str, Any]:
    f = TinyTag.get(file)
    if f == None:
        raise ValueError("Could not decode media")
    result = {"artist": f.artist, "album": f.album, "title": f.title}
    return result
