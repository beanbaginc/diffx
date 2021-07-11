.. _diffx-spec-intro:

============
Introduction
============

DiffX files are a superset of the :term:`Unified Diff` format, intended to
bring structure, parsing rules, and common metadata for diffs while retaining
backwards-compatibility with existing software (such as tools designed to
work with diffs built by Git, Subversion, CVS, or other software).


Scope
=====

DiffX offers:

* Standardized rules for parsing diffs
* Formalized storage and naming of metadata for the diff and for each commit
  and file within
* Ability to extend the format without breaking existing parsers
* Multiple commits can be represented in one diff file
* Git-compatible diffs of binary content
* Knowledge of text encodings for files and diff metadata
* Compatibility with all existing parsers and patching tools (for all standard
  diff features – new features will of course require support in tools, but
  can still be parsed)
* Mutability, allowing a tool to easily open a diff, record new data, and
  write it back out

DiffX is not designed to:

* Force all tools to support a brand new file format
* Break existing diffs in new tools or require tools to be rewritten
* Create any sort of vendor lock-in


Filenames
=========

Filenames can end in :file:`.diffx` or in :file:`.diff`.

It is expected that most diffs will retain the :file:`.diff` file extension,
though it might make sense for some tools to optionally write or export a
:file:`.diffx` file extension to differentiate from non-DiffX diffs.

Software should never assume a file is or is not a DiffX file purely based on
the file extension. It must attempt to parse at least the file's
:ref:`#diffx: <spec-diffx-main-header>` header according to this specification
in order to determine the file format.


General File Structure
======================

DiffX files are broken into hierarchical :ref:`sections <spec-diffx-sections>`,
which may contain free-form text, metadata, diffs, or subsections.

Each section is preceded by a :ref:`section header
<spec-diffx-section-format>`, which may provide options to identify
:ref:`content encodings <spec-encodings>`, content length information, and
other parsing hints relevant to the section.

All DiffX-specific content has been designed in a way to all but ensure it
will be ignored by most diff parsers (including GNU patch) if DiffX is not
supported by the parser.
