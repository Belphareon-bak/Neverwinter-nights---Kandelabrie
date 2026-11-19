"""Original equipment catalog and arena variants using stock NWN:EE models and combat AI."""

import json

from aurora import LOC, LIST, STRUCT, TYPE, bite, dword, gff_decode, integer, loc, lst, ref, string, word
from content import item, prop
from world import variables


# kind: 1 melee, 2 ranged, 3 armour/accessory, 4 monk gloves, 5 ammunition
GEAR = (
    (1, 22, 1, "Dýka", "nw_wswdg001"), (1, 60, 1, "Srp", "nw_wspmsc002"),
    (1, 28, 1, "Kyj", "nw_wblcl001"), (1, 9, 1, "Palcát", "nw_wblml001"),
    (1, 47, 1, "Řemdih", "nw_wblmms002"), (1, 58, 1, "Krátké kopí", "nw_wplmss002"),
    (1, 50, 1, "Bojová hůl", "nw_wdbmqs002"), (1, 0, 1, "Krátký meč", "nw_wswmss002"),
    (1, 1, 1, "Dlouhý meč", "nw_wswls001"), (1, 13, 1, "Obouruční meč", "nw_it_crewgs005"),
    (1, 51, 1, "Rapír", "nw_wswmrp002"), (1, 53, 1, "Šavle", "nw_wswmsc002"),
    (1, 38, 1, "Ruční sekera", "nw_waxhn001"), (1, 2, 1, "Bitevní sekera", "nw_waxbt001"),
    (1, 18, 1, "Obouruční sekera", "nw_waxgr001"), (1, 37, 1, "Lehké kladivo", "nw_wblhl001"),
    (1, 5, 1, "Válečné kladivo", "nw_wblhw001"), (1, 4, 1, "Lehký cep", "nw_wblfl001"),
    (1, 35, 1, "Těžký cep", "nw_wblfh001"), (1, 10, 1, "Halapartna", "nw_wplhb001"),
    (1, 55, 1, "Kosa", "nw_wplmsc002"), (1, 95, 1, "Trojzubec", "nw_wpltr001"),
    (1, 3, 1, "Půldruhý meč", "nw_wswbs001"), (1, 41, 1, "Katana", "nw_wswka001"),
    (1, 40, 1, "Kama", "nw_wspka001"), (1, 42, 1, "Kukri", "nw_wspmku002"),
    (1, 12, 1, "Dvojitý meč", "nw_wdbmsw002"), (1, 32, 1, "Dvojitý palcát", "nw_wdbma001"),
    (1, 33, 1, "Dvojitá sekera", "nw_wdbax001"), (1, 108, 1, "Trpasličí válečná sekera", "x2_wdwraxe001"),
    (1, 111, 1, "Bič", "x2_it_wpmwhip1"),
    (2, 8, 2, "Dlouhý luk", "nw_hen_daelb1"), (2, 11, 2, "Krátký luk", "nw_hen_galsb1"),
    (2, 6, 2, "Těžká kuše", "nw_wbwmxh002"), (2, 7, 2, "Lehká kuše", "nw_hen_bodxl1"),
    (2, 61, 2, "Prak", "nw_wbwmsl001"), (2, 31, 1, "Vrhací šipky", "nw_wthdt001"),
    (2, 59, 1, "Šurikeny", "nw_wthmsh002"), (2, 63, 1, "Vrhací sekery", "nw_wthax001"),
    (2, 20, 5, "Šípy", "nw_wamar001"), (2, 25, 5, "Šipky do kuše", "nw_wambo001"),
    (2, 27, 5, "Střely do praku", "nw_wambu001"),
    (3, 14, 3, "Malý štít", "nw_ashmsw002"), (3, 56, 3, "Velký štít", "nw_ashlw001"),
    (3, 57, 3, "Pavéza", "nw_ashmto002"),
    (4, 17, 3, "Přilba", "nw_arhe001"), (4, 21, 3, "Opasek", "nw_it_mbelt001"),
    (4, 26, 3, "Boty", "nw_it_mboots001"), (4, 36, 4, "Rukavice pro boj beze zbraně", "nw_it_mglove001"),
    (4, 78, 3, "Náramky", "nw_it_mbracer001"), (4, 80, 3, "Plášť", "nw_aarcl013"),
    (4, 19, 3, "Amulet", "nw_hen_dae1rw"), (4, 52, 3, "Prsten", "nw_hen_bod1rw"),
)

