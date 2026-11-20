"""The observatory, the upper terraces and their concealed branches."""

from aurora import bite, flt, integer, ref
from gateart import GATE, SHUTTER, SOCKETS
from interiors import TILESET, tile_assignments
from lightart import LAST_LANTERN, LAST_TOWER, REFRACTOR, STAIR_PORTAL
from routes import transition
from workart import LAB_MIRROR, LAB_SCREEN, LAB_SOURCE
from world import Area, color, variables


def scene(art, key, title, tileset, size, rooms, purpose, *,
          ambient, diffuse, fog, sky=0, music=49, wind=67, rises=(), stair_columns=None, tiles=None):
    area = Area(key, title, tileset, *size, rooms, purpose, special_tiles=tiles or {},
                rises=rises, stair_columns=stair_columns or {})
    area.art = art
    area.lighting.update(IsNight=bite(1), SkyBox=bite(sky), MoonFogAmount=bite(fog),
                         FogClipDist=flt(98.0 if sky else 48.0),
                         Grass_Density=flt(0.0),
                         MoonAmbientColor=color(*ambient), MoonDiffuseColor=color(*diffuse),
                         MoonFogColor=color(*(30, 40, 83) if sky else (19, 24, 42)),
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
              ambient=(91, 108, 149), diffuse=(175, 188, 219), fog=2, sky=4, music=59, wind=31,
              tiles={(2, 1): (68, 0), (2, 2): (208, 1), (3, 2): (208, 3),
                     (3, 3): (65, 0), (3, 4): (65, 0), (3, 5): (65, 0), (3, 6): (68, 2)})
    a.point("hvd_start", 23, 16, 82, "Nocleh pod kopulí")
    a.point("hvd_rim_halls", 40, 47, 270)
    a.point("hvd_rim_works", 52, 24, 180)
    transition(a, "Dovnitř hvězdárny", "hvt_rim_halls", "hvd_halls_in")
    transition(a, "Spodní servisní lávka", "hvt_rim_works", "hvd_works_rim", require="hvd_work_link")
    feature(a, "hvd_octagon", "Hvězdárna druhého nebe", 40, 60)
    feature(a, "hvd_quarry", "Servisní schodiště v horském zářezu", 58.45, 24, bearing=270)
    rail(a, [(32, 48), (48, 48)])
    lantern(a, 35.9, 51)
    lantern(a, 44.1, 51)
    a.find("hvd_book_camp", 21.43, 22.58, height=.89, clue=1)
    a.stash(7, "Výpravní bedna", 20.7, 19.98, "hvd_supply",
            text="Společná výstroj a zásoby pro výpravu z horského noclehu.")
    a.prop(58, "Ohniště v závětří", 17.85, 15.5, action="rest", tag="hvd_campfire")
    a.prop(318, "Mapa výprav", 21.06, 23.15, z=.88)
    a.prop(87, "Výstraha hlídky", 28.9, 25.8, action="read",
           text="U napnutých praporků se drž při kameni. Průlez na dílenskou lávku se otevírá od dílny.")
    feature(a, "hvd_dial", "Pult nové výpravy", 11.75, 15.2, action="reset", tag="hvd_reset",
           text="Družina se musí sejít u noclehu. Druhé použití vypraví novou hlídku.")
    fixture(a, [
        (434, "Plátěný nocleh", 15, 25, 180), (51, "Svázaná lůžka", 15.3, 23.1, 90),
        (108, "Suché dřevo", 15.3, 16.3, 12), (178, "Lavice u ohniště", 19.6, 15.8, 90),
        (97, "Stůl výpravy", 21.06, 22.78, 90), (49, "Zásobní sud", 11.9, 23, 0),
        (174, "Závěj u plátna", 12.2, 27.9, 65), (122, "Praporek poryvů", 32.8, 29.1, 10),
        (123, "Praporek při skále", 47.1, 30, 30), (410, "Skalní stěna", 30, 37, 65),
        (408, "Prasklý skalní blok", 48.2, 39, 20), (336, "Zlomený mezník", 32, 44, 0),
        (255, "Sníh pod kopulí", 49, 57, 10), (408, "Suti při zdi", 28, 56, 0),
        (463, "Vyschlý sud u průlezu", 55, 27, 35),
    ])
    light(a, 17.85, 15.5, 15109, 1.3)
    cover(a, [(31.9, 32.1), (41.2, 33.2), (31.5, 39.5)], 407)
    a.trap("Poryv mezi bradly", "hvd_wind", (35, 27, 47, 35), hazard=1)
    a.mob("hvd_strhavac", 40, 38)
    a.mob("hvd_vrhac", 47, 45)
    return a


