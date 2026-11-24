"""Wall shutters, the optical test bench and a suspended sounding plate."""

from math import cos, sin, tau
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, PALE, pillar, rosette
from art import BRASS, DARK, GILT, TRIM, Material, Mesh, star_chart


LAB_SOURCE = (21.28, 17.38)
LAB_MIRROR = (18.52, 18.46)
LAB_SCREEN = (16.93, 19.13)
MIRROR_MODEL = 245

RAY_AMBER=Material((1,.63,.29),'hvd_raylight',(.73,.39,.16),alpha=.91)
RAY_BLUE=Material((.46,.79,1),'hvd_raylight',(.34,.67,.97),alpha=.88)
RAY_WHITE=Material((.80,.91,1),'hvd_raylight',(.63,.82,1),alpha=.89,shadow=0)
WOOD=Material((.54,.44,.33),'hvd_oak')
IRON=Material((.24,.24,.26),'hvd_brass')
BLANK=Material((.67,.76,.73),'hvd_glass',(.04,.08,.12))
POLISHED=Material((.39,.67,.83),'hvd_glass',(.10,.21,.33))
FELT=Material((.32,.37,.33),'hvd_oak')
GRIT=Material((.34,.29,.25),'hvd_basalt')


def rim_bolt():
    mesh = Mesh()
    mesh.box(BASALT, 0, .059, .34, .46, .28, .52, tile_uv=.65)
    mesh.box(DARK, 0, -.091, .45, .217, .025, .29)
    mesh.box(IRON, 0, -.143, .50, .100, .092, .184)
    mesh.tube(BRASS, (-.061, -.157, .632), (.062, -.157, .633), .022, sides=7)
    for x, z in ((-.125,.391),(.08,.79),(.19,.485)):
        mesh.box(GRIT,x,-.112,z,.10,.016,.024)
    return mesh


def stock_rack():
    mesh = Mesh()
    for x in (-1.52, 1.52):
        mesh.box(WOOD, x, 0, 0, .25, .89, 1.98, tile_uv=.45)
    for z in (.24, .96, 1.68):
        mesh.box(WOOD, 0, 0, z, 3.2, .89, .13, tile_uv=.46)
        mesh.box(BRASS, 0, -.438, z+.105, 3.19, .025, .046)
    for x in (-1.0,-.52,.02):
        mesh.disc(BLANK, (x,.02,.35), (x,.02,.44), .216, sides=12)
        mesh.disc(BLANK, (x,.02,.49), (x,.02,.55), .207, sides=14)
    for x in (.68, 1.10):
        mesh.box(DARK, x, -.02, .37, .36, .56, .26)
        mesh.box(WOOD, x, -.02, .52, .37, .56, .126)
    for x in (-1.16,-.54,.12,.74):
        mesh.box(WOOD,x,.03,1.1,.48,.61,.08)
        mesh.tube(BRASS, (x,.19,1.33),(x,-.09,1.33),.215,sides=14,open_ends=True)
    return mesh


def quench_trough():
    mesh = Mesh()
    for x in (-.63,.63):
        mesh.box(BASALT,x,0,0,.27,.70,.57,tile_uv=.39)
    mesh.box(IRON,0,0,.55,1.91,.87,.084)
    for x in (-.94,.94):
        mesh.box(BASALT,x,0,.57,.12,.87,.37)
    for y in (-.40,.40):
        mesh.box(BASALT,0,y,.57,1.90,.13,.37)
    mesh.box(POLISHED,0,0,.78,1.74,.66,.025)
    mesh.tube(IRON,(-.53,-.34,.95),(-.79,.35,1.04),.046,sides=6)
    mesh.tube(IRON,(-.56,-.34,.95),(-.33,.36,1.00),.040,sides=6)
    mesh.disc(BRASS,(.44,.03,.815),(.44,.03,.857),.222,sides=17)
    return mesh


