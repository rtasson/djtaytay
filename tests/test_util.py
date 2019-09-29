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
    '''
    This test case exercises the get_complete_path() function,
    which is both responsible for resolving the complete path of
    a file relative to the configured root directory, as well as
    validating that it hasn't escaped the root directory. The
    fixtures below generate a file tree like so:

    ```
    parent_dir/
    ├── bad
    └── root
        ├── good
        └── symlink_to_bad -> ../bad
    ```

    `root` represents the configured `MUSIC_DIR`. We expect
    get_complete_path() to access `parent_dir/root/good` fine,
    but to raise an exception while attempting to access both
    `bad` and `symlink_to_bad`.
    '''

    @classmethod
    def setUpClass(self):
        self.parent_dir = tempfile.mkdtemp()
        self.root_dir = tempfile.mkdtemp(dir=self.parent_dir)
        self.good_file_handle, self.good_file_abs_path = tempfile.mkstemp(dir=self.root_dir)
        self.good_file_name = os.path.basename(self.good_file_abs_path)
        self.bad_file_handle, self.bad_file_abs_path = tempfile.mkstemp(dir=self.parent_dir)
        self.bad_file_name = os.path.basename(self.bad_file_abs_path)
        self.symlink_to_bad_name = "symlink_to_bad"
        self.symlink_to_bad_path = self.root_dir + "/symlink_to_bad"
        os.symlink(self.bad_file_abs_path, self.symlink_to_bad_path)

    @classmethod
    def tearDownClass(self):
        os.close(self.good_file_handle)
        os.remove(self.good_file_abs_path)
        os.remove(self.symlink_to_bad_path)
        os.rmdir(self.root_dir)
        os.close(self.bad_file_handle)
        os.remove(self.bad_file_abs_path)
        os.rmdir(self.parent_dir)

    # Test that the function can reconstruct complete paths
    def test_valid_complete_path(self):
        self.assertEqual(
            util.get_complete_path(self.good_file_name, self.root_dir),
            self.good_file_abs_path
        )

    # Test that the function raises an exception when the computed
    # path is outside the "root" path due to a relative file name
    def test_root_relative_escape(self):
        with self.assertRaises(ValueError):
            util.get_complete_path(
                "../" + self.bad_file_name,
                self.root_dir
            )

    # Test that the function raises an exception when the computed
    # path is outside the "root" path due to a symlink
    def test_root_symlink_escape(self):
        with self.assertRaises(ValueError):
            util.get_complete_path(
                self.symlink_to_bad_name,
                self.root_dir
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