def halls(art):
    a = scene(art, "hvd_halls", "Chodby clon", TILESET, (7, 7), [(0,0,7,7)],
              "Příjmová síň, úzká paprsková chodba a archiv při severní obslužné trase.",
              ambient=(79,88,118), diffuse=(148,158,200), fog=0, music=50, wind=67,
              tiles=tile_assignments("hvd_halls"))
    a.point("hvd_halls_in",17.8,13.55,90)
    a.point("hvd_study_secret",22.9,57.35,90)
    a.point("hvd_halls_study",21.0,53.15,260)
    transition(a, "Za zadní stěnu archivu","hvt_halls_study","hvd_study_in",
                 require="hvd_study_open")
    feature(a,"hvd_wallring","Mosazná zarážka police",19.65,55.45,action="study_pin",tag="hvd_study_pin",
            text="U spodní hrany kalibračních tabulek je zasazený mosazný čep. Když ho nadzvedneš, povolí táhlo u zadní stěny.")
    a.point("hvd_halls_works",12.65,44.95,0)
    a.point("hvd_halls_dome",55.5,36.65,270)
    transition(a, "Ven na římsu","hvt_halls_rim","hvd_rim_halls")
    transition(a, "K dílnám","hvt_halls_works","hvd_works_in")
    transition(a, "Do kopule","hvt_halls_dome","hvd_dome_in")
    for i,x in enumerate((28,35,42),1):
        a.point(f"hvd_hall_eye{i}",x,15,90)
        feature(a,"hvd_ray_case","Nástěnné vysílače clony",x,15)
        a.trap("Pole clony " + str(i),f"hvd_hallray{i}",(x-1.20,12.62,x+1.20,17.38),
               hazard=2,flag="hvd_hall_off",axis=1)
        light(a,x,16.92,15107,1.54)
    feature(a,"hvd_dial","Pojistka paprskové chodby",21.83,18.77,action="disarm",
            tag="hvd_ray_lock",flag="hvd_hall_off",skill=15,
            text="Uzavírá clony všech tří nástěnných vysílačů v paprskové chodbě. Rozebranou pojistku lze seřídit podle sešitu v dolní dílně nebo zneškodňováním pastí 15.")
    a.find("hvd_book_halls",9.50,13.9,height=.88,bearing=78)
    fixture(a,[(97,"Stůl výpravčího",9.08,14.16,90),
               (287,"Lavice u skříní s filtry",62.70,32.8,90)])
    for x,y in ((20.65,11.6),(19.8,45.1),(51.2,19.4),(59.7,35.9)):
        lantern(a,x,y)
    for x,y in ((20.9,48.3),(49.5,23.0),(61.35,26.8),(50.45,34.9)):
        feature(a,"hvd_crate","Bedna s výměnnými filtry",x,y,cover=1)
    for creature,x,y in (("hvd_strhavac",31,15),("hvd_vrhac",46,15),
                          ("hvd_spradac",54,26),("hvd_strhavac",57,34),("hvd_vrhac",16,42.4)):
        a.mob(creature,x,y)
    return a


