"""Eight compact, connected observatory locations."""

from aurora import bite, integer
from world import Area, color


def scene(art, key, title, tileset, size, rooms, purpose, *,
          ambient, diffuse, fog, sky=0, music=49, wind=67, rises=(), stair_columns=None, tiles=None):
    area = Area(key, title, tileset, *size, rooms, purpose, special_tiles=tiles or {},
                rises=rises, stair_columns=stair_columns or {})
    area.art = art
    area.lighting.update(IsNight=bite(1), SkyBox=bite(sky), MoonFogAmount=bite(fog),
                         MoonAmbientColor=color(*ambient), MoonDiffuseColor=color(*diffuse),
                         MoonFogColor=color(*(115, 127, 167) if sky else (29, 36, 61)),
                         ShadowOpacity=bite(38),
                         ChanceSnow=integer(48 if key == "hvd_rim" else 0))
    area.soundscape.update(MusicNight=integer(music), MusicDay=integer(music),
                           AmbientSndNight=integer(wind), AmbientSndDay=integer(wind))
    return area


def feature(area, asset, name, x, y, **settings):
    return area.prop(area.art[asset], name, x, y, **settings)


def fixture(area, rows):
    for appearance, name, x, y, bearing in rows:
        area.prop(appearance, name, x, y, bearing=bearing)


def cover(area, points, appearance):
    for x, y in points:
        area.prop(appearance, "Kamenný kryt", x, y, cover=1)


def light(area, x, y, tint=15113, height=1.75, tag=""):
    area.prop(tint, "Světlo", x, y, z=area.z_at(y) + height, tag=tag)


def lantern(area, x, y, tint=15113):
    feature(area, "hvd_beacon", "Stojatá hlídková lucerna", x, y)
    light(area, x, y, tint, 2.15)


def rail(area, run, bearing=0, z=None):
    for x, y in run:
        feature(area, "hvd_rail", "Kamenná balustráda", x, y, bearing=bearing, z=z)


def cloudbed(area, x, y):
    feature(area, "hvd_cloudbed", "Mraky pod římsou", x, y, z=1.3)


