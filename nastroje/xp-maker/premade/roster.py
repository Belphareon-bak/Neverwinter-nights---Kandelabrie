"""Level histories for the ten community builds selected for Zkušebna."""

from dataclasses import dataclass


CLASSES = {
    "B": 1, "C": 2, "D": 3, "F": 4, "M": 5, "P": 6, "Ra": 7, "R": 8,
    "S": 9, "W": 10, "SD": 27, "AA": 29, "A": 30, "BG": 31, "CoT": 32,
    "WM": 33, "DD": 36, "RDD": 37,
}
DWARF, ELF, HALFLING, HUMAN = 0, 1, 3, 6


@dataclass(frozen=True)
class Build:
    key: str
    name: str
    race: int
    gender: int
    head: int
    portrait: str
    alignment: str
    scores: tuple[int, ...]
    increases: str
    levels: str
    choices: str
    weapon: int
    armor: int
    offhand: int | None = None

    @property
    def classes(self):
        order = []
        for entry in self.levels.split():
            token, _, count = entry.partition("*")
            order.extend([CLASSES[token]] * int(count or 1))
        return order

    @property
    def ability_increases(self):
        return {level * 4: "SDCIWH".index(code)
                for level, code in enumerate(self.increases, 1)}

    @property
    def selected_feats(self):
        return {int(level): [feat.strip() for feat in feats.split(",")]
                for level, feats in (line.strip().split(" ", 1)
                                     for line in self.choices.strip().splitlines())}


