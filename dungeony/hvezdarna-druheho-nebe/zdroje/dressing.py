"""Room-by-room dressing on the existing observatory floor plans."""

from math import cos, radians, sin

from aurora import bite, flt, integer
from furnishings import SCENERY as ROOM_FURNISHINGS
from interiors import YARD_MODELS
from lightart import SCENERY as LINK_SCENERY
from plan import JOINS, TILE, ZONES
from world import color

from gateart import GATE


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
NAMES.update((model, name) for model, (name, _) in (ROOM_FURNISHINGS | LINK_SCENERY).items())

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
                          (36.9,23.7,-1.1,30),(46.5,26.7,-1.15,21),(60.0,8.8,-1.9,27)):
        s.put("hvd_crag",x,y,base=z,direction=heading)
    for x,y,a in ((14.1,12.5,36),(30.4,8.7,68),(41.8,18.88,21),(65.1,29.4,82)):
        s.put("hvd_snowbank",x,y,direction=a)
    s.put("hvd_flankwalls",13,33.45)
    for x in (8.1,17.9):
        s.put("hvd_sconce",x,32.25,lift=2.36)
        s.lamp(x,31.93,2.76,"amber")
    # The cleft sits behind two changes of direction and the near side of a spur.
    for x,y,z,heading in ((58.5,19.5,-.35,5),(62.55,22.0,-.42,83),(68.4,19.1,-.4,-5),
                         (73.2,29.5,-.48,5),(77.45,27.4,-.28,16),(81,20.3,-.38,-10),
                         (87.65,20.45,-.28,107),(87.64,29.6,-.34,83)):
        s.put("hvd_talus",x,y,base=z,direction=heading)
    for x,y,a in ((62.0,12.8,28),(70.55,28.5,27),(79.0,25.84,124),(86.46,28.45,30)):
        s.put("hvd_rubble",x,y,direction=a)


def halls(s):
    s.area.lighting.update(MoonAmbientColor=color(81,88,109), MoonDiffuseColor=color(193,183,170))
    # Ohlašovna. Zápis a nástroj obsluhy jsou na stejné bezpečné straně.
    s.put('hvd_register',12.40,23.05,name='Pult služby a kniha střídání')
    s.wall(13.65,24.09,0,'chart','amber',built=True)
    s.put(383,13.19,22.82,lift=.89,name='Svíce ohlašovny')
    s.lamp(13.19,22.82,1.15,'amber')
    s.put(178,8.12,18.9,direction=90,name='Lavice u ohlašovny')
    s.wall(13.2,10.70,180,None,'blue',built=True)
    s.put('hvd_drawers',18.14,11.18,direction=180,name='Výdejní zásuvky obsluhy clon')
    s.put('hvd_lining',20.47,18.79,direction=270,name='Kamenná opěra nouzového uzávěru')
    s.put('hvd_sconce',19.5,20.06,lift=2.12)
    s.lamp(19.5,19.88,2.52,'amber')

    # U každé clony je v kameni vidět přívod, výklenky slouží jako kryt.
    s.wall(32.48,20.12,0,None,'amber',built=True)
    s.put(287,32.48,19.51,name='Sklopná lavice v bezpečnostním výklenku')
    s.put('hvd_crate',39.54,10.46,direction=180,name='Odložené krytky vysílačů')
    s.lamp(39.6,10.64,1.27,'blue')
    s.put('hvd_oillamp',39.54,10.46,lift=.74)

    # Filtrovna před ohybem a severní servisní chodba.
    s.put('hvd_filtergrid',58.53,22.12,direction=270)
    s.wall(56.40,25.94,0,'rack','amber',built=True)
    s.put('hvd_filterbench',56.02,19.0,direction=180)
    s.lamp(56.02,19.07,1.42,'blue')
    s.wall(47.12,22.40,90,None,'blue',built=True)
    s.wall(52.59,32.10,270,'chart','blue',built=True)
    s.put('hvd_crate',52.06,35.36,direction=270,name='Značené bedny s náhradními rámy')
    s.wall(49.34,48.08,0,None,'blue',built=True)
    s.put('hvd_drawers',54.59,44.8,direction=270,name='Evidenční zásuvky se značkami filtrů')
    s.wall(37.8,47.70,0,None,'blue',built=True)
    s.wall(29.0,42.31,180,None,'amber',built=True)

    # Archiv má vlastní čtecí zákoutí a pracovní úložný kout.
    s.wall(11.92,39.82,180,'chart','amber',built=True)
    s.put('hvd_shelf',10.44,39.99,direction=180,name='Police starých protokolů')
    s.wall(18.37,59.26,0,None,'amber',built=True)
    s.put('hvd_drawers',17.66,58.87,name='Zásuvky starých služebních protokolů')
    s.put('hvd_arc_cabinet',12.2,59.07,name='Archiv průchodů a clon')
    s.put('hvd_lectern',21.67,54.11,direction=270,name='Pult s indexem filtrů')
    s.put('hvd_openbook',21.67,54.11,direction=270,lift=1.12,name='Rejstřík filtrů')
    s.wall(22.93,55.9,270,'chart','amber',built=True)
    s.put('hvd_crate',22.95,42.21,direction=270,name='Příjem použitých filtrů')


