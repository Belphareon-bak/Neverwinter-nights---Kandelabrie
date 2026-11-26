"""Build the observatory's two circuits on their shared Toolset plan."""

from collections import defaultdict

from aurora import bite, flt, integer, ref
from gateart import GATE, SHUTTER, SOCKETS
from interiors import TILESET, tile_assignments
from lightart import (ADIT_CENTER, LAST_LANTERN, LAST_TOWER, LANTERN_SINK, LANTERN_TURN,
                      REFRACTOR, STAIR_PORTAL)
from navrh_v21 import ACCESS_DOOR, ACCESS_SIGN, OUTLET, PRISM, R1_SAFE_RETURN, REPAIR_PASSAGES, SHRINES, SOURCE
from plan import (ENTRY_X, GATE_CLERK, GATE_REST, GATE_WEST_BAY, RIM_ENTRY_X, STORM_CABINET,
                  TOP_COLUMNS, TOP_GUARDS, TOP_MIRROR, WING_POST, WORK_STATIONS, ZONES,
                  check_plan)
from routes import place_transitions
from workart import LAB_MIRROR, LAB_SCREEN, LAB_SOURCE
from sunrepair import furnish as furnish_solar_service
from world import Area, color, variables


def scene(art, key, title, tileset, purpose, *,
          ambient, diffuse, fog, sky=0, music=49, battle=71, wind=67, wind_volume=57,
          flight=None, tiles=None):
    plan = ZONES[key[4:]]
    special_tiles = dict(tiles or {})
    for x in plan.bridges:
        col = x // 10
        special_tiles.update({(col, 2): (895, 0), (col, 3): (818, 0), (col, 4): (895, 2)})
    stair_columns = defaultdict(list)
    for col, row in plan.stairs:
        stair_columns[row].append(col)
        special_tiles[col, row] = flight, 0
    area = Area(key, title, tileset, *plan.size, plan.tiles, purpose, special_tiles=special_tiles, relief=plan.relief,
                rises=tuple(row + 1 for row in sorted(stair_columns)), stair_columns=dict(stair_columns))
    area.art = art
    area.lighting.update(IsNight=bite(1), SkyBox=bite(sky), MoonFogAmount=bite(fog),
                         FogClipDist=flt(98.0 if sky else 48.0),
                         Grass_Density=flt(0.0),
                         MoonAmbientColor=color(*ambient), MoonDiffuseColor=color(*diffuse),
                         MoonFogColor=color(*(30, 40, 83) if sky else (19, 24, 42)),
                         ShadowOpacity=bite(38),
                         ChanceSnow=integer(48 if key in ("hvd_camp", "hvd_rim") else 0))
    area.soundscape.update(MusicNight=integer(music), MusicDay=integer(music), MusicBattle=integer(battle),
                           AmbientSndNight=integer(wind), AmbientSndDay=integer(wind),
                           AmbientSndDayVol=integer(wind_volume), AmbientSndNitVol=integer(wind_volume))
    return area


def feature(area, asset, name, x, y, **settings):
    return area.prop(area.art[asset], name, x, y, **settings)


def fixture(area, rows):
    for appearance, name, x, y, bearing in rows:
        area.prop(appearance, name, x, y, bearing=bearing)


def wind_pack(area, group, title, approaches, positions, *, leash, bearing=270):
    area.encounter(group, title, *approaches)
    if area.key in ("hvd_steps", "hvd_walks"):
        templates = ("hvd_elit_vrhac", "hvd_elit_strh", "hvd_elit_sprad", "hvd_elit_strh")
    else:
        templates = ("hvd_vrhac", "hvd_strhavac", "hvd_spradac", "hvd_strhavac")
    for resource, (x, y) in zip(templates, positions, strict=True):
        area.mob(group, resource, x, y, leash=leash, bearing=bearing)


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


def chasm_gust(area, name, x, y, interval):
    area.sound("hvd_sfx_gust", name, "as_wt_gustchasm1", x, y, radius=11.0,
               volume=59, elevation=0.8, interval=interval, variation=9000)


