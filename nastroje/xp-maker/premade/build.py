"""Generate standalone NWN:EE local-vault characters from the published builds."""

from __future__ import annotations

import argparse
from collections import Counter
from functools import cache
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from common import add_observatory_sources

add_observatory_sources()

from aurora import (CHAR, SHORT, GameResources, Record, bite, dword, flt,
                    gff_encode, integer, loc, lst, ref, string, word)
from catalog import ARMOR, GEAR, armor_models, styled_item
from content import prop
from roster import CLASSES, HALFLING, HUMAN, ROSTER
from spellbook import Spellbook


ABILITIES = ("Str", "Dex", "Con", "Int", "Wis", "Cha")
ALIGNMENT = {"L": 85, "C": 15, "N": 50, "G": 85, "E": 15}
SKILLS = {
    "AE": "AnimalEmpathy", "Co": "Concentration", "DT": "DisableTrap",
    "Di": "Discipline", "He": "Heal", "Hi": "Hide", "In": "Intimidate",
    "Li": "Listen", "Lo": "Lore", "MS": "MoveSilently", "OL": "OpenLock",
    "Pe": "Persuade", "Pf": "Perform", "Se": "Search", "ST": "SetTrap",
    "SC": "Spellcraft", "Ta": "Taunt", "Tu": "Tumble", "UM": "UseMagicDevice",
    "Sp": "Spot", "CT": "CraftTrap",
}
CLOTHES, MAIN_HAND, OFF_HAND, ARROWS = 2, 16, 32, 2048


def number(value, default=0):
    return int(value) if value not in (None, "****") else default


def normal_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def modifier(score):
    return (score - 10) // 2


class Rules:
    def __init__(self, game):
        self.game = game
        self.classes = self.table("classes")
        self.feats = self.table("feat")
        self.skills = self.table("skills")
        self.races = self.table("racialtypes")
        self.skill_ids = {data["Label"]: index for index, data in self.skills.items()}
        self.feat_ids = {}
        for index, row in self.feats.items():
            if row["FEAT"] != "****":
                name = self.game.tlk(int(row["FEAT"]))
                self.feat_ids.setdefault(normal_name(name), index)
            self.feat_ids.setdefault(normal_name(row["LABEL"]), index)
        self.great_abilities = {
            self.feat_id(f"Great {ability} {roman}"): index
            for index, ability in enumerate(("Strength", "Dexterity", "Constitution",
                                             "Intelligence", "Wisdom", "Charisma"))
            for roman in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
        }

    @cache
    def table(self, name):
        if name == "****":
            return {}
        lines = self.game.read(name.lower(), "2da").decode("cp1252").splitlines()
        rows = [re.findall(r'"[^"]*"|\S+', line) for line in lines[1:] if line.strip()]
        if rows[0][0] == "DEFAULT:":
            rows.pop(0)
        header, *data = rows
        return {int(row[0]): dict(zip(header, (value.strip('"') for value in row[1:])))
                for row in data if row[0].isdigit()}

    def feat_id(self, name):
        key = normal_name(name)
        try:
            return self.feat_ids[key]
        except KeyError:
            raise ValueError(f"Feat absent from the installed game: {name}") from None

    @cache
    def class_skills(self, class_id):
        return {int(row["SkillIndex"]) for row in self.table(self.classes[class_id]["SkillsTable"]).values()
                if row["ClassSkill"] == "1"}

    @cache
    def automatic_feats(self, class_id, class_level):
        return [int(row["FeatIndex"]) for row in self.table(self.classes[class_id]["FeatsTable"]).values()
                if row["List"] == "3" and number(row["GrantedOnLevel"], -1) == class_level]

    def stat_gains(self, class_id, class_level):
        return self.table(self.classes[class_id]["StatGainTable"]).get(class_level - 1, {})

    def BAB(self, levels):
        return sum(int(self.table(self.classes[class_id]["AttackBonusTable"])[count - 1]["BAB"])
                   for class_id, count in levels.items())


def read_skill_plans(path):
    plans = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("["):
            plan = plans.setdefault(line[1:-1], {})
        else:
            level, *ranks = line.split()
            plan[int(level)] = {rank[:2]: int(rank[2:]) for rank in ranks}
    return plans


