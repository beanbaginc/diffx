"""A streaming writer for DiffX files."""

from __future__ import unicode_literals

import io
import json

import six
from six.moves import range

from pydiffx.errors import (DiffXContentError,
                            DiffXOptionValueChoiceError,
                            DiffXSectionOrderError)
from pydiffx.options import (DiffType,
                             LineEndings,
                             MetaFormat,
                             PreambleMimeType,
                             SpecVersion)
from pydiffx.sections import Section, VALID_SECTION_STATES
from pydiffx.utils.text import (NEWLINE_FORMATS,
                                guess_line_endings,
                                split_lines,
                                strip_bom)


class DiffXWriter(object):
    """A streaming writer for DiffX files.

    This is a low-level interface for writing a DiffX file to an existing
    stream, such as an opened file handle or an in-progress web server
    response.

    Consumers can incrementally write change, file, metadata, preamble, and
    diff contents to the stream without keeping it all in memory up-front.
    Consumers are responsible for including any necessary metadata for each
    section.
    """

    #: The supported version of the DiffX specification.
    VERSION = SpecVersion.DEFAULT_VERSION

    #: Default indentation to apply to preamble sections.
    DEFAULT_PREAMBLE_INDENT = 4

    #: Default encoding to use for the DiffX file.
    DEFAULT_ENCODING = 'utf-8'

    _LEVEL_NONE = 0
    _LEVEL_MAIN = 1
    _LEVEL_CHANGE = 2
    _LEVEL_FILE = 3

    def __init__(self, fp, encoding=DEFAULT_ENCODING, version=VERSION):
        """Initialize the writer.

        Args:
            fp (file or io.IOBase):
                The file pointer/stream to write to. This must be opened in
                binary (bytes) mode.

            encoding (unicode, optional):
                The default encoding for content in the file. This will
                generally be left as the default of "utf-8".

            version (unicode, optional):
                The version of the DiffX file to write.

                This must currently be ``1.0``.
        """
        if version not in SpecVersion.VALID_VALUES:
            raise DiffXOptionValueChoiceError(
                option='version',
                value=version,
                choices=SpecVersion.VALID_VALUES)

        self.fp = fp
        self._stack = [{
            'encoding': encoding,
        }]
        self._prev_section = None

        self._new_container_section(section_name='diffx',
                                    section_level=self._LEVEL_MAIN,
                                    encoding=self._cur_encoding,
                                    version=version)

    @property
    def _cur_section_level(self):
        """The current section level being written.

        Type:
            int
        """
        return len(self._stack) - 1

    @property
    def _cur_encoding(self):
        """The current encoding for the section.

        Type:
            unicode
        """
        return self._stack[-1]['encoding']

    def new_change(self, encoding=None):
        """Write a new change section to the stream.

        Args:
            encoding (unicode, optional):
                The encoding to use for the section. Defaults to the main
                DiffX file encoding.

        Raises:
            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        self._new_container_section(section_name='change',
                                    section_level=self._LEVEL_CHANGE,
                                    encoding=encoding)

    def new_file(self, encoding=None):
        """Write a new file section to the stream.

        :py:meth:`new_change` must have been called at least once before
        this is called.

        Args:
            encoding (unicode, optional):
                The encoding to use for the section. Defaults to the parent
                change section's encoding.

        Raises:
            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        self._new_container_section(section_name='file',
                                    section_level=self._LEVEL_FILE,
                                    encoding=encoding)

    def write_preamble(self,
                       text,
                       encoding=None,
                       indent=DEFAULT_PREAMBLE_INDENT,
                       line_endings=None,
                       mimetype=None):
        """Write a new preamble section for a change or a file.

        If called as the first operation on a new stream, this will write a
        top-level DiffX preamble.

        If called immediately after a call to :py:meth:`new_change`, this will
        write a change preamble.

        This cannot be called at any other time.

        This must be called before :py:meth:`write_meta` in the section.

        Args:
            text (unicode):
                The text to write.

            encoding (unicode, optional):
                The encoding to use for the section. Defaults to the parent
                change section's encoding.

            indent (int, optional):
                The optional indentation level for the text. This defaults to
                4 spaces.

                This is used to ensure preamble text cannot interfere with the
                parsing of any DiffX or diff content.

            line_endings (unicode, optional):
                The line endings used for the preamble. This can be "dos" or
                "unix".

                If not provided, a value will be computed based on content,
                and then inserted into the header.

            mimetype (unicode, optional):
                The optional mimetype for the file contents. If not provided,
                this will be plain text.

                Supported values are ``text/plain`` or ``text/markdown``.

        Raises:
            pydiffx.errors.DiffXContentError:
                The content was empty or was an invalid type.

            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.

            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        if not isinstance(text, six.text_type):
            raise DiffXContentError('text must be a Unicode string, not %s'
                                    % type(text))

        if (mimetype is not None and
            mimetype not in PreambleMimeType.VALID_VALUES):
            raise DiffXOptionValueChoiceError(
                option='mimetype',
                value=mimetype,
                choices=PreambleMimeType.VALID_VALUES)

        self._new_content_section(section_name='preamble',
                                  content=text,
                                  line_endings=line_endings,
                                  encoding=encoding,
                                  indent=indent,
                                  mimetype=mimetype)

    def write_meta(self, metadata, encoding=None,
                   meta_format=MetaFormat.JSON):
        """Write a new meta section for DiffX, a change, or a file.

        If called before :py:meth:`new_change`, this will write a top-level
        DiffX meta section.

        If called after :py:meth:`new_change` but before :py:meth:`new_file`,
        this will write a change meta section.

        If called after :py:meth:`new_file`, this will write a file meta
        section.

        This cannot be called before :py:meth:`write_preamble` in the
        section, or after :py:meth:`write_diff` in file sections.

        Args:
            metadata (dict):
                The metadata to write.

            encoding (unicode, optional):
                The encoding to use for the section. Defaults to the parent
                change section's encoding.

            meta_format (unicode, optional):
                The format for this metadata section.

                Valid values are in :py:class:`~pydiffx.options.MetaFormat`.

        Raises:
            pydiffx.errors.DiffXContentError:
                The metadata was empty or was an invalid type.

            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.

            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        if not isinstance(metadata, dict):
            raise DiffXContentError('metadata must be a dictionary, not %s'
                                    % type(metadata))

        if not metadata:
            raise DiffXContentError('metadata cannot be empty')

        if meta_format not in MetaFormat.VALID_VALUES:
            raise DiffXOptionValueChoiceError(
                option='meta_format',
                value=meta_format,
                choices=MetaFormat.VALID_VALUES)

        # NOTE: We're not bothering to write line_endings= here. It's not
        #       important at all for JSON metadata, and isn't a helpful
        #       parser aid. This may need to be revisited in the future if
        #       a different metadata format is ever provided.
        self._new_content_section(
            section_name='meta',
            content=json.dumps(metadata,
                               indent=4,
                               separators=(',', ': '),
                               sort_keys=True),
            encoding=encoding,
            format=meta_format,
            write_line_endings_option=False)

    def write_diff(self, content, diff_type=None, encoding=None,
                   line_endings=None):
        """Write a new diff section for a file.

        This must be called after :py:meth:`new_file`, and must be after the
        :py:meth:`write_meta` call.

        Args:
            content (bytes):
                The diff content to write.

            diff_type (unicode, optional):
                The type of diff to write. This must be one of
                :py:attr:`DIFF_TYPE_TEXT` or :py:attr:`DIFF_TYPE_BINARY`.

            encoding (unicode, optional):
                The encoding to use for the section. This does not inherit
                from previous sections.

            line_endings (unicode, optional):
                The line endings used for the diff. This can be
                "dos" or "unix".

                If not provided, a value will be computed based on content,
                and then inserted into the header.

        Raises:
            pydiffx.errors.DiffXContentError:
                The diff was an invalid type.

            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.

            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        if not isinstance(content, bytes):
            raise DiffXContentError('diff must be a byte string, not %s'
                                    % type(content))

        if (diff_type is not None and
            diff_type not in DiffType.VALID_VALUES):
            raise DiffXOptionValueChoiceError(
                option='diff_type',
                value=diff_type,
                choices=DiffType.VALID_VALUES)

        self._new_content_section(
            section_name='diff',
            content=content,
            encoding=encoding,
            line_endings=line_endings,
            type=diff_type,
            inherit_encoding=False)

    def _build_section(self, level, section_name):
        """Return a section with the given name and level.

        Args:
            level (int):
                The section level.

            section_name (unicode):
                The name of the section.

        Returns:
            unicode:
            The section ID.
        """
        return '%s%s' % ('.' * (level - 1),
                         section_name)

    def _validate_section(self, section):
        """Validate that a section has been added in the correct order.

        This will catch a consumer adding sections in the wrong order (such
        as a preamble to a file section, or a meta before a preamble).

        If a section has been added in the wrong order, a useful error message
        will be raised.

        Args:
            section (unicode):
                The new section to validate.

        Raises:
            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        if self._prev_section is None:
            return

        valid_sections = VALID_SECTION_STATES.get(self._prev_section)

        if section not in valid_sections:
            # Generally-speaking, we'll need this map at most once per writer.
            # Define it dynamically, rather than keeping it in memory the
            # whole time.
            write_preamble = 'write_preamble()'
            write_meta = 'write_meta()'
            write_diff = 'write_diff()'
            new_change = 'new_change()'
            new_file = 'new_file()'

            FUNC_MAP = {
                # Preamble sections
                Section.MAIN_PREAMBLE: write_preamble,
                Section.CHANGE_PREAMBLE: write_preamble,
                '...preamble': write_preamble,

                # Meta sections
                Section.MAIN_META: write_meta,
                Section.CHANGE_META: write_meta,
                Section.FILE_META: write_meta,

                # Diff section
                Section.FILE_DIFF: write_diff,
                '.diff': write_diff,
                '..diff': write_diff,

                # Container sections
                Section.MAIN: 'initialization',
                Section.CHANGE: new_change,
                Section.FILE: new_file,
            }

            if len(valid_sections) == 1:
                msg = (
                    '%(called_func)s cannot be called at this stage '
                    '(%(after_func)s). Expected %(valid_funcs)s'
                )
            else:
                msg = (
                    '%(called_func)s cannot be called at this stage '
                    '(%(after_func)s). Expected one of: %(valid_funcs)s'
                )

            raise DiffXSectionOrderError(msg % {
                'after_func': 'after %s' % FUNC_MAP.get(self._prev_section),
                'called_func': FUNC_MAP[section],
                'valid_funcs': ', '.join(sorted(
                    FUNC_MAP[_section]
                    for _section in valid_sections
                )),
            })

    def _new_container_section(self, section_name, section_level,
                               encoding=None, **options):
        """Start a new container section and write it to the stream.

        New sections will be added under this section until a section at
        the same or a higher level is added.

        Args:
            section_name (unicode):
                The name of the section being written.

            section_level (int):
                The level of the section to write.

            encoding (unicode, optional):
                The encoding to use for the section. If not provided,
                the parent section's encoding will be used.

            **options (dict):
                Additional options to provide in the header.

        Raises:
            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.

            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        section = self._build_section(section_level, section_name)
        self._validate_section(section)

        # If we're writing a new section at the current level, or moving up
        # levels, we'll need to pop the appropriate number of sections off
        # the stack.
        for i in range(self._cur_section_level - section_level + 1):
            self._stack.pop()

        self._stack.append({
            'encoding': encoding or self._cur_encoding,
        })

        self._write_section_header(section=section,
                                   encoding=encoding,
                                   **options)

    def _new_content_section(self,
                             section_name,
                             content,
                             line_endings=None,
                             encoding=None,
                             indent=None,
                             write_line_endings_option=True,
                             inherit_encoding=True,
                             **options):
        """Add a new content section and write it to the stream.

        Args:
            section_name (unicode):
                The name of the section being written.

            content (bytes or unicode):
                The content to write to the section.

            line_endings (unicode, optional):
                The type of line endings to write ("dos" or "unix"). If
                not provided, it will be computed based on the line endings
                of the first line.

            encoding (unicode, optional):
                The encoding to use for encoding. This can only be used for
                Unicode strings.

            indent (int, optional):
                The amount of indentation to apply to the content, after
                encoding.

            write_line_endings_option (bool, optional):
                Whether to write the ``line_endings`` option to the header.

            inherit_encoding (bool, optional):
                Whether to inherit the encoding, if one is not specified.

            **options (dict):
                Additional options for the header.

        Raises:
            pydiffx.errors.DiffXContentError:
                The diff was an invalid type.

            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.

            pydiffx.errors.DiffXSectionOrderError:
                This was called at the wrong point in diff generation.
        """
        section = self._build_section(self._cur_section_level + 1,
                                      section_name)
        self._validate_section(section)

        content, line_endings = self._prepare_content(
            content,
            line_endings=line_endings,
            indent=indent,
            encoding=encoding,
            inherit_encoding=inherit_encoding)

        header_options = dict(options, **{
            'encoding': encoding,
            'indent': indent,
            'length': len(content),
        })

        if write_line_endings_option:
            header_options['line_endings'] = line_endings

        self._write_section_header(section, **header_options)
        self.fp.write(content)

    def _write_section_header(self, section, **options):
        """Write a section header to the stream.

        Args:
            section (unicode):
                The section being written.

            **options (dict):
                Additional options to provide in the header.
        """
        options_str = ', '.join(
            '%s=%s' % (_key, _value)
            for _key, _value in sorted(six.iteritems(options),
                                       key=lambda pair: pair[0])
            if _value is not None
        )

        fp = self.fp
        fp.write(b'#%s:' % section.encode('ascii'))

        if options_str:
            fp.write(b' ')
            fp.write(options_str.encode('ascii'))

        fp.write(b'\n')

        self._prev_section = section

    def _prepare_content(self, content, indent=None, line_endings=None,
                         encoding=None, inherit_encoding=True):
        """Prepare content for writing to a section.

        This will take care to encode and indent the content, if needed, and
        add any necessary newline if missing. The result will be a byte string
        that can be written to the stream.

        The text cannot be empty.

        Args:
            content (bytes or unicode):
                The content to prepare.

            indent (int, optional):
                The amount of indentation to apply to the content, after
                encoding.

            line_endings (unicode, optional):
                The type of line endings to write ("dos" or "unix"). If
                not provided, it will be computed based on the line endings
                of the first line.

            encoding (unicode, optional):
                The encoding to use for encoding. This can only be used for
                Unicode strings.

            inherit_encoding (bool, optional):
                Whether to inherit the encoding, if one is not specified.

        Returns:
            tuple:
            A 2-tuple containing:

            1. The prepared content as a byte string.
            2. The newline format, for the header.

        Raises:
            pydiffx.errors.DiffXOptionValueError:
                An option value was invalid.
        """
        if not content:
            raise DiffXContentError('The text cannot be empty.')

        if (line_endings is not None and
            line_endings not in LineEndings.VALID_VALUES):
            raise DiffXOptionValueChoiceError(
                option='line_endings',
                value=line_endings,
                choices=LineEndings.VALID_VALUES)

        assert isinstance(content, (bytes, six.text_type))

        if not encoding and inherit_encoding:
            encoding = self._cur_encoding

        # If we were given an explicit line_endings, we'll split on that.
        # Otherwise, newline will be None below, and we'll split based on
        # the newline format we find.
        newline = NEWLINE_FORMATS.get(line_endings)
        newline_encoding = encoding or 'ascii'

        if newline is None:
            # We weren't given an explicit line_endings above, so we'll need
            # to compute it based on the first line.
            line_endings, newline = guess_line_endings(
                content,
                encoding=newline_encoding)
        elif isinstance(content, bytes):
            newline = newline.encode(newline_encoding)

        # Encode the content and newline in the specified encoding.
        if isinstance(newline, six.text_type):
            newline = newline.encode(encoding)

        if isinstance(content, six.text_type):
            content = content.encode(encoding)

        # Remove the newline's BOM, if needed (depending on the encoding)
        # so that we can safely append it to lines when splitting.
        newline = strip_bom(newline,
                            encoding=encoding)

        # If the content doesn't end in a newline, we'll need to add one.
        if not content.endswith(newline):
            content += newline

        # Write the string to a byte stream. This is more efficient than
        # building and joining lists of byte strings, or concatenating them.
        if indent:
            stream = io.BytesIO()
            indent_str = b' ' * indent
            lines = split_lines(content,
                                keep_ends=True,
                                newline=newline)

            for line in lines:
                stream.write(indent_str)
                stream.write(line)

            result = stream.getvalue()
            stream.close()
        else:
            result = content

        return result, line_endings
