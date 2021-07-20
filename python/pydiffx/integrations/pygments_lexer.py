import re

from pygments.lexer import RegexLexer, bygroups, include, this, using
from pygments.lexers.data import JsonLexer
from pygments.lexers.diff import DiffLexer
from pygments.token import Comment, Keyword, Name, Number, Text


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
                      using(JsonLexer))),
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