def workshops(s):
    s.area.lighting.update(FogClipDist=flt(104.0), MoonAmbientColor=color(104,112,141),
                           MoonDiffuseColor=color(196,191,210))
    for x,y,angle,tint in ((50.15,6.9,90,'amber'),(55.84,6.9,270,'amber'),
                            (45.62,17.83,0,'amber'),(51.11,17.83,0,'amber'),
                            (56.82,17.83,0,'blue'),(55.21,57.73,0,'blue')):
        s.wall(x,y,angle,None,tint,built=True)
    for model,((x,y),(xx,yy)) in YARD_MODELS.items():
        s.put(model,(x+xx)/2,(y+yy)/2,name='Obvodové zdivo dílenského dvora')
    # The laboratory eaves and the forge flue anchor to opposite walls of one court.
    s.put('hvd_lab_eaves',17.10,19.21)
    s.put('hvd_forge_flue',32.55,10.71)
    for x in (13.02,19.72):
        s.put('hvd_sconce',x,19.53,lift=2.39)
        s.lamp(x,19.22,2.70,'amber')
    s.put('hvd_tools', 17.03, 16.13, lift=.89, direction=80)
    s.put('hvd_oillamp', 17.02, 16.86, lift=1.07)
    s.lamp(17.02, 16.86, 1.30, 'amber')
    s.put('hvd_lensrack', 13.98, 19.06)
    s.put('hvd_lensrack', 21.40, 19.09, name='Sady čoček k proměření')
    s.put('hvd_grinder', 11.75, 13.24, direction=90, name='Upínací stolice optického skla')
    s.put('hvd_shelf', 11.17, 18.24, direction=90, name='Vysoušení leštěných čoček')
    s.put('hvd_hoist', 38.05, 18.9, direction=180)
    # The forge, anvil and bench each have their own usable space under the eastern roof.
    s.put('hvd_smithbench',35.32,11.92,direction=180)
    s.put('hvd_planrail',35.25,10.48,direction=180,name='Výkresy odlité objímky')
    s.put('hvd_crate',37.20,11.23,direction=180,name='Bedna s uhlím a tukem')
    s.put(108,38.55,11.56,direction=90,name='Přířezy pro opravované rámy')
    s.put(49,29.5,11.02,direction=23,name='Kádě ke kalení spony')
    s.lamp(32.55,12.8,1.55,'orange')
    s.sky(25, 23.85, 'amber')
    s.sky(25, 49.8, 'blue')
    s.bridge(25, 'amber')
    for y in (16.8, 54.2):
        s.put('hvd_skywalk', 25, y)
    for x,y,z in ((17.8,20.4,5),(31.8,20.4,5),(17.9,50.55,5),(32,50.55,5)):
        s.put('hvd_hangpier', x, y, base=z)

    s.put('hvd_octagon',30,79.4,name='Průčelí vstupu do Kopule')
    s.lamp(30,73.12,2.61,'violet')
    s.bay(15.45, 62.5, 'blue', model='hvd_workroof')
    s.bay(36.5, 62.0, 'amber', model='hvd_workroof')
    s.put('hvd_grinder',15.2,62.91)
    s.put('hvd_lensrack',12.02,61.32,direction=90,name='Odnímatelné okuláry před výstupem')
    s.put('hvd_capstan',36.25,62.38)
    s.put(361,37.79,62.94,direction=47,name='Rezervní lano k bubnu')
    s.rail(14.5, 50.44, 2, 4.90, 0, 0, 5)
    s.rail(31.1, 50.44, 3, 4.90, 0, 0, 5)
    s.put('hvd_crate',48.88,58.43,direction=180,name='Bedna s náhradními úvazy')
    s.put(361,47.83,58.19,direction=52,name='Svinuté lano pro přenášení čoček')
    for x,y,z,angle in ((8,14,-1.0,70),(44.1,5.5,-1.7,130),(9,55,-2.0,18),(51.2,66.6,-2.6,3)):
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
    for x,y,heading in ((14.01,30.1,270),(14.01,40.97,270),(45.99,29.88,90),
                        (45.99,40.98,90),(22.65,45.14,180),(37.30,45.14,180)):
        s.put('hvd_cupolarib',x,y,direction=heading)
    s.put('hvd_armillary',38.86,42.65)
    s.lamp(38.86,42.65,1.99,'amber')
    s.put('hvd_mounttrim',30,31)
    s.put('hvd_guide',24.7,29.65)
    s.put('hvd_guide',35.38,29.65)


