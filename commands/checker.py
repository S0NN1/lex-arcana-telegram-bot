from commands import dice_roller, dungeon_master, utils, character
from . import start
import telegram
import json
import logging
from telegram.ext import MessageHandler, Filters
from .constants import FILE_EXTENSION, GROUP_CAMPAIGN_ARCHIVED, GROUP_CAMPAIGN_NO_ACTIVE, GROUP_CHAR_CREATION, GROUP_CHAR_CREATION_2, GROUP_CHAR_CREATION_KEYBOARD, GROUP_DICE, GROUP_DICE_DESC, GROUP_DICE_VALUE, GROUP_DM_ACTION, GROUP_MENU_TRANSLATION, GROUP_WARN_2, GROUP_WARN_3, GROUP_WARN_4, PRIVATE_CAMPAIGN_MENU_KEYBOARD, PRIVATE_CHAR_CREATE_KEYBOARD, PRIVATE_DM_CAMPAIGN_MENU_KEYBOARD, PRIVATE_HP_CHOOSE, PRIVATE_HP_MENU, PRIVATE_HP_MENU_KEYBOARD, PRIVATE_HP_RESTORED, PRIVATE_HP_VALUE, PRIVATE_MENU_TRANSLATION, PRIVATE_MENU_TRANSLATION_KEYBOARD, GROUP_START, GROUP_CAMPAIGN_NAME, GROUP_MENU_WRONG_MESSAGE, GROUP_MENU_TRANSLATION_KEYBOARD, ACTION_NOT_IMPLEMENTED, RESOURCES_PATH, GROUP_LANG
from os import path, getcwd, remove

cwd = getcwd()


def command():
    return [MessageHandler(Filters.text, checker)]


def checker(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.CHECKER
    reply = update.message.text
    possibilities = utils.get_translation_list(GROUP_START, context.chat_data['lang'], True)
    if(reply == possibilities[0]):
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_NAME, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
        return start.NEW_CAMPAIGN
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_MENU_WRONG_MESSAGE, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_START, context.chat_data['lang'], True), False))
        return start.CHECKER


def universal_filter(update, context):
    reply = update.message.text
    conversation_list = utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True)
    if 'campaign_id' in context.chat_data.keys() and context.chat_data['campaign_id'] is not None:
        if reply == conversation_list[0]:
            text_message = utils.get_active_campaign(context.chat_data['campaign_id'], context.chat_data['lang'])
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML)
            return start.GROUP_MENU_CHECKER
        elif reply == conversation_list[2]:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_DICE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardRemove())
            return start.DICE_NUMBER
        elif reply == conversation_list[3]:
            players_list = utils.get_players(context.chat_data['campaign_id'] + FILE_EXTENSION)
            for player in players_list:
                text_message = 'USER: @' + player['username'] + '\n'
                text_message = text_message + utils.save_character(context.chat_data['campaign_id'] + FILE_EXTENSION, player['id'], None, context.chat_data['lang'])
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML)
                return start.GROUP_MENU_CHECKER
        elif reply in [conversation_list[4]]:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WARN_2, context.chat_data['lang'], False))
            return start.GROUP_MENU_CHECKER
        elif reply == conversation_list[5]:
            if utils.is_dm(context.chat_data['campaign_id'], update.message.from_user['id']):
                utils.archive_campaign(context.chat_data['campaign_id'])
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_ARCHIVED, context.chat_data['lang'], False))
                context.chat_data['campaign_name'] = None
                context.chat_data['campaign_id'] = None
                context.chat_data['dungeon_master_id'] = None
                context.chat_data['dungeon_master_name'] = None
                context.chat_data['active_players'] = None
                context.chat_data['campaign_data'] = None
                context.chat_data['user_id_in_conversation'] = None
                return start.GROUP_MENU_CHECKER
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_DM_ACTION, context.chat_data['lang'], False))
                return start.GROUP_MENU_CHECKER
        elif reply in conversation_list:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(ACTION_NOT_IMPLEMENTED, context.chat_data['lang'], False))
        else:
            start.GROUP_MENU_CHECKER
    elif reply in [conversation_list[4]]:
        if context.chat_data['user_id_in_conversation'] is None or context.chat_data['user_id_in_conversation'] == update.message.from_user['id']:
            context.chat_data['user_id_in_conversation'] = update.message.from_user['id']
            context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_NAME, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
            return start.NEW_CAMPAIGN_CHECKER
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WARN_4, context.chat_data['lang'], False))
            return start.GROUP_MENU_CHECKER
    elif '/start' in reply:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WARN_3, context.chat_data['lang'], False))
        return start.GROUP_MENU_CHECKER
    elif '/lang' in reply:
        context.chat_data['is_change_lang'] = True
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_LANG, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_flags(), False))
        return start.LANGUAGE_FOLLOW_UP
    elif reply in conversation_list:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_NO_ACTIVE, context.chat_data['lang'], False))
        return start.GROUP_MENU_CHECKER
    else:
        return start.GROUP_MENU_CHECKER


