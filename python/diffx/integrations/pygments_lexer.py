from pygments.lexer import RegexLexer, bygroups
from pygments.token import Comment, Generic, Name, Text


class DiffXLexer(RegexLexer):
    name = 'DiffX'
    aliases = ['diffx']
    filenames = ['*.diff', '*.patch', '*.diffx']
    mimetypes = ['text/x-diff', 'text/x-patch', 'text/x-diffx']

    tokens = {
        'root': [
            (r'(#\.*)(meta:)( *)([^\n]*)(\n)',
             bygroups(Text, Generic.Heading, Text, Name.Attribute, Text),
             'meta'),
            (r'(#\.*)([a-z]+:)( *)([^\n]*)(\n)',
             bygroups(Text, Generic.Heading, Text, Name.Attribute, Text)),
            (r'#[^\n]*', Comment.Single),
            (r' .*\n', Text),
            (r'\+.*\n', Generic.Inserted),
            (r'-.*\n', Generic.Deleted),
            (r'!.*\n', Generic.Strong),
            (r'@.*\n', Generic.Subheading),
            (r'([Ii]ndex|diff).*\n', Generic.Heading),
            (r'=.*\n', Generic.Heading),
            (r'.*\n', Text),
        ],

        'meta': [
            # End of the line
            (r' *(?=#|$)', Text, '#pop'),

            # Key/value pair
            (r'''([^,:?\[\]{}"'\n]+)(:)(.*\n)''',
             bygroups(Name.Tag, Text, Text)),
        ],
    }

    def analyse_text(text):
        if text[:7] == 'Index: ':
            return True
        if text[:5] == 'diff ':
            return True
        if text[:4] == '--- ':
            return 0.9