def workshops(art):
    a = scene(art, "hvd_works", "Dílny a servisní lávka", "tcm02", (6, 8),
              [(1, 1, 4, 2), (1, 5, 5, 7)],
              "Servisní dvůr s optickou zkouškou a dvojicí podest, mezi nimiž vede skutečný most.",
              ambient=(94, 112, 151), diffuse=(180, 192, 228), fog=1, sky=4, music=49, wind=202,
              tiles={(2, 2): (895, 0), (2, 3): (818, 0), (2, 4): (895, 2)})
    a.point("hvd_works_in", 25, 14.9, 90)
    a.point("hvd_work_lab", 17.1, 14.7, 90, "Dolní dílna · zkušebna s klíčem a zrcadlem")
    a.point("hvd_works_hp", 25, 55.4, 270)
    a.point("hvd_works_rim", 36, 15.5, 180)
    transition(a, "Do chodeb clon", "hvt_works_halls", "hvd_halls_works")
    for x in (22.0,28.0):
        feature(a,"hvd_bluepost","Mezník návratu do chodeb",x,10.9)
    transition(a, "Pod kopulí do hvězdárny", "hvt_works_dome", "hvd_dome_works")
    transition(a, "Starý servisní sestup", "hvt_works_rim", "hvd_rim_works",
                 flag="hvd_work_link")
    feature(a, "hvd_quarry", "Výstup na horskou římsu", 40.49, 15, bearing=270)
    cloudbed(a, 29, 34)
    fixture(a, [
        (97, "Zkušební stůl", 17, 16, 90), (456, "Výpočty odrazů", 16.3, 16.7, 0),
        (108, "Odložené díly rámů", 12.15, 17.9, 90), (48, "Kovadlina na rámy", 31.95, 15.88, 90),
        (63, "Vyhaslá výheň", 32.55, 12.9, 0),
        (336, "Odložená patka", 16, 56.7, 0),
    ])
    a.find("hvd_book_return", 17.39, 16.50, height=.88, bearing=81)
    a.find("hvd_book_optic", 17.37, 15.55, height=.88, bearing=97)
    a.stash(7, "Schránka na klíč správkyně", 15.14, 15.3, "hvd_keycase",
            text="Vedle pracovního stolu v ní správkyně nechala klíč od zamčeného pouzdra.")
    a.prop(447,"Pevné zrcadlo zkušebny",*LAB_MIRROR,bearing=130,tag="hvd_lab_mirror")
    feature(a,"hvd_lab_screen","Měřicí stupnice zkušebny",*LAB_SCREEN)
    a.stash(8, "Pouzdro s přenosným zrcadlem", 15.24, 17.65, "hvd_mirror_case", bearing=180,
            text="Pod západní stříškou u zkušebního stolu leží záložní zrcadlo do patice na Posledním stupni. Sešit na stole vysvětluje jeho použití.")
    feature(a,"hvd_lab_source","Spoušť zkušební optiky",*LAB_SOURCE,action="testbeam",tag="hvd_lab_switch",
            text="Vyšle vzorek světla přes pevné zrcadlo na měřicí stupnici. Rozsvítí správné rysky pro dvě clony v kopuli.")
    a.stash(7, "Pouzdro správkyně", 13.2, 15.55, "hvd_work_cache", key="hvd_workkey",
            text="Dolní dílna u západního okraje podesty. Klíč je ve schránce u pracovního stolu.")
    feature(a,"hvd_gong","Ozvučnice servisní lávky",27.85,52.9,action="chime",tag="hvd_work_chime",
            text="Ozvučnice udeří nejbližšího viditelného větrného elementála do 18 metrů. Na každou vlnu nepřátel má jeden úder.")
    feature(a, "hvd_sealstand", "Schránka údržby · Kotva", 18, 57, action="seal", seal=1, tag="hvd_anchor_seal")
    for x, y in ((22.4, 19.2), (28, 49), (12.5, 54), (46.2, 58.2)):
        lantern(a, x, y)
    cover(a, [(22, 52.8), (37.0, 56.5)], 337)
    for creature, x, y in (("hvd_spradac", 20.5, 54), ("hvd_strhavac", 29.5, 56), ("hvd_vrhac", 39, 54)):
        a.mob(creature, x, y)
    return a


