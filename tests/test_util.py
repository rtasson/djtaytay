import os
import json
import tempfile
import unittest
import contextlib

from flask import Response

import util

class TestErrorFunction(unittest.TestCase):
    test_string = "test"

    def test_error_json_response(self):
        # Test that error(msg) returns a JSON blob
        # with "error" key set
        with open('/dev/null', 'w') as f:
            with contextlib.redirect_stdout(f):
                self.assertEqual(
                    json.loads(util.error(self.test_string).get_data())["error"],
                    self.test_string
                )

    def test_error_status_code(self):
        # Test that error(msg) returns a 400 error code
        # unclear if we should actually test on this, but
        # for now this is the contract
        with open('/dev/null', 'w') as f:
            with contextlib.redirect_stdout(f):
                self.assertEqual(
                    util.error(self.test_string).status_code,
                    400
                )

class TestGetCompletePathFunction(unittest.TestCase):
    _temp_dir = None
    temp_file_name = None
    temp_file_handle = None
    temp_file_abs_path = None

    @classmethod
    def setUpClass(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_handle, self.temp_file_abs_path = tempfile.mkstemp(dir=self.temp_dir)
        self.temp_file_name = os.path.basename(self.temp_file_abs_path)

    @classmethod
    def tearDownClass(self):
        os.close(self.temp_file_handle)
        os.remove(self.temp_file_abs_path)
        os.rmdir(self.temp_dir)

    # Test that the function can reconstruct complete paths
    def test_valid_complete_path(self):
        self.assertEqual(
            util.get_complete_path(self.temp_file_name, self.temp_dir),
            self.temp_file_abs_path
        )

    # Test that the function raises an exception when the computed
    # path is outside the "root" path
    def test_root_escape(self):
        with self.assertRaises(ValueError):
            util.get_complete_path(
                "../" + self.temp_file_name,
                self.temp_dir
            )

'''
class TestTranscodeFunctions(unittest.TestCase):
    # Test that transcode() cleans up after itself.
    # This testcase will fail if there are currently
    # files in the temp directory with our static
    # prefix, 'djtaytay' - ie, if tracks are currently
    # being transcoded or were previously abandoned.
    def test_transcode_cleanup(self):
        # Currently looking for a properly-licensed clip
'''

if __name__ == '__main__':
    unittest.main()
