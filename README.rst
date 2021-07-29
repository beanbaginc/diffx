DiffX - Next-Generation Extensible Diff Format
==============================================

This repositories contains the specification and implementations for the
DiffX_ file format.

DiffX is an open, backwards-compatible extension to Unified Diffs that offers:

* Standardized parsing rules
* Structured metadata for the diffs, commits, and files
* Multiple commits per diff
* Binary file changes
* Knowledge of text encodings and line endings
* Mutability, allowing a tool to easily open a diff, record new data, and
  write it back out
* Versioning and extensibility for future spec changes

This is all achieved without breaking existing patch tools or most other diff
processing tools. It's not a new format. It's an extension of Unified Diffs.

Our aim is to evolve Unified Diffs into a format that all tools can use,
helping us move beyond the current reality of dozens of vendor-specific diff
formats.

`Learn more about DiffX <https://diffx.org/>`_ and start making use of it
today in Python with `pydiffx <https://diffx.org/pydiffx/>`_.


Example
=======

.. code-block:: diff

    #diffx: encoding=utf-8, version=1.0
    #.change:
    #..preamble: indent=4, length=319, mimetype=text/markdown
        Convert legacy header building code to Python 3.
        
        Header building for messages used old Python 2.6-era list comprehensions
        with tuples rather than modern dictionary comprehensions in order to build
        a message list. This change modernizes that, and swaps out six for a
        3-friendly `.items()` call.
    #..meta: format=json, length=270
    {
        "author": "Christian Hammond <christian@example.com>",
        "committer": "Christian Hammond <christian@example.com>",
        "committer date": "2021-06-02T13:12:06-07:00",
        "date": "2021-06-01T19:26:31-07:00",
        "id": "a25e7b28af5e3184946068f432122c68c1a30b23"
    }
    #..file:
    #...meta: format=json, length=176
    {
        "path": "/src/message.py",
        "revision": {
            "new": "f814cf74766ba3e6d175254996072233ca18a690",
            "old": "9f6a412b3aee0a55808928b43f848202b4ee0f8d"
        }
    }
    #...diff: length=629
    --- /src/message.py
    +++ /src/message.py
    @@ -164,10 +164,10 @@
                 not isinstance(headers, MultiValueDict)):
                 # Instantiating a MultiValueDict from a dict does not ensure that
                 # values are lists, so we have to ensure that ourselves.
    -            headers = MultiValueDict(dict(
    -                (key, [value])
    -                for key, value in six.iteritems(headers)
    -            ))
    +            headers = MultiValueDict({
    +                key: [value]
    +                for key, value in headers.items()
    +            })

             if in_reply_to:
                 headers['In-Reply-To'] = in_reply_to


See our page on `example DiffX files`_ for more.


.. _example DiffX files: https://diffx.org/spec/examples.html


Documentation
=============

* `Introduction to DiffX <https://diffx.org/>`_
* `The Problems with Diffs <https://diffx.org/problems-with-diffs.html>`_
* `DiffX Specification <https://diffx.org/spec/>`_
* `FAQ <https://diffx.org/faq.html>`_


Implementations
===============

* **Python:** pydiffx_ (`documentation <https://diffx.org/pydiffx/>`_,
  `source code <https://github.com/beanbaginc/diffx/tree/master/python>`_)

We're planning to add more implementations. If you're working on a DiffX
implementation, please let us know!


.. _DiffX: https://diffx.org/
.. _pydiffx: https://diffx.org/pydiffx/
