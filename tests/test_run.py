import re
import mock

from telegram import Bot, Chat, InlineQuery, Message, Update, User

import run


test_user = User(1, is_bot=False, username='test_user', first_name='test')
test_user_without_username = User(1, is_bot=False, first_name='test')


tests = [
    {
        'query': "2d20H",
        'user': test_user_without_username,
        'valid': True,
    },
    {
        'query': "2d20H",
        'user': test_user,
        'valid': True,
    },
    {
        'query': "ABCDEF",
        'user': test_user,
        'valid': False,
    },
]

def check_response(user, query, response):
    name = ''
    if user.username:
        name = user.username
    else:
        name = user.first_name

    lines = response.splitlines()

    title = '<i>{0} rolled {1}</i>'.format(name, query)
    if lines[0] != title:
        return False

    if lines[1] != '<b>Results:</b>:':
        return False

    regexp = re.compile(r'\[(([1-9]|1[0-9]|20)(\,\040?)?)+\]')
    for line in lines[2:len(lines)-2]:
        if not regexp.match(line):
            return False

    regexp = re.compile(r'<b>Total<\/b>: \[\d+\]')
    if not regexp.match(lines[len(lines)-1]):
        return False

    return True


@mock.patch('telegram.Bot._validate_token')
def test_command_query(patched_validate_token):
    patched_validate_token().return_value = True
    bot = Bot('token')

    responses = []

    def patch_send_message(chat_id, response, parse_type, disable_web_preview):
        responses.append(response)

    with mock.patch.object(Bot, 'send_message', side_effect=patch_send_message):
        for test in tests:
            message = Message(1, test.get('user'), None, Chat(1, ''), text='/roll {0}'.format(test.get('query')))
            update = Update(0, message)
            run.commandquery(bot, update, test.get('query').split(' '))
            response = responses.pop()
            assert check_response(test.get('user'), test.get('query'), response) is test.get('valid')


@mock.patch('telegram.Bot._validate_token')
def test_inline_query(patched_validate_token):
    patched_validate_token().return_value = True
    bot = Bot('token')

    result_list = []

    def patch_answer_inline_query(query_id, results, cache_time):
        result_list.append(results)

    with mock.patch.object(Bot, 'answer_inline_query', side_effect=patch_answer_inline_query):
        for test in tests:
            ilq = InlineQuery(1, test.get('user'), test.get('query'), 0)
            update = Update(0, inline_query=ilq)
            run.inlinequery(bot, update)
            received_results = result_list.pop()
            assert len(received_results) == 1
            response = received_results[0].input_message_content['message_text']
            assert check_response(test.get('user'), test.get('query'), response) is test.get('valid')