def mountain(art):
    a = scene(art, "hvd_rim", "Výstupová římsa a nocleh", "tts02", (7, 7),
              [(1, 0, 4, 3), (3, 2, 5, 5), (2, 4, 6, 7), (5, 2, 6, 3)],
              "Nocleh pod kopulí, větrná skalní stezka a závorou zavřený průlez.",
              ambient=(91, 108, 149), diffuse=(175, 188, 219), fog=2, sky=4, music=59, wind=31)
    a.point("hvd_start", 23, 16, 82, "Nocleh pod kopulí")
    a.point("hvd_rim_halls", 40, 47, 270, "Vchod do chodeb clon")
    a.point("hvd_rim_works", 52, 24, 180, "Servisní stezka")
    a.transition("Dovnitř hvězdárny", "hvt_rim_halls", (37, 52, 43, 55), "hvd_halls_in")
    a.transition("Spodní servisní lávka", "hvt_rim_works", (56, 21, 59, 27),
                 "hvd_works_rim", require="hvd_work_link")
    feature(a, "hvd_octagon", "Hvězdárna druhého nebe", 40, 60)
    feature(a, "hvd_columnade", "Ostění servisního průlezu", 58, 24, bearing=90)
    rail(a, [(32, 48), (48, 48)])
    lantern(a, 35.9, 51)
    lantern(a, 44.1, 51)
    a.prop(464, "Rozpis nebeské hlídky", 24.0, 21.8, z=.88, tag="hvd_rim_order", action="clue", clue=1,
           text="První záznam určuje, která pečeť zůstala na stanovišti.")
    a.prop(7, "Výpravní bedna", 28, 22, action="supply", tag="hvd_supply")
    a.prop(58, "Oheň pod přístřeškem", 18, 18.7, action="rest", tag="hvd_campfire")
    a.prop(318, "Mapa výprav", 25.5, 22.0, z=.89)
    a.prop(87, "Výstraha hlídky", 31, 22, action="read",
           text="U napnutých praporků se drž při kameni. Průlez na dílenskou lávku se otevírá od dílny.")
    a.prop(288, "Kniha nové výpravy", 13, 18, action="reset", tag="hvd_reset",
           text="Družina se musí sejít u noclehu. Druhé použití vypraví novou hlídku.")
    fixture(a, [
        (434, "Plátěný nocleh", 15, 25, 180), (51, "Svázaná lůžka", 15.3, 23.1, 90),
        (108, "Suché dřevo", 16.2, 19.2, 12), (178, "Lavice u ohniště", 20.8, 18.8, 90),
        (97, "Stůl výpravy", 24.8, 21.5, 90), (49, "Zásobní sud", 11.9, 23, 0),
        (174, "Závěj u plátna", 12.2, 27.9, 65), (122, "Praporek poryvů", 34, 27, 10),
        (123, "Praporek při skále", 47.1, 30, 30), (410, "Skalní stěna", 30, 37, 65),
        (408, "Prasklý skalní blok", 48.2, 39, 20), (336, "Zlomený mezník", 32, 44, 0),
        (255, "Sníh pod kopulí", 49, 57, 10), (408, "Suti při zdi", 28, 56, 0),
        (463, "Vyschlý sud u průlezu", 55, 27, 35),
    ])
    light(a, 18, 18.7, 15109, 1.3)
    cover(a, [(35.5, 30.5), (45.6, 34.0), (34.1, 40.0)], 407)
    a.trap("Poryv mezi bradly", "hvd_wind", (35, 27, 47, 35), hazard=1)
    a.mob("hvd_strhavac", 40, 38)
    a.mob("hvd_vrhac", 47, 45)
    return a


def halls(art):
    a = scene(art, "hvd_halls", "Chodby clon", "tni02", (7, 6),
              [(1, 1, 3, 3), (2, 2, 6, 3), (4, 3, 6, 5), (1, 4, 3, 5), (2, 3, 3, 5)],
              "Paprsková chodba se třemi poli, servisním výklenkem a schody ke kopuli.",
              ambient=(75, 85, 110), diffuse=(139, 145, 179), fog=0, music=50, wind=67)
    a.point("hvd_halls_in", 22, 16, 90)
    a.point("hvd_halls_works", 17, 45, 0, "Přístup k dílnám")
    a.point("hvd_halls_dome", 50, 44, 270, "Schody ke kopuli")
    a.transition("Ven na římsu", "hvt_halls_rim", (19, 10, 25, 13), "hvd_rim_halls")
    a.transition("Na servisní lávku", "hvt_halls_works", (10, 42, 13, 48), "hvd_works_in")
    a.transition("Do kopule", "hvt_halls_dome", (47, 48, 53, 51), "hvd_dome_in")
    for x, y, angle in ((22, 10.8, 0), (11.3, 45, 90), (50, 49, 0)):
        feature(a, "hvd_columnade", "Kamenné ostění", x, y, bearing=angle)
    for i, x in enumerate((35, 44, 53), 1):
        feature(a, "hvd_columnade", "Výbojová klenba", x, 25, bearing=90)
        feature(a, "hvd_beamstrip", "Meze světelného pole", x + .7, 25)
        a.trap("Pole clony " + str(i), f"hvd_hallray{i}", (x - 1, 21, x + 2, 29),
               hazard=2, flag="hvd_hall_off", axis=1)
        a.prop(826 if i == 3 else 827, "Prasklina ve filtru", x, 28.0, bearing=180)
        light(a, x, 28.1, 15107, 2.8)
    feature(a, "hvd_dial", "Pojistka paprskové chodby", 28, 19.0, action="disarm",
            tag="hvd_ray_lock", flag="hvd_hall_off", skill=15,
            text="Mosazná západka je ohnutá. Postup ukazuje nákres ze servisní dílny.")
    a.prop(464, "Předpis o clonách", 15.8, 23.5, z=.95, action="read",
           text="Když se pod obloukem rozběhne světlo, ustup před mosaznou rysku. "
                "Bezpečný odskok je ve výklenku u západky.")
    fixture(a, [
        (285, "Deska zapisovatele", 15.6, 23.3, 90), (456, "Záznamy směny", 16, 23.8, 0),
        (311, "Police s náhradními filtry", 12.4, 25, 90), (287, "Lavice obsluhy", 17, 18, 90),
        (125, "Prapor pozorovatelny", 21, 28.5, 90), (178, "Lavice u výstupu", 53, 46.3, 0),
        (474, "Převržený regál", 25.7, 43.8, 90), (336, "Úlomek klenby", 45, 39, 0),
        (447, "Odložený filtr v mosazi", 20, 47, 180), (318, "Nákres servisní lávky", 22, 45, 0),
    ])
    for x, y in ((18, 26), (14.7, 47.7), (46.4, 47), (54, 47)):
        lantern(a, x, y)
    cover(a, [(30, 28.2), (47, 31.3), (55, 37), (22.7, 42)], 79)
    for creature, x, y in (("hvd_strhavac", 31, 24), ("hvd_vrhac", 43, 25),
                           ("hvd_spradac", 53, 32), ("hvd_strhavac", 48, 36), ("hvd_vrhac", 24, 39)):
        a.mob(creature, x, y)
    return a


