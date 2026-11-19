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
    "hvd_landing": "Kamenné předpolí hvězdárny",
}

STUDY = (
    (97, "Stůl k měření", 0, 0, 0, 0),
    (178, "Lavice zapisovatele", .27, -1.04, 0, 0),
    ("hvd_openbook", None, -.45, .10, .88, 11),
    (455, "Výpočet polohy hvězd", .30, .29, .89, 26),
    ("hvd_oillamp", None, .72, .10, 1.07, 0),
    (56, "Poznačené svazky", -.97, .26, .87, 17),
    (457, "Volný útržek", .38, -.30, .89, 3),
    ("hvd_crate", None, -1.45, .56, 0, -13),
    (85, "Pytel vedle stolu", 1.54, 1.04, 0, 51),
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
    (178, "Pojízdná lavice", .11, -1.12, 0, 3),
    (48, "Kovadlina pro jemné kování", 1.92, -.61, 0, 180),
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
    (105, "Stojan na odložené zbraně", -2.38, 1.06, 0, 9),
    (51, "Sbalená noční výstroj", -.44, .82, 0, 84),
    ("hvd_crate", None, 2.55, 1.18, 0, 8),
    (55, "Složený prapor", 2.56, 1.18, .72, 2),
    (56, "Rozpisy služby", -.38, -.12, .54, 0),
    ("hvd_oillamp", None, 2.72, 1.15, .92, 0),
    (49, "Náhradní olej", 3.28, .74, 0, 6),
    (527, "Koš s čistými knoty", 2.65, -.48, 0, 99),
    (383, "Dohořelá svíčka", .65, .13, .55, 0),
)

