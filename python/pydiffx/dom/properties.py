"""Property classes used for the DiffX Object Model.

These are considered internal API and should not be used outside of this
codebase.
"""

from __future__ import unicode_literals

import six

from pydiffx.errors import (DiffXOptionValueChoiceError,
                            DiffXOptionValueError)
from pydiffx.options import (DiffType,
                             LineEndings,
                             MetaFormat,
                             PreambleMimeType,
                             SpecVersion)


class OptionProperty(object):
    """A property for accessing and setting an option in a section."""

    #: The name of the option.
    #:
    #: Type:
    #:     unicode
    option_name = None

    #: The data type that's required.
    #:
    #: Type:
    #:     type
    data_type = None

    #: Valid choices for the value.
    #:
    #: This is optional.
    #:
    #: Type:
    #:     list of object
    choices = None

    #: The default value if not set.
    #:
    #: Type:
    #:     object
    default = None

    def __get__(self, instance, owner):
        """Return the value for the option.

        Args:
            instance (pydiffx.dom.objects.BaseDiffXContainerSection):
                The section instance that owns this property.

            owner (type):
                The section type that owns this property.

        Returns:
            object:
            The option value.
        """
        return instance.options.get(self.option_name, self.default)

    def __set__(self, instance, value):
        """Set the value for an option.

        Args:
            instance (pydiffx.dom.objects.BaseDiffXContainerSection):
                The section instance that owns this property.

            value (object):
                The value to set.

        Raises:
            TypeError:
                The value was an incorrect type.

            pydiffx.errors.DiffXOptionValueChoiceError:
                The value wasn't one of the available choices.
        """
        if not isinstance(value, self.data_type):
            raise DiffXOptionValueError(
                'Expected "%(option_name)s" to be a %(expected_type)s type, '
                'got %(type)s instead'
                % {
                    'option_name': self.option_name,
                    'expected_type': self.data_type,
                    'type': type(value),
                })

        if self.choices and value not in self.choices:
            raise DiffXOptionValueChoiceError(
                option=self.option_name,
                value=value,
                choices=self.choices)

        instance.options[self.option_name] = value


class SubsectionAttrProperty(object):
    """A property for accessing and setting state in a subsection.

    This will forward on to an attribute in a subsection.
    """

    def __init__(self, section_attr_name, attr_name):
        """Initialize the property.

        Args:
            section_attr_name (unicode):
                The name of the attribute for the content section to forward
                to.

            attr_name (unicode):
                The name of the attribute on the content section.
        """
        self.section_attr_name = section_attr_name
        self.attr_name = attr_name

    def __get__(self, instance, owner):
        """Return the attribute value from the content section.

        Args:
            instance (pydiffx.dom.objects.BaseDiffXContainerSection):
                The container section instance that owns this property.

            owner (type):
                The container section type that owns this property.

        Returns:
            object:
            The subsection's content.
        """
        section = getattr(instance, self.section_attr_name)
        return getattr(section, self.attr_name)

    def __set__(self, instance, value):
        """Set the attribute value on the content section.

        Args:
            instance (pydiffx.dom.objects.BaseDiffXContainerSection):
                The container section instance that owns this property.

            value (object):
                The content to set.

        Raises:
            TypeError:
                The content value was an incorrect type.
        """
        section = getattr(instance, self.section_attr_name)
        setattr(section, self.attr_name, value)


class DiffTypeOptionProperty(OptionProperty):
    """A property for a diff section's "type" option."""

    option_name = 'type'
    data_type = six.text_type
    choices = DiffType.VALID_VALUES


class EncodingOptionProperty(OptionProperty):
    """A property for a section's "encoding" option."""

    option_name = 'encoding'
    data_type = six.text_type


class LineEndingsOptionProperty(OptionProperty):
    """A property for a content section's "line_endings" option."""

    option_name = 'line_endings'
    data_type = six.text_type
    choices = LineEndings.VALID_VALUES


class MetaFormatOptionProperty(OptionProperty):
    """A property for a meta section's "format" option."""

    option_name = 'format'
    data_type = six.text_type
    choices = MetaFormat.VALID_VALUES


class VersionOptionProperty(OptionProperty):
    """A property for the DiffX version."""

    option_name = 'version'
    data_type = six.text_type
    choices = SpecVersion.VALID_VALUES


class PreambleIndentOptionProperty(OptionProperty):
    """A property for a preamble section's "indent" option."""

    option_name = 'indent'
    data_type = int


class PreambleMimeTypeOptionProperty(OptionProperty):
    """A property for a preamble section's "mimetypes" option."""

    option_name = 'mimetype'
    data_type = six.text_type
    choices = PreambleMimeType.VALID_VALUES


class ContainerOptionsMixin(object):
    """A mixin for adding common options for container sections."""

    encoding = EncodingOptionProperty()

    __slots__ = ()


class DiffOptionsMixin(object):
    """A mixin for adding option properties that forward to a diff section."""

    diff = SubsectionAttrProperty('diff_section', 'content')
    diff_encoding = SubsectionAttrProperty('diff_section', 'encoding')
    diff_line_endings = SubsectionAttrProperty('diff_section', 'line_endings')
    diff_type = SubsectionAttrProperty('diff_section', 'type')

    __slots__ = ()


class MetaOptionsMixin(object):
    """A mixin for adding option properties that forward to a meta section."""

    meta = SubsectionAttrProperty('meta_section', 'content')
    meta_encoding = SubsectionAttrProperty('meta_section', 'encoding')
    meta_format = SubsectionAttrProperty('meta_section', 'format')

    __slots__ = ()


class PreambleOptionsMixin(object):
    """A mixin for adding option properties that forward to a preamble section.
    """

    preamble = SubsectionAttrProperty('preamble_section',
                                      'content')
    preamble_encoding = SubsectionAttrProperty('preamble_section',
                                               'encoding')
    preamble_indent = SubsectionAttrProperty('preamble_section',
                                             'indent')
    preamble_line_endings = SubsectionAttrProperty('preamble_section',
                                                   'line_endings')
    preamble_mimetype = SubsectionAttrProperty('preamble_section',
                                               'mimetype')

    __slots__ = ()
