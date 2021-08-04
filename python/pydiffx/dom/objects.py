"""The DiffX Object Model.

This is a set of classes that comprise the DiffX Object Model. These
consistent of container and content section classes, each with type-safe
properties used to manage content and options for the DiffX file.

The only object that should be created manually is :py:class:`DiffX`. The
others are created automatically or when calling :py:meth:`DiffX.add_change`
or :py:meth:`DiffXChangeSection.add_file`.
"""

from __future__ import unicode_literals

import io
import logging
from copy import deepcopy

import six

from pydiffx.dom.properties import (ContainerOptionsMixin,
                                    DiffOptionsMixin,
                                    DiffTypeOptionProperty,
                                    EncodingOptionProperty,
                                    LineEndingsOptionProperty,
                                    MetaFormatOptionProperty,
                                    MetaOptionsMixin,
                                    PreambleIndentOptionProperty,
                                    PreambleMimeTypeOptionProperty,
                                    PreambleOptionsMixin,
                                    VersionOptionProperty)
from pydiffx.dom.reader import DiffXDOMReader
from pydiffx.dom.writer import DiffXDOMWriter
from pydiffx.errors import DiffXUnknownOptionError
from pydiffx.options import DiffType, MetaFormat
from pydiffx.utils.text import (get_newline_for_type,
                                guess_line_endings,
                                split_lines)
from pydiffx.utils.unified_diffs import get_unified_diff_hunks
from pydiffx.writer import DiffXWriter


logger = logging.getLogger(__name__)


class BaseDiffXSection(object):
    """Base class for a DiffX section.

    This manages option storage and controls the initialization process for
    the subclass.

    Attributes:
        options (dict):
            The options set for this section. This can be manipulated directly
            without any type checking, but it's recommended that consumers
            go through the dedicated class-level attributes.

        section_id (unicode):
            The ID of this section. This corresponds to a value in
            :py:class:`~pydiffx.sections.Section`.
    """

    #: The name of the section.
    #:
    #: This must be provided by subclasses.
    #:
    #: Type:
    #:     unicode
    section_name = None

    #: Default options to set for the section.
    #:
    #: These will be written to :py:attr:`options` when constructing the
    #: section if not otherwise provided by the caller.
    #:
    #: Type:
    #:     dict
    default_options = {}

    __slots__ = (
        'options',
        'section_id',
        '_level',
    )

    def __init__(self, parent_section=None, **attrs):
        """Initialize the section.

        Args:
            parent_section (BaseDiffXContainerSection, optional):
                The parent container section.

            **attrs (dict):
                Attributes to set for the section.

                This may consist of attributes representing options or content
                subsections.

                Any invalid option will raise a
                :py:class:`~pydiffx.errors.DiffXUnknownOptionError`.
        """
        if parent_section is None:
            level = 0
        else:
            level = parent_section._level + 1

        self.options = self.default_options.copy()
        self.section_id = '%s%s' % ('.' * level, self.section_name)
        self._level = level

        self._setup_state()

        for name, value in six.iteritems(attrs):
            try:
                setattr(self, name, value)
            except AttributeError:
                raise DiffXUnknownOptionError(
                    '"%s" is not a valid option or content section'
                    % name)

    def _setup_state(self):
        """Set up subsections and subsection-related state."""
        pass

    def __eq__(self, other):
        """Return whether this section is equal to another section.

        Args:
            other (BaseDiffXSection):
                The section to compare to.

        Returns:
            bool:
            ``True`` if the two sections are equal. ``False`` if they are not.
        """
        return (
            type(self) is type(other) and
            self.section_id == other.section_id and
            self.options == other.options
        )

    def __repr__(self):
        """Return a string representation of this section.

        Returns:
            unicode:
            The string representation.
        """
        return '<%s(level=%s, options=%r)>' % (
            self.__class__.__name__,
            self._level,
            self.options
        )


