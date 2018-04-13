import json
import logging
import os
import sys
import unittest

from unittest import mock

sys.path.insert(0, './src')
from handler import roll


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def mock_tg_resp(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.text = {
                "ok": True
            }
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "https://api.telegram.org/botTEST":
        return MockResponse(
            {
                "statusCode": "200",
            },
            
            200
        )

    return MockResponse(None, 404)


class QueryTest(unittest.TestCase):
    @mock.patch('requests.post', side_effect=mock_tg_resp)
    def test(self, mock):
        event = {}
        event["body"] = json.dumps(
            {
                'update_id': 74399407,
                'message': {
                    'message_id': 614,
                    'from': {
                        'id': 339873294,
                        'is_bot': False,
                        'first_name': 'Brendan',
                        'last_name': 'Devenney',
                        'username': 'devenney',
                        'language_code': 'en-US'
                    },
                    'chat': {
                        'id': 339873294,
                        'first_name': 'Brendan',
                        'last_name': 'Devenney',
                        'username': 'devenney',
                        'type': 'private'
                    },
                    'date': 1523568333,
                    'text': '/roll 1d20',
                    'entities': [
                        {
                            'offset': 0,
                            'length': 5,
                            'type': 'bot_command'
                        }
                    ]
                }
            }
        )

        response = roll(
            event,    
            None
        )

        logger.debug(response)
        self.assertIsNotNone(response)
