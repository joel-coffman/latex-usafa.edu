import pytest

from evaluations import *


def test_escape():
    assert escape(r'No arbitrary \commands') == r'No arbitrary \\commands'
    assert escape(r'Math: $1 + 2$') == r'Math: \$1 + 2\$'

    assert escape('Paragraph\nParagraph') == 'Paragraph\n\nParagraph'
