.. _faq:

==========================
Frequently Asked Questions
==========================


How important is this, really?
==============================

If you're developing a code review tool or patcher or something that makes
use of diff files, you've probably had to deal with all the
:ref:`subtle things that can go wrong in a diff <problems-with-diffs>`.

If you're an end user working solely in Git, or in Subversion, or something
similar, you probably don't directly care. That being said, sometimes users
hit really funky problems that end up being due to command line options or
environmental problems mixed with the lack of information in a diff (no
knowledge of whether whitespace was being ignored, or the line endings being
used, or the text encoding). If tools had this information, they could be
smarter, and you wouldn't have to worry about as many things going wrong.

A structured, parsable format can only help.


Why not move to JSON or some other format for diffs?
====================================================

:term:`Unified Diffs` are a pretty decent format in many regards. Practically
any tool that understands diffs knows how to parse them, and they're very
forgiving in that they don't mind having unknown content outside of the range
of changes.

If we used an alternative format, it's likely nobody would ever use it.
Creating an incompatible format doesn't provide any real benefit, and would
fragment the development world and many current workflows.

By building on top of Unified Diffs, we get to keep compatibility with
existing tools, without having to rewrite the world. Everybody wins.


Why not use Git Bundles, or similar?
====================================

Git's bundles format is really just a way of taking part of a Git tree and
transporting it. You still need to have parent commits available on a clone.
You can't upload it to some service and expect it'll be able to work with it.

It's also a Git format, not something Mercurial, Subversion, etc. can make
use of. It's not an alternative to diffs.


How does DiffX retain backwards-compatibility?
==============================================

:term:`Unified Diffs` aren't at all strict about the content that exists
outside of a file header and a set of changed lines. This means you can add
basically anything before and after these parts of the diff. DiffX takes
advantage of this by adding identifiable markers that a parser can look for.

It also knows how to ignore any special data that may be specific to a Git
diff, Subversion diff, etc., preferring the DiffX data instead.

However, when you feed this back into something expecting an old-fashioned
Git diff or similar, that parser will ignore all the DiffX content that it
doesn't understand, and instead read in the legacy information.

This only happens if you generate a DiffX that contains the legacy
information, of course. DiffX files don't have to include these. It's really
up to the tool generating the diff.

So basically, we keep all the older content that non-DiffX tools look for, and
DiffX-capable tools will just ignore that content in favor of the new content.


What do DiffX files offer that Unified Diffs don't?
===================================================

Many things:

* A consistent way to parse, generate, and update diffs
* Multiple commits represented in one file
* Binary diffs
* Structured metadata in a standard format
* Per-file text encoding indicators
* Standard metadata for representing moved files, renames, attribute changes,
  and more.


What supports DiffX today?
==========================

DiffX is still in a specification and prototype phase. We are adding support
in `Review Board`_ and RBTools_.

If you're looking to add support as well, please `let us know`_ and we'll
add you to a list.


.. _Review Board: https://www.reviewboard.org/
.. _RBTools: https://www.reviewboard.org/downloads/rbtools/
.. _let us know: christian@beanbaginc.com