def lens_cradle(inspection=False):
    mesh = Mesh()
    width = 2.36 if inspection else 2.89
    for x in (-width/2+.12, width/2-.12):
        mesh.box(BASALT,x,0,0,.20,1.18,.21)
        mesh.box(WOOD,x,0,.21,.17,1.04,.55)
    mesh.box(WOOD,0,0,.70,width,1.18,.16,tile_uv=.42)
    mesh.box(FELT,0,0,.862,width-.14,1.04,.028)
    for x in (-.67,.67):
        mesh.box(WOOD,x,.14,.86,.22,.42,.54)
        mesh.disc(BRASS,(x,.09,1.29),(x,-.019,1.29), .38, sides=20)
        mesh.disc(POLISHED,(x,-.021,1.29),(x,-.039,1.29),.304,sides=20)
        mesh.box(BRASS,x,-.45,.89,.25,.057,.065)
    if not inspection:
        for x in (-1.23,1.23):
            mesh.box(DARK,x,0,.86,.10,1.03,.23)
        for y in (-.48,.48):
            mesh.box(DARK,0,y,.87,width-.28,.16,.26)
            mesh.trace(BRASS,(-1.12,y,.073),(1.18,y,.073),.064)
    return mesh


def polishing_tray():
    mesh = Mesh()
    for x in (-.94,.94):
        mesh.box(WOOD,x,0,0,.17,.66,.84)
    for z in (.23,.81):
        mesh.box(WOOD,0,0,z,2.11,.75,.10,tile_uv=.40)
    mesh.box(FELT,0,-.04,.911,1.98,.61,.044)
    for x, y, radius in ((-.61,-.07,.26),(.01,.06,.22),(.59,-.09,.27)):
        mesh.disc(BLANK,(x,y,.951),(x,y,.997),radius,sides=12)
        mesh.disc(POLISHED,(x,y,.996),(x,y,1.01),radius-.035,sides=13)
    for x in (-.58,0,.57):
        mesh.box(GRIT,x,.01,.33,.35,.42,.16)
    mesh.tube(IRON,(.37,-.25,.98),(.92,-.18,1.01),.033,sides=7)
    return mesh


def dispatch_tackle():
    mesh = Mesh()
    mesh.box(IRON,2.67,-.70,2.39,.34,.34,.29)
    mesh.disc(BRASS,(2.67,-.895,2.40),(2.67,-.685,2.40),.174,sides=12)
    mesh.disc(IRON,(2.67,-.916,2.40),(2.67,-.895,2.40),.071,sides=9)
    for start,end in (
        ((.11,.36,1.23),(2.57,-.78,2.53)), ((2.57,-.78,2.53),(2.81,-.78,2.43)),
        ((2.81,-.78,2.43),(2.81,-.78,1.43)), ((2.81,-.78,1.43),(1.87,-.78,1.04)),
        ((2.81,-.78,1.43),(3.58,-.78,1.04)),
    ):
        mesh.tube(FELT,start,end,.025,sides=6)
    return mesh


def forge_hearth():
    mesh = Mesh()
    mesh.polygon(GRIT, ((-2.8,-1.23,.018),(2.94,-1.23,.018),(3.10,.43,.018),
                        (2.36,.87,.018),(-2.69,.97,.018),(-2.96,.36,.018)))
    for a,b in (((-2.68,.97,.025),(2.36,.87,.025)),((2.36,.87,.025),(3.1,.43,.025))):
        mesh.trace(BRASS,a,b,.025)
    for x, y, z in ((-.51,.72,.029),(-1.16,.69,.031),(1.52,.62,.029),(1.93,.52,.026)):
        mesh.polygon(IRON,((x-.05,y-.082,z),(x+.13,y-.036,z),(x+.17,y+.053,z),(x-.13,y+.067,z)))
    return mesh


def bench_debris():
    mesh = Mesh()
    stain = ((-.84,-.36,.018),(.48,-.43,.018),(.86,-.12,.018),
             (.63,.25,.018),(-.19,.41,.018),(-.82,.17,.018))
    mesh.polygon(GRIT, stain)
    for x, y, size in ((-.49,.13,.17),(-.2,-.23,.12),(.04,.16,.09),
                       (.39,.08,.15),(.56,-.14,.085),(.12,-.29,.08)):
        mesh.polygon(BLANK, ((x-size,y,.029),(x+size,y-size,.035),
                             (x+.02,y+size,.023)))
    return mesh


def archive_case():
    m=Mesh()
    m.box(WOOD,0,0,0,4.90,.48,2.88)
    for x in (-2.35,0,2.35):
        m.box(WOOD,x,-.19,.18,.12,.31,2.70)
    m.box(DARK,0,-.07,0,4.92,.58,.19)
    m.box(TRIM,0,-.07,2.90,4.93,.55,.17)
    for i,z in enumerate((.88,1.51,2.15)):
        m.box(WOOD,0,-.25,z,4.53,.35,.084)
        for n in range(15):
            if n in (2,10) or (n+i)%7==6:
                continue
            x=-2.10+n*.30
            m.box((WOOD,DARK,BRASS,DARK)[(n+2*i)%4],x,-.30,z+.082,.15,.175,.26+.041*((i+n)%5))
    for x in (-1.28,1.27):
        m.box(WOOD,x,-.235,.19,1.80,.16,.61)
        m.box(BRASS,x,-.34,.42,.12,.07,.05)
    for x in (-2.68,2.68):
        m.box(WOOD,x,-.015,0,.57,.50,3.18)
    m.box(DARK,0,-.055,3.01,5.95,.54,.30)
    return m


