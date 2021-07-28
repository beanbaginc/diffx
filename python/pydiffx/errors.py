"""Common errors for parsing and generating diffs."""

from __future__ import unicode_literals

import six


class BaseDiffXError(Exception):
    """Base class for all DiffX errors."""


class DiffXParseError(BaseDiffXError):
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


class DiffXSectionOrderError(BaseDiffXError):
    """An error with the order of a section within the DiffX file."""


class DiffXContentError(BaseDiffXError):
    """An error with content for a section."""


class DiffXUnknownOptionError(BaseDiffXError):
    """An option name is unknown for a given section."""


class DiffXOptionValueError(BaseDiffXError):
    """An error with a value for an option."""


class DiffXOptionValueChoiceError(DiffXOptionValueError):
    """An error with the choice for a value for an option."""

    def __init__(self, option, value, choices):
        """Initialize the error.

        Args:
            option (unicode):
                The name of the option.

            value (object):
                The value that was chosen.

            choices (list of unicode):
                The list of values considered valid.
        """
        super(DiffXOptionValueChoiceError, self).__init__(
            '"%(value)s" is not a supported value for %(option)s. Expected '
            'one of: %(choices)s'
            % {
                'option': option,
                'value': value,
                'choices': ', '.join(sorted(choices)),
            })


class MalformedHunkError(Exception):
    """Error with the contents of a hunk in a patch.

    Attributes:
        line (bytes):
            The contents of the line triggering the error.

        line_num (int):
            The 1-based line number where the error occurred.
    """

    def __init__(self, line, line_num, msg=None):
        """Initialize the error.

        Args:
            line (bytes):
                The contents of the line triggering the error.

            line_num (int):
                The 1-based line number where the error occurred.

            msg (unicode, optional):
                An optional error message to display instead of the default
                message. This may contain ``line`` and ``line_num`` format
                strings (built for ``%``-based formatting).
        """
        if msg is None:
            msg = (
                'Malformed content in the diff hunk on line %(line_num)s: '
                '%(line)r'
            )

        super(MalformedHunkError, self).__init__(
            msg % {
                'line': line,
                'line_num': line_num,
            })

        self.line = line
        self.line_num = line_num

    def __eq__(self, other):
        """Return whether this exception equals another.

        Args:
            other (object):
                The object to compare to.

        Returns:
            bool:
            ``True`` if the objectws are equal. ``False`` if they are not.
        """
        return (type(self) is type(other) and
                self.line == other.line and
                self.line_num == other.line_num and
                six.text_type(self) == six.text_type(other))
