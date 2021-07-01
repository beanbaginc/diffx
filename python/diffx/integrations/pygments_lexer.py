import re

from pygments.lexer import RegexLexer, bygroups, include, this, using
from pygments.lexers.diff import DiffLexer
from pygments.token import (Comment, Keyword, Name, Number, Punctuation,
                            String, Text)


class DiffXMetadataLexer(RegexLexer):
    """Pygments lexer for highlighting DiffX metadata."""

    name = 'DiffX Metadata'
    aliases = ['diffx-metadata']
    filenames = []

    flags = re.DOTALL | re.MULTILINE

    tokens = {
        'root': [
            # Key/value pair
            (r'(\s*[a-z][a-z0-9 _-]*)(: ?)(.*\n)',
             bygroups(Keyword, Punctuation.Indicator,
                      using(this, state='value'))),

            (r'(\s*-)( )(.*\n)',
             bygroups(Punctuation.Indicator, Text,
                      using(this, state='value'))),

            (r'.*\n', Text),
        ],

        'value': [
            (r'(true|false|null)\b', Keyword.Constant),
            (r'0[0-7]+', Number.Oct),
            (r'-?(0|[1-9]\d*)', Number.Integer),
            (r'-?(0|[1-9]\d*)(\.\d+)', Number.Float),
            (r'"', String, 'string'),
        ],

        'string': [
            # Escape codes
            (r'\\(?:x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})',
             String.Escape),

            # Whitespace and linebreaks
            (r'\s', String),

            # Normal non-whitespace characters
            (r'[^\s"\\]+', String),

            # End of string
            (r'"', String, '#pop'),
        ],
    }


class DiffXLexer(RegexLexer):
    """Pygments lexer for highlighting DiffX files."""

    name = 'DiffX'
    aliases = ['diffx']
    filenames = ['*.diff', '*.patch', '*.diffx']
    mimetypes = ['text/x-diff', 'text/x-patch', 'text/x-diffx']

    _header_options = r'(?:( )([^\n]*))?(\n)'
    _end_section = r'(?=#\.{1,3}[a-z]|\Z)'
    _section_content = r'(.+?|\Z)'

    flags = re.DOTALL | re.MULTILINE

    tokens = {
        'root': [
            include('examples'),

            (r'(#(?:diffx|\.change|\.\.file):)' + _header_options,
             bygroups(Name.Tag, Text, Name.Attribute, Text)),
            (r'(#\.{1,3}meta:)' + _header_options + _section_content +
             _end_section,
             bygroups(Name.Tag, Text, Name.Attribute, Text,
                      using(DiffXMetadataLexer))),
            (r'(#\.{1,3}preamble:)' + _header_options + _section_content +
             _end_section,
             bygroups(Name.Tag, Text, Name.Attribute, Text, Text)),
            (r'(#\.{3}diff:)' + _header_options + _section_content +
             _end_section,
             bygroups(Name.Tag, Text, Name.Attribute, Text,
                      using(this, state='diff'))),
            (r'.*\n', Text),
        ],

        'diff': [
            include('examples'),

            (r'(delta)( )(\d+)(\n)',
             bygroups(Keyword, Text, Number.Integer, Text)),
            (r'.+', using(DiffLexer)),
        ],

        'examples': [
            (r'\.\.\.\n', Comment.Single),
        ],
    }

    def analyse_text(text):
        if text[:7] == 'Index: ':
            return True
        if text[:5] == 'diff ':
            return True
        if text[:4] == '--- ':
            return 0.9
