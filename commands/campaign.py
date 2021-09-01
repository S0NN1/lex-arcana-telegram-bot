import json
import uuid
import telegram
import os
import logging
from os import getcwd, path
from . import utils, start
from telegram.ext import ConversationHandler, MessageHandler, Filters
from .constants import CAMPAIGN_PATH, GROUP_CAMPAIGN_CONFIRM, GROUP_CAMPAIGN_CREATION, GROUP_CONFIRM_MESSAGE, GROUP_MENU_TRANSLATION, GROUP_MENU_TRANSLATION_KEYBOARD, GROUP_YES_NO, GROUP_CAMPAIGN_ANSWERS, FILE_EXTENSION, GROUP_WELCOME, GROUP_START, GROUP_CAMPAIGN_NAME, GROUP_CAMPAIGN_INVALID, GROUP_CAMPAIGN_SUCCESS, GROUP_MENU_MESSAGE, GROUP_CAMPAIGN_DELETE, GROUP_NO_PLAYERS

dict_mockup = {"groupChatId": 0, "name": "", "dungeonMasterId": 0, "dungeonMasterUsername": "", "players": []}
user_mockup = {
    "id": 0,
    "isDungeonMaster": False,
    "dices": {
        "d3": 0,
        "d4": 0,
        "d5": 0,
        "d6": 0,
        "d8": 0,
        "d10": 0,
        "d12": 0
    }
}
cwd = getcwd()
directory = os.path.abspath(os.path.join(cwd, 'data'))


def generate_campaign(name, dungeon_master_id, group_chat_id, players, dungeon_master_username):
    id = uuid.uuid4().hex
    if path.exists(path.join(path.join(cwd, CAMPAIGN_PATH), id) + FILE_EXTENSION):
        generate_campaign(name, dungeon_master_id, group_chat_id, players, dungeon_master_username)
    else:
        with open(path.join(path.join(cwd, CAMPAIGN_PATH), id) + '.json', 'w') as json_file:
            json_dict = dict_mockup
            json_dict["groupChatId"] = group_chat_id
            json_dict["dungeonMasterId"] = dungeon_master_id
            json_dict["dungeonMasterUsername"] = dungeon_master_username
            json_dict["name"] = name
            json_dict['players'] = []
            for player in players:
                player_dict = {
                    "id": player['id'],
                    "username": player['username']
                }
                json_dict['players'].append(player_dict)
            json.dump(json_dict, json_file, indent=4, sort_keys=True)
            json_file.close
        with open(path.join(cwd, "data/") + 'users.json', 'r+') as user_file:
            user_json_dict = json.load(user_file)
            dicts_not_found = []
            for player in players:
                found = False
                user_dict = user_mockup
                if 'users' not in user_json_dict.keys():
                    user_json_dict['users'] = []
                for user in user_json_dict['users']:
                    if user['id'] == player['id']:
                        if 'campaigns' not in user.keys():
                            user['campaigns'] = []
                        user['campaigns'].append(user_dict)
                        found = True
                        break
                if not found:
                    dicts_not_found.append({
                        "id": player['id'],
                        "username": player['username'],
                        "campaigns":
                        [
                            {
                                "id": id,
                                "isDungeonMaster": False,
                                "dices": {
                                    "d3": 0,
                                    "d4": 0,
                                    "d5": 0,
                                    "d6": 0,
                                    "d8": 0,
                                    "d10": 0,
                                    "d12": 0
                                }
                            },
                        ]
                    })
            for user in user_json_dict['users']:
                if user['id'] == dungeon_master_id:
                    if 'campaigns' not in user.keys():
                        user['campaigns'] = []
                    user_dict['isDungeonMaster'] = True
                    user['campaigns'].append(user_dict)
                    found = True
                    break
            if not found:
                dicts_not_found.append({
                    "id": dungeon_master_id,
                    "username": dungeon_master_username,
                    "campaigns":
                    [
                        {
                            "id": id,
                            "isDungeonMaster": True,
                            "dices": {
                                "d3": 0,
                                "d4": 0,
                                "d5": 0,
                                "d6": 0,
                                "d8": 0,
                                "d10": 0,
                                "d12": 0
                            }
                        },
                    ]
                })
            user_json_dict['users'].extend(dicts_not_found)
            user_file.seek(0)
            json.dump(user_json_dict, user_file, indent=4, sort_keys=True)
            user_file.truncate()
            user_file.close()
    return id


def delete_campaign(id):
    if path.exists(path.join(path.join(cwd, CAMPAIGN_PATH), id) + FILE_EXTENSION):
        os.remove(path.join(path.join(cwd, CAMPAIGN_PATH), id) + FILE_EXTENSION)


