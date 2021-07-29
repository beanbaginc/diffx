"""Unit tests for pydiffx.reader."""

from __future__ import unicode_literals

import io

from pydiffx.errors import DiffXParseError
from pydiffx.reader import DiffXReader
from pydiffx.sections import Section
from pydiffx.tests.testcases import TestCase


class DiffXReaderTests(TestCase):
    """Unit tests for pydiffx.reader.DiffXReader."""

    def test_with_simple_diff(self):
        """Testing DiffXReader with simple diff"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=82\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "message2.py",\n'
            b'        "old": "message.py"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=692\n'
            b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
            b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
            b'@@ -164,10 +164,10 @@\n'
            b'             not isinstance(headers, MultiValueDict)):\n'
            b'             # Instantiating a MultiValueDict from a dict does '
            b'not ensure that\n'
            b'             # values are lists, so we have to ensure that '
            b'ourselves.\n'
            b'-            headers = MultiValueDict(dict(\n'
            b'-                (key, [value])\n'
            b'-                for key, value in six.iteritems(headers)\n'
            b'-            ))\n'
            b'+            headers = MultiValueDict({\n'
            b'+                key: [value]\n'
            b'+                for key, value in headers.items()\n'
            b'+            })\n'
            b'\n'
            b'         if in_reply_to:\n'
            b'             headers["In-Reply-To"] = in_reply_to\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 82,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 692,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
                    b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
                    b'@@ -164,10 +164,10 @@\n'
                    b'             not isinstance(headers, MultiValueDict)):\n'
                    b'             # Instantiating a MultiValueDict from a '
                    b'dict does not ensure that\n'
                    b'             # values are lists, so we have to ensure '
                    b'that ourselves.\n'
                    b'-            headers = MultiValueDict(dict(\n'
                    b'-                (key, [value])\n'
                    b'-                for key, value in six.iteritems('
                    b'headers)\n'
                    b'-            ))\n'
                    b'+            headers = MultiValueDict({\n'
                    b'+                key: [value]\n'
                    b'+                for key, value in headers.items()\n'
                    b'+            })\n'
                    b'\n'
                    b'         if in_reply_to:\n'
                    b'             headers["In-Reply-To"] = in_reply_to\n'
                ),
                'type': 'diff',
            },
        ])

    def test_with_multi_commit_diff(self):
        """Testing DiffXReader with multi-commit diff"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=49, mimetype=text/markdown\n'
            b'    Summary of the _first_ commit in the series.\n'
            b'#..meta: format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T13:12:06-07:00",\n'
            b'    "date": "2021-06-01T19:26:31-07:00",\n'
            b'    "id": "a25e7b28af5e3184946068f432122c68c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: format=json, length=166\n'
            b'{\n'
            b'    "path": "file1",\n'
            b'    "revision": {\n'
            b'        "new": "eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef",\n'
            b'        "old": "c8839177d1a5605aa60abe69db95c84183f0eebe"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=60\n'
            b'--- /file1\n'
            b'+++ /file1\n'
            b'@@ -498,7 +498,7 @@\n'
            b' ... diff content\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=52\n'
            b'    Summary of commit #2\n'
            b'\n'
            b'    Here\'s a description.\n'
            b'#..meta: format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T19:46:25-07:00",\n'
            b'    "date": "2021-06-01T19:46:22-07:00",\n'
            b'    "id": "91127b687f583184144161f432222748c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: format=json, length=166\n'
            b'{\n'
            b'    "path": "file2",\n'
            b'    "revision": {\n'
            b'        "new": "a2ccb0cb48383472345d41a32afde39a7e6a72dd",\n'
            b'        "old": "1b7af7f97076effed5db722afe31c993e6adbc78"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=80\n'
            b'--- a/file2\n'
            b'+++ b/file2\n'
            b'@@ -66,7 +66,8 @@\n'
            b' ... diff content for commit 2, file2\n'
            b'#..file:\n'
            b'#...meta: format=json, length=166\n'
            b'{\n'
            b'    "path": "file3",\n'
            b'    "revision": {\n'
            b'        "new": "0d4a0fb8d62b762a26e13591d06d93d79d61102f",\n'
            b'        "old": "be089b7197974703c83682088a068bef3422c6c2"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=82\n'
            b'--- a/file3\n'
            b'+++ b/file3\n'
            b'@@ -258,7 +258,8 @@\n'
            b' ... diff content for commit 2, file3\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {
                    'indent': 4,
                    'length': 49,
                    'mimetype': 'text/markdown',
                },
                'section': Section.CHANGE_PREAMBLE,
                'text': 'Summary of the _first_ commit in the series.\n',
                'type': 'preamble',
            },
            {
                'level': 2,
                'line': 4,
                'metadata': {
                    'author': 'Test User <test@example.com>',
                    'committer': 'Test User <test@example.com>',
                    'committer date': '2021-06-02T13:12:06-07:00',
                    'date': '2021-06-01T19:26:31-07:00',
                    'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
                },
                'options': {
                    'format': 'json',
                    'length': 244,
                },
                'section': Section.CHANGE_META,
                'type': 'meta',
            },
            {
                'level': 2,
                'line': 12,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 13,
                'metadata': {
                    'path': 'file1',
                    'revision': {
                        'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
                        'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 166,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 21,
                'options': {
                    'length': 60,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- /file1\n'
                    b'+++ /file1\n'
                    b'@@ -498,7 +498,7 @@\n'
                    b' ... diff content\n'
                ),
                'type': 'diff',
            },
            {
                'level': 1,
                'line': 26,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 27,
                'options': {
                    'indent': 4,
                    'length': 52,
                },
                'section': Section.CHANGE_PREAMBLE,
                'text': (
                    "Summary of commit #2\n"
                    "\n"
                    "Here's a description.\n"
                ),
                'type': 'preamble',
            },
            {
                'level': 2,
                'line': 31,
                'metadata': {
                    'author': 'Test User <test@example.com>',
                    'committer': 'Test User <test@example.com>',
                    'committer date': '2021-06-02T19:46:25-07:00',
                    'date': '2021-06-01T19:46:22-07:00',
                    'id': '91127b687f583184144161f432222748c1a30b23',
                },
                'options': {
                    'format': 'json',
                    'length': 244,
                },
                'section': Section.CHANGE_META,
                'type': 'meta',
            },
            {
                'level': 2,
                'line': 39,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 40,
                'metadata': {
                    'path': 'file2',
                    'revision': {
                        'new': 'a2ccb0cb48383472345d41a32afde39a7e6a72dd',
                        'old': '1b7af7f97076effed5db722afe31c993e6adbc78',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 166,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 48,
                'options': {
                    'length': 80,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- a/file2\n'
                    b'+++ b/file2\n'
                    b'@@ -66,7 +66,8 @@\n'
                    b' ... diff content for commit 2, file2\n'
                ),
                'type': 'diff',
            },
            {
                'level': 2,
                'line': 53,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 54,
                'metadata': {
                    'path': 'file3',
                    'revision': {
                        'new': '0d4a0fb8d62b762a26e13591d06d93d79d61102f',
                        'old': 'be089b7197974703c83682088a068bef3422c6c2',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 166,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 62,
                'options': {
                    'length': 82,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- a/file3\n'
                    b'+++ b/file3\n'
                    b'@@ -258,7 +258,8 @@\n'
                    b' ... diff content for commit 2, file3\n'
                ),
                'type': 'diff',
            },
        ])

    def test_with_newlines_file_lf_content_crlf(self):
        """Testing DiffXReader with file containing LF newlines and content
        containing CRLF newlines
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=88\n'
            b'{\r\n'
            b'    "path": {\r\n'
            b'        "new": "message2.py",\r\n'
            b'        "old": "message.py"\r\n'
            b'    }\r\n'
            b'}\r\n'
            b'#...diff: length=712\n'
            b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\r\n'
            b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\r\n'
            b'@@ -164,10 +164,10 @@\r\n'
            b'             not isinstance(headers, MultiValueDict)):\r\n'
            b'             # Instantiating a MultiValueDict from a dict does '
            b'not ensure that\r\n'
            b'             # values are lists, so we have to ensure that '
            b'ourselves.\r\n'
            b'-            headers = MultiValueDict(dict(\r\n'
            b'-                (key, [value])\r\n'
            b'-                for key, value in six.iteritems(headers)\r\n'
            b'-            ))\r\n'
            b'+            headers = MultiValueDict({\r\n'
            b'+                key: [value]\r\n'
            b'+                for key, value in headers.items()\r\n'
            b'+            })\r\n'
            b'\r\n'
            b'         if in_reply_to:\r\n'
            b'             headers["In-Reply-To"] = in_reply_to\r\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 88,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 712,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\r\n'
                    b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\r\n'
                    b'@@ -164,10 +164,10 @@\r\n'
                    b'             not isinstance(headers, MultiValueDict)):'
                    b'\r\n'
                    b'             # Instantiating a MultiValueDict from a '
                    b'dict does not ensure that\r\n'
                    b'             # values are lists, so we have to ensure '
                    b'that ourselves.\r\n'
                    b'-            headers = MultiValueDict(dict(\r\n'
                    b'-                (key, [value])\r\n'
                    b'-                for key, value in six.iteritems('
                    b'headers)\r\n'
                    b'-            ))\r\n'
                    b'+            headers = MultiValueDict({\r\n'
                    b'+                key: [value]\r\n'
                    b'+                for key, value in headers.items()\r\n'
                    b'+            })\r\n'
                    b'\r\n'
                    b'         if in_reply_to:\r\n'
                    b'             headers["In-Reply-To"] = in_reply_to\r\n'
                ),
                'type': 'diff',
            },
        ])

    def test_with_newlines_file_crlf_content_lf(self):
        """Testing DiffXReader with file containing CRLF newlines and content
        containing LF newlines
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\r\n'
            b'#.change:\r\n'
            b'#..file:\r\n'
            b'#...meta: format=json, length=82\r\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "message2.py",\n'
            b'        "old": "message.py"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=692\r\n'
            b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
            b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
            b'@@ -164,10 +164,10 @@\n'
            b'             not isinstance(headers, MultiValueDict)):\n'
            b'             # Instantiating a MultiValueDict from a dict does '
            b'not ensure that\n'
            b'             # values are lists, so we have to ensure that '
            b'ourselves.\n'
            b'-            headers = MultiValueDict(dict(\n'
            b'-                (key, [value])\n'
            b'-                for key, value in six.iteritems(headers)\n'
            b'-            ))\n'
            b'+            headers = MultiValueDict({\n'
            b'+                key: [value]\n'
            b'+                for key, value in headers.items()\n'
            b'+            })\n'
            b'\n'
            b'         if in_reply_to:\n'
            b'             headers["In-Reply-To"] = in_reply_to\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 82,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 692,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
                    b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
                    b'@@ -164,10 +164,10 @@\n'
                    b'             not isinstance(headers, MultiValueDict)):\n'
                    b'             # Instantiating a MultiValueDict from a '
                    b'dict does not ensure that\n'
                    b'             # values are lists, so we have to ensure '
                    b'that ourselves.\n'
                    b'-            headers = MultiValueDict(dict(\n'
                    b'-                (key, [value])\n'
                    b'-                for key, value in six.iteritems('
                    b'headers)\n'
                    b'-            ))\n'
                    b'+            headers = MultiValueDict({\n'
                    b'+                key: [value]\n'
                    b'+                for key, value in headers.items()\n'
                    b'+            })\n'
                    b'\n'
                    b'         if in_reply_to:\n'
                    b'             headers["In-Reply-To"] = in_reply_to\n'
                ),
                'type': 'diff',
            },
        ])

    def test_with_content_line_endings_option_dos(self):
        """Testing DiffXReader with content section specifying line_endings=dos
        """
        # We're going to have some lines that use \n instead of \r\n in this
        # test, at the start and end of the diff. We'll then figure out if
        # we split it right based on the next section's starting line number.
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=88\n'
            b'{\r\n'
            b'    "path": {\r\n'
            b'        "new": "message2.py",\r\n'
            b'        "old": "message.py"\r\n'
            b'    }\r\n'
            b'}\r\n'
            b'#...diff: length=97, line_endings=dos\n'
            b' line 1\n'
            b' still line 1\r\n'
            b' here is line 2\r\n'
            b' and line 3\r\n'
            b' introducing line 4\n'
            b' which is still going.\r\n'
            b'#.change:\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 88,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 97,
                    'line_endings': 'dos',
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b' line 1\n still line 1\r\n'
                    b' here is line 2\r\n'
                    b' and line 3\r\n'
                    b' introducing line 4\n which is still going.\r\n'
                ),
                'type': 'diff',
            },
            {
                'level': 1,
                'line': 15,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
        ])

    def test_with_content_line_endings_option_unix(self):
        """Testing DiffXReader with content section specifying
        line_endings=unix
        """
        # We're going to have some lines that use \r\n instead of \n in this
        # test, at the start and end of the diff. We'll then figure out if
        # we split it right based on the next section's starting line number.
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=88\n'
            b'{\r\n'
            b'    "path": {\r\n'
            b'        "new": "message2.py",\r\n'
            b'        "old": "message.py"\r\n'
            b'    }\r\n'
            b'}\r\n'
            b'#...diff: length=97, line_endings=dos\n'
            b' line 1\n'
            b' still line 1\r\n'
            b' here is line 2\r\n'
            b' and line 3\r\n'
            b' introducing line 4\n'
            b' which is still going.\r\n'
            b'#.change:\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 88,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 97,
                    'line_endings': 'dos',
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b' line 1\n still line 1\r\n'
                    b' here is line 2\r\n'
                    b' and line 3\r\n'
                    b' introducing line 4\n which is still going.\r\n'
                ),
                'type': 'diff',
            },
            {
                'level': 1,
                'line': 15,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
        ])

    def test_with_content_utf16(self):
        """Testing DiffXReader with content in UTF-16 encoding"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-16, version=1.0\n'
            b'#.preamble: indent=4, length=36\n'
            b'    \xff\xfet\x00h\x00i\x00s\x00 \x00i\x00s\x00 \x00a\x00 '
            b'\x00t\x00e\x00s\x00t\x00\n\x00'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=48\n'
            b'\xff\xfe{\x00\n\x00 \x00 \x00 \x00 \x00"\x00k\x00e\x00y\x00'
            b'"\x00:\x00 \x00"\x00v\x00a\x00l\x00u\x00e\x00"\x00\n\x00}\x00'
            b'\n\x00'
            b'#...diff: encoding=utf-16, length=24, line_endings=dos\n'
            b'\xff\xfe \x00.\x00.\x00.\x00 \x00d\x00i\x00f\x00f\x00'
            b'\r\x00\n\x00'
            b'#.change:\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-16',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {
                    'indent': 4,
                    'length': 36,
                },
                'section': Section.MAIN_PREAMBLE,
                'text': 'this is a test\n',
                'type': 'preamble',
            },
            {
                'level': 1,
                'line': 3,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 4,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 5,
                'metadata': {
                    'key': 'value',
                },
                'options': {
                    'format': 'json',
                    'length': 48,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 9,
                'options': {
                    'encoding': 'utf-16',
                    'length': 24,
                    'line_endings': 'dos',
                },
                'section': Section.FILE_DIFF,
                'diff': ' ... diff\r\n'.encode('utf-16'),
                'type': 'diff',
            },
            {
                'level': 1,
                'line': 11,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
        ])

    def test_with_content_utf32(self):
        """Testing DiffXReader with content in UTF-32 encoding"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-32, version=1.0\n'
            b'#.preamble: indent=4, length=68\n'
            b'    \xff\xfe\x00\x00'
            b't\x00\x00\x00h\x00\x00\x00i\x00\x00\x00s\x00\x00\x00'
            b' \x00\x00\x00i\x00\x00\x00s\x00\x00\x00 \x00\x00\x00'
            b'a\x00\x00\x00 \x00\x00\x00t\x00\x00\x00e\x00\x00\x00'
            b's\x00\x00\x00t\x00\x00\x00\n\x00\x00\x00'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=96\n'
            b'\xff\xfe\x00\x00'
            b'{\x00\x00\x00\n\x00\x00\x00'
            b' \x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00'
            b'"\x00\x00\x00k\x00\x00\x00e\x00\x00\x00y\x00\x00\x00'
            b'"\x00\x00\x00:\x00\x00\x00 \x00\x00\x00"\x00\x00\x00'
            b'v\x00\x00\x00a\x00\x00\x00l\x00\x00\x00u\x00\x00\x00'
            b'e\x00\x00\x00"\x00\x00\x00\n\x00\x00\x00'
            b'}\x00\x00\x00\n\x00\x00\x00'
            b'#...diff: encoding=utf-32, length=48, line_endings=dos\n'
            b'\xff\xfe\x00\x00 \x00\x00\x00.\x00\x00\x00.\x00\x00\x00'
            b'.\x00\x00\x00 \x00\x00\x00d\x00\x00\x00i\x00\x00\x00'
            b'f\x00\x00\x00f\x00\x00\x00\r\x00\x00\x00\n\x00\x00\x00'
            b'#.change:\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-32',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {
                    'indent': 4,
                    'length': 68,
                },
                'section': Section.MAIN_PREAMBLE,
                'text': 'this is a test\n',
                'type': 'preamble',
            },
            {
                'level': 1,
                'line': 3,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 4,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 5,
                'metadata': {
                    'key': 'value',
                },
                'options': {
                    'format': 'json',
                    'length': 96,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 9,
                'options': {
                    'encoding': 'utf-32',
                    'length': 48,
                    'line_endings': 'dos',
                },
                'section': Section.FILE_DIFF,
                'diff': ' ... diff\r\n'.encode('utf-32'),
                'type': 'diff',
            },
            {
                'level': 1,
                'line': 11,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
        ])

    def test_with_extra_newlines(self):
        """Testing DiffXReader with extra newlines"""
        reader = DiffXReader(io.BytesIO(
            b'\n'
            b'\n'
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'\n'
            b'#.change:\n'
            b'\n'
            b'#..file:\n'
            b'\n'
            b'#...meta: format=json, length=82\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "message2.py",\n'
            b'        "old": "message.py"\n'
            b'    }\n'
            b'}\n'
            b'\n'
            b'\n'
            b'\n'
            b'#...diff: length=692\n'
            b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
            b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
            b'@@ -164,10 +164,10 @@\n'
            b'             not isinstance(headers, MultiValueDict)):\n'
            b'             # Instantiating a MultiValueDict from a dict does '
            b'not ensure that\n'
            b'             # values are lists, so we have to ensure that '
            b'ourselves.\n'
            b'-            headers = MultiValueDict(dict(\n'
            b'-                (key, [value])\n'
            b'-                for key, value in six.iteritems(headers)\n'
            b'-            ))\n'
            b'+            headers = MultiValueDict({\n'
            b'+                key: [value]\n'
            b'+                for key, value in headers.items()\n'
            b'+            })\n'
            b'\n'
            b'         if in_reply_to:\n'
            b'             headers["In-Reply-To"] = in_reply_to\n'
            b'\n'
            b'\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {},
                'section': Section.FILE,
                'type': 'file',
            },
            {
                'level': 3,
                'line': 3,
                'metadata': {
                    'path': {
                        'new': 'message2.py',
                        'old': 'message.py',
                    },
                },
                'options': {
                    'format': 'json',
                    'length': 82,
                },
                'section': Section.FILE_META,
                'type': 'meta',
            },
            {
                'level': 3,
                'line': 10,
                'options': {
                    'length': 692,
                },
                'section': Section.FILE_DIFF,
                'diff': (
                    b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
                    b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
                    b'@@ -164,10 +164,10 @@\n'
                    b'             not isinstance(headers, MultiValueDict)):\n'
                    b'             # Instantiating a MultiValueDict from a '
                    b'dict does not ensure that\n'
                    b'             # values are lists, so we have to ensure '
                    b'that ourselves.\n'
                    b'-            headers = MultiValueDict(dict(\n'
                    b'-                (key, [value])\n'
                    b'-                for key, value in six.iteritems('
                    b'headers)\n'
                    b'-            ))\n'
                    b'+            headers = MultiValueDict({\n'
                    b'+                key: [value]\n'
                    b'+                for key, value in headers.items()\n'
                    b'+            })\n'
                    b'\n'
                    b'         if in_reply_to:\n'
                    b'             headers["In-Reply-To"] = in_reply_to\n'
                ),
                'type': 'diff',
            },
        ])

    def test_with_header_long_line(self):
        """Testing DiffXReader with header with a very long length"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=7, xxx=xxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n'
            b'    :)\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {
                    'indent': 4,
                    'length': 7,
                    'xxx': 'x' * 385,
                },
                'section': Section.CHANGE_PREAMBLE,
                'text': ':)\n',
                'type': 'preamble',
            },
        ])

    def test_with_content_long_lines(self):
        """Testing DiffXReader with content section containing very long lines
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=390\n'
            b'    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            b'xxxxxxxxxxx\n'
        ))

        self.assertEqual(list(reader), [
            {
                'level': 0,
                'line': 0,
                'options': {
                    'encoding': 'utf-8',
                    'version': '1.0',
                },
                'section': Section.MAIN,
                'type': 'diffx',
            },
            {
                'level': 1,
                'line': 1,
                'options': {},
                'section': Section.CHANGE,
                'type': 'change',
            },
            {
                'level': 2,
                'line': 2,
                'options': {
                    'indent': 4,
                    'length': 390,
                },
                'section': Section.CHANGE_PREAMBLE,
                'text': '%s\n' % ('x' * 385),
                'type': 'preamble',
            },
        ])

    def test_with_invalid_version(self):
        """Testing DiffXReader with invalid version in DiffX header"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=142.6\n'
        ))

        message = (
            'Error on line 1: The DiffX version in this file (142.6) is not '
            'supported by this version of the diffx module'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_invalid_section_order(self):
        """Testing DiffXReader with invalid section order"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: version=1.0\n'
            b'#...file:\n'
        ))

        message = (
            'Error on line 2: Unknown or unexpected section ID "...file". '
            'Expected one of: ".change", ".meta", ".preamble"'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_header_invalid_option_key_chars(self):
        """Testing DiffXReader with header containing invalid characters in
        option key
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: #key=value, version=1.0\n'
        ))

        message = (
            'Error on line 1, column 9: Header option key "#key" contains '
            'invalid characters'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_header_invalid_format(self):
        """Testing DiffXReader with header in an invalid format"""
        reader = DiffXReader(io.BytesIO(
            b'#diffx: key=value key=value\n'
        ))

        message = (
            'Error on line 1: Unexpected or improperly formatted header: '
            '%r'
            % b'#diffx: key=value key=value'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_header_invalid_option_value_chars(self):
        """Testing DiffXReader with header containing invalid characters in
        option value
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: key=#value, version=1.0\n'
        ))

        message = (
            'Error on line 1, column 13: Header option value "#value" for '
            'key "key" contains invalid characters'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_content_missing_length_option(self):
        """Testing DiffXReader with content section missing length= option
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta:\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "message2.py",\n'
            b'        "old": "message.py"\n'
            b'    }\n'
            b'}\n'
        ))

        message = (
            'Error on line 4: Expected section "...meta" to have a length '
            'option'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_content_invalid_line_ending_option(self):
        """Testing DiffXReader with content section containing invalid
        line_ending= option
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: length=3, line_endings=c64\n'
            b'{}\n'
        ))

        message = (
            'Error on line 5: Unsupported value "c64" for line_endings. '
            'Expected one of: dos, unix'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_content_missing_newline(self):
        """Testing DiffXReader with content section missing trailing newline
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..preamble: length=2\n'
            b':)\n'
            b'#.change:\n'
        ))

        message = 'Error on line 4: Expected a newline after content'

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_meta_invalid_format(self):
        """Testing DiffXReader with meta section containing invalid format=
        option
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: length=14, format=html\n'
            b'<html></html>\n'
        ))

        message = (
            'Error on line 4: Unexpected metadata format "html". If the '
            '"format" option is provided, it must be "json".'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)

    def test_with_meta_deserialize_error(self):
        """Testing DiffXReader with meta section containing JSON content
        that could not be deserialized
        """
        reader = DiffXReader(io.BytesIO(
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: length=2\n'
            b'"\n'
        ))

        message = (
            'Error on line 4: JSON metadata could not be parsed: '
            'Invalid control character at: line 1 column 2 (char 1)'
        )

        with self.assertRaisesMessage(DiffXParseError, message):
            list(reader)
