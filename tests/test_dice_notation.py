import mock
import sys

import dice_notation


@mock.patch('builtins.input', side_effect=['4d1'])
def test_main(input):
    import dice_notation
    with mock.patch.object(dice_notation, "__name__", "__main__"):
        dice_notation.init()

    expected = 'Total: 4\nRolls: [Roll([1, 1, 1, 1], sides=1)]'

    stdout = sys.stdout.getvalue().strip()

    assert stdout == expected


def test_dice_notation():
    invalid = "invalid"
    assert not dice_notation.is_valid_dice_notation(invalid)

    invalid_because_spaces = "1d4 + 2"
    assert not dice_notation.is_valid_dice_notation(invalid)

    valid = "3d20"
    assert dice_notation.is_valid_dice_notation(valid)

    valid_with_suffix = "4d12+7"
    assert dice_notation.is_valid_dice_notation(valid_with_suffix)


def test_single_dice_notation():
    invalid = "invalid"
    assert not dice_notation.is_valid_single_dice_notation(invalid)

    invalid_because_spaces = "1d4 + 2"
    assert not dice_notation.is_valid_single_dice_notation(invalid)

    invalid_because_suffix = "4d12+7"
    assert not dice_notation.is_valid_single_dice_notation(invalid_because_suffix)

    invalid_because_more_than_one = "4d12+1d20"
    assert not dice_notation.is_valid_single_dice_notation(invalid_because_more_than_one)

    valid = "3d20"
    assert dice_notation.is_valid_single_dice_notation(valid)


def test_handicap():
    query = "1d20"

    result, rolls = dice_notation.handicap('advantage', query)
    assert result == int(max(rolls))

    result, rolls = dice_notation.handicap('disadvantage', query)
    assert result == int(min(rolls))


# TODO: Test all of the operators defined in dice_notations.py.
def test_evaluate():
    query = "(3d1 + 5) * 2"
    expected = 16

    total, rolls = dice_notation.evaluate(query)

    print(total)
    print(rolls)

    assert total == expected
    assert ((sum(int(roll) for roll in rolls) + 5) * 2) == expected

    query = "3d1 + 2"
    expected = 5

    total, rolls = dice_notation.evaluate(query)

    assert total == expected
    assert (sum(int(roll) for roll in rolls) + 2) == expected

