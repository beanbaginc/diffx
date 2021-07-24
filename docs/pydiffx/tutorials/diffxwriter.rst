.. _pydiffx-tutorial-diffxwriter:

Writing DiffX Files using DiffXWriter
=====================================

:py:class:`pydiffx.writer.DiffXWriter` is a low-level class for incrementally
writing DiffX files to a stream (such as a file, an HTTP response, or as input
to another process).

When using this writer, the caller is responsible for ensuring that all
necessary metadata or other content is correct and present. Errors cannot be
caught up-front, and any failures may cause a failure to write mid-stream.


Step 1. Create the Writer
=========================

To start, construct an instance of :py:class:`pydiffx.writer.DiffXWriter` and
point it to an open byte stream. This will immediately write the main DiffX
header to the stream.

.. important::

   Make sure you're writing to a byte stream! If the stream expects Unicode
   content, you will encounter failures when writing.


.. code-block:: python

   from pydiffx import DiffXWriter

   with open('outfile.diff', 'wb') as fp:
       writer = DiffXWriter(fp)

       ...

Once you've set up the writer, you can optionally add a :ref:`preamble
<spec-diffx-preamble>` and/or :ref:`metadata <spec-diffx-metadata>` section
(in that order), followed by your first (required) :ref:`change section
<spec-change-main>`.


Step 2. Write a Preamble (Optional)
===================================

Preamble sections are free-form text that describe an overall set of changes.
The main DiffX section (which you're writing right now) can have a preamble
that describes the entirety of all changes made in the entire DiffX file

.. tip::

   This would be a good spot for a merge commit message or a review request
   or pull request description.

The preamble can be written using
:py:meth:`writer.write_preamble() <pydiffx.writer.DiffXWriter.write_preamble>`:

.. code-block:: python

   writer.write_preamble(
       'Here is a summary of the set of changes in this DiffX file.\n'
       '\n'
       'And here would be the multi-line description!')

Preamble text is considered to be plain text by default. If this instead
represents Markdown-formatted text, you'll want to specify that using the
``mimetype`` parameter, like so:

.. code-block:: python

   from pydiffx import PreambleMimeType

   ...

   writer.write_preamble(
       'This is some Markdown text.\n'
       '\n'
       'You can tell because of the **bold** and the '
       '[links](https://example.com).',
       mimetype=PreambleMimeType.MARKDOWN)

A few additional things to note:

1. The preamble will be encoded using UTF-8 (assuming a different encoding was
   set up when creating the writer).
2. the written text will be indented 4 spaces (which avoids issues with
   user-provided preamble text conflicting with other parts of the DiffX
   file).
3. The line endings are going to be consistent throughout the text, as either
   UNIX (LF -- ``\n``) or DOS (CRLF -- ``\r\n``) line endings.

All of these can be overridden when writing by using the optional parameters
to :py:meth:`DiffXWriter.write_preamble
<pydiffx.writer.DiffXWriter.write_preamble>`.


Step 3. Write Metadata (Optional)
=================================

Metadata sections contain information in JSON form that parsers can use to
determine, for instance, where a diff would apply, or which repository a diff
pertains to. See the :ref:`main metadata section documentation
<spec-diffx-metadata>` for the kind of information you would put here.

The metadata can be written using :py:meth:`writer.write_meta
<pydiffx.writer.DiffXWriter.write_meta>`:

.. code-block:: python

   writer.write_meta({
       'stats': {
           'changes': 1,
           'files': 2,
           'insertions': 27,
           'deletions': 5,
       }
   })

While any metadata can go in here, we **strongly recommend** putting anything
specific to your tool or revision control system under a key that's unique to
your tool. For example, custom Git data might be under a ``git`` key.


.. _pydiffx-tutorial-diffxwriter-begin-change:

Step 4. Begin a New Change
==========================

DiffX files must have at least one :ref:`Change section <spec-change-main>`.
These contain an optional preamble and/or metadata, and one or more modified
files.

To start writing a new Change section:

.. code-block:: python

   writer.new_change()

.. note::

   If representing multiple commits, you're going to end up calling this once
   per commit, but only after you've finished writing all the
   :ref:`File sections <spec-changed-file-main>` under this change.

To write a change's preamble or metadata, just use the same functions shown
above, and they'll be part of this new section.

See the information on :ref:`Change Preamble Sections <spec-change-preamble>`
and :ref:`Change Metadata Sections <spec-change-metadata>` for what should go
here.


.. _pydiffx-tutorial-diffxwriter-begin-file:

Step 5. Begin a New File
========================

You can now start writing :ref:`File sections <spec-changed-file-main>`, one
per file in the change.

To start writing a new File section:

.. code-block:: python

   writer.new_file()

File sections require a :ref:`File Metadata section
<spec-changed-file-metadata>`, which must contain information identifying the
file being changed. They *do not* contain a preamble section.


Step 6. Write a File's Diff (Optional)
======================================

If there are changes made to the contents of the file, you'll need to write
a :ref:`File Diff section <spec-changed-file-diff>`.

This will contain a byte string of the diff content, which may be a plain
:term:`Unified Diff`, or it may wrap a full diff variant, such as a Git-style
diff.

To write the diff:

.. code-block:: python

   writer.write_diff(
       b'--- src/main.py\t2021-07-13 16:40:05.442067927 -0800\n'
       b'+++ src/main.py\n2021-07-17 22:22:27.834102484 -0800\n'
       b'@@ -120,6 +120,6 @@\n'
       b'     verbosity = options["verbosity"]\n'
       b'\n'
       b'     if verbosity > 0:\n'
       b'-        print("Starting the build...")\n'
       b'+        logging.info("Starting the build...")\n'
       b'\n'
       b'     start_build(**options)\n'
       b'\n'
   )

Or, if we're dealing with a Git-style diff, it might look like:

.. code-block:: python

   writer.write_diff(
       b'diff --git a/src/main.py b/src/main.py\n'
       b'index aba891f..cc52f7 100644\n'
       b'--- a/src/main.py\n'
       b'+++ b/src/main.py\n'
       b'@@ -120,6 +120,6 @@\n'
       b'     verbosity = options["verbosity"]\n'
       b'\n'
       b'     if verbosity > 0:\n'
       b'-        print("Starting the build...")\n'
       b'+        logging.info("Starting the build...")\n'
       b'\n'
       b'     start_build(**options)\n'
       b'\n'
   )

.. note::

   The DiffX specification does not define the format of these diffs.

   It is completely okay to wrap another diff variant in here, and necessary
   if you need an existing parser to extract variant-specific information from
   the file.

There are some **really** useful options you can provide to help parsers
better understand and process this diff:

* Pass ``encoding=...`` if you know the encoding of the file.

  This will help DiffX-compatible tools process the file contents correctly,
  normalizing it for the local filesystem or the contents coming from a
  repository.

  This is **strongly recommended**, and one of the major benefits to
  representing changes as a DiffX file.

* Pass ``line_endings=`` if you know for sure that this file is intended to
  use UNIX (LF -- ``\n``) or DOS (CRLF -- ``\r\n``) line endings.

  This is **strongly recommended**, and will help parsers process the file if
  there's a mixture of line endings. This is a real-world problem, as some
  source code repositories contain, for example, ``\r\n`` as a line ending but
  ``\n`` as a regular character in the file.

  You can use either :py:attr:`LineEndings.UNIX
  <pydiffx.options.LineEndings.UNIX>` or :py:attr:`LineEndings.DOS
  <pydiffx.options.LineEndings.DOS>` as values.


Step 7: Rinse and Repeat
========================

You've now written a file! Bet that feels good.

You can now go back to :ref:`pydiffx-tutorial-diffxwriter-begin-file` to write
a new file in the Change section, or go back to
:ref:`pydiffx-tutorial-diffxwriter-begin-change` to write a new change full of
files.

Once you're done, close the stream. Your DiffX file was written!


Putting It All Together
=======================

Let's look at an example tying together everything we've learned:

.. code-block:: python

   from pydiffx import DiffXWriter, LineEndings, PreambleMimeType

   with open('outfile.diff', 'wb') as fp:
       writer = DiffXWriter(fp)
       writer.write_preamble(
           '89e6c98d92887913cadf06b2adb97f26cde4849b'

           'This file makes a bunch of changes over a couple of commits.\n'
           '\n'
           'And we are using **Markdown** to describe it.',
           mimetype=PreambleMimeType.MARKDOWN)
       writer.write_meta({
           'stats': {
               'changes': 1,
               'files': 2,
               'insertions': 3,
               'deletions': 2,
           }
       })

       writer.new_change()
       writer.write_preamble('Something very enlightening about commit #1.')
       writer.write_meta({
           'author': 'Christian Hammond <christian@example.com>',
           'id': 'a25e7b28af5e3184946068f432122c68c1a30b23',
           'date': '2021-07-17T19:26:31-07:00',
           'stats': {
               'files': 2,
               'insertions': 2,
               'deletions': 2,
           },
       })

       writer.new_file()
       writer.write_meta({
           'path': 'src/main.py',
           'revision': 'revision': {
               'old': '3f786850e387550fdab836ed7e6dc881de23001b',
               'new': '89e6c98d92887913cadf06b2adb97f26cde4849b',
           },
           'stats': {
               'lines': 1,
               'insertions': 1,
               'deletions': 1,
           },
       })
       writer.write_diff(
           b'--- src/main.py\n'
           b'+++ src/main.py\n'
           b'@@ -120,6 +120,6 @@\n'
           b'     verbosity = options["verbosity"]\n'
           b'\n'
           b'     if verbosity > 0:\n'
           b'-        print("Starting the build...")\n'
           b'+        logging.info("Starting the build...")\n'
           b'\n'
           b'     start_build(**options)\n'
           b'\n',
           encoding='utf-8',
           line_endings=LineEndings.UNIX)

       # And so on...
       writer.new_file()
       writer.write_meta(...)
       writer.write_diff(...)

       writer.new_change()
       writer.write_preamble(...)
       writer.write_meta(...)

       writer.new_file()
       writer.write_meta(...)
       writer.write_diff(...)


That's not so bad, right? Sure beats a bunch of ``print`` statements.

Now that you know how to write a DiffX file, you can begin integrating
:ref:`pydiffx` into your codebase. :ref:`We'll be happy to list you as a DiffX
user! <diffx-users>`
