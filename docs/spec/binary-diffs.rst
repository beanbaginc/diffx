.. _spec-binary-diffs:

============
Binary Diffs
============

DiffX officially supports three types of binary diff formats:

1. VCDIFF_ binary diffs (recommended)
2. Git-compatible Literal binary diffs
3. Git-compatible Delta binary diffs

It's recommended that new diffs make use of the VCDIFF format. The Git delta
and literal binary diff formats are available for backward compatibility with
Git-compatible diff implementations.

These formats are represented in similar ways. This page will discuss the
common and diff-specific encoding and decoding rules for binary diffs.


.. _VCDIFF: https://www.rfc-editor.org/rfc/rfc3284.html


Encoding/Decoding Basics
========================

All three binary patch formats contain up to two payloads:

1. The application (forward) patch payload.

   This is used to patch the binary file, transforming the original into the
   patched copy.

2. The reverse (backward) patch payload.

   This is used to reverse the patch, transforming the patched copy back into
   the original.

For the VCDIFF binary diff, the reverse patch payload is optional. For the Git
binary diffs, they are required, for backward compatibility.

.. note::

   If the reverse payload is not available, then changes to a patched binary
   file cannot be undone.

Binary patches are in the following form:

.. code-block:: text

   <modified_type> <modified_raw_payload_length>
   <modified_payload>

   <original_type> <original_raw_payload_length>
   <original_payload>

The contents will be in ASCII format.

Valid types and payload formats are dependent on the type of binary diff:

* For VCDIFFs, ``modified_type`` will be ``vcdiff-apply`` and
  ``original_type`` will be ``vcdiff-reverse``.

* For Git Literal binary diffs, both ``modified_type`` and ``original_type``
  will be ``literal``.

* For Git Delta binary diffs, both ``modified_type`` and ``original_type``
  will be ``delta``.

``modified_raw_payload_length`` and ``original_raw_payload_length`` will be
the lengths of the raw modified and original payloads before compression and
encoding.


Binary Payloads
---------------

All three formats use the following format for payload data:

.. code-block:: text

   <len_c><data>
   ...

Each line represents up to 52 bytes of pre-encoded data. There may be an
unlimited number of lines. They contain the following fields:

* ``len_c`` is a line length character. This encodes the length of the
  (pre-encoded) data written on this line. See
  :ref:`spec-binary-diffs-git-line-len-chars` below.

* ``data`` is Base85_-encoded data for this line.

This format is memory-efficient, allowing data to be progressively written
to or read from a DiffX file without needing to keep the entire contents in
memory for the Base85_-encode/decode steps.

Depending on the binary diff format, additional information may be included.
This will be documented below for each binary diff format.


.. _Base85: https://en.wikipedia.org/wiki/Ascii85


Encoding Logic
~~~~~~~~~~~~~~

To encode data:

1. Prepare the data to encode.

   Data preparation depends on the diff format:

   * For VCDIFFs, generate a VCDIFF of the file contents and then compress it
     with zlib.

   * For Git Literal binary diffs, read the file data and then compress it
     with zlib.

   * For Git Delta binary diffs, generate a delta set of instructions for
     patching the file, and then compress it with zlib.

2. For each 52-byte chunk of prepared data:

   1. Generate and write a :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>` representing the chunk length.

   2. Generate and write Base85_-encoded data for the chunk.


Decoding Logic
~~~~~~~~~~~~~~

To decode data:

1. For each line:

   1. Read and decode 1 byte for the :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>`.

   2. Read and Base85_-decode remaining bytes for the line.

2. Process decoded data.

   This depends on the diff format:

   * For VCDIFFs, zlib-decompress the data and read as a VCDIFF.

   * For Git Literal binary diffs, zlib-decompress the data and write to the
     patched binary file.

   * For Git Delta binary diffs, zlib-decompress the data, process the
     resulting delta instructions, and apply to the patched binary file.


.. _spec-binary-diffs-git-line-len-chars:

Line Length Characters
----------------------

Each encoded line in a binary diff payload is prefixed by a line length
character. This encodes the length of the compressed (but not encoded) data
for the line.

Line length characters always represent a value between 1 and 52:

