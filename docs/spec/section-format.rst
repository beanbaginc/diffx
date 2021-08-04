.. _spec-diffx-section-format:

===================
Section Definitions
===================

DiffX files are grouped into hierarchical sections, each of which are preceded
by a header that may list options that define how content or subsections are
parsed.


.. _spec-section-headers:

Section Headers
===============

Sections headers are indicated by a ``#`` at the start of the line, followed
by zero or more periods (``.``) to indicate the nesting level, followed by the
section name, ``:``, and then optionally any parsing options for that section.

They are always encoded as ASCII strings, and are unaffected by the parent
section's encoding (see :ref:`spec-encodings`).

Section headers can be parsed with this regex:

.. code-block:: text

    ^#(?P<level>\.{0,3})(?P<section_name>[a-z]+):\s*(?P<options>.*)$


For instance, the following are valid section headers:

.. code-block:: diffx

   #diffx: version=1.0
   #.change:
   #..meta: length=100, my-option=value, another-option=another-value

The following are not:

.. code-block:: text

   #diffx::
   .preamble
   #.change
   #....diff:


Header Options
--------------

Headers may contain options that inform the parser of how to treat nested
content or sections. The available options are dependent on the type of
section.

Options are key/value pairs, each pair separated by a comma and space
(``", "``), with the key and value separated by an equals sign (``"="``).
Spaces are not permitted on either side of the ``"="``.

Keys must be in the following format: ``[A-Za-z][A-Za-z0-9_-]*``

Values must be in the following format: ``[A-Za-z9-9/._-]+``

Each option pair can be parsed with this regex:

.. code-block:: text

   (?P<option_key>[A-Za-z][A-Za-z0-9_-]*)=(?P<option_value>[A-Za-z0-9/._-]+)

.. note::

   It's recommended that diff generators write options in alphabetical order,
   to ensure consistent generation between implementations.


The following are valid headers with options:

.. code-block:: diffx

   #diffx: version=1.0
   #.change:
   #..meta: length=100, my-option=value, another-option=another-value


The following are not:

.. code-block:: text

   #diffx: 1.0
   #..meta: option=100+
   #..meta: option=value,option2=value
   #..meta: option=value, option2=value:
   #..meta: _option=value
   #..meta: my-option = value


.. _spec-section-ids:

Section IDs
-----------

The following are valid section IDs (as combinations of ``level`` and
``section_name``):

* ``diffx``
* ``.meta``
* ``.preamble``
* ``.change``
* ``..meta``
* ``..preamble``
* ``..file``
* ``...meta``
* ``...diff``

Anything else should raise a parsing error.


.. _spec-section-order:

Section Order
=============

Sections must appear in a specific order. Some sections are optional, some
are required, and some may repeat themselves. You can refer to the order
listed in :ref:`spec-section-ids`, or see :ref:`spec-diffx-sections` for
detailed information on each section and their valid subsections.

DiffX parsers can use the following state tree to determine which sections
may appear next when parsing a section:

* ``diffx``

  * ``.preamble``
  * ``.meta``
  * ``.change``

* ``.preamble``

  * ``.meta``
  * ``.change``

* ``.meta``

  * ``.change``

* ``.change``

  * ``..preamble``
  * ``..meta``
  * ``..file``

* ``..preamble``

  * ``..file``

* ``..meta``

  * ``..change``
  * ``..file``

* ``..file``

  * ``...meta``

* ``...meta``

  * ``...diff``
  * ``..file``
  * ``.change``

* ``...diff``

  * ``..file``
  * ``.change``


.. _spec-section-types:

Section Types
=============

There are two types of DiffX sections:

1. :ref:`Container Sections <spec-container-sections>` --
   Sections that contain one or more subsections

2. :ref:`Content Sections <spec-content-sections>` --
   Sections that contain text content


.. _spec-container-sections:

Container Sections
------------------

Container sections contain no content of their own, but will contain one
or more subsections.

The following are the container sections defined in this specification:

* :ref:`DiffX Main Section <spec-diffx-file-main>`
* :ref:`Change Section <spec-change-main>`
* :ref:`Changed File Section <spec-changed-file-main>`


.. _spec-container-section-common-options:

.. rubric:: Options

Each container section may list the following option:

.. _spec-container-section-options-encoding:

