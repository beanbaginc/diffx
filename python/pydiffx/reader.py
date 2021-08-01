"""A streaming reader for DiffX files."""

from __future__ import unicode_literals

import io
import json
import os
import re

import six

from pydiffx.errors import DiffXParseError
from pydiffx.options import SpecVersion
from pydiffx.sections import (CONTENT_SECTIONS,
                              META_SECTIONS,
                              PREAMBLE_SECTIONS,
                              Section,
                              VALID_SECTION_STATES)
from pydiffx.utils.text import (NEWLINE_FORMATS,
                                get_newline_for_type,
                                guess_line_endings,
                                split_lines,
                                strip_bom)


class DiffXReader(object):
    """A streaming reader for DiffX files.

    This is a low-level interface for reading a DiffX file from an existing
    stream, such as an opened file handle or a web server response.

    Consumers can iterate through each section of the DiffX file, reading
    sections one-by-one and processing them. This can be used to process the
    the metadata on-the-fly without retaining the entirety of the file in
    memory, or to convert it into another data structure.

    See :py:meth:`iter_sections` for details on the information returned
    during iteration.
    """

    _HEADER_OPTION_KEY_RE = re.compile(br'[A-Za-z][A-Za-z0-9_-]*')
    _HEADER_OPTION_VALUE_RE = re.compile(br'[A-Za-z0-9_.-]+')
    _HEADER_RE = re.compile(
        br'^#(?P<section_id>(?P<level>\.{0,3})'
        br'(?P<section_type>diffx|preamble|meta|change|file|diff)):'
        br'(?: (?P<options>[^=\s,]+=[^\s,]+(?:, [^=\s,]+=[^\s,]+)*))?$'
    )

    def __init__(self, fp):
        """Initialize the reader.

        Args:
            fp (file or io.IOBase):
                The file pointer/stream to read from. This must be opened in
                binary (bytes) mode.
        """
        self._fp = fp
        self._linenum = 0
        self._file_newlines = None

    def __iter__(self):
        """Iterate through all sections of a DiffX file.

        This is a convenience wrapper around :py:meth:`iter_sections`. See
        that method for details.

        Yields:
            dict:
            Information on the section.

        Raises:
            pydiffx.errors.DiffXParseError:
                The file or a section was unable to be parsed. Information
                will be provided in the message and the instance's attributes.
        """
        return self.iter_sections()

    def iter_sections(self):
        """Iterate through all sections of a DiffX file.

        Each section and subsection will be parsed individually, returning the
        following data on each new section:

        ``level`` (:py:class:`int`):
            The 0-based section level (corresponding to the number of ``.``
            level indicator characters in the section ID).

        ``line`` (:py:class:`int`):
            The 0-based line number where the section starts.

        ``options`` (:py:class:`dict`):
            A dictionary of options found for the section.

        ``section`` (:py:class:`unicode`):
            The ID of the section. This corresponds to one of:

            * :py:attr:`~pydiffx.sections.Section.MAIN`
            * :py:attr:`~pydiffx.sections.Section.MAIN_PREAMBLE`
            * :py:attr:`~pydiffx.sections.Section.MAIN_META`
            * :py:attr:`~pydiffx.sections.Section.CHANGE`
            * :py:attr:`~pydiffx.sections.Section.CHANGE_PREAMBLE`
            * :py:attr:`~pydiffx.sections.Section.CHANGE_META`
            * :py:attr:`~pydiffx.sections.Section.FILE`
            * :py:attr:`~pydiffx.sections.Section.FILE_META`
            * :py:attr:`~pydiffx.sections.Section.FILE_DIFF`

        ``type`` (:py:class:`unicode`):
            The type of section (the ID in the file following the ``.``
            level indicator characters).

        Preamble sections will also contain:

        ``text`` (:py:class:`unicode`):
            The decoded text content of the preamble.

        Metadata sections will also contain:

        ``metadata`` (:py:class:`dict`):
            A dictionary containing all metadata for the section.

        Diff sections will also contain:

        ``diff`` (:py:class:`bytes` or :py:class:`unicode`):
            The diff content. If an encoding is specified, this will be
            decoded to a Unicode string. Otherwise, it will be a byte string.
            Callers must check for this.

        Note:
            If any given section fails to parse, an error will be raised and
            parsing will stop.

        Yields:
            dict:
            Information on the section.

        Raises:
            pydiffx.errors.DiffXParseError:
                The file or a section was unable to be parsed. Information
                will be provided in the message and the instance's attributes.
        """
        # We'll be keeping track of a few pieces of state.
        #
        # This is a list of sections considered valid at each iteration.
        # We start by looking for the main "#diffx:" section. Every section
        # we process will rebuild this list, using a list of valid sections
        # defined in VALID_SECTION_STATES, keyed off by the current section
        # ID.
        valid_sections = {Section.MAIN}

        # This is a stack of encodings. Every time we go up a container
        # section, or go to a container section at the same level, we'll pop
        # the last value off the stack. We'll then add the new encoding
        # (either defined on the section or inherited from a parent section)
        # onto the stack.
        encodings = [None]

        # The last container section level from a previous iteration.
        prev_container_level = 0

        while True:
            section = self._read_header(valid_sections=valid_sections)

            if section is None:
                # We've read the last section. We're done parsing.
                break

            level = section['level']
            linenum = section['line']
            options = section['options']
            section_id = section['section']

            if section_id in CONTENT_SECTIONS:
                # This is a content section.
                encoding = options.get('encoding', encodings[-1])

                try:
                    length = options['length']
                except KeyError:
                    raise DiffXParseError(
                        'Expected section "%s" to have a length option'
                        % section_id,
                        linenum=linenum)

                if section_id in PREAMBLE_SECTIONS:
                    # This is a preamble section.
                    #
                    # Read the content and decode it using the current
                    # encoding (defined either on this section or in a parent).
                    section['text'] = self._read_content(
                        length=length,
                        encoding=encoding,
                        indent=options.get('indent'),
                        line_endings=options.get('line_endings'))
                elif section_id in META_SECTIONS:
                    # This is a metadata section.
                    #
                    # Validate the format as JSON (either explicitly provided
                    # as format=json, or left off entirely).
                    metadata_format = options.get('format', 'json')

                    if metadata_format != 'json':
                        raise DiffXParseError(
                            'Unexpected metadata format "%(format)s". If the '
                            '"format" option is provided, it must be "json".'
                            % {
                                'format': metadata_format,
                            },
                            linenum=linenum)

                    # Read the content and decode it using the current encoding
                    # (defined either on this section or in a parent).
                    content = self._read_content(
                        length=length,
                        encoding=encoding,
                        line_endings=options.get('line_endings'))

                    try:
                        section['metadata'] = json.loads(content)
                    except ValueError as e:
                        raise DiffXParseError(
                            'JSON metadata could not be parsed: %s' % e,
                            linenum=linenum)
                else:
                    assert section_id == Section.FILE_DIFF

                    # This is a diff section.
                    #
                    # Read the content. If an explicit encoding is provided,
                    # decode it to a Unicode string. Otherwise, it will remain
                    # a byte string.
                    #
                    # Encodings for diffs aren't inherited from parent
                    # sections.
                    section['diff'] = self._read_content(
                        length=length,
                        encoding=options.get('encoding'),
                        line_endings=options.get('line_endings'),
                        preserve_trailing_newline=True,
                        keep_bytes=True)
            else:
                # This is a container section.
                if section_id == Section.MAIN:
                    # This is the main DiffX section, which we'll encounter
                    # only once.
                    #
                    # Validate the DiffX version.
                    diffx_version = options.get('version')

                    if diffx_version not in SpecVersion.VALID_VALUES:
                        raise DiffXParseError(
                            'The DiffX version in this file (%s) is not '
                            'supported by this version of the diffx module'
                            % diffx_version,
                            linenum=section['line'])
                else:
                    # This is either the change or file section.
                    assert section_id in (Section.CHANGE, Section.FILE)

                    if level <= prev_container_level:
                        # We're at the same section level (change -> change,
                        # or file -> file), or we went back up a level
                        # (file -> change). Pop off the last encoding from
                        # the stack before we push a new encoding onto it.
                        encodings.pop()

                # Push a newly-specified encoding (if in the options) or the
                # parent section's encoding on the stack.
                encodings.append(options.get('encoding', encodings[-1]))

                prev_container_level = level

            # Set the new list of valid exceptions allowed at this stage of
            # parsing.
            valid_sections = VALID_SECTION_STATES[section_id]

            # Pass that section up to the caller for processing.
            yield section

    def _read_header(self, valid_sections={}):
        """Read a header at the current offset within the stream.

        The header will be validated against a list of valid sections for the
        current stage of parsing.

        The header's options will also be strictly validated, ensuring they
        conform to the exact specification of a DiffX header (single space
        before each option, valid characters in option keys and values).

        If the header is valid, information on the section will be returned.

        Args:
            valid_sections (set of unicode):
                The sections considered valid at this phase of parsing.

        Returns:
            dict:
            Information on the section for further processing. This will be
            ``None`` if we've reached the end of the file.

        Raises:
            pydiffx.errors.DiffXParseError:
                The section header could not be found, was invalid for this
                stage of parsing, or contained invalid formatting.
        """
        linenum = self._linenum

        # It's possible that we'll be at the end of the file, with some blank
        # lines, or hand-editing (or bad diff generation) has led to some
        # blank lines before a header. We'll iterate through any blank lines
        # until we reach content or an End of File.
        while True:
            header, eof = self._read_until(b'\n')

            if eof:
                return None

            if header.strip():
                break

        if self._file_newlines is None:
            # Given that we read up until a '\n', one of these are guaranteed
            # to match.
            if header.endswith(b'\r\n'):
                self._file_newlines = b'\r\n'
            else:
                assert header.endswith(b'\n')

                self._file_newlines = b'\n'

        assert header.endswith(self._file_newlines)
        header = header[:-len(self._file_newlines)]

        m = self._HEADER_RE.match(header)

        if not m:
            raise DiffXParseError(
                'Unexpected or improperly formatted header: %r' % header,
                linenum=linenum)

        # Validate the level and section ID.
        section_id = m.group('section_id').decode('ascii')

        if section_id not in valid_sections:
            raise DiffXParseError(
                'Unknown or unexpected section ID "%(section_id)s". '
                'Expected one of: %(valid_sections)s'
                % {
                    'section_id': section_id,
                    'valid_sections': ', '.join(
                        '"%s"' % _valid_section
                        for _valid_section in sorted(valid_sections)
                    ),
                },
                linenum=linenum)

        section_type = m.group('section_type')
        level = len(m.group('level'))

        # Parse the options out of the header.
        options_str = m.group('options')
        options = {}

        if options_str:
            # Options should be present.
            #
            # As this is a reference implementation, this will be strict with
            # the format. There should be exactly one space between the
            # "#<id>:" and the options, one space between each comma-separated
            # pair, and each key and value are expected to match a specific set
            # of characters.
            for option_pair in options_str.split(b', '):
                option_key, option_value = option_pair.split(b'=', 1)

                if not self._HEADER_OPTION_KEY_RE.match(option_key):
                    raise DiffXParseError(
                        'Header option key "%s" contains invalid characters'
                        % option_key.decode('ascii'),
                        linenum=linenum,
                        column=header.index(option_pair))

                if not self._HEADER_OPTION_VALUE_RE.match(option_value):
                    raise DiffXParseError(
                        'Header option value "%(value)s" for key "%(key)s" '
                        'contains invalid characters'
                        % {
                            'key': option_key.decode('ascii'),
                            'value': option_value.decode('ascii'),
                        },
                        linenum=linenum,
                        column=header.index(option_pair) + len(option_key) + 1)

                # These should safely decode, since we've validated the
                # characters above.
                option_key = option_key.decode('ascii')
                option_value = option_value.decode('ascii')

                # Convert the value to an integer, if it's a number.
                try:
                    option_value = int(option_value)
                except ValueError:
                    pass

                options[option_key] = option_value

        self._linenum += 1

        return {
            'level': level,
            'line': linenum,
            'options': options,
            'section': section_id,
            'type': section_type.decode('ascii'),
        }

    def _read_content(self,
                      length,
                      encoding=None,
                      indent=None,
                      line_endings=None,
                      preserve_trailing_newline=False,
                      keep_bytes=False):
        """Read content for a section, with the given length.

        The content will be read, any specified indentation stripped, and
        the resulting bytes decoded to a Unicode string (if an encoding is
        specified).

        The content will be validated to ensure that it ended in a newline
        (helping ensure that the length covered the entirety of the section's
        content).

        Args:
            length (int):
                The length of the content to read.

            encoding (unicode, optional):
                The encoding used to decode the content to a Unicode string.

                If ``None``, the result will be a byte string.

            indent (int, optional):
                The amount of indentation to strip from the beginning of each
                byte string.

            line_endings (unicode, optional):
                The specified line ending format (``dos`` or ``unix``). If
                provided, this will be used to split lines. If not provided,
                the line endings will be inferred.

            keep_bytes (bool, optional):
                Whether to keep the result as bytes, even if an encoding is
                provided.

        Returns:
            bytes or unicode:
            The processed string. The type is dependent on the ``encoding``
            value.

        Raises:
            pydiffx.errors.DiffXParseError:
                The content did not end in the newline, or an option did not
                validate.
        """
        fp = self._fp
        content = fp.read(length)

        # First, determine the line endings that we're going to be working
        # with.
        if line_endings:
            # An explicit line ending type was specified. Validate it and
            # get the newline characters, encoding it for the byte string.
            try:
                newline = get_newline_for_type(line_endings,
                                               encoding=encoding)
            except ValueError as e:
                raise DiffXParseError(six.text_type(e),
                                      linenum=self._linenum)
        else:
            # An explicit line ending type was not specified. Try to determine
            # the appropriate line ending based on the first line of content.
            line_endings, newline = guess_line_endings(content,
                                                       encoding=encoding)

        lines = split_lines(data=content,
                            newline=newline,
                            keep_ends=True)

        if indent:
            # It's important that we don't assume each line is actually
            # indented correctly. There could be nothing but a newline,
            # or due to some error the indentation on some line may be
            # wrong. Be careful to strip only the spaces, up to the specified
            # indentation level.
            indent_re = re.compile(br'^ {1,%d}' % indent)
            content = b''.join(
                indent_re.sub(b'', _line)
                for _line in lines
            )

        if encoding and not keep_bytes:
            # We know what this content was encoded with. We can now decode
            # it.
            content = content.decode(encoding)
            newline = newline.decode(encoding)

        # Validate that the content ends in a newline. This is to ensure that
        # the file was written according to spec.
        if not content.endswith(newline):
            raise DiffXParseError(
                'Expected a newline after content',
                linenum=self._linenum)

        self._linenum += len(lines)

        return content

    def _read_until(self, c, chunk_size=96):
        """Read from the stream until a character is found.

        Data will be read from the stream in chunks. All data up to the
        matching character will be returned. Any data that's read past the
        character will be preserved for the next read.

        If the end of the file is reached, all data read until the end of the
        file will be returned, and a flag will be set to inform the reader.

        Args:
            c (byte):
                The character to read until. This character will be included
                in the result.

            chunk_size (int, optional):
                The size of each chunk to read.

        Returns:
            tuple:
            A 2-tuple containing:

            1. The resulting byte string.
            2. A boolean indicating if the end of the file was reached.
        """
        s = io.BytesIO()
        fp = self._fp
        eof = False

        while True:
            chunk = fp.read(chunk_size)

            if not chunk:
                # The end of the file was reached. We'll bail out of the loop
                # and return everything we've read so far.
                eof = True
                break

            i = chunk.find(c)

            if i == -1:
                # We didn't find the character. Store the entire chunk.
                s.write(chunk)
            else:
                # We found the character. Store everything up to and including
                # it, and then go back in the stream for the next read.
                s.write(chunk[:i + 1])
                fp.seek(i + 1 - len(chunk), os.SEEK_CUR)
                break

        result = s.getvalue()
        s.close()

        return result, eof