ROSTER = (
    Build("shadow", "The Shadow Priest", HUMAN, 0, 7, "hu_m_17_", "LN",
          (8, 16, 12, 14, 16, 8), "WWDDDDDDDD",
          """
          M C C C C C M C C C
          C M C C C C M C C C
          M M SD C C C M C C C
          C M C M SD SD SD C SD C
          """,
          """
          1 Dodge, Blind Fight
          3 Weapon Finesse
          6 Extend Spell
          9 Called Shot
          12 Weapon Focus: Kama
          15 Improved Critical: Kama
          18 Mobility
          21 Epic Weapon Focus: Kama
          24 Great Wisdom I
          27 Great Dexterity I
          30 Great Dexterity II
          31 Armor Skin
          33 Great Dexterity III
          36 Great Dexterity IV
          39 Epic Dodge
          40 Great Wisdom II
          """, 40, 0),
    Build("slayer", "Dwarven Slayer", DWARF, 0, 10, "dw_m_05_", "LN",
          (17, 13, 16, 14, 8, 6), "SSSSSSSSSS",
          """
          F R F F F F R F DD DD
          DD DD DD DD DD DD DD DD R F
          F F F DD DD DD DD DD DD DD
          DD DD DD DD DD DD R DD DD DD
          """,
          """
          1 Power Attack, Cleave
          3 Weapon Focus: Greataxe, Dodge
          5 Weapon Specialization: Greataxe
          6 Toughness
          8 Blind Fight
          9 Knockdown
          12 Improved Critical: Greataxe
          15 Improved Knockdown
          18 Great Cleave
          21 Epic Weapon Focus: Greataxe, Great Strength I
          23 Epic Weapon Specialization: Greataxe
          24 Great Strength II
          27 Overwhelming Critical: Greataxe, Great Strength III
          30 Great Strength IV
          31 Devastating Critical: Greataxe
          33 Great Strength V
          35 Armor Skin
          36 Great Strength VI
          39 Great Strength VII
          40 Epic Prowess
          """, 18, 8),
    Build("master", "The Master", ELF, 1, 6, "el_f_19_", "CG",
          (16, 14, 12, 16, 8, 8), "SSSSSSSSSS",
          """
          R F R F R F F R F WM
          WM WM WM WM WM WM WM WM WM F
          WM R WM WM WM WM WM WM R F
          WM WM WM WM WM WM WM WM R F
          """,
          """
          1 Expertise
          2 Weapon Focus: Greatsword
          3 Dodge
          4 Mobility
          6 Spring Attack
          7 Weapon Specialization: Greatsword
          9 Whirlwind Attack
          10 Weapon of Choice: Greatsword
          12 Knockdown
          15 Improved Critical: Greatsword
          18 Blind Fight
          20 Power Attack
          21 Cleave
          24 Great Cleave, Epic Weapon Focus: Greatsword
          27 Great Strength I, Armor Skin
          30 Epic Weapon Specialization: Greatsword
          32 Overwhelming Critical: Greatsword
          33 Great Strength II
          35 Devastating Critical: Greatsword
          36 Great Strength III
          38 Epic Prowess
          39 Great Strength IV
          40 Improved Knockdown
          """, 13, 5),
    Build("outcast", "Dwarven Outcast", DWARF, 1, 4, "dw_f_02_", "NN",
          (15, 14, 14, 14, 14, 6), "SSSSSSSSSS",
          """
          Ra Ra Ra Ra Ra Ra F F F F
          Ra Ra Ra Ra Ra Ra Ra Ra Ra Ra
          Ra SD Ra Ra Ra Ra Ra Ra F F
          F F F F F F SD Ra Ra Ra
          """,
          """
          1 Weapon Focus: Handaxe, Favored Enemy: Undead
          3 Expertise
          5 Favored Enemy: Giants
          6 Knockdown
          7 Blind Fight
          8 Improved Knockdown
          9 Improved Critical: Handaxe
          10 Weapon Specialization: Handaxe
          12 Dodge
          14 Favored Enemy: Dragons
          15 Mobility
          18 Toughness
          19 Favored Enemy: Elementals
          21 Great Strength I
          24 Great Strength II
          25 Favored Enemy: Constructs
          27 Great Strength III
          28 Bane of Enemies
          30 Great Strength IV, Epic Weapon Focus: Handaxe
          32 Epic Weapon Specialization: Handaxe
          33 Great Strength V
          34 Epic Prowess
          36 Great Strength VI, Armor Skin
          39 Great Strength VII, Favored Enemy: Orcs
          40 Favored Enemy: Goblinoids
          """, 38, 2, 38),
    Build("howitzer", "The Divine Howitzer", ELF, 0, 5, "el_m_09_", "LG",
          (13, 18, 10, 11, 8, 15), "HHHHHHHHHH",
          """
          W P P P P P P AA P AA
          AA P AA AA AA AA AA AA AA P
          AA*19 P
          """,
          """
          1 Point Blank Shot
          3 Weapon Focus: Longbow
          6 Power Attack
          9 Divine Might
          12 Divine Shield
          15 Improved Critical: Longbow
          18 Rapid Shot
          21 Great Charisma I
          24 Epic Weapon Focus: Longbow, Great Charisma II
          27 Great Charisma III
          28 Epic Prowess
          30 Great Charisma IV
          32 Great Dexterity I
          33 Great Charisma V
          36 Great Charisma VI, Great Dexterity II
          39 Great Charisma VII
          """, 8, 5),
    Build("exalted", "Exalted Sorceress", HUMAN, 1, 3, "hu_f_11_", "LG",
          (14, 10, 14, 14, 8, 16), "HHHHHHHHHH",
          "S*19 P S*18 M S",
          """
          1 Expertise, Improved Expertise
          3 Extend Spell
          6 Empower Spell
          9 Spell Focus: Necromancy
          12 Greater Spell Focus: Necromancy
          15 Maximize Spell
          18 Still Spell
          21 Epic Skill Focus: Discipline
          24 Automatic Still Spell I, Automatic Still Spell II
          27 Automatic Still Spell III, Epic Spell Focus: Necromancy
          30 Epic Spell: Epic Mage Armor, Great Charisma I
          33 Epic Spell: Epic Warding, Great Charisma II
          36 Combat Casting, Great Charisma III
          39 Improved Combat Casting
          40 Great Charisma IV
          """, 22, 8, 56),
    Build("heirophant", "Heirophant of the Cabal", HUMAN, 0, 16, "hu_m_12_", "LN",
          (10, 10, 12, 14, 18, 8), "WWWWWWWWWW",
          "D*19 CoT D*8 CoT D*7 M D*3",
          """
          1 Spell Focus: Conjuration, Extend Spell
          3 Greater Spell Focus: Conjuration
          6 Zen Archery
          9 Empower Spell
          12 Spell Penetration
          15 Greater Spell Penetration
          18 Weapon Focus: Scimitar
          21 Great Wisdom I
          24 Great Wisdom II
          25 Great Wisdom III
          27 Great Wisdom IV
          29 Great Wisdom V
          30 Dragon Shape, Epic Spell Focus: Conjuration
          33 Great Wisdom VI
          34 Great Wisdom VII
          36 Great Wisdom VIII
          39 Great Wisdom IX, Great Wisdom X
          """, 53, 0),
    Build("bulwark", "The Bulwark of Tharizdun", HUMAN, 0, 18, "hu_m_22_", "NE",
          (16, 8, 14, 14, 8, 15), "HSSHHHHHHH",
          """
          B B B B B B RDD RDD RDD RDD
          BG BG B RDD BG RDD B BG RDD RDD
          RDD RDD B*18
          """,
          """
          1 Power Attack, Cleave
          3 Blind Fight
          6 Curse Song
          9 Knockdown
          12 Weapon Focus: Scimitar
          15 Divine Might
          18 Divine Shield
          21 Epic Weapon Focus: Scimitar
          24 Craft Wand
          27 Still Spell
          30 Epic Prowess
          33 Epic Skill Focus: Perform
          36 Lasting Inspiration
          37 Great Charisma I
          39 Great Charisma II
          40 Great Charisma III
          """, 53, 8, 57),
    Build("tiny", "Tiny Reaper", HALFLING, 0, 3, "ha_m_03_", "NE",
          (12, 18, 15, 14, 8, 8), "DDDDDDCDDD",
          "R*5 A*8 R*7 SD A*5 R A*13",
          """
          1 Ambidexterity
          3 Weapon Finesse
          6 Two-Weapon Fighting
          9 Weapon Focus: Dagger
          12 Dodge
          15 Improved Two-Weapon Fighting
          18 Mobility, Improved Evasion
          21 Epic Weapon Focus: Dagger
          24 Great Dexterity I
          27 Epic Dodge, Defensive Roll
          28 Great Dexterity II
          30 Epic Prowess
          32 Great Dexterity III
          33 Armor Skin
          36 Great Dexterity IV, Great Dexterity V
          39 Great Dexterity VI
          40 Great Dexterity VII
          """, 22, 0, 22),
    Build("quest", "Knight of the Quest", HUMAN, 1, 6, "hu_f_06_", "LG",
          (14, 8, 14, 10, 14, 16), "HHHHHHHSSS",
          """
          P P P P P P P CoT CoT P
          P R P P P P R P P CoT
          CoT CoT CoT P P CoT R CoT CoT CoT
          P P P P P P R P P P
          """,
          """
          1 Power Attack, Weapon Focus: Longsword
          3 Divine Might
          6 Divine Shield
          9 Blind Fight, Improved Critical: Longsword
          12 Toughness
          15 Extra Turning
          18 Extra Smiting
          21 Epic Weapon Focus: Longsword, Great Charisma I
          23 Epic Prowess
          24 Great Charisma II
          27 Great Charisma III
          28 Great Smiting I
          30 Armor Skin, Great Strength I
          33 Great Smiting II
          36 Great Smiting III, Great Strength II
          39 Great Strength III
          40 Great Smiting IV
          """, 1, 8, 57),
)
