"""Room-by-room dressing on the existing observatory floor plans."""

from math import cos, radians, sin

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
    "hvd_wallchart": "Mosazná mapa na stěně",
    "hvd_lining": "Kamenná obezdívka s mosaznou lištou",
    "hvd_lensrack": "Vestavěná skříň s čočkami",
    "hvd_wallring": "Mosazné táhlo v překladu",
    "hvd_bookpanel": "Zadní police archivu",
    "hvd_stonepanel": "Kamenný kryt v ostění",
    "hvd_skyport": "Nebeský oblouk s lampami v kameni",
    "hvd_skyrail": "Balustráda Horních sfér",
    "hvd_skybay": "Otevřená strážnice pod klenbou",
    "hvd_hangpier": "Kamenná opěra nad mraky",
    "hvd_skywalk": "Kamenná dráha s mosaznou linií",
    "hvd_orrery": "Kamenný orloj druhé oblohy",
    "hvd_apsewall": "Členěná stěna se soklem",
    "hvd_eavearch": "Klenutá opěra servisní lávky",
    "hvd_beactower": "Signální věž visutých ochozů",
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

    def signpost(self, x, y, shade="blue", direction=0, base=None):
        head = "hvd_amberpost" if shade == "amber" else "hvd_bluepost"
        self.put(head, x, y, direction=direction, base=base)
        self.lamp(x, y, 2.09, shade, base)

    def wall(self, x, y, direction, fixture=None, tint='blue', base=None, *, built=False):
        if not built:
            self.put('hvd_lining', x, y, direction=direction, base=base)
        if fixture:
            model = {'chart': 'hvd_wallchart', 'rack': 'hvd_lensrack'}[fixture]
            self.put(model, x, y, direction=direction, base=base)
        self.set(x, y, (('hvd_sconce', None, -2.16, -.17, 2.13, 0),), direction, base)
        a = radians(direction)
        self.lamp(x - 2.16*cos(a) + .36*sin(a), y - 2.16*sin(a) - .36*cos(a), 2.51, tint, base)

    def sky(self, x, y, tint, base=None):
        self.put('hvd_skyport', x, y, base=base)
        for side in (-1, 1):
            self.lamp(x + side*2.79, y - .72, 2.63, tint, base)

    def bay(self, x, y, tint, direction=0, base=None):
        self.put('hvd_skybay', x, y, direction=direction, base=base)
        self.set(x, y, (('hvd_sconce', None, -2.61, 1.38, 2.00, 0),
                        ('hvd_sconce', None, 2.61, 1.38, 2.00, 0)), direction, base)
        a = radians(direction)
        for dx in (-2.61, 2.61):
            self.lamp(x + dx*cos(a) - 1.10*sin(a), y + dx*sin(a) + 1.10*cos(a), 2.41, tint, base)

    def rail(self, x, y, count, dx, dy, direction, base):
        self.line('hvd_skyrail', x, y, count, dx, dy, direction, base=base)

    def service_niche(self, x, y, opens_east, base):
        # The stone lining joins both jambs so the sliding stone is the only opening.
        side = -1 if opens_east else 1
        self.put('hvd_apsewall',x + 2.42*side,y+2.47,base=base)
        self.put('hvd_apsewall',x + 2.42*side,y-2.47,direction=180,base=base)
        self.put('hvd_apsewall',x + 4.84*side,y,direction=-90*side,base=base)

    def bridge(self, x, shade):
        self.put("hvd_bridgewall", x, 35, base=5.0)
        for y, z in ((25, 5.03), (30.25, 6.55), (39.75, 6.55), (45, 5.02)):
            for side in (-1, 1):
                dx = (2.0 if y in (25, 45) else 1.54) * side
                self.put("hvd_amberpost" if shade == "amber" else "hvd_bluepost", x + dx, y, base=z)
            if y in (30.25, 39.75):
                for side in (-1,1):
                    self.lamp(x + 1.54*side, y, 2.06, shade, z)

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
    s.area.lighting.update(MoonAmbientColor=color(78,89,119), MoonDiffuseColor=color(171,183,211))
    s.wall(8.10,14.4,90,'chart','amber',built=True)
    s.wall(8.10,19.4,90,'rack','blue',built=True)
    s.wall(22.15,9.10,180,None,'amber',built=True)
    s.put('hvd_openbook',9.12,14.67,lift=.88,direction=81)
    s.put('hvd_oillamp',9.13,13.52,lift=1.07)
    s.lamp(9.13,13.52,1.3,'amber')
    s.set(10.0,10.7,SUPPLIES,180)
    s.put('hvd_runner',15.4,28.0)
    s.put('hvd_runner',15.4,34.8)
    s.wall(13.08,27.8,90,None,'blue',built=True)
    s.wall(17.72,35.10,270,None,'blue',built=True)

    # Working archive. The ordinary cabinet at the back of the side bay matches the nearby shelving.
    s.wall(7.10,51.7,90,'rack','blue',built=True)
    s.wall(25.41,44.0,270,'chart','amber',built=True)
    s.wall(12.83,55.50,0,'rack','amber',built=True)
    s.put('hvd_shelf',17.06,55.20)
    s.wall(20.65,54.8,0,None,'blue',built=True)
    s.put('hvd_armillary',10.18,53.55)
    s.lamp(10.18,53.55,2.04,'blue')
    s.set(23.49,46.1,REPAIR,270)
    s.put('hvd_pave_n',14.25,47.8)

    # Each side of the long east wing has its own role. Aisles and doorways remain open.
    for y,kind in ((14.4,'rack'),(23.9,'chart'),(33.8,'rack')):
        s.wall(64.10,y,270,kind,'amber',built=True)
    for y,kind in ((22.9,'rack'),(31.2,'chart')):
        s.wall(48.10,y,90,kind,'blue',built=True)
    s.wall(55.2,10.60,180,'chart','blue',built=True)
    s.wall(60.45,10.60,180,'rack','amber',built=True)
    s.set(62.56,23.95,STUDY,270)
    s.wall(50.52,38.6,0,None,'blue',built=True)
    s.put('hvd_runner',55.55,35.0)


