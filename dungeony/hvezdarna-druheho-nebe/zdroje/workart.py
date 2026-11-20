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
WOOD=Material((.54,.44,.33),'hvd_oak')


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
        y=side*2.30
        m.box(BASALT,0,y,.40,.86,.29,1.76)
        m.box(TRIM,0,y,1.92,.98,.31,.29)
        m.disc(BRASS,(0,y,1.30),(0,y-side*.245,1.30),.29,sides=12)
        m.trace(BRASS,(-1.18,0,.018),(-1.18,side*2.27,.018),.07)
        m.trace(BRASS,(1.18,0,.018),(1.18,side*2.27,.018),.07)
    return m


def ray_eye(isolated):
    m=Mesh()
    for side in (-1,1):
        depth=side*2.05
        m.disc(DARK if isolated else RAY_AMBER,(0,depth,1.30),(0,depth-side*.045,1.30),.193,sides=12)
        if isolated:
            m.box(PALE,0,depth-side*.060,1.26,.22,.07,.068)
    return m


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


def light_trial():
    m=Mesh()
    x,y=LAB_SOURCE
    mx,my=LAB_MIRROR
    sx,sy=LAB_SCREEN
    source=(-.52,.224,1.51)
    reflection=(mx-x,my-y,1.72)
    target=(sx-x,sy-y-.18,1.76)
    m.tube(RAY_AMBER,source,reflection,.025,.040,sides=8,open_ends=True)
    m.tube(RAY_BLUE,reflection,target,.039,.023,sides=8,open_ends=True)
    for i,(dx,count) in enumerate(((-.37,2),(.29,3))):
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
    'hvd_ray_case':('Nástěnné vysílače clony',ray_case),
    'hvd_lab_source':('Mosazná stolice zkušební optiky',test_optic),
    'hvd_lab_screen':('Sklo měřicí stupnice',gauge),
    'hvd_gong':('Závěsná ozvučnice',chime),
    'hvd_storm_inlay':('Rozeta bouřné podesty',storm_inlay),
}
VISUALS = {
    'hvd_arc_cabinet':('Skříň s kalibračním archivem',archive_case),
    'hvd_ray_ready':('Připravené vysílače',lambda:ray_eye(False)),
    'hvd_ray_cut':('Zakryté vysílače',lambda:ray_eye(True)),
    'hvd_lab_trace':('Zkušební odraz se stupnicí',light_trial),
}