def universal_filter_command():
    return [MessageHandler(Filters.chat_type.group & Filters.text, universal_filter)]


def player_checker(update, context):
    reply = update.message.text
    possibilities = utils.get_translation_list(PRIVATE_CAMPAIGN_MENU_KEYBOARD, context.chat_data['lang'], True)
    possibilities.append(utils.get_translation_list(PRIVATE_CHAR_CREATE_KEYBOARD, context.chat_data['lang'], False))
    logging.info(possibilities[3])
    if reply == possibilities[0]:
        text_message = utils.save_character(context.chat_data['currentCampaign'], update.message.from_user['id'], None, context.chat_data['lang'])
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML)
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    elif reply == possibilities[1]:
        players_list = utils.get_players(context.chat_data['currentCampaign'])
        for player in players_list:
            text_message = 'USER: @' + player['username'] + '\n'
            text_message = text_message + utils.save_character(context.chat_data['currentCampaign'], player['id'], None, context.chat_data['lang'])
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML)
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    elif reply == possibilities[2]:
        result_dict = utils.get_character_file(context.chat_data['currentCampaign'], update.message.from_user['id'])
        file_path = path.join(path.join(cwd, RESOURCES_PATH) + 'temp_character' + str(update.message.from_user['id']) + FILE_EXTENSION)
        with open(file_path, 'w') as temp_character_file:
            json.dump(result_dict, temp_character_file, indent=4, sort_keys=True)
            temp_character_file.close()
        with open(file_path, 'r') as temp_character_file:
            context.bot.send_document(update.effective_chat.id, document=temp_character_file, filename='character.json')
            temp_character_file.close()
        remove(file_path)
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    elif reply == possibilities[3]:
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    elif reply == possibilities[4]:
        menu_list = utils.get_translation_list(GROUP_CHAR_CREATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_CHAR_CREATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.CHARACTER_CREATION
    else:
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER


def dungeon_master_checker(update, context):
    reply = update.message.text
    logging.info(reply)
    possibilities = utils.get_translation_list(PRIVATE_DM_CAMPAIGN_MENU_KEYBOARD, context.chat_data['lang'], True)
    if reply == possibilities[0]:
        players_list = utils.get_players(context.chat_data['currentCampaign'])
        for player in players_list:
            text_message = 'USER: @' + player['username'] + '\n'
            text_message = text_message + utils.save_character(context.chat_data['currentCampaign'], player['id'], None, context.chat_data['lang'])
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML)
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    elif reply == possibilities[1] or reply == possibilities[2]:
        if reply == possibilities[1]:
            context.chat_data['isRestoreGroup'] = False
            players = utils.get_players(context.chat_data['currentCampaign'])
            print(players)
            print(context.chat_data['currentCampaign'])
            keyboard = []
            for player in players:
                keyboard.append([telegram.KeyboardButton('@' + player['username'])])
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_HP_CHOOSE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardMarkup(keyboard))
            return start.RESTORE_HP_CHAR
        else:
            menu_list = utils.get_translation_list(PRIVATE_HP_MENU, context.chat_data['lang'], True)
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.chat_data['isRestoreGroup'] = True
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_HP_MENU_KEYBOARD, context.chat_data['lang'], True), False))
            return start.RESTORE_HP_CHECKER
    elif reply == possibilities[3] or reply == possibilities[4]:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(ACTION_NOT_IMPLEMENTED, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    else:
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER


def character_creation(update, context):
    reply = update.message.text
    possibilities = utils.get_translation_list(GROUP_CHAR_CREATION_KEYBOARD, context.chat_data['lang'], True)
    if reply == possibilities[0]:
        with open(path.join(cwd, RESOURCES_PATH) + 'character_template.json', 'r') as json_file:
            context.bot.send_document(chat_id=update.effective_chat.id, document=json_file, caption=utils.get_translation_list(GROUP_CHAR_CREATION_2, context.chat_data['lang'], False), filename='template.json')
            json_file.close()
        return start.CHARACTER_IMPORT
    elif reply == possibilities[1]:
        text_message = utils.save_character(context.chat_data['currentCampaign'], update.message.from_user['id'], character.generate_character(context.chat_data['lang']), context.chat_data['lang'])
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    else:
        return start.CHARACTER_CREATION


def character_import(update, context):
    file_path = path.join(cwd, RESOURCES_PATH) + 'temp_template.json'
    with open(file_path, 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)
        f.close()
    if utils.check_schema():
        with open(file_path, 'r') as f:
            input_dict = json.load(f)
            f.close()
        character = utils.save_character(context.chat_data['currentCampaign'], update.message.from_user['id'], input_dict, context.chat_data['lang'])
        remove(file_path)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=character, parse_mode=telegram.ParseMode.HTML, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
    else:
        remove(file_path)
        return start.CHARACTER_IMPORT


def restore_hp_checker(update, context):
    reply = update.message.text
    possibilities = utils.get_translation_list(PRIVATE_HP_MENU_KEYBOARD, context.chat_data['lang'], True)
    print(possibilities)
    if possibilities[0] == reply:
        context.chat_data['isPercentage'] = True
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_HP_VALUE, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
        return start.RESTORE_HP_VALUE
    elif possibilities[1] == reply:
        context.chat_data['isPercentage'] = False
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_HP_VALUE, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
        return start.RESTORE_HP_VALUE
    else:
        return start.RESTORE_HP_CHECKER


def restore_hp_value(update, context):
    reply = update.message.text
    if reply.isnumeric():
        if context.chat_data['isPercentage'] and int(reply) <= 100 and int(reply) >= 0:
            if context.chat_data['isRestoreGroup']:
                dungeon_master.restore_hp_party(context.chat_data['currentCampaign'], int(reply), True)
            else:
                dungeon_master.restore_hp(context.chat_data['currentCampaign'], context.chat_data['restoreCharacter'], int(reply), True)
            context.chat_data['isRestoreGroup'] = None
            context.chat_data['isPercentage'] = None
            context.chat_data['restoreCharacter'] = None
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_HP_RESTORED, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
            return start.MENU_CHECKER
        elif not context.chat_data['isPercentage']:
            dungeon_master.restore_hp_party(context.chat_data['currentCampaign'], int(reply), False)
            context.chat_data['isRestoreGroup'] = None
            context.chat_data['isPercentage'] = None
            context.chat_data['restoreCharacter'] = None
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_HP_RESTORED, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
            return start.MENU_CHECKER
        else:
            return start.RESTORE_HP_VALUE
    else:
        return start.RESTORE_HP_VALUE


def dice_handler(update, context):
    reply = update.message.text
    if reply.isnumeric() and int(reply) >= 0 and int(reply) <= 10:
        context.user_data['dice_number'] = int(reply)
        context.user_data['dice_value'] = []
        dice = dice_roller.most_used_dice(update.message.from_user['id'], context.chat_data['campaign_id'])
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_DICE_DESC, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(dice, False))
        return start.DICE_COUNT
    else:
        return start.DICE_NUMBER