def points_per_level(rules, race, class_id, score, level):
    points = max(1, int(rules.classes[class_id]["SkillPointBase"]) + modifier(score))
    return (points + (race == HUMAN)) * (4 if level == 1 else 1)


def validate_prestige(rules, name, race, class_id, classes, feats, ranks):
    prereqs = rules.table(rules.classes[class_id]["PreReqTable"]).values()
    alternatives = {"FEATOR": [], "CLASSOR": [], "RACE": []}
    for row in prereqs:
        kind, amount = row["ReqType"], row["ReqParam1"]
        if kind == "VAR":
            continue
        value = int(amount)
        if kind in alternatives:
            options = {"FEATOR": feats, "CLASSOR": classes, "RACE": {race}}[kind]
            alternatives[kind].append(value in options)
            continue
        if kind == "SKILL":
            met = ranks[value] >= int(row["ReqParam2"])
        elif kind == "FEAT":
            met = value in feats
        elif kind == "BAB":
            met = rules.BAB(classes) >= value
        elif kind == "ARCSPELL":
            met = any(rules.classes[c]["Arcane"] == "1" for c in classes)
        else:
            raise ValueError(f"Unknown prestige requirement: {kind}")
        if not met:
            raise ValueError(f"{name} cannot enter {rules.classes[class_id]['Label']}: {row}")
    if any(options and not any(options) for options in alternatives.values()):
        raise ValueError(f"{name} has no qualifying feat, class, or race for {rules.classes[class_id]['Label']}")


def level_history(rules, build, allocation, spellbook):
    order = build.classes
    if len(order) != 40 or len(set(order)) != 3 or len(build.increases) != 10:
        raise ValueError(f"{build.name} needs three classes and forty levels")
    if set(allocation) - set(range(1, 41)):
        raise ValueError(f"Skill points outside the level history for {build.name}")
    classes = Counter()
    pre_epic_classes = Counter(order[:20])
    ranks = [0] * len(rules.skills)
    seen_class_skills = set()
    scores = list(build.scores)
    feats = {}
    levels = []
    saved = 0
    increases = build.ability_increases
    selected = build.selected_feats
    for level, class_id in enumerate(order, 1):
        if class_id not in classes:
            validate_prestige(rules, build.name, build.race, class_id, classes, feats, ranks)
        classes[class_id] += 1
        class_level = classes[class_id]
        row = rules.classes[class_id]
        class_skills = rules.class_skills(class_id)
        seen_class_skills.update(class_skills)
        class_stats = rules.stat_gains(class_id, class_level)
        for index, ability in enumerate(ABILITIES):
            scores[index] += number(class_stats.get(ability))
        if level in increases:
            scores[increases[level]] += 1

        saved += points_per_level(rules, build.race, class_id, scores[3], level)
        gains = [0] * len(ranks)
        for key, added in allocation.get(level, {}).items():
            skill = rules.skill_ids[SKILLS[key]]
            gains[skill] = added
            ranks[skill] += added
            limit = level + 3 if skill in seen_class_skills else (level + 3) // 2
            if ranks[skill] > limit:
                raise ValueError(f"{build.key} level {level}: {SKILLS[key]} exceeds {limit} ranks")
            saved -= added * (1 if skill in class_skills else 2)
        if saved < 0:
            raise ValueError(f"{build.key} level {level}: skill pool overdrawn by {-saved}")

        acquired = []
        if level == 1:
            acquired.extend(int(row["FeatIndex"])
                            for row in rules.table(rules.races[build.race]["FeatsTable"]).values())
        acquired.extend(rules.automatic_feats(class_id, class_level))
        if class_id == CLASSES["C"] and class_level == 1:
            acquired.extend(int(rules.table("domains")[domain]["GrantedFeat"])
                            for domain in spellbook.domains)
        for name in selected.get(level, []):
            feat = rules.feat_id(name)
            if feat in acquired or feat in feats:
                raise ValueError(f"{build.key} level {level}: {name} is already granted")
            if feat in rules.great_abilities:
                scores[rules.great_abilities[feat]] += 1
            acquired.append(feat)
        novel = [feat for feat in dict.fromkeys(acquired) if feat not in feats]
        feats.update(dict.fromkeys(novel))

        # Red dragon disciple upgrades its hit die as a class feature.
        hit_die = int(row["HitDie"])
        if class_id == CLASSES["RDD"]:
            hit_die = 6 if class_level < 4 else 8 if class_level < 6 else 10
        entry = Record(0, LvlStatClass=bite(class_id), LvlStatHitDie=bite(hit_die),
                       EpicLevel=bite(level > 20), SkillPoints=word(saved),
                       SkillList=skill_list(gains), FeatList=feat_list(novel, ident=0))
        if level in increases:
            entry.fields["LvlStatAbility"] = bite(increases[level])
        spellbook.learn(entry, class_id, class_level)
        levels.append(entry)

    hit_dice = sum(entry.value("LvlStatHitDie") for entry in levels)
    hp = hit_dice + 40 * modifier(scores[2])
    if rules.feat_id("Toughness") in feats:
        hp += 40
    save_values = []
    for save, score_index in (("FortSave", 2), ("RefSave", 1), ("WillSave", 4)):
        base = sum(int(rules.table(rules.classes[class_id]["SavingThrowTable"])[count - 1][save])
                   for class_id, count in pre_epic_classes.items())
        save_values.append((CHAR, base + modifier(scores[score_index]) + 10))
    # The engine adds the racial adjustments when reading a character's base scores.
    race = rules.races[build.race]
    stored_scores = {ability: bite(score - int(race[f"{ability}Adjust"]))
                     for ability, score in zip(ABILITIES, scores)}
    return dict(stored_scores,
                HitPoints=(SHORT, hit_dice), MaxHitPoints=(SHORT, hp),
                CurrentHitPoints=(SHORT, hp), PregameCurrent=(SHORT, hp),
                BaseAttackBonus=bite(rules.BAB(pre_epic_classes) + 10),
                FortSaveThrow=save_values[0], RefSaveThrow=save_values[1], WillSaveThrow=save_values[2],
                ClassList=lst([spellbook.complete_class(class_id, count, scores)
                               for class_id, count in classes.items()]),
                LvlStatList=lst(levels), FeatList=feat_list(feats), SkillPoints=word(saved),
                SkillList=skill_list(ranks))


