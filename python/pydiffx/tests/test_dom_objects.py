"""Unit tests for pydiffx.dom.objects."""

from __future__ import unicode_literals

import kgb
import six

from pydiffx.dom.objects import (DiffX,
                                 DiffXChangeSection,
                                 DiffXFileDiffSection,
                                 DiffXFileSection,
                                 DiffXMetaSection,
                                 DiffXPreambleSection,
                                 logger as dom_objects_logger)
from pydiffx.errors import (DiffXOptionValueChoiceError,
                            DiffXOptionValueError,
                            DiffXUnknownOptionError,
                            MalformedHunkError)
from pydiffx.options import (DiffType,
                             LineEndings,
                             MetaFormat,
                             PreambleMimeType)
from pydiffx.tests.testcases import TestCase


class BaseSectionTestCase(TestCase):
    """Base class for DOM section tests."""

    section_cls = None

    def run_content_test(self, content, expected_default=None,
                         attr_name='content'):
        section = self.section_cls()
        self.assertEqual(getattr(section, attr_name), expected_default)

        setattr(section, attr_name, content)
        self.assertEqual(getattr(section, attr_name), content)

    def run_invalid_content_type_test(self, content, expected_type,
                                      attr_name='content'):
        section = self.section_cls()

        expected_message = (
            'Expected the content to be a %s type, got %s instead'
            % (expected_type, type(content))
        )

        with self.assertRaisesMessage(TypeError, expected_message):
            setattr(section, attr_name, content)

    def run_option_test(self, option_name, value, expected_default=None):
        section = self.section_cls()
        self.assertEqual(getattr(section, option_name), expected_default)

        setattr(section, option_name, value)
        self.assertEqual(getattr(section, option_name), value)
        self.assertEqual(section.options[option_name], value)

    def run_invalid_option_type_test(self, option_name, value, expected_type):
        section = self.section_cls()

        expected_message = (
            'Expected "%s" to be a %s type, got %s instead'
            % (option_name, expected_type, type(value))
        )

        with self.assertRaisesMessage(DiffXOptionValueError, expected_message):
            setattr(section, option_name, value)

    def run_invalid_option_value_test(self, option_name, value,
                                      expected_choices):
        section = self.section_cls()

        expected_message = (
            '"%s" is not a supported value for %s. Expected one of: %s'
            % (value, option_name, ', '.join(sorted(expected_choices)))
        )

        with self.assertRaisesMessage(DiffXOptionValueChoiceError,
                                      expected_message):
            setattr(section, option_name, value)