def ray_case():
    m=Mesh()
    for side in (-1,1):
        y=side*2.42
        front=y-side*.27
        m.box(MASONRY,0,y,0,1.51,.49,2.97,tile_uv=.30)
        m.box(BASALT,0,y,0,1.64,.61,.36,tile_uv=.33)
        m.box(LIMESTONE,0,y,2.84,1.69,.62,.22,tile_uv=.33)
        m.box(DARK,0,front,.58,1.09,.063,1.86)
        for x in (-.46,.46):
            m.box(BRASS,x,front-side*.060,.47,.083,.118,2.05)
        m.disc(BRASS,(0,y,1.38),(0,front-side*.07,1.38),.32,sides=16)
        m.trace(BRASS,(-1.18,0,.018),(-1.18,side*2.27,.018),.07)
        m.trace(BRASS,(1.18,0,.018),(1.18,side*2.27,.018),.07)
    return m


def ray_eye(isolated):
    m=Mesh()
    for side in (-1,1):
        depth=side*2.055
        m.disc(DARK if isolated else RAY_BLUE,(0,depth,1.38),(0,depth-side*.052,1.38),.241,sides=16)
        offset=0 if isolated else .31
        for x in (-.132,.132):
            px=x+(offset if x>0 else -offset)
            m.box(BRASS,px,depth-side*.057,.965,.255,.075,.83)
        if isolated:
            m.box(TRIM,0,depth-side*.10,1.31,.10,.080,.14)
    return m


def ray_warning():
    m=Mesh()
    for side in (-1,1):
        start=(0,side*2.003,1.38)
        foot=(0,side*.15,.049)
        m.tube(RAY_WHITE,start,foot,.031,.046,sides=7,open_ends=True)
    m.trace(RAY_WHITE,(0,-2.04,.047),(0,2.04,.047),.038)
    return m


def shutter_panel():
    mesh = Mesh()
    mesh.box(MASONRY,0,.17,1.04,5.45,.29,2.15)
    mesh.box(BASALT,0,.01,1.18,5.19,.083,1.91)
    for z in (1.19,3.05):
        mesh.box(BRASS,0,-.082,z,5.24,.13,.091)
    mesh.box(MASONRY,0,.06,.72,2.38,.26,.46)
    mesh.box(BRASS,0,-.073,.79,1.97,.05,.24)
    mesh.box(DARK,0,-.101,.82,1.76,.02,.17)
    for x in (-1.71,0,1.71):
        mesh.disc(BRASS,(x,-.10,2.22),(x,-.18,2.22),.49,sides=16)
        mesh.disc(IRON,(x,-.18,2.22),(x,-.205,2.22),.405,sides=16)
        mesh.disc(BRASS,(x,-.09,2.87),(x,-.156,2.87),.119,sides=10)
        mesh.disc(BLANK,(x,-.156,2.87),(x,-.177,2.87),.079,sides=10)
        mesh.tube(BRASS,(x,-.098,1.32),(x,-.098,1.64),.028,sides=7)
    # Straight inlet, two-pronged outlet, and the angled reflection path.
    for x,segments in (
        (-1.71,((-.23,0,.23,0),(.07,.15,.23,0),(.07,-.15,.23,0))),
        (0,((-.25,0,0,0),(0,0,.22,.168),(0,0,.22,-.168))),
        (1.71,((-.24,.14,0,-.15),(0,-.15,.24,.14),(-.18,-.19,.18,-.19))),
    ):
        for a,b,c,d in segments:
            mesh.tube(GILT,(x+a,-.231,2.22+b),(x+c,-.231,2.22+d),.036,sides=7)
    return mesh


def shutter_button():
    mesh = Mesh()
    mesh.disc(BRASS,(0,.08,0),(0,-.094,0),.245,sides=12)
    mesh.disc(TRIM,(0,-.087,0),(0,-.175,0),.169,sides=12)
    mesh.disc(PALE,(0,-.174,0),(0,-.203,0),.105,sides=10)
    return mesh


