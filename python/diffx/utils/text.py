"""Utilities for processing text."""

from __future__ import unicode_literals

from diffx.options import LineEndings


#: A mapping of newline format types to character sequences.
#:
#: This contains only formats that are allowed in the ``line_endings=`` option
#: in DiffX content sections.
#:
#: Type:
#:     dict
NEWLINE_FORMATS = {
    LineEndings.DOS: b'\r\n',
    LineEndings.UNIX: b'\n',
}


def split_lines(data, newline=None, keep_ends=False):
    """Split data along newline boundaries.

    This can either auto-detect the newline format (using Python's default
    logic), or split along specified newline characters.

    Args:
        data (bytes):
            The data to split.

        newline (bytes, optional):
            The newline character(s) used to split the data into lines.
            If not provided, newlines will be auto-detected based on content.

        keep_ends (bool, optional):
            Whether to keep the line endings in the resulting lines.

    Returns:
        list of bytes:
        The split list of lines.
    """
    if newline is None:
        lines = data.splitlines(keep_ends)
    else:
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

    return lines


def guess_line_endings(text):
    """Return the line endings that appear to be used for text.

    This will check the first line of content and see if it appears to be
    DOS or UNIX line endings.

    If there are no newlines, UNIX line endings are assumed.

    Args:
        text (bytes):
            The text to guess line endings from.

    Returns:
        unicode:
        The guessed line endings type.
    """
    assert isinstance(text, bytes)

    i = text.find(b'\n')

    if i != -1 and text[:i + 1].endswith(NEWLINE_FORMATS[LineEndings.DOS]):
        return LineEndings.DOS

    # This should either be UNIX newlines, or the content may
    # be a single line without a newline. Either way, we'll
    # want to use UNIX newlines here.
    return LineEndings.UNIX