ARMOR = ("Oděv", "Vycpávaná zbroj", "Kožená zbroj", "Pobíjená kožená zbroj", "Šupinová zbroj",
         "Kroužková zbroj", "Dlahová zbroj", "Poloplátová zbroj", "Plná plátová zbroj")

BESTIARY = (
    ("nw_rat001", "Krysa"), ("nw_goblina", "Goblin"), ("nw_kobold001", "Kobold"),
    ("nw_orca", "Ork"), ("nw_skeleton", "Kostlivec"), ("nw_bandit002", "Bandita s lukem"),
    ("nw_wolf", "Vlk"), ("nw_zombie01", "Zombie"), ("nw_gnoll001", "Gnoll"),
    ("nw_kobold003", "Koboldí čaroděj"), ("nw_bugbeara", "Bugbear"), ("nw_werewolf", "Vlkodlak"),
    ("nw_orcchiefa", "Orčí náčelník"), ("nw_spidgiant", "Obří pavouk"), ("nw_ogre01", "Zlobr"),
    ("nw_gargoyle", "Chrlič"), ("x2_beholder002", "Malý beholder"),
    ("x0_wyrmling_blk", "Černé dráče"), ("nw_minotaur", "Minotaurus"), ("nw_orcwiza", "Orčí šaman"),
    ("nw_troll", "Troll"), ("nw_mummy", "Mumie"), ("nw_direwolf", "Strašlivý vlk"),
    ("nw_wraith", "Přízrak"), ("x0_wyrmling_red", "Rudé dráče"), ("x2_harpy001", "Harpyje"),
    ("nw_airelder", "Prastarý elementál vzduchu"), ("nw_fireelder", "Prastarý elementál ohně"),
    ("nw_eartheld", "Prastarý elementál země"), ("nw_waterhuge", "Obří elementál vody"),
    ("x0_medusa", "Medúza"), ("x0_manticore", "Mantikora"), ("nw_slaadred", "Rudý slaad"),
    ("nw_yuan_ti003", "Yuan-ti"), ("nw_rakshasa", "Rakšása"), ("nw_ogrechief01", "Zlobří náčelník"),
    ("nw_ettin", "Ettin"), ("nw_zombieboss", "Nemrtvý obr"), ("x0_gynosphinx", "Gynosphinga"),
    ("nw_umberhulk", "Umbra"), ("x2_mindflayer001", "Mozkožrout"), ("nw_trollboss", "Trollí vůdce"),
    ("nw_slaadgray", "Šedý slaad"), ("nw_mummyboss", "Vládce mumií"),
    ("nw_vampire001", "Upír"), ("x3_emgolem001", "Smaragdový golem"), ("x3_rubygolem001", "Rubínový golem"),
    ("x2_beholder001", "Beholder"), ("x0_sphinx", "Sfinga"), ("nw_minotaurboss", "Minotauří šampion"),
    ("x3_diagolem001", "Diamantový golem"), ("x2_pitfiend001", "Pekelný běs"),
    ("nw_slaaddeth", "Slaad smrti"), ("nw_drgred001", "Mladý rudý drak"), ("nw_balorboss", "Balor"),
    ("nw_lich002", "Lich"), ("x2_mindflayer002", "Starší mozkožrout"), ("nw_drgred002", "Dospělý rudý drak"),
    ("nw_lichboss", "Pán lichů"), ("x2_dragonshad001", "Stínový drak"),
    ("nw_drgred003", "Prastarý rudý drak"), ("x2_demilich001", "Demilich"),
    ("x2_slaadwhite001", "Bílý slaad"), ("nw_lich001", "Arcimág lich"),
    ("x2_slaadblack001", "Černý slaad"), ("x2_golem002", "Mithrilový golem"),
    ("x2_golem001", "Adamantiový golem"), ("x2_dragonpris001", "Prizmatický drak"),
    ("x2_dracolich001", "Drakolich"),
)


def decoded(game, name, extension):
    def text_fields(record):
        for key, (kind, value) in record.fields.items():
            if kind == LOC:
                strref, strings = value
                record.fields[key] = (kind, (strref, {lang: blob.decode("cp1250", errors="replace").replace("\ufffd", "?")
                                                    for lang, blob in strings.items()}))
            elif kind == STRUCT:
                text_fields(value)
            elif kind == LIST:
                for child in value:
                    text_fields(child)
    record = gff_decode(game.read(name, extension), "cp1250")
    text_fields(record)
    return record