def stair_rails(s):
    zone = ZONES['steps']
    courts = {(x,y) for left,bottom,right,top in zone.rooms
              for x in range(left,right) for y in range(bottom,top)}
    openings = [join.point('steps') for join in JOINS if 'steps' in (join.first,join.second)]
    for x,y in sorted(courts - set(zone.stairs)):
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
            if (x+dx,y+dy) in courts:
                continue
            edge_x,edge_y = TILE*(x+.5+.5*dx),TILE*(y+.5+.5*dy)
            for half in (-2.45,2.45):
                px,py = edge_x + half*dy,edge_y + half*dx
                if any(abs(px-ox)<6.15 and abs(py-oy)<6.15 for ox,oy in openings):
                    continue
                s.put('hvd_skyrail',px-.44*dx,py-.44*dy,direction=90 if dx else 0)


def steps(s):
    s.area.lighting.update(FogClipDist=flt(147.0), MoonAmbientColor=color(89,102,142),
                           MoonDiffuseColor=color(206,218,244))
    stair_rails(s)
    s.sky(30,2.7,'blue',5)
    s.sky(67.4,5,'blue',5,direction=-90)
    s.sky(25,97.3,'amber',20)
    s.put('hvd_stairaxis',30,12.7,base=5)
    s.put('hvd_stairaxis',34.73,35.02,direction=68,base=10,name='Zaměření druhého schodiště')
    s.put('hvd_stairaxis',29.98,77.0,base=20,name='Zaměření horní terasy')
    for x,y,shade in ((21.5,18.6,'amber'),(38.55,18.6,'amber'),
                      (31.25,38.6,'blue'),(48.72,38.6,'blue'),
                      (21.52,58.65,'amber'),(38.55,58.65,'amber')):
        s.signpost(x,y,shade)
    for x,y in ((12.0,16.3),(47.94,16.3),(13.2,37.25),(55.31,35.6),
                (11.2,55.45),(57.73,55.43),(12.8,78.8),(47.1,77.45),(59.0,7.92)):
        s.put('hvd_hangpier',x,y)
    s.bay(12.56,15.4,'amber',90)
    s.put('hvd_oillamp',14.83,16.48,lift=1.05)
    s.lamp(14.83,16.48,1.31,'amber')
    s.put('hvd_beactower',46.10,16.87)
    s.lamp(46.10,16.87,7.65,'blue')

    # Měřičská podesta má orloj a stojan na záznamy podél kamenné hrany.
    s.put('hvd_orrery',54.55,36.27,direction=21)
    s.lamp(54.55,35.64,3.2,'violet')
    s.bay(15.28,36.8,'blue',base=10)
    s.put('hvd_logstand',16.16,36.63,base=10,name='Záznamy výšek na schodišti')
    s.put('hvd_openbook',16.05,36.6,lift=.90,base=10)

    # Bouřná podesta. Kryt i vybavení hlídky stojí při balustrádách.
    s.put('hvd_eddy',33,54.65,base=15.02)
    s.lamp(33,54.65,3.95,'blue',15)
    s.bay(13.3,55.6,'amber',90,15)
    s.put('hvd_wicktable',51.04,58.3,base=15,name='Sušení knotů na horní podestě')
    s.put('hvd_arc_cabinet',54.53,58.12,base=15,name='Skříň hlídky v závětří')
    s.put('hvd_sconce',54.5,57.75,lift=2.7,base=15)
    s.lamp(54.5,57.54,2.96,'blue',15)
    s.bay(15.75,84.0,'amber',90,20)
    s.put('hvd_spearrack',16.82,84.36,direction=90,base=20)
    s.put('hvd_goldbann',18.13,87.7,lift=.54,base=20)
    s.put('hvd_beactower',42.37,84.19,base=20)
    s.lamp(42.37,84.19,7.62,'amber',20)
    s.clouds([(5,20,-8,24),(52,39,-10,57),(57,66,-8,103),(15,89,-9,18)],
             [(8,41,-12,14),(59,36,-10,126),(7,61,-8,135),(64,61,-10,23)])


