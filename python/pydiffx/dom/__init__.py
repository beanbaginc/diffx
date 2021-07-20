"""The DiffX Object Model and high-level reader/writer.

The DiffX Object Model makes it easy to create or process DiffX files. They can
be constructed up-front and then written out, or loaded from data into a series
of objects for processing.

This module provides convenience imports for the DiffX Object Model:

.. autosummary::
   :nosignatures:

   ~pydiffx.dom.objects.DiffX

Consumers will want to start with the documentation for
:py:class:`~pydiffx.dom.objects.DiffX`.
"""

from __future__ import unicode_literals

from pydiffx.dom.objects import DiffX


__all__ = (
    'DiffX',
)

__autodoc_excludes__ = __all__
