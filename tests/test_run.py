import parser

from telegram import User

import dice_notation
import run


def test_roll_em():
    dice = "1d10"
    modifier = 2
    dice_notation = "{} + {}".format(dice, modifier)

    total, roll_results = run.roll_em(dice_notation)

    assert total is not None
    assert 3 <= total <= 12

    assert roll_results is not None

    calculated_total = sum(int(roll) for roll in roll_results) + modifier

    assert total == calculated_total


def test_roll_responder():
    query = "5d1 + 7"
    test_user = User(id=1, is_bot=False, first_name='test', username='test')

    expected = "<i>{0} rolled {1}</i>\n\n".format(test_user.username, query)
    expected += "<b>Results</b>:\n"
    expected += "\t\t5d1: [1, 1, 1, 1, 1]\n"
    expected += "<b>Total</b>: 12"

    total, roll_results = dice_notation.evaluate(query)

    actual = run.roll_responder(test_user, query, total, roll_results)

    assert actual == expected
