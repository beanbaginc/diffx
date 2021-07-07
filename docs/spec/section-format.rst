.. _diffx-section-format:

==========================
Section and Header Formats
==========================

.. _spec-section-types:

Section Types
-------------

There are two types of DiffX sections:

.. _spec-container-sections:

1. **Container Sections**

   These are sections that contain subsections, but no content of their
   own. The following are container sections:

   * :ref:`DiffX Main Section <spec-diffx-file-main>`
   * :ref:`Change Section <spec-change-main>`
   * :ref:`Changed File Section <spec-changed-file-main>`

.. _spec-content-sections:

2. **Content Sections**

   These are sections that contain content, but no subsections. The following
   are content sections:

   * :ref:`DiffX Preamble Section <spec-diffx-preamble>`
   * :ref:`DiffX Metadata Section <spec-diffx-metadata>`
   * :ref:`Change Preamble Section <spec-change-preamble>`
   * :ref:`Change Metadata Section <spec-change-metadata>`
   * :ref:`Changed File Metadata Section <spec-changed-file-metadata>`
   * :ref:`Changed File Diff Section <spec-changed-file-diff>`


.. _spec-section-headers:

Section Headers
---------------

Sections headers are indicated by a ``#`` at the start of the line, followed
by zero or more periods (``.``) to indicate the nesting level, followed by the
section name, ``:``, and then optionally any parsing options for that section.

They are always encoded as ASCII strings, and are unaffected by the parent
section's encoding (see :ref:`spec-encodings`).

Section headers can be parsed with this regex:

.. code-block:: text

    ^#(?P<level>\.*)(?P<name>[a-z]+):\s*(?P<options>.*)$

The options, if provided, are a comma-separated list of key/value pairs. The
key/value pairs are separated with a ``=``, without any spacing in-between.

.. note::

   It's recommended that diff generators write options in alphabetical order.

For instance, the following are valid sections:

.. code-block:: diffx

   #diffx: version=1.0
   #.change:
   #..meta: length=100, my-option=value, another-option=another-value

The following are not:

.. code-block:: text

   #diffx:
   .preamble
   #.change
   #..meta: option
   #..meta: my-option = value


.. _spec-common-section-options:

All sections have the following options:

Options
~~~~~~~

.. _spec-common-section-options-encoding:

``encoding`` (string -- *optional*):
    The text encoding for the section.

    See :ref:`spec-encodings` for encoding rules.

    .. code-block:: diffx
       :caption: **Example**

       #.change: type=encoding

``length`` (integer -- *required for content sections*):
    The length of the section's content/subsections in bytes.

    This is used by parsers to read the content for a section (up to but not
    including the following section or sub-section), regardless of the
    encoding used within the section.

    The length does not include the section header or its trailing newline,
    or any subsections. It's the length from the end of the header to the
    start of the next section/subsection.

    .. note::

       It does not contain the length of subsections in order to avoid needing
       to keep the entire diff in memory during generation (since each parent
       section would need to know the length of every sub-section).

    This is required for content sections (preambles, metadata, or diff
    content), but can be omitted for container sections (changes, files).

    .. code-block:: diffx
       :caption: **Example**

       #.meta: length=100


Metadata Section Format
-----------------------

Metadata sections can appear directly under the :ref:`DiffX main section
<spec-diffx-file-main>`, within a particular
:ref:`change section <spec-change-main>`, or within a particular
:ref:`changed file's section <spec-changed-file-main>`.

Metadata sections contain structured content that can be transformed into
key/values and lists.

.. note::

   YAML would be a good format, except it's too complex with too many
   inconsistencies and unnecessary features. Given the lack of any similar
   grammar out there, we have devised a very simple, easy-to-parse grammar
   that should resemble the metadata formats used in most diff formats.

   A formal design and rules for this is coming soon in this spec.

An example metadata section with key/value pairs, lists, and strings may look
like:

.. code-block:: diffx

   #.meta: length=135
   some key: "Some string"
   some boolean: true
   list key:
       - 123
       - "value"
   dictionary key:
       sub key:
           sub-sub key: "value"


Options
~~~~~~~

This includes the :ref:`common options <spec-common-section-options>` along
with:

``format`` (string -- *reserved*):
    This would indicate the metadata format (e.g., ``yaml``, ``json``,
    ``xml``, etc.).

    This is currently unused, and is reserved for future versions of the spec.
    For now, there's only the standard format defined in this spec, to keep
    parsing specific.

    We reserve this for future versions of the DiffX specification, in case
    a more suitable, standardized structured data format becomes available
    that may be worth supporting.


Custom Metadata
~~~~~~~~~~~~~~~

While this specification covers many standard metadata keys, certain types of
diffs, or diff generators, will need to provide custom metadata.

All custom metadata should be nested under an appropriate vendor key. For
example:

.. code-block:: diffx

   #.meta: length=39
   myscm:
       key1: "value"
       key2: 123


Vendors can propose to include custom metadata in the DiffX specification,
effectively promoting it out of the vendor key, if it may be useful outside of
the vendor's toolset.