def camp(art):
    a = scene(art, "hvd_camp", "Horský tábor", "tts02",
              "Kamenný nocleh, společné ohniště, zásobárna a jediná horská cesta.",
              ambient=(95,111,148), diffuse=(199,209,233), fog=2, sky=4, music=92, wind=30, wind_volume=27,
              tiles={(2, row): (116, 0) for row in (1,2,3)})
    a.point("hvd_start",27,16,82,"Tábor · počátek výpravy")
    a.find("hvd_book_camp",17.57,24.32,height=.88,clue=1)
    a.stash(7,"Výpravní bedna",37.67,24.14,"hvd_supply",
            text="Společná výstroj a zásoby pro výpravu z horského noclehu.")
    fire = (20.9, 15.36)
    a.prop(58, "Ohniště v závětří", *fire, action="rest", tag="hvd_campfire")
    a.sound("hvd_sfx_fire", "Praskání táborového ohně", "al_cv_firecamp1", *fire,
            radius=10.0, volume=70, elevation=0.45)
    feature(a,"hvd_dial","Pult nové výpravy",22.78,23.68,action="reset",tag="hvd_reset",
            text="Družina se musí sejít u noclehu. Druhé použití vypraví novou hlídku.")
    fixture(a, [
        (51,"Lůžka výpravy",14.90,23.43,90), (51,"Náhradní pokrývky",19.77,23.83,270),
        (108,"Dřevo v dosahu ohniště",16.7,16.4,12),
        (178,"Lavice po větru",18.42,14.53,0), (178,"Lavice obrácená k ohni",20.42,17.51,180),
        (97,"Stůl výpravy pod zadní stěnou",17.58,24.34,0),
        (49,"Zásobní sud",40.95,23.09,0),
    ])
    light(a,*fire,15109,1.3)
    return a


def mountain(art):
    a = scene(art, "hvd_rim", "Výstupová římsa", "tts02",
              "Horská stezka stoupá k jediné veřejné bráně hvězdárny. Zadní svah obrůstají skalní vrstvy.",
              ambient=(91,108,149), diffuse=(175,188,219), fog=2, sky=4, music=59, wind=31)
    a.point("hvd_fork",26,11.7,90,"Rozcestí · dolní okruh 35–37")
    feature(a,"hvd_skyport","Jižní brána hvězdárny",RIM_ENTRY_X,38.30)
    a.prop(87,"Směrovník pod průčelím",24.68,17.80,bearing=19,action="read",
           text="Hvězdárna je za osvětlenou bránou nad stezkou. V síni se dej vlevo do dílen, nebo vpravo k obsluze clon.")
    fixture(a,[(122,"Návětrný praporek",25.76,17.22,10),
               (123,"Praporek při zdi",17.4,29,30),
               (336,"Zlomený mezník",12.5,21,0)])
    a.point("hvd_rim_cover_home",87.95,25,0)
    a.trigger("Závětří mezi skalami","hvd_scan_rim",(82.0,21.0,88.0,29.0),"hvd_zone",
              secret="hvd_secret_rim")
    feature(a,"hvd_rimbolt","Zapuštěná servisní západka",86.15,23.02,bearing=180,
            action="rim_latch",flag="hvd_secret_rim",tag="hvd_latch_outer",
            text="Ve spáře mezi kamenem a sněhem je hladký železný zub. Po zatlačení uvolní protizávaží desky.")
    return a


