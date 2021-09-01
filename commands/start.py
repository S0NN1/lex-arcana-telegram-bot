import os
import logging
import telegram
from os import getcwd

from commands.utils import generate_keyboard
from . import checker, utils, campaign, menu
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from .constants import GROUP_WARN, GROUP_WELCOME, PRIVATE_MENU_MESSAGE, GROUP_LANG, PRIVATE_LANG, GROUP_START, GROUP_MENU_MESSAGE, GROUP_MENU_TRANSLATION, GROUP_MENU_TRANSLATION_KEYBOARD

CHECKER, NEW_CAMPAIGN, NEW_CAMPAIGN_FOLLOW_UP, BOT_INFO, START, LANGUAGE, LANGUAGE_FOLLOW_UP, CAMPAIGN_CREATION = range(8)
MENU, MENU_CHECKER, ACTIVE_CAMPAIGNS, PLAYER_CHECKER, DUNGEON_MASTER_CHECKER, RESTORE_HP_CHECKER, RESTORE_HP_VALUE, RESTORE_HP_CHAR, CHARACTER_CREATION, CHARACTER_IMPORT = range(10)
GROUP_MENU_CHECKER, NEW_CAMPAIGN_CHECKER, NEW_CAMPAIGN_FOLLOW_UP_CHECKER, CAMPAIGN_CREATION_CHECKER, DICE_NUMBER, DICE_COUNT = range(6)


def group_start(update, context):
    if 'lang' not in context.chat_data:
        context.chat_data['lang'] = utils.get_language(str(update.message.from_user['id']))
    context.user_data['in_conversation'] = True
    context.chat_data['group_chat_id'] = update.message.chat['id']
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WELCOME, context.chat_data['lang'], False), reply_markup=generate_keyboard(utils.get_translation_list(GROUP_START, context.chat_data['lang'], True), False))
    return CHECKER


def group_language(update, context):
    context.chat_data['user_id_in_conversation'] = update.message.from_user['id']
    if(not utils.already_created(str(update.message.chat['id']), os.path.abspath(os.path.join(getcwd(), 'data/campaigns')))):
        context.chat_data['is_change_lang'] = False
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_LANG, 'en_US', False), reply_markup=generate_keyboard(utils.get_flags(), False))
        return LANGUAGE_FOLLOW_UP
    elif update.message.text == '/lang':
        context.chat_data['is_change_lang'] = True
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_LANG, context.chat_data['lang'], False), reply_markup=generate_keyboard(utils.get_flags(), False))
        return LANGUAGE_FOLLOW_UP
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WARN, 'en_US', False))
    context.user_data['in_conversation'] = False
    context.chat_data['user_id_in_conversation'] = None
    return ConversationHandler.WAITING


def group_language_follow_up(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return LANGUAGE_FOLLOW_UP
    flags = utils.get_flags()
    logging.info(update.message.text)
    if update.message.text in flags:
        context.chat_data['lang'] = utils.map_flag_to_language(update.message.text)
        context.user_data['in_conversation'] = True
        context.chat_data['group_chat_id'] = update.message.chat['id']
        if context.chat_data['is_change_lang']:
            menu_list = utils.get_translation_list(GROUP_MENU_TRANSLATION, context.chat_data['lang'], True)
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
            return ConversationHandler.WAITING
        else:
            if(not utils.already_created(str(update.message.chat['id']), os.path.abspath(os.path.join(getcwd(), 'data/campaigns')))):
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WELCOME, context.chat_data['lang'], False), reply_markup=generate_keyboard(utils.get_translation_list(GROUP_START, context.chat_data['lang'], True), False))
                return CHECKER
            else:
                context.user_data['in_conversation'] = False
                context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_MENU_MESSAGE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardRemove())
                return ConversationHandler.WAITING
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_LANG, context.chat_data['lang'], False), reply_markup=generate_keyboard(utils.get_flags(), False))
        return LANGUAGE_FOLLOW_UP


def private_language(update, context):
    try:
        context.chat_data['lang']
        if update.message.text != '/lang':
            return ConversationHandler.END
    except Exception:
        if update.message.text != '/start':
            return ConversationHandler.END
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_LANG, 'en_US', False), reply_markup=generate_keyboard(utils.get_flags(), False))
    return LANGUAGE_FOLLOW_UP


