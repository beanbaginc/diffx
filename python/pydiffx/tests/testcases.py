"""Unit tests for pydiffx.reader."""

from __future__ import unicode_literals

import re
import unittest
from contextlib import contextmanager

from pydiffx.utils.text import NEWLINE_FORMATS, split_lines


class TestCase(unittest.TestCase):
    """Base class for DiffX unit tests."""

    maxDiff = 10000

    ws_re = re.compile(r'\s+')

    def shortDescription(self):
        """Return the description of the current test.

        This changes the default behavior to replace all newlines with spaces,
        allowing a test description to span lines. It should still be kept
        short, though.

        Returns:
            unicode:
            The normalized test description.
        """
        doc = self._testMethodDoc

        if doc is not None:
            doc = doc.split('\n\n', 1)[0]
            doc = self.ws_re.sub(' ', doc).strip()

        return doc

    def assertMultiLineBytesEqual(self, first, second, line_endings='unix'):
        """Assert that lines in two byte strings are equal.

        Args:
            first (bytes):
                The first byte string to compare.

            second (bytes):
                The second byte string to compare.

            line_endings (unicode, optional):
                The line ending time used to split the lines.

        Raises:
            AssertionError:
                The lines in the strings were not equal.
        """
        if first != second:
            newline = NEWLINE_FORMATS[line_endings].encode('ascii')

            self.assertEqual(
                split_lines(first,
                            newline=newline,
                            keep_ends=True),
                split_lines(second,
                            newline=newline,
                            keep_ends=True))

    @contextmanager
    def assertRaisesMessage(self, exception, message):
        with self.assertRaisesRegexp(exception, re.escape(message)):
            yield
