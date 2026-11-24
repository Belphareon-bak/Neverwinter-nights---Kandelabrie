"""Room-by-room dressing on the existing observatory floor plans."""

from math import cos, radians, sin

from aurora import bite, flt, integer
from furnishings import SCENERY as ROOM_FURNISHINGS
from interiors import YARD_MODELS
from lightart import SCENERY as LINK_SCENERY
from navrh_v21 import HALL_ACCESS, HALL_PREVIEW
from plan import (ENTRY_X, GATE_CLERK, GATE_EAST_BAY, GATE_WEST_BAY, RIM_ENTRY_X,
                  STORM_WICKTABLE, TEMPLE_ORIGIN, WING_POST, WORK_STATIONS)
from workart import SCENERY as SHOP_FURNISHINGS
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
    "hvd_ledgecover": "Zmrzlý balvan na hraně římsy",
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
NAMES.update((model, name) for model, (name, _) in (ROOM_FURNISHINGS | LINK_SCENERY | SHOP_FURNISHINGS).items())

GUARD = (
    (287, "Lavice nebeské hlídky", 0, 1.02, 0, 0),
    (105, "Stojan na odložené zbraně", -2.39, .88, 0, 0),
    ("hvd_crate", None, 2.37, .87, 0, 0),
    (55, "Složený prapor", 2.52, .92, .72, 2),
    ("hvd_oillamp", None, 2.04, .84, .92, 0),
    (49, "Náhradní olej", 2.18, .36, 0, 6),
    (527, "Koš s čistými knoty", 2.60, -.12, 0, 99),
    (56, "Rozpisy služby", -.52, 1.02, .54, 0),
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
    s.put("hvd_camplodge",17.55,23.13)
    s.put("hvd_campshell",38.3,23.35,name="Otevřená zásobárna výprav")
    s.put("hvd_camp_path",27,16)
    s.put("hvd_crate",35.7,24.27,name="Bedna s čerstvými zásobami")
    s.put("hvd_crate",36.3,22.97,name="Výbava připravená k odnosu")
    s.put(361,35.7,24.22,lift=.72,name="Svazek náhradního lana")
    s.put("hvd_shelf",39.97,24.68,name="Police náhradních popruhů a skob")
    s.put("hvd_oillamp",18.32,24.29,lift=.88)
    s.lamp(18.32,24.29,1.23,"amber")
    s.put("hvd_sconce",39.7,24.94,lift=2.13)
    s.lamp(39.7,24.51,2.48,"amber")
    s.signpost(21.93,32.75,"amber")
    s.put(87,28.75,34.72,direction=185,name="Směrovník na Výstupovou římsu")
    s.put("hvd_snowbank",12.55,27.5,direction=24)
    s.put("hvd_talus",16.8,11.36,direction=15,name="Závětří pod hranou skály")
    s.put("hvd_crag",46.1,21.7,base=-.92,direction=70)
    s.put("hvd_snowbank",33.72,26.86,direction=113)


def mountain(s):
    s.area.lighting.update(ChanceSnow=integer(27), FogClipDist=flt(96.0),
                           MoonAmbientColor=color(65,80,119), MoonDiffuseColor=color(193,202,229))
    s.put("hvd_rim_roads",26,12,name="Dlážděné rozcestí")
    for x,y,z,heading in ((36.9,23.7,-1.1,30),(46.5,26.7,-1.15,21),(60.0,8.8,-1.9,27)):
        s.put("hvd_crag",x,y,base=z,direction=heading)
    for x,y,a in ((14.1,12.5,36),(7.65,19.60,39),(4.68,29.75,60),(22.95,32.7,29),
                  (30.4,8.7,68),(41.8,18.88,21),(65.1,29.4,82)):
        s.put("hvd_snowbank",x,y,direction=a)
    s.put("hvd_flankwalls",RIM_ENTRY_X,35.4,direction=0)
    for dx in (-2.79,2.79):
        s.lamp(RIM_ENTRY_X+dx,37.58,2.63,'amber')
    # The cleft sits behind two changes of direction and the near side of a spur.
    for x,y,z,heading in ((58.5,19.5,-.35,5),(62.55,22.0,-.42,83),(68.4,19.1,-.4,-5),
                         (73.2,29.5,-.48,5),(77.45,27.4,-.28,16),(81,20.3,-.38,-10),
                         (87.65,20.45,-.28,107),(87.64,29.6,-.34,83)):
        s.put("hvd_talus",x,y,base=z,direction=heading)
    for x,y,a in ((62.0,12.8,28),(70.55,28.5,27),(79.0,25.84,124),(86.46,28.45,30)):
        s.put("hvd_rubble",x,y,direction=a)


def service_vestibule(s):
    wall_x,y = HALL_ACCESS[0], HALL_ACCESS[3]+.63
    s.put('hvd_sconce',wall_x+.09,y,direction=90,lift=2.07)
    s.lamp(wall_x+.44,y,2.39,'amber')


def halls(s):
    s.area.lighting.update(MoonAmbientColor=color(81,88,109), MoonDiffuseColor=color(193,183,170))
    service_vestibule(s)
    end_y = HALL_PREVIEW[3]
    s.put('hvd_sconce',43.7,end_y-.09,lift=2.11)
    s.lamp(43.7,end_y-.43,2.43,'amber')
    # Ohlašovna. Zápis a nástroj obsluhy jsou na stejné bezpečné straně.
    s.put('hvd_register',12.30,11.64,direction=180,name='Pult služby a kniha střídání')
    s.put(383,13.43,12.05,lift=.89,name='Svíce ohlašovny')
    s.lamp(13.43,12.05,1.15,'amber')
    s.put(178,18.75,19.80,name='Lavice u ohlašovny')
    for x in (9.73,16.33):
        s.put('hvd_sconce',x,24.02,lift=2.05)
        s.lamp(x,23.59,2.4,'amber')
    s.wall(13.2,10.70,180,None,'blue',built=True)
    s.put('hvd_drawers',18.26,11.18,direction=180,name='Výdejní zásuvky obsluhy clon')

    # U každé clony je v kameni vidět přívod, výklenky slouží jako kryt.
    s.wall(32.48,20.12,0,None,'amber',built=True)
    s.put(287,32.48,19.51,name='Sklopná lavice v bezpečnostním výklenku')
    s.put('hvd_crate',39.54,10.46,direction=180,name='Odložené krytky vysílačů')
    s.lamp(39.6,10.64,1.27,'blue')
    s.put('hvd_oillamp',39.54,10.46,lift=.74)

    # Filtrovna před ohybem a severní servisní chodba.
    s.put('hvd_filtergrid',58.53,22.12,direction=270)
    s.put('hvd_wallchart',56.62,25.94)
    s.wall(55.90,25.94,0,None,'amber',built=True)
    s.put('hvd_filterbench',56.02,19.0,direction=180)
    s.lamp(56.02,19.07,1.42,'blue')
    s.put('hvd_crate',58.02,19.33,direction=180,name='Značené bedny s náhradními rámy')
    s.wall(47.12,22.40,90,None,'blue',built=True)
    s.wall(49.34,48.08,0,None,'blue',built=True)
    s.put('hvd_drawers',54.59,44.8,direction=270,name='Evidenční zásuvky se značkami filtrů')
    s.wall(37.8,47.70,0,None,'blue',built=True)
    s.wall(29.0,42.31,180,None,'amber',built=True)

    # Archiv má vlastní čtecí zákoutí a pracovní úložný kout.
    s.wall(15.53,39.82,180,'chart','amber',built=True)
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
    for x,y,angle,tint in ((ENTRY_X-2.78,2.05,90,'amber'),(ENTRY_X+2.78,2.05,270,'amber'),
                          (44.2,19.48,0,'amber'),(58.31,19.48,0,'blue'),
                          (46.15,4.44,180,'amber'),(57.76,4.44,180,'blue'),
                          (53.05,59.86,0,'blue')):
        s.put('hvd_sconce',x,y,direction=angle,lift=2.13)
        a=radians(angle)
        s.lamp(x+.40*sin(a),y-.40*cos(a),2.53,tint)
    s.put('hvd_entry_arm',ENTRY_X,19.45)
    for x in (ENTRY_X-3.35,ENTRY_X+3.35):
        s.put('hvd_bluebann',x,19.57,lift=3.42)
    for x in (ENTRY_X-2.99,ENTRY_X+2.99):
        s.put(453,x,18.18,direction=180,name='Socha nositele hvězdné sféry')
    s.put('hvd_wallpanel',43.16,7.66,direction=90,name='Reliéf poledníku v bočním zdivu')
    s.put('hvd_spearrack',58.58,8.69,direction=270,name='Stojan vstupní hlídky')
    s.put(287,45.99,5.29,direction=180,name='Čekací lavice u vstupního ochozu')
    s.put('hvd_drawers',57.06,5.31,direction=180,name='Skříňky na mapy pro příchozí')
    for model,((x,y),(xx,yy)) in YARD_MODELS.items():
        s.put(model,(x+xx)/2,(y+yy)/2,name='Obvodové zdivo dílenského dvora')
    # Cold work faces the inspection light. The hot side exhausts through the south wall.
    s.put('hvd_lab_eaves',17.10,19.21)
    s.put('hvd_forge_flue',33.18,10.71)
    for x in (13.02,19.72):
        s.put('hvd_sconce',x,19.53,lift=2.39)
        s.lamp(x,19.22,2.70,'amber')
    s.put('hvd_oillamp',12.68,15.72,lift=.91)
    s.lamp(12.68,15.72,1.26,'amber')
    s.put('hvd_lensrack', 11.03, 17.90, direction=90,name='Odzkoušené čočky v západním výklenku')
    s.put('hvd_grinder', *WORK_STATIONS['grind'], direction=180, name='Brus s ruční klikou a upnutým kolem')
    s.put('hvd_cuttings',18.94,12.72,direction=197)
    s.put('hvd_shelf',15.05,11.25,direction=180,name='Plátno a plst na mokrý výbrus')
    s.put('hvd_polishtray',14.71,18.89)
    s.put('hvd_stockrack', *WORK_STATIONS['intake'],name='Příjem skleněných polotovarů a odlitých objímek')
    s.put('hvd_crate',38.26,18.75,direction=180,name='Bedna s nerozbalenými polotovary')
    s.put('hvd_smithbench',37.13,11.53,direction=180)
    s.put('hvd_planrail',37.05,10.48,direction=180,name='Rozměry mosazné objímky na výkresu')
    s.put('hvd_quench',28.81,11.42,direction=180)
    s.put('hvd_forgehearth',32.06,11.92)
    s.put(49,35.11,11.44,direction=20,name='Vodní soudek od kalicího žlabu')
    s.put('hvd_crate',34.98,13.20,direction=78,name='Zásoba dřevěného uhlí u výhně')
    s.put('hvd_sconce',32.35,10.70,direction=180,lift=2.35)
    s.lamp(32.39,11.04,2.66,'orange')
    s.sky(25, 23.85, 'amber')
    s.sky(25, 49.8, 'blue')
    s.bridge(25, 'amber')
    for y in (16.8, 54.2):
        s.put('hvd_skywalk', 25, y)
    for x,y,z in ((17.8,20.4,5),(31.8,20.4,5),(17.9,50.55,5),(32,50.55,5)):
        s.put('hvd_hangpier', x, y, base=z)

    for x in (27.18,32.82):
        s.put('hvd_sconce',x,73.18,lift=2.16)
        s.lamp(x,72.78,2.55,'violet')
    ix,iy = WORK_STATIONS['inspection']
    s.bay(ix+.35,iy-.28,'blue',model='hvd_workroof')
    s.put('hvd_lenscheck',ix,iy,name='Přejímka čoček před montáží v Kopuli')
    s.put('hvd_lensrack',ix-2.02,iy+.85,name='Police náhradních okulárů')
    wx,wy = WORK_STATIONS['dispatch']
    s.put('hvd_dispatch',wx,wy)
    s.put('hvd_sconce',wx-2.72,wy+1.56,lift=2.04)
    s.lamp(wx-2.72,wy+1.13,2.40,'amber')
    s.put('hvd_capstan',wx,wy)
    s.put('hvd_lifttackle',wx,wy)
    s.put('hvd_lenscrate',wx+2.73,wy-.78)
    s.put(361,wx+2.52,wy+1.14,direction=0,name='Svinutý popruh k přepravnímu rámu')
    s.put('hvd_crate',48.88,58.43,direction=180,name='Bedna s náhradními úvazy')
    s.put(361,47.83,58.19,direction=52,name='Svinuté lano pro přenášení čoček')
    for x,y,z,angle in ((8,14,-1.0,70),(4,54,-4.0,18)):
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
        (41.45,12.35,180,None,'blue'),(8.34,25.99,90,None,'blue'),
        (51.27,26.38,270,None,'amber'),
    ):
        s.wall(x,y,angle,item,light,built=True)
    s.put(383,13.91,33.32,lift=.88,name='Svíce u pozorovacího deníku')
    s.put(287,45.86,35.52,direction=270,name='Lavice při pozorovacím sále')
    s.put('hvd_lectern',15.34,36.45,direction=90,name='Pult měření polohy hvězd')
    s.put('hvd_openbook',15.29,36.45,direction=90,lift=1.14,name='Rozložený hvězdný katalog')
    s.put('hvd_lensrack',8.69,26.32,direction=90,name='Západní výklenek · srovnávací okuláry')
    s.put('hvd_filterbench',10.8,23.84,direction=180,name='Stolec pro kontrolu cejchování okulárů')
    s.put('hvd_drawers',50.66,26.31,direction=270,name='Východní výklenek · listy průchodů hvězd')
    s.put('hvd_armillary',48.04,27.18,name='Přenosný model pro zápis průchodů')
    s.put('hvd_shelf',45.33,12.83,direction=180,name='Nástroje ke kontrole refraktoru')
    s.put('hvd_tools',45.33,12.86,direction=180,lift=.89,name='Montážní měrky a klíče')
    s.put('hvd_drawers',40.13,12.92,direction=180,name='Mosazná protizávaží v přihrádkách')
    s.put('hvd_crate',47.28,15.82,direction=270,name='Zajištěná bedna pod krytem seřízení')
    for x in (22.85,39.4):
        s.put('hvd_wallring',x,45.95,lift=1.50,name='Oko pro jištění severní clony')
    s.put('hvd_mounttrim',30,31)


