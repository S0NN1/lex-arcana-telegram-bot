from random import choice, randint
import json
from . import utils


def d_(f):
    def dice(n=1):
        return sum([randint(1, f) for i in range(n)])
    return dice


d_4 = d_(4)


d_6 = d_(6)


custos_language = ''
data = utils.json_to_dict("data", "names")
virtutes = utils.json_to_dict("virtutes", "specs")
virtutes_by_class = utils.json_to_dict("virtutesByClass", "specs")
peritiae = utils.json_to_dict("peritiae", "specs")
peritia_by_class = utils.json_to_dict("peritiaByClass", "specs")
multipliers = utils.json_to_dict("multipliers", "specs")
spec_by_house = utils.json_to_dict("specByHouse", "specs")
spec_by_origin = utils.json_to_dict("specByOrigin", "specs")
pietas = utils.json_to_dict("pietas", "specs")
hp = utils.json_to_dict("hp", "specs")
specs = utils.json_to_dict("specs", "specs")
bio = utils.json_to_dict("bio", "specs")
aetates = utils.json_to_dict("aetates", "specs")
grades = utils.json_to_dict("grades", "specs")
locative = utils.json_to_dict("locative", "names")
praenomina = utils.json_to_dict("praenomina", "names")
nomina = utils.json_to_dict("nomina", "names")
cognomina = utils.json_to_dict("cognomina", "names")
extra_nomen_male = utils.json_to_dict("extraNomenMale", "names")
extra_nomen_female = utils.json_to_dict("extraNomenFemale", "names")
the_format = utils.json_to_dict("theFormat", "names")
province_to_language = utils.json_to_dict("provinceToLanguage", "names")
melee_weapons = utils.json_to_dict("meleeWeapons", "equipment")
ranged_weapons = utils.json_to_dict("rangedWeapons", "equipment")
armors = utils.json_to_dict("armors", "equipment")
shields = utils.json_to_dict("shields", "equipment")
house = utils.json_to_dict("house", "geography")
provinces = utils.json_to_dict("province", "geography")
languages = utils.json_to_dict("languages", "geography")
settlements = utils.json_to_dict("settlements", "geography")
origins = utils.json_to_dict("origins", "geography")


def gen_vicus(input_province):
    region = None
    if input_province in ['Italia', 'Illyricum', 'Iberia', 'Numidia', 'Raetia', 'Mauretania']:
        region = 'Latin'
    elif input_province in ['Gallia', 'Germania', 'Britannia']:
        region = choice(['Celtic', 'Celtic', 'Latin'])
    elif input_province in ['Macedonia', 'Thracia', 'Achaia', 'Asia', 'Aegyptus']:
        region = 'Greek'
    elif input_province in ['Dacia', 'Syria', 'Armenia', 'Mesopotamia', 'Arabia']:
        region = choice(['Greek', 'Latin'])
    else:
        region = 'Latin'
    base = choice(list(data['names'][region].keys()))
    gender = data['names'][region][base]['gender']
    number = data['names'][region][base]['number']
    if input_province in data['modifiers']['regionalImmutables']:
        modifier_type = choice(['immutables', 'regionalImmutables', 'adjectives'])
    else:
        modifier_type = choice(['immutables', 'adjectives'])
    mod = choice(data['modifiers'][modifier_type]) if modifier_type != 'regionalImmutables' else choice(data['modifiers'][modifier_type][input_province])
    if region == 'Greek' and modifier_type not in ['regionali_mutabili', 'regionalImmutables']:
        modifier_type = 'greekImmutables'
        mod = choice(data['modifiers'][modifier_type])
    if modifier_type == 'adjectives':
        mod += data['declination'][gender][number]
    return base + ' ' + mod


def gen_castrum(input_province):
    region = None
    if input_province in ['Italia', 'Illyricum', 'Iberia', 'Numidia', 'Raetia', 'Mauretania']:
        region = 'Latin'
    elif input_province in ['Gallia', 'Germania', 'Britannia']:
        region = choice(['Celtic', 'Celtic', 'Latin'])
    elif input_province in ['Macedonia', 'Thracia', 'Achaia', 'Asia', 'Aegyptus']:
        region = 'Greek'
    elif input_province in ['Dacia', 'Syria', 'Armenia', 'Mesopotamia', 'Arabia']:
        region = choice(['Greek', 'Latin'])
    else:
        region = 'Latin'
    base = choice(list(data['castra'][region].keys()))
    gender = data['castra'][region][base]['gender']
    number = data['castra'][region][base]['number']
    if input_province in data['modifiers']['regionalImmutables']:
        modifier_type = choice(['immutables', 'regionalImmutables', 'adjectives'])
    else:
        modifier_type = choice(['immutables', 'adjectives'])
    mod = choice(data['modifiers'][modifier_type]) if modifier_type != 'regionalImmutables' else choice(data['modifiers'][modifier_type][input_province])
    if region == 'Greek' and modifier_type not in ['regionali_mutabili', 'regionalImmutables']:
        modifier_type = 'greekImmutables'
    mod = choice(data['modifiers'][modifier_type])
    if modifier_type == 'adjectives':
        mod += data['declination'][gender][number]
    return base + ' ' + mod