``encoding`` (string -- *optional*):
    The default text encoding for child or grandchild preamble or metadata
    content sections.

    This will typically be set once on the :ref:`DiffX Main Section
    <spec-diffx-file-main>`. It's recommended that diff generators use
    ``utf-8``.

    Encodings are not automatically applied to the :ref:`Changed File Diff
    Section <spec-changed-file-diff>`.

    See :ref:`spec-encodings`.

    .. code-block:: diffx
       :caption: **Example**

       #.change: type=encoding


.. _spec-content-sections:

Content Sections
----------------

There are three types of content sections:

* :ref:`Preamble Sections <spec-preamble-sections>`
* :ref:`Metadata Sections <spec-metadata-sections>`
* :ref:`Changed File Diff Section <spec-changed-file-diff>`

The following are the content sections defined in this specification:

* :ref:`DiffX Preamble Section <spec-diffx-preamble>`
* :ref:`DiffX Metadata Section <spec-diffx-metadata>`
* :ref:`Change Preamble Section <spec-change-preamble>`
* :ref:`Change Metadata Section <spec-change-metadata>`
* :ref:`Changed File Metadata Section <spec-changed-file-metadata>`
* :ref:`Changed File Diff Section <spec-changed-file-diff>`


.. _spec-content-section-common-options:

.. rubric:: Options

Each container section supports the following options:

.. _spec-content-section-options-encoding:

``encoding`` (string -- *optional*):
    The default text encoding for the content of this section.

    This will typically be set once on the :ref:`DiffX Main Section
    <spec-diffx-file-main>`. It's recommended that diff generators use
    ``utf-8``. However, this can be useful if existing content using another
    encoding is being wrapped in DiffX.

    See :ref:`spec-encodings`.

    .. code-block:: diffx
       :caption: **Example**

       #..preamble: encoding=utf-32, length=217

``length`` (integer -- *required*):
    The length of the section's content in bytes.

    This is used by parsers to read the content for a section (up to but not
    including the following section or sub-section), regardless of the
    encoding used within the section.

    The length does not include the section header or its trailing newline,
    or any subsections. It's the length from the end of the header to the
    start of the next section/subsection.

    .. code-block:: diffx
       :caption: **Example**

       #.meta: length=100

.. _spec-content-section-options-line-endings:

``line_endings`` (string -- *recommended*):
    The known type of line endings used within the content.

    If specified, this must be either ``dos`` (:term:`CRLF` line endings --
    ``\r\n``) or ``unix`` (:term:`LF` line endings -- ``\n``).

    If a diff generator knows the type of line endings being used for content,
    then it should include this. This is particularly important for diff
    content, to aid diff parsers in splitting the lines and preserving or
    stripping the correct line endings.

    If this option is not specified, diff parsers should determine whether
    the first line ends with a :term:`CRLF` or :term:`LF` by reading up until
    the first :term:`LF` and determine whether it's preceded by a :term:`CR`.

    .. admonition:: Design Rationale

       Diffs have been encountered in production usage that use DOS line
       endings but include Line Feed characters as part of the line's data,
       and in these situations, knowing the line endings up-front will aid in
       parsing.

       Diffs have also been found that use a CRCRLF (``\r\r\n``) line feeds,
       as a result of a diff generator (in one known case, an older version of
       Perforce) being confused when diffing files from another operating
       system with non-native line endings. This edge case was considered but
       rejected, as it's ultimately a bug that should be handled before the
       diff is put into a DiffX file.


.. _spec-preamble-sections:

Preamble Sections
~~~~~~~~~~~~~~~~~

Metadata sections can appear directly under the :ref:`DiffX main section
<spec-diffx-file-main>` or within a particular
:ref:`change section <spec-change-main>`.

This section contains human-readable text, often representing a commit
message, a sumamry of a complete set of changes across several files or diffs,
or a merge commit's text.

This content is free-form text, but *cannot* contain anything that looks like
modifications to a diff file, DiffX section information, or lines specific
to a variant of a diff format. Tools should prefix each line with a set number
of spaces to avoid this, setting the :ref:`indent option
<spec-preamble-indent-mimetype>` to inform parsers of this number.

Preamble sections **must** end in a newline, in the section's encoding.

Preamble sections may also include a :ref:`mimetype option
<spec-preamble-option-mimetype>` help indicate whether the
text is something other than plain text (such as Markdown)