def skill_list(ranks):
    return lst([Record(0, Rank=bite(rank)) for rank in ranks])


def feat_list(feats, ident=1):
    return lst([Record(ident, Feat=word(feat)) for feat in feats])


class Equipment:
    def __init__(self, rules):
        self.game = rules.game
        self.armor = armor_models(self.game)
        self.base_items = rules.table("baseitems")
        self.models = {base: (name, model) for _, base, _, name, model in GEAR}

    def loadout(self, build):
        equipped, inventory = [], []

        def put(base, *, slot=0, name=None, model=None, properties=(), stack=1):
            if model is None:
                default_name, model = self.models[base]
                name = name or default_name
            sequence = len(equipped) + len(inventory) + 1
            stem = f"zpc_{build.key[:6]}_{sequence}"
            item = styled_item(self.game, stem, name, base, model, properties=properties, stack=stack)
            item.ident = slot
            item.fields.update(ObjectId=dword(2048 + sequence), Dropable=bite(1), Pickpocketable=bite(0),
                               XPosition=flt(0), YPosition=flt(0), ZPosition=flt(0),
                               XOrientation=flt(1), YOrientation=flt(0), ZOrientation=flt(0),
                               Comment=string("Zkusebna dobrodruhu"))
            if slot:
                equipped.append(item)
            else:
                next_column = sum(int(self.base_items[stored.value("BaseItem")]["InvSlotWidth"])
                                  for stored in inventory)
                item.fields.update(Repos_PosX=word(next_column), Repos_Posy=word(0))
                inventory.append(item)

        put(16, slot=CLOTHES, name=f"{ARMOR[build.armor]} +5", model=self.armor[build.armor],
            properties=(prop(1, table=2, value=5),))
        for weapon, slot in ((build.weapon, MAIN_HAND), (build.offhand, OFF_HAND)):
            if weapon is None:
                continue
            name = f"{self.models[weapon][0]} +5"
            if weapon == 8:
                properties = (prop(56, table=2, value=5), prop(45, table=2, value=5))
            elif weapon in (56, 57):
                properties = (prop(1, table=2, value=5),)
            else:
                properties = (prop(6, table=2, value=5),)
            put(weapon, slot=slot, name=name, properties=properties)
        if build.weapon == 8:
            put(20, slot=ARROWS, stack=99)
            put(20, stack=99)
            put(20, stack=99)
        if build.key == "heirophant":
            put(61, name="Prak +5", properties=(prop(56, table=2, value=5),))
            put(27, stack=99)
        put(26, name="Boty trvalého spěchu", properties=(prop(35),))
        put(49, name="Lektvar úplného uzdravení", model="nw_it_mpotion001",
            properties=(prop(15, 139, 3, 1),), stack=5)
        return dict(Equip_ItemList=lst(equipped), ItemList=lst(inventory))