* A value of ``A-Z`` represents a number between 1..26.

* A value of ``a-z`` represents a number between 27..52.


Encoding Logic
~~~~~~~~~~~~~~

To encode a length to a line length character:

1. If ``line_length`` between 1..26:

   1. Set to ASCII character for
      ``line_length + (ASCII value of 'A') - 1``

2. Else if ``line_length`` between 27..52:

   1. Set to ASCII character for
      ``line_length + (ASCII value of 'a') - 1 - 26``


.. rubric:: Example in Python

.. code-block:: python

   LEN_LOWER = ord('Z') - ord('A')  # 26

   assert 1 <= unencoded_line_len <= 52

   if unencoded_line_len <= LEN_LOWER:
       len_c = chr(unencoded_line_len + ord('A') - 1)
   else:
       len_c = chr(unencoded_line_len + ord('a') - 1 - LEN_LOWER)


Decoding Logic
~~~~~~~~~~~~~~

To decode a length from a line length character:

1. Set length to ASCII value of character.

2. If length is between 1..26:

   1. Increment length by ``1 - (ASCII value of 'A')``.

3. Else if length is between 27..52:

   1. Increment length by ``1 - (ASCII value of 'a') + 26``


.. rubric:: Example in Python

.. code-block:: python

   LEN_LOWER = ord('Z') - ord('A')  # 26

   unencoded_line_length = ord(len_c)

   if unencoded_line_length <= LEN_LOWER:
       unencoded_line_length += 1 - ord('A')
   else:
        unencoded_line_length += 1 - ord('a') + LEN_LOWER


.. _spec-binary-diffs-vcdiffs:

VCDIFFs
=======

DiffX recommends using VCDIFF files to represent binary diffs.

The VCDIFF_ format itself is covered under `RFC 3284
<https://datatracker.ietf.org/doc/html/rfc3284>`_, and will not be documented
here. We recommend using an existing VCDIFF implementation as part of your
DiffX implementation.

A DiffX-stored VCDIFF is stored in the following format:

.. code-block:: diffx

   #...diff: length=<content_length>, type=binary, binary-format=vcdiff
   vcdiff-apply <modified_raw_payload_length>
   <len_c><data>
   ...

   vcdiff-revert <original_raw_payload_length>
   <len_c><data>
   ...


Encoding Logic
--------------

To encode a VCDIFF to a DiffX file:

1. Generate the binary VCDIFF data for the file using a VCDIFF implementation.

2. Compress the binary data with zlib.

3. For each 52-byte chunk of compressed data:

   1. Generate and write a :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>` representing the chunk length.

   2. Generate and write Base85_-encoded data for the chunk.


Decoding Logic
--------------

To decode an encoded VCDIFF from a DiffX file:

1. For each line of diff section content data:

   1. Read and decode 1 byte for the :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>`.

   2. Read and Base85_-decode remaining bytes for the line.

   3. Cap the decoded data to the decoded line length.

      This is important for ensuring we don't treat any padding as
      zlib-compressed data.

2. zlib-decompress the resulting data.

3. Process decompressed data as a VCDIFF.


.. _spec-binary-diffs-git-literals:

Git Literal Binary Diffs
========================

Git Literal binary diffs contain the full contents of both the original
and modified binary files, zlib-compressed and encoded as Base85_.

A DiffX-stored Git Literal binary diff will be in the following format:

.. code-block:: diffx

   #...diff: length=<content_length>, type=binary, binary-format=git-literal
   GIT binary patch
   literal <modified_length>
   <len_c><data>
   ...

   literal <original_length>
   <len_c><data>
   ...


Encoding Logic
--------------

To encode a Git Literal binary diff:

1. Compress the binary file using zlib.