def walks(s):
    s.area.lighting.update(FogClipDist=flt(119.0), MoonAmbientColor=color(94,111,156),
                           MoonDiffuseColor=color(194,212,246))
    s.sky(2.65,15,'blue',5,direction=90)
    for x in (70.85,79.15):
        s.rail(x,8.3,2,0,4.88,90,5)
    s.put('hvd_lining',72.26,5.63,direction=90,base=5)
    s.put('hvd_lining',77.74,5.67,direction=270,base=5)
    s.put('hvd_wallfoot',76.8,13.53,direction=270,base=5,name='Zídka za skladovým výklenkem')
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
    for x,angle in ((31.1,90),(38.9,270)):
        s.put('hvd_tallpier',x,67.98,base=10)
        s.put('hvd_sconce',x,66.99,lift=2.44,base=10,direction=angle)
        s.lamp(x,66.76,2.77,'violet',10)
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
    s.wall(11.49,25.89,270,None,'amber',built=True)
    s.put('hvd_crate',6.62,21.34,direction=90,name='Záložní olej a motouz')
    s.wall(26.38,38.42,270,'chart','amber',built=True)
    s.put('hvd_oillamp',25.33,37.51,lift=1.02)
    s.lamp(25.33,37.51,1.34,'amber')
    s.put('hvd_pave_w',23.92,38.43,name='Vyvýšená dlažba v psacím výklenku')
    s.put('hvd_drawers',12.4,42.38)
    s.put('hvd_shelf',13.14,31.42,direction=180,name='Sešity noční služby')
    s.put('hvd_planrail',14.0,31.08,direction=180,name='Sestava výkresů služebního výstupu')
    s.wall(5.32,34.3,90,'chart','blue',built=True)
    s.put('hvd_armillary',6.54,39.86,name='Soukromý měřicí kruh')
    s.put(178,21.16,36.19,direction=90,name='Nízká lavice pod výkresy')
    s.put('hvd_lectern',6.93,41.49,direction=90,name='Rozložené pracovní desky')
    s.put('hvd_openbook',6.93,41.49,direction=90,lift=1.15)
    s.put('hvd_shelf',15.62,55.77,direction=90,name='Podklady k horní službě')
    s.wall(24.84,54.2,270,'rack','blue',built=True)
    s.put('hvd_lensrack',28.65,75.45,direction=270,name='Náhradní okuláry ve služební štole')
    s.put('hvd_crate',7.66,103.87,direction=90,name='Bedna údržby')
    s.put('hvd_grinder',26.72,134.85,direction=90,name='Přípravek na náhradní čočky')
    for x,y,angle,tint in ((20.14,67.8,90,'blue'),(25.89,81.6,270,'amber'),
                           (10.12,94.9,90,'blue'),(15.91,112.8,270,'blue'),(22.9,127.35,270,'amber'),
                           (17.12,140.6,90,'blue'),(17.85,153.45,270,'blue')):
        s.wall(x,y,angle,None,tint,built=True)


def dress_areas(zones):
    designers = (camp, mountain, halls, workshops, dome, steps, walks, gate, summit, study)
    for area, design in zip(zones, designers, strict=True):
        design(Dress(area))