class BaseDiffXContainerSection(BaseDiffXSection):
    """Base class for container sections.

    Container sections contain additional container and/or content sections.
    They're also responsible for setting options on the content sections.

    Subclasses must explicitly set :py:attr:`subsections`.

    Attributes:
        subsections (list of BaseDiffXSection):
            The list of subsections in this section.
    """

    __slots__ = ('subsections',)

    def __eq__(self, other):
        """Return whether this section is equal to another section.

        Args:
            other (BaseDiffXSection):
                The section to compare to.

        Returns:
            bool:
            ``True`` if the two sections are equal. ``False`` if they are not.
        """
        return (
            super(BaseDiffXContainerSection, self).__eq__(other) and
            self.subsections == other.subsections
        )

    def __iter__(self):
        """Iterate through the immediate subsections.

        Yields:
            BaseDiffXSection:
                A subsection of this section.
        """
        return iter(self.subsections)


class BaseDiffXContentSection(BaseDiffXSection):
    """Base class for content sections.

    Content sections contain data in some form, indicated by
    :py:attr:`data_type`.

    They cannot have subsections of their own.

    Consumers will generally not need to access content sections directly.
    Instead, they'll set data or options through the parent container class's
    type-safe attributes, or during construction of the parent section.
    """

    #: The type of data allowed for this section.
    #:
    #: Type:
    #:     type
    data_type = None

    #: Default value for the section.
    #:
    #: Type:
    #:     object
    default_value = None

    __slots__ = ('_content')

    def __init__(self, **kwargs):
        """Initialize the section.

        Args:
            **kwargs (dict):
                Keyword arguments to pass to the parent. See the
                documentation for details.
        """
        if self.default_value is None:
            self._content = None
        else:
            self._content = deepcopy(self.default_value)

        super(BaseDiffXContentSection, self).__init__(**kwargs)

    @property
    def content(self):
        """The content of this section.

        The type will be that of :py:attr:`data_type`.
        """
        return self._content

    @content.setter
    def content(self, value):
        """The content of this section.

        The type will be that of :py:attr:`data_type`.

        Args:
            value (object):
                The content to set.

        Raises:
            TypeError:
                The value was an unsupported type.
        """
        if not isinstance(value, self.data_type):
            raise TypeError(
                'Expected the content to be a %(expected_type)s type, '
                'got %(type)s instead'
                % {
                    'expected_type': self.data_type,
                    'type': type(value),
                })

        self._content = value

    def __eq__(self, other):
        """Return whether this section is equal to another section.

        Args:
            other (BaseDiffXSection):
                The section to compare to.

        Returns:
            bool:
            ``True`` if the two sections are equal. ``False`` if they are not.
        """
        return (
            super(BaseDiffXContentSection, self).__eq__(other) and
            self.content == other.content
        )