def steps(s):
    s.area.lighting.update(FogClipDist=flt(147.0), MoonAmbientColor=color(89,102,142),
                           MoonDiffuseColor=color(206,218,244))
    s.sky(30,2.7,'blue',5)
    for x,y,shade in ((21.5,18.6,'amber'),(38.55,18.6,'amber'),
                      (31.25,38.6,'blue'),(48.72,38.6,'blue'),
                      (21.52,58.65,'amber'),(38.55,58.65,'amber')):
        s.signpost(x,y,shade)
    s.bay(13.15,15.4,'amber',90)
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
    s.bay(WING_POST[0],57.58,'blue',base=15)
    x,y = STORM_WICKTABLE
    s.put('hvd_wicktable',x,y,base=15,name='Sušení knotů na horní podestě')
    s.put('hvd_oillamp',x-.84,y-.30,lift=1.08,base=15)
    s.lamp(x-.84,y-.30,1.23,'amber',15)
    bay_x,bay_y = 15.75,84.0
    s.bay(bay_x,bay_y,'amber',90,20)
    s.put('hvd_spearrack',bay_x,bay_y,direction=90,base=20)
    s.put('hvd_goldbann',bay_x-1.53,bay_y,direction=90,lift=.54,base=20)
    s.put('hvd_beactower',42.37,84.19,base=20)
    s.lamp(42.37,84.19,7.62,'amber',20)
    s.clouds([(5,20,-8,24),(52,39,-10,57),(57,66,-8,103),(15,89,-9,18)],
             [(8,41,-12,14),(59,36,-10,126),(7,61,-8,135),(64,61,-10,23)])