def patronymic_particle(origin, gender):
    if origin == 'Britannia':
        if gender == 'female':
            return 'nic '
        else:
            return choice(['mab ', 'ap '])
    elif origin in ['Syria', 'Arabia', 'Mesopotamia']:
        if gender == 'female':
            return 'Bat-'
    else:
        return 'Bar-'


def get_praenomen(gender, origin, family):
    return choice(praenomina[gender][origin])


def get_nomen(gender, origin, family):
    if d_4() <= 2:
        if gender == 'male':
            return choice(extra_nomen_male[origin])
        else:
            return choice(extra_nomen_female[origin])
    return choice(nomina[gender]['latin'])


def get_cognomen(gender, origin, family):
    return choice(cognomina[gender][origin])


def get_name(gender, origin, family):
    fmt = choice(the_format[gender][origin])
    r = ''
    for c in fmt:
        if c == 'p':
            r += get_praenomen(gender, 'latin', family) + ' '
        elif c == 'n':
            r += get_nomen(gender, origin, family) + ' '
        elif c == 'c':
            r += get_cognomen(gender, province_to_language[origin], family) + ' '
        elif c == 'm':
            r += patronymic_particle(origin, gender)
            gender = 'male'
    if len(fmt) < 2:
        r += choice(locative[gender][origin])
    return r


