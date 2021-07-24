.. _diffx-intro:

DiffX - Next-Generation Extensible Diff Format
==============================================

If you're a software developer, you've probably worked with diff files. Git
diffs, Subversion diffs, CVS diffs.. Some kind of diff. You probably haven't
given it a second thought, really. You make some changes, run a command, a
diff comes out. Maybe you hand it to someone, or apply it elsewhere, or put it
up for review.

Diff files show the differences between two text files, in the form of
inserted (``+``) and deleted (``-``) lines. Along with this, they contain some
basic information used to identify the file (usually just the name/relative
path within some part of the tree), maybe a timestamp or revision, and maybe
some other information.

Most people and tools work with :term:`Unified Diffs`. They look like this:

.. code-block:: diff

   --- readme    2016-01-26 16:29:12.000000000 -0800
   +++ readme    2016-01-31 11:54:32.000000000 -0800
   @@ -1 +1,3 @@
    Hello there
   +
   +Oh hi!

Or this:

.. code-block:: diff

   Index: readme
   ===================================================================
   RCS file: /cvsroot/readme,v
   retrieving version 1.1
   retrieving version 1.2
   diff -u -p -r1.1 -r1.2
   --- readme    26 Jan 2016 16:29:12 -0000        1.1
   +++ readme    31 Jan 2016 11:54:32 -0000        1.2
   @@ -1 +1,3 @@
    Hello there
   +
   +Oh hi!

Or this:

.. code-block:: diff

   diff --git a/readme b/readme
   index d6613f5..5b50866 100644
   --- a/readme
   +++ b/readme
   @@ -1 +1,3 @@
    Hello there
   +
   +Oh hi!

Or even this:

.. code-block:: diff

   Index: readme
   ===================================================================
   --- (revision 123)
   +++ (working copy)
   Property changes on: .
   -------------------------------------------------------------------
   Modified: myproperty
   ## -1 +1 ##
   -old value
   +new value

Or this!

.. code-block:: diff

   ==== //depot/proj/logo.png#1 ==A== /src/proj/logo.png ====
   Binary files /tmp/logo.png and /src/proj/logo.png differ


Here's the problem
==================

Unified Diffs themselves are not a viable standard for modern development.
They only standardize parts of what we consider to be a diff, namely the
``---``/``+++`` lines for file identification, ``@@ ... @@`` lines for
diff hunk offsets/sizes, and ``-``/``++`` for inserted/deleted lines.
They **don't** standardize encodings, revisions, metadata, or even how
filenames or paths are represented!

This makes it *very* hard for patch tools, code review tools, code analysis
tools, etc. to reliably parse any given diff and gather useful information,
other than the changed lines, particularly if they want to support multiple
types of source control systems. And there's a lot of good stuff in diff files
that some tools, like code review tools or patchers, want.

You should see what GNU Patch has to deal with.

Unified Diffs have not kept up with where the world is going. For instance:

* A single diff can't represent a list of commits
* There's no standard way to represent binary patches
* Diffs don't know about text encodings (which is more of a problem than you
  might think)
* Diffs don't have any standard format for arbitrary metadata, so everyone
  implements it their own way.

We're long past the point where diffs should be able to do all this. Tools
should be able to parse diffs in a standard way, and should be able to modify
them without worrying about breaking anything. It should be possible to load a
diff, any diff, using a Python module or Java package and pull information out
of it.

Unified Diffs aren't going away, and they don't need to. We just need to add
some extensibility to them. And that's completely doable, today.


Here's the good news
====================

Unified Diffs, by nature, are *very* forgiving, and they're everywhere, in
one form or another. As you've seen from the examples above, tools shove all
kinds of data into them. Patchers basically skip anything they don't
recognize. All they really lack is structure and standards.

Git's diffs are the closest things we have to a standard diff format (in that
both Git and Mercurial support it, and Subversion pretends to, but poorly),
and the closest things we have to a modern diff format (as they optionally
support binary diffs and have a general concept of metadata, though it's
largely Git-specific).

They're a good start, though still not formally defined. Still, we can build
upon this, taking some of the best parts from Git diffs and from other
standards, and using the forgiving nature of Unified Diffs to define a new,
structured Unified Diff format.


DiffX files
===========

We propose a new format called Extensible Diffs, or DiffX files for short.
These are **fully backwards-compatible with existing tools**, while also being
**future-proof** and remaining **human-readable**.

.. literalinclude:: spec/example-diffs/commit.diff
   :language: diffx

DiffX files are built on top of Unified Diffs, providing structure and
metadata that tools can use. Any DiffX file is a complete Unified Diff, and
can even contain all the legacy data that Git, Subversion, CVS, etc. may want
to store, while also structuring data in a way that any modern tool can easily
read from or write to using **standard parsing rules.**

Let's summarize. Here are some things DiffX offers:

* Standardized rules for parsing diffs
* Formalized storage and naming of metadata for the diff and for each commit
  and file within
* Ability to extend the format without breaking existing parsers
* Multiple commits can be represented in one diff file
* Git-compatible diffs of binary content
* Knowledge of text encodings for files and diff metadata
* Compatibility with all existing parsers and patchers (for all standard
  diff features -- new features will of course require support in tools, but
  can still be parsed)
* Mutability, allowing a tool to easily open a diff, record new data, and
  write it back out

DiffX is **not** designed to:

* Force all tools to support a brand new file format
* Break existing diffs in new tools or require tools to be rewritten
* Create any sort of vendor lock-in


Want to learn more?
===================

If you want to know more about what diffs are lacking, or how they differ from
each other (get it?), then read :ref:`problems-with-diffs`.

If you want to get your hands dirty, check out the :ref:`diffx-spec`.

See :ref:`example DiffX files <spec-diffx-examples>` to see this in action.

Other questions? We have a :ref:`FAQ <faq>` for you.


Implementations
===============

* Python: :ref:`pydiffx`


.. _diffx-users:

Who's using DiffX?
==================

* `Review Board`_ from `Beanbag`_. We built DiffX to solve long-standing
  problems we've encountered with diffs, and are baking support into all our
  products.


.. _Beanbag: https://www.beanbaginc.com/
.. _Review Board: https://www.reviewboard.org/


.. toctree::
   :hidden:

   problems-with-diffs
   spec/index
   pydiffx/index
   faq
   glossary
