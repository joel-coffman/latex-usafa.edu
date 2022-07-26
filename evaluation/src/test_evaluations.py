import evaluations


def test_escape():
    assert evaluations.escape(r'No arbitrary \commands') == \
        r'No arbitrary \\commands'
    assert evaluations.escape(r'Math: $1 + 2$') == r'Math: \$1 + 2\$'

    assert evaluations.escape('Paragraph\nParagraph') == \
        'Paragraph\n\nParagraph'
