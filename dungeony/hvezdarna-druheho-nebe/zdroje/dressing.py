"""Room-by-room dressing on the existing observatory floor plans."""

from math import atan2, cos, degrees, radians, sin

from aurora import bite, flt, integer
from world import color


NAMES = {
    "hvd_tallpier": "Tesaná nosná pilířová patka", "hvd_brokpier": "Pilíř po sesuvu",
    "hvd_wallpanel": "Reliéf hvězdářského zdiva", "hvd_wallfoot": "Kamenná soklová římsa",
    "hvd_window": "Okno se zlatým sklem", "hvd_cloister": "Oblouk arkády",
    "hvd_shutwin": "Lucernová clona", "hvd_guide": "Vodicí kolej s mosaznými sponami",
    "hvd_facade": "Kamenný výklenek s filtry", "hvd_campshell": "Horský přístřešek",
    "hvd_shoproof": "Stříška optické dílny", "hvd_crag": "Zasněžený skalní hřbet",
    "hvd_snowbank": "Závěj na skalní lavici", "hvd_isle": "Skalní úlomek pod ochozem",
    "hvd_rubble": "Sesutá kamenná patka", "hvd_pave_n": "Tmavá dlažba s hvězdnou vložkou",
    "hvd_pave_w": "Pískovcová dlažba s vložkou", "hvd_runner": "Měřicí pás v dlažbě",
    "hvd_bluebann": "Modrý plukovní prapor", "hvd_goldbann": "Prapor návratového světla",
    "hvd_tools": "Sada jemných dílenských nástrojů", "hvd_openbook": "Otevřená kniha",
    "hvd_crate": "Bedna se zásobami", "hvd_shelf": "Police s výměnnými díly",
    "hvd_oillamp": "Olejová lucerna v kleci", "hvd_lectern": "Pult se servisním rukopisem",
    "hvd_armillary": "Prstencový model oblohy", "hvd_cupolarib": "Žebro kopule",
    "hvd_mounttrim": "Kotvící věnec refraktoru", "hvd_bridgewall": "Klenba pod lávkou",
    "hvd_bluepost": "Modrý navigační hrot", "hvd_amberpost": "Zlatý navigační hrot",
    "hvd_sentrybay": "Výklenek hlídky", "hvd_sconce": "Nástěnný hořák",
    "hvd_gatecrest": "Koruna brány s reliéfem dvojího nebe", "hvd_hoist": "Výklopný dílenský naviják",
    "hvd_grille": "Mosazné mřížoví", "hvd_altarbase": "Stupňovitý základ stanoviště",
    "hvd_pavilion": "Otevřený pavilon poslední služby", "hvd_eddy": "Spirála stlačeného větru",
    "hvd_mistbank": "Vlny mraků pod ochozy",
}

STUDY = (
    (97, "Stůl k měření", 0, 0, 0, 0),
    (178, "Lavice zapisovatele", .27, -1.04, 0, 0),
    ("hvd_openbook", None, -.45, .10, .88, 11),
    (455, "Výpočet polohy hvězd", .30, .29, .89, 26),
    ("hvd_oillamp", None, .72, .10, 1.01, 0),
    (56, "Poznačené svazky", -.97, .26, .87, 17),
    (457, "Volný útržek", .38, -.30, .89, 3),
    ("hvd_crate", None, -1.45, .56, 0, -13),
    (85, "Pytel pod stolem", 1.36, .54, 0, 51),
    (49, "Sud u stěny", 1.81, .82, 0, 9),
)

REPAIR = (
    (97, "Stolice pro výměnu okulárů", 0, 0, 0, 0),
    ("hvd_tools", None, -.11, -.04, .89, 8),
    (383, "Krátká svíce v objímce", -.75, .36, .87, 0),
    (456, "Listy s rozměry rámečků", .38, .10, .89, -17),
    (360, "Stočené lano", .73, .45, .89, 28),
    ("hvd_crate", None, -1.52, .16, 0, 70),
    (109, "Sestavené součásti", .98, .86, 0, 9),
    (85, "Pytle se zlomky skla", -1.29, -.48, 0, -20),
    (178, "Pojízdná lavice", .11, -1.12, 0, 3),
    (48, "Kovadlina pro jemné kování", 1.52, -.41, 0, 180),
)