2. For each 52-byte chunk:

   1. Encode a :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>` for the chunk size.

      It may be < 52 for the final chunk in a file.

   2. Encode the chunk data using Base85_.

   3. Write the line length character and encoded data.


.. rubric:: Example in Python

.. code-block:: python

   LEN_A = ord('A')  # 65
   LEN_Z = ord('Z')  # 90
   LEN_a = ord('a')  # 97
   LEN_z = ord('z')  # 122
   LEN_LOWER = LEN_Z - LEN_A + 1             # 26
   LEN_UPPER = LEN_z - LEN_a + 1 + LEN_LOWER # 52

   data: bytes = b'<file data>'

   compressed_data: bytes = zlib.compress(data)
   compressed_len: int = len(compressed_data)
   pos: int = 0

   while pos < compressed_len:
       chunk: bytes = compressed_data[pos:pos + LEN_UPPER]
       chunk_len: int = len(chunk)
       pos += chunk_len

       if chunk_len <= LEN_LOWER:
           len_c = chunk_len + LEN_A - 1
       else:
           len_c = chunk_len + LEN_a - 1 - LEN_LOWER

       out.write('%c%s' % (len_c, base64.b85encode(chunk, pad=True)))


Decoding Logic
--------------

To decode a Literal:

1. For each line:

   1. Read and decode 1 byte for the :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>`.

   2. Read and Base85_-decode remaining bytes for the line.

   3. Cap the decoded data to the decoded line length.

      This is important for ensuring we don't treat any padding as
      zlib-compressed data.

2. zlib-decompress the resulting data as the patched file.


.. rubric:: Example in Python

.. code-block:: python

   LEN_A = ord('A')  # 65
   LEN_Z = ord('Z')  # 90
   LEN_a = ord('a')  # 97
   LEN_LOWER = LEN_Z - LEN_A + 1  # 26


   lines_data: list[bytes] = [b'...', ...]
   result_lines: list[bytes] = []

   for line_data in lines_data:
       length: int = line_data[0]

       if length <= LEN_LOWER:
           length += 1 - LEN_A
       else:
           length += 1 - LEN_a + LEN_LOWER

       result_lines.append(base64.b85decode(line_data[1:])[:length])

   result_data: bytes = zlib.decompress(b''.join(result_lines))


.. _spec-binary-diffs-git-deltas:

Git Delta Binary Diffs
======================

Git Delta binary diffs contain instructions on applying patches to binary
files. Unlike :ref:`spec-binary-diffs-git-literals`, these do not require
embedding the full content of the new file in the patch.

There are two sets of delta lines, each starting with ``delta``. The first
patches the original file, producing the patched file. The second reverts
the patched file, producing the original file.

A DiffX-stored Git Delta binary diff will be in the following format:

.. code-block:: diffx

   #...diff: length=<content_length>, type=binary, binary-format=git-delta
   GIT binary patch
   delta <modified_raw_payload_length>
   <len_c><data>
   ...

   delta <original_raw_payload_length>
   <len_c><data>
   ...


.. _spec-binary-diffs-git-delta:

Delta Payload Format
--------------------

The Git delta diff format describes the changes made to binary files. It's in
the following format:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Offset (bytes)
     - Length (bytes)
     - Description

   * - 0
     - Variable (>= 2)
     - Header

   * - >= 2
     - Variable
     - Instructions


Header Format
~~~~~~~~~~~~~

The header describes the total file size of the original file and the total
file size of the modified file. It's in the following format:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Offset (bytes)
     - Length (bytes)
     - Description

   * - 0
     - Variable (>= 1)
     - The size of the original file in bytes.

   * - >= 1
     - Variable (>= 1)
     - The size of the modified file in bytes.

Each length is encoded as a series of bytes, from Most-Significant Byte to
Least. Each length byte uses 1 bit (Most-Significant Bit) to indicate if
there's more bytes to read for the length, and 7 bits to encode a value for
the length.

Logic for encoding and decoding lengths will be shown below.


Instructions
~~~~~~~~~~~~

The Delta format has two types of instructions:

* :ref:`ADD <spec-binary-diffs-git-delta-add>`:
  Adds new bytes following the instruction to the modified file.

* :ref:`COPY <spec-binary-diffs-git-delta-copy>`:
  Copies a range of bytes from the original file to the modified file.

Instructions must cover the entire contents of the file. Unchanged ranges
of the file must be represented as COPY instructions.


.. _spec-binary-diffs-git-delta-add:

ADD Instruction
^^^^^^^^^^^^^^^

The ADD instruction adds new bytes following the instruction to the modified
file. These bytes are appended to the target object at the current write
position.