def shutter_lamp():
    mesh = Mesh()
    mesh.disc(RAY_AMBER,(0,.015,0),(0,-.042,0),.083,sides=12)
    return mesh


def shutter_sink_glow():
    mesh = Mesh()
    mesh.box(RAY_AMBER,0,0,0,1.67,.035,.10)
    return mesh


def test_optic():
    m=Mesh()
    m.disc(BASALT,(0,0,0),(0,0,.16),.81,sides=12)
    m.box(MASONRY,0,0,.13,.95,.81,.85)
    m.box(TRIM,0,0,.92,1.2,1.11,.18)
    for x in (-.37,.29):
        m.box(BRASS,x,.07,1.07,.22,.34,.40)
    m.tube(BRASS,(.51,-.22,1.39),(-.45,.18,1.50),.184,.225,sides=12)
    m.disc(PALE,(-.43,.17,1.50),(-.56,.226,1.51),.178,sides=12)
    m.tube(BRASS,(.30,-.32,1.12),(.30,-.53,1.41),.045,sides=7)
    m.disc(GILT,(.30,-.53,1.39),(.30,-.53,1.52),.092,sides=10)
    return m


def gauge():
    m=Mesh()
    m.box(BASALT,0,.04,.96,1.64,.22,1.43)
    m.box(BRASS,0,-.085,1.03,1.52,.08,1.28)
    m.box(DARK,0,-.128,1.15,1.37,.05,1.05)
    for x in (-.59,.59):
        rosette(m,x,-.168,1.98,.075,PALE,4)
    return m


def light_trial(west, east):
    m=Mesh()
    x,y=LAB_SOURCE
    mx,my=LAB_MIRROR
    sx,sy=LAB_SCREEN
    source=(-.52,.224,1.51)
    reflection=(mx-x,my-y,1.72)
    target=(sx-x,sy-y-.18,1.76)
    m.tube(RAY_AMBER,source,reflection,.025,.040,sides=8,open_ends=True)
    m.tube(RAY_BLUE,reflection,target,.039,.023,sides=8,open_ends=True)
    for i,(dx,count) in enumerate(((-.37,west),(.29,east))):
        for tick in range(count):
            u=target[0]+dx+.15*(tick-(count-1)/2)
            m.tube(PALE if i else GILT,(u,target[1],1.44),(u,target[1],1.93),.035,sides=6)
    return m


def chime():
    m=Mesh()
    for x in (-.87,.87):
        pillar(m,x,.14,2.66,radius=.16)
    m.box(BASALT,0,.14,0,2.25,.81,.16)
    m.box(TRIM,0,.14,2.53,2.12,.34,.16)
    for x in (-.35,.35):
        m.tube(DARK,(x,.10,2.53),(x,.09,2.13),.033,sides=6)
    m.tube(BRASS,(0,.221,1.57),(0,.047,1.57),.73,.67,sides=20)
    m.disc(DARK,(0,.043,1.57),(0,.006,1.57),.51,sides=20)
    for r in (.34,.57):
        outline=[(r*cos(i*tau/30),-.019,1.57+r*sin(i*tau/30)) for i in range(31)]
        for a,b in zip(outline,outline[1:]):
            m.tube(GILT,a,b,.017,sides=5)
    m.disc(BRASS,(0,.0,1.57),(0,-.105,1.57),.204,sides=12)
    m.tube(WOOD,(.51,-.29,.64),(.28,-.43,1.07),.035,sides=7)
    m.disc(DARK,(.28,-.46,1.08),(.28,-.39,1.08),.088,sides=8)
    return m


def storm_inlay():
    model=Mesh()
    for material,polygons in star_chart().faces.items():
        for vertices,uv in polygons:
            model.polygon(material,[(x*.68,y*.68,z) for x,y,z in vertices],uv)
    return model


def dome_mirror():
    m = Mesh()
    m.box(BASALT, 0, .04, 0, 1.73, .74, .18)
    for x in (-.60, .60):
        m.tube(BRASS, (x,.22,.18), (x,.08,1.58), .082, .064, sides=8)
        m.disc(TRIM, (x,.22,.17), (x,.22,.27), .13, sides=8)
    m.disc(DARK, (0,.15,1.57), (0,.02,1.57), .74, sides=24)
    m.disc(BRASS, (0,.018,1.57), (0,-.068,1.57), .73, sides=24)
    m.disc(POLISHED, (0,-.063,1.57), (0,-.081,1.57), .656, sides=24)
    m.tube(PALE, (-.43,-.089,1.29), (.17,-.089,1.98), .028, .012, sides=6)
    return m


