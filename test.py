import parser

import run


def test_parse_dice_notation():
    invalid = "invalid"
    assert not run.parse_dice_notation(invalid)

    valid = "3d20"
    assert run.parse_dice_notation(valid)

    valid_with_suffix = "4d12 + 7"
    assert run.parse_dice_notation(valid_with_suffix)


def test_roll_em():
    dice_notation = "1d10 + 2"

    response, computed_components = run.roll_em(dice_notation)

    assert response is not None
    assert 3 <= sum(int(num) for num in response) <= 12

    assert computed_components is not None

    eq = ''.join(str(component) for component in computed_components)
    total = eval(parser.expr(eq).compile())

    print(total)
    assert total == sum(int(num) for num in response) + 2


def test_roll_responder():
    query = "5d1 + 7"

    expected = "Roll: {0}\nResult: [1, 1, 1, 1, 1]\nTotal: 12".format(query)
    actual = run.roll_responder(query)

    assert actual == expected
