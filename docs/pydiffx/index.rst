.. _pydiffx:

=======
pydiffx
=======

pydiffx is a Python implementation of the :ref:`DiffX specification
<diffx-spec>`.

DiffX is a proposed specification for a structured version of :term:`Unified
Diffs` that contains metadata, standardized parsing, multi-commit diffs, and
binary diffs, in a format compatible with existing diff parsers.
:ref:`Learn more about DiffX <diffx-intro>`.

This module is a reference implementation designed to make it easy to read and
write DiffX files in any Python application.


Compatibility
=============

* Python 2.7
* Python 3.6
* Python 3.7
* Python 3.8
* Python 3.9
* Python 3.10
* Python 3.11


Installation
============

pydiffx can be installed on Python 2.7 and 3.6+ using :command:`pip`:

.. code-block:: shell

   pip install -U pydiffx


Using pydiffx
=============

DiffX files can be managed through one of two sets of interfaces:

* A streaming reader (:py:class:`pydiffx.reader.DiffXReader`) and
  writer (:py:class:`pydiffx.writer.DiffXWriter`) for progressively working
  with DiffX files of any size.

* A DiffX Object Model (:py:class:`pydiffx.dom.objects.DiffX`) for treating
  DiffX files as a mutable data structure.

To get familiar with these interfaces, follow our tutorials:

* :ref:`pydiffx-tutorial-diffxwriter`


.. toctree::
   :hidden:

   tutorials/index


Documentation
=============

.. toctree::
   :maxdepth: 3

   coderef/index
   releasenotes/index
