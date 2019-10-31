.. _diffx-spec:

===============================
DiffX File Format Specification
===============================

Overview
========

DiffX files are a superset of the :term:`Unified Diff` format.
:term:`Context Diffs` or other base diff formats are not supported.

Filenames can end in :file:`.diffx` or in :file:`.diff`.

The file is broken into hierarchical sections, and look roughly like this:

* :ref:`spec-diffx-main-header`

  * :ref:`spec-diffx-preamble`
  * :ref:`spec-diffx-metadata`
  * :ref:`One or more "changes" (aka commits) <spec-changes-list>`

    * :ref:`spec-change-main`
    * :ref:`spec-change-preamble`
    * :ref:`spec-change-metadata`
    * :ref:`One or more changed files <spec-changed-files-list>`

      * :ref:`spec-changed-file-main`
      * :ref:`spec-changed-file-metadata`
      * :ref:`spec-changed-file-diff`


Common Section Format
---------------------

Sections headers are indicated by a ``#`` at the start of the line, followed
by zero or more periods (``.``) to indicate the nesting level, followed by the
section name, ``:``, and then optionally any parsing options for that section.

Section headers can be parsed with this regex:

.. code-block:: text

    ^#(?P<level>\.*)(?P<name>[a-z]+):\s*(?P<options>.*)$

The options, if provided, are a comma-separated list of key/value pairs. The
key/value pairs are separated with a ``=``, without any spacing in-between.

Section headers are always encoded in the parent section's encoding.

For instance, the following are valid sections:

.. code-block:: diffx

   #diffx: version=1.0
   #.change:
   #..preamble:
   #..meta: my-option=value, another-option=another-value

The following are not:

.. code-block:: text

   .preamble
   #.change
   #..meta: option
   #..meta: my-option = value


.. _spec-common-section-options:

All sections have the following options:

Options (Recommended)
~~~~~~~~~~~~~~~~~~~~~

``encoding`` (string):
    The text encoding for the section.

    If not specified, the parent section's encoding is used.

    If no encoding is specified by any parent section, the section is treated
    as 8-bit binary data.

    See the special note for the :ref:`DiffX main section's encoding
    <spec-diffx-main-option-encoding>`.

``length`` (integer):
    The length of the section's own content in bytes.

    This is used by parsers to read the content for a section (up to but not
    including the following section or sub-section), regardless of the
    encoding used within the section.

    The length does not include the section header, its trailing newline, or
    any subsections. It skips subsections in order to reduce how much of a
    diff must be in memory when writing or parsing a DiffX file.

    While not strictly required, this is recommended and should always be used
    if the DiffX file or section specifies any non-8-bit encodings (such as
    UTF-16).

    If this is a section that does not include anything but subsections
    (i.e., the length is always 0), then the length can be omitted.


Metadata Section Format
-----------------------

Metadata sections can appear directly under the :ref:`DiffX main section
<spec-diffx-file-main>`, within a particular
:ref:`change section <spec-change-main>`, or within a particular
:ref:`changed file's section <spec-changed-file-main>`.

Metadata sections contain structured content that can be transformed into
key/values and lists. YAML is used as the format, as it allows for very
readable structured data, and has widely available support in most languages.
This is chosen instead of a custom format to keep implementation easy, and is
used instead of a more syntax-heavy format (like JSON), to enhance readability
and maintainability.

.. note::

   YAML-like syntax is a good start, but too complex to officially support.
   The plan is to define a simple grammar that is easy to parse.

An example metadata section with key/value pairs, lists, and strings may look
like:

.. code-block:: diffx

   #.meta:
   some key: Some string
   another key: "A quoted string"
   list key:
       - value
       - value
   dictionary key:
       sub key: value


This includes the :ref:`common options <spec-common-section-options>` along
with:


Options (Reserved)
~~~~~~~~~~~~~~~~~~

These are currently unused, and are reserved for future versions of the spec:

``format`` (string):
    This would indicate the metadata format (``yaml``, ``json``, ``xml``,
    etc.). This is not recommended for public use, though, as we want to
    keep parsing consistent. It's here so the format can adapt down the road
    as needs change.


Custom Metadata
~~~~~~~~~~~~~~~

While this specification covers many standard metadata keys, certain types of
diffs, or diff generators, will need to provide custom metadata.

All custom metadata should be nested under an appropriate vendor key. For
example:

