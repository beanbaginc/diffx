"""Reader for parsing a DiffX file into DOM objects."""

from __future__ import unicode_literals

from pydiffx.reader import DiffXReader
from pydiffx.sections import Section


class DiffXDOMReader(object):
    """A reader for parsing a DiffX file into DOM objects.

    This will construct a :py:class:`~pydiffx.dom.objects.DiffX` from an input
    byte stream, such as a file, HTTP response, or memory-backed stream.

    Often, you won't use this directly. Instead, you'll call
    :py:meth:`DiffXFile.from_stream() <pydiffx.dom.objects.DiffX.from_stream>`
    or :py:meth:`DiffXFile.from_bytes()
    <pydiffx.dom.objects.DiffX.from_bytes>`.

    If constructing manually, one instance can be reused for multiple streams.

    Attributes:
        diffx_cls (type):
            The :py:class:`~pydiffx.dom.objects.DiffX` class or subclass
            to create when parsing.
    """

    #: The class to instantiate for reading from a stream.
    #:
    #: Subclasses can set this if they need to use a more specialized reader.
    #:
    #: Type:
    #:     type
    reader_cls = DiffXReader

    def __init__(self, diffx_cls):
        """Initialize the reader.

        Args:
            diffx_cls (type):
                The :py:class:`~pydiffx.dom.objects.DiffX` class or subclass
                to create when parsing.
        """
        self.diffx_cls = diffx_cls

    def parse(self, stream):
        """Parse a stream and construct the DOM objects.

        The stream will be closed after reading.

        Args:
            stream (file or io.IOBase):
                The byte stream containing a valid DiffX file.

        Returns:
            pydiffx.dom.objects.DiffX:
            The resulting DiffX instance.

        Raises:
            pydiffx.errors.DiffXParseError:
                The DiffX contents could not be parsed. Details will be in
                the error message.
        """
        with stream:
            reader = self.reader_cls(stream)
            diffx = self.diffx_cls()

            section_handlers = {
                Section.MAIN: self._read_main_section,
                Section.MAIN_META: self._read_meta_section,
                Section.MAIN_PREAMBLE: self._read_preamble_section,
                Section.CHANGE: self._read_change_section,
                Section.CHANGE_PREAMBLE: self._read_preamble_section,
                Section.CHANGE_META: self._read_meta_section,
                Section.FILE: self._read_file_section,
                Section.FILE_META: self._read_meta_section,
                Section.FILE_DIFF: self._read_diff_section,
            }

            cur_section = diffx

            for section_info in reader:
                section_id = section_info['section']
                section_handler = section_handlers[section_id]

                cur_section = (
                    section_handler(diffx, cur_section, section_info) or
                    cur_section
                )

        return diffx

    def _read_meta_section(self, diffx, section, section_info):
        """Read a meta section.

        This will add the metadata content and options to the section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.BaseDiffXContainerSection):
                The current container section being populated.

            section_info (dict):
                Information on the section from the streaming reader.
        """
        section.meta = section_info['metadata']
        self._set_content_options(section.meta_section,
                                  section_info['options'])

    def _read_preamble_section(self, diffx, section, section_info):
        """Read a preamble section.

        This will add the preamble text and options to the section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.BaseDiffXContainerSection):
                The current container section being populated.

            section_info (dict):
                Information on the section from the streaming reader.
        """
        section.preamble = section_info['text']
        self._set_content_options(section.preamble_section,
                                  section_info['options'])

    def _read_diff_section(self, diffx, section, section_info):
        """Read a diff section.

        This will add the diff content and options to the section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.DiffXFileSection):
                The current file section being populated.

            section_info (dict):
                Information on the section from the streaming reader.
        """
        section.diff = section_info['diff']
        self._set_content_options(section.diff_section,
                                  section_info['options'])

    def _read_main_section(self, diffx, section, section_info):
        """Read the main section.

        This will set options on the main section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.DiffXChangeSection):
                The current section being populated.

            section_info (dict):
                Information on the section from the streaming reader.
        """
        diffx.options.clear()
        diffx.options.update(section_info['options'])

    def _read_change_section(self, diffx, section, section_info):
        """Read a change section.

        This will add a new change section to the main DiffX section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.DiffX):
                The current section being populated.

            section_info (dict):
                Information on the section from the streaming reader.

        Returns:
            pydiffx.dom.objects.DiffXChangeSection:
            The new change section.
        """
        return diffx.add_change(**section_info['options'])

    def _read_file_section(self, diffx, section, section_info):
        """Read a file section.

        This will add a new file section to the current change section.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object being populated.

            section (pydiffx.dom.objects.DiffXChangeSection):
                The current section being populated.

            section_info (dict):
                Information on the section from the streaming reader.

        Returns:
            pydiffx.dom.objects.DiffXFileSection:
            The new file section.
        """
        return diffx.changes[-1].add_file(**section_info['options'])

    def _set_content_options(self, section, options):
        options.pop('length', None)

        section.options.clear()
        section.options.update(options)