def workshops(art):
    a = scene(art, "hvd_works", "Dílny a servisní lávka", "tcm02", (6, 7),
              [(1, 1, 4, 2), (1, 5, 5, 6)],
              "Servisní dvůr s optickou zkouškou a dvojicí podest, mezi nimiž vede skutečný most.",
              ambient=(94, 112, 151), diffuse=(180, 192, 228), fog=1, sky=4, music=49, wind=202,
              tiles={(2, 2): (895, 0), (2, 3): (818, 0), (2, 4): (895, 2)})
    a.point("hvd_works_in", 26, 15.0, 90)
    a.point("hvd_works_hp", 42, 54, 180, "Horní lávka ke kopuli")
    a.point("hvd_works_rim", 36, 15.5, 180, "Sestup ke starému noclehu")
    a.transition("Do chodeb clon", "hvt_works_halls", (23, 10, 29, 13), "hvd_halls_works")
    a.transition("Lávka do kopule", "hvt_works_dome", (45, 51, 49, 57), "hvd_dome_works")
    a.transition("Starý servisní sestup", "hvt_works_rim", (37, 11, 40, 19), "hvd_rim_works",
                 flag="hvd_work_link")
    feature(a, "hvd_columnade", "Ostění servisního sestupu", 40, 15, bearing=90)
    feature(a, "hvd_columnade", "Ostění horní galerie", 49, 54, bearing=90)
    cloudbed(a, 29, 34)
    rail(a, [(16, 19), (34, 19), (16, 51), (35, 51), (44, 51)])
    rail(a, [(23.3, 35), (26.7, 35)], 90, 6.65)
    fixture(a, [
        (97, "Zkušební stůl", 17, 16, 90), (456, "Výpočty odrazů", 16.3, 16.7, 0),
        (108, "Zbytky prken", 13, 18.4, 90), (48, "Kovadlina na rámy", 32.2, 17.9, 90),
        (63, "Vyhaslá výheň", 33, 12.6, 0), (434, "Plachta dílny", 15.0, 14.5, 90),
        (287, "Servisní lavice", 35, 58.2, 0), (336, "Odložená patka", 16, 56.7, 0),
        (294, "Stará nebeská sféra", 43, 57, 0),
    ])
    a.prop(464, "Návratový zápis správkyně", 17.7, 15.5, z=5.88, action="notes", tag="hvd_return_log",
           text="Sešla jsem starou lávkou. V ohlašovně mě minuli. Lucernu jsem nechala nahoře. "
                "Klíč od pouzdra je pod přehybem desek.")
    a.prop(447, "Zkušební zrcadlo", 20, 17.2, bearing=130, action="mirror", tag="hvd_lab_mirror",
           text="Patice je stejná jako u poslední lucerny. Vezmi zrcadlo s sebou.")
    feature(a, "hvd_dial", "Spoušť zkušební optiky", 22.7, 17.8, action="testbeam")
    a.prop(7, "Pouzdro správkyně", 12.8, 12.5, action="loot", loot=1, tag="hvd_work_cache")
    a.prop(455, "Nákres objektivu", 17.1, 16.25, z=5.92, action="read",
           text="Západní clona na II. Východní clona na III. Rysky jsou i v kopuli.")
    feature(a, "hvd_beacon", "Ozvučnice servisní lávky", 30.9, 17.5, action="chime", tag="hvd_work_chime")
    feature(a, "hvd_sealstand", "Schránka údržby · Kotva", 18, 57, action="seal", seal=1, tag="hvd_anchor_seal")
    for x, y in ((24, 19.2), (28, 49), (12.5, 54), (46.2, 58.2)):
        lantern(a, x, y)
    cover(a, [(22, 52.8), (37.0, 56.5)], 337)
    for creature, x, y in (("hvd_spradac", 20.5, 54), ("hvd_strhavac", 29.5, 56), ("hvd_vrhac", 39, 54)):
        a.mob(creature, x, y)
    return a