SUPPLIES = (
    ("hvd_crate", None, 0, 0, 0, 0),
    ("hvd_crate", None, 1.22, -.09, 0, -9),
    (49, "Sud s olejem", -.77, .55, 0, 0),
    (85, "Svázané vaky", -.26, -.61, 0, 47),
    (360, "Svinuté lano", .21, .11, .72, 0),
    (14, "Brašna hlídky", 1.19, -.06, .72, 72),
    (383, "Svíce na bedně", .41, .12, .72, 0),
    (361, "Druhé jistící lano", 1.78, .43, .035, 14),
)

GUARD = (
    (287, "Lavice nebeské hlídky", 0, 0, 0, 0),
    (105, "Stojan na odložené zbraně", -1.85, 1.02, 0, 9),
    (51, "Sbalená noční výstroj", -.44, .82, 0, 84),
    ("hvd_crate", None, 1.62, .80, 0, 8),
    (55, "Složený prapor", 1.64, .80, .72, 2),
    (56, "Rozpisy služby", -.38, -.12, .54, 0),
    ("hvd_oillamp", None, 1.92, .85, .92, 0),
    (49, "Náhradní olej", 2.41, .90, 0, 6),
    (527, "Koš s čistými knoty", 1.27, -.02, 0, 99),
    (383, "Dohořelá svíčka", .65, .13, .55, 0),
    (85, "Plátěný pytel", -1.71, -.22, 0, -32),
)

STATION = (
    ("hvd_lectern", None, 0, 0, 0, 0),
    ("hvd_openbook", None, .03, -.01, 1.141, 0),
    (383, "Svíce na pultu", -.29, .18, 1.115, 0),
    ("hvd_oillamp", None, 1.19, .76, 1.82, 0),
    ("hvd_bluepost", None, 1.19, .76, 0, 0),
    (56, "Záznamy hlídky", .59, .75, 0, 16),
    (14, "Brašna pro poslední záznam", -1.0, .55, 0, -15),
)

LIGHTS = {"amber": 15113, "blue": 15107, "orange": 15109, "violet": 15110}


class Dress:
    def __init__(self, area):
        self.area = area

    def put(self, model, x, y, *, direction=0, lift=0, base=None, name=None):
        appearance = self.area.art[model] if isinstance(model, str) else model
        z = self.area.z_at(y) if base is None else base
        self.area.prop(appearance, name or NAMES[model], x, y, z=z + lift, bearing=direction)

    def lamp(self, x, y, lift=1.88, tint="amber", base=None):
        self.put(LIGHTS[tint], x, y, lift=lift, base=base, name="Osvětlení")

    def set(self, x, y, kit, direction=0, base=None):
        a = radians(direction)
        z = self.area.z_at(y) if base is None else base
        for asset, label, dx, dy, dz, bearing in kit:
            px = x + dx * cos(a) - dy * sin(a)
            py = y + dx * sin(a) + dy * cos(a)
            self.put(asset, px, py, lift=dz, direction=direction + bearing, base=z, name=label)

    def line(self, asset, x, y, count, dx, dy, direction=0, lift=0, base=None):
        for i in range(count):
            self.put(asset, x + dx * i, y + dy * i, direction=direction, lift=lift, base=base)

    def relief(self, x, y, direction=0, shade="blue", base=None):
        self.put("hvd_facade", x, y, direction=direction, base=base)
        self.set(x, y, (("hvd_sconce", None, -.79, -.72, 2.4, 0), ("hvd_sconce", None, .79, -.72, 2.4, 0)),
                 direction, base)
        self.lamp(x, y, 2.55, shade, base)

    def signpost(self, x, y, shade="blue", direction=0, base=None):
        head = "hvd_amberpost" if shade == "amber" else "hvd_bluepost"
        self.put(head, x, y, direction=direction, base=base)
        self.lamp(x, y, 2.09, shade, base)

    def arch(self, x, y, direction=0, shade="amber", base=None):
        self.put("hvd_cloister", x, y, direction=direction, base=base)
        self.set(x, y, (("hvd_oillamp", None, -2.17, -.39, 2.40, 0),
                        ("hvd_oillamp", None, 2.17, -.39, 2.40, 0)), direction, base)
        self.lamp(x, y, 2.55, shade, base)

    def bridge(self, x, shade):
        self.put("hvd_bridgewall", x, 35, base=5.0)
        for y, z in ((25, 5.03), (30.25, 6.55), (39.75, 6.55), (45, 5.02)):
            for side in (-1, 1):
                dx = (2.0 if y in (25, 45) else 1.54) * side
                self.put("hvd_amberpost" if shade == "amber" else "hvd_bluepost", x + dx, y, base=z)
            if y in (30.25, 39.75):
                self.lamp(x, y, 2.02, shade, z)

    def clouds(self, banks, rocks):
        for x, y, z, angle in rocks:
            self.put("hvd_isle", x, y, base=z, direction=angle)
        for x, y, z, angle in banks:
            self.put("hvd_mistbank", x, y, base=z, direction=angle)