class DiffX(ContainerOptionsMixin,
            MetaOptionsMixin,
            PreambleOptionsMixin,
            BaseDiffXContainerSection):
    """Representation of a DiffX file.

    This represents a DiffX file as a hierarchical series of objects and
    attributes. It can be used to construct a new DiffX file piece-by-piece
    before writing it out to a file or stream, or to read in an existing
    DiffX file for processing or manipulation.

    Consumers will start by working directly with a :py:class:`DiffX` instance.

    When constructing one, they'll need to add at least one change by using
    :py:meth:`add_change`, and at least one file to that change.

    When reading one, they can read the preamble, metadata, or list of files
    using the provided attributes.

    Attributes:
        encoding (unicode):
            The default encoding for all preamble and metadata sections in
            the DiffX file. This may be ``None``, in which case an encoding
            cannot be assumed.

            Changing this will not affect the in-memory representation of any
            data, but it will affect how it's written.

        meta (dict):
            Global metadata for the entire DiffX file.

        meta_encoding (unicode):
            Encoding used when reading/writing the metadata in the file.

            See :py:attr:`DiffXMetaSection.encoding`.

        meta_section (DiffXMetaSection):
            The actual metadata section. This will generally not be accessed
            directly.

        preamble (unicode):
            The preamble content describing the entire series of changes in
            the DiffX file.

        preamble_encoding (unicode):
            Encoding used when reading/writing the preamble content in the
            file.

            See :py:attr:`DiffXPreambleSection.encoding`.

        preamble_indent (int):
            Indentation applied to each line of preamble content.

            See :py:attr:`DiffXPreambleSection.indent`.

        preamble_line_endings (unicode):
            The type of line endings used in the preamble content.

            See :py:attr:`DiffXPreambleSection.line_endings`.

        preamble_mimetype (unicode):
            The mimetype representing the format of the preamble content.

            See :py:attr:`DiffXPreambleSection.mimetype`.

        preamble_section (DiffXPreambleSection):
            The actual preamble section. This will generally not be accessed
            directly.
    """

    default_options = {
        'encoding': DiffXWriter.DEFAULT_ENCODING,
        'version': DiffXWriter.VERSION,
    }

    __slots__ = (
        'changes',
        'meta_section',
        'preamble_section',
    )

    #: The version of the DiffX file.
    #:
    #: Only supported versions can be set.
    #:
    #: Type:
    #:     unicode
    version = VersionOptionProperty()

    @classmethod
    def from_bytes(cls, data):
        """Construct an instance from a DiffX file stored in a byte string.

        Args:
            data (bytes):
                The DiffX file contents to parse.

        Returns:
            DiffX:
            The resulting DiffX instance.

        Raises:
            pydiffx.errors.DiffXParseError:
                The DiffX contents could not be parsed. Details will be in
                the error message.
        """
        return cls.from_stream(io.BytesIO(data))

    @classmethod
    def from_stream(cls, stream):
        """Construct an instance from a DiffX file read from a stream.

        This will close the stream after it's been read.

        Args:
            data (file or io.IOBase):
                The stream to read from.

        Returns:
            DiffX:
            The resulting DiffX instance.

        Raises:
            pydiffx.errors.DiffXParseError:
                The DiffX contents could not be parsed. Details will be in
                the error message.
        """
        return DiffXDOMReader(cls).parse(stream)

    @property
    def subsections(self):
        """A list of the preamble, meta, and change subsections.

        Type:
            list of BaseDiffXSection
        """
        return [
            self.preamble_section,
            self.meta_section,
        ] + self.changes

    def add_change(self, **attrs):
        """Add a new change section.

        Args:
            **attrs (dict):
                Attributes to set on the section. This may consist of any
                attributes listed on :py:class:`DiffXChangeSection`.

        Returns:
            DiffXChangeSection:
            The newly-added change section.

        Raises:
            pydiffx.errors.DiffXUnknownOptionError:
                One or more attribute names are invalid.
        """
        change_section = DiffXChangeSection(parent_section=self,
                                            **attrs)
        self.changes.append(change_section)

        return change_section

    def generate_stats(self):
        """Generate statistics for the DiffX metadata.

        This will gather statistics on the number of changes, files,
        insertions, deletions, and total lines changed.

        This should only be run once the diff is complete, before writing
        it.
        """
        stats = {
            'changes': len(self.changes),
            'deletions': 0,
            'files': 0,
            'insertions': 0,
            'lines changed': 0,
        }

        for change_section in self.changes:
            change_section.generate_stats()
            change_stats = change_section.meta['stats']

            stats['files'] += change_stats['files']
            stats['insertions'] += change_stats['insertions']
            stats['deletions'] += change_stats['deletions']
            stats['lines changed'] += change_stats['lines changed']

        # Set the computed stats. Don't override the key if there's something
        # already there, since it might contain some custom stats.
        if 'stats' in self.meta:
            self.meta['stats'].update(stats)
        else:
            self.meta['stats'] = stats

    def to_bytes(self):
        """Write and return the DiffX file contents.

        Returns:
            bytes:
            The DiffX file contents.

        Raises:
            pydiffx.errors.BaseDiffXError:
                There was an error generating the content.
        """
        with io.BytesIO() as stream:
            DiffXDOMWriter().write_stream(self, stream)

            return stream.getvalue()

    def _setup_state(self):
        """Set up subsections and subsection-related state."""
        self.preamble_section = DiffXPreambleSection(parent_section=self)
        self.meta_section = DiffXMetaSection(parent_section=self)
        self.changes = []