class DiffXTests(BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffX."""

    section_cls = DiffX

    def test_to_bytes_with_simple_diff(self):
        """Testing DiffX.to_bytes with a simple diff"""
        diffx_file = DiffX()
        change = diffx_file.add_change()
        change.add_file(
            meta={
                'path': {
                    'old': 'message.py',
                    'new': 'message2.py',
                },
            },
            diff=(
                b'--- message.py\t2021-07-02 13:20:12.285875444 -0700\n'
                b'+++ message2.py\t2021-07-02 13:21:31.428383873 -0700\n'
                b'@@ -164,10 +164,10 @@\n'
                b'             not isinstance(headers, MultiValueDict)):\n'
                b'             # Instantiating a MultiValueDict from a dict '
                b'does not ensure that\n'
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

        self._check_result(
            diffx_file,
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

    def test_to_bytes_with_complex_diff(self):
        """Testing DiffX.to_bytes with a complex diff"""
        diffx_file = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32',
            version='1.0')

        change = diffx_file.add_change(
            preamble='test',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.MARKDOWN,
            meta={
                'author': 'Test User <test@example.com>',
                'committer': 'Test User <test@example.com>',
                'committer date': '2021-06-02T13:12:06-07:00',
                'date': '2021-06-01T19:26:31-07:00',
                'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
            },
            meta_encoding='utf-8')
        change.add_file(
            meta={
                'path': 'file1',
                'revision': {
                    'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                    'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
                },
            },
            meta_encoding='latin1',
            diff=(
                b'--- /file1\n'
                b'+++ /file1\n'
                b'@@ -498,7 +498,7 @@\n'
                b' ... diff content\n'
            ))

        change = diffx_file.add_change(
            preamble=(
                "Summary of commit #2\n"
                "\n"
                "Here's a description.\n"
            ),
            preamble_encoding='utf-8',
            meta={
                'author': 'Test User <test@example.com>',
                'committer': 'Test User <test@example.com>',
                'committer date': '2021-06-02T19:46:25-07:00',
                'date': '2021-06-01T19:46:22-07:00',
                'id': '91127b687f583184144161f432222748c1a30b23',
            },
            meta_encoding='utf-8')

        change.add_file(
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32',
            diff=' ... diff'.encode('utf-16'),
            diff_encoding='utf-16')

        change.add_file(
            meta={
                'path': 'file3',
                'revision': {
                    'old': 'be089b7197974703c83682088a068bef3422c6c2',
                    'new': '0d4a0fb8d62b762a26e13591d06d93d79d61102f',
                },
            },
            meta_encoding='utf-8',
            diff=(
                b'--- a/file3\r\n'
                b'+++ b/file3\r\n'
                b'@@ -258,7 +258,8 @@\r\n'
                b' ... diff content for commit 2, file3\r\n'
            ),
            diff_line_endings=LineEndings.DOS)

        self._check_result(
            diffx_file,
            b'#diffx: encoding=utf-16, version=1.0\n'
            b'#.preamble: encoding=ascii, indent=2, length=36,'
            b' line_endings=dos, mimetype=text/plain\n'
            b'  This is the file-level preamble.\r\n'
            b'#.meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00{\x00\x00\x00\n\x00\x00\x00'
            b' \x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00"'
            b'\x00\x00\x00k\x00\x00\x00e\x00\x00\x00y\x00\x00\x00"'
            b'\x00\x00\x00:\x00\x00\x00 \x00\x00\x00"\x00\x00\x00v'
            b'\x00\x00\x00a\x00\x00\x00l\x00\x00\x00u\x00\x00\x00e'
            b'\x00\x00\x00"\x00\x00\x00\n\x00\x00\x00}\x00\x00\x00'
            b'\n\x00\x00\x00'
            b'#.change:\n'
            b'#..preamble: indent=2, length=14, line_endings=unix, '
            b'mimetype=text/markdown\n'
            b'  \xff\xfet\x00e\x00s\x00t\x00\n\x00'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T13:12:06-07:00",\n'
            b'    "date": "2021-06-01T19:26:31-07:00",\n'
            b'    "id": "a25e7b28af5e3184946068f432122c68c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=latin1, format=json, length=166\n'
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
            b'#..preamble: encoding=utf-8, indent=4, length=56, '
            b'line_endings=unix\n'
            b'    Summary of commit #2\n'
            b'    \n'
            b'    Here\'s a description.\n'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T19:46:25-07:00",\n'
            b'    "date": "2021-06-01T19:46:22-07:00",\n'
            b'    "id": "91127b687f583184144161f432222748c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00'
            b'{\x00\x00\x00\n'
            b'\x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00'
            b' \x00\x00\x00"\x00\x00\x00k\x00\x00\x00e\x00\x00\x00'
            b'y\x00\x00\x00"\x00\x00\x00:\x00\x00\x00 \x00\x00\x00'
            b'"\x00\x00\x00v\x00\x00\x00a\x00\x00\x00l\x00\x00\x00'
            b'u\x00\x00\x00e\x00\x00\x00"\x00\x00\x00\n'
            b'\x00\x00\x00}\x00\x00\x00\n\x00\x00\x00'
            b'#...diff: encoding=utf-16, length=22, line_endings=unix\n'
            b'\xff\xfe \x00.\x00.\x00.\x00 \x00d\x00i\x00f\x00f\x00\n\x00'
            b'#..file:\n'
            b'#...meta: encoding=utf-8, format=json, length=166\n'
            b'{\n'
            b'    "path": "file3",\n'
            b'    "revision": {\n'
            b'        "new": "0d4a0fb8d62b762a26e13591d06d93d79d61102f",\n'
            b'        "old": "be089b7197974703c83682088a068bef3422c6c2"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=86, line_endings=dos\n'
            b'--- a/file3\r\n'
            b'+++ b/file3\r\n'
            b'@@ -258,7 +258,8 @@\r\n'
            b' ... diff content for commit 2, file3\r\n'
        )

    def test_to_bytes_with_binary_diff_content(self):
        """Testing DiffX.to_bytes with a binary diff content"""
        diffx_file = DiffX()
        change = diffx_file.add_change()
        change.add_file(
            meta={
                'path': 'file.bin',
            },
            diff_type='binary',
            diff=b'Binary file has changed')

        self._check_result(
            diffx_file,
            b'#diffx: encoding=utf-8, version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=27\n'
            b'{\n'
            b'    "path": "file.bin"\n'
            b'}\n'
            b'#...diff: length=24, line_endings=unix, type=binary\n'
            b'Binary file has changed\n'
        )

    def test_from_bytes_with_simple_diff(self):
        """Testing DiffX.from_bytes with a simple diff"""
        diffx = DiffX.from_bytes(
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

        self.assertEqual(diffx.options, {
            'encoding': 'utf-8',
            'version': '1.0',
        })
        self.assertIsNone(diffx.preamble)
        self.assertEqual(diffx.preamble_section.options, {})
        self.assertEqual(diffx.meta, {})
        self.assertEqual(diffx.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(diffx.changes), 1)

        # Change #1
        change = diffx.changes[0]
        self.assertEqual(change.options, {})
        self.assertIsNone(change.preamble)
        self.assertEqual(change.preamble_section.options, {})
        self.assertEqual(change.meta, {})
        self.assertEqual(change.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(change.files), 1)

        # Change #1, file #1
        file = change.files[0]
        self.assertEqual(file.meta, {
            'path': {
                'new': 'message2.py',
                'old': 'message.py',
            },
        })
        self.assertEqual(file.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(
            file.diff,
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
            b'             headers["In-Reply-To"] = in_reply_to\n')
        self.assertEqual(file.diff_section.options, {
            'line_endings': LineEndings.UNIX,
        })

    def test_from_bytes_with_complex_diff(self):
        """Testing DiffX.from_bytes with a complex diff"""
        diffx = DiffX.from_bytes(
            b'#diffx: encoding=utf-16, version=1.0\n'
            b'#.preamble: encoding=ascii, indent=2, length=36,'
            b' line_endings=dos, mimetype=text/plain\n'
            b'  This is the file-level preamble.\r\n'
            b'#.meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00{\x00\x00\x00\n\x00\x00\x00'
            b' \x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00"'
            b'\x00\x00\x00k\x00\x00\x00e\x00\x00\x00y\x00\x00\x00"'
            b'\x00\x00\x00:\x00\x00\x00 \x00\x00\x00"\x00\x00\x00v'
            b'\x00\x00\x00a\x00\x00\x00l\x00\x00\x00u\x00\x00\x00e'
            b'\x00\x00\x00"\x00\x00\x00\n\x00\x00\x00}\x00\x00\x00'
            b'\n\x00\x00\x00'
            b'#.change:\n'
            b'#..preamble: indent=2, length=14, line_endings=unix, '
            b'mimetype=text/markdown\n'
            b'  \xff\xfet\x00e\x00s\x00t\x00\n\x00'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T13:12:06-07:00",\n'
            b'    "date": "2021-06-01T19:26:31-07:00",\n'
            b'    "id": "a25e7b28af5e3184946068f432122c68c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=latin1, format=json, length=166\n'
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
            b'#.change: encoding=utf-32\n'
            b'#..preamble: encoding=utf-8, indent=4, length=56, '
            b'line_endings=unix\n'
            b'    Summary of commit #2\n'
            b'    \n'
            b'    Here\'s a description.\n'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T19:46:25-07:00",\n'
            b'    "date": "2021-06-01T19:46:22-07:00",\n'
            b'    "id": "91127b687f583184144161f432222748c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00'
            b'{\x00\x00\x00\n'
            b'\x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00'
            b' \x00\x00\x00"\x00\x00\x00k\x00\x00\x00e\x00\x00\x00'
            b'y\x00\x00\x00"\x00\x00\x00:\x00\x00\x00 \x00\x00\x00'
            b'"\x00\x00\x00v\x00\x00\x00a\x00\x00\x00l\x00\x00\x00'
            b'u\x00\x00\x00e\x00\x00\x00"\x00\x00\x00\n'
            b'\x00\x00\x00}\x00\x00\x00\n\x00\x00\x00'
            b'#...diff: encoding=utf-16, length=22, line_endings=unix\n'
            b'\xff\xfe \x00.\x00.\x00.\x00 \x00d\x00i\x00f\x00f\x00\n\x00'
            b'#..file:\n'
            b'#...meta: encoding=utf-8, format=json, length=166\n'
            b'{\n'
            b'    "path": "file3",\n'
            b'    "revision": {\n'
            b'        "new": "0d4a0fb8d62b762a26e13591d06d93d79d61102f",\n'
            b'        "old": "be089b7197974703c83682088a068bef3422c6c2"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=86, line_endings=dos\n'
            b'--- a/file3\r\n'
            b'+++ b/file3\r\n'
            b'@@ -258,7 +258,8 @@\r\n'
            b' ... diff content for commit 2, file3\r\n'
        )

        self.assertEqual(diffx.options, {
            'encoding': 'utf-16',
            'version': '1.0',
        })
        self.assertEqual(diffx.preamble,
                         'This is the file-level preamble.\r\n')
        self.assertEqual(diffx.preamble_section.options, {
            'encoding': 'ascii',
            'indent': 2,
            'line_endings': LineEndings.DOS,
            'mimetype': PreambleMimeType.PLAIN,
        })
        self.assertEqual(diffx.meta, {
            'key': 'value',
        })
        self.assertEqual(diffx.meta_section.options, {
            'encoding': 'utf-32',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(diffx.changes), 2)

        # Change #1
        change = diffx.changes[0]
        self.assertEqual(change.options, {})
        self.assertEqual(change.preamble, 'test\n')
        self.assertEqual(change.preamble_section.options, {
            'indent': 2,
            'line_endings': LineEndings.UNIX,
            'mimetype': PreambleMimeType.MARKDOWN,
        })
        self.assertEqual(change.meta, {
            'author': 'Test User <test@example.com>',
            'committer': 'Test User <test@example.com>',
            'committer date': '2021-06-02T13:12:06-07:00',
            'date': '2021-06-01T19:26:31-07:00',
            'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
        })
        self.assertEqual(change.meta_section.options, {
            'encoding': 'utf-8',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(change.files), 1)

        # Change #1, file #1
        file = change.files[0]
        self.assertEqual(file.meta, {
            'path': 'file1',
            'revision': {
                'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
            },
        })
        self.assertEqual(file.meta_section.options, {
            'encoding': 'latin1',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(
            file.diff,
            b'--- /file1\n'
            b'+++ /file1\n'
            b'@@ -498,7 +498,7 @@\n'
            b' ... diff content\n')
        self.assertEqual(file.diff_section.options, {
            'line_endings': LineEndings.UNIX,
        })

        # Change #2
        change = diffx.changes[1]
        self.assertEqual(change.options, {
            'encoding': 'utf-32',
        })
        self.assertEqual(change.preamble,
                         "Summary of commit #2\n"
                         "\n"
                         "Here's a description.\n")
        self.assertEqual(change.preamble_section.options, {
            'encoding': 'utf-8',
            'indent': 4,
            'line_endings': LineEndings.UNIX,
        })
        self.assertEqual(change.meta, {
            'author': 'Test User <test@example.com>',
            'committer': 'Test User <test@example.com>',
            'committer date': '2021-06-02T19:46:25-07:00',
            'date': '2021-06-01T19:46:22-07:00',
            'id': '91127b687f583184144161f432222748c1a30b23',
        })
        self.assertEqual(change.meta_section.options, {
            'encoding': 'utf-8',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(change.files), 2)

        # Change #2, file #1
        file = change.files[0]
        self.assertEqual(file.meta, {
            'key': 'value',
        })
        self.assertEqual(file.meta_section.options, {
            'encoding': 'utf-32',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(file.diff, ' ... diff\n'.encode('utf-16'))
        self.assertEqual(file.diff_section.options, {
            'encoding': 'utf-16',
            'line_endings': LineEndings.UNIX,
        })

        # Change #2, file #2
        file = change.files[1]
        self.assertEqual(file.meta, {
            'path': 'file3',
            'revision': {
                'old': 'be089b7197974703c83682088a068bef3422c6c2',
                'new': '0d4a0fb8d62b762a26e13591d06d93d79d61102f',
            },
        })
        self.assertEqual(file.meta_section.options, {
            'encoding': 'utf-8',
            'format': MetaFormat.JSON,
        })
        self.assertEqual(
            file.diff,
            b'--- a/file3\r\n'
            b'+++ b/file3\r\n'
            b'@@ -258,7 +258,8 @@\r\n'
            b' ... diff content for commit 2, file3\r\n')
        self.assertEqual(file.diff_section.options, {
            'line_endings': LineEndings.DOS,
        })

    def test_from_bytes_with_no_diffx_encoding(self):
        """Testing DiffX.from_bytes with a diffx without a main encoding"""
        diffx = DiffX.from_bytes(
            b'#diffx: version=1.0\n'
            b'#.change:\n'
            b'#..file:\n'
            b'#...meta: format=json, length=82\n'
            b'{\n'
            b'    "path": {\n'
            b'        "new": "message2.py",\n'
            b'        "old": "message.py"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=50\n'
            b'--- file\n'
            b'+++ file\n'
            b'@@ -1 +1 @@\n'
            b'-old line\n'
            b'+new line\n'
        )

        self.assertEqual(diffx.options, {
            'version': '1.0',
        })
        self.assertIsNone(diffx.preamble)
        self.assertEqual(diffx.preamble_section.options, {})
        self.assertEqual(diffx.meta, {})
        self.assertEqual(diffx.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(diffx.changes), 1)

        # Change #1
        change = diffx.changes[0]
        self.assertEqual(change.options, {})
        self.assertIsNone(change.preamble)
        self.assertEqual(change.preamble_section.options, {})
        self.assertEqual(change.meta, {})
        self.assertEqual(change.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(len(change.files), 1)

        # Change #1, file #1
        file = change.files[0]
        self.assertEqual(file.meta, {
            'path': {
                'new': 'message2.py',
                'old': 'message.py',
            },
        })
        self.assertEqual(file.meta_section.options, {
            'format': MetaFormat.JSON,
        })
        self.assertEqual(
            file.diff,
            b'--- file\n'
            b'+++ file\n'
            b'@@ -1 +1 @@\n'
            b'-old line\n'
            b'+new line\n')
        self.assertEqual(file.diff_section.options, {})

    def test_from_bytes_to_bytes_preserves_content(self):
        """Testing DiffX.from_bytes followed by to_bytes results in
        byte-for-byte reproduction
        """
        diff_content = (
            b'#diffx: version=1.0\n'
            b'#.preamble: encoding=ascii, indent=2, length=36,'
            b' line_endings=dos, mimetype=text/plain\n'
            b'  This is the file-level preamble.\r\n'
            b'#.meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00{\x00\x00\x00\n\x00\x00\x00'
            b' \x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00"'
            b'\x00\x00\x00k\x00\x00\x00e\x00\x00\x00y\x00\x00\x00"'
            b'\x00\x00\x00:\x00\x00\x00 \x00\x00\x00"\x00\x00\x00v'
            b'\x00\x00\x00a\x00\x00\x00l\x00\x00\x00u\x00\x00\x00e'
            b'\x00\x00\x00"\x00\x00\x00\n\x00\x00\x00}\x00\x00\x00'
            b'\n\x00\x00\x00'
            b'#.change: encoding=utf-16\n'
            b'#..preamble: indent=2, length=14, line_endings=unix, '
            b'mimetype=text/markdown\n'
            b'  \xff\xfet\x00e\x00s\x00t\x00\n\x00'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T13:12:06-07:00",\n'
            b'    "date": "2021-06-01T19:26:31-07:00",\n'
            b'    "id": "a25e7b28af5e3184946068f432122c68c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=latin1, format=json, length=166\n'
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
            b'#.change: encoding=utf-32\n'
            b'#..preamble: encoding=utf-8, indent=4, length=56, '
            b'line_endings=unix\n'
            b'    Summary of commit #2\n'
            b'    \n'
            b'    Here\'s a description.\n'
            b'#..meta: encoding=utf-8, format=json, length=244\n'
            b'{\n'
            b'    "author": "Test User <test@example.com>",\n'
            b'    "committer": "Test User <test@example.com>",\n'
            b'    "committer date": "2021-06-02T19:46:25-07:00",\n'
            b'    "date": "2021-06-01T19:46:22-07:00",\n'
            b'    "id": "91127b687f583184144161f432222748c1a30b23"\n'
            b'}\n'
            b'#..file:\n'
            b'#...meta: encoding=utf-32, format=json, length=96\n'
            b'\xff\xfe\x00\x00'
            b'{\x00\x00\x00\n'
            b'\x00\x00\x00 \x00\x00\x00 \x00\x00\x00 \x00\x00\x00'
            b' \x00\x00\x00"\x00\x00\x00k\x00\x00\x00e\x00\x00\x00'
            b'y\x00\x00\x00"\x00\x00\x00:\x00\x00\x00 \x00\x00\x00'
            b'"\x00\x00\x00v\x00\x00\x00a\x00\x00\x00l\x00\x00\x00'
            b'u\x00\x00\x00e\x00\x00\x00"\x00\x00\x00\n'
            b'\x00\x00\x00}\x00\x00\x00\n\x00\x00\x00'
            b'#...diff: encoding=utf-16, length=22, line_endings=unix\n'
            b'\xff\xfe \x00.\x00.\x00.\x00 \x00d\x00i\x00f\x00f\x00\n\x00'
            b'#..file:\n'
            b'#...meta: encoding=utf-8, format=json, length=166\n'
            b'{\n'
            b'    "path": "file3",\n'
            b'    "revision": {\n'
            b'        "new": "0d4a0fb8d62b762a26e13591d06d93d79d61102f",\n'
            b'        "old": "be089b7197974703c83682088a068bef3422c6c2"\n'
            b'    }\n'
            b'}\n'
            b'#...diff: length=86, line_endings=dos\n'
            b'--- a/file3\r\n'
            b'+++ b/file3\r\n'
            b'@@ -258,7 +258,8 @@\r\n'
            b' ... diff content for commit 2, file3\r\n'
        )

        diffx = DiffX.from_bytes(diff_content)
        self.assertMultiLineBytesEqual(diffx.to_bytes(), diff_content)

    def test_meta(self):
        """Testing DiffX.meta"""
        self.run_content_test({'key': 'value'},
                              attr_name='meta',
                              expected_default={})

    def test_preamble(self):
        """Testing DiffX.preamble"""
        self.run_content_test('This is a test',
                              attr_name='preamble')

    def test_generate_stats(self):
        """Testing DiffX.generate_stats"""
        diffx = DiffX()

        change_section = diffx.add_change()
        change_section.add_file(diff=(
            b'git --diff a/file b/file\n'
            b'index abc1234...def5678 100644\n'
            b'--- a/file\n'
            b'+++ b/file\n'
            b'@@ -10,7 +12,10 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'@@ -23,7 +40,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-- \n'
            b'2.9.2\n'
        ))
        change_section.add_file(diff=(
            b'--- a/file\t(revision 1)\n'
            b'+++ b/file\t(revision 2)\n'
            b'@@ -5,9 +5,12 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'-# old line\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))

        change_section = diffx.add_change()
        change_section.add_file(diff=(
            b'git --diff a/file b/file\n'
            b'index abc1234...def5678 100644\n'
            b'--- a/file\n'
            b'+++ b/file\n'
            b'@@ -10 +12,2 @@\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'@@ -23,7 +40,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))
        change_section.add_file(diff=(
            b'--- a/file\t(revision 1)\n'
            b'+++ b/file\t(revision 2)\n'
            b'@@ -5,8 +5,11 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))

        diffx.generate_stats()

        self.assertEqual(
            diffx.meta.get('stats'), {
                'changes': 2,
                'deletions': 9,
                'files': 4,
                'insertions': 19,
                'lines changed': 28,
            })

    def test_generate_stats_merges(self):
        """Testing DiffX.generate_stats merges with existing stats"""
        diffx = DiffX(meta={
            'stats': {
                'special': 123,
            },
        })

        change_section = diffx.add_change()
        change_section.add_file(diff=(
            b'git --diff a/file b/file\n'
            b'index abc1234...def5678 100644\n'
            b'--- a/file\n'
            b'+++ b/file\n'
            b'@@ -10,7 +12,10 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))

        diffx.generate_stats()

        self.assertEqual(
            diffx.meta.get('stats'), {
                'changes': 1,
                'deletions': 1,
                'files': 1,
                'insertions': 4,
                'lines changed': 5,
                'special': 123,
            })

    def test_repr(self):
        """Testing DiffX.__repr__"""
        diffx = DiffX(
            preamble='This is a test.',
            meta={
                'key': 'value',
            })

        self.assertEqual(
            repr(diffx),
            '<DiffX(level=0, options=%r)>'
            % {
                'encoding': 'utf-8',
                'version': '1.0',
            })

    def test_eq(self):
        """Testing DiffX.__eq__"""
        diffx1 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32')
        change1 = diffx1.add_change(
            preamble='test',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.MARKDOWN,
            meta={
                'author': 'Test User <test@example.com>',
                'committer': 'Test User <test@example.com>',
                'committer date': '2021-06-02T13:12:06-07:00',
                'date': '2021-06-01T19:26:31-07:00',
                'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
            },
            meta_encoding='utf-8')
        change1.add_file(
            meta={
                'path': 'file1',
                'revision': {
                    'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                    'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
                },
            },
            meta_encoding='latin1',
            diff=(
                b'--- /file1\n'
                b'+++ /file1\n'
                b'@@ -498,7 +498,7 @@\n'
                b' ... diff content\n'
            ))

        diffx2 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32')
        change2 = diffx2.add_change(
            preamble='test',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.MARKDOWN,
            meta={
                'author': 'Test User <test@example.com>',
                'committer': 'Test User <test@example.com>',
                'committer date': '2021-06-02T13:12:06-07:00',
                'date': '2021-06-01T19:26:31-07:00',
                'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
            },
            meta_encoding='utf-8')
        change2.add_file(
            meta={
                'path': 'file1',
                'revision': {
                    'old': 'c8839177d1a5605aa60abe69db95c84183f0eebe',
                    'new': 'eed8df7f1400a95cdf5a87ddb947e7d9c5a19cef',
                },
            },
            meta_encoding='latin1',
            diff=(
                b'--- /file1\n'
                b'+++ /file1\n'
                b'@@ -498,7 +498,7 @@\n'
                b' ... diff content\n'
            ))

        self.assertEqual(diffx1, diffx2)

    def test_ne(self):
        """Testing DiffX.__ne__"""
        diffx1 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32')

        diffx2 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16')

        self.assertNotEqual(diffx1, diffx2)

    def test_ne_with_subsection(self):
        """Testing DiffX.__ne__ with subsection not equal"""
        diffx1 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32')
        diffx1.add_change(
            preamble='test',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.MARKDOWN,
            meta={
                'author': 'Test User <test@example.com>',
                'committer': 'Test User <test@example.com>',
                'committer date': '2021-06-02T13:12:06-07:00',
                'date': '2021-06-01T19:26:31-07:00',
                'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
            },
            meta_encoding='utf-8')

        diffx2 = DiffX(
            encoding='utf-16',
            preamble='This is the file-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-32')
        diffx2.add_change(
            preamble='test',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.MARKDOWN,
            meta={},
            meta_encoding='utf-8')

        self.assertNotEqual(diffx1, diffx2)

    def _check_result(self, diffx_file, expected_result,
                      line_endings=LineEndings.UNIX):
        """Check the byte content of a DiffX file.

        This will write the file and then check that it matches the expected
        result, load the file back in, and compare the resulting objects.

        Args:
            diffx_file (pydiffx.dom.DiffX):
                The DiffX file object to compare.

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
        data = diffx_file.to_bytes()

        self.assertMultiLineBytesEqual(data, expected_result,
                                       line_endings=line_endings)


class DiffXChangeSectionTests(BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffXChangeSection."""

    section_cls = DiffXChangeSection

    def test_init_with_options(self):
        """Testing DiffXChangeSection.__init__ with options"""
        section = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)

        self.assertEqual(section.encoding, 'utf-8')
        self.assertEqual(section.options, {
            'encoding': 'utf-8',
        })

        self.assertEqual(section.preamble,
                         'This is the change-level preamble.')
        self.assertEqual(section.preamble_encoding, 'ascii')
        self.assertEqual(section.preamble_indent, 2)
        self.assertEqual(section.preamble_line_endings, LineEndings.DOS)
        self.assertEqual(section.preamble_mimetype, PreambleMimeType.PLAIN)
        self.assertEqual(section.preamble_section.options, {
            'encoding': 'ascii',
            'indent': 2,
            'line_endings': LineEndings.DOS,
            'mimetype': PreambleMimeType.PLAIN,
        })

        self.assertEqual(section.meta, {
            'key': 'value',
        })
        self.assertEqual(section.meta_encoding, 'utf-16')
        self.assertEqual(section.meta_format, MetaFormat.JSON)
        self.assertEqual(section.meta_section.options, {
            'encoding': 'utf-16',
            'format': MetaFormat.JSON,
        })

    def test_init_with_invalid_options(self):
        """Testing DiffXChangeSection.__init__ with invalid options"""
        message = '"invalid_option" is not a valid option or content section'

        with self.assertRaisesMessage(DiffXUnknownOptionError, message):
            DiffXChangeSection(invalid_option=1)

    def test_meta(self):
        """Testing DiffXChangeSection.meta"""
        self.run_content_test({'key': 'value'},
                              attr_name='meta',
                              expected_default={})

    def test_generate_stats(self):
        """Testing DiffXChangeSection.generate_stats"""
        section = DiffXChangeSection()
        section.add_file(diff=(
            b'git --diff a/file b/file\n'
            b'index abc1234...def5678 100644\n'
            b'--- a/file\n'
            b'+++ b/file\n'
            b'@@ -10,7 +12,10 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'@@ -23,7 +40,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-- \n'
            b'2.9.2\n'
        ))
        section.add_file(diff=(
            b'--- a/file\t(revision 1)\n'
            b'+++ b/file\t(revision 2)\n'
            b'@@ -5,9 +5,12 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'-# old line\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))
        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'files': 2,
                'deletions': 5,
                'insertions': 11,
                'lines changed': 16,
            })

    def test_generate_stats_merges(self):
        """Testing DiffXChangeSection.generate_stats merges with existing
        stats
        """
        section = DiffXChangeSection(
            meta={
                'stats': {
                    'special': 123,
                },
            })

        section.add_file(diff=(
            b'git --diff a/file b/file\n'
            b'index abc1234...def5678 100644\n'
            b'--- a/file\n'
            b'+++ b/file\n'
            b'@@ -10,7 +12,10 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'@@ -23,7 +40,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-- \n'
            b'2.9.2\n'
        ))
        section.add_file(diff=(
            b'--- a/file\t(revision 1)\n'
            b'+++ b/file\t(revision 2)\n'
            b'@@ -5,9 +5,12 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'-# old line\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))
        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'files': 2,
                'deletions': 5,
                'insertions': 11,
                'lines changed': 16,
                'special': 123,
            })

    def test_generate_stats_with_parse_error(self):
        """Testing DiffXChangeSection.generate_stats with diff hunk parse
        error
        """
        section = DiffXChangeSection()
        section.add_file(diff=(
            b'--- a/file\t(revision 1)\n'
            b'+++ b/file\t(revision 2)\n'
            b'@@ -5,9 +5,12 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
            b'-# old line\n'
            b'-# old line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b'+# new line\n'
            b' #\n'
            b' #\n'
            b' #\n'
        ))

        # This one contains the parse error (hunk is truncated).
        section.add_file(diff=(
            b'--- file1\n'
            b'+++ file2\n'
            b'@@ -109,10 +129,10 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'-# old line\n'
        ))

        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'files': 2,
                'deletions': 3,
                'insertions': 6,
                'lines changed': 9,
            })

    def test_repr(self):
        """Testing DiffXChangeSection.__repr__"""
        diffx = DiffX()
        change = diffx.add_change(encoding='utf-8')

        self.assertEqual(
            repr(change),
            '<DiffXChangeSection(level=1, options=%r)>'
            % {'encoding': 'utf-8'})

    def test_eq(self):
        """Testing DiffXChangeSection.__eq__"""
        section1 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)
        section1.add_file(
            meta={
                'path': {
                    'old': 'message.py',
                    'new': 'message2.py',
                },
            },
            diff=b'... diff')

        section2 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)
        section2.add_file(
            meta={
                'path': {
                    'old': 'message.py',
                    'new': 'message2.py',
                },
            },
            diff=b'... diff')

        self.assertEqual(section1, section2)

    def test_ne(self):
        """Testing DiffXChangeSection.__ne__"""
        section1 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)

        section2 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.UNIX,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)

        self.assertNotEqual(section1, section2)

    def test_ne_with_subsection(self):
        """Testing DiffXChangeSection.__ne__ with subsection not equal"""
        section1 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)
        section1.add_file(
            meta={
                'path': {
                    'old': 'message.py',
                    'new': 'message2.py',
                },
            },
            diff=b'... diff')

        section2 = DiffXChangeSection(
            encoding='utf-8',
            preamble='This is the change-level preamble.',
            preamble_encoding='ascii',
            preamble_indent=2,
            preamble_line_endings=LineEndings.DOS,
            preamble_mimetype=PreambleMimeType.PLAIN,
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON)
        section2.add_file(
            meta={},
            diff=b'... diff')

        self.assertNotEqual(section1, section2)


class DiffXFileSectionTests(kgb.SpyAgency, BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffXFileSection."""

    section_cls = DiffXFileSection

    def test_init_with_options(self):
        """Testing DiffXFileSection.__init__ with options"""
        section = DiffXFileSection(
            encoding='utf-8',
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON,
            diff=b'... diff',
            diff_encoding='latin1',
            diff_line_endings=LineEndings.UNIX,
            diff_type=DiffType.TEXT)

        self.assertEqual(section.encoding, 'utf-8')
        self.assertEqual(section.options, {
            'encoding': 'utf-8',
        })

        self.assertEqual(section.meta, {
            'key': 'value',
        })
        self.assertEqual(section.meta_encoding, 'utf-16')
        self.assertEqual(section.meta_format, MetaFormat.JSON)
        self.assertEqual(section.meta_section.options, {
            'encoding': 'utf-16',
            'format': MetaFormat.JSON,
        })

        self.assertEqual(section.diff, b'... diff')
        self.assertEqual(section.diff_encoding, 'latin1')
        self.assertEqual(section.diff_line_endings, LineEndings.UNIX)
        self.assertEqual(section.diff_type, DiffType.TEXT)
        self.assertEqual(section.diff_section.options, {
            'encoding': 'latin1',
            'line_endings': LineEndings.UNIX,
            'type': DiffType.TEXT,
        })

    def test_init_with_invalid_options(self):
        """Testing DiffXFileSection.__init__ with invalid options"""
        message = '"invalid_option" is not a valid option or content section'

        with self.assertRaisesMessage(DiffXUnknownOptionError, message):
            DiffXFileSection(invalid_option=1)

    def test_meta(self):
        """Testing DiffXFileSection.meta"""
        self.run_content_test({'key': 'value'},
                              attr_name='meta',
                              expected_default={})

    def test_diff(self):
        """Testing DiffXFileSection.diff"""
        self.run_content_test(b'...diff',
                              attr_name='diff')

    def test_generate_stats(self):
        """Testing DiffXFileSection.generate_stats"""
        section = DiffXFileSection(
            diff=(
                b'git --diff a/file b/file\n'
                b'index abc1234...def5678 100644\n'
                b'--- a/file\n'
                b'+++ b/file\n'
                b'@@ -10,7 +12,10 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'@@ -23,7 +40,7 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-- \n'
                b'2.9.2\n'
            ))
        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'deletions': 2,
                'insertions': 5,
                'lines changed': 7,
            })

    def test_generate_stats_merges(self):
        """Testing DiffXFileSection.generate_stats merges with existing
        stats
        """
        section = DiffXFileSection(
            meta={
                'stats': {
                    'special': 123,
                },
            },
            diff=(
                b'git --diff a/file b/file\n'
                b'index abc1234...def5678 100644\n'
                b'--- a/file\n'
                b'+++ b/file\n'
                b'@@ -10,7 +12,10 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'@@ -23,7 +40,7 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-- \n'
                b'2.9.2\n'
            ))
        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'deletions': 2,
                'insertions': 5,
                'lines changed': 7,
                'special': 123,
            })

    def test_generate_stats_with_line_endings(self):
        """Testing DiffXFileSection.generate_stats merges with
        diff_line_endings set
        """
        section = DiffXFileSection(
            diff_line_endings=LineEndings.UNIX,
            diff=(
                b'misleading line ending: \r\n'
                b'git --diff a/file b/file\n'
                b'index abc1234...def5678 100644\n'
                b'--- a/file\n'
                b'+++ b/file\n'
                b'@@ -10,7 +12,10 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'@@ -23,7 +40,7 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
                b'+# new line\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-- \n'
                b'2.9.2\n'
            ))
        section.generate_stats()

        self.assertEqual(
            section.meta.get('stats'),
            {
                'deletions': 2,
                'insertions': 5,
                'lines changed': 7,
            })

    def test_generate_stats_with_no_diff(self):
        """Testing DiffXFileSection.generate_stats with no diff"""
        section = DiffXFileSection()
        section.generate_stats()

        self.assertNotIn('stats', section.meta)

    def test_generate_stats_with_binary_diff(self):
        """Testing DiffXFileSection.generate_stats with
        diff_type=DiffType.BINARY
        """
        section = DiffXFileSection(
            diff_type=DiffType.BINARY,
            diff=b'Binary file has changed')
        section.generate_stats()

        self.assertNotIn('stats', section.meta)

    def test_generate_stats_with_parse_error(self):
        """Testing DiffXFileSection.generate_stats with diff hunk parse error
        """
        self.spy_on(dom_objects_logger.error)

        section = DiffXFileSection(
            diff=(
                b'--- file1\n'
                b'+++ file2\n'
                b'@@ -109,10 +129,10 @@\n'
                b' #\n'
                b' #\n'
                b' #\n'
                b'-# old line\n'
            ))
        section.generate_stats()

        self.assertIsNone(section.meta.get('stats'))
        self.assertSpyCalledWith(
            dom_objects_logger.error,
            'Error parsing diff hunks for %r: %s',
            section,
            MalformedHunkError(
                line=b'-# old line',
                line_num=7,
                msg=(
                    'Unexpected end of file when processing the diff hunk '
                    'on line 7'
                )))

    def test_repr(self):
        """Testing DiffXFileSection.__repr__"""
        diffx = DiffX()
        change = diffx.add_change()
        file = change.add_file(encoding='utf-16')

        self.assertEqual(
            repr(file),
            '<DiffXFileSection(level=2, options=%r)>'
            % {'encoding': 'utf-16'})

    def test_eq(self):
        """Testing DiffXFileSection.__eq__"""
        section1 = DiffXFileSection(
            encoding='utf-8',
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON,
            diff=b'... diff',
            diff_encoding='latin1',
            diff_line_endings=LineEndings.UNIX,
            diff_type=DiffType.TEXT)

        section2 = DiffXFileSection(
            encoding='utf-8',
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON,
            diff=b'... diff',
            diff_encoding='latin1',
            diff_line_endings=LineEndings.UNIX,
            diff_type=DiffType.TEXT)

        self.assertEqual(section1, section2)

    def test_ne(self):
        """Testing DiffXFileSection.__ne__"""
        section1 = DiffXFileSection(
            encoding='utf-8',
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON,
            diff=b'... diff',
            diff_encoding='latin1',
            diff_line_endings=LineEndings.UNIX,
            diff_type=DiffType.TEXT)

        section2 = DiffXFileSection(
            encoding='utf-8',
            meta={
                'key': 'value',
            },
            meta_encoding='utf-16',
            meta_format=MetaFormat.JSON,
            diff=b'... diff',
            diff_encoding='utf-8',
            diff_line_endings=LineEndings.UNIX,
            diff_type=DiffType.TEXT)

        self.assertNotEqual(section1, section2)