def halls(art):
    a = scene(art, "hvd_halls", "Chodby clon", TILESET,
              "Klenutá spojka s rozvaděčem tří větví a archivem.",
              ambient=(79,88,118), diffuse=(148,158,200), fog=0, music=50, wind=67,
              tiles=tile_assignments("hvd_halls"))
    spans = (
        ("Paprsková chodba",0,1,15,12.55,17.45,(28,35,42)),
        ("Stará filtrovna",1,0,49.85,47,52.7,(30.1,34.65)),
        ("Archiv clon",2,1,45,42.2,47.8,(40.8,28.2)),
    )
    index = 0
    for name,ray_mode,axis,center,low,high,stations in spans:
        for at in stations:
            index += 1
            x,y = (at,center) if axis else (center,at)
            bounds = (x-1.18,low,x+1.18,high) if axis else (low,y-1.18,high,y+1.18)
            a.point(f"hvd_hall_eye{index}",x,y,90 if axis else 180,branch=ray_mode+1)
            feature(a,"hvd_ray_case",f"{name} · dvojice clon",x,y,bearing=0 if axis else 90)
            a.trap(f"{name} · pásmo {index}",f"hvd_hallray{index}",bounds,
                   hazard=2,branch=ray_mode+1,axis=axis,ray_mode=ray_mode)
    feature(a,"hvd_clonpanel","Rozvaděč chodeb clon",13,23.96,action="read",tag="hvd_ray_lock",
            text="Zleva Paprsková chodba, Stará filtrovna a Archiv. Vybranou větev převezme záchyt ve spodní liště. "
                 "Její čočky zaklopí víčka a rozsvítí se příslušná kontrolka. Ostatní dvě větve zůstávají v provozu.")
    for x,code,label in ((11.29,1,"Paprsková chodba"),(13,2,"Stará filtrovna"),(14.71,3,"Archiv")):
        feature(a,"hvd_clon_knob",f"Rozvaděč · {label}",x,23.79,z=1.46,
                action="hall_switch",control=code,tag=f"hvd_hall_cmd{code}")
        a.point(f"hvd_hall_led{code}",x,23.76,90,z=2.87)
    a.point("hvd_hall_sink_home",13,23.84,90,z=.86)
    a.find("hvd_book_halls",12.05,12.12,height=.88,bearing=180)
    a.door('hvd_repairdoor','Kamenné dveře Filtrovny světla',*ACCESS_DOOR,key='hvd_ithrenkey',bearing=90)
    feature(a,'hvd_sunglyph','Značení zapečetěné Filtrovny',*ACCESS_SIGN,action='repair_door',
            text='Servis světla pro Poslední stupeň. Klíč od kamenných dveří nosí Ithren, strážce průchodu.')
    wind_pack(a,"clony","Průvan za první clonou",((22,12.5,26,17.5),(44,12.5,47,17.5)),
              ((31,14.4),(34.2,15.5),(36.9,13.9),(39.0,10.9)),leash=13,bearing=180)
    wind_pack(a,"filtry","Proudy za filtrovnou",((47,36.05,52.7,37.15),(46.8,42.2,49,47.8)),
              ((50.1,38.35),(53.1,40.3),(48.5,40.75),(51.6,43.0)),leash=11)
    wind_pack(a,"archiv","Hlídka kalibračních zápisů",((23,42.2,26.5,47.8),(8.8,46.4,24,48.6)),
              ((16.4,43.8),(14.2,46.6),(20.7,46.0),(21.3,41.6)),leash=11,bearing=90)
    return a


def light_service(art):
    a = scene(art, "hvd_service", "Světelný servis", TILESET,
              "Opravárenská Filtrovna a Sál skládání pod společným skalním zlomem.",
              ambient=(81,88,109), diffuse=(193,183,170), fog=0, music=82, wind=67,
              tiles=tile_assignments("hvd_service"))
    furnish_solar_service(a)
    light(a,*SOURCE,15113,height=3.15)
    a.sound("hvd_sfx_prism", "Hučení napájeného hranolu", "al_mg_ballmagic1", *PRISM,
            radius=8.0, volume=34, elevation=1.5, active=False)
    a.sound("hvd_sfx_outbell", "Tón potvrzeného světla u výstupu", "as_cv_bell1", *OUTLET,
            radius=34.0, volume=127, elevation=1.5, min_distance=9.0, active=False, loop=False)
    return a