def dome(art):
    a = scene(art,"hvd_dome","Kopule druhého nebe",TILESET,(6,6),[(0,0,6,6)],
              "Měřicí sál, obslužné výklenky a průchody v nosném zdivu kopule.",
              ambient=(92,103,137),diffuse=(178,184,217),fog=0,music=27,wind=68,
              tiles=tile_assignments("hvd_dome"))
    a.point("hvd_dome_in",30,19.65,90)
    a.point("hvd_dome_works",16.65,26,0)
    a.point("hvd_dome_steps",30,43.15,270)
    a.point("hvd_dome_short",43.35,26,180)
    a.point("hvd_dome_study",43.0,14.64,180)
    a.point("hvd_dome_secret",46.82,14.625,0)
    transition(a, "Zpět do komory správkyně","hvt_dome_study","hvd_study_dome",
                 require="hvd_study_link")
    a.point("hvd_optic_gate",*STAIR_PORTAL,90)
    a.point("hvd_short_lock",50.66,26.08,0)
    transition(a, "Do chodeb clon","hvt_dome_halls","hvd_halls_dome")
    transition(a, "Na lávku do dílny","hvt_dome_works","hvd_works_hp")
    transition(a, "Schody do nebe","hvt_dome_steps","hvd_steps_in",require="hvd_aligned")
    transition(a, "Zkratka do předbraní","hvt_dome_short","hvd_gate_short",
                 require="hvd_shortcut")
    feature(a,"hvd_starmap","Mosazná mapa dvojí oblohy",*REFRACTOR)
    feature(a,"hvd_plinth","Prasklý refraktor",*REFRACTOR,tag="hvd_refractor",action="optics",
            text="Mosazné rysky u západního a východního ovladače jsou II a III. Potvrď obě polohy u refraktoru.")
    feature(a,"hvd_console","Západní clona · cílová ryska II",21,29,action="dial",dial=1,tag="hvd_dial_w")
    feature(a,"hvd_console","Východní clona · cílová ryska III",39,29,action="dial",dial=2,tag="hvd_dial_e")
    feature(a,"hvd_sector2","Cílová ryska II",21,27.4)
    feature(a,"hvd_sector3","Cílová ryska III",39,27.4)
    feature(a,"hvd_logstand","Pozorovací stolec s deníkem",14.02,32.31,bearing=90)
    a.find("hvd_book_dome",14.43,32.21,height=.88,bearing=77)
    feature(a,"hvd_wallring","Uzávěr schodiště z Předbraní",46.68,28.96,action="read",bearing=180,
            text="Sestup je jištěný závorou nahoře. V protější strážnici Předbraní se průchod otevírá z druhé strany.")
    a.prop(447,"Pevné zrcadlo u severní štěrbiny",25.3,44.72,bearing=180)
    light(a,30,32.8,15110,3.2)
    a.trap("Zpětný výboj refraktoru","hvd_domeray",(26,28,34,35),hazard=0)
    return a


