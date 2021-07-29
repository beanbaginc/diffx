* :ref:`DiffX Main Section <spec-diffx-main-header>` (*required*)
  * :ref:`DiffX Main Preamble Section <spec-diffx-preamble>` (*optional*)
  * :ref:`DiffX Main Metadata Section <spec-diffx-metadata>` (*optional*)
    (*one or more required*)
    * :ref:`Change Preamble Section <spec-change-preamble>` (*optional*)
    * :ref:`Change Metadata Section <spec-change-metadata>` (*optional*)
    * :ref:`File Sections <spec-changed-file-main>`
      (*one or more required*)
      * :ref:`File Metadata Section <spec-changed-file-metadata>` (*required*)
      * :ref:`File Diff Section <spec-changed-file-diff>` (*optional*)
.. _spec-diffx-metadata-stats:

.. _spec-change-metadata-author:

    This is the person or entity credited with making the changes represented
    in the diff.

    Diffs against a source code repository will usually have an author,
    whereas diffs against a local file might not. This field is not required,
    but is strongly recommended when suitable information is available.


.. _spec-change-metadata-author-date:

``author date`` (string -- *recommended*):
    The date/time that the commit/change was authored, in `ISO 8601`_ format.

    This can distinguish the date in which a commit was authored (e.g., when
    the diff was last generated, when the original commit was made, or when a
    change was put up for review) from the date in which it was officially
    placed in a repository.

    Not all source code management systems differentiate between when a change
    was authored and when it was committed to a repository. In this case, a
    diff generator may opt to either:

    1. Include the key and set it to the same value as :ref:`date
       <spec-change-metadata-date>`.
    2. Leave the key out entirely.

    If the key is not present, diff parsers should assume the value of
    :ref:`date <spec-change-metadata-date>` (if provided).

    If it is present, it is expected to contain a date equal to or older than
    :ref:`date <spec-change-metadata-date>` (which must also be present).
           "author date": "2021-05-24T18:21:06Z",
           "date": "2021-06-01T12:34:30Z"

.. _spec-change-metadata-committer:

``committer`` (string -- *recommended*):
    The committer of the commit/change, in the form of ``Full Name <email>``.

    This can distinguish the person or entity responsible for placing a
    change in a repository from the author of that change. For example, it
    may be a person or an identifier for an automated system that lands a
    change provided by an author in a review request or pull request.

    Not all source code management systems track authors and committers
    separately. In this case, a diff generator may opt to either:

    1. Include the key and set it to the same value as :ref:`author
       <spec-change-metadata-author>`.
    2. Leave the key out entirely.

    If the key is not present, diff parsers should assume the value of
    :ref:`author <spec-change-metadata-author>` (if present).

    If present, :ref:`author <spec-change-metadata-author>` must also be
    present.
           "author": "Ann Chovey <achovey@example.com>",
           "committer": "John Dory <jdory@example.com>"

.. _spec-change-metadata-date:

    The date/time the commit/change was placed in the repository, in `ISO
    8601`_ format.

    This can distinguish the date in which a commit was officially placed in
    a repository from the date in which the change was authored.

    For most source code management systems, this will be equal to the date
    of the commit.

    For changes to local code, this may be left out, or it may equal the
    date/time in which the diff was generated.


.. _spec-change-metadata-id:

    * **Git:** The commit ID
    * **Mercurial:** The changeset ID
    * **Subversion:** The commit revision (if generating from an existing
    repository. In this case, ``id`` can either be ``null`` or omitted

.. _spec-change-metadata-parent-ids:

    If present, :ref:`id <spec-change-metadata-id>` must also be present.


.. _spec-change-metadata-stats:


.. _spec-changed-file-metadata-op:


.. _spec-changed-file-metadata-path:

    The revision identifies the file, not the commit. In many systems (such as
    Subversion), these may the same identifier. In others (such as Git),
    they're separate.
        be ``null`` or omitted.
        file. Otherwise, it can be ``null`` or omitted.

.. _spec-changed-file-metadata-stats:


.. _spec-changed-file-metadata-unix-file-mode:
