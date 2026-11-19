"""Three connected areas for character training, equipment selection, and encounters."""

from aurora import Record, bite, flt, loc, lst, ref, string, word
from content import creatures
from world import Area, color, variables


def architecture(area, fixtures):
    for appearance, name, x, y in fixtures:
        area.prop(appearance, name, x, y)


def hall():
    area = Area("zks_hall", "Síň postav", "tni02", 10, 8,
                [(2, 1, 8, 5), (1, 3, 3, 7), (7, 3, 9, 7), (3, 5, 7, 7)],
                "Příprava postavy, jejího přesvědčení a vývoje.")
    area.point("zks_start", 49, 18, title="Vstup do síně postav")
    area.point("zks_hall_gear", 25, 57, 0)
    area.point("zks_hall_arena", 76, 57, 180)
    area.prop(464, "Kronika postavy", 46, 28, action="character", tag="zks_character")
    area.prop(87, "Co kde najdu", 54, 20, action="read",
              text="Kronika nebo mistryně Neria upraví XP a přesvědčení. Západní dveře vedou do zbrojnice. "
                   "Východní dveře vedou ke knize bestiáře a na kolbiště.")
    area.prop(58, "Odpočinek v síni", 52, 44, action="rest")
    area.passage("Do zbrojnice", 18, 62, "zks_gear_in", appearance=252)
    area.passage("K výcvikovému dvoru", 83, 62, "zks_arena_in", appearance=252)
    architecture(area, [(97, "Stůl kronikářky", 43, 30), (311, "Svazky se záznamy", 32, 35),
                        (178, "Lavice u ohně", 49, 46), (125, "Prapor zbrojnice", 22, 60),
                        (127, "Prapor kolbiště", 78, 60), (57, "Lampa při vstupu", 40, 19),
                        (57, "Lampa při vstupu", 59, 19), (57, "Lampa kronikářky", 50, 31),
                        (57, "Lampa u zbrojnice", 26, 55), (57, "Lampa u kolbiště", 73, 55),
                        (288, "Výklenek s kronikami", 49, 66), (383, "Svíce", 43, 30)])
    return area


def armory():
    area = Area("zks_armory", "Zbrojnice a klenotnice", "tni02", 11, 8,
                [(2, 1, 9, 7), (1, 3, 2, 6), (9, 2, 10, 7)],
                "Výdejna všech typů výstroje a zkušebních pomůcek.")
    area.point("zks_gear_in", 54, 19, title="Vstup z hlavní síně")
    area.point("zks_gear_arena", 88, 61, 180)
    area.passage("Zpět do síně postav", 54, 13, "zks_hall_gear", appearance=252)
    area.passage("Přímo k bestiáři", 95, 63, "zks_arena_gear", appearance=252)
    for x, y, appearance, title, group, tag in (
        (35, 33, 105, "Zbraně na blízko", 1, "zks_melee"),
        (72, 32, 7, "Střelba a střelivo", 2, "zks_ranged"),
        (34, 55, 8, "Zbroje a štíty", 3, "zks_armor"),
        (57, 54, 105, "Oděv a doplňky", 4, "zks_apparel"),
        (78, 54, 311, "Šperky, spěch a pomůcky", 5, "zks_jewels"),
    ):
        area.prop(appearance, title, x, y, action="gear", group=group, tag=tag)
    architecture(area, [(57, "Lampa výdejny", 43, 29), (57, "Lampa výdejny", 65, 29),
                        (57, "Lampa klenotnice", 82, 49), (57, "Lampa zbrojnice", 24, 49),
                        (97, "Stůl klenotnice", 75, 54), (288, "Výklenek se štíty", 25, 55),
                        (178, "Lavice", 52, 62), (49, "Sud s násadami", 39, 44),
                        (246, "Zkouška tepaného vzoru", 55, 40), (7, "Schránka střeliva", 78, 34)])
    return area


