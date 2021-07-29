"""Unit tests for pydiffx.utils.text."""

from __future__ import unicode_literals

from pydiffx.options import LineEndings
from pydiffx.tests.testcases import TestCase
from pydiffx.utils.text import get_newline_for_type


class GetNewlineForTypeTests(TestCase):
    """Unit tests for pydiffx.utils.text.get_newline_for_type."""

    def test_with_dos(self):
        """Testing get_newline_for_type with "dos" line endings"""
        self.assertEqual(get_newline_for_type(LineEndings.DOS),
                         b'\r\n')

    def test_with_unix(self):
        """Testing get_newline_for_type with "unix" line endings"""
        self.assertEqual(get_newline_for_type(LineEndings.UNIX),
                         b'\n')

    def test_with_invalid_line_endings(self):
        """Testing get_newline_for_type with invalid value for line endings"""
        message = (
            'Unsupported value "xxx" for line_endings. Expected one of: '
            'dos, unix'
        )

        with self.assertRaisesMessage(ValueError, message):
            get_newline_for_type('xxx')

    def test_with_encoding(self):
        """Testing get_newline_for_type with encoding"""
        self.assertEqual(get_newline_for_type(LineEndings.DOS,
                                              encoding='utf-32'),
                         b'\r\x00\x00\x00\n\x00\x00\x00')

    def test_with_encoding_invalid(self):
        """Testing get_newline_for_type with invalid encoding"""
        message = 'unknown encoding: xxx-invalid'

        with self.assertRaisesMessage(LookupError, message):
            get_newline_for_type(LineEndings.DOS,
                                 encoding='xxx-invalid')