class DiffXChangeSection(ContainerOptionsMixin,
                         MetaOptionsMixin,
                         PreambleOptionsMixin,
                         BaseDiffXContainerSection):
    """A change section within a DiffX file.

    A change represents a set of changes to files, possibly backed by a commit.

    Changes can be added through :py:meth:`DiffX.add_change`.

    Attributes:
        encoding (unicode):
            The default encoding for preamble and metadata sections anywhere
            under this section.

            This may be ``None``, in which case the parent
            :py:attr:`DiffX.encoding` value will be used.

            Changing this will not affect the in-memory representation of any
            data, but it will affect how it's written.

        meta (dict):
            Metadata for the change.

        meta_encoding (unicode):
            Encoding used when reading/writing the metadata in the file.

            See :py:attr:`DiffXMetaSection.encoding`.

        meta_section (DiffXMetaSection):
            The actual metadata section. This will generally not be accessed
            directly.

        preamble (unicode):
            The preamble content describing the change.

        preamble_encoding (unicode):
            Encoding used when reading/writing the preamble content in the
            file.

            See :py:attr:`DiffXPreambleSection.encoding`.

        preamble_indent (int):
            Indentation applied to each line of preamble content.

            See :py:attr:`DiffXPreambleSection.indent`.

        preamble_line_endings (unicode):
            The type of line endings used in the preamble content.

            See :py:attr:`DiffXPreambleSection.line_endings`.

        preamble_mimetype (unicode):
            The mimetype representing the format of the preamble content.

            See :py:attr:`DiffXPreambleSection.mimetype`.

        preamble_section (DiffXPreambleSection):
            The actual preamble section. This will generally not be accessed
            directly.
    """

    section_name = 'change'

    __slots__ = (
        'meta_section',
        'preamble_section',
        'files',
    )

    @property
    def subsections(self):
        """A list of the preamble, meta, and file subsections.

        Type:
            list of BaseDiffXSection
        """
        return [
            self.preamble_section,
            self.meta_section,
        ] + self.files

    def add_file(self, **attrs):
        """Add a new file section.

        Args:
            **attrs (dict):
                Attributes to set on the section. This may consist of any
                attributes listed on :py:class:`DiffXFileSection`.

        Returns:
            DiffXFileSection:
            The newly-added change section.

        Raises:
            pydiffx.errors.DiffXUnknownOptionError:
                One or more attribute names are invalid.
        """
        file_section = DiffXFileSection(parent_section=self, **attrs)
        self.files.append(file_section)

        return file_section

    def generate_stats(self):
        """Generate statistics for the change section's metadata.

        This will gather statistics on the number of files, insertions,
        deletions, and total lines changed.

        This should only be run once the change is complete. Normally,
        callers will want to call :py:meth:`DiffX.generate_stats` instead.
        """
        stats = {
            'deletions': 0,
            'files': len(self.files),
            'insertions': 0,
            'lines changed': 0,
        }

        for file_section in self.files:
            file_section.generate_stats()
            file_stats = file_section.meta.get('stats', {})

            stats['insertions'] += file_stats.get('insertions', 0)
            stats['deletions'] += file_stats.get('deletions', 0)
            stats['lines changed'] += file_stats.get('lines changed', 0)

        # Set the computed stats. Don't override the key if there's something
        # already there, since it might contain some custom stats.
        if 'stats' in self.meta:
            self.meta['stats'].update(stats)
        else:
            self.meta['stats'] = stats

    def _setup_state(self):
        """Set up subsections and subsection-related state."""
        self.preamble_section = DiffXPreambleSection(parent_section=self)
        self.meta_section = DiffXMetaSection(parent_section=self)
        self.files = []