def mountain(s):
    s.area.lighting.update(ChanceSnow=integer(27), FogClipDist=flt(96.0),
                           MoonAmbientColor=color(65,80,119), MoonDiffuseColor=color(193,202,229))
    # The summit is a shelf in the rock. The exposed terrain is visible behind the drum.
    for x,y,z,angle in ((15,56,0,81),(21,61,0,13),(29,67,-1.0,112),
                        (47,69,-.25,240),(56,62,-.65,210),(62,51,-1.0,81),(60.5,42,-3.1,58)):
        s.put("hvd_crag",x,y,base=z,direction=angle)
    for x,y,angle in ((26,42,35),(49,45,96),(33,54,35),(52,55,74),(32,62,148),
                      (33,29,21),(50,33,151),(12,22,31),(28,11,84),(53,28,84)):
        s.put("hvd_snowbank",x,y,direction=angle)
    s.put("hvd_campshell",16,18.8,direction=3)
    s.put("hvd_campshell",27.8,26.1,direction=90)
    s.set(15.2,21.1,SUPPLIES,5)
    s.set(22.7,23.7,STUDY,0)
    s.set(29.0,15.4,SUPPLIES,133)
    s.set(12.4,17.2,STATION,110)
    s.set(54,23.5,SUPPLIES,97)
    for x,y in ((13.2,18),(20.8,21.2),(26.1,24.9),(32.8,31.8),(43.6,39),(37.2,49.2),(45,50.5)):
        s.lamp(x,y,1.65,"orange")
    for x,y in ((34.4,31.8),(45.8,35.4),(34.9,40.8),(45.6,44.1),(35.2,47.3),(45.0,47.2)):
        s.put("hvd_wallfoot",x,y,direction=90 if y < 47 else 0)
        s.put("hvd_bluepost",x,y+.94)
        s.put("hvd_rubble",x + (-.64 if x<40 else .71),y - .94,direction=125)
    for y in (27.5,32.5,37.5,42.5,47.5):
        s.put("hvd_runner",39.9,y,lift=.016)
    for x in (34.0,47.0):
        s.put("hvd_window",x,57.5)
        s.put("hvd_tallpier",x - .83,55.25)
        s.put("hvd_tallpier",x + .83,55.25)
        s.put("hvd_bluebann",x,54.11,lift=1.6)
        s.put("hvd_wallpanel",x,59.25,direction=90)
        s.put("hvd_sconce",x,55.79,lift=2.3)
        s.lamp(x,55.79,2.8,"amber")
    for x,y,d in ((29,48,14),(31,52,93),(48,48,-12),(52,51,82),(48,64,55),(35,63,149)):
        s.put("hvd_rubble",x,y,direction=d)
        s.put(255,x+.46,y-.44,direction=d+19,name="Sníh u odhaleného zdiva")
    s.put("hvd_lectern",33.1,46.3,direction=39)
    s.put("hvd_lectern",52.3,26.8,direction=117)
    s.arch(56.8,24.0,90,"amber")


