import mock

from telegram import Bot, Chat, InlineQuery, Message, Update, User

import dice_notation
import run

TEST_QUERY_INVALID = 'invalid'
TEST_QUERY_WITH_ADVANTAGE = "advantage 1d1"
TEST_QUERY_WITH_DISADVANTAGE = "disadvantage 1d1"
TEST_QUERY_WITH_MODIFIER = "4d1+2"

OUTPUTS = {
    TEST_QUERY_WITH_MODIFIER: {
        'results': '4d1: [1, 1, 1, 1]',
        'total': 6,
    },
    TEST_QUERY_WITH_ADVANTAGE: {
        'results': '1d1: [1]\n\t\t1d1: [1]',
        'total': 1,
    },
    TEST_QUERY_WITH_DISADVANTAGE: {
        'results': '1d1: [1]\n\t\t1d1: [1]',
        'total': 1,
    },
}

def user_and_query_to_static_response(user, query):
    query_string = ''
    if query.startswith('advantage'):
        query_string = '{} with advantage'.format(query.replace('advantage ', ''))
    elif query.startswith('disadvantage'):
        query_string = '{} with disadvantage'.format(query.replace('disadvantage ', ''))
    else:
        query_string = query

    title = "@{0} rolled {1}".format(user.username, query_string)

    results = OUTPUTS[query]['results']
    total = OUTPUTS[query]['total']

    expected = "<i>{0}</i>\n".format(title)
    expected += "<b>Results</b>:\n"
    expected += "\t\t{0}\n".format(results)
    expected += "<b>Total</b>: {0}".format(total)

    return expected


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
    query = TEST_QUERY_WITH_MODIFIER
    test_user = User(id=1, is_bot=False, first_name='test', username='test')

    total, roll_results = dice_notation.evaluate(query)
    title = "@{0} rolled {1}".format(test_user.username, query)

    actual = run.roll_responder(title, query, total, roll_results)
    expected = user_and_query_to_static_response(test_user, query)

    assert actual == expected



@mock.patch('telegram.Bot._validate_token')
def test_command_query(patched_validate_token):
    patched_validate_token().return_value = True
    bot = Bot('token')
    test_user = User(1, is_bot=False, username='test_user', first_name='test')

    responses = []

    def patch_send_message(chat_id, response, parse_type, disable_web_preview):
        responses.append(response)

    with mock.patch.object(Bot, 'send_message', side_effect=patch_send_message):

        query = TEST_QUERY_WITH_MODIFIER

        message = Message(1, test_user, None, Chat(1, ''), text='/roll {0}'.format(query))
        update = Update(0, message)

        run.commandquery(bot, update, query.split(' '))

        response = responses.pop()
        expected_message = user_and_query_to_static_response(test_user, query)

        assert response == expected_message

        query = TEST_QUERY_WITH_ADVANTAGE
        message = Message(1, test_user, None, Chat(1, ''), text='/roll {0}'.format(query))
        update = Update(0, message)

        run.commandquery(bot, update, query.split(' '))

        response = responses.pop()
        expected_message = user_and_query_to_static_response(test_user, query)

        assert response == expected_message

        query = TEST_QUERY_WITH_DISADVANTAGE
        message = Message(1, test_user, None, Chat(1, ''), text='/roll {0}'.format(query))
        update = Update(0, message)

        run.commandquery(bot, update, query.split(' '))

        response = responses.pop()
        expected_message = user_and_query_to_static_response(test_user, query)

        assert response == expected_message

        query = TEST_QUERY_INVALID
        message = Message(1, test_user, None, Chat(1, ''), text='/roll {0}'.format(query))
        update = Update(0, message)

        run.commandquery(bot, update, query.split(' '))

        response = responses.pop()
        expected_message = run.INVALID_DICE_NOTATION_MSG

        assert response == expected_message

@mock.patch('telegram.Bot._validate_token')
def test_inline_query(patched_validate_token):
    patched_validate_token().return_value = True
    bot = Bot('token')
    test_user = User(1, is_bot=False, username='test_user', first_name='test')

    result_list = []

    def patch_answer_inline_query(query_id, results, cache_time):
        result_list.append(results)

    with mock.patch.object(Bot, 'answer_inline_query', side_effect=patch_answer_inline_query):
        query = TEST_QUERY_WITH_MODIFIER

        ilq = InlineQuery(1, test_user, '{0}'.format(query), 0)
        update = Update(0, inline_query=ilq)

        run.inlinequery(bot, update)

        received_results = result_list.pop()

        assert len(received_results) == 1
        actual_response = received_results[0].input_message_content['message_text']
        expected_response = user_and_query_to_static_response(test_user, query)

        assert actual_response == expected_response

        query = TEST_QUERY_INVALID

        ilq = InlineQuery(1, test_user, '{0}'.format(query), 0)
        update = Update(0, inline_query=ilq)

        run.inlinequery(bot, update)

        received_results = result_list.pop()

        assert len(received_results) == 1
        actual_response = received_results[0].input_message_content['message_text']
        expected_response = run.INVALID_DICE_NOTATION_MSG

        assert actual_response == expected_response