def arena():
    area = Area("zks_arena", "Výcvikový dvůr a bestiář", "tni02", 15, 13,
                [(3, 1, 12, 3), (1, 5, 14, 12)],
                "Předsíň bestiáře a oddělené kolbiště s prostorem i pro draky.")
    area.point("zks_arena_in", 66, 19, title="Předsíň bestiáře")
    area.point("zks_arena_gear", 92, 22, 180)
    area.point("zks_into_ring", 74, 57, title="Vstup do kolbiště")
    area.passage("Zpět do síně postav", 35, 17, "zks_hall_arena", appearance=252)
    area.passage("Do zbrojnice", 113, 19, "zks_gear_arena", appearance=252)
    area.prop(464, "Kniha bestiáře", 76, 24, action="bestiary", tag="zks_beasts")
    area.prop(58, "Odpočinek v předsíni", 50, 23, action="rest")
    area.prop(87, "Pravidla kolbiště", 64, 24, action="read",
              text="V knize lze přivolat jednotlivce i smíšenou skupinu. Stvůry čekají za přechodem na kolbiště. "
                   "Při porážce se vrátíš do předsíně. Kniha umí také celé kolbiště vyčistit.")
    area.passage("Na kolbiště", 104, 25, "zks_into_ring", appearance=391)
    area.passage("Ústup zpět k bestiáři", 70, 54, "zks_arena_in", appearance=391)
    area.prop(464, "Kniha bestiáře u ústupu", 79, 55, action="bestiary")
    for index in range(12):
        x = 26 + index % 6 * 19
        y = 84 + index // 6 * 22
        area.point(f"zks_spawn_{index + 1}", x, y, 270)
    architecture(area, [(97, "Pult bestiáře", 73, 25), (311, "Skříň bestiáře", 83, 27),
                        (57, "Lampa předsíně", 47, 17), (57, "Lampa předsíně", 97, 17),
                        (57, "Lampa u výstupu", 65, 57), (57, "Lampa u výstupu", 86, 57),
                        (57, "Ohraničení kolbiště", 20, 68), (57, "Ohraničení kolbiště", 130, 68),
                        (57, "Ohraničení kolbiště", 20, 108), (57, "Ohraničení kolbiště", 130, 108),
                        (125, "Prapor kolbiště", 19, 80), (127, "Prapor kolbiště", 131, 80)])
    return area


def mentor():
    figure = creatures()["hvd_kopi"]
    for event in tuple(figure.fields):
        if event.startswith("Script"):
            figure.fields[event] = ref("")
    figure.fields.update(TemplateResRef=ref("zks_mentor"), Tag=string("zks_mentor"),
                         FirstName=loc("Mistryně Neria"), LastName=loc(""),
                         Description=loc("Připravuje návštěvníky na zkoušky schopností a výstroje."),
                         FactionID=word(2), Plot=bite(1), Gender=bite(1), Wings=bite(0),
                         Appearance_Head=bite(1), Deity=string(""), ScriptDialogue=ref("zks_talk"),
                         Equip_ItemList=lst([Record(2, EquippedRes=ref("zks_mentor_robe"))]),
                         VarTable=variables())
    return figure


def area_records(zone, tiles):
    records = zone.records(tiles)
    entries = records["are"].fields
    entries.update(OnEnter=ref(""), OnExit=ref(""), OnHeartbeat=ref(""), NoRest=bite(0),
                   MoonAmbientColor=color(135, 132, 122), MoonDiffuseColor=color(179, 165, 144),
                   MoonFogAmount=bite(0))
    if zone.key == "zks_hall":
        figure = mentor()
        figure.fields.update(XPosition=flt(56), YPosition=flt(31), ZPosition=flt(0),
                             XOrientation=flt(0), YOrientation=flt(-1))
        records["git"].fields["Creature List"] = lst([Record(4, **figure.fields)])
        records["gic"].fields["Creature List"] = lst([Record(4, Comment=string("Mistryně Neria"))])
    return records
