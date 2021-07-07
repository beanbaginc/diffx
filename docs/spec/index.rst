.. _diffx-spec:

===============================
DiffX File Format Specification
===============================

Overview
========

DiffX files are a superset of the :term:`Unified Diff` format.
:term:`Context Diffs` or other base diff formats are not supported.

Filenames can end in :file:`.diffx` or in :file:`.diff`.

The file is broken into hierarchical sections, each preceded by a header
and containing options that contain encodings, length information, and
parsing hints relevant to the section.


.. toctree::
   :maxdepth: 3
   :numbered:

   section-format
   sections
   encodings