def character(rules, build, allocation, equipment):
    spellbook = Spellbook(rules, build)
    fields = level_history(rules, build, allocation, spellbook)
    for name in ("Neck", "Torso", "Belt", "Pelvis", "LShoul", "LBicep", "LFArm", "LHand",
                 "LThigh", "LShin", "LFoot", "RShoul", "RBicep", "RFArm", "RHand",
                 "RThigh", "RShin", "RFoot"):
        fields[f"BodyPart_{name}"] = bite(1)
    fields.update(FirstName=loc(build.name), LastName=loc(""), IsPC=bite(1), IsDM=bite(0),
                  Description=loc("Komunitní build na 40. úrovni pro Zkušebnu dobrodruhů."),
                  Tag=string(""), Conversation=ref(""), TemplateResRef=ref(""),
                  Gender=bite(build.gender), Race=bite(build.race), Subrace=string(""), Age=integer(35),
                  StartingPackage=bite(int(rules.classes[build.classes[0]]["Package"])),
                  Deity=string("Torm" if build.key == "quest" else ""),
                  GoodEvil=bite(ALIGNMENT[build.alignment[1]]),
                  LawfulChaotic=bite(ALIGNMENT[build.alignment[0]]),
                  Gold=dword(1000), Experience=dword(780000), OverrideBAB=bite(0),
                  ArmorClass=(SHORT, 10), NaturalAC=bite(0), fortbonus=(SHORT, 0),
                  refbonus=(SHORT, 0), willbonus=(SHORT, 0),
                  Appearance_Type=word(int(rules.races[build.race]["Appearance"])),
                  Appearance_Head=bite(build.head), Phenotype=integer(0),
                  Portrait=ref(f"po_{build.portrait}"),
                  Color_Skin=bite(2), Color_Hair=bite(4 + build.head),
                  Color_Tattoo1=bite(0), Color_Tattoo2=bite(0), Wings=bite(0), Tail=bite(0),
                  CreatureSize=integer(2 if build.race == HALFLING else 3),
                  SoundSetFile=word(219 if build.gender else 218), MovementRate=bite(0),
                  FactionID=word(0), ChallengeRating=flt(40), Plot=bite(0), IsImmortal=bite(0),
                  IsDestroyable=bite(1), IsRaiseable=bite(1), IsCommandable=bite(1),
                  Disarmable=bite(1), Interruptable=bite(1), CorpseDecayTime=dword(5000), QBList=lst([]))
    if build.key in ("howitzer", "exalted", "bulwark"):
        familiar = {"howitzer": (7, "Havran"), "exalted": (10, "Argos"), "bulwark": (0, "Netopyr")}
        kind, name = familiar[build.key]
        fields.update(FamiliarType=integer(kind), FamiliarName=string(name))
    if build.key in ("outcast", "heirophant"):
        kind, name = (1, "Vichr") if build.key == "outcast" else (2, "Bourka")
        fields.update(CompanionType=integer(kind), CompanionName=string(name))
    fields.update(equipment.loadout(build))
    return Record(**fields)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, type=Path, help="NWN:EE game directory containing data/")
    parser.add_argument("--output", required=True, type=Path, help="Destination for the ten .bic files")
    args = parser.parse_args()
    game = GameResources(args.game.resolve())
    rules = Rules(game)
    plans = read_skill_plans(HERE / "skills.txt")
    equipment = Equipment(rules)
    records = {f"zks_{build.key}.bic": character(rules, build, plans[build.key], equipment)
               for build in ROSTER}
    args.output.mkdir(parents=True, exist_ok=True)
    for file, record in records.items():
        (args.output / file).write_bytes(gff_encode("BIC", record))
        print(f"{file}  {record.value('FirstName')[1][0]}")


if __name__ == "__main__":
    main()
