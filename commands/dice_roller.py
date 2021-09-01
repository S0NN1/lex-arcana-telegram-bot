import random
import os
import json

cwd = os.getcwd()
directory = os.path.abspath(os.path.join(cwd, 'data'))


def update_dice(dice_number, id, campaign_id):
    dice = 'd' + str(dice_number)
    with open(directory + '/users.json', 'r+') as json_file:
        json_dict = json.load(json_file)
        for user in json_dict["users"]:
            if user["id"] == id:
                for campaign in user["campaigns"]:
                    if campaign["id"] == campaign_id:
                        campaign["dices"][dice] = campaign["dices"][dice] + 1
                        json_file.seek(0)
                        json.dump(json_dict, json_file, indent=4, sort_keys=True)
                        json_file.truncate()
                        json_file.close()
                        return
    json_file.close()


def most_used_dice(id, campaign_id):
    dices = {}
    with open(directory + '/users.json', 'r') as json_file:
        json_dict = json.load(json_file)
        for user in json_dict["users"]:
            if user["id"] == id:
                for campaign in user["campaigns"]:
                    if campaign["id"] == campaign_id:
                        dices = campaign["dices"]
                        break

    sorted_values = sorted(dices.values(), reverse=True)
    sorted_dices = {}
    for i in sorted_values:
        for k in dices.keys():
            if dices[k] == i and k not in sorted_dices:
                sorted_dices[k] = dices[k]
                break
    json_file.close()
    return sorted_dices


def roll_dice(dice_number, id, campaign_id, modifier=0, multiplier=False):
    value = random.randint(1, dice_number) * modifier if multiplier else random.randint(1, dice_number) + modifier
    update_dice(dice_number, id, campaign_id)
    return value
