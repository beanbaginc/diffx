.. _spec-diffx-sections:

=================
Section Hierarchy
=================

DiffX files are structured according to the following hierarchy:

* :ref:`DiffX Main Section <spec-diffx-main-header>` -- *required*

  * :ref:`DiffX Main Preamble Section <spec-diffx-preamble>` -- *optional*
  * :ref:`DiffX Main Metadata Section <spec-diffx-metadata>` -- *optional*
  * :ref:`Change (commit) Sections <spec-change-main>`
    -- *one or more required*

     * :ref:`Change Preamble Section <spec-change-preamble>` -- *optional*
     * :ref:`Change Metadata Section <spec-change-metadata>` -- *optional*
     * :ref:`File Sections <spec-changed-file-main>`
       -- *one or more required*

       * :ref:`File Metadata Section <spec-changed-file-metadata>`
         -- *required*
       * :ref:`File Diff Section <spec-changed-file-diff>` -- *optional*


.. _spec-diffx-file-main:

DiffX Main Section
==================

**Type:** :ref:`Container Section <spec-container-sections>`

These sections cover the very top of a DiffX file. Each of these sections can
only appear once per file.


.. _spec-diffx-main-header:

DiffX Main Header
-----------------

The first line of a DiffX file must be the start of the file section. This
indicates to the parser that this is a DiffX-formatted file, and can provide
options for parsing the file.

If not specified in a file, then the file cannot be treated as a DiffX file.


.. rubric:: Options

This supports the :ref:`common container section options
<spec-container-section-common-options>`, along with:

.. _spec-diffx-main-option-encoding:

``encoding`` (string -- *recommended*):
    The default text encoding of the DiffX file.

    This does *not* cover diff content, which is treated as binary data by
    default.

    See :ref:`spec-encodings` for encoding rules.

    .. important::

       If unspecified, the parser cannot assume a particular encoding. This is
       to match behavior with existing :term:`Unified Diff` files. It is
       strongly recommended that all tools that generate DiffX files specify
       an encoding option, with ``utf-8`` being the recommended encoding.

    .. code-block:: diffx
       :caption: **Example**

       #diffx: encoding=utf-8, version=1.0

``version`` (string -- *required*):
    The DiffX specification version (currently ``1.0``).

    .. code-block:: diffx
       :caption: **Example**

       #diffx: version=1.0


.. rubric:: Subsections

* :ref:`spec-diffx-preamble` (*optional*)
* :ref:`spec-diffx-metadata` (*optional*)
* :ref:`spec-changes-list` (*required*)


.. rubric:: Example

.. code-block:: diffx
   :caption: **Example**

   #diffx: encoding=utf-8, version=1.0
   ...


.. _spec-diffx-preamble:

DiffX Preamble Section
----------------------

**Type:** :ref:`Preamble Section <spec-preamble-sections>`

This section contains human-readable text describing the diff as a whole. This
can summarize a complete set of changes across several files or diffs, or
perhaps even a merge commit's text.

You'll often see Git commit messages (or similar) at the top of a
:term:`Unified Diff` file. Those do not belong in this section. Instead, place
those in the :ref:`Change Preamble section <spec-change-preamble>`.


.. rubric:: Options

This supports all of the :ref:`common preamble section options
<spec-preamble-section-common-options>`.


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.preamble: indent=4, length=80
       Any free-form text can go here.

       It can span as many lines as you like.


.. _spec-diffx-metadata:

DiffX Metadata Section
----------------------

**Type:** :ref:`Metadata Section <spec-metadata-sections>`

This section provides metadata on the diff file as a whole. It can contain
anything that the diff generator wants to provide.

While diff generators are welcome to add additional keys, they are encouraged
to either submit them for inclusion in this specification, or stick them under
a namespace. For instance, a hypothetical Git-specific key for a clone URL
would look like:

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.meta: format=json, length=82
   {
       "git": {
           "clone url": "https://github.com/beanbaginc/diffx"
       }
   }


.. rubric:: Options

This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.


.. rubric:: Metadata Keys

``stats`` (dictionary -- *optional*):
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

    .. code-block:: json
       :caption: **Example**

       {
           "stats": {
               "changed": 4,
               "files": 2,
               "insertions": 30,
               "deletions": 15
           }
       }


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.meta: format=json, length=99
   {
      "stats": {
       "changed": 4,
       "files": 2,
       "insertions": 30,
       "deletions": 15
      }
   }


.. _spec-changes-list:

Change Sections
===============


.. _spec-change-main:

Change Section
--------------

**Type:** :ref:`Container Section <spec-container-sections>`