def armor_models(game):
    ac_values = {int(row[0]): int(float(row[2])) for line in game.read("parts_chest", "2da").decode("ascii").splitlines()
                 if len(row := line.split()) > 2 and row[0].isdigit() and row[2] != "****"}
    models = {}
    for name, kind in sorted(game.index):
        if kind == TYPE["uti"] and name.startswith(("nw_aarcl", "nw_cloth", "nw_maarcl")):
            record = gff_decode(game.read(name, "uti"))
            if record.value("BaseItem") == 16 and record.value("ArmorPart_Torso") in ac_values:
                models.setdefault(ac_values[record.value("ArmorPart_Torso")], name)
    return models


def styled_item(game, key, name, base, source, *, properties=(), stack=1):
    model = gff_decode(game.read(source, "uti"))
    assert model.value("BaseItem") == base, (key, source, model.value("BaseItem"), base)
    result = item(key, base, name, "Výstroj ze Zkušebny dobrodruhů.", properties=properties, stack=stack)
    for field, value in model.fields.items():
        if field.startswith(("ModelPart", "ArmorPart")) or field.endswith("Color"):
            result.fields[field] = value
    return result


def equipment(game):
    models = armor_models(game)
    definitions = (*GEAR, *((3, 16, 3, name, models[ac]) for ac, name in enumerate(ARMOR)))
    resources = {}
    rows = []
    for index, (group, base, kind, name, source) in enumerate(definitions):
        key = f"zks_e{index:02d}"
        stack = 99 if base in (20, 25, 27) else 50 if base in (31, 59, 63) else 1
        resources[key] = styled_item(game, key, name, base, source, stack=stack)
        rows.append([key, group, kind, name, stack, base])
    for key, name, base, source, props in (
        ("zks_haste", "Boty trvalého spěchu", 26, "nw_it_mboots001", (prop(35),)),
        ("zks_amulet", "Amulet atributů", 19, "nw_hen_dae1rw", ()),
        ("zks_ring", "Prsten atributů", 52, "nw_hen_bod1rw", ()),
        ("zks_focus", "Ohnisko kouzel", 19, "nw_hen_dae1rw", ()),
        ("zks_heal", "Lektvar úplného uzdravení", 49, "nw_it_mpotion001", (prop(15, 139, 3, 1),)),
    ):
        resources[key] = styled_item(game, key, name, base, source, properties=props)
    for key, source in (("zks_lock", "nw_it_picks004"), ("zks_med", "nw_it_medkit004"), ("zks_trap", "nw_it_trap001")):
        stock = decoded(game, source, "uti")
        stock.fields.update(TemplateResRef=ref(key), Tag=string(key), Plot=bite(0))
        resources[key] = stock
    return resources, rows


def beasts(game):
    resources = {}
    rows = []
    for index, (source, name) in enumerate(BESTIARY):
        key = f"zks_m{index:02d}"
        creature = decoded(game, source, "utc")
        cr = float(creature.value("ChallengeRating"))
        hp = creature.value("MaxHitPoints")
        creature.fields.update(TemplateResRef=ref(key), Tag=string(key), FirstName=loc(name), LastName=loc(""),
                               Description=loc("Protivník přivolaný z bestiáře."), FactionID=word(1), Plot=bite(0),
                               IsImmortal=bite(0), Conversation=ref(""), ScriptDialogue=ref(""),
                               ScriptDeath=ref("zks_ar_dead"), BodyBag=bite(0), ItemList=lst([]),
                               VarTable=variables(zks_monster=1))
        resources[key] = creature
        rows.append([key, name, round(cr, 2), hp])
    rows.sort(key=lambda row: row[2])
    return resources, rows


def nwscript_data(gear, monsters):
    def function(name, values):
        # ASCII JSON is independent of the client's Czech code page.
        literal = json.dumps(json.dumps(values, ensure_ascii=True, separators=(",", ":")))
        return f"json {name}()\n{{\n    return JsonParse({literal});\n}}\n"
    return function("ZKS_GearCatalog", gear) + "\n" + function("ZKS_Bestiary", monsters)