def workshops(art, tiles):
    a = scene(art, "hvd_works", "Dílny a servisní lávka", "tcm02",
              "Klenutá vstupní síň, dvůr zkušebny a kovárny, servisní lávka a horní přijímací dvůr.",
              ambient=(94, 103, 133), diffuse=(183, 184, 205), fog=1, sky=4, music=49, wind=30, wind_volume=27,
              tiles=tiles)
    a.fixed_tiles = True
    a.point("hvd_entry",ENTRY_X,15.0,90,"Vstupní síň · Zkušebna vlevo, Chodby clon vpravo")
    feature(a,"hvd_wallchart","Rozpis stanovišť na severní stěně",56.18,19.46,action="read",
            text="Vlevo je Zkušebna. Za dílnami pokračuje servisní lávka na horní dvůr. Vpravo jsou Chodby clon. "
                 "Přes filtrovnu a archiv také dojdeš na horní dvůr.")
    a.point("hvd_work_lab", 17.1, 17.7, 90, "Zkušebna a zápisky optika")
    a.point("hvd_work_flow", 35.75, 17.55, 90, "Příjem materiálu a kovárna objímek")
    dispatch_x, dispatch_y = WORK_STATIONS['dispatch']
    a.point("hvd_work_ship", dispatch_x, dispatch_y-2.4, 90, "Přejímka a expedice ke Kopuli")
    a.sound("hvd_sfx_hoist", "Zavrzání navijáku pod napnutým lanem", "as_cv_woodframe1",
            dispatch_x, dispatch_y, radius=8.0, volume=83, elevation=1.3, min_distance=2.5,
            interval=17000, variation=6000)
    chasm_gust(a, "Poryv pod servisní lávkou", 25.0, 35.2, 21000)
    cloudbed(a, 29, 34)
    a.trap("Poryv při vstupu na dvůr","hvd_wind",(40,12.9,49,17.8),hazard=1)
    wind_pack(a,"dvur","Vítr mezi dvěma dílnami",((37.2,12.1,39.8,17.9),(22.31,17.4,27.66,19.55)),
              ((34.9,15.55),(32.0,16.45),(29.0,16.3),(31.0,13.05)),leash=12,bearing=0)
    wind_pack(a,"zkusebna","Poryvy ve Zkušebně",((22.6,11.3,25.0,17.3),),
              ((19.55,14.8),(16.6,15.5),(18.3,12.3),(21.37,12.0)),leash=9,bearing=0)
    fixture(a, [
        (48, "Kovadlina k vyrovnání objímek", *WORK_STATIONS["anvil"], 90),
        (63, "Vyhaslá výheň na objímky", *WORK_STATIONS["forge"], 0),
    ])
    feature(a,"hvd_writedesk","Pult optika v západním výklenku",*WORK_STATIONS["desk"],bearing=90)
    a.find("hvd_book_return", 13.07, 14.22, height=.88, bearing=81)
    a.find("hvd_book_optic", 13.13, 14.96, height=.88, bearing=97)
    a.stash(7, "Schránka na klíč správkyně", 14.33, 13.72, "hvd_keycase", bearing=90,
            text="Příruční skříňka na straně zápisového pultu obrácené k brusírně.")
    a.prop(447,"Pevné zrcadlo zkušebny",*LAB_MIRROR,bearing=130,tag="hvd_lab_mirror")
    feature(a,"hvd_lab_screen","Měřicí stupnice zkušebny",*LAB_SCREEN)
    a.stash(8, "Pouzdro s přenosným zrcadlem", 14.23, 16.90, "hvd_mirror_case", bearing=90,
            text="Vedle zápisového pultu leží zrcadlo do patice na Posledním stupni. Sešit optika popisuje jeho použití.")
    feature(a,"hvd_lab_source","Spoušť zkušební optiky",*LAB_SOURCE,action="testbeam",tag="hvd_lab_switch",
            text="Vyšle vzorek světla přes pevné zrcadlo na měřicí stupnici. Rozsvítí správné rysky pro dvě clony v kopuli.")
    a.stash(7, "Pouzdro správkyně", 12.58, 12.70, "hvd_work_cache", key="hvd_workkey",
            text="Západní roh brusírny. Klíč je v příruční schránce vedle zápisového pultu.")
    feature(a,"hvd_gong","Ozvučnice servisní lávky",27.85,52.9,action="chime",tag="hvd_work_chime",
            text="Ozvučnice udeří nejbližšího viditelného větrného elementála do 18 metrů. Na každou vlnu nepřátel má jeden úder.")
    feature(a, "hvd_sealstand", "Schránka údržby · Kotva", 18, 57, action="seal", seal=1, tag="hvd_anchor_seal")
    for x, y in ((22.4, 19.2), (28, 49), (12.5, 54), (46.2, 58.2)):
        lantern(a, x, y)
    wind_pack(a,"prijem","Přijímací dvůr nad lávkou",((22,50,28,53),(27.3,64.8,35.8,67),(43.4,52,47,58.1)),
              ((28.6,55.2),(31.9,56.4),(36.5,56.55),(40.1,55.85)),leash=16)
    return a


def dome(art):
    a = scene(art, "hvd_dome", "Kopule druhého nebe", TILESET,
              "Měřicí sál, obslužné výklenky a průchody v nosném zdivu kopule.",
              ambient=(92,103,137), diffuse=(178,184,217), fog=0, music=82, wind=68,
              tiles=tile_assignments("hvd_dome"))
    a.point("hvd_optic_gate",*STAIR_PORTAL,90)
    a.point("hvd_upper_note",31.4,51.0,90,"Výstup k hornímu okruhu 38–40")
    feature(a,"hvd_starmap","Mosazná mapa dvojí oblohy",*REFRACTOR)
    feature(a,"hvd_plinth","Prasklý refraktor",*REFRACTOR,tag="hvd_refractor",action="optics",
            text="V deníku u západní stěny je poslední měření. Nastav podle něj obě clony a vrať se k objektivu.")
    a.sound("hvd_sfx_dome", "Hučení seřízeného refraktoru", "al_mg_ballmagic1", *REFRACTOR,
            radius=9.0, volume=39, elevation=2.2, active=False)
    feature(a,"hvd_console","Západní clona",21,29,action="dial",dial=1,tag="hvd_dial_w")
    feature(a,"hvd_console","Východní clona",39,29,action="dial",dial=2,tag="hvd_dial_e")
    feature(a,"hvd_logstand","Pozorovací stolec s deníkem",14.02,32.31,bearing=90)
    a.find("hvd_book_dome",14.43,32.21,height=.88,bearing=77)
    feature(a,"hvd_dome_mirror","Pevné zrcadlo u severní štěrbiny",25.3,44.72)
    light(a,30,32.8,15110,3.2)
    a.trap("Zpětný výboj refraktoru","hvd_domeray",(26,28,34,35),hazard=0)
    return a