def dome(art):
    a = scene(art, "hvd_dome", "Kopule druhého nebe", "tni02", (6, 6),
              [(1, 2, 4, 4), (2, 1, 4, 5), (4, 2, 5, 3), (3, 4, 4, 5)],
              "Kruhový měřicí sál, poškozený refraktor a výstupní oblouk mezi světy.",
              ambient=(92, 103, 137), diffuse=(178, 184, 217), fog=0, music=27, wind=68)
    a.point("hvd_dome_in", 30, 17, 90)
    a.point("hvd_dome_works", 16, 26, 0, "Servisní vchod")
    a.point("hvd_dome_steps", 30, 41, 270, "Otevření schodů")
    a.point("hvd_dome_short", 41, 26, 180, "Zkratka z předbraní")
    a.point("hvd_optic_gate", 30, 46.2, 90)
    a.transition("Do chodeb clon", "hvt_dome_halls", (27, 10, 33, 13), "hvd_halls_dome")
    a.transition("Na lávku do dílny", "hvt_dome_works", (10, 23, 13, 29), "hvd_works_hp")
    a.transition("Schody do nebe", "hvt_dome_steps", (27, 45, 33, 49), "hvd_steps_in", require="hvd_aligned")
    a.transition("Zkratka do předbraní", "hvt_dome_short", (46, 23, 50, 29), "hvd_gate_short", require="hvd_shortcut")
    for x, y, angle in ((30, 11, 0), (11, 26, 90), (48, 26, 90), (30, 45.8, 0)):
        feature(a, "hvd_columnade", "Oblouk v plášti kopule", x, y, bearing=angle)
    feature(a, "hvd_starmap", "Mosazná mapa dvojí oblohy", 30, 31)
    feature(a, "hvd_plinth", "Čep refraktoru", 30, 31)
    feature(a, "hvd_refractor", "Prasklý refraktor", 30, 31, tag="hvd_refractor", action="optics",
            text="V objektivu visí cizí hvězdy. Mosazné rysky u jihozápadního a jihovýchodního ovladače jsou II a III.")
    feature(a, "hvd_dial", "Západní clona · cílová ryska II", 21, 29, action="dial", dial=1, tag="hvd_dial_w")
    feature(a, "hvd_dial", "Východní clona · cílová ryska III", 39, 29, action="dial", dial=2, tag="hvd_dial_e")
    feature(a, "hvd_sector2", "Cílová ryska II", 21, 27.4)
    feature(a, "hvd_sector3", "Cílová ryska III", 39, 27.4)
    fixture(a, [
        (285, "Hlavní stolec hvězdáře", 23.5, 18.3, 90), (456, "Pozorovací záznamy", 23.8, 18.6, 0),
        (294, "Kandelábrijská obloha", 17.4, 33.5, 0), (447, "Pevné zrcadlo u severní štěrbiny", 28.0, 42.5, 0),
        (311, "Skříň s filtry", 35.8, 17.3, 0), (317, "Prstenec svící", 28.0, 20.0, 0),
        (725, "Znak pozorovatelny", 37.5, 35.4, 90), (474, "Rozbité pouzdro skel", 14.5, 35.7, 16),
    ])
    a.prop(464, "Deník hvězdárny", 23.5, 18.5, z=.93, action="read",
           text="Po Čase potíží jsme sestrojili vlastní průchod. Když se obě rysky setkají, "
                "objektiv hledí na návratovou lucernu v nebeském předbraní.")
    for x, y in ((24.8, 42.2), (35.2, 42.2), (18, 23.7), (42, 23.2)):
        lantern(a, x, y)
    light(a, 30, 32.8, 15110, 3.2)
    light(a, 30, 42.7, 15107, 2.5)
    a.trap("Zpětný výboj refraktoru", "hvd_domeray", (26, 28, 34, 35), hazard=0)
    return a


