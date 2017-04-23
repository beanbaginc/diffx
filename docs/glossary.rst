.. _glossary:

========
Glossary
========


.. glossary::

   Unified Diff
   Unified Diffs
       A more-or-less standard way of representing changes to one or more
       text files. The standard part is the way it represents changes to
       lines, like:

       .. code-block:: diff

          @@ -1 +1,3 @@
           Hello there
          +
          +Oh hi!

       The rest of the format has no standardization. There are some general
       standard-ish markers that tools like GNU Patch understand, but there's
       a *lot* of variety here, so they're hard to parse. For instance:

       .. code-block:: diff

          --- readme    26 Jan 2016 16:29:12 -0000        1.1
          +++ readme    31 Jan 2016 11:54:32 -0000        1.2

       .. code-block:: diff

          --- readme    (revision 123)
          +++ readme    (working copy)

       .. code-block:: diff

          --- a/readme
          +++ b/readme

       This is one of the problems being solved by DiffX.