def steps(art, flight):
    a = scene(art, "hvd_steps", "Schody do nebe", "tcm02", (7, 9),
              [(1,1,6,8), (0,2,7,3), (0,4,7,5), (0,6,7,7)],
              "Tři široké lety po kamenné ose, měřicí podesta a vyvýšená bouřná hlídka.",
              ambient=(100,115,159), diffuse=(206,209,242), fog=1, sky=4, music=49, wind=202,
              rises=(3,5,7), stair_columns={2:(3,),4:(3,),6:(3,)},
              tiles={(3,row):(flight,0) for row in (2,4,6)})
    a.point("hvd_steps_in",35,15.0,90)
    a.point("hvd_steps_walks",35,75.1,270,"Horní podesta schodů")
    a.point("hvd_steps_eave",18.25,16.66,0)
    a.point("hvd_steps_eaveup",51.35,54.1,180)
    a.point("hvd_eave_secret",15.62,16.65,0)
    a.point("hvd_eavetop_door",54.90,54.10,0)
    transition(a, "Sestoupit do kopule","hvt_steps_dome","hvd_dome_steps")
    transition(a, "K visutým ochozům","hvt_steps_walks","hvd_walks_in")
    transition(a, "Pod západní opěru","hvt_steps_eave","hvd_eave_in",
                 require="hvd_eave_open")
    transition(a, "Na servisní římsu","hvt_steps_eaveup","hvd_eave_top",
                 require="hvd_eave_open")
    feature(a,"hvd_wallring","Západka protizávaží",19.46,19.62,action="eave_pin",tag="hvd_eave_pin",
            text="Od táhla u opěry vede řetěz dolů za západní balustrádu. Západku brzdí napnutá pojistka.")
    feature(a,"hvd_storm_inlay","Rozeta bouřné komory",35,54.85)
    feature(a,"hvd_sealstand","Hnízdo Pečeti křídla",45.1,56.5,action="seal",seal=2,tag="hvd_wing_seal")
    feature(a,"hvd_gong","Ozvučnice bouřné podesty",24.75,55.3,action="chime",tag="hvd_steps_chime",
            text="Rozkmitá nejbližší viditelné větrné tělo do 18 metrů. Pro každou vlnu vydrží jeden úder.")
    a.point("hvd_storm_center",35,54.85)
    a.find("hvd_book_steps",27.35,15.48,height=.88,clue=2)
    a.prop(97,"Stolek obsluhy prvního schodu",27.01,15.5,bearing=90)
    cover(a,[(29.85,51.9),(41.15,51.9),(28.05,57.4),(42.4,58.3)],337)
    a.mob("hvd_vir",35,54.85,seal=2,elite=1)
    a.mob("hvd_spradac",43.65,54.26)
    a.mob("hvd_strhavac",36.7,36.8)
    a.mob("hvd_vrhac",37.4,74.5)
    return a


def study(art):
    a = scene(art,"hvd_study","Skrytá komora správkyně",TILESET,(2,3),[(0,0,2,3)],
              "Samostatná kalibrační pracovna, malá předsíň a zalomený průlez do kopule.",
              ambient=(85,78,98),diffuse=(174,165,198),fog=0,music=50,wind=68,
              tiles=tile_assignments("hvd_study"))
    a.point("hvd_study_in",8.46,6.25,90)
    a.point("hvd_study_dome",17.25,21.45,230)
    a.point("hvd_comm_secret",15.26,18.55,0)
    transition(a, "Zpět ke skladům clon","hvt_study_halls","hvd_halls_study")
    transition(a, "Za zadní clonou do kopule","hvt_study_dome","hvd_dome_study",
                 require="hvd_study_link")
    feature(a,"hvd_wallring","Uzávěr zadní clony",13.15,20.73,action="study_turn",tag="hvd_study_turn",
            text="Táhlo u severní stěny zdvihne uzávěr krátké servisní chodby do kopule.")
    a.stash(7,"Kufřík na vyřazené čočky",4.44,18.96,"hvd_study_cache",bearing=90)
    feature(a,"hvd_writedesk","Písařský stůl správkyně",5.05,12.66,bearing=90)
    return a


def eave(art, flight):
    a = scene(art,"hvd_eave","Římsa pod Schody do nebe","tcm02",(5,9),
              [(1,1,4,2),(1,5,4,8),(0,6,5,7)],
              "Spodní servisní můstek pod opěrami a oddělený výlez na bouřnou podestu.",
              ambient=(80,99,135),diffuse=(160,184,219),fog=2,sky=4,music=49,wind=202,
              rises=(7,),stair_columns={6:(2,)},
              tiles={(2,2):(895,0),(2,3):(818,0),(2,4):(895,2),(2,6):(flight,0)})
    a.point("hvd_eave_in",25,15.3,90)
    a.point("hvd_eave_top",25,75.8,270)
    transition(a, "Pod západní opěru schodů","hvt_eave_steps","hvd_steps_eave")
    transition(a, "Východ na bouřnou podestu","hvt_eave_up","hvd_steps_eaveup")
    feature(a,"hvd_cloister","Nízký vstup pod schody",25,11.8)
    feature(a,"hvd_cloister","Výlez k bouřné podestě",25,80.45)
    a.trap("Poryv pod obloukem","hvd_eave_wind",(23,30,27,42),hazard=1,flag="hvd_eave_safe",axis=1)
    feature(a,"hvd_wallring","Pojistka větrné klapky",29.6,18.9,action="eave_brake",tag="hvd_eave_brake",
            text="Ruční pojistka drží klapku u mostu. Při zajištění odvede poryv do spodního kamenného kanálu.")
    a.stash(7,"Pouzdro za opěrou",34.28,56.8,"hvd_eave_cache",bearing=30)
    return a


