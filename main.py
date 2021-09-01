import os
import logging
from os.path import join, dirname
from os import getcwd, path
from dotenv import load_dotenv
from commands import utils, start, campaign
from telegram.ext import Updater, CallbackQueryHandler, PicklePersistence

cwd = getcwd()


def main():
    # Load dotenv
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    # Check and generate files
    utils.check_files_and_directories()
    # Peristence file
    persistence = PicklePersistence(filename=path.join(cwd, "data/persistence/bot_data"))
    # Define updater
    updater = Updater(token=os.environ.get("TOKEN"), use_context=True, persistence=persistence)
    # Define dispatcher
    dispatcher = updater.dispatcher
    # Define error handler
    error_handler = logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Private Conversation Handler
    dispatcher.add_handler(start.start_command())
    # Group Menu Conversation Handler
    dispatcher.add_handler(start.group_menu_command())
    # Private Menu Conversation Handler
    dispatcher.add_handler(start.private_menu_command())
    # Group Conversation Handler
    dispatcher.add_handler(start.start_command(False))
    # Callback Handler
    dispatcher.add_handler(CallbackQueryHandler(campaign.inline_button))
    # Error Handler
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