def walks(s):
    s.area.lighting.update(FogClipDist=flt(117.0),ChanceSnow=integer(38))
    for x,y,shade in ((20.4,21.1,'blue'),(60.8,24.95,'amber'),
                      (32.1,35.65,'blue'),(53.62,42.4,'amber'),
                      (25.52,54.5,'blue'),(61.38,55.1,'amber'),
                      (47.8,76.6,'amber'),(27.95,85.8,'blue'),(18.65,100.4,'amber')):
        s.signpost(x,y,shade)
    for x,y,angle in ((9.3,12.15,16),(15.5,13.55,74),(29.33,23.4,66),
                      (22.73,40.55,40),(18.4,52.24,23),(50.3,35.1,76),
                      (64.37,48.3,110),(61.65,57.02,54),(35.15,70.24,158),
                      (44.58,82.15,90),(14.75,94.95,68),(12.66,101.18,8),
                      (72.83,7.92,27)):
        s.put('hvd_rubble',x,y,direction=angle,lift=-.06)
    s.put('hvd_talus',70.68,5.14,base=4.62,direction=90)
    s.put('hvd_talus',79.55,4.64,base=4.61,direction=90)
    s.put('hvd_spearrack',6.72,75.96,direction=90)
    s.put('hvd_wicktable',75.06,76.37,direction=270)
    s.put('hvd_oillamp',75.07,76.37,lift=.88)
    s.lamp(75.07,76.37,1.21,'amber')
    s.clouds([(5,38,-17,55),(40,39,-18,88),(75,39,-21,126),(42,55,-19,9)],[])