STATION = (
    ("hvd_lectern", None, 0, 0, 0, 0),
    ("hvd_openbook", None, .03, -.01, 1.141, 0),
    (383, "Svíce na pultu", -.29, .18, 1.115, 0),
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
        self.set(x, y, (("hvd_sconce", None, -.97, -.53, 2.4, 0),
                        ("hvd_sconce", None, .97, -.53, 2.4, 0)), direction, base)
        self.lamp(x, y, 2.55, shade, base)

    def signpost(self, x, y, shade="blue", direction=0, base=None):
        head = "hvd_amberpost" if shade == "amber" else "hvd_bluepost"
        self.put(head, x, y, direction=direction, base=base)
        self.lamp(x, y, 2.09, shade, base)

    def arch(self, x, y, direction=0, shade="amber", base=None):
        self.put("hvd_cloister", x, y, direction=direction, base=base)
        self.set(x, y, (("hvd_sconce", None, -2.42, -.29, 2.22, 0),
                        ("hvd_sconce", None, 2.42, -.29, 2.22, 0)), direction, base)
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
    # Wind shelter and provisions face the beginning of the cleared track.
    s.put("hvd_campshell", 15.8, 20.35)
    s.put("hvd_campshell", 31.7, 14.85, direction=176)
    s.set(13.4, 21.55, SUPPLIES, 8)
    s.set(31.9, 14.3, SUPPLIES, 174)
    s.put("hvd_oillamp", 20.99, 22.02, lift=1.07)
    s.lamp(20.99, 22.02, 1.34, "amber")
    s.signpost(22.6, 25.87, "amber")
    s.signpost(31.95, 27.75, "blue")
    # The rock shoulders frame one approach. The secondary lane descends to the workshops.
    for x,y,z,angle in ((17,56,-.9,66),(22,63,-.1,14),(29,68,-1.4,124),
                        (50,68,-1.75,232),(55,62,-.9,218),(61,48,-1.8,76)):
        s.put("hvd_crag",x,y,base=z,direction=angle)
    for x,y,angle in ((27.5,31.9,36),(29.9,35.2,92),(40.3,30.3,89),
                      (40.9,35.8,75),(28.9,43.8,42),(49.3,44.5,163),
                      (32.6,59.7,40),(47.4,60.3,80)):
        s.put("hvd_snowbank",x,y,direction=angle)
    for x,y,d in ((31.1,34.9,90),(39.8,38.35,96),(31.05,42.7,90)):
        s.put("hvd_wallfoot",x,y,direction=d)
        s.put("hvd_rubble",x + .35,y - 2.0,direction=d - 18)
    s.signpost(37.65, 42.4, "blue")
    s.signpost(52.6, 26.75, "amber")
    s.put("hvd_bluebann", 57.9, 21.12, lift=.75, direction=90)
    # Flat forecourt and two attached wings close the vestibule against the rock.
    s.put("hvd_landing",40.0,50.0)
    for x in (33.15,46.85):
        s.put("hvd_wallfoot",x,49.8,direction=90)
        s.put("hvd_window",x,54.6)
        s.put("hvd_wallpanel",x,56.09,direction=90)
        s.put("hvd_bluebann",x,54.18,lift=.65)
        s.put("hvd_sconce",x - .88,54.31,lift=2.3)
        s.lamp(x - .88,54.03,2.76,"amber")
    for x,y,d in ((29.0,48.6,15),(30.6,52.1,94),(48.4,49.1,26),(49.1,54.7,84)):
        s.put("hvd_rubble",x,y,direction=d)


def halls(s):
    s.area.lighting.update(MoonAmbientColor=color(66,81,108), MoonDiffuseColor=color(149,166,203))
    # The two native corridors have solid masonry. Furnish the rooms they connect.
    s.put("hvd_shelf", 9.85, 17.9, direction=90)
    s.put("hvd_oillamp", 11.59, 13.64, lift=1.07)
    s.put("hvd_bluepost", 20.2, 16.95)
    s.set(20.15, 42.0, REPAIR, 180)
    s.put("hvd_shelf", 14.0, 49.3)
    s.put("hvd_shelf", 17.0, 49.3)
    s.relief(15.15, 51.15, 0, "amber")
    s.put("hvd_armillary", 12.4, 46.6)
    s.lamp(12.4, 46.6, 2.05, "amber")
    s.put("hvd_oillamp", 17.0, 49.23, lift=2.50)
    s.put("hvd_runner", 15.0, 36.0)
    s.put("hvd_runner", 15.0, 27.0)
    s.set(53.1, 17.35, STUDY, 180)
    s.set(55.3, 30.85, REPAIR, 180)
    s.relief(62.15, 21.1, 270, "blue")
    s.relief(62.15, 28.2, 270, "amber")
    s.put("hvd_shutwin", 60.65, 15.35, direction=270)
    s.put("hvd_shelf", 62.15, 34.1, direction=270)
    s.put("hvd_armillary", 50.28, 29.25)
    s.lamp(50.28, 29.25, 1.9, "blue")
    for x in (26.5, 35.0, 43.5):
        s.put("hvd_runner", x, 15.0, direction=90)


def workshops(s):
    s.area.lighting.update(FogClipDist=flt(87.0), MoonAmbientColor=color(83,91,128),
                           MoonDiffuseColor=color(181,180,194))
    # Workshop bays have their own work surfaces. The middle aisle leads straight to the bridge.
    s.put("hvd_shoproof",16.72,16.3)
    s.put("hvd_shoproof",34.3,15.6,direction=180)
    s.put("hvd_hoist",31.55,20.72,direction=28)
    s.put("hvd_tools",17.02,16.02,lift=.88,direction=80)
    s.put("hvd_oillamp",16.95,16.83,lift=1.07)
    s.lamp(16.95,16.83,1.28,"amber")
    s.put("hvd_shelf",12,18.42,direction=90)
    s.put("hvd_oillamp",12,18.42,lift=2.51,direction=90)
    s.relief(10.65,15.1,90,"blue")
    s.set(34.65,16.8,REPAIR,180)
    s.lamp(34.65,16.8,1.5,"orange")
    s.set(34.4,10.75,SUPPLIES,165)
    s.put("hvd_wallfoot",38.9,9.55)
    s.put("hvd_wallfoot",39.78,20.58,direction=90)
    s.put("hvd_amberpost",28.47,20.93)

    s.bridge(25,"amber")
    s.arch(25,23.4,0,"amber")
    s.arch(25,50.75,0,"blue")
    for x in (14,19,31,37):
        s.put("hvd_wallfoot",x,21.4)
        s.put("hvd_wallfoot",x,50.4)
    s.put("hvd_pave_w",25,18.42)
    s.put("hvd_pave_w",25,54.8)

    # The far landing is a sheltered maintenance yard below the entrance to the dome.
    s.put("hvd_shoproof",34.2,57.75)
    s.set(34.5,57.2,REPAIR,0)
    s.lamp(34.5,57.2,1.5,"amber")
    s.relief(11.2,55.3,90,"blue")
    s.relief(40.75,61.05,0,"blue")
    s.set(14.85,56.5,SUPPLIES,85)
    s.put("hvd_shelf",19.25,59.55)
    s.put("hvd_oillamp",19.25,59.55,lift=2.51)
    s.put("hvd_armillary",44.0,57.9)
    s.lamp(44.0,57.9,1.95,"blue")
    s.put("hvd_pave_n",43.05,54)
    s.clouds([(3,37,-7,27),(41,33,-7,135),(27,64,-8,0)],
             [(7,34,-10,20),(45,42,-7,120),(55,23,-8,55),(53,58,-7,66)])


def dome(s):
    s.area.lighting.update(FogClipDist=flt(60.0), MoonAmbientColor=color(72,83,117),
                           MoonDiffuseColor=color(162,165,202))
    # Keep the four approaches open around a ring of load-bearing ribs and work bays.
    for x,y in ((17.9,22.25),(19.4,38.4),(25.0,42.3),(36.4,41.7),(41.4,35.9),(43.2,20.45),
                (34.7,18.2),(24.1,18.5)):
        direction=degrees(atan2(31-y,30-x))-90
        s.put("hvd_cupolarib",x,y,direction=direction)
        s.put("hvd_bluebann",x,y+.24,lift=2.3,direction=direction)
        s.lamp(x,y,3.9,"violet")

    # South of the instrument, the writer's table faces shelves and the repair station.
    s.relief(24.2,15.85,180,"amber")
    s.relief(39.2,15.72,180,"blue")
    s.put("hvd_shelf",20.55,18.95,direction=135)
    s.put("hvd_oillamp",20.55,18.95,lift=2.51)
    s.put("hvd_pave_w",23.0,22.0)
    s.put("hvd_oillamp",24.80,22.22,lift=1.07)
    s.lamp(24.80,22.22,1.28,"amber")
    s.set(38.95,21.7,REPAIR,162)
    s.put("hvd_pave_n",38.45,21.40)

    # Spare lens racks and charts follow the rounded outer walls on either side.
    s.relief(12.1,31.35,90,"blue")
    s.relief(46.25,33.1,270,"blue")
    s.put("hvd_shelf",14.05,35.6,direction=75)
    s.put("hvd_shelf",16.95,39.3,direction=22)
    s.put("hvd_oillamp",16.95,39.3,lift=2.51)
    s.set(21.0,35.48,STUDY,10)
    s.put("hvd_pave_n",20.8,35.59)
    s.put("hvd_shelf",43.65,36.65,direction=270)
    s.put("hvd_oillamp",43.65,36.65,lift=2.51)
    s.put("hvd_armillary",38.95,38.6)
    s.lamp(38.95,38.6,1.9,"amber")

    s.relief(21.05,43.7,0,"blue")
    s.relief(38.6,44.7,0,"blue")
    s.put("hvd_mounttrim",30,31)
    s.put("hvd_gatecrest",30,46.4)
    s.put("hvd_guide",24.7,29.65)
    s.put("hvd_guide",35.38,29.65)
    s.lamp(30,46.15,1.5,"violet")


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
    s.arch(30.0,17.1,0,"blue",5.0)
    s.put("hvd_pavilion",29.9,57.8,base=15.0)
    s.lamp(22.8,15.05,1.25,"amber",5.0)
    s.put("hvd_oillamp",22.72,15.75,lift=1.07,base=5.0)
    s.set(43.6,34.6,STATION,245,10.0)
    s.set(15.2,55.7,GUARD,18,15.0)
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
    for x,y,d in ((51,17.5,124),(19.1,27.45,88),(17.1,34.65,86)):
        s.set(x,y,GUARD,d,5.0)
    for x,y,d in ((20.9,17.3,9),(53.1,26.4,185),(25,36.5,162),(45,36.3,220)):
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
    s.put("hvd_altarbase",38.2,55.4,direction=90,base=9.2)
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
    for x,y,d,z in ((21.1,17.0,9,5),(47.7,16.05,-12,5),(24.4,54.4,165,10),
                    (45.3,55.7,227,10),(18.4,49.0,96,10),(51.8,49.0,281,10)):
        s.set(x,y,STATION,d,z)
    for x,y,d in ((10.3,44.2,90),(59,45.8,269),(53.4,53.6,355)):
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