def halls(s):
    s.area.lighting.update(MoonAmbientColor=color(66,81,108), MoonDiffuseColor=color(149,166,203))
    # One side holds active filters. The opposite wall preserves the cover recesses.
    for x in (31.4,35.5,40,44.5,49.0,53.5,57.4):
        s.put("hvd_wallfoot",x,20.0)
        s.put("hvd_wallfoot",x,29.9,direction=180)
        s.put("hvd_runner",x,25.0,direction=90)
    for i,x in enumerate((32.3,38.2,44,49.7,55.4)):
        s.arch(x,25,90, "blue" if i%2 else "violet")
        s.put("hvd_guide",x-.20,25)
        s.put("hvd_shutwin",x,29.92)
        s.put("hvd_bluebann",x,19.95,direction=180,lift=.72)
        s.put("hvd_sconce",x,20.63,direction=180,lift=2.3)
        s.put("hvd_tallpier",x-2.4,29.7)
    for x,y,d in ((13.0,18.8,90),(27.8,16.5,270),(17.9,34.5,90),
                  (26.9,40.7,270),(58.1,34,270),(59.4,43.8,270),(54.7,49.8,0)):
        s.relief(x,y,d,"amber" if x<29 else "blue")
    for x,y,d in ((16.2,17.9,4),(18.3,27.4,90),(18.2,45.8,165),(28.5,47.8,180),
                  (54,42.2,90),(55.7,46.6,218)):
        s.set(x,y,STUDY,d)
    for x,y,d in ((12.5,26,90),(20.8,49.0,3),(23.2,33.3,90),(57.3,39,270),(49,46.3,180)):
        s.put("hvd_shelf",x,y,direction=d)
        s.put("hvd_tools",x+.53,y,direction=d,lift=.88)
    for x,y,d in ((15,46,70),(29.7,40.9,270),(53.3,35.4,180)):
        s.set(x,y,SUPPLIES,d)
    for x,y in ((13,21),(18.4,48),(26,43),(47,47),(53,40)):
        s.signpost(x,y,"amber")


def workshops(s):
    s.area.lighting.update(FogClipDist=flt(87.0), MoonAmbientColor=color(83,91,128),
                           MoonDiffuseColor=color(181,180,194))
    s.put("hvd_shoproof",17,16.0,direction=7)
    s.put("hvd_shoproof",34.3,15.6,direction=180)
    s.put("hvd_hoist",31.8,19.8,direction=28)
    s.put("hvd_shoproof",34.2,56.8)
    s.bridge(25,"amber")
    for x,y,d in ((17.0,15.0,0),(34.6,16.9,180),(35.0,56.1,355)):
        s.set(x,y,REPAIR,d)
        s.lamp(x,y,1.9,"orange")
    for x,y,d in ((13,12.8,12),(35.8,12.3,160),(15,53.3,75),(28,59,175),(44.7,59,271)):
        s.set(x,y,SUPPLIES,d)
    for x,y,d in ((12,17.6,90),(29.2,12.3,180),(32.8,59,0),(42.7,57.8,180),(18.2,58.8,0)):
        s.put("hvd_shelf",x,y,direction=d)
        s.put("hvd_oillamp",x,y,lift=2.31,direction=d)
    for x,y,d in ((24,17,0),(24,51,0),(41,55,90)):
        s.arch(x,y,d,"amber")
    for x,y,d in ((11,15,90),(38.3,13,90),(11.2,56.0,90),(47.2,58,0)):
        s.relief(x,y,d,"blue")
    for x,y in ((14.2,16.7),(18,53.5),(41,58.8)):
        s.put("hvd_armillary",x,y)
        s.lamp(x,y,1.95,"blue")
    for y in (51.2,56.2):
        for x in (15,20,25,30,35,40,44.8):
            s.put("hvd_pave_w" if x in (15,40) else "hvd_pave_n",x,y)
    for x in (14,19,31,37):
        s.put("hvd_wallfoot",x,21.4)
        s.put("hvd_wallfoot",x,50.4)
        s.put("hvd_rubble",x-.68,50.2)
    s.clouds([(3,37,-7,27),(41,33,-7,135),(27,64,-8,0)],
             [(7,34,-10,20),(45,42,-7,120),(55,23,-8,55),(53,58,-7,66)])