def new_campaign(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.NEW_CAMPAIGN
    context.chat_data['campaign_name'] = update.message.text
    logging.info(context.chat_data['campaign_name'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CONFIRM_MESSAGE, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True), False))
    return start.NEW_CAMPAIGN_FOLLOW_UP


def new_campaign_checker(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.NEW_CAMPAIGN_CHECKER
    context.chat_data['campaign_name'] = update.message.text
    logging.info(context.chat_data['campaign_name'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CONFIRM_MESSAGE, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True), False))
    return start.NEW_CAMPAIGN_FOLLOW_UP_CHECKER


def new_campaign_follow_up_checker(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.NEW_CAMPAIGN_FOLLOW_UP
    reply = update.message.text
    logging.info(reply)
    context.chat_data['dungeon_master_id'] = update.message.from_user['id']
    context.chat_data['dungeon_master_name'] = update.message.from_user['username'] if update.message.from_user['username'] is not None else update.message.from_user['first_name']
    logging.info(context.chat_data['dungeon_master_id'])
    logging.info(update.message.from_user)
    context.chat_data['group_chat_id'] = update.message.chat['id']
    logging.info(context.chat_data['group_chat_id'])
    context.chat_data['campaign_data'] = utils.get_translation_list(GROUP_CAMPAIGN_CREATION, context.chat_data['lang'], False).replace("*", "*" + context.chat_data['campaign_name'] + "*").replace("@", "@" + context.chat_data['dungeon_master_name'])
    possibilities = utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True)
    if(reply == possibilities[0] and context.chat_data['campaign_name'] is not None):
        context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data['campaign_data'], parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True), True))
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_CONFIRM, context.chat_data['lang'], False), parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_CAMPAIGN_ANSWERS, context.chat_data['lang'], True), False))
        context.chat_data['active_players'] = []
        return start.CAMPAIGN_CREATION_CHECKER
    elif (reply == possibilities[1]):
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_NAME, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
        return start.NEW_CAMPAIGN_CHECKER
    else:
        context.chat_data['campaign_name'] = None
        context.chat_data['dungeon_master_id'] = None
        context.chat_data['dungeon_master_name'] = None
        delete_campaign(context.chat_data['campaign_id'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_INVALID, context.chat_data['lang'], False))
        menu_list = utils.get_translation_list(GROUP_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        context.user_data['in_conversation'] = False
        context.chat_data['user_id_in_conversation'] = None
        return start.GROUP_MENU_CHECKER


def new_campaign_follow_up(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.NEW_CAMPAIGN_FOLLOW_UP_CHECKER
    reply = update.message.text
    logging.info(reply)
    context.chat_data['dungeon_master_id'] = update.message.from_user['id']
    context.chat_data['dungeon_master_name'] = update.message.from_user['username'] if update.message.from_user['username'] is not None else update.message.from_user['first_name']
    logging.info(context.chat_data['dungeon_master_id'])
    logging.info(update.message.from_user)
    context.chat_data['group_chat_id'] = update.message.chat['id']
    logging.info(context.chat_data['group_chat_id'])
    context.chat_data['campaign_data'] = utils.get_translation_list(GROUP_CAMPAIGN_CREATION, context.chat_data['lang'], False).replace("*", "*" + context.chat_data['campaign_name'] + "*").replace("@", "@" + context.chat_data['dungeon_master_name'])
    possibilities = utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True)
    if(reply == possibilities[0] and context.chat_data['campaign_name'] is not None):
        context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data['campaign_data'], parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True), True))
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_CONFIRM, context.chat_data['lang'], False), parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_CAMPAIGN_ANSWERS, context.chat_data['lang'], True), False))
        context.chat_data['active_players'] = []
        return start.CAMPAIGN_CREATION
    elif (reply == possibilities[1]):
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_NAME, context.chat_data['lang'], False), reply_markup=telegram.ForceReply())
        return start.NEW_CAMPAIGN
    else:
        context.chat_data['campaign_name'] = None
        context.chat_data['dungeon_master_id'] = None
        context.chat_data['dungeon_master_name'] = None
        delete_campaign(context.chat_data['campaign_id'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_INVALID, context.chat_data['lang'], False))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WELCOME, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_START, context.chat_data['lang'], True), False))
        context.user_data['in_conversation'] = True
        context.chat_data['user_id_in_conversation'] = None
        return start.CHECKER