A DiffX file will have one or more change sections. Each can represent a
simple change to a series of files (perhaps generated locally on the command
line) or a commit in a repository.

Each change section can have an optional preamble and metadata. It must have
one or more file sections.


.. rubric:: Subsections

* :ref:`spec-change-preamble` (*optional*)
* :ref:`spec-change-metadata` (*optional*)
* :ref:`spec-changed-files-list` (*required*)


.. rubric:: Options

This supports the :ref:`common container section options
<spec-container-section-common-options>`.


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.change:
   ...


.. _spec-change-preamble:

Change Preamble Section
-----------------------

**Type:** :ref:`Preamble Section <spec-preamble-sections>`

Many diffs based on commits contain a commit message before any file content.
We refer to this as the "preamble." This content is free-form text, but should
not contain anything that looks like modifications to a diff file, in order to
remain compatible with existing diff behavior.


.. rubric:: Options

This supports all of the :ref:`common preamble section options
<spec-preamble-section-common-options>`.


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.change:
   #..preamble: indent=4, length=111
       Any free-form text can go here.

       It can span as many lines as you like. Represents the commit message.


.. _spec-change-metadata:

Change Metadata Section
-----------------------

**Type:** :ref:`Metadata Section <spec-metadata-sections>`

The change metadata sections contains metadata on the commit/change the diff
represents, or anything else that the diff tool chooses to provide.

Diff generators are welcome to add additional keys, but are encouraged to
either submit them as a standard, or stick them under a namespace. For
instance, a hypothetical Git-specific key for a clone URL would look like:

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.change:
   #..meta: format=json, length=82
   {
       "git": {
           "clone url": "https://github.com/beanbaginc/diffx"
       }
   }


.. rubric:: Options

This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.


.. rubric:: Metadata Keys

``author`` (string -- *required*):
    The author of the commit/change, in the form of ``Full Name <email>``.

    .. code-block:: json
       :caption: **Example**

       {
           "author": "Ann Chovey <achovey@example.com>"
       }

``committer`` (string -- *recommended*):
    The committer of the commit/change, in the form of ``Full Name <email>``.
    This may or may not differ from ``author``.

    .. code-block:: json
       :caption: **Example**

       {
           "committer": "John Dory <jdory@example.com>"
       }

``committer date`` (string -- *recommended*):
    The date/time the commit/change was committed, in `ISO 8601`_ format.

    .. code-block:: json
       :caption: **Example**

       {
           "committer date": "2021-06-01T12:34:30Z"
       }

``date`` (string -- *required*):
    The date/time that the commit/change was written, in `ISO 8601`_ format.

    .. code-block:: json
       :caption: **Example**

       {
           "date": "2021-06-01T12:34:30Z"
       }

``id`` (string -- *recommended*):
    The unique ID of the change.

    This value depends on the revision control system. For example, the
    following would be used on these systems:

    * Git: The commit ID
    * Mercurial: The changeset ID
    * Subversion: The commit revision (if generating from an existing
      commit)

    Not all revision control systems may be able to supply an ID. For example,
    on Subversion, there's no ID associated with pending changes to a
    repository. In this case, ``id`` can either be ``null`` or ommitted
    entirely.

    .. code-block:: json
       :caption: **Example**

       {
           "id": "939dba397f0a577201f56ac72efb6f983ce69262"
       }

``parent ids`` (list of string -- *optional*):
    A list of parent change IDs.

    This value depends on the revision control system, and may contain
    zero or more values.

    For example, Git and Mercurial may list 1 parent ID in most cases, but
    may list 2 if representing a merge commit. The first commit in a tree
    may have no ID.

    Having this information can help tools that need to know the history in
    order to analyze or apply the change.

    .. code-block:: json
       :caption: **Example**

       {
           "parent ids": [
               "939dba397f0a577201f56ac72efb6f983ce69262"
           ]
       }

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

    .. code-block:: json
       :caption: **Example**

       {
           "stats": {
               "files": 10,
               "deletions": 75,
               "insertions": 43
           }
       }


.. _spec-changed-files-list:

Changed File Sections
=====================


.. _spec-changed-file-main:

Changed File Section
--------------------

**Type:** :ref:`Container Section <spec-container-sections>`

The file section simply contains two subsections: ``#...meta:`` and
``#...diff:``. The metadata section is required, but the diff section may be
optional, depending on the operation performed on the file.


.. rubric:: Subsections

* :ref:`spec-changed-file-metadata` (*required*)
* :ref:`spec-changed-file-diff` (*optional*)


.. rubric:: Options

This supports the :ref:`common container section options
<spec-container-section-common-options>`.


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.change:
   #..file:
   ...


