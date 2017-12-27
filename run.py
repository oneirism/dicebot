#!/usr/bin/env python3

import logging
import sys
from uuid import uuid4

from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import CommandHandler, InlineQueryHandler, Updater

import dice_notation
from grammar import Grammar
grammar = Grammar()

INVALID_DICE_NOTATION_MSG = 'Invalid <a href="https://en.wikipedia.org/wiki/Dice_notation">Dice Notation.</a>'
INVALID_DICE_NOTATION_MSG += '\r\nExample: <code>1d10</code> or <code>2d30 + 4</code>'
INVALID_DICE_NOTATION_MSG += '\r\n<i>Maximums: 10 components, 100 dice, 1000 sides.</i>'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

logger = logging.getLogger(__name__)


def roll_responder(title: str, result: int, rolls: list) -> str:
    response = '<i>{0}</i>\n'.format(title)

    response += '<b>Results</b>:\n'
    for roll in rolls:
        html = '{0}d{1}: {2}'.format(len(roll), roll.sides, roll)
        response += '\t\t{0}\n'.format(html)
    response += '<b>Total</b>: {0}'.format(result)
    return response


def commandquery(bot: Bot, update, args):
    chat_id = update.message.chat_id
    user = update.message.from_user

    name = ''
    if user.username:
        name = user.username
    else:
        name = user.first_name

    response = ''

    if args[0] in ['advantage', 'disadvantage']:
        query = ''.join(args[1:])
        if dice_notation.is_single_die(query):
            result, rolls = dice_notation.handicap(args[0], query)

            title = '{0} rolled {1} with {2}'.format(
                name, query, args[0]
            )

            response = roll_responder(title, result, rolls)
    else:
        query = ''.join(args)

        if dice_notation.is_dice_notation(query):
            result, rolls = grammar.evaluate(query)

            title = '{0} rolled {1}'.format(
                name, query
            )
            response = roll_responder(title, result, rolls)
        else:
            response = 'Query: {0}\n\n{1}'.format(query, INVALID_DICE_NOTATION_MSG)

    bot.send_message(chat_id, response, 'HTML', True)


def inlinequery(bot: Bot, update: Update):
    query = update.inline_query.query.replace(" ", "")
    user = update.inline_query.from_user

    name = ''
    if user.username:
        name = user.username
    else:
        name = user.first_name
    results = list()

    if dice_notation.is_single_die(query):
        title = '{0} rolled {1}'.format(
            name, query
        )

        advantage_total, advantage_rolls = dice_notation.handicap('advantage', query)

        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Roll {0} with advantage".format(query),
                                                input_message_content=InputTextMessageContent(
                                                    roll_responder(
                                                        '{0} with advantage'.format(title),
                                                        advantage_total, advantage_rolls
                                                    ),
                                                    disable_web_page_preview=True,
                                                    parse_mode='HTML'
                                                )))

        disadvantage_total, disadvantage_rolls = dice_notation.handicap('disadvantage', query)

        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Roll {0} with disadvantage".format(query),
                                                input_message_content=InputTextMessageContent(
                                                    roll_responder(
                                                        '{0} with disadvantage'.format(title),
                                                        disadvantage_total, disadvantage_rolls
                                                    ),
                                                    disable_web_page_preview=True,
                                                    parse_mode='HTML'
                                                )))

    if dice_notation.is_dice_notation(query):
        title = '{0} rolled {1}'.format(
            name, query
        )

        result, rolls = grammar.evaluate(query)

        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Roll {0}".format(query),
                                                input_message_content=InputTextMessageContent(
                                                    roll_responder(title, result, rolls),
                                                    disable_web_page_preview=True,
                                                    parse_mode='HTML'
                                                )))
    else:
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Invalid Roll",
                                                input_message_content=InputTextMessageContent(
                                                    'Query: {0}\n\n{1}'.format(
                                                        query,
                                                        INVALID_DICE_NOTATION_MSG
                                                    ),
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