.. code-block:: diffx

   #.meta: length=39
   myscm:
       key1: value
       key2: value


Vendors can propose to include custom metadata in the DiffX specification,
effectively promoting it out of the vendor key, if it may be useful outside of
the vendor's toolset.


.. _spec-diffx-file-main:

DiffX Main Sections
===================

These sections cover the very top of a DiffX file. Each of these sections can
only appear once per file.


.. _spec-diffx-main-header:

DiffX Main Header (Required)
----------------------------

The first line of a DiffX file must be the start of the file section. This
indicates to the parser that this is a DiffX-formatted file, and can provide
options for parsing the file.

If not specified in a file, then the file cannot be treated as a DiffX file.

This *only* supports the following options:


Options (Required)
~~~~~~~~~~~~~~~~~~

``version`` (string):
    The DiffX specification version (currently ``1.0``).


Options (Optional)
~~~~~~~~~~~~~~~~~~

.. _spec-diffx-main-option-encoding:

``encoding`` (string -- *recommended*):
    The default text encoding of the DiffX file (for example, ``utf-8``). This
    applies to all strings found within metadata and preambles.

    This does *not* cover diff content, which is treated as binary data by
    default.

    If unspecified, the parser cannot assume a particular encoding. This is to
    match behavior with existing :term:`Unified Diff` files. It is strongly
    recommended that all tools that generate DiffX files specify an encoding
    option. It is recommended that tools use ``utf-8``.


Subsections
~~~~~~~~~~~

* :ref:`spec-diffx-preamble`
* :ref:`spec-diffx-metadata`
* :ref:`spec-changes-list`


Example
~~~~~~~

.. code-block:: diffx
   :caption: **Example**

   #diffx: version=1.0, encoding=utf-8


.. _spec-diffx-preamble:

DiffX Preamble Section (Optional)
---------------------------------

The DiffX preamble contains human-readable text describing the diff as a
whole. This can summarize a complete set of changes across several files or
diffs, or perhaps even a merge commit's text.

This content is free-form text, but should not contain anything that looks
like modifications to a diff file, in order to remain compatible with existing
diff behavior.

The text must match the encoding (if specified) in the
:ref:`DiffX Main Header <spec-diffx-main-header>`.

You'll often see Git commit messages (or similar) at the top of a
:term:`Unified Diff` file. Those do not belong in this section. Instead, place
those in the :ref:`Change Preamble section <spec-change-preamble>`.

This includes the :ref:`common options <spec-common-section-options>` along
with:


Options (Optional)
~~~~~~~~~~~~~~~~~~

``format`` (string):
    The format of the text, as a hint to the parser. Must be one of
    ``plain`` or ``markdown``.

    Other types may be used in the future, but only if first covered by this
    specification. Note that consumers of the diff file are not required to
    render the text in these formats. It is merely a hint.

.. todo:: Override encoding?


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.preamble: length=72
   Any free-form text can go here.

   It can span as many lines as you like.


.. _spec-diffx-metadata:

DiffX Metadata Section (Optional)
---------------------------------

The DiffX metadata sections contains metadata on the diff file as a whole, and
can contain anything that the generating tool wants to provide.

Diff generators are welcome to add additional keys, but are encouraged to
either submit them as a standard, or stick them under a namespace. For
instance, a hypothetical Git-specific key for a clone URL would look like:

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.meta: length=60
   git:
       clone url: https://github.com/reviewboard/reviewboard


Keys (Optional)
~~~~~~~~~~~~~~~

``stats`` (dictionary):
    A dictionary of statistics on the commits, containing the following
    sub-keys:

    ``changes`` (integer -- *recommended*):
        The total number of changes in the diff.

    ``files`` (integer -- *required*):
        The total number of files across all changes in the diff.

    ``insertions`` (integer -- *recommended*):
        The total number of insertions made.

    ``deletions`` (integer -- *recommended*):
        The total number of deletions made.


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.meta: length=68
   stats:
       changed: 4
       files: 2
       insertions: 30
       deletions: 15


.. _spec-changes-list:

Change Sections
===============


.. _spec-change-main:

Change Section (Required)
-------------------------

A DiffX file has one or more change sections. Each can represent a simple
change to a series of files (perhaps generated locally on the command line) or
a commit in a repository.

Each change section can have an optional preamble and metadata. It must have
one or more file sections.


Subsections
~~~~~~~~~~~