This instruction is in the following form:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Length (bytes)
     - Description

   * - control
     - 1
     - The ADD instruction in the form of ``0xxxxxxx``. The 7 bits contain
       the length of data to write.

   * - data
     - Variable (1..127)
     - The bytes to write.

For example, the following instruction adds 6 new bytes to the modified
file:

+----------+-------+-------+-------+-------+-------+-------+
| control  | byte1 | byte2 | byte3 | byte4 | byte5 | byte6 |
+==========+=======+=======+=======+=======+=======+=======+
| 00000110 | 0x68  | 0x65  | 0x6C  | 0x6C  | 0x6F  | 0x21  |
+----------+-------+-------+-------+-------+-------+-------+


.. _spec-binary-diffs-git-delta-copy:

COPY Instruction
^^^^^^^^^^^^^^^^

The COPY instruction copies a range of bytes from the original file to
the modified file. These bytes are appended to the target object at the
current write position.

This instruction is in the following form:

.. list-table::
   :widths: 10 10 20 60
   :header-rows: 1

   * - Field
     - Length (bytes)
     - Condition
     - Description

   * - control
     - 1
     - Always present
     - The COPY instruction in the form of ``1xxxxxxx``. The 7 bits each
       indicate which of the next 7 bytes (offsets and sizes) are present.

   * - offset1
     - 1
     - Bit 1 is set
     - Offset byte 1 to write (0x00 assumed if not present)

   * - offset2
     - 1
     - Bit 2 is set
     - Offset byte 2 to write (0x00 assumed if not present)

   * - offset3
     - 1
     - Bit 3 is set
     - Offset byte 3 to write (0x00 assumed if not present)

   * - offset4
     - 1
     - Bit 4 is set
     - Offset byte 4 to write (0x00 assumed if not present)

   * - size1
     - 1
     - Bit 5 is set
     - Size byte 1 to write (0x00 assumed if not present)

   * - size2
     - 1
     - Bit 6 is set
     - Size byte 2 to write (0x00 assumed if not present)

   * - size3
     - 1
     - Bit 7 is set
     - Size byte 3 to write (0x00 assumed if not present)


The control bits indicate which of the offset and size bytes are present.
An offset or size byte that is not present will be set to 0. This helps
keep the COPY instructions as compact as possible.

The resulting offset is 4 bytes, and the resulting size is 3 bytes. Both
are in little-endian order.

If the size is zero, it must be interpreted as 65535. Similarly, when
encoding, a size of 65535 can be encoded to 0.

For example, the following instruction copies 2600 bytes of data at offset
123456:

+----------+---------+---------+-------+-------+-------+
| control  | offset2 | offset3 | size1 | size2 | size3 |
+==========+=========+=========+=======+=======+=======+
| 10110111 | 0x40    | 0xE2    | 0x01  | 0x28  | 0x0A  |
+----------+---------+---------+-------+-------+-------+


Encoding Logic
--------------

Outer Encoding
~~~~~~~~~~~~~~

1. Write a header for the original file.
2. Write a header for the modified file.

3. For each hunk to write:

   1. If COPY is optimal:

      1. Write a COPY instruction.

   2. Else if ADD is optimal:

      1. Write an ADD instruction.

4. Compress the binary file using zlib.