def gate(s):
    s.area.lighting.update(FogClipDist=flt(116.0), MoonAmbientColor=color(101,116,160),
                           MoonDiffuseColor=color(218,209,238))
    west_x,west_y = GATE_WEST_BAY
    s.bay(west_x,west_y,'blue',90,5)
    clerk_x,clerk_y = GATE_CLERK
    s.put(383,clerk_x+.14,clerk_y+.71,lift=.88,base=5,name='Písařova svíce')
    s.lamp(clerk_x+.14,clerk_y+.71,1.14,'amber',5)
    east_x,east_y = GATE_EAST_BAY
    s.bay(east_x,east_y,'amber',180,5)
    s.set(east_x,east_y,GUARD,180,5)
    s.put('hvd_wicktable',56.92,37.84,direction=0,base=5,name='Pult pro údržbu výzbroje stráže')
    s.put(287,3.09,24.54,direction=90,name='Lavice západní obchůzky')
    s.put(91,66.19,26.54,direction=225,name='Nebeský hlídač východního nástupu')
    for x in (20.8,49.2):
        s.put('hvd_tallpier',x,38.83,base=5)
        s.put('hvd_sconce',x,37.94,lift=2.44,base=5)
        s.lamp(x,37.63,2.77,'blue',5)
    s.put('hvd_gatecrest',*GATE,base=10)
    for x,angle in ((31.1,90),(38.9,270)):
        s.put('hvd_tallpier',x,67.98,base=10)
        s.put('hvd_sconce',x,66.99,lift=2.44,base=10,direction=angle)
        s.lamp(x,66.76,2.77,'violet',10)
    s.put(125,23.8,58.4,direction=180,base=10,name='Znak nebeské hlídky')
    s.put(126,46.2,58.4,direction=180,base=10,name='Znak návratu')
    s.clouds([(10,51,-8,38),(52,60,-10,109),(56,12,-9,52)],
             [(8,49,-12,23),(65,30,-12,78)])