def steps(art):
    a = scene(art, "hvd_steps", "Schody do nebe", "tcm02", (6, 7),
              [(2, 1, 4, 6), (1, 3, 5, 5), (0, 2, 6, 3), (0, 4, 6, 5)],
              "Dvě skutečná stoupání oddělená bouřnou podestou, kryt za poškozenými balustrádami.",
              ambient=(96, 115, 167), diffuse=(187, 204, 245), fog=2, sky=4, music=49, wind=202,
              rises=(3, 5), stair_columns={2: (2,), 4: (3,)})
    a.point("hvd_steps_in", 30, 15.1, 90)
    a.point("hvd_steps_walks", 30, 53, 270, "Horní schodiště")
    a.transition("Sestoupit do kopule", "hvt_steps_dome", (27, 10, 33, 13), "hvd_dome_steps")
    a.transition("K visutým ochozům", "hvt_steps_walks", (27, 56.5, 33, 60), "hvd_walks_in")
    cloudbed(a, 30, 35)
    feature(a, "hvd_columnade", "Ostění prvního schodu", 30, 11, bearing=0)
    feature(a, "hvd_columnade", "Oblouk horních ochozů", 30, 57)
    feature(a, "hvd_starmap", "Měřicí kruh bouřné podesty", 30, 35.8)
    rail(a, [(12.3, 35), (47.8, 35), (21.4, 17.1), (38.6, 17.1)], 90)
    for x, y in ((23, 17.5), (37, 17.5), (31, 38.5), (24.5, 55), (35.5, 55)):
        lantern(a, x, y)
    a.prop(464, "Rozpis u prvního schodu", 23.0, 15.3, z=5.83, action="clue", clue=2, tag="hvd_steps_order")
    a.prop(288, "Pult odpočívadla", 23.15, 15.25, bearing=90)
    feature(a, "hvd_sealstand", "Hnízdo Pečeti křídla", 42, 36.5, action="seal", seal=2, tag="hvd_wing_seal")
    feature(a, "hvd_beacon", "Ozvučnice bouřné podesty", 17.5, 35, action="chime", tag="hvd_steps_chime")
    a.point("hvd_storm_center", 30, 35.7)
    fixture(a, [(125, "Roztržený znak hlídky", 37, 31.2, 0), (336, "Zlomená římsa", 15, 30, 140),
                (93, "Socha pozorovatele", 39, 54.2, 180), (91, "Socha držící astroláb", 21, 54.2, 180)])
    cover(a, [(22, 32), (37.8, 34), (24, 38.0), (37.3, 38.2)], 337)
    a.mob("hvd_vir", 30, 35.7, seal=2, elite=1)
    a.mob("hvd_spradac", 44, 34)
    a.mob("hvd_strhavac", 35.7, 49.5)
    a.mob("hvd_vrhac", 27, 53.5)
    return a


