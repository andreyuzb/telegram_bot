#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

from telegram.utils.helpers import escape_markdown

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, Filters, MessageHandler, RegexHandler, ConversationHandler
import logging
import subprocess
from emoji import emojize
import configparser

TOKEN = ""

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('server_bot.ini')

IPADDR = range(1)
COMMAND1 = range(1)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
	'This is personal bot of Andrey Useinov.\n'
	'Send /help for more information about commands.\n' +
	emojize(":smile:  :punch: :fist:", use_aliases=True))


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
	'This bot is using for different tasks on AUs server\n'
	'Yout can use next commands:\n'
	'/start - basic information about bot.\n'
	'/help - this message.\n'
	'/apache_status - information about stutus of apache server.\n'
	'/ping - ping some ip address.\n'
	'/sys_command - some system commands.\n'
	)

def apache_status(bot, update, direct=True):
    """Send a message when the command /apache_status is issued."""
    user_id = update.message.from_user.id

    if user_id == int(config['ADMIN']['id']):
    	command = "service apache2 status"
    	output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    	output = output.stdout.read().decode('utf-8')
    	output = '`{0}`'.format(output)
    	update.message.reply_text(output) 
    else:
        update.message.reply_text('You dont have permissions to execute this command.')

def ping(bot, update):

    update.message.reply_text(
        'Please, enter IP address, that you want to ping.\n'
        'Send /cancel to cancel this command.\n'
        )

    return IPADDR

def ipaddr(bot, update):
    command = "ping -c 4 " + str(update.message.text)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = output.stdout.read().decode('utf-8')
    output = '`{0}`'.format(output) 
    update.message.reply_text(output)

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('You can try this command in another time.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def sys_command(bot, update):
    reply_keyboard = [['who', 'netstat -nat']]

    update.message.reply_text(
        'You can fulfill some system commands. Please, choose.\n'
        'Send /cancel to stop this dialog.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))

    return COMMAND1

def command1(bot, update):
    command = str(update.message.text)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = output.stdout.read().decode('utf-8')
    output = '`{0}`'.format(output)
    update.message.reply_text(output,reply_markup=ReplyKeyboardRemove()) 
    
    return ConversationHandler.END

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(
                query.upper())),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN))]

    update.inline_query.answer(results)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("apache_status", apache_status)) 
   
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('ping', ping)],

        states={
            IPADDR: [MessageHandler(Filters.text, ipaddr)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('sys_command', sys_command)],

        states={
            COMMAND1: [MessageHandler(Filters.text, command1)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )    

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

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
