"""Spell choices and prepared slots for the casting characters."""

import re

from aurora import SHORT, Record, bite, integer, lst, word
from roster import CLASSES


# Spells are assigned to the matching stock class and spell level by spells.2da.
PRIORITIES = {
    "B": """
        Cure_Minor_Wounds Light Resistance Flare Daze
        Mage_Armor Cure_Light_Wounds Grease Tashas_Hideous_Laughter Expeditious_Retreat
        Bulls_Strength Cats_Grace Ghostly_Visage Silence Sound_Burst
        Haste Displacement Greater_Magic_Weapon Clarity Slow
        Improved_Invisibility War_Cry Neutralize_Poison Cure_Critical_Wounds Hold_Monster
        Greater_Dispelling Mind_Fog Mass_Cure_Light_Wounds Ethereal_Visage Summon_Creature_V
        Dirge Mass_Haste Ice_Storm Energy_Buffer
    """,
    "C": """
        Cure_Minor_Wounds Resistance Light Guidance
        Divine_Favor Bless Shield_of_Faith Protection_from_Alignment
        Aid Lesser_Restoration Silence Resist_Elements
        Greater_Magic_Weapon Magic_Vestment Prayer Negative_Energy_Protection
        Divine_Power Death_Ward Freedom_of_Movement Restoration
        Spell_Resistance Battletide True_Seeing Slay_Living
        Heal Blade_Barrier Greater_Dispelling Greater_Sanctuary
        Regenerate Resurrection Greater_Restoration
        Aura_versus_Alignment Fire_Storm Earthquake
        Mass_Heal Implosion Gate
    """,
    "D": """
        Cure_Minor_Wounds Light Resistance Guidance
        Grease Entangle Camouflage Cure_Light_Wounds
        Barkskin Blood_Frenzy Owls_Wisdom Resist_Elements
        Greater_Magic_Fang Spike_Growth Poison Protection_from_Elements
        Ice_Storm Freedom_of_Movement Stoneskin Flame_Strike
        Owls_Insight Stonehold Spell_Resistance Death_Ward
        Heal Greater_Dispelling Energy_Buffer Drown
        Creeping_Doom True_Seeing Harm Fire_Storm
        Sunburst Premonition Finger_of_Death
        Storm_of_Vengeance Elemental_Swarm Shapechange
    """,
    "P": """
        Divine_Favor Bless Deafening_Clang Protection_from_Alignment
        Aura_of_Glory Eagle_Splendor Bulls_Strength Resist_Elements
        Greater_Magic_Weapon Magic_Vestment Prayer Remove_Blindness_and_Deafness
        Holy_Sword Death_Ward Restoration
    """,
    "Ra": """
        Blade_Thirst Entangle Camouflage Resist_Elements
        Cats_Grace Owls_Wisdom Aid Barkskin
        Greater_Magic_Fang Greater_Magic_Weapon Cure_Moderate_Wounds
        Freedom_of_Movement Summon_Creature_IV Cure_Serious_Wounds
    """,
    "S": """
        Light Ray_of_Frost Acid_Splash Resistance Daze Flare Disrupt_Undead
        Shield Mage_Armor Grease Protection_from_Alignment Magic_Missile
        Death_Armor Ghostly_Visage See_Invisibility Ultravision Eagle_Splendor
        Haste Displacement Negative_Energy_Burst Flame_Arrow Greater_Magic_Weapon
        Isaacs_Lesser_Missile_Storm Ice_Storm Improved_Invisibility Stoneskin Evards_Black_Tentacles
        Mestils_Acid_Sheath Lesser_Spell_Mantle Feeblemind Bigbys_Interposing_Hand
        Isaacs_Greater_Missile_Storm Bigbys_Forceful_Hand Greater_Dispelling True_Seeing
        Finger_of_Death Spell_Mantle Bigbys_Grasping_Hand
        Wail_of_the_Banshee Mordenkainens_Disjunction Time_Stop
        Horrid_Wilting Premonition Mass_Blindness_and_Deafness
    """,
    "W": """
        Ray_of_Frost Light Resistance True_Strike Shield Mage_Armor Protection_from_Alignment
    """,
}