def walks(art):
    tiles = {}
    for x in (2, 5):
        tiles.update({(x, 2): (895, 0), (x, 3): (818, 0), (x, 4): (895, 2)})
    a = scene(art, "hvd_walks", "Visuté ochozy", "tcm02", (8, 8),
              [(1, 1, 7, 2), (1, 5, 4, 6), (5, 5, 7, 6), (1, 6, 7, 7)],
              "Dvě mostní ramena nad propastí a samostatná stanoviště kopí a lucerny.",
              ambient=(98, 116, 168), diffuse=(182, 204, 239), fog=2, sky=4, music=49, wind=202, tiles=tiles)
    a.point("hvd_walks_in", 40, 15, 90)
    a.point("hvd_walks_gate", 40, 63, 270, "Výstup do předbraní")
    a.transition("Zpět na bouřnou podestu", "hvt_walks_steps", (37, 10, 43, 13), "hvd_steps_walks")
    a.transition("Do předbraní", "hvt_walks_gate", (37, 67, 43, 70), "hvd_gate_in")
    cloudbed(a, 40, 38)
    feature(a, "hvd_columnade", "Severní oblouk ochozů", 40, 68)
    feature(a, "hvd_sealstand", "Podstavec Pečeti kopí", 19, 57.7, action="seal", seal=3, tag="hvd_spear_seal")
    feature(a, "hvd_sealstand", "Podstavec Pečeti lucerny", 63, 57.7, action="seal", seal=4, tag="hvd_lamp_seal")
    rail(a, [(16, 19), (34, 19), (42, 19), (64, 19), (16, 51), (34, 51), (63, 51),
             (30, 68), (50, 68)])
    rail(a, [(23.3, 35), (26.7, 35), (53.3, 35), (56.7, 35)], 90, 6.65)
    for x, y in ((21.8, 18.5), (28.2, 18.5), (55, 17.5), (52, 51.5),
                 (19.5, 53), (46, 63), (34, 63)):
        lantern(a, x, y, 15107 if x < 30 else 15113)
    fixture(a, [(105, "Stojan kopiníka", 14.3, 58, 90), (125, "Znak kopí", 19, 62, 180),
                (91, "Kamenný kopiník", 17.5, 61.4, 180), (92, "Kamenný světlonoš", 65, 61.4, 180),
                (126, "Znak lucerny", 63, 62, 180), (287, "Lavice stráže", 69, 56, 90),
                (288, "Stolec pro výměnu knotů", 65.8, 54, 0), (49, "Rezervní olej", 68, 55, 0)])
    cover(a, [(17, 54), (30, 57), (53, 55), (65, 53), (46, 65)], 337)
    for creature, x, y, sign in (("hvd_kopi", 22, 57, 3), ("hvd_strhavac", 26, 51, 0),
                                 ("hvd_vrhac", 32, 57, 0), ("hvd_svetlonos", 61, 56, 4),
                                 ("hvd_spradac", 50, 56, 0), ("hvd_strhavac", 56, 52, 0)):
        a.mob(creature, x, y, seal=sign, elite=bool(sign))
    return a


