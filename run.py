#!/usr/bin/env python3
import dice_notation

import logging
import re
import sys
import typing
from uuid import uuid4

import dice
import parser
from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent, ParseMode, Update, User
from telegram.ext import CommandHandler, InlineQueryHandler, Updater


INVALID_DICE_NOTATION_MSG = 'Invalid <a href="https://en.wikipedia.org/wiki/Dice_notation">Dice Notation.</a>'
INVALID_DICE_NOTATION_MSG += '\r\nExample: <code>1d10</code> or <code>2d30 + 4</code>'


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

logger = logging.getLogger(__name__)


def roll_responder(title: str, query: str, result: int, rolls: list) -> str:
    response = '<i>{0}</i>\n'.format(title)

    response += '<b>Results</b>:\n'
    for roll in rolls:
        html = '{0}d{1}: {2}'.format(len(roll), roll.sides, roll)
        response += '\t\t{0}\n'.format(html)
    response += '<b>Total</b>: {0}'.format(result)
    return response


def roll_em(query: str) -> (int, list):
    total, roll_results = dice_notation.evaluate(query)

    return total, roll_results


def commandquery(bot: Bot, update, args):
    chat_id = update.message.chat_id

    if args[0] in ['advantage', 'disadvantage']:
        query = ''.join(args[1:])
        if dice_notation.is_valid_single_dice_notation(query):
            result, rolls = dice_notation.handicap(args[0], query)

            title = '@{0} rolled {1} with {2}'.format(
                update.message.from_user.username, query, args[0]
            )

            response = roll_responder(title, query, result, rolls)
    else:
        query = ''.join(args)

        if dice_notation.is_valid_dice_notation(query):
            result, rolls = dice_notation.evaluate(query)

            title = '@{0} rolled {1}'.format(
                update.message.from_user.username, query
            )
            response = roll_responder(title, query, result, rolls)
        else:
            response = INVALID_DICE_NOTATION_MSG

    msg = bot.send_message(chat_id, response, 'HTML', True)


def inlinequery(bot: Bot, update: Update):
    query = update.inline_query.query.replace(" ", "")
    results = list()

    if dice_notation.is_valid_dice_notation(query):
        title = '@{0} rolled {1}'.format(
            update.inline_query.from_user.username, query
        )

        result, rolls = dice_notation.evaluate(query)

        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Roll {0}".format(query),
                                                input_message_content=InputTextMessageContent(
                                                    roll_responder(title, query, result, rolls),
                                                    disable_web_page_preview=True,
                                                    parse_mode='HTML'
                                                )))
    else:
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Invalid Roll",
                                                input_message_content=InputTextMessageContent(
                                                    INVALID_DICE_NOTATION_MSG,
                                                    disable_web_page_preview=True,
                                                    parse_mode='HTML'
                                                )))

    bot.answer_inline_query(update.inline_query.id, results, cache_time=0)


if __name__ == '__main__': # pragma: no cover
    TOKEN = sys.argv[1]

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_handler(CommandHandler("roll", commandquery,
                                  pass_args=True))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

