.. _spec-encodings:

==============
Encoding Rules
==============

Historically, diffs have lacked any encoding information. A diff generated
on one computer could use an encoding for diff content or filenames that would
make it difficult to parse or apply on another computer.

To address this, DiffX has explicit support for encodings.

DiffX files follow these simple rules:

1. DiffX files have no default encoding. Tools *should* always
   :ref:`set an explicit encoding <spec-diffx-main-option-encoding>`
   (``utf-8`` is **strongly recommended**).

   If not specified, all content must be treated as 8-bit binary data, and
   tools should be careful when assuming the encoding of any content. This
   is to match behavior with existing :term:`Unified Diff` files.

2. :ref:`Section headers <spec-section-headers>` are *always* encoded as ASCII
   (no non-ASCII content is allowed in headers).

3. Sections inherit the encoding of their parent section, unless overridden
   with the :ref:`encoding option <spec-common-section-options-encoding>`.

4. Preambles and metadata in :ref:`content sections
   <spec-content-sections>` are encoded using their section's encoding.

5. :ref:`Diff sections <spec-changed-file-diff>` **do not** inherit their
   parent section's encoding, for compatibility with standard diff behavior.
   Instead, diff content should always be treated as 8-bit binary data, unless
   an explicit :ref:`encoding option <spec-common-section-options-encoding>`
   is defined for the section.

.. tip::

   DiffX parsers should prioritize content (such as filenames) in metadata
   sections over scraping content in :ref:`diff sections
   <spec-changed-file-diff>`, in order to avoid encoding issues.