* :ref:`spec-change-preamble`
* :ref:`spec-change-metadata`
* :ref:`spec-changed-files-list`


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:


.. _spec-change-preamble:

Change Preamble Section (Optional)
----------------------------------

Many diffs based on commits contain a commit message before any file content.
We refer to this as the "preamble." This content is free-form text, but should
not contain anything that looks like modifications to a diff file, in order to
remain compatible with existing diff behavior.

This includes the :ref:`common options <spec-common-section-options>` along
with:


Options (Optional)
~~~~~~~~~~~~~~~~~~

``format``:
    The format of the text, as a hint to the parser. Can be ``plain`` or
    ``markdown``. Other types may be used, but they should be added to this
    document. Note that consumers of the patch are not required to render the
    text in these formats. It is merely a hint.

    This defaults to ``plain``.


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:
   #..preamble: length=30
   Any free-form text can go here.

   It can span as many lines as you like. Represents the commit message.


.. _spec-change-metadata:

Change Metadata Section (Optional)
----------------------------------

The change metadata sections contains metadata on the commit/change the diff
represents, or anything else that the diff tool chooses to provide.

Diff generators are welcome to add additional keys, but are encouraged to
either submit them as a standard, or stick them under a namespace. For
instance, a hypothetical Git-specific key for a clone URL would look like:

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:
   #..meta: length=56
   git:
       clone url: https://github.com/beanbaginc/diffx


Keys (Optional)
~~~~~~~~~~~~~~~

``author`` (string -- *required*):
    The author of the commit/change, in the form of ``Full Name <email>``.

``committer`` (string -- *recommended*):
    The committer of the commit/change, in the form of ``Full Name <email>``.
    This may or may not differ from ``author``.

``committer date`` (string -- *recommended*):
    The date/time the commit/change was committed, in `ISO 8601`_ format.

``commit id`` (string -- *required*):
    The ID/revision of the commit/change. This depends on the revision control
    system.

``date`` (string -- *required*):
    The date/time that the commit/change was written, in `ISO 8601`_ format.

``parent commit ids`` (string -- *optional*):
    A list of parent commit/change IDs. There may be multiple parents if this
    is a merge commit. Having this information can help tools that need to
    know the history in order to analyze or apply the change.

``stats`` (dictionary -- *recommended*):
    A dictionary of statistics on the change.

    This can be useful information to provide to diff analytics tools to
    help quickly determine the size and scope of a change.

    ``files`` (integer -- *required*):
        The total number of files in the commit/change.

    ``insertions`` (integer -- *required*):
        The total number of inserted lines across all files.

    ``deletions`` (integer -- *required*):
        The total number of deleted lines across all files.


.. _spec-changed-files-list:

Changed File Sections
=====================


.. _spec-changed-file-main:

Changed File Section (Required)
------------------------------------

The file section simply contains two subsections: ``#...meta:`` and
``#...diff:``. The metadata section is required, but the diff section may be
optional, depending on the operation performed on the file.


Subsections
~~~~~~~~~~~

* :ref:`spec-changed-file-metadata`
* :ref:`spec-changed-file-diff`


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:
   #..file:


.. _spec-changed-file-metadata:

Changed File Metadata Section (Required)
----------------------------------------

The file metadata section contains metadata on the file. It may contain
information about the file itself, operations on the file, etc.

At a minimum, a filename must be provided. Unless otherwise specified, the
expectation is that the change is purely a content change in an existing file.
This is controlled by an ``op`` option.

For usage in a revision control system, the ``revision`` options must be
provided. It should be possible for the parser to have enough information
between the revision and the filename to fetch a copy of the file from a
matching repository.

The rest of the information is purely optional, but may be beneficial to
clients, particularly those wanting to display information on file mode
changes or that want to quickly display statistics on the file.

Diff generators are welcome to add additional keys, but are encouraged to
either submit them as a standard, or stick them under a namespace. For
instance, a hypothetical Git-specific key for a submodule reference would look
like:

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:
   #..file:
   #...meta: length=39
   git:
       submodule: vendor/somelibrary


Metadata Keys (Required)
~~~~~~~~~~~~~~~~~~~~~~~~

