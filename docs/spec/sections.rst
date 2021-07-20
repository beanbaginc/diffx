=================
DiffX files are structured according to the following hierarchy:

DiffX Main Header
-----------------
.. rubric:: Options
This supports the :ref:`common container section options
<spec-container-section-common-options>`, along with:
.. rubric:: Subsections
.. rubric:: Example
DiffX Preamble Section
----------------------
**Type:** :ref:`Preamble Section <spec-preamble-sections>`
.. rubric:: Options
This supports all of the :ref:`common preamble section options
<spec-preamble-section-common-options>`.
.. rubric:: Example
DiffX Metadata Section
----------------------
**Type:** :ref:`Metadata Section <spec-metadata-sections>`
to either submit them for inclusion in this specification, or stick them under
a namespace. For instance, a hypothetical Git-specific key for a clone URL
would look like:
   #.meta: format=json, length=82
   {
       "git": {
           "clone url": "https://github.com/beanbaginc/diffx"
       }
   }


.. rubric:: Options

This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.
.. rubric:: Metadata Keys
    .. code-block:: json
       {
           "stats": {
               "changed": 4,
               "files": 2,
               "insertions": 30,
               "deletions": 15
           }
       }
.. rubric:: Example
   #.meta: format=json, length=99
   {
      "stats": {
       "changed": 4,
       "files": 2,
       "insertions": 30,
       "deletions": 15
      }
   }
Change Section
--------------
.. rubric:: Subsections
.. rubric:: Options

This supports the :ref:`common container section options
<spec-container-section-common-options>`.


.. rubric:: Example
Change Preamble Section
-----------------------
**Type:** :ref:`Preamble Section <spec-preamble-sections>`
.. rubric:: Options
This supports all of the :ref:`common preamble section options
<spec-preamble-section-common-options>`.
.. rubric:: Example
Change Metadata Section
-----------------------
**Type:** :ref:`Metadata Section <spec-metadata-sections>`
   #..meta: format=json, length=82
   {
       "git": {
           "clone url": "https://github.com/beanbaginc/diffx"
       }
   }

.. rubric:: Options
This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.


.. rubric:: Metadata Keys
    .. code-block:: json
       {
           "author": "Ann Chovey <achovey@example.com>"
       }
    .. code-block:: json
       {
           "committer": "John Dory <jdory@example.com>"
       }
    .. code-block:: json
       {
           "committer date": "2021-06-01T12:34:30Z"
       }
    .. code-block:: json
       {
           "commit id": "939dba397f0a577201f56ac72efb6f983ce69262"
       }
    .. code-block:: json
       {
           "date": "2021-06-01T12:34:30Z"
       }
    .. code-block:: json
       {
           "parent commit ids": [
               "939dba397f0a577201f56ac72efb6f983ce69262"
           ]
       }
    .. code-block:: json
       {
           "stats": {
               "files": 10,
               "deletions": 75,
               "insertions": 43
           }
       }
Changed File Section
--------------------
.. rubric:: Subsections
.. rubric:: Options

This supports the :ref:`common container section options
<spec-container-section-common-options>`.


.. rubric:: Example
Changed File Metadata Section
-----------------------------
**Type:** :ref:`Metadata Section <spec-metadata-sections>`
   #...meta: format=json, length=65
   {
       "git": {
           "submodule": "vendor/somelibrary"
       }
   }


.. rubric:: Options
This supports all of the :ref:`common metadata section options
<spec-metadata-section-common-options>`.

.. rubric:: Metadata Keys
       .. code-block:: json
          {
              "mimetype": "image/png"
          }
       .. code-block:: json
          {
              "mimetype": {
                  "old": "text/plain; charset=utf-8",
                  "new": "text/html; charset=utf-8"
              }
          }
        .. code-block:: json
           {
               "op": "create",
               "path": "/src/main.py"
           }
        .. code-block:: json
           {
               "op": "delete",
               "path": "/src/compat.py"
           }
        .. code-block:: json
           {
               "op": "modify",
               "path": "/src/tests.py"
           }
        .. code-block:: json
           {
               "op": "copy",
               "path": {
                   "old": "/images/logo.png",
                   "new": "/test-data/images/sample-image.png"
               }
           }
        .. code-block:: json
           {
               "op": "move",
               "path": {
                   "old": "/src/tests.py",
                   "new": "/src/tests/test_utils.py"
               }
           }
        .. code-block:: json
           {
               "op": "copy-modify",
               "path": {
                   "old": "/test-data/payload1.json",
                   "new": "/test-data/payload2.json"
               }
           }
        .. code-block:: json
           {
               "op": "move-modify",
               "path": {
                   "old": "/src/utils.py",
                   "new": "/src/encoding.py"
               }
           }
    .. code-block:: json
       {
           "path": "/trunk/myproject/README"
       }
    .. code-block:: json
       {
           "path": {
               "old": "/src/README",
               "new": "/src/README.txt"
           }
       }
    .. code-block:: json
       {
           "path": {
               "old": "lib/test.c",
               "new": "tests/test.c"
           }
       }
    .. code-block:: json
       {
           "path": "/src/main.py",
           "revision": {
               "old": "41",
               "new": "42"
           }
       }
    .. code-block:: json
       {
           "path": "/src/main.py",
           "revision": {
               "old": "4f416cce335e2cf872f521f54af4abe65af5188a",
               "new": "214e857ee0d65bb289c976cb4f9a444b71f749b3"
           }
       }
    .. code-block:: json
       {
           "path": "/src/main.py",
           "revision": {
               "old": "change12945",
               "new": "change12968"
           }
       }
    .. code-block:: json
       {
           "path": "/src/main.py",
           "revision": {
               "old": "8179510"
           }
       }
    .. code-block:: json
       {
           "path": "/src/main.py",
           "stats": {
               "total lines": 315,
               "lines changed": 35,
               "insertions": 22,
               "deletions": 3,
               "similarity": "98.89%"
           }
       }
    .. code-block:: json
       {
           "op": "create",
           "path": "/test-data/images",
           "type": "symlink",
           "symlink target": "static/images"
       }
    .. code-block:: json
       {
           "op": "create",
           "path": "/test-data/fonts",
           "type": "symlink",
           "symlink target": "static/fonts"
       }
        .. code-block:: json
           {
               "path": "/src",
               "type": "directory",
               "unix file mode": {
                   "old": "0100700",
                   "new": "0100755"
               }
           }
        .. code-block:: json
           {
               "path": "/src/main.py",
               "type": "file"
           }
        .. code-block:: json
           {
               "op": "create",
               "path": "/test-data/images",
               "type": "symlink",
               "symlink target": "static/images"
           }
    ``old`` (string -- *required*):
        ``"100644"``). This should be provided if modifying or deleting the
    ``new`` (string-- *required*):
    .. code-block:: json
       {
           "path": "/src/main.py",
           "unix file mode":{
               "old": "0100644",
               "new": "0100755"
           }
       }
    .. code-block:: json
       {
           "op": "create",
           "path": "/src/run-tests.sh",
           "unix file mode": "0100755"
       }
Changed File Diff Section
-------------------------
.. rubric:: Options
This supports the :ref:`common content section options
<spec-content-section-common-options>`, along with:
.. rubric:: Example