def gate(art):
    a = scene(art, "hvd_gate", "Předbraní Horních sfér", "tcm02", (7, 7),
              [(1, 1, 6, 4), (2, 4, 5, 6), (0, 4, 7, 5)],
              "Poutní schodiště, trojice patic pod obřadním obloukem a malá strážnice při zkratce.",
              ambient=(111, 124, 172), diffuse=(204, 214, 251), fog=1, sky=4, music=27, wind=30,
              rises=(5,), stair_columns={4: (3,)})
    a.point("hvd_gate_in", 35, 16.3, 90)
    a.point("hvd_gate_top", 35, 50.5, 270)
    a.point("hvd_gate_short", 52, 22.0, 180, "Odpočívárna a servisní zkratka")
    a.point("hvd_final_gate", 35, 53.3, 90)
    a.transition("Zpět na visuté ochozy", "hvt_gate_walks", (32, 10, 38, 13), "hvd_walks_gate")
    a.transition("Sestup do kopule", "hvt_gate_dome", (57, 18, 60, 25), "hvd_dome_short", flag="hvd_shortcut")
    a.transition("Vstoupit na Poslední stupeň", "hvt_gate_top", (32, 53, 38, 57), "hvd_top_in",
                 require="hvd_gate_open")
    cloudbed(a, 35, 38)
    feature(a, "hvd_gatearch", "Brána tří pečetí", 35, 53.3, tag="hvd_stone_frame")
    feature(a, "hvd_starmap", "Rozeta pod třemi paticemi", 35, 29)
    feature(a, "hvd_columnade", "Ostění servisního sestupu", 59, 22, bearing=90)
    for i, x in enumerate((29, 35, 41), 1):
        feature(a, "hvd_sealstand", f"{('I', 'II', 'III')[i-1]} · Patice pečeti", x, 28,
                action="socket", slot=i, tag=f"hvd_socket_{i}")
        feature(a, f"hvd_sector{i}", "Podlahový znak stupně", x, 25.7)
    feature(a, "hvd_dial", "Ověřit tři patice", 35, 35.6, action="gate", tag="hvd_gate_control")
    a.prop(240, "Reliéf tří stupňů", 46.0, 19.8, action="clue", clue=3, tag="hvd_gate_order")
    a.prop(288, "Stolec rozpisu a obnovy pečetí", 23, 19.1, action="recap", tag="hvd_recap")
    a.prop(58, "Odpočinek ve strážnici", 54, 16, action="rest")
    a.prop(8, "Schránka poslední hlídky", 52, 34.4, action="loot", loot=2, tag="hvd_guard_cache")
    feature(a, "hvd_dial", "Zakrytí proudu ve strážnici", 48.1, 30.6, action="disarm",
            flag="hvd_chest_off", skill=15, tag="hvd_guard_lock")
    a.trap("Závora světla ve strážnici", "hvd_gatechest", (50, 31, 55, 36), hazard=2, flag="hvd_chest_off")
    a.trap("Výboj tří patic", "hvd_gatespark", (27, 24, 43, 36), hazard=0)
    fixture(a, [(453, "Socha navracejícího světlo", 28.9, 53.0, 178),
                (453, "Socha vítající příchozí", 41.1, 53.0, 182),
                (125, "Znak nebeské hlídky", 27.3, 55.5, 0), (126, "Znak návratu", 42.7, 55.5, 0),
                (51, "Složené pokrývky stráže", 54.6, 14.5, 90), (287, "Lavice pod plátnem", 56, 16, 90),
                (311, "Skříň na výstroj", 55.9, 36.3, 90), (49, "Olej pod policí", 56, 32, 0),
                (294, "Sféra Horních sfér", 18.9, 35, 0), (91, "Starý člen hlídky", 17, 30, 100)])
    rail(a, [(12.5, 21), (12.5, 26), (15.5, 38), (52, 38)])
    for x, y in ((21, 28), (46.5, 26.5), (30, 38.6), (40, 38.6), (31, 51.5), (39, 51.5)):
        lantern(a, x, y)
    cover(a, [(24.5, 34.0), (44.4, 35), (47, 28.6)], 78)
    return a


