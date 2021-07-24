"""Unit tests for pydiffx.utils.unified_diffs."""

from __future__ import unicode_literals

from pydiffx.errors import MalformedHunkError
from pydiffx.tests.testcases import TestCase
from pydiffx.utils.unified_diffs import get_unified_diff_hunks


class GetUnifiedDiffHunksTests(TestCase):
    """Unit tests for pydiffx.utils.unified_diffs.get_unified_diff_hunks."""

    def test_with_one_hunk(self):
        """Testing get_unified_diff_hunks with one basic hunk"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,7 +12,10 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 10,
                            'first_changed_line': 14,
                            'last_changed_line': 17,
                            'num_lines_changed': 4,
                        },
                    },
                ],
                'num_processed_lines': 12,
                'total_deletes': 1,
                'total_inserts': 4,
            })

    def test_with_multiple_hunks(self):
        """Testing get_unified_diff_hunks with multiple hunks"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,7 +12,10 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'@@ -23,7 +40,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 10,
                            'first_changed_line': 14,
                            'last_changed_line': 17,
                            'num_lines_changed': 4,
                        },
                    },
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 22,
                            'num_lines': 7,
                            'first_changed_line': 25,
                            'last_changed_line': 25,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 39,
                            'num_lines': 7,
                            'first_changed_line': 42,
                            'last_changed_line': 42,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 21,
                'total_deletes': 2,
                'total_inserts': 5,
            })

    def test_with_multiple_hunks_no_lines_of_context(self):
        """Testing get_unified_diff_hunks with no lines of context"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -13,1 +15,4 @@\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'@@ -26,1 +43,1 @@\n',
                b'-# old line\n',
                b'+# new line\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 0,
                        'lines_of_context_post': 0,
                        'orig': {
                            'start_line': 12,
                            'num_lines': 1,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 14,
                            'num_lines': 4,
                            'first_changed_line': 14,
                            'last_changed_line': 17,
                            'num_lines_changed': 4,
                        },
                    },
                    {
                        'context': None,
                        'lines_of_context_pre': 0,
                        'lines_of_context_post': 0,
                        'orig': {
                            'start_line': 25,
                            'num_lines': 1,
                            'first_changed_line': 25,
                            'last_changed_line': 25,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 42,
                            'num_lines': 1,
                            'first_changed_line': 42,
                            'last_changed_line': 42,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 9,
                'total_deletes': 2,
                'total_inserts': 5,
            })

    def test_with_all_inserts(self):
        """Testing get_unified_diff_hunks with all inserts"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,6 +12,10 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 6,
                            'first_changed_line': None,
                            'last_changed_line': None,
                            'num_lines_changed': 0,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 10,
                            'first_changed_line': 14,
                            'last_changed_line': 17,
                            'num_lines_changed': 4,
                        },
                    },
                ],
                'num_processed_lines': 11,
                'total_deletes': 0,
                'total_inserts': 4,
            })

    def test_with_all_deletes(self):
        """Testing get_unified_diff_hunks with all deletes"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,10 +12,6 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# new line\n',
                b'-# new line\n',
                b'-# new line\n',
                b'-# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 10,
                            'first_changed_line': 12,
                            'last_changed_line': 15,
                            'num_lines_changed': 4,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 6,
                            'first_changed_line': None,
                            'last_changed_line': None,
                            'num_lines_changed': 0,
                        },
                    },
                ],
                'num_processed_lines': 11,
                'total_deletes': 4,
                'total_inserts': 0,
            })

    def test_with_all_mixture_of_changes(self):
        """Testing get_unified_diff_hunks with mixture of inserts, deletes,
        and unchanged lines
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,9 +12,12 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'+# new line\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 9,
                            'first_changed_line': 13,
                            'last_changed_line': 13,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 12,
                            'first_changed_line': 14,
                            'last_changed_line': 19,
                            'num_lines_changed': 4,
                        },
                    },
                ],
                'num_processed_lines': 14,
                'total_deletes': 1,
                'total_inserts': 4,
            })

    def test_with_change_on_first_line(self):
        """Testing get_unified_diff_hunks with change on first content line
        of hunk
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -1,4 +1,5 @@\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 0,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 0,
                            'num_lines': 4,
                            'first_changed_line': 0,
                            'last_changed_line': 0,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 0,
                            'num_lines': 5,
                            'first_changed_line': 0,
                            'last_changed_line': 1,
                            'num_lines_changed': 2,
                        },
                    },
                ],
                'num_processed_lines': 7,
                'total_deletes': 1,
                'total_inserts': 2,
            })

    def test_with_change_on_second_line(self):
        """Testing get_unified_diff_hunks with change on second content line
        of hunk
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -1,5 +1,6 @@\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 1,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 0,
                            'num_lines': 5,
                            'first_changed_line': 1,
                            'last_changed_line': 1,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 0,
                            'num_lines': 6,
                            'first_changed_line': 1,
                            'last_changed_line': 2,
                            'num_lines_changed': 2,
                        },
                    },
                ],
                'num_processed_lines': 8,
                'total_deletes': 1,
                'total_inserts': 2,
            })

    def test_with_change_on_third_line(self):
        """Testing get_unified_diff_hunks with change on third content line
        of hunk
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -1,6 +1,7 @@\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 2,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 0,
                            'num_lines': 6,
                            'first_changed_line': 2,
                            'last_changed_line': 2,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 0,
                            'num_lines': 7,
                            'first_changed_line': 2,
                            'last_changed_line': 3,
                            'num_lines_changed': 2,
                        },
                    },
                ],
                'num_processed_lines': 9,
                'total_deletes': 1,
                'total_inserts': 2,
            })

    def test_with_single_line_replace(self):
        """Testing get_unified_diff_hunks with single-line chunk with replaced
        line
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -1 +1 @@\n',
                b'-# old line\n',
                b'+# new line\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 0,
                        'lines_of_context_post': 0,
                        'orig': {
                            'start_line': 0,
                            'num_lines': 1,
                            'first_changed_line': 0,
                            'last_changed_line': 0,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 0,
                            'num_lines': 1,
                            'first_changed_line': 0,
                            'last_changed_line': 0,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 3,
                'total_deletes': 1,
                'total_inserts': 1,
            })

    def test_with_insert_before_only_line(self):
        """Testing get_unified_diff_hunks with insert before only line in
        hunk
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -1,1 +1,2 @@\n',
                b'+# new line\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 0,
                        'lines_of_context_post': 1,
                        'orig': {
                            'start_line': 0,
                            'num_lines': 1,
                            'first_changed_line': None,
                            'last_changed_line': None,
                            'num_lines_changed': 0,
                        },
                        'modified': {
                            'start_line': 0,
                            'num_lines': 2,
                            'first_changed_line': 0,
                            'last_changed_line': 0,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 3,
                'total_deletes': 0,
                'total_inserts': 1,
            })

    def test_with_header_context(self):
        """Testing get_unified_diff_hunks with context information in header
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,7 +12,10 @@ def foo(self):\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': b'def foo(self):',
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 10,
                            'first_changed_line': 14,
                            'last_changed_line': 17,
                            'num_lines_changed': 4,
                        },
                    },
                ],
                'num_processed_lines': 12,
                'total_deletes': 1,
                'total_inserts': 4,
            })

    def test_with_garbage_between_hunks(self):
        """Testing get_unified_diff_hunks with garbage between hunks"""
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,7 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'garbage\n'
                b'@@ -30,7 +32,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 7,
                            'first_changed_line': 14,
                            'last_changed_line': 14,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 9,
                'total_deletes': 1,
                'total_inserts': 1,
            })

    def test_with_garbage_like_header_between_hunks(self):
        """Testing get_unified_diff_hunks with header-like garbage ("@@ ...")
        between hunks
        """
        self.assertEqual(
            get_unified_diff_hunks([
                b'@@ -10,7 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'@@ garbage\n'
                b'@@ -30,7 +32,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ]),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 7,
                            'first_changed_line': 14,
                            'last_changed_line': 14,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 9,
                'total_deletes': 1,
                'total_inserts': 1,
            })

    def test_with_garbage_between_hunks_with_ignore_garbage(self):
        """Testing get_unified_diff_hunks with garbage between hunks with
        ignore_garbage=True
        """
        self.assertEqual(
            get_unified_diff_hunks(
                [
                    b'@@ -10,7 +12,7 @@\n',
                    b' #\n',
                    b' #\n',
                    b' #\n',
                    b'-# old line\n',
                    b'+# new line\n',
                    b' #\n',
                    b' #\n',
                    b' #\n',
                    b'garbage\n',
                    b'@@ -30,7 +32,7 @@\n',
                    b' #\n',
                    b' #\n',
                    b' #\n',
                    b'-# old line\n',
                    b'+# new line\n',
                    b' #\n',
                    b' #\n',
                    b' #\n',
                ],
                ignore_garbage=True),
            {
                'hunks': [
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 9,
                            'num_lines': 7,
                            'first_changed_line': 12,
                            'last_changed_line': 12,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 11,
                            'num_lines': 7,
                            'first_changed_line': 14,
                            'last_changed_line': 14,
                            'num_lines_changed': 1,
                        },
                    },
                    {
                        'context': None,
                        'lines_of_context_pre': 3,
                        'lines_of_context_post': 3,
                        'orig': {
                            'start_line': 29,
                            'num_lines': 7,
                            'first_changed_line': 32,
                            'last_changed_line': 32,
                            'num_lines_changed': 1,
                        },
                        'modified': {
                            'start_line': 31,
                            'num_lines': 7,
                            'first_changed_line': 34,
                            'last_changed_line': 34,
                            'num_lines_changed': 1,
                        },
                    },
                ],
                'num_processed_lines': 19,
                'total_deletes': 2,
                'total_inserts': 2,
            })

    def test_with_garbage_in_hunk(self):
        """Testing get_unified_diff_hunks with garbage in hunk"""
        message = (
            'Malformed content in the diff hunk on line 5: %r'
            % b'garbage\n'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,9 +12,9 @@\n'
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'garbage\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ])

    def test_with_bad_hunk_length_both(self):
        """Testing get_unified_diff_hunks with bad hunk length on both
        original and modified sides at end of file
        """
        message = (
            'Unexpected end of file when processing the diff hunk on line 6'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,7 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
            ])

    def test_with_bad_hunk_length_orig(self):
        """Testing get_unified_diff_hunks with bad hunk length on original
        side at end of file
        """
        message = (
            'Unexpected end of file when processing the diff hunk on line 6'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,7 +12,4 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
            ])

    def test_with_bad_hunk_length_modified(self):
        """Testing get_unified_diff_hunks with bad hunk length on modified
        side at end of file
        """
        message = (
            'Unexpected end of file when processing the diff hunk on line 6'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,4 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
            ])

    def test_with_bad_hunk_length_both_and_new_hunk(self):
        """Testing get_unified_diff_hunks with bad hunk length on both
        original and modified sides followed by new hunk
        """
        message = (
            'Malformed content in the diff hunk on line 7: %r'
            % b'@@ -30,7 +32,7 @@\n'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,7 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'@@ -30,7 +32,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ])

    def test_with_bad_hunk_length_orig_and_new_hunk(self):
        """Testing get_unified_diff_hunks with bad hunk length on original
        side followed by new hunk
        """
        message = (
            'Malformed content in the diff hunk on line 7: %r'
            % b'@@ -30,7 +32,7 @@\n'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,7 +12,4 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'@@ -30,7 +32,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ])

    def test_with_bad_hunk_length_modified_and_new_hunk(self):
        """Testing get_unified_diff_hunks with bad hunk length on modified
        side followed by new hunk
        """
        message = (
            'Malformed content in the diff hunk on line 7: %r'
            % b'@@ -30,7 +32,7 @@\n'
        )

        with self.assertRaisesMessage(MalformedHunkError, message):
            get_unified_diff_hunks([
                b'@@ -10,4 +12,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b'@@ -30,7 +32,7 @@\n',
                b' #\n',
                b' #\n',
                b' #\n',
                b'-# old line\n',
                b'+# new line\n',
                b' #\n',
                b' #\n',
                b' #\n',
            ])
