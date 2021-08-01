"""Constants and utilities for options."""

from __future__ import unicode_literals


class DiffType(object):
    """Types available for a diff.

    These may be used in a diff section's ``diff_type`` option.
    """

    #: Text-based diffs.
    TEXT = 'text'

    #: Binary diffs.
    BINARY = 'binary'

    #: A set of values allowed for the diff_type option.
    VALID_VALUES = {
        BINARY,
        TEXT,
    }


class LineEndings(object):
    """Line ending types available for a content section.

    These may be used in a content section's ``line_endings`` option.
    """

    #: DOS (CRLF) line endings.
    DOS = 'dos'

    #: UNIX (LF) line endings.
    UNIX = 'unix'

    #: A set of values allowed for the line_endings option.
    VALID_VALUES = {
        DOS,
        UNIX,
    }


class MetaFormat(object):
    """Formats available for a meta section.

    These may be used in a meta section's ``format`` option.
    """

    #: JSON metadata.
    JSON = 'json'

    #: A set of values allowed for the format option.
    VALID_VALUES = {
        JSON,
    }


class PreambleMimeType(object):
    """Mimetypes available for a preamble section.

    These may be used in a preamble section's ``mimetype`` option.
    """

    #: Plain text.
    PLAIN = 'text/plain'

    #: Markdown text.
    MARKDOWN = 'text/markdown'

    #: A set of values allowed for the mimetype option.
    VALID_VALUES = {
        MARKDOWN,
        PLAIN,
    }


class SpecVersion(object):
    """Supported specification versions.

    These may be used as the DiffX ``version`` option.
    """

    #: The default version to write.
    DEFAULT_VERSION = '1.0'

    #: A set of values allowed for the version option.
    VALID_VALUES = {
        '1.0',
    }
