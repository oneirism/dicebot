#!/usr/bin/env python3
import logging
import sys
from uuid import uuid4

import dice
from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import CommandHandler, InlineQueryHandler, Updater


INVALID_DICE_NOTATION_MSG = 'Invalid <a href="https://en.wikipedia.org/wiki/Dice_notation">Dice Notation.</a>'
INVALID_DICE_NOTATION_MSG += '\r\nExample: <code>1d10</code> or <code>2d30 + 4</code>'
INVALID_DICE_NOTATION_MSG += '\r\n<i>Maximums: 10 components, 100 dice, 1000 sides.</i>'


def format_response(title, result):
    response = '<i>{0}</i>\n'.format(title)

    rolls = print_sub(result)
    print("Rolls: {0}".format(rolls))

    response += '<b>Results:</b>:\n'
    print(type(rolls))
    if isinstance(rolls, str):
        response += '\t\t{0}\n'.format(rolls)
    else:
        for roll in rolls:
            print(roll)
            print(type(roll))
            if isinstance(roll, str):
                response += '\t\t{0}\n'.format(roll)
            else:
                response += '\t\t{0}\n'.format(roll[0])

    response += '<b>Total</b>: {0}'.format(result.result)

    return response

def print_op(element):
    lines = []

    for _, e in enumerate(element.original_operands):
        newlines = print_sub(e)
        if newlines is not None:
            lines.append(newlines)

    return lines

def print_sub(element, **kwargs):
    if not hasattr(element, 'result'):
        element.evaluate_cached(**kwargs)

    if isinstance(element, dice.elements.Operator):
        return print_op(element)

    elif isinstance(element, dice.elements.Dice):
        if any(not isinstance(op, (dice.elements.Integer, int)) for op in element.original_operands):
            return print_op(element)

        print("Result: {0}".format(element.result))
        return '{}: {}'.format(element, element.result)

    return None

def commandquery(bot: Bot, update, args):
    chat_id = update.message.chat_id
    user = update.message.from_user

    name = ''
    if user.username:
        name = user.username
    else:
        name = user.first_name

    query = ''.join(args)

    title = '{0} rolled {1}'.format(
        name, query
    )

    print('Query: {}'.format(query))
    print('Args: {}'.format(args))
    try:
        result = dice.roll(query, raw=True)
        response = format_response(title, result)
    except Exception as e:
        logging.exception(e)

        response = INVALID_DICE_NOTATION_MSG

    bot.send_message(chat_id, response, 'HTML', True)


def inlinequery(bot: Bot, update: Update):
    query = update.inline_query.query.replace(" ", "")
    user = update.inline_query.from_user

    name = ''
    response = ''
    response_title = ''
    title = ''

    if user.username:
        name = user.username
    else:
        name = user.first_name


    try:
        result = dice.roll(query, raw=True)
        title = '{0} rolled {1}'.format(
            name, query
        )
        response = format_response(title, result)
        response_title='Roll {0}'.format(query)
    except Exception as e:
        logging.exception(e)

        response_title='Invalid Dice Notation'
        response = INVALID_DICE_NOTATION_MSG

    results = list()
    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title=response_title,
                                            input_message_content=InputTextMessageContent(
                                            response,
                                            disable_web_page_preview=True,
                                            parse_mode='HTML'
    )))

    bot.answer_inline_query(update.inline_query.id, results, cache_time=0)


if __name__ == '__main__': # pragma: no cover
    TOKEN = sys.argv[1]

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

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