class Custos(object):
    def excellent_class(self):
        q = sorted({q1: sum([self.virtutes[i] for i in virtutes_by_class[q1]]) for q1 in virtutes_by_class}.items(), key=lambda item: item[1], reverse=True)[0]
        return q[0]

    def decent_class(self):
        for p in peritiae:
            if self.peritiae[p] < 3 or self.peritiae[p] > 18:
                raise Exception('Illegal peritia: {} {}'.format(p, self.peritiae[p]))
        if self.peritiae[peritia_by_class[self.own_class]] > 15:
            return self.own_class
        p = sorted(self.peritiae.items(), key=lambda item: item[1], reverse=True)[0]
        if p[1] < 15:
            raise Exception('Peritiae too low: {}'.format(p))
        for q in peritia_by_class:
            if p[0] == peritia_by_class[q]:
                return q
        raise Exception('Highest peritia: {}'.format(p))

    def __init__(self, gender=None, own_class=None, origin=None):
        while 1:
            self.virtutes = {v: d_6(2) for v in virtutes}
            self.own_class = self.excellent_class()
            self.input_province = choice(list(provinces.keys()))
            self.peritiae = provinces[self.input_province]
            vp = {k: self.virtutes[k] for k in self.virtutes}
            for p in peritiae:
                x, y = tuple(peritiae[p])
                vx = randint(1, vp[x]) if vp[x] > 0 else -vp[x]
                vy = randint(1, vp[y]) if vp[y] > 0 else -vp[y]
                vp[x] = - (vp[x] - vx) if vp[x] > 0 else 0
                vp[y] = - (vp[y] - vy) if vp[y] > 0 else 0
                self.peritiae[p] += vx + vy
            self.aetas = randint(16, 60)
            try:
                self.own_class = self.decent_class()
                break
            except Exception:
                pass
        aetas = 'young' if self.aetas <= 30 else ('adult' if self.aetas <= 45 else 'mature')
        mod = aetates[aetas]
        for v in self.virtutes:
            self.virtutes[v] += mod[v]
        self.hp = self.virtutes['Vigor'] + self.virtutes['Coordinatio'] + hp[self.own_class]
        self.pietas = self.virtutes['Sensibilitas'] + self.virtutes['Ratio'] + pietas[self.own_class]
        self.multipliers = {k: 2 for k in multipliers}
        self.multipliers[peritia_by_class[self.own_class]] += 4
        for i in range(4):
            self.multipliers[choice(multipliers)] += 1
        self.origin = choice(origins[self.input_province])
        self.house = choice(house[self.origin])
        self.specs = {}
        self.specs[choice(spec_by_origin[self.origin])] = 1
        x = choice(spec_by_origin[self.origin])
        while x in self.specs:
            x = choice(spec_by_origin[self.origin])
        self.specs[x] = 1
        x = choice(spec_by_house[self.origin][self.house])
        while x in self.specs:
            x = choice(spec_by_house[self.origin][self.house])
        self.specs[x] = 2
        t = specs['spec' + peritia_by_class[self.own_class]]
        x = choice(t)
        while x in self.specs:
            x = choice(t)
        self.specs[x] = 1
        x = choice(t)
        while x in self.specs:
            x = choice(t)
        self.specs[x] = 1
        self.specs = [{'id': s, 'val': self.specs[s]} for s in self.specs]
        self.city = ''
        if self.origin in ['Cihps', '2']:
            self.city = choice(settlements[self.input_province][self.origin])
        elif self.origin in ['5', '3']:
            self.city = gen_vicus(self.input_province)
        else:
            self.city = gen_castrum(self.input_province)
        self.gender = choice(['male', 'female']) if not gender else gender
        self.name = get_name(self.gender, self.input_province, self.house)
        self.languages = languages[self.input_province]['fixed']
        self.languages.append(choice(languages[self.input_province]['choice']))
        self.grade = "Gregarius"
        self.weight = 0
        weight_max = self.hp / 2
        base_damage = self.peritiae['DeBello'] / 2
        if base_damage < 3:
            base_damage = 3
        if self.own_class == '4':
            base_damage = 6
        if self.own_class == '1':
            base_damage = 4
        sel_melee_weapons = [a for a in melee_weapons if melee_weapons[a]['difficulty'] <= base_damage]
        primary_melee_weapon = max(sel_melee_weapons, key=lambda x: melee_weapons[x]['difficulty'])
        self.weight += melee_weapons[primary_melee_weapon]['weight']
        sel_throwing_weapons = [a for a in ranged_weapons if ranged_weapons[a]['difficulty'] <= base_damage]
        throwing_weapon = max(sel_throwing_weapons, key=lambda x: ranged_weapons[x]['difficulty'])
        self.weight += ranged_weapons[throwing_weapon]['weight']
        weight_max -= self.weight
        shield = None
        armor = None
        secondary_melee_weapon = None
        weapon_translated_dict = utils.get_translation_list('weapons.' + primary_melee_weapon, custos_language, None)
        if "1" not in weapon_translated_dict['traits']:
            if weight_max > 18:
                shield = 'Scutum'
            elif weight_max > 12:
                shield = 'Clipeus'
            elif weight_max >= 2:
                shield = 'Parma'
        if shield:
            self.weight += shields[shield]['weight']
            weight_max -= shields[shield]['weight']
        if weight_max >= 3:
            armor = max([a for a in armors if armors[a]['weight'] <= weight_max], key=lambda x: armors[x]['protection'])
        if armor:
            self.weight += armors[armor]['weight']
            weight_max -= armors[armor]['weight']
        if weight_max >= 3:
            sel_melee_weapons = [a for a in melee_weapons if melee_weapons[a]['difficulty'] <= min(base_damage, weight_max)]
            secondary_melee_weapon = max(sel_melee_weapons, key=lambda x: melee_weapons[x]['difficulty'])
            self.weight += melee_weapons[secondary_melee_weapon]['weight']
        self.equipment = {}
        if shield:
            self.equipment['shield'] = shield
        if armor:
            self.equipment['armor'] = armor
        self.equipment['melee_weapons'] = [primary_melee_weapon]
        self.equipment['ranged_weapons'] = [throwing_weapon]
        if secondary_melee_weapon:
            self.equipment['melee_weapons'].append(secondary_melee_weapon)
        self.equip = ['sagum', 'caligae', '1', '9', '8', '11', '2', '10', '6', 'stilus', '12', '13', '14']
        if self.own_class == '2':
            self.equip += ['speculum', 'lituus']
        elif self.own_class == '5':
            self.equip += ['dolabra', 'abacus']
        else:
            self.equip.append(choice(['7', '5', '4', '14']))
        self.bio = bio[self.origin][self.house]
        self.indigitamenta = self.own_class
        self.combat_skills = self.own_class
        self.max_hp = self.hp
        self.max_pietas = self.pietas
        for spec in self.specs:
            spec['peritiae'] = spec['id'][:(len(spec['id']) - 1)]

    def json(self):
        return json.dumps(self.__dict__)


def make_char():
    return Custos().json()


def generate_character(language):
    global custos_language
    custos_language = language
    custos = json.loads(make_char())
    return custos