``path`` (string or dictionary):
    The path of the file either within a repository a relative path on the
    filesystem.

    If the file(s) are within a repository, this will be an absolute path.

    If the file(s) are outside of a repository, this will be a relative path
    based on the parent of the files.

    This can take one of two forms:

    1. A single string, if both the original and modified file have the same
       path.

    2. A dictionary, if the path has changed (renaming, moving, or copying a
       file).

       The dictionary would contain the following keys:

       ``old`` (string -- *required*):
           The path to the original file.

       ``new`` (string -- *required*):
           The path to the modified file.

    This is often the same value used in the ``---`` line (though without any
    special prefixes like Git's ``a/``). It may contain spaces, and must be in
    the encoding format used for the section.

    This **must not** contain revision information. That should be supplied in
    :ref:`revision <spec-changed-file-metadata-revision>`.


    .. code-block:: diffx
       :caption: **Example:** Modified file within a Subversion repository

       path: /trunk/myproject/README


    .. code-block:: diffx
       :caption: **Example:** Renamed file within a Git repository

       path:
           old: /src/README
           new: /src/README.txt


    .. code-block:: diffx
       :caption: **Example:** Renamed local file

       path:
           old: lib/test.c
           new: tests/test.c


Metadata Keys (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _spec-changed-file-metadata-mimetype:

``mimetype`` (string or dictionary):
    The mimetype of the file as a string. This is especially important for
    binary files.

    When possible, the encoding of the file should be recorded in the
    mimetype through the standard ``; charset=...`` parameter. For instance,
    ``text/plain; charset=utf-8``.

    The mimetype value can take one of two forms:

    1. The mimetype is the same between the original and modified files.

       If the mimetype is not changing (or the file is newly-added), then
       this will be a single value string.

       .. code-block:: diffx
          :caption: **Example**

          mimetype: image/png

    2. The mimetype has changed.

       If the mimetype has changed, then this should contain the following
       subkeys instead:

       ``old`` (string -- *required*):
           The old mimetype of the file.

       ``new`` (string -- *required*):
           The new mimetype of the file.

       .. code-block:: diffx
          :caption: **Example**

          mimetype:
              old: text/plain; charset=utf-8
              new: text/html; charset=utf-8

``op`` (string):
    The operation performed on the file.

    If not specified, this defaults to ``modify``.

    The following values are supported:

    ``create``:
        The file is being created.

        .. code-block:: diffx
           :caption: **Example**

           op: create
           path: /src/main.py

    ``delete``:
        The file is being deleted.

        .. code-block:: diffx
           :caption: **Example**

           op: delete
           path: /src/compat.py

    ``modify`` (default):
        The file or its permissions are being modified (but not
        renamed/copied/moved).

        .. code-block:: diffx
           :caption: **Example**

           op: modify
           path: /src/tests.py

    ``copy``:
        The file is being copied without modifications. The ``path`` key
        must have ``old`` and ``new`` values.

        .. code-block:: diffx
           :caption: **Example**

           op: copy
           path:
               old: /images/logo.png
               new: /test-data/images/sample-image.png

    ``move``:
        The file is being moved or renamed without modifications. The
        ``path`` key must have ``old`` and ``new`` values.

        .. code-block:: diffx
           :caption: **Example**

           op: move
           path:
               old: /src/tests.py
               new: /src/tests/test_utils.py

    ``copy-modify``:
        The file is being copied with modifications. The ``path`` key must
        have ``old`` and ``new`` values.

        .. code-block:: diffx
           :caption: **Example**

           op: copy-modify
           path:
               old: /test-data/payload1.json
               new: /test-data/payload2.json

    ``move-modify``:
        The file is being moved with modifications. The ``path`` key must
        have ``old`` and ``new`` values.

        .. code-block:: diffx
           :caption: **Example**

           op: move-modify
           path:
               old: /src/utils.py
               new: /src/encoding.py


.. _spec-changed-file-metadata-revision:

``revision`` (dictionary):
    Revision information for the file. This contains the following sub-keys:

    Revisions are dependent on the type of source code management system. They
    may be numeric IDs, SHA1 hashes, or any other indicator normally used
    for the system.

    The revision identifies the file, not the commit. In many systems
    (such as Subversion), these may the same identifier. In others (such as
    Git), they're separate.

    ``old`` (string -- *required*):
        The old revision of the file, before any modifications are made.
        The patch data must be able to be applied to the file at this
        revision.

    ``new`` (string -- *recommended*):
        The new revision of the file after the patch has been applied. This is
        optional, as it may not always be useful information, depending on the
        type of source code management system. Most will have a value to
        provide.


    .. code-block:: diffx
       :caption: **Example:** Numeric revisions

       path: /src/main.py
       revision:
           old: 41
           new: 42

    .. code-block:: diffx
       :caption: **Example:** SHA1 revisions

       path: /src/main.py
       revision:
           old: 4f416cce335e2cf872f521f54af4abe65af5188a
           new: 214e857ee0d65bb289c976cb4f9a444b71f749b3

    .. code-block:: diffx
       :caption: **Example:** Sample SCM-specific revision strings

       path: /src/main.py
       revision:
           old: change12945
           new: change12968

    .. code-block:: diffx
       :caption: **Example:** Only an old revision is available

       path: /src/main.py
       revision:
           old: 8179510


Metadata Keys (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~

``stats`` (dictionary):
    A dictionary of statistics on the file.

    This can be useful information to provide to diff analytics tools to
    help quickly determine how much of a file has changed.

    ``lines changed`` (integer -- *required*):
        The total number of lines changed in the file.

    ``insertions`` (integer -- *required*):
        The total number of inserted lines (``+``) in the file.

    ``deletions`` (integer -- *required*):
        The total number of deleted lines (``-``) in the file.

    ``total lines`` (integer -- *optional*):
        The total number of lines in the file.

    ``similarity`` (percentage -- *optional*):
        The similarity percent between the old and new files (i.e., how much
        of the file remains the same). How this is calculated depends on the
        source code management system. This can include decimal places.

    .. code-block:: diffx
       :caption: **Example**

       path: /src/main.py
       stats:
           total lines: 315
           lines changed: 35
           insertions: 22
           deletions: 3
           similarity: 98.89%

``unix file mode`` (dictionary):
    The UNIX file mode information for the file. This is a dictionary
    containing the following subkeys:

    ``old`` (octal -- *required*):
        The original file mode in Octal format for the file (e.g.,
        ``100644``). This should be provided if modifying or deleting the
        file.

    ``new`` (octal -- *required*):
        The new file mode in Octal format for the file. This should be
        provided if modifying or adding the file.

    .. code-block:: diffx
       :caption: **Example**

       path: /src/main.py
       unix file mode:
           old: 100644
           new: 100755


.. _spec-changed-file-diff:

Changed File Diff Section (Optional)
------------------------------------

If the file was added, modified, or deleted, the file diff section must
contain a representation of those changes.

This is designated by a ``#...diff:`` section.

This section supports traditional text-based diffs and binary diffs (following
the format used for Git binary diffs). The ``type`` option for the section is
used to specify the diff type (``text`` or ``binary``), and defaults to
``text`` if unspecified (see the :ref:`options
<spec-changed-file-diff-options>`) below.


Text Diffs
~~~~~~~~~~

For text diffs, the section contains the content people are accustomed to from
a Unified Diff. These are the ``---`` and ``+++`` lines with the diff hunks.

For compatibility purposes, this may also include any additional data normally
provided in that Unified Diff. For example, an ``Index:`` line, or Git's
``diff --git`` or CVS's ``RCS file:``. This allows a DiffX file to be used by
tools like :command:`git apply` without breaking.

DiffX parsers should always use the metadata section, if available, over
old-fashioned metadata in the diff section when processing a DiffX file.


Binary Diffs
~~~~~~~~~~~~

The diff section may also include binary diff data. This follows Git's binary
patch support, and may optionally include the Git-specific lines
(``diff --git``, ``index`` and ``GIT binary patch``) for compatibility.

To flag a binary diff section, add a ``type=binary`` option to the
``#...diff:`` section.


.. note::
   Determine if the Git approach is correct.

   This is still a work-in-progress. Git's binary patch support may be
   ideal, or there may be a better approach.


This includes the :ref:`common options <spec-common-section-options>` along
with:


.. _spec-changed-file-diff-options:

Options (Optional)
~~~~~~~~~~~~~~~~~~

``type`` (string):
    Indicates the content type of the section.

    Supported types are:

    ``binary``:
        This is a binary file.

    ``text`` (default):
        This is a text file. This is standard for diffs.


Example
~~~~~~~

.. code-block:: diffx

   #diffx: version=1.0, encoding=utf-8
   #.change:
   #..file:
   #...diff: length=642
   --- README
   +++ README
   @@ -7,7 +7,7 @@
   ...
   #..file: length=12364
   #...diff: type=binary
   delta 729
   ...
   delta 224
   ...


.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