def dice_count(update, context):
    reply = update.message.text
    possibilities = dice_roller.most_used_dice(update.message.from_user['id'], context.chat_data['campaign_id'])
    if reply in possibilities:
        context.user_data['dice_number'] = context.user_data['dice_number'] - 1
        context.user_data['dice_value'].append(int(reply[1:]))
        if context.user_data['dice_number'] == 0:
            for dice in context.user_data['dice_value']:
                value = dice_roller.roll_dice(dice, update.message.from_user['id'], context.chat_data['campaign_id'])
                context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_DICE_VALUE, context.chat_data['lang'], False) + str(value))
            menu_list = utils.get_translation_list(GROUP_MENU_TRANSLATION, context.chat_data['lang'], True)
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
            return start.GROUP_MENU_CHECKER
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
            return start.DICE_COUNT
    else:
        return start.DICE_COUNT


def restore_hp_char(update, context):
    reply = update.message.text
    players = utils.get_players(context.chat_data['currentCampaign'])
    for player in players:
        if player['username'] == reply[1:]:
            context.chat_data['restoreCharacter'] = player['id']
            menu_list = utils.get_translation_list(PRIVATE_HP_MENU, context.chat_data['lang'], True)
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_HP_MENU_KEYBOARD, context.chat_data['lang'], True), False))
            return start.RESTORE_HP_CHECKER
    return start.RESTORE_HP_CHAR
