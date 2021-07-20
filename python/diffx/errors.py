"""Common errors for parsing and generating diffs."""

from __future__ import unicode_literals


class DiffXParseError(Exception):
    """An error when parsing a DiffX file.

    Parse errors contain information on the line (and sometimes the column)
    causing parsing to fail, along with an error message.

    Attributes:
        column (int):
            The 0-based column number where the parse error occurred. This
            may be ``None`` for some parse errors.

        linenum (int):
            The 0-based line number where the parse error occurred.
    """

    def __init__(self, msg, linenum, column=None):
        """Initialize the error.

        Args:
            msg (unicode):
                An error message explaining why the file could not be parsed.

            linenum (int):
                The 0-based line number where the parse error occurred.

            column (int, optional):
                The 0-based column number where the parse error occurred.
        """
        prefix = 'Error on line %d' % (linenum + 1)

        if column is not None:
            prefix = '%s, column %d' % (prefix, column + 1)

        super(DiffXParseError, self).__init__('%s: %s' % (prefix, msg))

        self.linenum = linenum
        self.column = column