class DiffXFileSection(ContainerOptionsMixin,
                       DiffOptionsMixin,
                       MetaOptionsMixin,
                       BaseDiffXContainerSection):
    """A file section within a change section.

    A file represents a change to a particular file. This may be a change to
    the file contents, or just to the metadata of the file.

    Metadata must always provide sufficient information for identifying and
    working with the file without having to parse the embedded diff.

    Files can be added through :py:meth:`DiffXChangeSection.add_file`.

    Attributes:
        diff (bytes):
            The file's Unified Diff contents.

            This may be a plain Unified Diff, or it may be a vendor-specific
            variant (such as a Git-style diff).

        diff_encoding (unicode):
            The encoding of the diff content.

            See :py:attr:`DiffXFileDiffSection.encoding`.

        diff_line_endings (unicode):
            The identifier for the type of line endings (DOS or UNIX)
            separating each line of the diff content.

            See :py:attr:`DiffXFileDiffSection.line_endings`.

        diff_section (DiffXFileDiffSection):
            The actual diff section. This will generally not be accessed
            directly.

        diff_type (unicode):
            The type of the diff (text or binary).

            See :py:attr:`DiffXFileDiffSection.type`.

        encoding (unicode):
            The default encoding for this section.

            This is sort of redundant with :py:attr:`meta_encoding`, as the
            metadata is the only content section affected by this encoding.
            However, it's here for consistency and future expansion.

            This may be ``None``, in which case the parent
            :py:attr:`DiffXChange.encoding` value will be used.

            Changing this will not affect the in-memory representation of any
            data, but it will affect how it's written.

        meta (dict):
            Metadata for the file.

        meta_encoding (unicode):
            The encoding used when reading/writing the metadata content in the
            file.

            See :py:attr:`DiffXMetaSection.encoding`.

        meta_section (DiffXMetaSection):
            The actual metadata section. This will generally not be accessed
            directly.
    """

    section_name = 'file'

    __slots__ = (
        'diff_section',
        'meta_section',
    )

    def generate_stats(self):
        """Generate statistics for the file section's metadata.

        This will gather statistics on the number of insertions, deletions,
        and total lines changed.

        Note that if the content in :py:attr:`diff` has a parse error, the data
        may be incorrect.

        This should only be run once the change is complete. Normally,
        callers will want to call :py:meth:`DiffX.generate_stats` instead.
        """
        if self.diff is None or self.diff_type == DiffType.BINARY:
            return

        if self.diff_line_endings:
            # This function can raise an exception, but only if the line
            # endings aren't a supported type. Our property already validates
            # this, so we should be fine, unless someone's done something
            # very wrong.
            newline = get_newline_for_type(self.diff_line_endings,
                                           encoding=self.diff_encoding)
        else:
            line_endings, newline = guess_line_endings(
                self.diff,
                encoding=self.diff_encoding)

        try:
            hunks_info = get_unified_diff_hunks(
                split_lines(data=self.diff,
                            newline=newline),
                ignore_garbage=True)
        except Exception as e:
            logger.error('Error parsing diff hunks for %r: %s',
                         self, e)
            return

        total_deletes = hunks_info['total_deletes']
        total_inserts = hunks_info['total_inserts']

        stats = {
            'deletions': total_deletes,
            'insertions': total_inserts,
            'lines changed': total_deletes + total_inserts,
        }

        # Set the computed stats. Don't override the key if there's something
        # already there, since it might contain some custom stats.
        if 'stats' in self.meta:
            self.meta['stats'].update(stats)
        else:
            self.meta['stats'] = stats

    def _setup_state(self):
        """Set up subsections and subsection-related state."""
        self.meta_section = DiffXMetaSection(parent_section=self)
        self.diff_section = DiffXFileDiffSection(parent_section=self)
        self.subsections = [
            self.meta_section,
            self.diff_section,
        ]