5. For each 52-byte chunk:

   1. Encode a :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>` for the chunk size.

      It may be < 52 for the final chunk in a file.

   2. Encode the chunk data using Base85_.

   3. Write the line length character and encoded data.


Header Encoding
~~~~~~~~~~~~~~~

This takes in the length of the file the header represents.

1. Loop:

   1. Set ``header_byte`` to ``file_len & 0x7F``.

   2. Bit-shift ``file_len`` right 7 bits.

   3. If ``file_len`` is 0:

      1. Write ``header_byte``.

      2. Break loop.

   4. Else if ``file_len`` is non-0:

       1. Write ``header_byte | 0x80``.


ADD Instruction Encoding
~~~~~~~~~~~~~~~~~~~~~~~~

1. Verify size is <= 127 bytes.

2. Write size as byte.

3. Write new data bytes.


COPY Instruction Encoding
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Set ``control`` byte to 0x80.

2. Compute offsets (up to 4 bytes):

   1. If ``(offset & 0xFF)`` is not 0:

      1. OR 0x01 to ``control``.
      2. Append ``offset & 0xFF`` to arguments.

   2. If ``(offset >> 8 & 0xFF)`` is not 0:

      1. OR 0x02 to ``control``.
      2. Append ``offset >> 8 & 0xFF`` to arguments.

   3. If ``(offset >> 16 & 0xFF)`` is not 0:

      1. OR 0x04 to ``control``.
      2. Append ``offset >> 16 & 0xFF`` to arguments.

   4. If ``(offset >> 24 & 0xFF)`` is not 0:

      1. OR 0x08 to ``control``.
      2. Append ``offset >> 24 & 0xFF`` to arguments.

3. Compute sizes (up to 3 bytes):

   1. Set ``size`` to 0 if set to 65535.

   2. If ``(size & 0xFF)`` is not 0:

      1. OR 0x10 to ``control``.
      2. Append ``size & 0xFF`` to arguments.

   3. If ``(size >> 8 & 0xFF)`` is not 0:

      1. OR 0x20 to ``control``.
      2. Append ``size >> 8 & 0xFF`` to arguments.

   4. If ``(size >> 16 & 0xFF)`` is not 0:

      1. OR 0x40 to ``control``.
      2. Append ``size >> 16 & 0xFF`` to arguments.

4. Write ``control`` and arguments.


Example
~~~~~~~

.. rubric:: Example in Python

.. code-block:: python

   LEN_A = ord('A')  # 65
   LEN_Z = ord('Z')  # 90
   LEN_a = ord('a')  # 97
   LEN_z = ord('z')  # 122
   LEN_LOWER = LEN_Z - LEN_A + 1             # 26
   LEN_UPPER = LEN_z - LEN_a + 1 + LEN_LOWER # 52

   orig_data: bytes = b'<file data>'
   modified_data: bytes = b'<file data>'
   result = io.Bytes()

   for (mode,
        modified_offset,
        modified_hunk,
        modified_size) in calc_hunks(orig_data, modified_data):
       if mode == ADD:
           assert 1 <= modified_size <= 127

           result.write(bytes([modified_size, *modified_hunk]))
       elif mode == COPY:
           control = 0x80
           args = bytearray()

           for shift, mask in zip((0, 8, 16, 24),
                                  (0x01, 0x02, 0x04, 0x08)):
               value = (modified_offset >> shift) & 0xFF

               if value:
                   control |= mask
                   args.append(value)

           for shift, mask in zip((0, 8, 16),
                                  (0x10, 0x20, 0x40)):
               value = (modified_size >> shift) & 0xFF

               if value:
                   control |= mask
                   args.append(value)

           result.write(bytes([control, *args]))

   compressed_data: bytes = zlib.compress(result.getvalue())
   compressed_len: int = len(compressed_data)
   pos: int = 0

   while pos < compressed_len:
       chunk: bytes = compressed_data[pos:pos + LEN_UPPER]
       chunk_len: int = len(chunk)
       pos += chunk_len

       if chunk_len <= LEN_LOWER:
           len_c = chunk_len + LEN_A - 1
       else:
           len_c = chunk_len + LEN_a - 1 - LEN_LOWER

       out.write('%c%s' % (len_c, base64.b85encode(chunk, pad=True)))


Decoding Logic
--------------

Outer Decoding
~~~~~~~~~~~~~~

1. For each line:

   1. Read and decode 1 byte for the :ref:`line length character
      <spec-binary-diffs-git-line-len-chars>`.

   2. Read and Base85_-decode remaining bytes for the line.

   3. Cap the decoded data to the decoded line length.

      This is important for ensuring we don't treat any padding as
      zlib-compressed data.

2. zlib-decompress the resulting data as the Delta instructions payload.

3. Read the original file header.

4. Read the modified file header

5. While there's data to read:

   1. Read 1 byte as ``control``.

   2. If left-most bit 1 is set (``control & 0x80``):

      1. Decode as a COPY, giving ``src_offset`` and ``copy_len``.

      2. Write data from original file at ``src_offset`` of length
         ``copy_len``.

   3. Else:

      1. Decode as an ADD, giving ``add_length`` and ``add_bytes``.

      3. Write ``add_bytes``.


Header Decoding
~~~~~~~~~~~~~~~

1. Set ``file_len`` and ``shift`` to 0.

2. Loop:

   1. Read ``header_byte``.

   2. OR ``(header_byte & 0x7F) << shift`` to ``file_len``.

   3. If ``header_byte & 0x80`` is set:

      1. Break loop.

   4. Add 7 to ``shift``.

3. Return ``file_len``.


ADD Instruction Decoding
~~~~~~~~~~~~~~~~~~~~~~~~

1. Use ``control`` as ``add_length``.

2. Read and return ``add_length`` bytes.


COPY Instruction Decoding
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Compute ``src_offset`` (up to 4 bytes):

   1. If ``(control & 0x01)`` is not 0:

      1. Read 1 byte as ``src_offset``.

   2. If ``(control & 0x02)`` is not 0:

      1. Read 1 byte and bit-shift left 8.

      2. OR result to ``src_offset``.

   3. If ``(control & 0x04)`` is not 0:

      1. Read 1 byte and bit-shift left 16.

      2. OR result to ``src_offset``.

   4. If ``(control & 0x08)`` is not 0:

      1. Read 1 byte and bit-shift left 24.

      2. OR result to ``src_offset``.

2. Compute ``copy_len`` (up to 3 bytes):

   1. If ``(control & 0x10)`` is not 0:

      1. Read 1 byte as ``copy_len``.

   2. If ``(control & 0x20)`` is not 0:

      1. Read 1 byte and bit-shift left 8.

      2. OR result to ``copy_len``.

   3. If ``(control & 0x40)`` is not 0:

      1. Read 1 byte and bit-shift left 16.

      2. OR result to ``copy_len``.

   4. If ``copy_len`` is 0:

      1. Set to ``65536``.

3. Return ``src_offset`` and ``copy_len``.


Example
~~~~~~~

.. rubric:: Example in Python

.. code-block:: python

   LEN_A = ord('A')  # 65
   LEN_Z = ord('Z')  # 90
   LEN_a = ord('a')  # 97
   LEN_z = ord('z')  # 122
   LEN_LOWER = LEN_Z - LEN_A + 1             # 26
   LEN_UPPER = LEN_z - LEN_a + 1 + LEN_LOWER # 52

   orig_data: bytes = '<original file data>'
   delta_lines_data: list[bytes] = [b'...', ...]

   # Decode the delta data.
   result_lines: list[bytes] = []

   for line_data in delta_lines_data:
       length: int = line_data[0]

       if length <= LEN_LOWER:
           length += 1 - LEN_A
       else:
           length += 1 - LEN_a + LEN_LOWER

       result_lines.append(base64.b85decode(line_data[1:])[:length])

   # Decompress the decoded delta data.
   delta_data: bytes = zlib.decompress(b''.join(result_lines))
   delta_data_len = len(delta_data)

   result = io.Bytes()
   offset: int = 0

   # Read headers.
   for i in range(2):
      file_len: int = 0
      shift: int = 0

      while True:
          header_byte = delta_data[offset]
          offset += 1

          file_len |= (header_byte & 0x7F) << shift

          if not (header_byte & 0x80):
              break

          shift += 7

   while offset < delta_data_len:
       op = delta_data[offset]
       offset += 1

       if op & 0x80:
           # This is a COPY.
           src_offset = 0
           copy_len = 0

           # Calculate the offset.
           for shift, mask in zip((0, 8, 16, 24),
                                  (0x01, 0x02, 0x04, 0x08)):
               if op & mask:
                   src_offset |= delta_data[offset] << shift
                   offset += 1

           # Calculate the length.
           for shift, mask in zip((0, 8, 16),
                                  (0x10, 0x20, 0x40)):
               if op & mask:
                   copy_len |= delta_data[offset] << shift
                   offset += 1

           if copy_len == 0:
               copy_len = 65536

           result.write(orig_data[src_offset:src_offset + copy_len])
       else:
           # This is an ADD.
           add_len = op
           result.write(delta_data[offset:offset + add_len])
           offset += add_len

    result_data = result.getvalue()
