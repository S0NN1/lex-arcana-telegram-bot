import telegram
import logging
import os
import json
import jsonschema
import shutil
from pathlib import Path
from os import getcwd, path
from .constants import CAMPAIGN_PATH, DATA_PATH, GROUP_CAMPAIGN_TITLES, USER_FILE, RESOURCES_PATH, PERSISTENCE_PATH, FILE_EXTENSION, PRIVATE_CHAR_TITLES, ARCHIVED_CAMPAIGN_PATH

cwd = getcwd()


def generate_keyboard(buttons, is_inline):
    keyboard = []
    if is_inline:
        for button in buttons:
            keyboard.append([telegram.InlineKeyboardButton(text=button, callback_data=button)])
        return telegram.InlineKeyboardMarkup(keyboard)
    else:
        for button in buttons:
            keyboard.append([telegram.KeyboardButton(button)])
        return telegram.ReplyKeyboardMarkup(keyboard)


def get_translation_list(keyword, language, is_keyboard):
    keywords = keyword.split('.')
    translation_list = []
    with open(path.join(cwd, RESOURCES_PATH) + 'translations.json', 'r') as json_file:
        json_dict = json.load(json_file)
        language_dict = json_dict[language]
        for key in keywords:
            language_dict = language_dict[key]
    for dict_key in language_dict.keys():
        translation_list.append(language_dict[dict_key])
    json_file.close
    if is_keyboard is None:
        return language_dict
    elif not is_keyboard:
        return translation_list[0]
    else:
        return translation_list


def get_language(user_id):
    with open(path.join(cwd, DATA_PATH) + USER_FILE, 'r') as json_file:
        json_dict = json.load(json_file)
        for user in json_dict['users']:
            if user['id'] == user_id:
                if user['lang']:
                    return user['lang']
                else:
                    break
    return 'en_US'


def get_character_file(campaign_id, user_id):
    result_dict = {}
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r') as json_file:
        json_dict = json.load(json_file)
        if 'players' in json_dict.keys():
            for player in json_dict['players']:
                if 'character' in player.keys() and player['id'] == user_id:
                    result_dict = player['character']
        json_file.close()
    return result_dict


def already_created(keyword, path_name):
    logging.info(path_name)
    for filename in os.listdir(path_name):
        if filename.endswith(FILE_EXTENSION):
            logging.info(filename)
            with open(path.join(path_name, filename)) as f:
                if keyword in f.read():
                    f.close()
                    return True
                f.close()
    return False


def map_flag_to_language(flag):
    if flag == '🇮🇹':
        return 'it_IT'
    elif flag == '🇺🇸':
        return 'en_US'


def get_flags():
    return ['🇺🇸', '🇮🇹']


def check_files_and_directories():
    os.makedirs(os.path.join(cwd, CAMPAIGN_PATH), exist_ok=True)
    os.makedirs(os.path.join(cwd, ARCHIVED_CAMPAIGN_PATH), exist_ok=True)
    os.makedirs(os.path.join(cwd, PERSISTENCE_PATH), exist_ok=True)
    if not os.path.exists(os.path.join(cwd, DATA_PATH) + USER_FILE):
        with open(os.path.join(cwd, DATA_PATH) + USER_FILE, 'w') as json_file:
            user_dict = {"users": []}
            json_file.seek(0)
            json.dump(user_dict, json_file, indent=4, sort_keys=True)
            json_file.truncate()
        json_file.close
        Path(os.path.join(cwd, DATA_PATH) + USER_FILE).touch()


def json_to_dict(keyword, json_name):
    keywords = keyword.split('.')
    with open(path.join(cwd, RESOURCES_PATH) + json_name + '.json', 'r') as json_file:
        json_dict = json.load(json_file)
        for key in keywords:
            json_dict = json_dict[key]
    json_file.close
    return json_dict


def get_active_campaigns(user_id):
    campaigns = []
    for filename in os.listdir(os.path.join(cwd, CAMPAIGN_PATH)):
        if filename.endswith(FILE_EXTENSION):
            with open(os.path.join(os.path.join(cwd, CAMPAIGN_PATH), filename), 'r') as json_file:
                json_dict = json.load(json_file)
                if "dungeonMasterId" in json_dict.keys() and str(json_dict['dungeonMasterId']) == str(user_id):
                    campaigns.append({"name": json_dict['name'], "isDM": True, "id": filename})
                    json_file.close()
                else:
                    if "players" in json_dict.keys():
                        for player in json_dict['players']:
                            if player['id'] == user_id:
                                campaigns.append({"name": json_dict['name'], "isDM": False, "id": filename})
                                json_file.close()
    print(sorted(campaigns, key=lambda k: k['name']))
    return sorted(campaigns, key=lambda k: k['name'])