def portable_mirror_assets():
    name = f'it_smlmisc_{MIRROR_MODEL:03d}'
    glass = Material((.64,.83,.95),'hvd_glass',(.12,.21,.29))
    model = Mesh()
    model.disc(BRASS,(0,.088,.052),(0,.088,.113),.249,sides=20)
    model.disc(glass,(0,.088,.112),(0,.088,.125),.209,sides=20)
    model.tube(WOOD,(0,-.341,.082),(0,-.122,.082),.047,.036,sides=8)
    model.disc(BRASS,(0,-.373,.082),(0,-.339,.082),.051,sides=8)
    model.disc(GILT,(0,-.142,.082),(0,-.111,.082),.051,sides=8)

    size = 64
    header = pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,32,8)
    pixels = bytearray()
    for row in range(size):
        v = (row+.5-size/2)/(size*.5)
        for col in range(size):
            u = (col+.5-size/2)/(size*.5)
            x,y = .93*u+.36*v, -.36*u+.93*v
            edge = (x/.55)**2 + ((y-.24)/.58)**2
            if edge <= 1:
                if edge > .76:
                    color = (235,193,119) if y-x > .10 else (155,101,56)
                else:
                    sheen = abs(y-1.15*x-.31) < .07 or abs(y-1.15*x-.13) < .03
                    color = (221,246,255) if sheen else (106+int(40*y),161+int(35*y),196+int(35*y))
            elif abs(x) <= .115 and -.83 <= y < -.30:
                color = (201,152,85) if y < -.74 or y > -.42 else (80,49,33)
            else:
                pixels.extend((0,0,0,0))
                continue
            pixels.extend((*reversed(color),255))
    return {
        f'{name}.mdl': model.mdl(name).replace(b'classification Other',b'classification Item'),
        f'i{name}.tga': header+pixels,
    }


SCENERY = {
    'hvd_dome_mirror':('Pevné zrcadlo u severní štěrbiny',dome_mirror),
    'hvd_ray_case':('Nástěnné vysílače clony',ray_case),
    'hvd_lab_source':('Mosazná stolice zkušební optiky',test_optic),
    'hvd_lab_screen':('Sklo měřicí stupnice',gauge),
    'hvd_gong':('Závěsná ozvučnice',chime),
    'hvd_storm_inlay':('Rozeta bouřné podesty',storm_inlay),
    'hvd_rimbolt':('Zapuštěná servisní západka',rim_bolt),
    'hvd_stockrack':('Materiál k výbrusu a odlévání',stock_rack),
    'hvd_quench':('Kameninový žlab ke kalení objímek',quench_trough),
    'hvd_lenscrate':('Přepravní rám s vypodloženými čočkami',lens_cradle),
    'hvd_lenscheck':('Přejímací stojan s hotovými čočkami',lambda: lens_cradle(True)),
    'hvd_polishtray':('Plstěný stojan po mokrém výbrusu',polishing_tray),
    'hvd_lifttackle':('Lano navijáku, kladka a úvaz rámu',dispatch_tackle),
    'hvd_forgehearth':('Okraj ohnivzdorné podlahy se sazemi',forge_hearth),
    'hvd_cuttings':('Brusný prach a odřezky skla',bench_debris),
    'hvd_clonpanel':('Schéma pohonu tří uzávěrů',shutter_panel),
    'hvd_clon_knob':('Mosazné tlačítko na schématu',shutter_button),
}
VISUALS = {
    'hvd_arc_cabinet':('Skříň s kalibračním archivem',archive_case),
    'hvd_ray_ready':('Připravené vysílače',lambda:ray_eye(False)),
    'hvd_ray_cut':('Zakryté vysílače',lambda:ray_eye(True)),
    'hvd_rayflash':('Varovný pruh vysílačů',ray_warning),
    'hvd_panel_lit':('Potvrzovací světlo pojistky',shutter_lamp),
    'hvd_sinkglow':('Rozsvícená spodní lišta rozvaděče',shutter_sink_glow),
    **{f'hvd_lab_trace{west}{east}': ('Zkušební odraz se stupnicí',
        lambda west=west, east=east: light_trial(west, east))
       for west in (1,2,3) for east in (1,2,3) if west != east},
}