class DiffXPreambleSection(BaseDiffXContentSection):
    """A preamble section.

    The contents and options for this section will generally be accessed
    through the parent section's attributes.
    """

    section_name = 'preamble'
    data_type = six.text_type

    #: The encoding used when reading/writing the preamble content.
    #:
    #: Changing this will not affect the in-memory representation of the
    #: preamble, but it will affect how it's written.
    #:
    #: If ``None``, the ``encoding`` option of the section is used instead.
    #:
    #: Type:
    #:     unicode
    encoding = EncodingOptionProperty()

    #: The indentation applied to each line of the preamble content.
    #:
    #: This will be added to the beginning of each encoded line of the
    #: preamble when reading/writing the preamble content in the file.
    #:
    #: Changing this will not affect the in-memory representation of the
    #: preamble, but it will affect how it's written.
    #:
    #: If ``None``, no indentation will be applied.
    #:
    #: It's recommended to use an indentation of 4, to ensure preamble
    #: content does not impact parsing.
    #:
    #: Type:
    #:     int
    indent = PreambleIndentOptionProperty()

    #: The type of line endings used in the preamble content.
    #:
    #: Valid values are defined in :py:class:`~pydiffx.options.LineEndings`.
    #:
    #: This should be explicitly set if the type of line endings are known,
    #: as a hint to parsers.
    #:
    #: If ``None``, parsers will need to carefully handle newline detection
    #: based on their needs.
    #:
    #: Type:
    #:     unicode
    line_endings = LineEndingsOptionProperty()

    #: The mimetype representing the format of the preamble content.
    #:
    #: This can help consumers render the preamble content the way it was
    #: meant to be seen.
    #:
    #: Valid values are defined in
    #: :py:class:`~pydiffx.options.PreambleMimeType`.
    #:
    #: If ``None``, the preamble content is assumed to be plain text.
    #:
    #: Type:
    #:     unicode
    mimetype = PreambleMimeTypeOptionProperty()

    __slots__ = ()


class DiffXMetaSection(BaseDiffXContentSection):
    """A metadata section.

    The contents and options for this section will generally be accessed
    through the parent section's attributes.
    """

    default_options = {
        'format': MetaFormat.JSON,
    }

    section_name = 'meta'
    data_type = dict
    default_value = {}

    #: The encoding used when reading/writing the metadata content in the file.
    #:
    #: Changing this will not affect the in-memory representation of the
    #: metadata, but it will affect how it's written.
    #:
    #: If ``None``, the section's ``encoding`` will be used instead.
    #:
    #: Type:
    #:     unicode
    encoding = EncodingOptionProperty()

    #: The metadata format used when reading/writing the content in the file.
    #:
    #: This is available for future expansion. For now, it will always be
    #: :py:attr:`~pydiffx.options.MetaFormat.JSON`.
    #:
    #: Type:
    #:     unicode
    format = MetaFormatOptionProperty()

    __slots__ = ()


class DiffXFileDiffSection(BaseDiffXContentSection):
    """A diff content section.

    The contents and options for this section will generally be accessed
    through the parent section's attributes.
    """

    section_name = 'diff'
    data_type = bytes

    #: The encoding of the diff content.
    #:
    #: This _does not_ inherit from any other section's encoding. It must be
    #: explicitly provided for an encoding to be set.
    #:
    #: It's recommended that diff generators set this if they know the
    #: encoding of the file being changed.
    #:
    #: If ``None``, no encoding can be assumed.
    #:
    #: Type:
    #:     unicode
    encoding = EncodingOptionProperty()

    #: The type of line endings used in the diff content.
    #:
    #: Valid values are defined in :py:class:`~pydiffx.options.LineEndings`.
    #:
    #: This should be explicitly set if the type of line endings are known,
    #: as a hint to parsers. Diffs may legitimately contain newline characters
    #: of an alternate type that are not intended to be interpreted as
    #: newlines. This hint can help avoid issues parsing those diffs.
    #:
    #: If ``None``, parsers will need to carefully handle newline detection
    #: based on their needs.
    #:
    #: Type:
    #:     unicode
    line_endings = LineEndingsOptionProperty()

    #: The type of the diff (text or binary).
    #:
    #: Valid values are defined in :py:class:`~pydiffx.options.DiffType`.
    #:
    #: Type:
    #:     unicode
    type = DiffTypeOptionProperty()

    __slots__ = ()