def workshops(s):
    s.area.lighting.update(FogClipDist=flt(104.0), MoonAmbientColor=color(104,112,141),
                           MoonDiffuseColor=color(196,191,210))
    # Two windbreaks close the work yards on opposite sides of the service axis.
    s.bay(16.13, 17.43, 'amber')
    s.bay(34.05, 13.28, 'blue', 180)
    s.put('hvd_tools', 17.03, 16.13, lift=.89, direction=80)
    s.put('hvd_oillamp', 17.02, 16.86, lift=1.07)
    s.lamp(17.02, 16.86, 1.30, 'amber')
    s.put('hvd_lensrack', 13.98, 18.98)
    s.put('hvd_hoist', 38.05, 17.28, direction=180)
    # The forge, anvil and bench each have their own usable space under the eastern roof.
    s.set(35.32, 14.77, REPAIR[:5], 180)
    s.set(36.11, 11.82, SUPPLIES[:6], 180)
    s.put('hvd_shelf',34.13,11.65,direction=180)
    s.sky(25, 23.85, 'amber')
    s.sky(25, 49.8, 'blue')
    s.bridge(25, 'amber')
    for y in (16.8, 54.2):
        s.put('hvd_skywalk', 25, y)
    s.rail(12.3, 20.75, 2, 4.89, 0, 0, 5)
    s.rail(31.4, 20.75, 2, 4.89, 0, 0, 5)
    for x,y,z in ((17.8,20.4,5),(31.8,20.4,5),(17.9,50.55,5),(32,50.55,5)):
        s.put('hvd_hangpier', x, y, base=z)

    s.put('hvd_octagon',25,64.21,name='Kupole na horní servisní podestě')
    s.lamp(25,60.12,2.61,'violet')
    s.bay(15.45, 62.5, 'blue')
    s.bay(36.5, 62.0, 'amber')
    s.set(15.2, 62.92, SUPPLIES, 0)
    s.set(36.25, 62.39, REPAIR, 0)
    s.rail(14.5, 50.44, 2, 4.90, 0, 0, 5)
    s.rail(31.1, 50.44, 3, 4.90, 0, 0, 5)
    s.put('hvd_armillary', 44.0, 57.9)
    s.lamp(44.0, 57.9, 1.95, 'blue')
    for x,y,z,angle in ((8,14,-1.0,70),(42,17,-1.7,130),(9,55,-2.0,18),(51.2,66.6,-2.6,3)):
        s.put('hvd_crag', x, y, base=z, direction=angle)
    s.clouds([(8,36,-10,14),(36,41,-11,133)], [(7,36,-13,38),(42,42,-11,52)])