def summit(s):
    s.area.lighting.update(FogClipDist=flt(125.0), MoonAmbientColor=color(106,113,146),
                           MoonDiffuseColor=color(229,222,219))
    s.sky(35,2.7,'amber',5)
    s.bay(15.1,16.42,'amber',base=5)
    s.put('hvd_spearrack',15.1,17.58,base=5,name='Výzbroj nástupu hlídky')
    s.bay(54.90,16.42,'blue',base=5)
    s.put('hvd_oillamp',54.76,14.76,base=5,lift=.89)
    s.lamp(54.76,14.76,1.18,'amber',5)
    s.put('hvd_temple',*TEMPLE_ORIGIN,base=10,name='Chrám posledního stupně')
    s.put('hvd_wicktable',55.55,46.85,base=10,name='Pracovní stůl obsluhy záchytu')
    s.put('hvd_oillamp',55.65,46.63,base=10,lift=.88)
    s.lamp(55.65,46.63,1.14,'amber',10)
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
    designers = {
        'camp': camp, 'rim': mountain, 'halls': halls, 'works': workshops, 'dome': dome,
        'steps': steps, 'walks': walks, 'gate': gate, 'top': summit, 'study': study,
        'service': service_vestibule,
    }
    for area in zones:
        design = designers.get(area.key[4:])
        if design:
            design(Dress(area))
