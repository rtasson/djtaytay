import json
import ffmpeg
import os.path

from pathlib import Path
from flask import Response

try:
    admin_password = os.environ['ADMIN_PASSWORD']
except:
    print("Must specify an ADMIN_PASSWORD environment variable.")
    exit(1)

def error(message, code=400):
    """error(message)

    Helper function to print to stdout and return `message` in
    a JSON blob in a Flask Response.

    """
    # TODO: use Flask's logging
    response = json.dumps({"error": message})
    return Response(response, code, mimetype='application/json')

def get_complete_path(path, root):
    """get_complete_path(path, root)

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
        ex = ValueError()
        ex.strerror = err_msg
        raise ex

    return real_path

def transcode(path):
    """transcode(path)

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

def directory_listing(path, root):
    """directory_listing(path, root)

    This function constructs a dict representing a directory's
    contents and returns it. If the path is not a directory,
    a ValueError is raised.

    """
    if not os.path.isdir(path):
        ex = ValueError()
        ex.strerror = "Not a directory: {}".format(path)
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

def valid_login(username, password):
    if username == "admin" and password == admin_password:
        return True
    else:
        return False
