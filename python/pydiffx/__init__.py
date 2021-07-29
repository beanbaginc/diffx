"""An implementation of DiffX, an extensible, structured Unified Diff format.

pydiffx makes it easy to work with `DiffX <https://diffx.org>`_ files.
This is a proposed standard for a new diff format that can contain
structured metadata, formal parsing rules, multiple commits and binary files,
while remaining backwards-compatible with existing Unified Diff parsers.

This module is the starting point for using pydiffx, and contains several
convenience imports:

.. autosummary::
   :nosignatures:

   ~pydiffx.dom.objects.DiffX
   ~pydiffx.options.DiffType
   ~pydiffx.options.LineEndings
   ~pydiffx.options.MetaFormat
   ~pydiffx.options.PreambleMimeType
   ~pydiffx.reader.DiffXReader
   ~pydiffx.writer.DiffXWriter
"""

from __future__ import unicode_literals

from pydiffx._version import (__version__,
                              __version_info__,
                              VERSION,
                              get_package_version,
                              get_version_string,
                              is_release)
from pydiffx.dom.objects import DiffX
from pydiffx.options import DiffType, LineEndings, MetaFormat, PreambleMimeType
from pydiffx.reader import DiffXReader
from pydiffx.writer import DiffXWriter


__all__ = (
    '__version__',
    '__version_info__',
    'DiffType',
    'DiffX',
    'DiffXReader',
    'DiffXWriter',
    'LineEndings',
    'MetaFormat',
    'PreambleMimeType',
    'VERSION',
    'get_package_version',
    'get_version_string',
    'is_release',
)

__autodoc_excludes__ = __all__