.. _spec-changed-file-metadata:

Changed File Metadata Section
-----------------------------

**Type:** :ref:`Metadata Section <spec-metadata-sections>`

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

   #diffx: encoding=utf-8, version=1.0
   #.change:
   #..file:
   #...meta: format=json, length=65
   {
       "git": {
           "submodule": "vendor/somelibrary"
       }
   }


.. rubric:: Options

This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.


.. rubric:: Metadata Keys

.. _spec-changed-file-metadata-mimetype:

``mimetype`` (string or dictionary -- *recommended*):
    The mimetype of the file as a string. This is especially important for
    binary files.

    When possible, the encoding of the file should be recorded in the
    mimetype through the standard ``; charset=...`` parameter. For instance,
    ``text/plain; charset=utf-8``.

    The mimetype value can take one of two forms:

    1. The mimetype is the same between the original and modified files.

       If the mimetype is not changing (or the file is newly-added), then
       this will be a single value string.

       .. code-block:: json
          :caption: **Example**

          {
              "mimetype": "image/png"
          }

    2. The mimetype has changed.

       If the mimetype has changed, then this should contain the following
       subkeys instead:

       ``old`` (string -- *required*):
           The old mimetype of the file.

       ``new`` (string -- *required*):
           The new mimetype of the file.

       .. code-block:: json
          :caption: **Example**

          {
              "mimetype": {
                  "old": "text/plain; charset=utf-8",
                  "new": "text/html; charset=utf-8"
              }
          }

``op`` (string -- *recommended*):
    The operation performed on the file.

    If not specified, this defaults to ``modify``.

    The following values are supported:

    ``create``:
        The file is being created.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "create",
               "path": "/src/main.py"
           }

    ``delete``:
        The file is being deleted.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "delete",
               "path": "/src/compat.py"
           }

    ``modify`` (default):
        The file or its permissions are being modified (but not
        renamed/copied/moved).

        .. code-block:: json
           :caption: **Example**

           {
               "op": "modify",
               "path": "/src/tests.py"
           }

    ``copy``:
        The file is being copied without modifications. The ``path`` key
        must have ``old`` and ``new`` values.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "copy",
               "path": {
                   "old": "/images/logo.png",
                   "new": "/test-data/images/sample-image.png"
               }
           }

    ``move``:
        The file is being moved or renamed without modifications. The
        ``path`` key must have ``old`` and ``new`` values.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "move",
               "path": {
                   "old": "/src/tests.py",
                   "new": "/src/tests/test_utils.py"
               }
           }

    ``copy-modify``:
        The file is being copied with modifications. The ``path`` key must
        have ``old`` and ``new`` values.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "copy-modify",
               "path": {
                   "old": "/test-data/payload1.json",
                   "new": "/test-data/payload2.json"
               }
           }

    ``move-modify``:
        The file is being moved with modifications. The ``path`` key must
        have ``old`` and ``new`` values.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "move-modify",
               "path": {
                   "old": "/src/utils.py",
                   "new": "/src/encoding.py"
               }
           }

``path`` (string or dictionary -- *required*):
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


    .. code-block:: json
       :caption: **Example:** Modified file within a Subversion repository

       {
           "path": "/trunk/myproject/README"
       }


    .. code-block:: json
       :caption: **Example:** Renamed file within a Git repository

       {
           "path": {
               "old": "/src/README",
               "new": "/src/README.txt"
           }
       }


    .. code-block:: json
       :caption: **Example:** Renamed local file

       {
           "path": {
               "old": "lib/test.c",
               "new": "tests/test.c"
           }
       }


.. _spec-changed-file-metadata-revision:

``revision`` (dictionary -- *recommended*):
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


    .. code-block:: json
       :caption: **Example:** Numeric revisions

       {
           "path": "/src/main.py",
           "revision": {
               "old": "41",
               "new": "42"
           }
       }

    .. code-block:: json
       :caption: **Example:** SHA1 revisions

       {
           "path": "/src/main.py",
           "revision": {
               "old": "4f416cce335e2cf872f521f54af4abe65af5188a",
               "new": "214e857ee0d65bb289c976cb4f9a444b71f749b3"
           }
       }

    .. code-block:: json
       :caption: **Example:** Sample SCM-specific revision strings

       {
           "path": "/src/main.py",
           "revision": {
               "old": "change12945",
               "new": "change12968"
           }
       }

    .. code-block:: json
       :caption: **Example:** Only an old revision is available

       {
           "path": "/src/main.py",
           "revision": {
               "old": "8179510"
           }
       }