See :ref:`spec-encodings` for information on how to encode content within
preamble sections.


.. _spec-preamble-section-common-options:

.. rubric:: Options

This supports the :ref:`common content section options
<spec-content-section-common-options>`, along with:

.. _spec-preamble-indent-mimetype:

``indent`` (integer -- *recommended*):
    The number of spaces content is indented within this preamble.

    In order to prevent user-provided text from breaking parsing (by
    introducing DiffX headers or diff data), diff generators may want to
    indent the content a number of spaces. This option is a hint to parsers
    to say how many spaces should be removed from preamble text.

    A suggested value would be ``4``. If left off, the default is ``0``.

    When writing the file, indentation MUST be applied *after* encoding the
    text, to ensure maximum compatibility with diff parsers.

    When reading the file, indentation MUST be stripped *before* decoding
    the text.

    .. note::

       The order in which indentation is applied is important.

       Indentation must be ASCII spaces (``0x20``), applied after the
       content is encoded, and stripped before it's decoded, in order to
       avoid encoded characters at column 0 being picked up by diff parsers
       as syntax.

    .. code-block:: diffx
       :caption: **Example**

       #.preamble: indent=4, length=55
           This content won't break parsing if it adds:

           #.change:

.. _spec-preamble-option-mimetype:

``mimetype`` (string -- *optional*):
    The mimetype of the text, as a hint to the parser.

    Supported mimetypes at this time are:

    * ``text/plain`` (default)
    * ``text/markdown``

    Other types may be used in the future, but only if first covered by this
    specification. Note that consumers of the diff file are not required to
    render the text in these formats. It is merely a hint.

    .. code-block:: diffx
       :caption: **Example**

       #.preamble: length=40, mimetype=text/markdown
       Here is a **description** of the change.


.. _spec-metadata-sections:

Metadata Sections
~~~~~~~~~~~~~~~~~

Metadata sections can appear directly under the :ref:`DiffX main section
<spec-diffx-file-main>`, within a particular
:ref:`change section <spec-change-main>`, or within a particular
:ref:`changed file's section <spec-changed-file-main>`.

Metadata sections contain structured JSON content. It MUST be outputted in a
pretty-printed (rather than minified) format, with dictionary keys sorted and
4 space indentation. This is important for keeping output consistent across
JSON implementations.

Metadata sections **must** end in a newline, in the section's encoding.

.. admonition:: Design Rationale

   JSON is widely-supported in most languages. Its syntax is unlikely to
   cause any conflicts with existing diff parsers (due to ``{`` and ``}``
   having no special meaning in diffs, and indented content being sufficient
   to prevent any metadata content from appearing as DiffX, unified diff,
   or SCM-specific syntax.

An example metadata section with key/value pairs, lists, and strings may look
like:

.. code-block:: diffx

   #.meta: format=json, length=209
   {
       "dictionary key": {
           "sub key": {
               "sub-sub key": "value"
           }
       },
       "list key": [
          123,
          "value"
       ],
       "some boolean": true,
       "some key": "Some string"
   }


.. _spec-metadata-section-common-options:

.. rubric:: Options

This supports the :ref:`common content section options
<spec-content-section-common-options>`, along with:

``format`` (string -- *recommended*):
    This would indicate the metadata format. Currently, only ``json`` is
    officially supported, and is the default if not provided.

    It's recommended that diff generators always provide this option in order
    to be explicit about the metadata format. They must not introduce their
    own format options without proposing it for the DiffX specification.

    Diff parsers must always check for the presence of this option. If
    provided, it must confirm that the value is a format it can parse, and
    provide a suitable failure if it cannot understand the format.

    New format options will only be introduced along with a DiffX
    specification version change.


Custom Metadata
~~~~~~~~~~~~~~~

While this specification covers many standard metadata keys, certain types of
diffs, or diff generators, will need to provide custom metadata.

All custom metadata should be nested under an appropriate vendor key. For
example:

.. code-block:: diffx

   #.meta: format=json, length=70
   {
       "myscm": {
           "key1": "value",
           "key2": 123
       }
   }


Vendors can propose to include custom metadata in the DiffX specification,
effectively promoting it out of the vendor key, if it may be useful outside of
the vendor's toolset.
