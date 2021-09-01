from commands.constants import CAMPAIGN_PATH
from os import path, getcwd
import json
cwd = getcwd()


def restore_hp(campaign_id, player_id, percentage, is_percetage):
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r+') as json_file:
        json_dict = json.load(json_file)
        for player in json_dict['players']:
            if player["id"] == player_id:
                hp = percentage
                if is_percetage:
                    hp = player['character']['max_hp'] / 100 * percentage
                if player['character']['hp'] + hp >= player['character']['max_hp']:
                    player['character']['hp'] = player['character']['max_hp']
                else:
                    player['character']['hp'] = player['character']['hp'] + hp
                json_file.seek(0)
                json.dump(json_dict, json_file, indent=4, sort_keys=True)
                json_file.truncate()
                break
    json_file.close


def restore_hp_party(campaign_id, percentage, is_percetage):
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r+') as json_file:
        json_dict = json.load(json_file)
        for player in json_dict['players']:
            restore_hp(campaign_id, player['id'], percentage, is_percetage)


def create_drop():
    return


def retrieve_monsters(campaign_id):
    with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r') as json_file:
        json_dict = json.load(json_file)
        if "monsters" not in json_dict.keys():
            json_dict["monsters"] = []
        if len(json_dict["monsters"]) == 0:
            result = None
        else:
            result = json_dict['monsters']
    json_file.close()
    return result


def create_monster(already_exist, monster_dict, campaign_id):
    if already_exist:
        return retrieve_monsters(campaign_id)
    else:
        with open(path.join(path.join(cwd, CAMPAIGN_PATH), campaign_id), 'r+') as json_file:
            json_dict = json.load(json_file)
            if "monsters" not in json_dict.keys():
                json_dict["monsters"] = []
            json_dict["monsters"].append(monster_dict)
            json_file.seek(0)
            json.dump(json_dict, json_file, indent=4, sort_keys=True)
            json_file.truncate()
            json_file.close()
        return True