def campaign_creation(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.CAMPAIGN_CREATION
    reply = update.message.text
    answers = utils.get_translation_list(GROUP_CAMPAIGN_ANSWERS, context.chat_data['lang'], True)
    if(reply == answers[0] and len(context.chat_data['active_players']) != 0):
        context.chat_data['campaign_id'] = generate_campaign(context.chat_data['campaign_name'], context.chat_data['dungeon_master_id'], context.chat_data['group_chat_id'], context.chat_data['active_players'], context.chat_data['dungeon_master_name'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_SUCCESS, context.chat_data['lang'], False))
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_MENU_MESSAGE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardRemove())
        context.user_data['in_conversation'] = False
        context.chat_data['user_id_in_conversation'] = None
        return ConversationHandler.END
    elif reply == answers[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_NO_PLAYERS, context.chat_data['lang'], False))
        return start.CAMPAIGN_CREATION
    else:
        context.chat_data['campaign_name'] = None
        context.chat_data['dungeon_master_id'] = None
        context.chat_data['dungeon_master_name'] = None
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_DELETE, context.chat_data['lang'], False))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_WELCOME, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_START, context.chat_data['lang'], True), False))
        context.user_data['in_conversation'] = True
        return start.CHECKER


def campaign_creation_checker(update, context):
    if update.message.from_user['id'] != context.chat_data['user_id_in_conversation']:
        return start.CAMPAIGN_CREATION_CHECKER
    reply = update.message.text
    answers = utils.get_translation_list(GROUP_CAMPAIGN_ANSWERS, context.chat_data['lang'], True)
    if(reply == answers[0] and len(context.chat_data['active_players']) != 0):
        context.chat_data['campaign_id'] = generate_campaign(context.chat_data['campaign_name'], context.chat_data['dungeon_master_id'], context.chat_data['group_chat_id'], context.chat_data['active_players'], context.chat_data['dungeon_master_name'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_SUCCESS, context.chat_data['lang'], False))
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_MENU_MESSAGE, context.chat_data['lang'], False), reply_markup=telegram.ReplyKeyboardRemove())
        context.user_data['in_conversation'] = False
        context.chat_data['user_id_in_conversation'] = None
        return ConversationHandler.END
    elif reply == answers[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_NO_PLAYERS, context.chat_data['lang'], False))
        return start.CAMPAIGN_CREATION_CHECKER
    else:
        context.chat_data['campaign_name'] = None
        context.chat_data['dungeon_master_id'] = None
        context.chat_data['dungeon_master_name'] = None
        context.bot.send_message(chat_id=update.effective_chat.id, text=utils.get_translation_list(GROUP_CAMPAIGN_DELETE, context.chat_data['lang'], False))
        menu_list = utils.get_translation_list(GROUP_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        context.user_data['in_conversation'] = False
        context.chat_data['user_id_in_conversation'] = None
        return start.GROUP_MENU_CHECKER


def inline_button(update, context):
    temp_campaign_data = context.chat_data['campaign_data']
    query = update.callback_query
    username = update.callback_query.from_user['username']
    if username is None:
        username = update.callback_query.from_user['first_name']
    query.answer()
    checkers = utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True)
    if query.data == checkers[0]:
        if username not in context.chat_data['campaign_data']:
            context.chat_data['campaign_data'] = context.chat_data['campaign_data'] + '*@' + username + '*' + '\n'
            player_dict = {'id': update.callback_query.from_user['id'], 'username': update.callback_query.from_user['username' if update.callback_query.from_user['username'] is not None else 'first_name']}
            context.chat_data['active_players'].append(player_dict)
    else:
        if ('*@' + username + '*' + '\n') in context.chat_data['campaign_data']:
            context.chat_data['campaign_data'] = context.chat_data['campaign_data'].replace('*@' + username + '*' + '\n', '')
            player_dict = {'id': update.callback_query.from_user['id'], 'username': update.callback_query.from_user['username' if update.callback_query.from_user['username'] is not None else 'first_name']}
            context.chat_data['active_players'].remove(player_dict)

    if context.chat_data['campaign_data'] != temp_campaign_data:
        query.edit_message_text(text=context.chat_data['campaign_data'], parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_YES_NO, context.chat_data['lang'], True), True))


def my_campaigns(update, context):
    return ConversationHandler.END


def command(is_private=True):
    return [MessageHandler(Filters.text, my_campaigns)] if is_private else [MessageHandler(Filters.text, new_campaign)]


def new_campaign_command():
    return [MessageHandler(Filters.text, new_campaign_follow_up)]


def campaign_creation_command():
    return [MessageHandler(Filters.text, campaign_creation)]


def command_checker():
    return [MessageHandler(Filters.text, new_campaign_checker)]


def new_campaign_checker_command():
    return [MessageHandler(Filters.text, new_campaign_follow_up_checker)]


def campaign_creation_checker_command():
    return [MessageHandler(Filters.text, campaign_creation_checker)]