def walks(art, flight):
    tiles = {}
    for x in (2, 5):
        tiles.update({(x, 2): (895, 0), (x, 3): (818, 0), (x, 4): (895, 2)})
    tiles[4,7] = flight,0
    a = scene(art, "hvd_walks", "Visuté ochozy", "tcm02", (8, 10),
              [(1,1,7,2), (1,5,4,6), (5,5,7,6), (1,6,7,7), (0,7,8,8), (3,8,6,9)],
              "Dvě ohrazená ramena nad propastí a vlastní schodiště k Předbraní.",
              ambient=(98, 116, 168), diffuse=(182, 204, 239), fog=2, sky=4, music=49, wind=202,
              rises=(8,), stair_columns={7:(4,)}, tiles=tiles)
    a.point("hvd_walks_in", 40, 15, 90)
    a.point("hvd_walks_gate", 45, 83.80, 270)
    transition(a, "Zpět na bouřnou podestu", "hvt_walks_steps", "hvd_steps_walks")
    transition(a, "Do předbraní", "hvt_walks_gate", "hvd_gate_in")
    a.stash(7,"Kožený kufřík staré hlídky",68.72,62.95,"hvd_walk_cache",bearing=60)
    cloudbed(a, 40, 38)
    feature(a, "hvd_sealstand", "Podstavec Pečeti kopí", 19, 57.7, action="seal", seal=3, tag="hvd_spear_seal")
    feature(a, "hvd_sealstand", "Podstavec Pečeti lucerny", 63, 57.7, action="seal", seal=4, tag="hvd_lamp_seal")
    for x, y in ((21.8, 18.5), (28.2, 18.5), (59.0, 17.9), (52, 51.5),
                 (19.5, 53), (46, 63), (34, 63)):
        lantern(a, x, y, 15107 if x < 30 else 15113)
    fixture(a, [(125, "Znak kopí", 19, 62, 180),
                (91, "Kamenný kopiník", 17.5, 61.4, 180), (92, "Kamenný světlonoš", 65, 61.4, 180),
                (126, "Znak lucerny", 63, 62, 180), (287, "Lavice stráže", 67.8, 65.1, 0)])
    cover(a, [(17, 54), (30, 57), (53, 55), (65, 53), (50.5, 59.8)], 337)
    for creature, x, y, sign in (("hvd_kopi", 22, 57, 3), ("hvd_strhavac", 26, 51, 0),
                                 ("hvd_vrhac", 32, 57, 0), ("hvd_svetlonos", 61, 56, 4),
                                 ("hvd_spradac", 50, 56, 0), ("hvd_strhavac", 56, 52, 0)):
        a.mob(creature, x, y, seal=sign, elite=bool(sign))
    return a