def dome(s):
    s.area.lighting.update(FogClipDist=flt(61.0),MoonAmbientColor=color(92,103,142),
                           MoonDiffuseColor=color(189,191,223))
    for x,y,angle,item,light in (
        (22.85,17.10,180,'chart','amber'),(35.3,17.12,180,'rack','blue'),
        (13.30,33.65,90,'rack','blue'),(13.30,39.2,90,'chart','blue'),
        (20.78,45.90,0,'rack','amber'),(24.83,45.90,0,None,'blue'),
        (36.44,45.90,0,'chart','blue'),(39.96,45.90,0,None,'amber'),
        (46.70,34.10,270,'rack','blue'),(46.70,40.0,270,'chart','amber'),
        (41.45,12.35,180,None,'blue'),
    ):
        s.wall(x,y,angle,item,light,built=True)
    s.put('hvd_oillamp',23.99,18.94,lift=1.07)
    s.lamp(23.99,18.94,1.32,'amber')
    s.put('hvd_openbook',22.73,18.78,lift=.88,direction=12)
    s.put('hvd_tools',23.51,19.03,lift=.89,direction=30)
    s.set(45.00,35.52,REPAIR[:8],270)
    s.set(15.03,37.61,STUDY,90)
    s.put('hvd_armillary',36.87,44.26)
    s.lamp(36.87,44.26,1.99,'amber')
    s.put('hvd_mounttrim',30,31)
    s.put('hvd_guide',24.7,29.65)
    s.put('hvd_guide',35.38,29.65)


def steps(s):
    s.area.lighting.update(FogClipDist=flt(130.0), MoonAmbientColor=color(96,113,162),
                           MoonDiffuseColor=color(210,217,246))
    s.sky(35, 11.35, 'blue', 5)
    s.sky(35, 80.0, 'amber', 20)
    for y,z in ((15.0,5),(33.1,10),(38.0,10),(53.0,15),(57.9,15),(74.4,20)):
        s.put('hvd_skywalk', 35, y, base=z)
    # Continuous protective edges follow the highest part of each retaining wall.
    for y,z in ((30.53,10),(50.53,15),(70.53,20)):
        s.rail(17.2, y, 3, 4.90, 0, 0, z)
        s.rail(43, y, 3, 4.90, 0, 0, z)
        for x in (21.2, 48.8):
            s.put('hvd_hangpier', x, y, base=z)
    for x in (30.95,39.05):
        for y,z in ((32.45,10),(52.45,15),(72.45,20)):
            s.signpost(x,y,'blue',base=z)
    # A hidden service entrance lies behind the low western retaining wall.
    s.service_niche(15.62,16.65,True,5)
    s.bay(13.3,17.65,'amber',90,5)
    s.put('hvd_lining',19.55,19.88,base=5)
    s.rail(20.32, 13.34, 1, 0, 0, 90, 5)
    s.put('hvd_oillamp', 27.01, 15.91, lift=1.07, base=5)
    s.lamp(27.01, 15.91, 1.30, 'amber', 5)
    s.rail(46.7, 12.8, 2, 4.90, 0, 0, 5)
    s.bay(50.0, 18.4, 'blue', base=5)
    s.set(50.0,18.95,SUPPLIES,0,5)
    s.put('hvd_orrery', 49.05, 37.04, direction=15, base=10)
    s.lamp(49.05,36.58,3.25,'violet',10)
    s.bay(19.6,36.6,'blue',base=10)
    s.set(19.6,37.05,STATION,0,10)
    s.put('hvd_eddy',35,54.85,base=15.02)
    s.lamp(35,54.85,3.95,'blue',15)
    s.bay(19.85,57.95,'amber',base=15)
    s.set(19.73,58.36,GUARD,0,15)
    s.bay(50.1,57.8,'blue',base=15)
    s.service_niche(54.90,54.10,False,15)
    for x in (20.6,49.4):
        s.bay(x,76.1,'amber',base=20)
        s.rail(x,80.6,3,4.90,0,0,20)
    s.clouds([(7,23,-8,24),(50,41,-10,57),(53,67,-8,103),(19,76,-11,18)],
             [(8,41,-12,14),(59,36,-10,126),(7,61,-8,135),(64,61,-10,23)])