class DiffXFileDiffSectionTests(BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffXFileDiffSection."""

    section_cls = DiffXFileDiffSection

    def test_init_with_options(self):
        """Testing DiffXFileDiffSection.__init__ with options"""
        section = DiffXFileDiffSection(
            content=b'... diff',
            encoding='utf-8',
            line_endings=LineEndings.UNIX,
            type=DiffType.BINARY)

        self.assertEqual(section.content, b'... diff')
        self.assertEqual(section.encoding, 'utf-8')
        self.assertEqual(section.line_endings, LineEndings.UNIX)
        self.assertEqual(section.type, DiffType.BINARY)
        self.assertEqual(section.options, {
            'encoding': 'utf-8',
            'line_endings': LineEndings.UNIX,
            'type': DiffType.BINARY,
        })

    def test_init_with_invalid_options(self):
        """Testing DiffXFileDiffSection.__init__ with invalid options"""
        message = '"invalid_option" is not a valid option or content section'

        with self.assertRaisesMessage(DiffXUnknownOptionError, message):
            DiffXFileDiffSection(invalid_option=1)

    def test_content(self):
        """Testing DiffXFileDiffSection.content"""
        self.run_content_test(b'test')

    def test_content_with_invalid_type(self):
        """Testing DiffXFileDiffSection.content with invalid typw"""
        self.run_invalid_content_type_test(content='test',
                                           expected_type=bytes)

    def test_encoding(self):
        """Testing DiffXFileDiffSection.encoding"""
        self.run_option_test('encoding', 'utf-8')

    def test_encoding_with_invalid_type(self):
        """Testing DiffXFileDiffSection.encoding with invalid type"""
        self.run_invalid_option_type_test(option_name='encoding',
                                          value=123,
                                          expected_type=six.text_type)

    def test_line_endings_with_dos(self):
        """Testing DiffXFileDiffSection.line_endings with dos"""
        self.run_option_test('line_endings', LineEndings.DOS)

    def test_line_endings_with_unix(self):
        """Testing DiffXFileDiffSection.line_endings with unix"""
        self.run_option_test('line_endings', LineEndings.UNIX)

    def test_line_endings_with_invalid_value(self):
        """Testing DiffXFileDiffSection.line_endings with invalid value"""
        self.run_invalid_option_value_test(
            option_name='line_endings',
            value='xxx',
            expected_choices=LineEndings.VALID_VALUES)

    def test_line_endings_with_invalid_type(self):
        """Testing DiffXFileDiffSection.line_endings with invalid type"""
        self.run_invalid_option_type_test(option_name='line_endings',
                                          value=123,
                                          expected_type=six.text_type)

    def test_type_with_dos(self):
        """Testing DiffXFileDiffSection.type with binary"""
        self.run_option_test('type', DiffType.BINARY)

    def test_type_with_unix(self):
        """Testing DiffXFileDiffSection.type with text"""
        self.run_option_test('type', DiffType.TEXT)

    def test_type_with_invalid_value(self):
        """Testing DiffXFileDiffSection.type with invalid value"""
        self.run_invalid_option_value_test(
            option_name='type',
            value='xxx',
            expected_choices=DiffType.VALID_VALUES)

    def test_type_with_invalid_type(self):
        """Testing DiffXFileDiffSection.type with invalid type"""
        self.run_invalid_option_type_test(option_name='type',
                                          value=123,
                                          expected_type=six.text_type)

    def test_eq(self):
        """Testing DiffXFileDiffSection.__eq__"""
        section1 = DiffXFileDiffSection(
            content=b'... diff',
            encoding='utf-8',
            line_endings=LineEndings.UNIX,
            type=DiffType.BINARY)

        section2 = DiffXFileDiffSection(
            content=b'... diff',
            encoding='utf-8',
            line_endings=LineEndings.UNIX,
            type=DiffType.BINARY)

        self.assertEqual(section1, section2)

    def test_ne(self):
        """Testing DiffXFileDiffSection.__ne__"""
        section1 = DiffXFileDiffSection(
            content=b'... diff',
            encoding='utf-8',
            line_endings=LineEndings.UNIX,
            type=DiffType.BINARY)

        section2 = DiffXFileDiffSection(
            content=b'... diff',
            encoding='utf-8',
            line_endings=LineEndings.UNIX,
            type=DiffType.TEXT)

        self.assertNotEqual(section1, section2)


class DiffXMetaSectionTests(BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffXMetaSection."""

    section_cls = DiffXMetaSection

    def test_init_with_options(self):
        """Testing DiffXMetaSection.__init__ with options"""
        section = DiffXMetaSection(
            content={'key': 'value'},
            encoding='utf-8',
            format=MetaFormat.JSON)
        self.assertEqual(section.content, {
            'key': 'value',
        })
        self.assertEqual(section.encoding, 'utf-8')
        self.assertEqual(section.format, MetaFormat.JSON)
        self.assertEqual(section.options, {
            'encoding': 'utf-8',
            'format': MetaFormat.JSON,
        })

    def test_init_with_invalid_options(self):
        """Testing DiffXMetaSection.__init__ with invalid options"""
        message = '"invalid_option" is not a valid option or content section'

        with self.assertRaisesMessage(DiffXUnknownOptionError, message):
            DiffXMetaSection(invalid_option=1)

    def test_content(self):
        """Testing DiffXMetaSection.content"""
        self.run_content_test(
            {
                'key': 'value',
            },
            expected_default={})

    def test_content_with_invalid_type(self):
        """Testing DiffXMetaSection.content with invalid typw"""
        self.run_invalid_content_type_test(content='invalid',
                                           expected_type=dict)

    def test_encoding(self):
        """Testing DiffXMetaSection.encoding"""
        self.run_option_test('encoding', 'utf-8')

    def test_encoding_with_invalid_type(self):
        """Testing DiffXMetaSection.encoding with invalid type"""
        self.run_invalid_option_type_test(option_name='encoding',
                                          value=123,
                                          expected_type=six.text_type)

    def test_format(self):
        """Testing DiffXMetaSection.format"""
        self.run_option_test(option_name='format',
                             value=MetaFormat.JSON,
                             expected_default=MetaFormat.JSON)

    def test_format_with_invalid_value(self):
        """Testing DiffXMetaSection.format with invalid value"""
        self.run_invalid_option_value_test(
            option_name='format',
            value='xxx',
            expected_choices=MetaFormat.VALID_VALUES)

    def test_format_with_invalid_type(self):
        """Testing DiffXMetaSection.format with invalid type"""
        self.run_invalid_option_type_test(option_name='format',
                                          value=123,
                                          expected_type=six.text_type)

    def test_eq(self):
        """Testing DiffXMetaSection.__eq__"""
        section1 = DiffXMetaSection(
            content={'key': 'value'},
            encoding='utf-8',
            format=MetaFormat.JSON)

        section2 = DiffXMetaSection(
            content={'key': 'value'},
            encoding='utf-8',
            format=MetaFormat.JSON)

        self.assertEqual(section1, section2)

    def test_ne(self):
        """Testing DiffXMetaSection.__ne__"""
        section1 = DiffXMetaSection(
            content={'key': 'value'},
            encoding='utf-8',
            format=MetaFormat.JSON)

        section2 = DiffXMetaSection(
            content={'key': None},
            encoding='utf-8',
            format=MetaFormat.JSON)

        self.assertNotEqual(section1, section2)


class DiffXPreambleSectionTests(BaseSectionTestCase):
    """Unit tests for pydiffx.dom.objects.DiffXPreambleSection."""

    section_cls = DiffXPreambleSection

    def test_init_with_options(self):
        """Testing DiffXPreambleSection.__init__ with options"""
        section = DiffXPreambleSection(
            content='test content',
            encoding='utf-16',
            indent=2,
            line_endings=LineEndings.UNIX,
            mimetype=PreambleMimeType.PLAIN)
        self.assertEqual(section.content, 'test content')
        self.assertEqual(section.encoding, 'utf-16')
        self.assertEqual(section.indent, 2)
        self.assertEqual(section.line_endings, LineEndings.UNIX)
        self.assertEqual(section.mimetype, PreambleMimeType.PLAIN)
        self.assertEqual(section.options, {
            'encoding': 'utf-16',
            'indent': 2,
            'line_endings': LineEndings.UNIX,
            'mimetype': PreambleMimeType.PLAIN,
        })

    def test_init_with_invalid_options(self):
        """Testing DiffXPreambleSection.__init__ with invalid options"""
        message = '"invalid_option" is not a valid option or content section'

        with self.assertRaisesMessage(DiffXUnknownOptionError, message):
            DiffXPreambleSection(invalid_option=1)

    def test_content(self):
        """Testing DiffXPreambleSection.content"""
        self.run_content_test('test content')

    def test_content_with_invalid_type(self):
        """Testing DiffXPreambleSection.content with invalid typw"""
        self.run_invalid_content_type_test(content=123,
                                           expected_type=six.text_type)

    def test_encoding(self):
        """Testing DiffXPreambleSection.encoding"""
        self.run_option_test('encoding', 'utf-8')

    def test_encoding_with_invalid_type(self):
        """Testing DiffXPreambleSection.encoding with invalid type"""
        self.run_invalid_option_type_test(option_name='encoding',
                                          value=123,
                                          expected_type=six.text_type)

    def test_indent(self):
        """Testing DiffXPreambleSection.indent"""
        self.run_option_test('indent', 4)

    def test_indent_with_invalid_type(self):
        """Testing DiffXPreambleSection.indent with invalid type"""
        self.run_invalid_option_type_test(option_name='indent',
                                          value='xxx',
                                          expected_type=int)

    def test_line_endings_with_dos(self):
        """Testing DiffXPreambleSection.line_endings with dos"""
        self.run_option_test('line_endings', LineEndings.DOS)

    def test_line_endings_with_unix(self):
        """Testing DiffXPreambleSection.line_endings with unix"""
        self.run_option_test('line_endings', LineEndings.UNIX)

    def test_line_endings_with_invalid_value(self):
        """Testing DiffXPreambleSection.line_endings with invalid value"""
        self.run_invalid_option_value_test(
            option_name='line_endings',
            value='xxx',
            expected_choices=LineEndings.VALID_VALUES)

    def test_line_endings_with_invalid_type(self):
        """Testing DiffXPreambleSection.line_endings with invalid type"""
        self.run_invalid_option_type_test(option_name='line_endings',
                                          value=123,
                                          expected_type=six.text_type)

    def test_mimetype_with_plain(self):
        """Testing DiffXPreambleSection.mimetype with text/plain"""
        self.run_option_test('mimetype', PreambleMimeType.PLAIN)

    def test_mimetype_with_markdown(self):
        """Testing DiffXPreambleSection.mimetype with text/markdown"""
        self.run_option_test('mimetype', PreambleMimeType.MARKDOWN)

    def test_mimetype_with_invalid_value(self):
        """Testing DiffXPreambleSection.mimetype with invalid value"""
        self.run_invalid_option_value_test(
            option_name='mimetype',
            value='image/png',
            expected_choices=PreambleMimeType.VALID_VALUES)

    def test_mimetype_with_invalid_type(self):
        """Testing DiffXPreambleSection.mimetype with invalid type"""
        self.run_invalid_option_type_test(option_name='mimetype',
                                          value=123,
                                          expected_type=six.text_type)

    def test_eq(self):
        """Testing DiffXPreambleSection.__eq__"""
        section1 = DiffXPreambleSection(
            content='test content',
            encoding='utf-16',
            indent=2,
            line_endings=LineEndings.UNIX,
            mimetype=PreambleMimeType.PLAIN)

        section2 = DiffXPreambleSection(
            content='test content',
            encoding='utf-16',
            indent=2,
            line_endings=LineEndings.UNIX,
            mimetype=PreambleMimeType.PLAIN)

        self.assertEqual(section1, section2)

    def test_ne(self):
        """Testing DiffXPreambleSection.__ne__"""
        section1 = DiffXPreambleSection(
            content='test content',
            encoding='utf-16',
            indent=2,
            line_endings=LineEndings.UNIX,
            mimetype=PreambleMimeType.PLAIN)

        section2 = DiffXPreambleSection(
            content='test content',
            encoding='utf-8',
            indent=2,
            line_endings=LineEndings.UNIX,
            mimetype=PreambleMimeType.PLAIN)

        self.assertNotEqual(section1, section2)