def dome(s):
    s.area.lighting.update(FogClipDist=flt(60.0), MoonAmbientColor=color(72,83,117),
                           MoonDiffuseColor=color(162,165,202))
    # Open ribs keep the apparatus visible from above. The books stay on the outer rim.
    for x,y in ((17.5,27),(19.4,38.4),(25.0,42.3),(36.4,41.7),(41.3,36.6),(42.0,23.7),
                (34.7,18.2),(24.1,18.5)):
        direction=degrees(atan2(31-y,30-x))-90
        s.put("hvd_cupolarib",x,y,direction=direction)
        s.put("hvd_bluebann",x,y+.24,lift=2.3,direction=direction)
        s.lamp(x,y,3.9,"violet")
    for x,y,d in ((12.1,30.3,90),(13.5,36.5,60),(20.8,40,0),(37.3,41.7,0),
                  (44.0,31,270),(38.2,17.6,180),(24.3,15.6,180),(17.2,19.6,140)):
        s.relief(x,y,d,"blue")
    for x,y,d in ((17.7,34.8,98),(21.6,36,6),(36.9,36.6,359),(37.4,19.5,171),(45,28.5,275)):
        s.set(x,y,STUDY,d)
    for x,y,d in ((14.6,35.4,90),(20.5,38.9,20),(40,37,268),(36.5,17.5,0),(42.7,28.8,266)):
        s.put("hvd_shelf",x,y,direction=d)
        s.put("hvd_oillamp",x,y-.19,lift=2.31)
    for x,y in ((19.2,24.2),(19.7,37.6),(42,27.7),(38.3,35),(33.6,42.8)):
        s.put("hvd_armillary",x,y)
        s.lamp(x,y,2.0,"amber")
    for x,y,d in ((22.5,20.5,0),(37.5,20.5,0),(17,30.5,0),(17,35.5,0),(42.5,26.0,90),
                  (42.5,31.0,90),(24.5,39,0),(35.5,39,0),(30,39.5,90),(30,21.4,0)):
        s.put("hvd_pave_n",x,y,direction=d)
    s.put("hvd_mounttrim",30,31)
    s.put("hvd_gatecrest",30,46.4)
    s.arch(30,44.8,0,"violet")
    for x,y in ((25.0,42.5),(35.0,42.5),(25.0,22),(35.0,22),(18.8,29),(41.4,29)):
        s.put("hvd_guide",x,y)
        s.put("hvd_sconce",x,y,lift=1.95,direction=90 if x<30 else -90)
        s.lamp(x,y,2.8,"amber")


def steps(s):
    s.area.lighting.update(MoonAmbientColor=color(71,88,129), MoonDiffuseColor=color(192,188,229))
    for x in (5.0,11.0,17.0,35.0,41.0,47.0,53.0):
        s.relief(x,21.9,0,"blue",base=5.0)
    for x in (5.0,11.0,17.0,22.8,44.0,50.0,56.0):
        s.relief(x,41.6,0,"violet",base=10.0)
    for x in (11.7,16.7,36.0,41.0,46.0,51.0):
        s.put("hvd_wallfoot",x,30.7,base=10.0)
    for x in (11.7,16.7,21.7,46.0,51.0):
        s.put("hvd_wallfoot",x,50.2,base=15.0)
    s.put("hvd_eddy",30,35.7,base=10.02)
    s.lamp(30,35.7,4.45,"blue",10.0)
    s.arch(25.0,17.1,0,"blue",5.0)
    s.arch(35.0,52.5,0,"amber",15.0)
    s.put("hvd_pavilion",29.9,57.8,base=15.0)
    s.set(21.0,15.8,STATION,92,5.0)
    s.set(43.6,34.6,STATION,245,10.0)
    s.set(21.0,55.5,GUARD,34,15.0)
    for x,y,z,tint in ((15.0,33.6,10.0,"blue"),(22.3,32.1,10.0,"violet"),
                       (36.9,32.2,10.0,"blue"),(14.4,38.2,10.0,"blue"),
                       (44.9,38.0,10.0,"amber"),(17.5,54.5,15.0,"amber"),
                       (43.4,54.2,15.0,"amber")):
        s.signpost(x,y,tint,base=z)
        s.put("hvd_bluebann",x,y+.36,lift=.70,base=z)
        s.put("hvd_pave_n",x,y,base=z)
    for x,y,z,d in ((12,32,10,34),(19,39,10,19),(41,38,10,133),(49,36,10,23),
                      (20,51,15,129),(40,55,15,220),(18,15,5,21)):
        s.put("hvd_brokpier",x,y,base=z,direction=d)
        s.put("hvd_rubble",x+.64,y+.40,base=z,direction=d+33)
    s.clouds([(6,35,-6,36),(51,41,-8,62),(51,58,-8,42)],
             [(4,12,-7,90),(3,30,-3,43),(55,35,-4,68),(57,50,-4,165),(4,54,-4,119)])


