"""Room-by-room dressing on the existing observatory floor plans."""

from math import cos, radians, sin

from aurora import bite, flt, integer
from furnishings import SCENERY as ROOM_FURNISHINGS
from lightart import SCENERY as LINK_SCENERY
from world import color

from gateart import GATE


NAMES = {
    "hvd_secretrock": "Zasněžený výčnělek",
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
NAMES.update((model, name) for model, (name, _) in (ROOM_FURNISHINGS | LINK_SCENERY).items())

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

    def sky(self, x, y, tint, base=None, direction=0):
        self.put('hvd_skyport', x, y, base=base, direction=direction)
        angle = radians(direction)
        for side in (-1, 1):
            self.lamp(x + side*2.79*cos(angle) + .72*sin(angle),
                      y + side*2.79*sin(angle) - .72*cos(angle), 2.63, tint, base)

    def bay(self, x, y, tint, direction=0, base=None, *, model='hvd_skybay'):
        self.put(model, x, y, direction=direction, base=base)
        self.set(x, y, (('hvd_sconce', None, -2.61, 1.38, 2.00, 0),
                        ('hvd_sconce', None, 2.61, 1.38, 2.00, 0)), direction, base)
        a = radians(direction)
        for dx in (-2.61, 2.61):
            self.lamp(x + dx*cos(a) - 1.10*sin(a), y + dx*sin(a) + 1.10*cos(a), 2.41, tint, base)

    def rail(self, x, y, count, dx, dy, direction, base):
        self.line('hvd_skyrail', x, y, count, dx, dy, direction, base=base)

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


def camp(s):
    s.area.lighting.update(ChanceSnow=integer(25), FogClipDist=flt(95.0),
                           MoonAmbientColor=color(79,92,124), MoonDiffuseColor=color(199,210,234))
    s.put("hvd_campshell",15.8,20.35)
    s.put("hvd_campshell",31.7,14.85,direction=176)
    s.set(13.4,21.55,SUPPLIES,8)
    s.set(31.9,14.3,SUPPLIES,174)
    s.put("hvd_oillamp",20.99,22.02,lift=1.07)
    s.lamp(20.99,22.02,1.34,"amber")
    s.put("hvd_skywalk",26,26.2)
    for x in (22.55,29.45):
        s.signpost(x,27.88,"amber")
    s.put("hvd_snowbank",10.7,28.1,direction=30)
    s.put("hvd_crag",36.9,24.8,base=-1.18,direction=70)


def mountain(s):
    s.area.lighting.update(ChanceSnow=integer(27), FogClipDist=flt(96.0),
                           MoonAmbientColor=color(65,80,119), MoonDiffuseColor=color(193,202,229))
    s.put("hvd_rim_roads",26,12,name="Dlážděné rozcestí")
    for x,y,z,heading in ((8,19,-1.05,39),(5.8,30,-1.4,60),(23.1,33.9,-1.0,29),
                          (53.2,24.3,-1.4,46),(48.5,34.9,-1.25,218),(59.3,5.0,-1.9,57)):
        s.put("hvd_crag",x,y,base=z,direction=heading)
    for x,y,a in ((14.1,12.5,36),(32.8,8.7,68),(43.2,20.7,21),(46.9,25.4,56),(65.4,29.4,82)):
        s.put("hvd_snowbank",x,y,direction=a)
    s.put("hvd_flankwalls",13,33.45)
    for x in (8.1,17.9):
        s.put("hvd_sconce",x,32.25,lift=2.36)
        s.lamp(x,31.93,2.76,"amber")
    s.signpost(39.7,29.2,"blue")
    # The dead-end is behind staggered outcrops. Its closed face shares the rock material.
    for x,y,z,a in ((72.7,19.9,-1.21,2),(80.9,20.12,-.97,-11),(83.3,30.08,-.73,10),
                    (90.3,30.0,-1.2,30),(88.0,20.03,-1.32,19)):
        s.put("hvd_secretrock",x,y,base=z,direction=a)
    for x,y,a in ((61.8,19.63,2),(69.1,23.55,27),(77.4,23.0,124),(85.6,27.9,30)):
        s.put("hvd_rubble",x,y,direction=a)


def halls(s):
    s.area.lighting.update(MoonAmbientColor=color(78,89,119), MoonDiffuseColor=color(171,183,211))
    s.wall(8.10,14.4,90,'chart','amber',built=True)
    s.wall(8.10,19.4,90,'rack','blue',built=True)
    s.wall(22.15,9.10,180,None,'amber',built=True)
    s.put('hvd_openbook',9.12,14.67,lift=.88,direction=81)
    s.put('hvd_oillamp',9.13,13.52,lift=1.07)
    s.lamp(9.13,13.52,1.3,'amber')
    s.set(10.0,10.7,SUPPLIES,180)

    # Working archive. The ordinary cabinet at the back of the side bay matches the nearby shelving.
    s.wall(7.10,51.7,90,'rack','blue',built=True)
    s.wall(25.41,51.2,270,'chart','amber',built=True)
    s.wall(12.83,59.30,0,'rack','amber',built=True)
    s.put('hvd_shelf',17.06,58.95)
    s.wall(20.65,59.30,0,None,'blue',built=True)
    s.put('hvd_shelf',9.28,53.99,direction=90,name='Evidence uložených clon')
    s.put(56,22.93,46.42,direction=270,name='Svazek oprav clon')
    s.put('hvd_crate',23.70,46.46,direction=270,name='Příjem použitých filtrů')
    s.put('hvd_pave_n',14.25,47.8)

    # Each side of the long east wing has its own role. Aisles and doorways remain open.
    for y,kind in ((14.4,'rack'),(34.75,'rack')):
        s.wall(64.10,y,270,kind,'amber',built=True)
    for y,kind in ((22.9,'rack'),(31.2,'chart')):
        s.wall(48.10,y,90,kind,'blue',built=True)
    s.wall(55.2,10.60,180,'chart','blue',built=True)
    s.wall(60.45,10.60,180,'rack','amber',built=True)
    s.set(62.65,31.4,STUDY,270)
    s.put('hvd_arc_cabinet',64.08,18.92,direction=270,name='Registry seřizovačů')
    s.wall(50.52,38.6,0,None,'blue',built=True)
    s.put('hvd_runner',55.55,35.0)


def workshops(s):
    s.area.lighting.update(FogClipDist=flt(104.0), MoonAmbientColor=color(104,112,141),
                           MoonDiffuseColor=color(196,191,210))
    s.put('hvd_headhouse',53,2.85,direction=180,base=5)
    s.sky(57.3,55,'blue',5,direction=-90)
    for y in (4.4,8.9,13.2):
        s.put('hvd_skywalk',53,y,base=5)
    for x in (39.3,44.2,49.1):
        s.put('hvd_skywalk',x,16.7,base=5,direction=90)
    for x in (42,47,52,57):
        s.put('hvd_skywalk',x,55,base=5,direction=90)
    # Two windbreaks close the work yards on opposite sides of the service axis.
    s.bay(16.13, 17.43, 'amber', model='hvd_workroof')
    s.bay(34.05, 12.5, 'amber', 180, model='hvd_workroof')
    s.put('hvd_tools', 17.03, 16.13, lift=.89, direction=80)
    s.put('hvd_oillamp', 17.02, 16.86, lift=1.07)
    s.lamp(17.02, 16.86, 1.30, 'amber')
    s.put('hvd_lensrack', 13.98, 18.98)
    s.put('hvd_hoist', 38.05, 18.9, direction=180)
    # The forge, anvil and bench each have their own usable space under the eastern roof.
    s.put('hvd_smithbench',35.32,11.92,direction=180)
    s.put('hvd_crate',36.11,11.90,direction=180,name='Bedna s uhlím a tukem')
    s.sky(25, 23.85, 'amber')
    s.sky(25, 49.8, 'blue')
    s.bridge(25, 'amber')
    for y in (16.8, 54.2):
        s.put('hvd_skywalk', 25, y)
    s.rail(12.3, 20.75, 2, 4.89, 0, 0, 5)
    s.rail(31.4, 20.75, 2, 4.89, 0, 0, 5)
    for x,y,z in ((17.8,20.4,5),(31.8,20.4,5),(17.9,50.55,5),(32,50.55,5)):
        s.put('hvd_hangpier', x, y, base=z)

    s.put('hvd_octagon',30,79.4,name='Průčelí vstupu do Kopule')
    s.lamp(30,73.12,2.61,'violet')
    s.bay(15.45, 62.5, 'blue', model='hvd_workroof')
    s.bay(36.5, 62.0, 'amber', model='hvd_workroof')
    s.put('hvd_grinder',15.2,62.91)
    s.put('hvd_capstan',36.25,62.38)
    s.put(361,37.79,62.94,direction=47,name='Rezervní lano k bubnu')
    s.rail(14.5, 50.44, 2, 4.90, 0, 0, 5)
    s.rail(31.1, 50.44, 3, 4.90, 0, 0, 5)
    for x,y,z,angle in ((8,14,-1.0,70),(46,6,-1.7,130),(9,55,-2.0,18),(51.2,66.6,-2.6,3)):
        s.put('hvd_crag', x, y, base=z, direction=angle)
    s.clouds([(8,36,-10,14),(36,41,-11,133)], [(7,36,-13,38),(42,42,-11,52)])


def dome(s):
    s.area.lighting.update(FogClipDist=flt(61.0),MoonAmbientColor=color(92,103,142),
                           MoonDiffuseColor=color(189,191,223))
    for x,y,angle,item,light in (
        (13.31,32.31,90,'chart','amber'),(35.3,17.12,180,None,'blue'),
        (13.30,39.2,90,None,'blue'),
        (23.01,45.90,0,None,'blue'),(36.44,45.90,0,'chart','blue'),
        (46.70,34.10,270,None,'blue'),(46.70,40.0,270,None,'amber'),
        (41.45,12.35,180,None,'blue'),
    ):
        s.wall(x,y,angle,item,light,built=True)
    s.put(383,13.91,33.32,lift=.88,name='Svíce u pozorovacího deníku')
    s.put(287,45.86,35.52,direction=270,name='Lavice při pozorovacím sále')
    s.put('hvd_lectern',15.34,36.45,direction=90,name='Pult měření polohy hvězd')
    s.put('hvd_openbook',15.29,36.45,direction=90,lift=1.14,name='Rozložený hvězdný katalog')
    s.put('hvd_armillary',36.87,44.26)
    s.lamp(36.87,44.26,1.99,'amber')
    s.put('hvd_mounttrim',30,31)
    s.put('hvd_guide',24.7,29.65)
    s.put('hvd_guide',35.38,29.65)


def steps(s):
    s.area.lighting.update(FogClipDist=flt(130.0), MoonAmbientColor=color(96,113,162),
                           MoonDiffuseColor=color(210,217,246))
    s.sky(30, 2.7, 'blue', 5)
    s.sky(67.4, 5, 'blue', 5, direction=-90)
    s.sky(25, 97.3, 'amber', 20)
    for x,y,z,heading in ((30,6.5,5,0),(25,16,5,0),(25,33.4,10,0),(34,35.8,10,90),
                           (44.9,37.4,10,0),(44.9,53.4,15,0),(38.5,58,15,90),
                           (35,74.9,20,0),(30.3,81.7,20,55),(25,90.1,20,0),
                           (25,94.8,20,0),(45.9,6.8,5,90),(61,5,5,90)):
        s.put('hvd_skywalk',x,y,base=z,direction=heading)
    for row,columns in s.area.stair_columns.items():
        center = 10*columns[0] + 5
        y = 10*(row+1)+.53
        for x in (12.5,17.4,22.3,27.2,32.1,37.0,41.9,46.8,51.7,56.6):
            if abs(x-center)>6.1:
                s.rail(x,y,1,0,0,0,s.area.z_at(y))
        for x in (center-4.3,center+4.3):
            s.signpost(x,y+1.8,'blue')
    s.bay(13.3,17.65,'amber',90,5)
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
    for x in (20.6,49.4):
        s.bay(x,76.1,'amber',base=20)
        s.rail(x,80.6,3,4.90,0,0,20)
    s.clouds([(7,23,-8,24),(50,41,-10,57),(53,67,-8,103),(19,76,-11,18)],
             [(8,41,-12,14),(59,36,-10,126),(7,61,-8,135),(64,61,-10,23)])


def walks(s):
    s.area.lighting.update(FogClipDist=flt(119.0), MoonAmbientColor=color(94,111,156),
                           MoonDiffuseColor=color(194,212,246))
    s.sky(2.65,15,'blue',5,direction=90)
    s.put('hvd_headhouse',75,5.4,direction=180,base=5)
    for x in (70.85,79.15):
        s.rail(x,8.3,2,0,4.88,90,5)
    s.put('hvd_skywalk',75,11.1,base=5)
    for x,tint in ((25,'blue'),(55,'amber')):
        s.sky(x,22.55,tint)
        s.sky(x,49.55,tint)
        s.bridge(x,tint)
        s.put('hvd_bridgeedge',x,35,base=5)
        for y in (17.4,54.1):
            s.put('hvd_skywalk',x,y)
        for px,y in ((x-3.55,20.68),(x+3.55,20.68),(x-3.55,50.3),(x+3.55,50.3)):
            s.put('hvd_hangpier',px,y)
    for x,count in ((13.0,2),(31.8,4),(62.4,2)):
        s.rail(x,20.86,count,4.91,0,0,5)
    for x in (13.35,46.70):
        s.rail(x,11.05,5,4.90,0,0,5)
    for y in (10.85,19.15):
        s.rail(3.32,y,2,4.90,0,0,5)
    s.rail(74.76,19.15,2,4.90,0,0,5)
    for x, tint in ((19, 'blue'), (63, 'amber')):
        s.bay(x,66.8,tint)
    s.put('hvd_beactower',63,68.3)
    s.lamp(63,68.3,7.7,'amber')
    s.bay(47.05,18.55,'blue',180)
    s.put('hvd_spearrack',12.72,64.6,direction=90)
    s.put(178,15.18,65.1,direction=90,name='Lavice pro údržbu zbroje')
    s.put('hvd_wicktable',61.21,67.3)
    for x in (13.0,17.9,22.8,27.7,32.6,37.5,52.5,57.4,62.3,67.2):
        s.rail(x,69.6,1,0,0,0,10)
    for x,y,heading in ((45,64.8,0),(45,68.15,0),(45,82.9,0),(37.2,85.5,90),
                        (32.3,85.5,90),(27.4,85.5,90),(22.5,85.5,90),(15,88,0),(15,103,0)):
        s.put('hvd_skywalk',x,y,direction=heading)
    for x in (11.1,58.9):
        s.rail(x,82.45,2,0,4.89,90,15)
    for x in (10.9,19.1):
        s.rail(x,102.6,2,0,4.89,90,20)
    s.sky(15,107.3,'amber',20)
    s.clouds([(6,34,-9,55),(38,31,-10,88),(72,39,-9,126),(34,56,-8,9)],
             [(11,40,-12,29),(40,41,-12,110),(73,38,-13,91)])


def gate(s):
    s.area.lighting.update(FogClipDist=flt(116.0), MoonAmbientColor=color(101,116,160),
                           MoonDiffuseColor=color(218,209,238))
    s.sky(5,2.7,'blue',5)
    s.sky(65,2.7,'amber',5)
    for y in (16.5,21.4,30.7,38.15):
        s.put('hvd_skywalk',35,y,base=5)
    # The socket court sits between the two working wings. The stone gate has its own ceremonial façade.
    for x in (22.2,47.8):
        s.bay(x,37.9,'blue',base=5)
        s.put('hvd_hangpier',x,50.75,base=10)
    s.bay(20,24.6,'blue',90,5)
    s.bay(54.0,16.9,'amber',270,5)
    s.set(16.18,26.4,GUARD,90,5)
    s.put(383,42.79,20.99,lift=.88,base=5,name='Písařova svíce')
    s.lamp(42.79,20.99,1.13,'amber',5)
    s.rail(15.1,33.35,2,0,4.90,90,5)
    s.rail(56.2,27.4,2,0,4.90,90,5)
    s.rail(18.6,50.74,3,4.90,0,0,10)
    s.rail(41.65,50.74,3,4.90,0,0,10)
    for y in (55,60,65):
        s.put('hvd_skywalk',35,y,base=10)
    s.put('hvd_gatecrest',*GATE,base=10)
    for x in (25,45):
        s.bay(x,54.6,'amber',base=10)
        s.put('hvd_goldbann',x,55.82,lift=.7,base=10)
    s.clouds([(10,51,-8,38),(52,60,-10,109),(56,12,-9,52)],
             [(8,49,-12,23),(65,30,-12,78)])


def summit(s):
    s.area.lighting.update(FogClipDist=flt(116.0), MoonAmbientColor=color(93,110,150),
                           MoonDiffuseColor=color(224,215,244))
    s.sky(35,2.7,'amber',5)
    s.bay(45.8,20.0,'blue',base=5)
    s.put('hvd_oillamp',44.16,14.52,base=5,lift=1.07)
    s.lamp(44.16,14.52,1.32,'amber',5)
    s.rail(14.1,30.65,2,4.90,0,0,10)
    s.rail(34.1,30.65,5,4.90,0,0,10)
    for x,angle,shade in ((13.1,90,'blue'),(56.9,270,'amber')):
        s.rail(x,39.1,3,0,4.9,90,10)
        s.bay(x,49.4,shade,angle,10)
    for x in (21,49):
        s.bay(x,58.0,'amber',base=10)
        s.put('hvd_hangpier',x,58.85,base=10)
    for x,y,z,heading in ((35,8,5,0),(27,15.8,5,60),(25,33.7,10,0),
                            (30.5,38.6,10,45),(35,43.5,10,0),(35,48.4,10,0),(35,53.3,10,0)):
        s.put('hvd_skywalk',x,y,base=z,direction=heading)
    for y in (33.7,38.6,43.5,48.4,53.3):
        s.put('hvd_pave_n',20,y,base=10)
        s.put('hvd_pave_w',50,y,base=10)
    s.clouds([(13,43,-8,86),(59,42,-9,120),(27,65,-8,58)],
             [(9,37,-12,110),(61,50,-12,19),(29,66,-12,10)])


def study(s):
    s.area.lighting.update(MoonAmbientColor=color(79,80,105), MoonDiffuseColor=color(184,168,149))
    s.wall(26.87,39.1,270,'chart','amber',built=True)
    s.put('hvd_oillamp',25.91,38.43,lift=1.01)
    s.lamp(25.94,38.43,1.33,'amber')
    s.put('hvd_shelf',9.35,42.89,name='Sešity noční služby')
    s.wall(5.13,36.2,90,'rack','blue',built=True)
    s.put('hvd_armillary',11.0,34.65,name='Měřicí kruh správkyně')
    s.put('hvd_runner',17.47,38.05)
    s.put('hvd_shelf',21.4,49.1,direction=180,name='Podklady k horní službě')
    s.wall(26.84,53.1,270,'rack','blue',built=True)
    s.wall(7.4,57.9,0,'chart','amber',built=True)
    s.put('hvd_shelf',14.63,57.28,name='Pracovní registry při výstupu')
    s.put('hvd_lensrack',28.7,75.45,direction=270,name='Držák vyřazených čoček')
    s.put('hvd_crate',7.66,103.87,direction=90,name='Bedna údržby')
    s.put('hvd_grinder',26.72,134.85,direction=90,name='Přípravek na náhradní čočky')
    for x,y,angle,tint in ((11.3,23.2,270,'amber'),(20.14,67.8,90,'blue'),(26.0,79.6,270,'amber'),
                           (10.12,94.9,90,'blue'),(15.91,112.8,270,'blue'),(22.9,127.35,270,'amber'),
                           (17.12,140.6,90,'blue'),(17.85,153.45,270,'blue')):
        s.wall(x,y,angle,None,tint,built=True)


def dress_areas(zones):
    designers = (camp, mountain, halls, workshops, dome, steps, walks, gate, summit, study)
    for area, design in zip(zones, designers, strict=True):
        design(Dress(area))
