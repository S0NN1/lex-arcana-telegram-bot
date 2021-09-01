import logging
import os
import json
from telegram.ext import CommandHandler, Filters
from . import utils, start
from .constants import PRIVATE_BACK, PRIVATE_CAMPAIGN_MENU, PRIVATE_CAMPAIGN_MENU_KEYBOARD, PRIVATE_CHAR_CREATE, PRIVATE_CHAR_CREATE_KEYBOARD, PRIVATE_CHOOSE_CAMPAIGN, PRIVATE_DM_CAMPAIGN_MENU, PRIVATE_DM_CAMPAIGN_MENU_KEYBOARD, PRIVATE_MENU_TRANSLATION, PRIVATE_MENU_TRANSLATION_KEYBOARD, GROUP_MENU_TRANSLATION, GROUP_MENU_TRANSLATION_KEYBOARD, CAMPAIGN_PATH

cwd = os.getcwd()


def command():
    return CommandHandler("menu", menu, filters=Filters.chat_type.group)


def menu(update, context):
    menu_list = utils.get_translation_list(GROUP_MENU_TRANSLATION, context.chat_data['lang'], True)
    text_message = ""
    for text in menu_list:
        text_message = text_message + text
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(GROUP_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
    return start.GROUP_MENU_CHECKER


def private_menu(update, context):
    menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
    text_message = ""
    for text in menu_list:
        text_message = text_message + text
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
    return start.MENU_CHECKER


def private_menu_checker(update, context):
    reply = update.message.text
    logging.info(reply)
    possibilities = utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True)
    if reply == possibilities[0]:
        context.chat_data['activeCampaigns'] = utils.get_active_campaigns(update.message.from_user['id'])
        campaign_names = []
        for campaign in context.chat_data['activeCampaigns']:
            campaign_names.append(campaign['name'])
        campaign_names.append(utils.get_translation_list(PRIVATE_BACK, context.chat_data['lang'], False))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=utils.get_translation_list(PRIVATE_CHOOSE_CAMPAIGN, context.chat_data['lang'], False), reply_markup=utils.generate_keyboard(campaign_names, False))
        return start.ACTIVE_CAMPAIGNS
    else:
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER


def active_campaign_handler(update, context):
    reply = update.message.text
    found = False
    for campaign in context.chat_data['activeCampaigns']:
        if campaign['name'] == reply:
            found = True
            index = context.chat_data['activeCampaigns'].index(campaign)
            logging.info(index)
            break
    if found:
        if context.chat_data['activeCampaigns'][index]['isDM']:
            menu_list = utils.get_translation_list(PRIVATE_DM_CAMPAIGN_MENU, context.chat_data['lang'], True)
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_DM_CAMPAIGN_MENU_KEYBOARD, context.chat_data['lang'], True), False))
            context.chat_data['currentCampaign'] = context.chat_data['activeCampaigns'][index]['id']
            return start.DUNGEON_MASTER_CHECKER
        else:
            menu_list = utils.get_translation_list(PRIVATE_CAMPAIGN_MENU, context.chat_data['lang'], True)
            player_menu_keyboard = utils.get_translation_list(PRIVATE_CAMPAIGN_MENU_KEYBOARD, context.chat_data['lang'], True)
            id_found = False
            character_created = False
            with open(os.path.join(os.path.join(cwd, CAMPAIGN_PATH), context.chat_data['activeCampaigns'][index]['id']), 'r') as json_file:
                json_dict = json.load(json_file)
                for player in json_dict['players']:
                    if player['id'] == update.message.from_user['id']:
                        id_found = True
                        if 'character' in player.keys():
                            character_created = True
                        break

                if id_found and not character_created:
                    menu_list[0] = utils.get_translation_list(PRIVATE_CHAR_CREATE, context.chat_data['lang'], False)
                    player_menu_keyboard[0] = utils.get_translation_list(PRIVATE_CHAR_CREATE_KEYBOARD, context.chat_data['lang'], False)

            logging.info(menu_list)
            json_file.close()
            text_message = ""
            for text in menu_list:
                text_message = text_message + text
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(player_menu_keyboard, False))
            context.chat_data['currentCampaign'] = context.chat_data['activeCampaigns'][index]['id']
            return start.PLAYER_CHECKER
    else:
        menu_list = utils.get_translation_list(PRIVATE_MENU_TRANSLATION, context.chat_data['lang'], True)
        text_message = ""
        for text in menu_list:
            text_message = text_message + text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text_message, reply_markup=utils.generate_keyboard(utils.get_translation_list(PRIVATE_MENU_TRANSLATION_KEYBOARD, context.chat_data['lang'], True), False))
        return start.MENU_CHECKER