def walks(s):
    s.area.lighting.update(FogClipDist=flt(112.0), MoonAmbientColor=color(76,88,124),
                           MoonDiffuseColor=color(178,204,236))
    s.bridge(25,"blue")
    s.bridge(55,"amber")
    for x,y,tint in ((25,18,"blue"),(55,18,"amber"),(25,51,"blue"),(55,51,"amber"),(40,66,"amber")):
        s.arch(x,y,0,tint,5.0)
    for i,x in enumerate((15,20,31,36,41,46,61,66)):
        s.put("hvd_wallfoot",x,21.5,base=5.0)
        s.put("hvd_pave_n" if x<45 else "hvd_pave_w",x,15,base=5.0)
        if i%2==0:
            s.signpost(x,19.9,"blue" if x<45 else "amber",base=5.0)
    s.put("hvd_sentrybay",20,60.8,base=5.0)
    s.put("hvd_sentrybay",62,60.8,base=5.0)
    s.set(15.2,58.9,GUARD,87,5.0)
    s.set(67.0,58.6,GUARD,263,5.0)
    s.set(22.7,62.2,STATION,151,5.0)
    s.set(59.1,62.7,STATION,176,5.0)
    s.set(38.2,18.0,STATION,0,5.0)
    s.set(11.4,16.8,SUPPLIES,87,5.0)
    s.set(68.9,16.6,SUPPLIES,286,5.0)
    for y in (53.8,58.7,63.6):
        for x in (16.3,21.3,26.3,31.3,53.7,58.7,63.7,68.7):
            s.put("hvd_pave_n" if x<38 else "hvd_pave_w",x,y,base=5.0)
    for x,y,angle in ((14,54,90),(36,57,270),(47,57,90),(71,55,270),(32,67,0),(48,67,0)):
        s.relief(x,y,angle,"blue" if x<40 else "amber",base=5.0)
        s.put("hvd_bluebann" if x<40 else "hvd_goldbann",x,y-.29,lift=.98,base=5.0,direction=angle)
    s.clouds([(6,34,-7,55),(38,31,-7,88),(72,39,-6,126),(34,56,-8,9)],
             [(11,40,-8,29),(6,52,-7,19),(40,41,-8,110),(73,38,-9,91),(45,52,-10,50)])


