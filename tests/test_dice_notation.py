import dice_notation

def test_dice_notation():
    invalid = "invalid"
    assert not dice_notation.is_valid_dice_notation(invalid)

    invalid_because_spaces = "1d4 + 2"
    assert not dice_notation.is_valid_dice_notation(invalid)

    valid = "3d20"
    assert dice_notation.is_valid_dice_notation(valid)

    valid_with_suffix = "4d12+7"
    assert dice_notation.is_valid_dice_notation(valid_with_suffix)
