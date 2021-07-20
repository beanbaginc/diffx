"""Utilities for processing text."""

from __future__ import unicode_literals

import codecs

from diffx.options import LineEndings


#: A mapping of newline format types to character sequences.
#:
#: This contains only formats that are allowed in the ``line_endings=`` option
#: in DiffX content sections.
#:
#: Type:
#:     dict
NEWLINE_FORMATS = {
    LineEndings.DOS: '\r\n',
    LineEndings.UNIX: '\n',
}


#: A mapping of encodings to possible BOM markers.
BOMS = {
    'utf-8': (codecs.BOM_UTF8,),
    'utf-16': (codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE),
    'utf-16-le': (codecs.BOM_UTF16_LE,),
    'utf-16-be': (codecs.BOM_UTF16_BE,),
    'utf-32': (codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE),
    'utf-32-le': (codecs.BOM_UTF32_LE,),
    'utf-32-be': (codecs.BOM_UTF32_BE,),
}


def split_lines(data, newline, keep_ends=False):
    """Split data along newline boundaries.

    This differs from :py:meth:`str.splitlines` in that it will split across
    a specific newline boundary, rather than against any sequence of newline
    characters.

    Args:
        data (bytes):
            The data to split.

        newline (bytes):
            The newline character(s) used to split the data into lines.

        keep_ends (bool, optional):
            Whether to keep the line endings in the resulting lines.

    Returns:
        list of bytes:
        The split list of lines.
    """
    assert data
    assert newline

    lines = data.split(newline)

    if keep_ends:
        lines = [
            b'%s%s' % (_line, newline)
            for _line in lines
        ]

    # If the very last line of the original text had a newline, then we're
    # going to end up with too many lines at the end. This is because
    # the split() above would have added a final blank entry. Get rid of
    # it.
    if data.endswith(newline):
        lines.pop()
    elif keep_ends:
        lines[-1] = lines[-1][:-len(newline)]

    return lines


def guess_line_endings(text, encoding=None):
    """Return the line endings that appear to be used for text.

    This will check the first line of content and see if it appears to be
    DOS or UNIX line endings.

    If there are no newlines, UNIX line endings are assumed.

    Args:
        text (bytes or unicode):
            The text to guess line endings from.

        encoding (unicode, optional):
            The encoding of the text, if it's a byte string.

    Returns:
        tuple:
        A 2-tuple of:

        1. The guessed line endings type (as a ``line_endings=`` option
           value).
        2. The line ending characters (in the same string type as ``text``).
    """
    unix_newline = NEWLINE_FORMATS[LineEndings.UNIX]
    dos_newline = NEWLINE_FORMATS[LineEndings.DOS]

    if isinstance(text, bytes):
        assert encoding
        unix_newline = strip_bom(unix_newline.encode(encoding),
                                 encoding)
        dos_newline = strip_bom(dos_newline.encode(encoding),
                                encoding)

    i = text.find(unix_newline)

    if i != -1 and text[:i + len(unix_newline)].endswith(dos_newline):
        return LineEndings.DOS, dos_newline
    else:
        # This should either be UNIX newlines, or the content may
        # be a single line without a newline. Either way, we'll
        # want to use UNIX newlines here.
        return LineEndings.UNIX, unix_newline


def strip_bom(data, encoding):
    """Strip a BOM from the beginning of a string.

    If the encoding is one that contains a BOM, and any version (such as
    Big Endian or Little Endian) of the BOM are present, they'll be stripped.

    Args:
        data (bytes):
            The byte string to strip a BOM from.

        encoding (unicode):
            The encoding of the byte string.

    Returns:
        bytes:
        The string, without any BOM markers.
    """
    boms = BOMS.get(encoding)

    if boms and data.startswith(boms):
        data = data[len(boms[0]):]

    return data
