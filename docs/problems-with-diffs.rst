.. _problems-with-diffs:

=======================
The Problems with Diffs
=======================

Diffs today have a number of problems that may not seem that obvious if you're
not working closely with them. Parsing them, generating them, passing them
between various systems.

We covered some of this on the front page, but let's go into more detail on
the problems with diffs today.


Revision control systems represent data differently
===================================================

There really isn't much of a standard in how you actually store information in
diffs. All you really can depend on are the original and modified filenames
(but not the format used to show them), and the file modifications.

A number of things have been bolted onto diffs and handled by GNU patch over
the years, but very little has become standardized. This makes it very
difficult to reliably store or parse metadata without writing a lot of custom
code.

Git, for instance, needs to track data such as file modes, SHA1s, similarity
information (for move/rename detection), and more. They do this with some
strings that appear above the typical ``---``/``+++`` filename blocks that Git
knows how to parse, but GNU patch will ignore. For instance, to handle a file
move, you might get:

.. code-block:: diff

   diff --git a/README b/README2
   index 91bf7ab..dd93b71 100644
   similarity index 95%
   rename from README
   rename to README2
   --- a/README
   +++ b/README

Perforce, on the other hand, doesn't encode any information on revisions or
file modes, requiring that tools add their own metadata to the files. For
example, Review Board adds this additional data for a moved file with
changes (based on an existing extended Perforce diff format it adopted for
compatibility):

.. code-block:: diff

   Moved from: //depot/project/README
   Moved to: //depot/project/README2
   --- //depot/project/README  //depot/project/README#2
   +++ //depot/project/README2  12-10-83 13:40:05

Or without changes:

.. code-block:: diff

   ==== //depot/project/README#2 ==MV== //depot/project/README2 ====

Let's look at a simple diff in CVS:

.. code-block:: diff

   Index: README
   ===================================================================
   RCS file: /path/to/README,v
   retrieving revision 1.1
   retrieving revision 1.2
   diff -u -p -r1.1 -r1.2
   --- README    07 May 2014 08:50:30 -0000      1.1
   +++ README    10 Dec 2014 13:40:05 -0000      1.2

No real consistency, and the next revision control system that comes along
will probably end up injecting its own arbitrary content in diffs.


Operations like moves/deletes are inconsistent
==============================================

Diffs are pretty good at handling file modifications and, generally, the
introduction of new files. Unfortunately, they fall short at handling other
simple operations, like a deleted file or a moved/renamed file. Again,
different implementations end up representing these operations in different
ways.

For some time, Perforce's :command:`p4 diff` wouldn't show deleted file
content, prompting some companies to write their own wrapper.

TFS won't even show added or deleted content natively.

Git represents deleted files with:

.. code-block:: diff

   diff --git a/README b/README
   deleted file mode 100644
   index 91bf7ab..0000000
   --- a/README
   +++ /dev/null
   @@ -1,3 +0,0 @@
   -All the lines
   -are deleted
   -one by one

Subversion uses:

.. code-block:: diff

   Index: README
   ===================================================================
   --- README      (revision 4)
   +++ README      (working copy)
   @@ -1,3 +0,0 @@
   -All the lines
   -are deleted
   -one by one

Most are consistent with the removal of the lines, but that's about it. Some
have metadata explicitly indicating a delete, but others don't differentiate
between deleted files and removing all lines from files.

Copies/moves are worse. There is no standard at all, and SVN/Git/etc. have
been forced to work around this by inventing their own formats and command
line switches, which the patch tool needs to have special knowledge of.


No support for binary files
===========================

Binary files have no official support in diffs. Git has its own support for
binary files in diffs, but GNU patch rejects them, requiring :command:`git
apply` to be used instead.

Very few systems even try to support binary files in diffs, instead simply
adding a marker explaining the file has unspecified binary changes. This
usually says ``Binary files <file> and <file> differ``.

In the world of binary files in diffs, Git's way of handling them seems to be
the current de-facto standard, as :command:`hg diff --git` will generate
these changes as well. Still, it's not very wide-spread yet.


Text encodings are unclear
==========================

When you view a diff, you have to essentially guess at the encoding. This can
be done by trying a few encodings, or assuming an encoding if you know the
encodings in the repository the diff is being applied to. This is pretty bad,
though. Today, there's just no way to consistently know for sure how to
properly decode text in a diff.

This manifests in the wild when working with international teams and different
languages and sets of editors. If the encoding of a file has been changed
from, say, UTF-8 to zh_CN, then any tool working with the diff and the source
files will break, and it's hard to diagnose why at first.


They're limited to single commits
=================================

Tools will generally output a separate diff file for every commit, which means
more files to keep track of and e-mail around, and means that the ordering
must be respected when applying the changes or when uploading files to any
services or software that needs to operate on them. This isn't a huge problem
in practice, but ideally, a diff could just contain each commit.

DVCS is basically the standard for all modern source code management
solutions, but that wasn't the case when Unified Diffs were first created. A
new diff format should account for this.


Fixing these problems
=====================

These problems are all solvable, without breaking existing diffs.

Diffs have a lot of flexibility in what kind of "garbage" data is stored, so
long as the diff contains at least one genuine modification to a file. Git,
SVN, etc. diffs leverage this to store additional data.

We're leveraging this as well. We store an encoding marker at the top of the
file and to break the diff into sections. Sections can contain options to
control parsing behavior, metadata on the content represented by the section,
and the content itself. The content may be standard text diff data (with or
without implementation-specific metadata) or binary diff content.

Through this, it's also possible to extend the format by defining custom
metadata, custom sections, and to specify custom parsing behavior in sections.

Diffs also don't have limits as to how many times a file shows up with
modifications. Tools like :command:`patch` and :command:`diffstat` are more
than happy to work with any entries that come up. That means we can safely
store the diffs for a series of commits in one file and still be able to patch
safely.

This is all done without breaking parsing/patching behavior for existing
diffs, or causing incompatibilities between DiffX files and existing tools.