def normalized(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


class Spellbook:
    def __init__(self, rules, build):
        self.rules = rules
        self.domains = (14, 19) if build.key == "shadow" else ()
        self.known = {}
        self.choices = {}
        for token, text in PRIORITIES.items():
            class_id = CLASSES[token]
            if class_id not in build.classes:
                continue
            class_column = rules.classes[class_id]["SpellTableColumn"]
            order = {normalized(name): index for index, name in enumerate(text.split())}
            for level in range(10):
                candidates = [(order.get(normalized(row["Label"]), len(order)), spell)
                              for spell, row in rules.table("spells").items()
                              if row.get(class_column) == str(level)]
                self.choices[class_id, level] = [spell for _, spell in sorted(candidates)]

    def learn(self, entry, class_id, class_level):
        row = self.rules.classes[class_id]
        spell_known = self.rules.table(row["SpellKnownTable"])
        if not spell_known and class_id != CLASSES["W"]:
            return
        for level in range(10):
            options = self.choices[class_id, level]
            if class_id == CLASSES["W"]:
                count = len(options) if level == 0 else 4 if level == 1 else 0
            else:
                raw = spell_known[class_level - 1].get(f"SpellLevel{level}", "****")
                count = int(raw) if raw != "****" else 0
            known = self.known.setdefault((class_id, level), [])
            new = options[len(known):count]
            if len(known) + len(new) != count:
                raise ValueError(f"Missing spell options for class {class_id}, spell level {level}")
            if new:
                known.extend(new)
                entry.fields[f"KnownList{level}"] = lst([Record(0, Spell=word(spell)) for spell in new])

    def complete_class(self, class_id, class_level, scores):
        result = Record(2, Class=integer(class_id), ClassLevel=(SHORT, class_level))
        row = self.rules.classes[class_id]
        known = {level: self.known.get((class_id, level), []) for level in range(10)}
        for level, spell_list in known.items():
            if spell_list:
                result.fields[f"KnownList{level}"] = lst([Record(3, Spell=word(spell)) for spell in spell_list])
        if row["PickDomains"] == "1":
            result.fields.update(Domain1=bite(self.domains[0]), Domain2=bite(self.domains[1]))
        if row["PickSchool"] == "1":
            result.fields["School"] = bite(0)
        gain_table = self.rules.table(row["SpellGainTable"])
        if not gain_table:
            return result
        score = scores["STR DEX CON INT WIS CHA".split().index(row["SpellcastingAbil"])]
        mod = (score - 10) // 2
        daily = []
        for level in range(10):
            raw = gain_table[class_level - 1].get(f"SpellLevel{level}", "****")
            count = 0
            if raw != "****" and score >= 10 + level:
                count = int(raw) + (max(0, 1 + (mod - level) // 4) if level else 0)
            daily.append(count)
            if not count or row["MemorizesSpells"] != "1":
                continue
            options = known[level] if row["SpellbookRestricted"] == "1" else self.choices[class_id, level]
            # Prepare at most three different spells per level, with repeats for combat buffs.
            ready = [Record(3, Spell=word(options[index % min(3, len(options))]),
                            Ready=bite(1), SpellMetaMagic=bite(0)) for index in range(count)]
            if row["PickDomains"] == "1" and level:
                domains = self.rules.table("domains")
                domain_spells = [domains[domain][f"Level_{level}"] for domain in self.domains]
                allowed = [int(spell) for spell in domain_spells if spell != "****"]
                if allowed:
                    ready[-1] = Record(3, Spell=word(allowed[-1]), Ready=bite(1),
                                       DomainSpell=bite(1), SpellMetaMagic=bite(0))
            result.fields[f"MemorizedList{level}"] = lst(ready)
        if row["MemorizesSpells"] == "0":
            result.fields["SpellsPerDayList"] = lst([Record(17767, NumSpellsLeft=bite(count)) for count in daily])
        return result
