"""Utilities for parsing Unified Diffs."""

from __future__ import unicode_literals

import re

from pydiffx.errors import MalformedHunkError


UNIFIED_DIFF_HUNK_HEADER_RE = re.compile(
    br'^@@ -(?P<orig_start>\d+)(,(?P<orig_num_lines>\d+))? '
    br'\+(?P<modified_start>\d+)(,(?P<modified_num_lines>\d+))? @@'
    br'( (?P<context>.*))?$',
    re.M)


def get_unified_diff_hunks(lines, ignore_garbage=False):
    """Return information on each hunk in a Unified Diff.

    This will iterate through each hunk, generating information on each hunk.
    Parsing will continue until something other than a hunk is found (unless
    passing ``ignore_garbage=True``).

    Args:
        lines (list of bytes):
            The list of lines in the diff. This should generally be the
            result of using :py:func:`~pydiffx.utils.text.split_lines`.

        ignore_garbage (bool, optional):
            Whether to ignore garbage lines found outside of a hunk.

            If ``True``, all lines will be processed for hunk data.

            If ``False`` (the default), reading will stop once something
            other than a hunk is found.

    Returns:
        dict:
        A dictionary containing the results. This will have the following
        keys:

        ``hunks`` (:py:class:`list` of :py:class:`dict`):
            The list of hunks. Each dictionary will contain:

            ``context`` (:py:class:`bytes`):
                Optional context shown after the ``@@`` header. This may be
                ``None``.

            ``lines_of_context_pre`` (:py:class:`int`):
                The number of lines of context before the first changed line in
                the hunk.

            ``lines_of_context_post`` (:py:class:`int`):
                The number of lines of context after the last changed line in
                the hunk.

            ``modified`` (:py:class:`dict`):
                Information on the modified side of the hunk. This will
                contain the following keys:

                ``start_line`` (:py:class:`int`):
                    The 0-based line number in the original file where the
                    hunk begins. This will be the line number of the first
                    line shown in the hunk, which may include lines of
                    context.

                ``num_lines`` (:py:class:`int`):
                    The number of lines shown for the original side of the
                    hunk in the diff, including any lines of context,
                    unchanged lines, or changed lines.

                ``first_changed_line`` (:py:class:`int`):
                    The 0-based line number in the original file where the
                    first change in the hunk (a ``-`` line) occurs. This
                    will always be after any lines of context.

                ``last_changed_line`` (:py:class:`int`):
                    The 0-based line number in the original file where the
                    last change in the hunk (a ``-`` line) occurs. This will
                    always be before any lines of context.

                ``num_lines_changed`` (:py:class:`int`):
                    The number of lines that were changed in original side
                    of the hunk (the number of ``-`` lines).

            ``orig`` (:py:class:`dict`):
                Information on the original side of the hunk. This will
                contain the following keys:

                ``start_line`` (:py:class:`int`):
                    The 0-based line number in the modified file where the
                    hunk begins. This will be the line number of the first
                    line shown in the hunk, which may include lines of
                    context.

                ``num_lines`` (:py:class:`int`):
                    The number of lines shown for the modified side of the
                    hunk in the diff, including any lines of context,
                    unchanged lines, or changed lines.

                ``first_changed_line`` (:py:class:`int`):
                    The 0-based line number in the modified file where the
                    first change in the hunk (a ``+`` line) occurs. This will
                    always be after any lines of context.

                ``last_changed_line`` (:py:class:`int`):
                    The 0-based line number in the modified file where the
                    last change in the hunk (a ``+`` line) occurs. This will
                    always be before any lines of context.

                ``num_lines_changed`` (:py:class:`int`):
                    The number of lines that were changed in modified side of
                    the hunk (the number of ``+`` lines).

        ``num_processed_lines`` (:py:class:`int`):
            The number of lines read in the diff to produce these results.
            Callers can use this to start parsing the rest of a diff after
            these lines.

        ``total_deletes`` (:py:class:`int`):
            The total number of deleted lines found.

        ``total_inserts`` (:py:class:`int`):
            The total number of inserted lines found.

    Raises:
        pydiffx.errors.MalformedHunkError:
            A line was found within a hunk that was not valid and could not be
            parsed, or a hunk was terminated prematurely.
    """
    total_inserts = 0
    total_deletes = 0

    hunks = []
    cur_hunk_entry = None
    cur_hunk_orig = None
    cur_hunk_modified = None

    hunk_orig_i = 0
    hunk_modified_i = 0

    # Go through each hunk of the diff, trying to find the number of lines
    # of context shown at the beginning of the hunk. This will usually be
    # upwards of 3 lines, but that's not a rule. It could be more, or fewer,
    # depending on file length and diff generation settings.
    for line_num, line in enumerate(lines, start=1):
        found_garbage = False

        if line.startswith(b'@@'):
            # This was not an expected change within a hunk, so it might be a
            # hunk header or it might be something else in a new diff (such as
            # new filename lines or something specific to a diff variant).
            #
            # Check if this is a hunk header.
            m = UNIFIED_DIFF_HUNK_HEADER_RE.match(line)

            if m:
                # It's a hunk header.
                if cur_hunk_entry is not None:
                    # We didn't finish up a previous hunk. Thi sindicates
                    # corruption. Liek GNU patch, we want to just error out.
                    raise MalformedHunkError(line=line,
                                             line_num=line_num)

                # Reset for the next hunk. Pull the line numbers and ranges
                # out of the header, as well as the context. Make sure all
                # line numbers are 0-based.
                cur_hunk_orig = {
                    'first_changed_line': None,
                    'last_changed_line': None,
                    'num_lines': int(m.group('orig_num_lines') or '1'),
                    'num_lines_changed': 0,
                    'start_line': int(m.group('orig_start')) - 1,
                }

                cur_hunk_modified = {
                    'first_changed_line': None,
                    'last_changed_line': None,
                    'num_lines': int(m.group('modified_num_lines') or '1'),
                    'num_lines_changed': 0,
                    'start_line': int(m.group('modified_start')) - 1,
                }

                cur_hunk_entry = {
                    'context': m.group('context'),
                    'orig': cur_hunk_orig,
                    'modified': cur_hunk_modified,
                }

                hunk_orig_i = 0
                hunk_modified_i = 0
            else:
                # This is a garbage line. We'll check later if we encountered
                # this while in a hunk.
                found_garbage = True
        elif cur_hunk_entry is not None:
            # We're in a hunk. Only lines starting with "-", "+", or " "
            # are allowed here.
            if line.startswith(b'-'):
                if cur_hunk_orig['first_changed_line'] is None:
                    # We've found the first change in the original side of
                    # the hunk. We now know the number of lines of context.
                    #
                    # We're going to reduce each index by 1. Hunk ranges use
                    # a 1-base index, but we want 0-based.
                    cur_hunk_orig['first_changed_line'] = \
                        cur_hunk_orig['start_line'] + hunk_orig_i

                cur_hunk_orig['num_lines_changed'] += 1
                cur_hunk_orig['last_changed_line'] = \
                    cur_hunk_orig['start_line'] + hunk_orig_i

                total_deletes += 1
                hunk_orig_i += 1
            elif line.startswith(b'+'):
                if cur_hunk_modified['first_changed_line'] is None:
                    # We've found the first change in the modified side of
                    # the hunk. We now know the number of lines of context.
                    #
                    # We're going to reduce each index by 1. Hunk ranges use
                    # a 1-base index, but we want 0-based.
                    cur_hunk_modified['first_changed_line'] = \
                        cur_hunk_modified['start_line'] + hunk_modified_i

                cur_hunk_modified['num_lines_changed'] += 1
                cur_hunk_modified['last_changed_line'] = \
                    cur_hunk_modified['start_line'] + hunk_modified_i

                total_inserts += 1
                hunk_modified_i += 1
            elif line.startswith(b' '):
                # We might be before a group of changes, inside a group of
                # changes, or after a group of changes, within a hunk. Either
                # way, we have nothing to do but bump up both line offsets.
                hunk_orig_i += 1
                hunk_modified_i += 1
            else:
                # We shouldn't have encountered this. This will be a corrupt
                # diff. We'll process this at the end of this loop iteration.
                found_garbage = True
        else:
            # This isn't a new diff header, or something in a hunk.
            found_garbage = True

        if found_garbage:
            # We found something we didn't expect. Depending on whether we
            # were processing a hunk, we're either going to stop parsing now,
            # or raise an exception.
            if cur_hunk_entry is not None:
                # This is always an error, as it means the diff is corrupt.
                # Raise an exception.
                raise MalformedHunkError(line=line,
                                         line_num=line_num)
            elif not ignore_garbage:
                # We've reached the end of a consecutive list of hunks.
                # We're done.
                #
                # Decrement line_num, so that processing will begin at
                # that line.
                line_num -= 1
                break

        # See if we've finished up with a hunk.
        if (cur_hunk_entry is not None and
            hunk_orig_i >= cur_hunk_orig['num_lines'] and
            hunk_modified_i >= cur_hunk_modified['num_lines']):
            # We've hit the end of the hunk. Finalize it and set up for the
            # next.
            lines_of_context_pre = []
            lines_of_context_post = []

            for hunk_dict in (cur_hunk_orig, cur_hunk_modified):
                first_changed_line = hunk_dict['first_changed_line']
                last_changed_line = hunk_dict['last_changed_line']
                start_line = hunk_dict['start_line']

                if first_changed_line is not None:
                    lines_of_context_pre.append(first_changed_line -
                                                start_line)

                if last_changed_line is not None:
                    lines_of_context_post.append(
                        hunk_dict['num_lines'] -
                        (last_changed_line - start_line + 1))

            cur_hunk_entry.update({
                'lines_of_context_pre': min(lines_of_context_pre or [0]),
                'lines_of_context_post': min(lines_of_context_post or [0]),
            })

            hunks.append(cur_hunk_entry)

            cur_hunk_orig = None
            cur_hunk_modified = None
            cur_hunk_entry = None
            hunk_orig_i = 0
            hunk_modified_i = 0

    if cur_hunk_entry is not None:
        # The last hunk terminated prematurely.
        raise MalformedHunkError(
            line=line,
            line_num=line_num,
            msg=(
                'Unexpected end of file when processing the diff hunk on line '
                '%(line_num)s'
            ))

    return {
        'hunks': hunks,
        'num_processed_lines': line_num,
        'total_deletes': total_deletes,
        'total_inserts': total_inserts,
    }