``stats`` (dictionary -- *optional*):
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

    ``similarity`` (string -- *optional*):
        The similarity percent between the old and new files (i.e., how much
        of the file remains the same). How this is calculated depends on the
        source code management system. This can include decimal places.

    .. code-block:: json
       :caption: **Example**

       {
           "path": "/src/main.py",
           "stats": {
               "total lines": 315,
               "lines changed": 35,
               "insertions": 22,
               "deletions": 3,
               "similarity": "98.89%"
           }
       }


.. _spec-changed-file-metadata-symlink-target:

``symlink target`` (string or dictionary -- *optional*):
    The target for a symlink (if :ref:`type
    <spec-changed-file-metadata-type>` is set to ``symlink``). Target paths
    are absolute on the filesystem, or relative to the symlink.

    If adding a new symlink, this will be a string containing the target path.

    If modifying an existing symlink to point to a new location, this will be
    a dictionary containing the following subkeys:

    ``old`` (string -- *required*):
        The old target path.

    ``new`` (string -- *required*):
        The new target path.

    .. code-block:: json
       :caption: **Example:** Changing a symlink's target.

       {
           "op": "create",
           "path": "/test-data/images",
           "type": "symlink",
           "symlink target": "static/images"
       }

    .. code-block:: json
       :caption: **Example:** Adding a file with permissions.

       {
           "op": "create",
           "path": "/test-data/fonts",
           "type": "symlink",
           "symlink target": "static/fonts"
       }


.. _spec-changed-file-metadata-type:

``type`` (string -- *recommended*):
    The type of entry designated by the path. This may help parsers to
    provide better error or output information, or to give patchers a better
    sense of the kinds of changes they should expect to make.

    ``directory``:
        The entry represents changes to a directory.

        This will most commonly be used to change permissions on a directory.

        .. code-block:: json
           :caption: **Example**

           {
               "path": "/src",
               "type": "directory",
               "unix file mode": {
                   "old": "0100700",
                   "new": "0100755"
               }
           }

    ``file`` (default):
        The entry represents a file. This is the default in diffs.

        .. code-block:: json
           :caption: **Example**

           {
               "path": "/src/main.py",
               "type": "file"
           }

    ``symlink``:
        The entry represents a symbolic link.

        This should not include changes to the contents of the file, but is
        likely to include :ref:`symlink target
        <spec-changed-file-metadata-symlink-target>` metadata.

        .. code-block:: json
           :caption: **Example**

           {
               "op": "create",
               "path": "/test-data/images",
               "type": "symlink",
               "symlink target": "static/images"
           }

    Custom types can be used if needed by the source code management system,
    though it will be up to them to process those types of changes.

    All custom types should be in the form of :samp:`{vendor}:{type}`. For
    example, ``svn:properties``.

``unix file mode`` (octal or dictionary -- *optional*):
    The UNIX file mode information for the file or directory.

    If adding a new file or directory, this will be a string containing the
    file mode.

    If modifying a file or directory, this will be a dictionary containing
    the following subkeys:

    ``old`` (string -- *required*):
        The original file mode in Octal format for the file (e.g.,
        ``"100644"``). This should be provided if modifying or deleting the
        file.

    ``new`` (string-- *required*):
        The new file mode in Octal format for the file. This should be
        provided if modifying or adding the file.

    .. code-block:: json
       :caption: **Example:** Changing a file's type

       {
           "path": "/src/main.py",
           "unix file mode":{
               "old": "0100644",
               "new": "0100755"
           }
       }

    .. code-block:: json
       :caption: **Example:** Adding a file with permissions.

       {
           "op": "create",
           "path": "/src/run-tests.sh",
           "unix file mode": "0100755"
       }


.. _spec-changed-file-diff:

Changed File Diff Section
-------------------------

**Type:** :ref:`Content Section <spec-content-sections>`

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


.. _spec-changed-file-diff-options:

.. rubric:: Options

This supports the :ref:`common content section options
<spec-content-section-common-options>`, along with:

``type`` (string -- *optional*):
    Indicates the content type of the section.

    Supported types are:

    ``binary``:
        This is a binary file.

    ``text`` (default):
        This is a text file. This is standard for diffs.

    .. code-block:: diffx
       :caption: **Example**

       #...diff: type=binary
       delta 729
       ...
       delta 224
       ...


.. rubric:: Example

.. code-block:: diffx

   #diffx: encoding=utf-8, version=1.0
   #.change:
   #..file:
   #...diff: length=642
   --- README
   +++ README
   @@ -7,7 +7,7 @@
   ...
   #..file:
   #...diff: length=12364, type=binary
   delta 729
   ...
   delta 224
   ...


.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
