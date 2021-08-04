"""Writer for generating a DiffX file from DOM objects."""

from __future__ import unicode_literals

import six

from pydiffx.writer import DiffXWriter
from pydiffx.sections import CONTENT_SECTIONS


class DiffXDOMWriter(object):
    """A writer for generating a DiffX file from DOM objects.

    This will write a :py:class:`~pydiffx.dom.objects.DiffX` object tree
    to a byte stream, such as a file, HTTP response, or memory-backed stream.

    If constructing manually, one instance can be reused for multiple DiffX
    objects.
    """

    #: The class to instantiate for writing to a stream.
    #:
    #: Subclasses can set this if they need to use a more specialized writer.
    #:
    #: Type:
    #:     type
    writer_cls = DiffXWriter

    _remapped_options = {
        'diff': {
            'type': 'diff_type',
        },
        'meta': {
            'format': 'meta_format'
        },
    }

    def write_stream(self, diffx, stream):
        """Write a DiffX object to a stream.

        Args:
            diffx (pydiffx.dom.objects.DiffX):
                The DiffX object to write.

            stream (file or io.IOBase):
                The byte stream to write to.

        Raises:
            pydiffx.errors.BaseDiffXError:
                The DiffX contents could not be written. Details will be in
                the error message.
        """
        main_options = diffx.options.copy()

        version = main_options.pop('version', DiffXWriter.VERSION)
        encoding = main_options.pop('encoding', None)

        writer = self.writer_cls(stream,
                                 version=version,
                                 encoding=encoding,
                                 **main_options)

        for subsection in diffx:
            self._write_section(subsection, writer)

    def _write_section(self, section, writer):
        """Write a section to the stream.

        Args:
            section (pydiffx.dom.objects.BaseDiffXSection):
                The section to write.

            writer (pydiffx.dom.writer.DiffXWriter):
                The streaming writer to write with.
        """
        if section.section_id in CONTENT_SECTIONS:
            self._write_content_section(section, writer)
        else:
            self._write_container_section(section, writer)

    def _write_container_section(self, section, writer):
        """Write a container section to the stream.

        Args:
            section (pydiffx.dom.objects.BaseDiffXContainerSection):
                The container section to write.

            writer (pydiffx.dom.writer.DiffXWriter):
                The streaming writer to write with.
        """
        write_func = getattr(writer, 'new_%s' % section.section_name)
        write_func(**self._get_options(section))

        for subsection in section:
            self._write_section(subsection, writer)

    def _write_content_section(self, section, writer):
        """Write a content section to the stream.

        If there's no content to write, the section will be skipped.

        Args:
            section (pydiffx.dom.objects.BaseDiffXContentSection):
                The content section to write.

            writer (pydiffx.dom.writer.DiffXWriter):
                The streaming writer to write with.
        """
        content = section.content

        if content:
            write_func = getattr(writer, 'write_%s' % section.section_name)
            write_func(content, **self._get_options(section))

    def _get_options(self, section):
        """Return options to write for a given section.

        This will take care of renaming any options as appropriate to pass
        to the writer function.

        Args:
            section (pydiffx.dom.objects.BaseDiffXSection):
                The section being written.

        Returns:
            dict:
            The options to pass to the writer function.
        """
        options = section.options

        try:
            remapped_options = self._remapped_options[section.section_name]
        except KeyError:
            return options

        return {
            remapped_options.get(_key, _key): _value
            for _key, _value in six.iteritems(options)
        }