def steps(art, terrain):
    a = scene(art, "hvd_steps", "Schody do nebe", "tcm02",
              "Tři osmnáctimetrová ramena nesou podestu pozorovatelů a bouřnou podestu. Východní lávka vede na Ochozy.",
              ambient=(100,115,159), diffuse=(206,209,242), fog=1, sky=4, music=128, wind=30, wind_volume=35,
              flight=terrain.flight)
    a.fixed_tiles = True
    a.special_tiles = terrain.decks['steps']
    chasm_gust(a, "Poryv na okraji dolního ramene", 38.55, 18.6, 23000)
    chasm_gust(a, "Poryv u měřicí podesty", 48.72, 38.6, 29000)
    chasm_gust(a, "Poryv nad třetím ramenem", 41.8, 79.8, 25000)
    cloudbed(a,34,48)
    feature(a,"hvd_storm_inlay","Rozeta bouřné komory",33,54.65)
    feature(a,"hvd_sealstand","Hnízdo Pečeti křídla",*WING_POST,action="seal",seal=2,tag="hvd_wing_seal")
    feature(a,"hvd_gong","Ozvučnice bouřné podesty",16.15,55.4,action="chime",tag="hvd_steps_chime",
            text="Rozkmitá nejbližší viditelné větrné tělo do 18 metrů. Pro každou vlnu vydrží jeden úder.")
    a.point("hvd_storm_center",33,54.65)
    a.point("hvd_ward1",16.9,36.2,90)
    feature(a,"hvd_beacon","Návěstí ochranné lucerny",16.9,36.2)
    a.find("hvd_book_steps",15.08,15.86,height=.88,clue=2)
    a.prop(97,"Stůl obsluhy prvního schodiště",14.9,16.0,bearing=90)
    cover(a,[(12.4,53.4)],337)
    feature(a,"hvd_arc_cabinet","Skříň horní hlídky",*STORM_CABINET,cover=1)
    wind_pack(a,"schody_pat","Hlídka prvního schodiště",((17.3,12.7,43.0,14.7),(22.0,19.3,38.0,21.2)),
              ((28.15,16.4),(31.55,17.2),(35.2,15.55),(38.54,17.6)),leash=11)
    wind_pack(a,"merici","Poryv na měřicí podestě",((20,30,41,34),(30,38,49,40)),
              ((36.7,36.8),(39.85,35.9),(38.8,33.35),(35.25,33.45)),leash=14,bearing=235)
    a.encounter("bourna","Bouřné hnízdo",(28,50,50,53),(20,57,41,60))
    a.mob("bourna","hvd_vir",33,54.65,seal=2,elite=1,leash=16)
    a.mob("bourna","hvd_elit_vrhac",41.35,54.9,leash=15,bearing=220)
    a.mob("bourna","hvd_elit_strh",43.95,57.3,leash=15,bearing=235)
    a.mob("bourna","hvd_elit_sprad",45.85,55.28,leash=16,bearing=222)
    wind_pack(a,"horni","Stráž nad třetím ramenem",((20,70,40,73),(20,82,36,85.5)),
              ((37.4,74.5),(34.2,77.0),(30.8,75.5),(27.4,77.0)),leash=13,bearing=236)
    return a


