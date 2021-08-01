"""Unit tests for pydiffx.writer."""

from __future__ import unicode_literals

import io

import six

from pydiffx.errors import (DiffXContentError,
                            DiffXOptionValueChoiceError,
                            DiffXSectionOrderError)
from pydiffx.options import DiffType, LineEndings, PreambleMimeType
from pydiffx.reader import DiffXReader
from pydiffx.tests.testcases import TestCase
from pydiffx.writer import DiffXWriter


class DiffXWriterTests(TestCase):
    """Unit tests for pydiffx.reader.DiffXWriter."""

    def test_with_simple_diff(self):
        """Testing DiffXWriter with a simple diff"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'path': {
                'old': 'message.py',
                'new': 'message2.py',
            },
        })
        writer.write_diff(
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
        )

        self._check_result(
            stream,
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
            b'#...diff: length=692, line_endings=unix\n'
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
        )

    def test_with_multi_commit_diff(self):
        """Testing DiffXWriter with a multi-commit diff"""
        stream, writer = self._create_writer()

        writer.new_change()
        writer.write_preamble(
            'Summary of the _first_ commit in the series.',
            mimetype=PreambleMimeType.MARKDOWN)
        writer.write_meta({
            'author': 'Test User <test@example.com>',
            'committer': 'Test User <test@example.com>',
            'committer date': '2021-06-02T13:12:06-07:00',
            'date': '2021-06-01T19:26:31-07:00',
            'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
        })

        writer.new_file()
        writer.write_meta({
            'path': 'file1',
            'revision': {
                'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
            },
        })
        writer.write_diff(
            b'--- /file1\n'
            b'+++ /file1\n'
            b'@@ -498,7 +498,7 @@\n'
            b' ... diff content\n'
        )

        writer.new_change()
        writer.write_preamble(
            "Summary of commit #2\n"
            "\n"
            "Here's a description.\n"
        )
        writer.write_meta({
            'author': 'Test User <test@example.com>',
            'committer': 'Test User <test@example.com>',
            'committer date': '2021-06-02T19:46:25-07:00',
            'date': '2021-06-01T19:46:22-07:00',
            'id': '91127b687f583184144161f432222748c1a30b23',
        })

        writer.new_file()
        writer.write_meta({
            'path': 'file2',
            'revision': {
                'old': '1b7af7f97076effed5db722afe31c993e6adbc78',
                'new': 'a2ccb0cb48383472345d41a32afde39a7e6a72dd',
            },
        })
        writer.write_diff(
            b'--- a/file2\n'
            b'+++ b/file2\n'
            b'@@ -66,7 +66,8 @@\n'
            b' ... diff content for commit 2, file2\n'
        )

        writer.new_file()
        writer.write_meta({
            'path': 'file3',
            'revision': {
                'old': 'be089b7197974703c83682088a068bef3422c6c2',
                'new': '0d4a0fb8d62b762a26e13591d06d93d79d61102f',
            },
        })

        writer.write_diff(
            b'--- a/file3\n'
            b'+++ b/file3\n'
            b'@@ -258,7 +258,8 @@\n'
            b' ... diff content for commit 2, file3\n'
        )

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=49, line_endings=unix,'
            b' mimetype=text/markdown\n'
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
            b'#...diff: length=60, line_endings=unix\n'
            b'--- /file1\n'
            b'+++ /file1\n'
            b'@@ -498,7 +498,7 @@\n'
            b' ... diff content\n'
            b'#.change:\n'
            b'#..preamble: indent=4, length=56, line_endings=unix\n'
            b'    Summary of commit #2\n'
            b'    \n'
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
            b'#...diff: length=80, line_endings=unix\n'
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
            b'#...diff: length=82, line_endings=unix\n'
            b'--- a/file3\n'
            b'+++ b/file3\n'
            b'@@ -258,7 +258,8 @@\n'
            b' ... diff content for commit 2, file3\n'
        )

    def test_with_unsupported_version(self):
        """Testing DiffXWriter with an unsupported version"""
        message = (
            '"123.456" is not a supported value for version. Expected '
            'one of: 1.0'
        )

        with self.assertRaisesMessage(DiffXOptionValueChoiceError, message):
            self._create_writer(version='123.456')

    def test_with_content_crlf_and_no_line_endings(self):
        """Testing DiffXWriter with content containing CRLF newlines and no
        line_endings= option
        """
        stream, writer = self._create_writer()

        writer.write_preamble(
            'This is a summary\r\n'
            '\r\n'
            'And here is the description with embedded "\n", like that.')

        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'path': {
                'old': 'file.txt',
                'new': 'file.txt',
            },
        })
        writer.write_diff(
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... not a \n!\r\n'
        )

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=92, line_endings=dos\n'
            b'    This is a summary\r\n'
            b'    \r\n'
            b'    And here is the description with embedded "\n", like that.'
            b'\r\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=77\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "file.txt",\n'
            b'        "old": "file.txt"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=85, line_endings=dos\n'
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... not a \n!\r\n'
        )

    def test_with_content_crlf_and_line_endings_dos(self):
        """Testing DiffXWriter with content containing CRLF newlines and
        line_endings=dos
        """
        stream, writer = self._create_writer()

        writer.write_preamble(
            'This is a summary\r\n'
            '\r\n'
            'And here is the description with embedded "\n", like that.',
            line_endings=LineEndings.DOS)

        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'path': {
                'old': 'file.txt',
                'new': 'file.txt',
            },
        })
        writer.write_diff(
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... not a \n!\r\n',
            line_endings=LineEndings.DOS)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=92, line_endings=dos\n'
            b'    This is a summary\r\n'
            b'    \r\n'
            b'    And here is the description with embedded "\n", like '
            b'that.\r\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=77\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "file.txt",\n'
            b'        "old": "file.txt"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=85, line_endings=dos\n'
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... not a \n!\r\n'
        )

    def test_with_content_crlf_and_line_endings_unix(self):
        """Testing DiffXWriter with content containing CRLF newlines and
        line_endings=unix
        """
        stream, writer = self._create_writer()

        writer.write_preamble(
            'This is a summary\r\n'
            '\r\n'
            'And here is the description with embedded "\n", like that.',
            line_endings=LineEndings.UNIX)

        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'path': {
                'old': 'file.txt',
                'new': 'file.txt',
            },
        })
        writer.write_diff(
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... each CR is just a character, not a newline.',
            line_endings=LineEndings.UNIX)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=95, line_endings=unix\n'
            b'    This is a summary\r\n'
            b'    \r\n'
            b'    And here is the description with embedded "\n'
            b'    ", like that.\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=77\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "file.txt",\n'
            b'        "old": "file.txt"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=119, line_endings=unix\n'
            b'--- /file.txt\r\n'
            b'+++ /file.txt\r\n'
            b'@@ -498,7 +498,7 @@\r\n'
            b' ... diff content\r\n'
            b' ... each CR is just a character, not a newline.\n'
        )

    def test_with_content_utf16(self):
        """Testing DiffXWriter with content in UTF-16 encoding"""
        stream, writer = self._create_writer(encoding='utf-16')
        writer.write_preamble('this is a test\n')

        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        writer.write_diff(
            ' ... diff\r\n'.encode('utf-16'),
            encoding='utf-16')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-16, version=1.0\n'
            b'#.preamble: indent=4, length=36, line_endings=unix\n'
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
        )

    def test_with_content_utf32(self):
        """Testing DiffXWriter with content in UTF-32 encoding"""
        stream, writer = self._create_writer(encoding='utf-32')
        writer.write_preamble('this is a test\n')

        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        writer.write_diff(
            ' ... diff\r\n'.encode('utf-32'),
            encoding='utf-32')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-32, version=1.0\n'
            b'#.preamble: indent=4, length=68, line_endings=unix\n'
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
        )

    def test_new_change_after_new_change(self):
        """Testing DiffXWriter.new_change after new_change"""
        stream, writer = self._create_writer()
        writer.new_change()

        message = (
            'new_change() cannot be called at this stage (after '
            'new_change()). Expected one of: new_file(), write_meta(), '
            'write_preamble()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.new_change()

    def test_new_change_after_new_file(self):
        """Testing DiffXWriter.new_change after new_file"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()

        message = (
            'new_change() cannot be called at this stage (after new_file()). '
            'Expected write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.new_change()

    def test_new_file_before_change(self):
        """Testing DiffXWriter.new_file before new_change"""
        stream, writer = self._create_writer()

        message = (
            'new_file() cannot be called at this stage (after '
            'initialization). Expected one of: new_change(), write_meta(), '
            'write_preamble()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.new_file()

    def test_new_file_after_new_file(self):
        """Testing DiffXWriter.new_file after new_file"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()

        message = (
            'new_file() cannot be called at this stage (after new_file()). '
            'Expected write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.new_file()

    def test_write_diff_with_diff_type_binary(self):
        """Testing DiffXWriter.write_diff with diff_type=binary"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })
        writer.write_diff(b'...', diff_type=DiffType.BINARY)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=23\n'
            b'{\n'
            b'    "key": "value"\n'
            b'}\n'
            b'#...diff: length=4, line_endings=unix, type=binary\n'
            b'...\n'
        )

    def test_write_diff_with_diff_type_invalid(self):
        """Testing DiffXWriter.write_diff with invalid diff_type= value"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            '"xxx" is not a supported value for diff_type. Expected one of: '
            'binary, text'
        )

        with self.assertRaisesMessage(DiffXOptionValueChoiceError, message):
            writer.write_diff(b'...', diff_type='xxx')

    def test_write_diff_with_diff_type_text(self):
        """Testing DiffXWriter.write_diff with diff_type=text"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })
        writer.write_diff(b'...', diff_type=DiffType.TEXT)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=23\n'
            b'{\n'
            b'    "key": "value"\n'
            b'}\n'
            b'#...diff: length=4, line_endings=unix, type=text\n'
            b'...\n'
        )

    def test_write_diff_with_non_bytes(self):
        """Testing DiffXWriter.write_diff with non-bytes diff"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        message = 'diff must be a byte string, not %s' % six.text_type

        with self.assertRaisesMessage(DiffXContentError, message):
            writer.write_diff('...')

    def test_write_diff_with_encoding_no_newline_line_endings(self):
        """Testing DiffXWriter.write_diff with multi-byte encoding, no
        trailing newline, and specific line endings
        """
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })
        writer.write_diff('...'.encode('utf-16'),
                          diff_type=DiffType.TEXT,
                          line_endings=LineEndings.UNIX,
                          encoding='utf-16')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=23\n'
            b'{\n'
            b'    "key": "value"\n'
            b'}\n'
            b'#...diff: encoding=utf-16, length=10, line_endings=unix,'
            b' type=text\n'
            b'\xff\xfe.\x00.\x00.\x00\n\x00'
        )

    def test_write_diff_before_change(self):
        """Testing DiffXWriter.write_diff before new_change"""
        stream, writer = self._create_writer()

        message = (
            'write_diff() cannot be called at this stage (after '
            'initialization). Expected one of: new_change(), write_meta(), '
            'write_preamble()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_diff(b'...')

    def test_write_diff_before_file(self):
        """Testing DiffXWriter.write_diff before new_file"""
        stream, writer = self._create_writer()
        writer.new_change()

        message = (
            'write_diff() cannot be called at this stage (after '
            'new_change()). Expected one of: new_file(), write_meta(), '
            'write_preamble()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_diff(b'...')

    def test_write_diff_before_file_write_meta(self):
        """Testing DiffXWriter.write_diff before new_file + write_meta"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()

        message = (
            'write_diff() cannot be called at this stage (after new_file()). '
            'Expected write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_diff(b'...')

    def test_write_diff_after_write_diff(self):
        """Testing DiffXWriter.write_diff after write_diff"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })
        writer.write_diff(b'...')

        message = (
            'write_diff() cannot be called at this stage (after '
            'write_diff()). Expected one of: new_change(), new_file()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_diff(b'...')

    def test_write_meta_with_invalid_type(self):
        """Testing DiffXWriter.write_meta with non-dict"""
        stream, writer = self._create_writer()

        message = "metadata must be a dictionary, not %s" % list

        with self.assertRaisesMessage(DiffXContentError, message):
            writer.write_meta([1, 2, 3])

    def test_write_meta_with_empty_dictionary(self):
        """Testing DiffXWriter.write_meta with empty dict"""
        stream, writer = self._create_writer()

        message = 'metadata cannot be empty'

        with self.assertRaisesMessage(DiffXContentError, message):
            writer.write_meta({})

    def test_write_meta_after_write_meta(self):
        """Testing DiffXWriter.write_meta after write_meta"""
        stream, writer = self._create_writer()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_meta() cannot be called at this stage (after '
            'write_meta()). Expected new_change()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_meta({
                'key': 'value',
            })

    def test_write_meta_after_change_write_meta(self):
        """Testing DiffXWriter.write_meta after new_change + write_meta"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_meta() cannot be called at this stage (after '
            'write_meta()). Expected one of: new_change(), new_file()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_meta({
                'key': 'value',
            })

    def test_write_meta_after_file_write_meta(self):
        """Testing DiffXWriter.write_meta after new_file + write_meta"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_meta() cannot be called at this stage (after '
            'write_meta()). Expected one of: new_change(), new_file(), '
            'write_diff()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_meta({
                'key': 'value',
            })

    def test_write_preamble_with_indent_0(self):
        """Testing DiffXWriter.write_preamble with indent=0"""
        stream, writer = self._create_writer()
        writer.write_preamble('...', indent=0)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=0, length=4, line_endings=unix\n'
            b'...\n'
        )

    def test_write_preamble_with_unicode_string(self):
        """Testing DiffXWriter.write_preamble with a Unicode string"""
        stream, writer = self._create_writer()
        writer.write_preamble('...')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=8, line_endings=unix\n'
            b'    ...\n'
        )

    def test_write_preamble_with_byte_string(self):
        """Testing DiffXWriter.write_preamble with a byte string"""
        stream, writer = self._create_writer()

        message = 'text must be a Unicode string, not %s' % bytes

        with self.assertRaisesMessage(DiffXContentError, message):
            writer.write_preamble(b'...')

    def test_write_preamble_with_empty_text(self):
        """Testing DiffXWriter.write_preamble with empty text"""
        stream, writer = self._create_writer()

        message = 'The text cannot be empty.'

        with self.assertRaisesMessage(DiffXContentError, message):
            writer.write_preamble('')

    def test_write_preamble_with_line_endings_dos(self):
        """Testing DiffXWriter.write_preamble with line_endings=dos"""
        stream, writer = self._create_writer()
        writer.write_preamble('text', line_endings=LineEndings.DOS)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=10, line_endings=dos\n'
            b'    text\r\n'
        )

    def test_write_preamble_with_line_endings_unix(self):
        """Testing DiffXWriter.write_preamble with line_endings=unix"""
        stream, writer = self._create_writer()
        writer.write_preamble('text', line_endings=LineEndings.UNIX)

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=9, line_endings=unix\n'
            b'    text\n'
        )

    def test_write_preamble_with_line_endings_invalid(self):
        """Testing DiffXWriter.write_preamble with invalid line_endings=
        value
        """
        stream, writer = self._create_writer()

        message = (
            '"xxx" is not a supported value for line_endings. Expected one '
            'of: dos, unix'
        )

        with self.assertRaisesMessage(DiffXOptionValueChoiceError, message):
            writer.write_preamble('text', line_endings='xxx')

    def test_write_preamble_with_mimetype_text_plain(self):
        """Testing DiffXWriter.write_preamble with mimetype=text/plain"""
        stream, writer = self._create_writer()
        writer.write_preamble('hi!', mimetype='text/plain')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=8, line_endings=unix,'
            b' mimetype=text/plain\n'
            b'    hi!\n'
        )

    def test_write_preamble_with_mimetype_text_markdown(self):
        """Testing DiffXWriter.write_preamble with mimetype=text/markdown"""
        stream, writer = self._create_writer()
        writer.write_preamble('hi!', mimetype='text/markdown')

        self._check_result(
            stream,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.preamble: indent=4, length=8, line_endings=unix,'
            b' mimetype=text/markdown\n'
            b'    hi!\n'
        )

    def test_write_preamble_with_mimetype_invalid(self):
        """Testing DiffXWriter.write_preamble with invalid mimetype= value"""
        stream, writer = self._create_writer()

        message = (
            '"text/xxx" is not a supported value for mimetype. Expected one '
            'of: text/markdown, text/plain'
        )

        with self.assertRaisesMessage(DiffXOptionValueChoiceError, message):
            writer.write_preamble('hi!', mimetype='text/xxx')

    def test_write_preamble_after_main_write_meta(self):
        """Testing DiffXWriter.write_preamble after write_meta"""
        stream, writer = self._create_writer()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_preamble() cannot be called at this stage (after '
            'write_meta()). Expected new_change()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def test_write_preamble_after_change_write_meta(self):
        """Testing DiffXWriter.write_preamble after new_change + write_meta"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_preamble() cannot be called at this stage (after '
            'write_meta()). Expected one of: new_change(), new_file()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def test_write_preamble_after_write_preamble(self):
        """Testing DiffXWriter.write_preamble after write_preamble"""
        stream, writer = self._create_writer()
        writer.write_preamble('text')

        message = (
            'write_preamble() cannot be called at this stage (after '
            'write_preamble()). Expected one of: new_change(), write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def test_write_preamble_after_change_write_preamble(self):
        """Testing DiffXWriter.write_preamble after new_change + write_preamble
        """
        stream, writer = self._create_writer()
        writer.new_change()
        writer.write_preamble('text')

        message = (
            'write_preamble() cannot be called at this stage (after '
            'write_preamble()). Expected one of: new_file(), write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def test_write_preamble_after_new_file(self):
        """Testing DiffXWriter.write_preamble after new_file"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()

        message = (
            'write_preamble() cannot be called at this stage (after '
            'new_file()). Expected write_meta()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def test_write_meta_after_write_diff(self):
        """Testing DiffXWriter.write_meta after write_diff"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })
        writer.write_diff(b'...')

        message = (
            'write_meta() cannot be called at this stage (after '
            'write_diff()). Expected one of: new_change(), new_file()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_meta({
                'key': 'value',
            })

    def test_write_preamble_after_file_write_meta(self):
        """Testing DiffXWriter.write_preamble after new_file + write_meta"""
        stream, writer = self._create_writer()
        writer.new_change()
        writer.new_file()
        writer.write_meta({
            'key': 'value',
        })

        message = (
            'write_preamble() cannot be called at this stage (after '
            'write_meta()). Expected one of: new_change(), new_file(), '
            'write_diff()'
        )

        with self.assertRaisesMessage(DiffXSectionOrderError, message):
            writer.write_preamble('text')

    def _create_writer(self, **kwargs):
        """Return a new stream and writer.

        Args:
            **kwargs (dict):
                Keyword arguments to pass to the writer.

        Returns:
            tuple:
            A 2-tuple of:

            1. The byte stream.
            2. The writer.
        """
        stream = io.BytesIO()

        try:
            writer = DiffXWriter(stream, **kwargs)
        except Exception:
            stream.close()
            raise

        return stream, writer

    def _check_result(self, stream, expected_result,
                      line_endings=LineEndings.UNIX):
        """Check the result of a write.

        This will check that the stream matches the expected result, and
        check that the result can be successfully parsed by a reader.

        Args:
            stream (io.BytesIO):
                The fully-written stream.

            expected_result (bytes):
                The expected byte content of the DiffX file.

            line_endings (unicode, optional):
                The expected line endings of the DiffX file.

        Raises:
            AssertionError:
                The byte content was incorrect.

            pydiffx.errors.DiffXParseError:
                The resulting content could not be parsed.
        """
        data = stream.getvalue()
        stream.close()

        self.assertMultiLineBytesEqual(data, expected_result,
                                       line_endings=line_endings)

        # Make sure the generated diff can be parsed.
        stream = io.BytesIO(data)
        reader = DiffXReader(stream)
        list(reader)
        stream.close()
