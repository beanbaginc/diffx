"""Section-related definitions.

This is mostly useful internally for diff generation and parsing.
"""

from __future__ import unicode_literals


class Section(object):
    """Valid section IDs in a DiffX file."""

    #: The ID of the main DiffX section.
    MAIN = 'diffx'

    #: The ID of the main DiffX preamble section.
    MAIN_PREAMBLE = '.preamble'

    #: The ID of the main DiffX metadata section.
    MAIN_META = '.meta'

    #: The ID of a change section.
    CHANGE = '.change'

    #: The ID of a change's preamble section.
    CHANGE_PREAMBLE = '..preamble'

    #: The ID of a change's metadata section.
    CHANGE_META = '..meta'

    #: The ID of a file section.
    FILE = '..file'

    #: The ID of a file's metadata section.
    FILE_META = '...meta'

    #: The ID of a file's diff section.
    FILE_DIFF = '...diff'


#: A set of all preamble sections.
PREAMBLE_SECTIONS = {
    Section.MAIN_PREAMBLE,
    Section.CHANGE_PREAMBLE,
}


#: A set of all meta sections.
META_SECTIONS = {
    Section.MAIN_META,
    Section.CHANGE_META,
    Section.FILE_META,
}


#: A set of all content sections.
CONTENT_SECTIONS = PREAMBLE_SECTIONS | META_SECTIONS | {
    Section.FILE_DIFF,
}


#: A mapping of section IDs to sections that may appear next in the file.
VALID_SECTION_STATES = {
    Section.MAIN: {
        Section.MAIN_PREAMBLE,
        Section.MAIN_META,
        Section.CHANGE,
    },
    Section.MAIN_PREAMBLE: {
        Section.MAIN_META,
        Section.CHANGE,
    },
    Section.MAIN_META: {
        Section.CHANGE,
    },
    Section.CHANGE: {
        Section.CHANGE_PREAMBLE,
        Section.CHANGE_META,
        Section.FILE,
    },
    Section.CHANGE_PREAMBLE: {
        Section.CHANGE_META,
        Section.FILE,
    },
    Section.CHANGE_META: {
        Section.CHANGE,
        Section.FILE,
    },
    Section.FILE: {
        Section.FILE_META,
    },
    Section.FILE_META: {
        Section.CHANGE,
        Section.FILE_DIFF,
        Section.FILE,
    },
    Section.FILE_DIFF: {
        Section.CHANGE,
        Section.FILE,
    },
}