def walks(art, terrain):
    a = scene(art, "hvd_walks", "Visuté ochozy", "tcm02",
              "Dvě zmrzlé stezky stoupají ke kruhovým svatyním Kopí a Lucerny.",
              ambient=(111,121,151), diffuse=(196,210,240), fog=2, sky=4, music=103, wind=30, wind_volume=36)
    a.fixed_tiles = True
    a.special_tiles = terrain.decks['walks']
    chasm_gust(a, "Poryv pod západním ochozem", 22.73, 40.55, 25000)
    chasm_gust(a, "Poryv ve východní zatáčce", 61.65, 57.02, 31000)
    chasm_gust(a, "Poryv u horního hřebene", 14.75, 94.95, 28000)
    for x, y, interval in ((29.33, 23.4, 19000), (64.37, 48.3, 26000)):
        a.sound("hvd_sfx_ice", "Praskání ledu na kraji ochozu", "as_na_x2iccrak1", x, y,
                radius=8.5, volume=75, elevation=0.2, min_distance=2.0, interval=interval, variation=7000)
    a.stash(7,"Kožený kufřík staré hlídky",60.1,69.34,"hvd_walk_cache",bearing=0)
    guards = (
        (3,"kopi","hvd_kopi","hvd_elit_vrhac",(11.75,74.75),(14.62,74.52),"hvd_elit_strh",(9.35,73.35)),
        (4,"lucerna","hvd_svetlonos","hvd_elit_strh",(70.01,74.98),(67.05,74.22),"hvd_elit_vrhac",(73.02,74.1)),
    )
    for shrine,(sign,group,mob,escort,first,extra,last_escort,last) in zip(SHRINES,guards,strict=True):
        x,y=shrine.center
        feature(a,f"hvd_tholos_{shrine.key.lower()}",shrine.name,x,y,bearing=shrine.entrance+90)
        a.point(f"hvd_shrine_{shrine.key.lower()}",x,y,270,shrine.name)
        feature(a,"hvd_sealstand","Oltář pečeti · "+shrine.name,*shrine.seal,action="seal",seal=sign,
                tag="hvd_spear_seal" if sign==3 else "hvd_lamp_seal")
        a.encounter(group,"Stráž · "+shrine.name,(x-3.2,y-3.2,x+3.2,y+3.2))
        a.mob(group,mob,*shrine.stand,seal=sign,elite=1,bearing=shrine.entrance,leash=6)
        a.mob(group,escort,*first,bearing=shrine.entrance,leash=6)
        a.mob(group,last_escort,*last,bearing=shrine.entrance,leash=7)
        a.mob(group,"hvd_elit_sprad",*extra,bearing=shrine.entrance,leash=6)
        light(a,*shrine.seal,15107 if sign==3 else 15113,height=2.15)
    a.point("hvd_ward2",35.4,66.35,90)
    feature(a,"hvd_beacon","Návěstí ochranné lucerny",35.4,66.35)
    for x,y in ((22.8,17.25),(36.9,15.5),(60,20.1),(27.9,60.2),(51.1,62.7),(41,72.85)):
        lantern(a,x,y,15107 if x<30 else 15113)
    for x,y in ((18.65,63.70),(65.97,63.84)):
        feature(a,"hvd_ledgecover","Balvan využívaný jako kryt hlídky",x,y,cover=1)
    wind_pack(a,"rim_low_w","Dolní západní křižovatka",((18.2,21.5,32.8,24.7),(20.0,29.8,32.8,32.0)),
              ((23.2,24.8),(27.1,25.7),(24.2,28.3),(28.0,29.4)),leash=9)
    wind_pack(a,"rim_low_e","Dolní východní křižovatka",((47.2,21.5,65.1,24.8),(46.5,29.8,60.8,32.0)),
              ((50.8,24.6),(54.5,25.6),(55.8,28.75),(52.4,29.3)),leash=9)
    wind_pack(a,"rim_west","Poryvy na západní římse",((18.3,54,29,57.5),(19.5,61,30,63.2)),
              ((24.9,55.7),(25.9,58.0),(22.1,57.2),(24.3,59.8)),leash=8)
    wind_pack(a,"rim_east","Proud pod východní svatyní",((50.8,52.1,64,55),(50,60.25,64,62.3)),
              ((54.5,55.15),(56.9,58.1),(60.0,57.0),(61.9,59.6)),leash=8,bearing=250)
    feature(a,"hvd_adit_mouth","Ústí zarostlého odvodňovacího kanálu",*ADIT_CENTER,bearing=180)
    a.point("hvd_walks_cover_home",75,4.96,270)
    a.trigger("Závětří za výběžkem","hvd_scan_walks",(72.71,5.26,77.42,8.0),"hvd_zone",
              secret="hvd_secret_exit")
    feature(a,"hvd_rimbolt","Zapuštěná západka pod výztuhou",77.34,5.32,bearing=180,
            action="walk_latch",flag="hvd_secret_exit",tag="hvd_latch_walks",
            text="Z mosazné lišty vyčnívá čep. Po zatlačení uvolní desku ze strany ochozů.")
    return a