def gate(art, flight, *, test_guide):
    a = scene(art, "hvd_gate", "Předbraní Horních sfér", "tcm02", (7, 7),
              [(1, 1, 6, 4), (2, 4, 5, 6), (0, 4, 7, 5)],
              "Optický dvůr se třemi sloupy, závorou a schodištěm k Bráně tří paprsků.",
              ambient=(111, 124, 172), diffuse=(204, 214, 251), fog=1, sky=4, music=27, wind=30,
              rises=(5,), stair_columns={4: (3,)}, tiles={(3,4): (flight,0)})
    a.point("hvd_gate_in", 35, 16.3, 90)
    a.point("hvd_gate_top", 35, 50.5, 270)
    a.point("hvd_gate_short", 52, 22.0, 180)
    a.point("hvd_gate_rest",54,16,90,"Odpočívárna stráže")
    a.point("hvd_final_gate", *GATE, 90)
    transition(a, "Zpět na visuté ochozy", "hvt_gate_walks", "hvd_walks_gate")
    transition(a, "Sestup do kopule", "hvt_gate_dome", "hvd_dome_short", flag="hvd_shortcut")
    transition(a, "Vstoupit na Poslední stupeň", "hvt_gate_top", "hvd_top_in",
                 require="hvd_gate_open")
    cloudbed(a, 35, 38)
    feature(a, "hvd_gatearch", "Kamenné ostění Brány tří paprsků", *GATE, tag="hvd_stone_frame")
    feature(a, "hvd_gateinlay", "Vedení optické soustavy", 35, 29.6)
    feature(a, "hvd_cloister", "Ostění servisního sestupu", 56.15, 22, bearing=90)
    positions = (*SOCKETS, SHUTTER)
    names = ("Západní sloup", "Střední sloup", "Východní sloup", "Závora převodu")
    for slot, ((x, y), name) in enumerate(zip(positions, names), 1):
        a.stash(a.art["hvd_gate_pod" if slot <= 3 else "hvd_clamp_pod"], name, x, y, f"hvd_socket_{slot}",
                text="Otevři a přesuň do patice jednu pečeť z vlastní výpravy. Pečeť můžeš opět vyjmout.")
        a.places[-1].fields.update(VarTable=variables(slot=slot), OnInvDisturbed=ref("hvd_slot_inv"))
        if slot <= 3:
            feature(a, "hvd_filter_arm", f"{name} · páčka clony", x + .82, y - .12, z=a.z_at(y) + .38,
                    action="gate_filter", slot=slot, tag=f"hvd_filter_{slot}",
                    text="Přestavuje clonu mezi Srpkem, Hvězdou a Sluncem. Znak se ukáže na čele sloupu.")
    feature(a, "hvd_gatepull", "Spoušť tří paprsků", 37.05, 37.45, action="gate", tag="hvd_gate_control",
            text="Spojí světlo tří seřízených sloupů, pokud správná pečeť drží závoru převodu.")
    a.prop(240, "Reliéf přísahy", 46.0, 19.1)
    feature(a, "hvd_register", "Přijímací místo písaře pečetí", 44.04, 21.02)
    a.find("hvd_book_gate", 44.21, 20.68, height=.88, clue=3)
    feature(a, "hvd_dial", "Mechanismus výměny ztracených pečetí", 23.9, 21.05,
            action="recap", tag="hvd_recap")
    if test_guide:
        a.stash(7, "TEST · Pouzdro s řešením brány", 23.55, 17.50, "hvd_test_case",
                text="Zkušební list obsahuje přesnou sestavu pro tuto výpravu.")
    a.prop(58, "Odpočinek ve strážnici", 54, 16, action="rest")
    a.stash(8, "Schránka poslední hlídky", 52, 34.4, "hvd_guard_cache")
    feature(a, "hvd_dial", "Zakrytí proudu ve strážnici", 48.1, 30.6, action="disarm",
            flag="hvd_chest_off", skill=15, tag="hvd_guard_lock")
    a.trap("Závora světla ve strážnici", "hvd_gatechest", (50, 31, 55, 36), hazard=2, flag="hvd_chest_off")
    a.trap("Výboj optických sloupů", "hvd_gatespark", (26, 24, 44, 36), hazard=0)
    fixture(a, [(453, "Socha navracejícího světlo", 28.9, 53.0, 178),
                (453, "Socha vítající příchozí", 41.1, 53.0, 182),
                (125, "Znak nebeské hlídky", 27.3, 55.5, 0), (126, "Znak návratu", 42.7, 55.5, 0),
                (51, "Složené pokrývky stráže", 54.6, 14.5, 90), (287, "Lavice ve strážnici", 51.0, 18.65, 0),
                (311, "Skříň na výstroj", 55.9, 36.3, 90), (49, "Olej pod policí", 56, 32, 0),
                (91, "Starý člen hlídky", 17, 30, 100)])
    for x, y in ((21, 28), (46.5, 26.5), (30, 38.6), (40, 38.6), (31, 51.5), (39, 51.5)):
        lantern(a, x, y)
    for x, y, bearing in ((24.5,34.0,25),(44.4,35,335),(47,28.6,255)):
        feature(a, "hvd_raybaffle", "Stínicí blok optického dvora", x, y, bearing=bearing, cover=1)
    return a