def walks(s):
    s.area.lighting.update(FogClipDist=flt(119.0), MoonAmbientColor=color(94,111,156),
                           MoonDiffuseColor=color(194,212,246))
    for x,tint in ((25,'blue'),(55,'amber')):
        s.sky(x,22.55,tint)
        s.sky(x,49.55,tint)
        s.bridge(x,tint)
        for y in (17.4,54.1):
            s.put('hvd_skywalk',x,y)
        for px,y in ((x-3.55,20.68),(x+3.55,20.68),(x-3.55,50.3),(x+3.55,50.3)):
            s.put('hvd_hangpier',px,y)
    for x,count in ((13.0,2),(31.8,4),(62.4,2)):
        s.rail(x,20.86,count,4.91,0,0,5)
    for x,y,d in ((11.6,56.2,90),(11.6,61.08,90),(68.8,53.2,90),(37.7,55.8,90),
                  (47.1,54.9,90),(20.9,65.9,0),(25.8,65.9,0),(56.4,65.9,0)):
        s.put('hvd_skyrail',x,y,direction=d)
    s.bay(19.0,62.6,'blue')
    s.bay(63.0,62.6,'amber')
    s.put('hvd_beactower',63.0,67.7)
    s.lamp(63.0,67.7,7.7,'amber')
    s.bay(47.05,18.55,'blue',180)
    s.set(12.98,62.3,SUPPLIES,90)
    s.set(60.18,63.34,STATION,0)
    s.put('hvd_skyrail',68.0,59.63,direction=90)
    s.sky(40,68,'amber')
    s.put('hvd_skywalk',40,64.7)
    s.rail(30.0,67.7,2,4.90,0,0,5)
    s.rail(45.1,67.7,2,4.90,0,0,5)
    s.clouds([(6,34,-9,55),(38,31,-10,88),(72,39,-9,126),(34,56,-8,9)],
             [(11,40,-12,29),(40,41,-12,110),(73,38,-13,91)])


def gate(s):
    s.area.lighting.update(FogClipDist=flt(116.0), MoonAmbientColor=color(101,116,160),
                           MoonDiffuseColor=color(218,209,238))
    s.sky(35,12,'blue',5)
    for y in (16.5,21.4,30.7,38.15):
        s.put('hvd_skywalk',35,y,base=5)
    # The socket court sits between the two working wings. The stone gate has its own ceremonial façade.
    for x in (22.2,47.8):
        s.bay(x,37.9,'blue',base=5)
        s.put('hvd_hangpier',x,50.75,base=10)
    s.bay(20,24.6,'blue',90,5)
    s.bay(54.0,16.9,'amber',270,5)
    s.set(16.18,26.4,GUARD,90,5)
    s.put('hvd_oillamp',44.86,20.99,lift=1.05,base=5)
    s.put('hvd_openbook',43.52,20.88,lift=.88,base=5)
    s.lamp(44.86,20.99,1.28,'amber',5)
    s.wall(44.04,21.39,0,'chart','amber',5)
    s.rail(15.1,33.35,2,0,4.90,90,5)
    s.rail(56.2,27.4,2,0,4.90,90,5)
    s.rail(18.6,50.74,3,4.90,0,0,10)
    s.rail(41.65,50.74,3,4.90,0,0,10)
    s.put('hvd_gatecrest',35,53.33,base=10)
    for x in (25,45):
        s.bay(x,54.6,'amber',base=10)
        s.put('hvd_goldbann',x,55.82,lift=.7,base=10)
    for x in (18.0,52.0):
        s.put('hvd_orrery',x,56.0,base=10)
        s.lamp(x,55.7,3.25,'violet',10)
    s.clouds([(10,51,-8,38),(52,60,-10,109),(56,12,-9,52)],
             [(8,49,-12,23),(65,30,-12,78)])


