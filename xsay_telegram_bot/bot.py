import logging
import typing
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from . import xsay


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def random(update:Update, context: CallbackContext):
    generator = xsay.Generator()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=generator.generate())


def run_bot(api_token: str, image_templates_file_path: str, phrases_file_path: str) -> typing.NoReturn:
    updater = Updater(token=api_token, use_context=True)
    dispatcher = updater.dispatcher

    # Initialize singleton generator
    generator = xsay.Generator(image_templates_file_path, phrases_file_path)

    start_handler = CommandHandler('start', start)
    random_handler = CommandHandler('random', random)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(random_handler)
    
    updater.start_polling()