def summit(art, flight):
    a = scene(art, "hvd_top", "Poslední stupeň", "tcm02", (7, 7),
              [(2, 1, 5, 3), (1, 3, 6, 5), (2, 5, 5, 6), (0, 2, 7, 3)],
              "Tři povrchem odlišené výseče strážní podesty a vyzdvižené stanoviště poslední lucerny.",
              ambient=(93, 105, 147), diffuse=(223, 214, 247), fog=1, sky=4, music=49, wind=30,
              rises=(3,), stair_columns={2: (3,)}, tiles={(3,2): (flight,0)})
    a.point("hvd_top_in", 35, 15.8, 90)
    a.point("hvd_top_mirror", 44.6, 17.8, 270, "Patice zkušebního zrcadla pod schody")
    a.point("hvd_boss_home", 35, 50.82, 270)
    a.point("hvd_add_west", 17.5, 43.3, 315)
    a.point("hvd_add_east", 52.5, 43.3, 225)
    a.point("hvd_summit_exit", 35, 58.5, 90)
    transition(a, "Ústup do předbraní", "hvt_top_gate", "hvd_gate_top")
    transition(a, "Návrat na římsu", "hvt_top_rim", "hvd_start", require="hvd_won")
    cloudbed(a, 35, 37)
    feature(a, "hvd_starmap", "Návratová rozeta", 35, 47.1)
    a.prop(97, "Stůl stráže na Posledním stupni", 25.5, 18.8)
    a.find("hvd_book_top", 25.78, 18.48, height=.88)
    a.trap("Ithrenovo stanoviště", "hvd_boss_start", (13, 30, 57, 55), hazard=3)
    feature(a, "hvd_sealstand", "Patice zkušebního zrcadla", 44.6, 17.8, action="mount", tag="hvd_mirror_mount")
    feature(a,"hvd_lighttower","Věž návratového objektivu",*LAST_TOWER[:2],z=LAST_TOWER[2])
    feature(a,"hvd_signallamp","Poslední lucerna · ruční clona",*LAST_LANTERN,
            action="shutter",tag="hvd_final_sh",
            text="Odraz z věže dopadá přímo do lucerny. Po doznění bojových výbojů stáhni mosaznou clonu.")
    a.point("hvd_signal_home",*LAST_LANTERN,90)
    a.stash(8, "Schránka · Plášť dvojí oblohy", 28.4, 55.5, "hvd_cloak_reward",
            key="hvd_clona", reward=True, text="Pečeť povolí, až utichne falešný odraz lucerny.")
    a.stash(8, "Schránka · Spona strážce", 41.6, 55.5, "hvd_badge_reward",
            key="hvd_clona", reward=True, text="Pečeť povolí, až utichne falešný odraz lucerny.")
    for y in (33.5, 39.0, 46.8, 52.7):
        for index, x in enumerate((20, 35, 50), 1):
            feature(a, f"hvd_sector{index}", "Znak výseče", x, y)
    for x, y in ((27.5, 37), (42.5, 37), (27.5, 47), (42.5, 47)):
        feature(a, "hvd_beamstrip", "Mosazné značení hranice výsečí", x, y)
    cover(a, [(14.4, 37.5), (55.7, 36), (22.5, 41.7), (46.6, 41.7), (25.5, 49), (44.3, 49)], 337)
    for x, y in ((23, 19), (47, 19), (14, 48), (56, 48)):
        lantern(a, x, y)
    fixture(a, [(125, "Prapor přísahy", 27, 54, 180), (126, "Prapor návratu", 43, 54, 180),
                (453, "Stráž při lucerně", 24, 57.45, 178), (453, "Stráž při lucerně", 46, 55, 182)])
    return a


def areas(art, flight, *, test_guide=False):
    zones = [
        mountain(art), halls(art), workshops(art), dome(art), steps(art, flight),
        walks(art, flight), gate(art, flight, test_guide=test_guide), summit(art, flight), study(art), eave(art, flight),
    ]
    return zones