def summit(s):
    s.area.lighting.update(FogClipDist=flt(116.0), MoonAmbientColor=color(93,110,150),
                           MoonDiffuseColor=color(224,215,244))
    s.sky(35,11.75,'blue',5)
    s.sky(35,58.7,'amber',10)
    for x in (24.6,45.8):
        s.bay(x,20.0,'blue',base=5)
    s.put('hvd_oillamp',26.31,19.03,base=5,lift=1.07)
    s.lamp(26.31,19.03,1.32,'amber',5)
    s.rail(14.1,30.65,3,4.90,0,0,10)
    s.rail(45.7,30.65,3,4.90,0,0,10)
    for x,angle,shade in ((13.1,90,'blue'),(56.9,270,'amber')):
        s.rail(x,39.1,3,0,4.9,90,10)
        s.bay(x,49.4,shade,angle,10)
    for x in (21,49):
        s.bay(x,55.9,'amber',base=10)
        s.put('hvd_orrery',x,60.7,base=10)
        s.put('hvd_hangpier',x,58.85,base=10)
    for y in (16.04,33.7,38.6,43.5,48.4,53.3):
        z=5 if y<20 else 10
        s.put('hvd_skywalk',35,y,base=z)
        if z==10:
            s.put('hvd_pave_n',20,y,base=z)
            s.put('hvd_pave_w',50,y,base=z)
    s.clouds([(13,43,-8,86),(59,42,-9,120),(27,65,-8,58)],
             [(9,37,-12,110),(61,50,-12,19),(29,66,-12,10)])


def study(s):
    s.area.lighting.update(FogClipDist=flt(48.0),MoonAmbientColor=color(98,89,112),
                           MoonDiffuseColor=color(188,174,208))
    # This compact room has one writing desk, a west filing bay and a separate optics bench.
    s.wall(3.25,12.85,90,'chart','amber',built=True)
    s.wall(7.22,20.90,0,'rack','amber',built=True)
    s.wall(11.73,20.90,0,'chart','blue',built=True)
    s.wall(15.0,12.85,270,'rack','blue',built=True)
    s.wall(12.56,8.30,180,None,'amber',built=True)
    s.put('hvd_oillamp',5.09,13.24,lift=1.07)
    s.lamp(5.09,13.24,1.31,'amber')
    s.put('hvd_openbook',4.97,12.38,lift=.88,direction=90)
    s.put('hvd_tools',5.29,12.91,lift=.89,direction=80)
    s.put(178,6.40,12.66,direction=90,name='Lavice u zápisů')
    s.put('hvd_shelf',3.60,16.37,direction=90)
    s.put('hvd_armillary',13.02,14.33,direction=270)
    s.lamp(13.02,14.33,1.96,'blue')
    s.set(12.64,11.9,REPAIR[:5],270)
    s.put('hvd_pave_n',9.42,14.98)
    s.put('hvd_sconce',19.11,20.86,direction=270,lift=1.55)
    s.lamp(18.80,20.86,1.98,'blue')


def eave(s):
    s.area.lighting.update(FogClipDist=flt(105.0), MoonAmbientColor=color(85,101,146),
                           MoonDiffuseColor=color(170,189,232))
    s.bay(31.98,19.20,'amber',base=5)
    s.set(33.33,19.80,SUPPLIES,0,5)
    s.bridge(25,'blue')
    s.rail(14.3,21.35,2,4.90,0,0,5)
    for y,z in ((23.0,5),(34.75,6.65),(49.8,5)):
        s.put('hvd_eavearch',25,y,base=z)
        for side in (-1,1):
            s.set(25+side*3.1,y-1.95,(('hvd_sconce',None,0,0,2.05,0),),base=z)
            s.lamp(25+side*3.1,y-2.35,2.54,'blue',z)
    s.bay(34.6,58.55,'amber',base=5)
    s.rail(38.68,56.23,1,0,0,90,5)
    s.put('hvd_crate',35.86,57.40,direction=26,base=5)
    s.put('hvd_skywalk',25,55.4,base=5)
    s.put('hvd_skywalk',25,74.2,base=10)
    s.bay(36.0,75.85,'blue',base=10)
    s.rail(14.8,70.83,2,4.90,0,0,10)
    s.clouds([(5,42,-11,90),(42,32,-11,14)],[(7,30,-10,32),(42,39,-10,49)])


def dress_areas(zones):
    designers = (mountain, halls, workshops, dome, steps, walks, gate, summit, study, eave)
    for area, design in zip(zones, designers, strict=True):
        design(Dress(area))
