import pytest


def escape(value):
    '''Replace special characters in LaTeX with "safe" substitution'''
    escaped = value
    for character in ['\\', '&', '#', '_', '$']:
        escaped = escaped.replace(character, '\\' + character)

    special = {
        '<': '\\textless',
        '>': '\\textgreater',
        '\'': '\\textquotesingle',
        '"': '\\textquotedbl',
        '-': '-',
    }
    for character, replacement in special.items():
        escaped = escaped.replace(character, replacement + '{}')

    escaped = escaped.replace('\n', '\n\n')
    return escaped


def test_escape():
    assert escape(r'No arbitrary \commands') == r'No arbitrary \\commands'
    assert escape(r'Math: $1 + 2$') == r'Math: \$1 + 2\$'

    assert escape('Paragraph\nParagraph') == 'Paragraph\n\nParagraph'