def gate(s):
    s.area.lighting.update(FogClipDist=flt(102.0), MoonAmbientColor=color(92,103,146),
                           MoonDiffuseColor=color(214,201,229))
    for x in (4,10,16,22,28,43,49,55,61,67):
        s.relief(x,41.32,0,"amber" if x<31 else "blue",base=5.0)
    for x in (13.8,18.8,23.8,28.8,41.2,46.2,51.2,56.2):
        s.put("hvd_wallfoot",x,50.8,base=10.02)
        s.put("hvd_tallpier",x,53.9,base=10.0)
    s.put("hvd_gatecrest",35,53.3,base=10)
    for x in (25.4,44.6):
        s.put("hvd_sentrybay",x,54.7,base=10)
        s.put("hvd_armillary",x,52.2,base=10)
        s.put("hvd_goldbann",x,53.1,lift=1.02,base=10)
        s.lamp(x,52.2,2.5,"amber",10)
    for x,y,d in ((14.5,15.7,90),(15,23,90),(15.3,30,90),(14.2,36.6,90),
                  (55.7,27.0,270),(56.2,35.5,270)):
        s.arch(x,y,d,"amber",5.0)
        s.put("hvd_wallpanel",x,y,direction=d,base=5.0)
    for x,y,d in ((51,17.5,124),(51.5,35.5,268),(19.1,28.4,88),(17.3,33.3,86)):
        s.set(x,y,GUARD,d,5.0)
    for x,y,d in ((22.9,17.8,9),(47.8,19.7,185),(25,36.5,162),(45,36.3,220)):
        s.set(x,y,STATION,d,5.0)
    for x,y,d in ((22,29.8,90),(49.3,26.7,270),(18,20.7,0),(53.6,38.2,0)):
        s.put("hvd_grille",x,y,direction=d,base=5.0)
    for y in (15.5,20.5,25.5,30.5,35.5,39.0):
        for x in (19.8,24.8,45.3,50.3):
            s.put("hvd_pave_w" if x==19.8 or x==50.3 else "hvd_pave_n",x,y,base=5)
    s.put("hvd_altarbase",35,29.0,base=4.30)
    for x,y in ((29,23.9),(41,23.9),(27.7,32.5),(43.3,32.5),(29.0,37.5),(41,37.5)):
        s.signpost(x,y,"amber",base=5.0)
    s.clouds([(10,51,-6,38),(52,60,-8,109),(56,12,-7,52)],
             [(8,49,-6,23),(53,62,-5,211),(65,30,-7,78),(3,19,-6,120)])


def summit(s):
    s.area.lighting.update(FogClipDist=flt(96.0), MoonAmbientColor=color(80,94,141),
                           MoonDiffuseColor=color(209,208,241))
    for x in (4.4,10.1,15.8,21.5,27.2,42.8,48.5,54.2,59.9,65.6):
        s.relief(x,21.65,0,"amber" if x<35 else "blue",base=5)
    s.put("hvd_pavilion",35,54.8,base=10)
    s.put("hvd_altarbase",35,55.5,base=9.76)
    for x,y in ((21.1,54.2),(48.9,54.2)):
        s.put("hvd_sentrybay",x,y,base=10)
        s.put("hvd_armillary",x,y-.96,base=10)
        s.put("hvd_goldbann",x,y+.54,lift=1.2,base=10)
        s.lamp(x,y,2.78,"amber",10)
    for x,y,angle in ((12.4,34,90),(12.5,42,90),(13.3,49.2,90),
                      (57.8,34.4,270),(57.6,41.8,270),(56.9,49.3,270)):
        s.arch(x,y,angle,"blue" if x<35 else "amber",10)
        s.put("hvd_tallpier",x,y-.96,base=10)
    for y in (32.8,37.7,42.6,47.5,52.4):
        s.put("hvd_pave_n",19.8,y,base=10.0)
        s.put("hvd_runner",35,y,base=10.0)
        s.put("hvd_pave_w",50.2,y,base=10.0)
    for x,y,d,z in ((23.3,17.6,9,5),(45.6,16.3,-12,5),(24.4,54.4,165,10),
                    (45.3,55.7,227,10),(18.4,49.0,96,10),(51.8,49.0,281,10)):
        s.set(x,y,STATION,d,z)
    for x,y,d in ((10.3,44.2,90),(59,45.8,269),(21.5,55.8,18),(49.6,56.1,355)):
        s.set(x,y,GUARD,d,10)
    for i,x in enumerate((13.2,18.3,23.4,46.6,51.7,56.8)):
        s.put("hvd_wallfoot",x,50.5)
        s.signpost(x,51.5,"blue" if i<3 else "amber",base=10)
        s.put("hvd_pave_n",x,53.8,base=10)
    s.clouds([(13,43,-7,86),(59,42,-6,120),(27,65,-8,58)],
             [(9,37,-7,110),(61,50,-6,19),(8.1,56,-4,129),(59,57,-5,232),(29,66,-8,10)])


def dress_areas(zones):
    designers = (mountain, halls, workshops, dome, steps, walks, gate, summit)
    for area, design in zip(zones, designers, strict=True):
        design(Dress(area))