def gate(art, terrain, *, test_guide):
    a = scene(art, "hvd_gate", "Předbraní Horních sfér", "tcm02",
              "Optický dvůr se třemi sloupy, závorou a schodištěm k Bráně tří paprsků.",
              ambient=(111, 124, 172), diffuse=(204, 214, 251), fog=1, sky=4, music=27, wind=30,
              flight=terrain.flight)
    a.fixed_tiles = True
    a.special_tiles = terrain.decks['gate']
    west_x, west_y = GATE_WEST_BAY
    clerk_x, clerk_y = GATE_CLERK
    a.point("hvd_gate_rest",*GATE_REST,90,"Odpočívárna stráže")
    a.point("hvd_final_gate", *GATE, 90)
    cloudbed(a, 35, 38)
    feature(a, "hvd_gatearch", "Kamenné ostění Brány tří paprsků", *GATE, tag="hvd_stone_frame")
    feature(a, "hvd_gateinlay", "Vedení optické soustavy", 35, 29.6)
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
    feature(a, "hvd_register", "Přijímací místo písaře pečetí", *GATE_CLERK,bearing=90)
    a.find("hvd_book_gate",clerk_x+.60,clerk_y-.22,height=.88,bearing=90,clue=3)
    feature(a, "hvd_dial", "Mechanismus výměny ztracených pečetí", west_x-.61,west_y-2.37,
            action="recap", tag="hvd_recap")
    if test_guide:
        a.stash(7, "TEST · Pouzdro s řešením brány", west_x-.62,west_y+2.37, "hvd_test_case",
                bearing=90,text="Zkušební list obsahuje přesnou sestavu pro tuto výpravu.")
    a.prop(58, "Odpočinek ve strážnici",*GATE_REST,action="rest",tag="hvd_gate_rest_fire")
    a.stash(8, "Schránka poslední hlídky", 52, 34.4, "hvd_guard_cache")
    feature(a, "hvd_dial", "Zakrytí proudu ve strážnici", 48.1, 30.6, action="disarm",
            flag="hvd_chest_off", skill=15, tag="hvd_guard_lock")
    a.trap("Závora světla ve strážnici", "hvd_gatechest", (50, 31, 55, 36), hazard=2, flag="hvd_chest_off")
    a.trap("Výboj optických sloupů", "hvd_gatespark", (26, 24, 44, 36), hazard=0)
    fixture(a, [(453,"Socha navracejícího světlo",27.8,55.6,178),
                (453,"Socha vítající příchozí",42.2,55.6,182),
                (311,"Skříň na výstroj",58.97,36.8,270), (49,"Olej pod policí",58.94,34.51,0)])
    for x, y in ((20,11.35),(50,11.35),(31.3,51.5),(38.7,51.5)):
        lantern(a, x, y)
    for x,y,bearing in ((20.65,33.8,10),(47.86,33.8,350)):
        feature(a, "hvd_raybaffle", "Stínicí blok optického dvora", x, y, bearing=bearing, cover=1)
    return a


REWARD_CATEGORIES = (
    ('zbrane', 'Zbraně', 22.75), ('zbroje', 'Zbroje', 26.0), ('roby', 'Róby', 29.25),
    ('helmice', 'Helmice', 40.75), ('prsteny', 'Prsteny', 44.0), ('amulety', 'Amulety', 47.25),
)


