#!/usr/bin/env python3
import logging
import re
import sys
import typing
from uuid import uuid4

import dice
import parser
from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent, ParseMode, Update
from telegram.ext import CommandHandler, InlineQueryHandler, Updater


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

logger = logging.getLogger(__name__)


def parse_dice_notation(query: str) -> typing.Match:
    #TODO(devenney): Restrict number of dice and size of bonus.
    pattern = re.compile("^(\d+)(d)(\d+)((\+)(\d+))?")
    return pattern.match(query)


def roll_responder(query: str) -> str:
    roll_results, computed_components = roll_em(query)

    eq = ''.join(str(component) for component in computed_components)
    total = eval(parser.expr(eq).compile())

    response = 'Roll: {0}\nResult: {1}\nTotal: {2}'.format(query,  ' - '.join(str(roll) for roll in roll_results), total)
    return response


def roll_em(query: str) -> list:
    pattern = re.compile("(\d+)(d)(\d+)")

    operand_pattern = re.compile("([+-/*])")

    components = re.split(operand_pattern, query.replace(" ", ""))

    computed_components = []
    roll_results = []

    for component in components:
        print(component)
        if pattern.match(component):
            rolls = dice.roll(component)
            roll_results.append(rolls)
            computed_components.append('(')
            for roll in rolls[:-1]:
                computed_components.append(roll)
                computed_components.append('+')
            computed_components.append(rolls[-1])
            computed_components.append(')')
        else:
            computed_components.append(component)

    return roll_results, computed_components


def commandquery(bot: Bot, update, args):
    query = ''.join(args)
    if parse_dice_notation(query):
        response = roll_responder(query)
        update.message.reply_text(response)
    else:
        update.message.reply_text("Invalid Dice Notation. Example: 2d30 + 4")


def inlinequery(bot: Bot, update: Update):
    query = update.inline_query.query
    results = list()

    if parse_dice_notation(query):
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Roll",
                                                input_message_content=InputTextMessageContent(
                                                    roll_responder(query))))
    else:
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Invalid Roll",
                                                input_message_content=InputTextMessageContent(
                                                    "Invalid Dice Notation")))

    update.inline_query.answer(results, cache_time=0)


def error(bot: Bot, update, error: Exception):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    TOKEN = sys.argv[1]

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_handler(CommandHandler("roll", commandquery,
                                  pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