def private_language_follow_up(update, context):
    flags = utils.get_flags()
    logging.info(update.message.text)
    if update.message.text in flags:
        context.chat_data['lang'] = utils.map_flag_to_language(update.message.text)
        context.chat_data['user_id'] = update.message.from_user['id']
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_MENU_MESSAGE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_LANG, context.chat_data['lang'], False), reply_markup=generate_keyboard(utils.get_flags(), False))
        return LANGUAGE_FOLLOW_UP


def start_command(is_private=True):
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', callback=private_language, filters=Filters.chat_type.private), CommandHandler('lang', callback=private_language, filters=Filters.chat_type.private)],
        fallbacks=[[MessageHandler(Filters.text, private_language)]],
        persistent=True, name='private_conversation',
        states={
            LANGUAGE: [MessageHandler(Filters.text, private_language)],
            LANGUAGE_FOLLOW_UP: [MessageHandler(Filters.text, private_language_follow_up)]}) if is_private else ConversationHandler(
                entry_points=[
                    CommandHandler('start', callback=group_language, filters=Filters.chat_type.group), CommandHandler('lang', callback=group_language, filters=Filters.chat_type.group)],
                fallbacks=[MessageHandler(Filters.text, group_start)],
                per_chat=True,
                per_user=True,
                persistent=True,
                allow_reentry=True,
                name='group_conversation',
                states={
                    START: [MessageHandler(Filters.text, group_start)],
                    LANGUAGE: [MessageHandler(Filters.text, group_language)],
                    LANGUAGE_FOLLOW_UP: [MessageHandler(Filters.text, group_language_follow_up)],
                    CHECKER: checker.command(),
                    NEW_CAMPAIGN: campaign.command(is_private=False),
                    NEW_CAMPAIGN_FOLLOW_UP: campaign.new_campaign_command(),
                    CAMPAIGN_CREATION: campaign.campaign_creation_command()})


def private_menu_command():
    return ConversationHandler(
        entry_points=[CommandHandler('menu', callback=menu.private_menu, filters=Filters.chat_type.private)],
        fallbacks=[[MessageHandler(Filters.text, menu.private_menu)]],
        persistent=True,
        name='private_menu',
        allow_reentry=True,
        states={
            MENU: [MessageHandler(Filters.text, menu.private_menu)],
            MENU_CHECKER: [MessageHandler(Filters.text, menu.private_menu_checker)],
            ACTIVE_CAMPAIGNS: [MessageHandler(Filters.text, menu.active_campaign_handler)],
            PLAYER_CHECKER: [MessageHandler(Filters.text, checker.player_checker)],
            CHARACTER_CREATION: [MessageHandler(Filters.text, checker.character_creation)],
            CHARACTER_IMPORT: [MessageHandler(Filters.document, checker.character_import)],
            DUNGEON_MASTER_CHECKER: [MessageHandler(Filters.text, checker.dungeon_master_checker)],
            RESTORE_HP_CHECKER: [MessageHandler(Filters.text, checker.restore_hp_checker)],
            RESTORE_HP_VALUE: [MessageHandler(Filters.text, checker.restore_hp_value)],
            RESTORE_HP_CHAR: [MessageHandler(Filters.text, checker.restore_hp_char)]})


def group_menu_command():
    return ConversationHandler(
        entry_points=[CommandHandler('menu', callback=menu.menu, filters=Filters.chat_type.group)],
        fallbacks=[MessageHandler(Filters.text, menu.menu)],
        per_chat=True,
        per_user=True,
        allow_reentry=True,
        persistent=True,
        name='group_conversation',
        states={
            GROUP_MENU_CHECKER: checker.universal_filter_command(),
            NEW_CAMPAIGN_CHECKER: campaign.command_checker(),
            NEW_CAMPAIGN_FOLLOW_UP_CHECKER: campaign.new_campaign_checker_command(),
            CAMPAIGN_CREATION_CHECKER: campaign.campaign_creation_checker_command(),
            DICE_NUMBER: [MessageHandler(Filters.text, checker.dice_handler)],
            DICE_COUNT: [MessageHandler(Filters.text, checker.dice_count)]
        })
