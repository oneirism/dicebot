# Standard Library
import json
import logging
import os
from uuid import uuid4

# Third-Party
import dice
import requests

# Local
# TODO: Force local import
from utils import format_response


# Environment Variables
ENV = os.environ['ENV']
if ENV == "TEST":
    TOKEN = "TEST"
else:
    TOKEN = os.environ['TELEGRAM_TOKEN']

# Globals
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def init_logger():
    # Logging
    logger = logging.getLogger()

    if ENV == "Production":
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    return logger


def roll(event, context):
    try:
        logger = init_logger()

        logger.debug(context)

        # Read Telegram API event 
        event_body = json.loads(event.get("body"))

        logger.debug(event_body)

        # Inline Queries
        if event_body.get("inline_query") is not None:
            ilq = event_body.get("inline_query")

            # TODO: Handle this a little more gracefully. Prefer usernames where available.
            first_name = ilq.get("from").get("first_name")

            # Get the user's query
            query = ilq.get("query")

            # Roll the dice!
            # TODO: Make this a function.
            result = dice.roll(query, raw=True)

            response = format_response(
                "{} rolled {}.".format(first_name, query),
                result
            )

            # Build the ILQ response data
            response_data = {
                "cache_time": 0,
                "inline_query_id": ilq.get("id"),
                "results": json.dumps(
                            [
                        {
                            "type": "article",
                            "id": str(uuid4()),
                            "title": "Roll {}".format(query),
                            "input_message_content": {
                                "message_text": response,
                                "parse_mode": "HTML"
                            }
                        }
                    ]
                )
            }

            # Send our response
            url = BASE_URL + "/answerInlineQuery"
            response = requests.post(url, response_data)

            logging.debug("Response: %s", response.text)

        # Command Queries
        elif event_body.get("message") is not None:
            message = event_body.get("message")
            message_text = str(message.get("text"))

            # Roll commands
            if "/roll" in message_text:

                # TODO: Handle this a little more gracefully. Prefer usernames where available.
                # TODO: Make this a function.
                first_name = message.get("from").get("first_name")

                # Our query is everything after the first occurrence of "roll"
                query = message_text.partition("roll ")[2]

                # Roll the dice!
                # TODO: Make this a function.
                result = dice.roll(query, raw=True)
                response = format_response(
                    "{} rolled {}.".format(first_name, query),
                    result
                )

                # Build the command response data
                response_data = {
                    "text": response.encode("utf8"),
                    "chat_id": message.get("chat").get("id"),
                    "parse_mode": "HTML"
                }

                # Send our response
                url = BASE_URL + "/sendMessage"
                response = requests.post(url, response_data)

                logging.debug("Response: %s", response.text)

    except Exception as e:
        logging.critical(e)

    # Let Telegram know we've processed the message
    return {"statusCode": 200}