def summit(art, terrain, reward_items):
    a = scene(art, "hvd_top", "Poslední stupeň", "tcm02",
              "Široké schodiště stoupá k dórskému chrámu. Za jeho otevřeným nádvořím hlídá Ithren Poslední lucernu.",
              ambient=(93, 105, 147), diffuse=(223, 214, 247), fog=1, sky=4, music=98, battle=47, wind=30,
              flight=terrain.flight)
    a.fixed_tiles = True
    a.special_tiles = terrain.decks['top']
    a.point("hvd_top_mirror", *TOP_MIRROR, 270, "Patice zkušebního zrcadla pod schody")
    a.point("hvd_boss_home", 35, 50.82, 270)
    a.point("hvd_sun_home", LAST_LANTERN[0],LAST_LANTERN[1]-.92,270)
    for index,(x,y) in enumerate(TOP_GUARDS,1):
        a.point(f"hvd_valk_{index}",x,y,0 if x<35 else 180)
    cloudbed(a, 35, 37)
    a.prop(97, "Zápisový stůl stráže pod schody", 54.32, 14.52, bearing=12)
    a.find("hvd_book_top", 54.47, 14.24, height=.88, bearing=12)
    a.trap("Ithrenova výzva", "hvd_guard_greet", (10.5, 41.2, 59.5, 55.4), hazard=3)
    feature(a, "hvd_sealstand", "Patice zkušebního zrcadla", *TOP_MIRROR, action="mount", tag="hvd_mirror_mount")
    feature(a,"hvd_lighttower","Věž návratového objektivu",*LAST_TOWER[:2],z=LAST_TOWER[2])
    feature(a,"hvd_signallamp","Poslední lucerna",*LAST_LANTERN,action="lantern",tag="hvd_final_lamp")
    a.sound("hvd_sfx_topbell", "Tón opravené ochranné lucerny", "as_cv_bell1", *LAST_LANTERN,
            radius=17.0, volume=127, elevation=1.7, min_distance=4.0, active=False, loop=False)
    feature(a,"hvd_letout","Páka odkláněcího zrcadla",*LANTERN_TURN,action="divert",tag="hvd_lamp_turn",
            text="Páka stáhne lucernu z dráhy paprsku a pošle jeho světlo do kamenného záchytu.")
    feature(a,"hvd_lightdump","Kamenný záchyt odkloněného světla",*LANTERN_SINK[:2])
    a.point("hvd_signal_home",*LAST_LANTERN,90)
    for index,(category,title,x) in enumerate(REWARD_CATEGORIES,1):
        resources = reward_items.get(category, ())
        a.stash(8, f"Výstroj hlídky · {title}", x, 56.75, f"hvd_reward_{index}",
                key="hvd_clona", reward=True,
                text="Po ohlášení opravy si můžeš vzít jeden předmět ze všech schránek dohromady.")
        a.places[-1].fields['VarTable'] = variables(
            reward_count=len(resources),
            **{f'reward_{slot}':resource for slot,resource in enumerate(resources,1)},
        )
    for index,x in enumerate((20,35,50),1):
        feature(a,f"hvd_sector{index}",f"Značka výseče {index}",x,32.0)
    cover(a,TOP_COLUMNS,art['hvd_doric'])
    for x,y in ((19.53,18.32),(50.47,18.32),(17.1,32.22),(52.9,32.22)):
        lantern(a, x, y)
    fixture(a, [(125, "Prapor přísahy", 24.5, 58.25, 180),
                (126, "Prapor návratu", 45.5, 58.25, 180)])
    return a


def study(art):
    a = scene(art, "hvd_study", "Pracovna správkyně", TILESET,
              "Pracovna s archivním stejnopisem Kotvy a zalomeným služebním výstupem k ochozům.",
              ambient=(77,83,110), diffuse=(185,164,139), fog=1, music=50, wind=68,
              tiles=tile_assignments("hvd_study"))
    a.point("hvd_study_rim_cover_home",2.42,15,180)
    a.point("hvd_study_exit_cover_home",15,157.90,270)
    feature(a,"hvd_writedesk","Pracovní stůl správkyně",25.52,38.42,bearing=270)
    a.find("hvd_book_study",25.0,38.38,height=.88,bearing=265)
    feature(a,"hvd_sealstand","Archivní pouzdro · záložní Pečeť kotvy",20.7,40.91,
            action="study_anchor",tag="hvd_study_anchor",
            text="Platný stejnopis Kotvy, uložený pro službu, která na horní ochozy přicházela ze štoly.")
    a.stash(7,"Pouzdro soukromých map",6.32,37.25,"hvd_study_cache",bearing=90,
            text="Správkyniny náhradní čočky a drobné zásoby na cestu k ochozům.")
    feature(a,"hvd_wallring","Vnitřní západka skalní spáry",8.95,11.53,bearing=180,
            action="study_latch",flag="hvd_secret_rim",tag="hvd_latch_rim")
    feature(a,"hvd_wallring","Závora výstupu na ochozy",12.20,153.9,bearing=90,
            action="study_latch",flag="hvd_secret_exit",tag="hvd_latch_exit",
            text="Táhlo vede za severní kamennou obložku. Odjištěná deska otevře pěší výstup na ochozy.")
    return a


def areas(art, terrain, work_tiles, *, test_guide=False, reward_items=None):
    check_plan()
    zones = [
        camp(art), mountain(art), halls(art), workshops(art,work_tiles), dome(art), steps(art, terrain),
        walks(art, terrain), gate(art, terrain, test_guide=test_guide),
        summit(art, terrain, reward_items or {}), study(art), light_service(art),
    ]
    place_transitions(zones)
    by_code = {area.key[4:]: area for area in zones}
    by_code['halls'].point('hvd_r1_safe_return',*R1_SAFE_RETURN)
    for source, target, name, bounds, landing in REPAIR_PASSAGES:
        target_tag = f'hvd_land_{target}_r1'
        by_code[source].trigger(name,f'hvt_repair_{source}',bounds,'hvd_travel',
                                target=target_tag,repair_entry=int(source=='halls'))
        by_code[target].point(target_tag,*landing)
    return zones