def get_players(campaign_id):
    players_list = []
    with open(os.path.join(os.path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r') as json_file:
        json_dict = json.load(json_file)
        if 'players' in json_dict.keys():
            for player in json_dict['players']:
                if 'character' in player.keys():
                    players_list.append({'id': player['id'], 'username': player['username']})
    return players_list


def save_character(campaign_id, player_id, character, language):
    print(character)
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r+') as json_file:
        json_dict = json.load(json_file)
        for player in json_dict['players']:
            if player['id'] == player_id:
                if 'character' not in player.keys():
                    player['character'] = character
                result_character = player['character']
                break
        json_file.seek(0)
        json.dump(json_dict, json_file, indent=4, sort_keys=True)
        json_file.truncate()
        json_file.close
        translate_character(result_character, language)
        print(result_character)
        return character_to_message(result_character, language)


def character_to_message(character, lang):
    message = ''
    titles = get_translation_list(PRIVATE_CHAR_TITLES, lang, True)
    message = message + '\n' + new_line(bold(titles[0].upper()))
    message = message + new_line(character['name'])

    message = message + '\n' + new_line(bold(titles[1].upper()))
    message = message + new_line(character['gender'])

    message = message + '\n' + new_line(bold(titles[2].upper()))
    message = message + new_line(str(character['aetas']))

    message = message + '\n' + new_line(bold(titles[3].upper()))
    message = message + new_line(character['input_province'])

    message = message + '\n' + new_line(bold(titles[4].upper()))
    message = message + new_line(list_string(character['languages']))

    message = message + '\n' + new_line(bold(titles[5].upper()))
    message = message + new_line(character['city'])

    message = message + '\n' + new_line(bold(titles[6].upper()))
    message = message + new_line(character['origin'])

    message = message + '\n' + new_line(bold(titles[7].upper()))
    message = message + new_line(character['house'])

    message = message + '\n' + new_line(bold(titles[8].upper()))
    message = message + new_line(character['own_class'])

    message = message + '\n' + new_line(bold(titles[9].upper()))
    message = message + new_line(character['grade'])

    message = message + '\n' + new_line(bold(titles[10].upper()))
    message = message + new_line(str(character['hp']) + '/' + str(character['max_hp']))

    message = message + '\n' + new_line(bold(titles[11].upper()))
    message = message + new_line(str(character['weight']))

    message = message + '\n' + new_line(bold(titles[12].upper()))
    message = message + list_stats(character['virtutes'], None)

    message = message + '\n' + new_line(bold(titles[13].upper()))
    message = message + list_stats(character['peritiae'], character['specs'])

    message = message + '\n' + new_line(bold(titles[14].upper()))
    message = message + new_line(str(character['pietas']) + '/' + str(character['max_pietas']))

    message = message + '\n' + new_line(bold(titles[15].upper()))
    message = message + list_stats(character['multipliers'], None)

    if('armor' in character['equipment'].keys()):
        message = message + '\n' + new_line(bold(titles[16].upper()))
        message = message + new_line(character['equipment']['armor'])

    if('shield' in character['equipment'].keys()):
        message = message + '\n' + new_line(bold(titles[17].upper()))
        message = message + new_line(character['equipment']['shield'])

    message = message + '\n' + new_line(bold(titles[18].upper()))
    message = message + list_weapons(character['equipment']['melee_weapons'], lang)

    message = message + '\n' + new_line(bold(titles[19].upper()))
    message = message + list_weapons(character['equipment']['ranged_weapons'], lang)

    message = message + '\n' + new_line(bold(titles[20].upper()))
    message = message + new_line(list_string(character['equip']))

    message = message + '\n' + new_line(bold(titles[21].upper()))
    message = message + new_line('6🔺 ' + character['indigitamenta'])

    message = message + '\n' + new_line(bold(titles[22].upper()))
    message = message + new_line(underlined(character['combat_skills']['name']) + ': ' + character['combat_skills']['description'])

    message = message + '\n' + new_line(bold(titles[23].upper()))
    message = message + new_line(character['bio'])
    print(message)

    return message


def bold(string):
    return '<b>' + string + '</b>'


def underlined(string):
    return '<u>' + string + '</u>'


def italic(string):
    return '<i>' + string + '</i>'


def new_line(string):
    return str(string) + '\n'


def list_string(list):
    string = ''
    for str in list:
        string = string + str + ', '
    string = string[:len(string) - 2]
    return string


def list_stats(list, specs):
    string = ''
    i = 0
    for key in sorted(list.keys()):
        string = string + underlined(key[:2] + ' ' + key[2:] if 'De' in key and 'rum' not in key else key) + ': ' + str(list[key]) + '\n'
        if specs is not None:
            for spec in specs:
                if spec['peritiae'][4:] == key:
                    string = string + italic(spec['id']) + ": " + str(spec['val']) + '\n'
        i = i + 1
    return string


def list_weapons(list, language):
    string = ''
    desc = get_translation_list('weaponsDescriptions', language, True)
    for object in list:
        string = new_line(string + underlined(object['name']))

        if not len(object['traits']) == 0:
            string = string + italic(desc[0]) + ": "
            string = new_line(string + list_string(object['traits']))
        if 'range' in object.keys():
            string = string + italic(desc[1]) + ": "
            string = new_line(string + list_string(object['range']))
    return string


def translate_character(character, lang):
    character['own_class'] = get_translation_list('class', lang, None)[character['own_class']]
    character['origin'] = get_translation_list('origin', lang, None)[character['origin']]
    character['house'] = get_translation_list('house', lang, None)[character['house']]
    for spec in character['specs']:
        spec['id'] = get_translation_list('specs.' + spec['id'][:len(spec['id']) - 1], lang, None)[spec['id'][len(spec['id']) - 1:]]
    character['gender'] = get_translation_list('gender', lang, None)[character['gender']]
    languages = []
    for language in character['languages']:
        languages.append(get_translation_list('languages', lang, None)[language])
    character['languages'] = languages
    melee_weapons = []
    for weapon in character['equipment']['melee_weapons']:
        new_weapon = get_translation_list('weapons', lang, None)[weapon]
        if len(new_weapon['traits']) != 0:
            traits = []
            for trait in new_weapon['traits']:
                traits.append(get_translation_list('traits', lang, None)[trait])
            new_weapon['traits'] = traits
        melee_weapons.append(new_weapon)
    character['equipment']['melee_weapons'] = melee_weapons
    ranged_weapons = []
    for weapon in character['equipment']['ranged_weapons']:
        new_weapon = get_translation_list('weapons', lang, None)[weapon]
        if len(new_weapon['traits']) != 0:
            traits = []
            for trait in new_weapon['traits']:
                traits.append(get_translation_list('traits', lang, None)[trait])
            new_weapon['traits'] = traits
        if 'range' in new_weapon.keys() and len(new_weapon['range']) != 0:
            ranges = []
            for range in new_weapon['range']:
                ranges.append(get_translation_list('range', lang, None)[range])
            new_weapon['range'] = ranges
        ranged_weapons.append(new_weapon)
    character['equipment']['ranged_weapons'] = ranged_weapons
    equips = []
    for equip in character['equip']:
        new_equip = equip
        if equip.isnumeric():
            new_equip = get_translation_list('equipment', lang, None)[equip]
        equips.append(new_equip)
    character['equip'] = equips
    character['bio'] = get_translation_list('bio', lang, None)[character['bio']]
    character['indigitamenta'] = get_translation_list('indigitamenta', lang, None)[character['indigitamenta']]
    character['combat_skills'] = get_translation_list('combatSkills', lang, None)[character['combat_skills']]


def is_dm(campaign_id, user_id):
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id) + FILE_EXTENSION, 'r+') as json_file:
        json_dict = json.load(json_file)
        if json_dict['dungeonMasterId'] == user_id:
            return True
    return False