def summit(art):
    a = scene(art, "hvd_top", "Poslední stupeň", "tcm02", (7, 7),
              [(2, 1, 5, 3), (1, 3, 6, 5), (2, 5, 5, 6), (0, 2, 7, 3)],
              "Tři povrchem odlišené výseče strážní podesty a vyzdvižené stanoviště poslední lucerny.",
              ambient=(93, 105, 147), diffuse=(223, 214, 247), fog=1, sky=4, music=49, wind=30,
              rises=(3,), stair_columns={2: (3,)})
    a.point("hvd_top_in", 35, 15.8, 90)
    a.point("hvd_boss_home", 35, 45, 270)
    a.point("hvd_add_west", 17.5, 43.3, 315)
    a.point("hvd_add_east", 52.5, 43.3, 225)
    a.point("hvd_summit_exit", 35, 58.5, 90)
    a.transition("Ústup do předbraní", "hvt_top_gate", (32, 10, 38, 13), "hvd_gate_top")
    a.transition("Návrat na římsu", "hvt_top_rim", (32, 57, 38, 60), "hvd_start", require="hvd_won")
    cloudbed(a, 35, 37)
    feature(a, "hvd_columnade", "Oblouk služebního návratu", 35, 58.7)
    feature(a, "hvd_starmap", "Návratová rozeta", 35, 47.1)
    a.prop(87, "Plán hlídkové podesty", 25.5, 18.8, action="read",
           text="Ithren střeží tři výseče. Světlo před nárazem označí ohroženou cestu. "
                "Zkušební zrcadlo pasuje do patice pod schody.")
    a.trap("Ithrenovo stanoviště", "hvd_boss_start", (13, 30, 57, 55), hazard=3)
    feature(a, "hvd_sealstand", "Patice zkušebního zrcadla", 44.6, 17.8, action="mount", tag="hvd_mirror_mount")
    feature(a, "hvd_dial", "Ruční clona poslední lucerny", 35, 53.5, action="shutter", tag="hvd_final_sh")
    feature(a, "hvd_beacon", "Poslední lucerna", 35, 55.5)
    light(a, 35, 55.5, 15109, 2.1, tag="hvd_last_lamp")
    a.prop(8, "Schránka · Plášť dvojí oblohy", 28.4, 55.5, action="reward", loot=3, tag="hvd_cloak_reward")
    a.prop(8, "Schránka · Spona strážce", 41.6, 55.5, action="reward", loot=4, tag="hvd_badge_reward")
    for y in (33.5, 39.0, 46.8, 52.7):
        for index, x in enumerate((20, 35, 50), 1):
            feature(a, f"hvd_sector{index}", "Znak výseče", x, y)
    for x, y in ((27.5, 37), (42.5, 37), (27.5, 47), (42.5, 47)):
        feature(a, "hvd_beamstrip", "Mosazné značení hranice výsečí", x, y)
    cover(a, [(14.4, 37.5), (55.7, 36), (22.5, 41.7), (46.6, 41.7), (25.5, 49), (44.3, 49)], 337)
    rail(a, [(12.3, 35), (57.7, 35), (13, 43.8), (57, 43.8)], 90)
    rail(a, [(23, 57.2), (47, 57.2)])
    for x, y in ((23, 19), (47, 19), (14, 48), (56, 48), (27.3, 56), (42.7, 56)):
        lantern(a, x, y)
    fixture(a, [(125, "Prapor přísahy", 27, 54, 180), (126, "Prapor návratu", 43, 54, 180),
                (453, "Stráž při lucerně", 24, 55, 178), (453, "Stráž při lucerně", 46, 55, 182)])
    return a


def areas(art):
    zones = [make(art) for make in (mountain, halls, workshops, dome, steps, walks, gate, summit)]
    for area in zones:
        for trigger in area.triggers:
            if trigger.value("Type") == 1:
                feature(area, "hvd_threshold", "Kamenný práh cesty",
                        trigger.value("XPosition"), trigger.value("YPosition"))
    return zones