def archive_campaign(campaign_id):
    shutil.move(os.path.join(CAMPAIGN_PATH, campaign_id) + FILE_EXTENSION, ARCHIVED_CAMPAIGN_PATH)


def get_active_campaign(campaign_id, language):
    campaign = {}
    titles = get_translation_list(GROUP_CAMPAIGN_TITLES, language, True)
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id) + FILE_EXTENSION, 'r') as json_file:
        json_dict = json.load(json_file)
        campaign['name'] = json_dict['name']
        campaign['dungeonMasterUsername'] = '@' + json_dict['dungeonMasterUsername']
        campaign['players'] = []
        for player in json_dict['players']:
            if 'character' in player.keys():
                character_name = player['character']['name']
                character_class = get_translation_list('class', language, None)[player['character']['own_class']]
            else:
                character_name = ''
                character_class = ''
            campaign['players'].append({'username': '@' + player['username'], 'character_name': character_name, 'character_class': character_class})
        json_file.close
    message = ''
    message = message + bold(titles[0])
    message = message + new_line(campaign['name'])

    message = message + bold(titles[1])
    message = message + new_line(campaign['dungeonMasterUsername']) + '\n'

    message = message + new_line(bold(titles[2]).upper())
    for player in campaign['players']:
        message = message + bold(titles[3])
        message = message + new_line(player['username'])
        message = message + bold(titles[4])
        message = message + new_line(player['character_name'])
        message = message + bold(titles[5])
        message = message + new_line(player['character_class']) + '\n'

    return message


def check_schema():
    try:
        with open(path.join(cwd, RESOURCES_PATH) + 'character_template.json', 'r') as json_file:
            schema = json.load(json_file)
            json_file.close()
        with open(path.join(cwd, RESOURCES_PATH) + 'temp_template.json', 'r') as f:
            input_dict = json.load(f)
            f.close()
        jsonschema.validate(input_dict, schema)
        return True
    except Exception:
        return False
