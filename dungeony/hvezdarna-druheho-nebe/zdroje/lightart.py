"""Optical paths and architectural glimpses beyond the observatory's thresholds."""

from math import cos, pi, sin, tau

from architecture import BASALT, ICE, LIMESTONE, MASONRY, SLATE, WOOD, rosette
from art import BRASS, CROWN, DARK, GILT, TRIM, Material, Mesh, arch


REFRACTOR = (30.0, 31.0)
STAIR_PORTAL = (30.0, 46.11)
LAST_TOWER = (16.0, 54.8, 4.0)
LAST_LANTERN = (38.15, 55.5)
LAST_LANTERN_HEIGHT = 10.0
TOWER_LENS = (2.92, 0.0, 8.38)
LANTERN_GLASS = (0.0, 0.0, 2.24)

NIGHT = Material((.18, .24, .43), 'hvd_clouds', (.10, .14, .25))
VOID = Material((.043, .057, .070), 'hvd_rough')
COLD = Material((.59, .86, 1.0), 'hvd_raylight', (.43, .76, .96), alpha=.89)
PALE_MIST = Material((.53, .80, 1.0), 'hvd_raylight', (.25, .51, .85), alpha=.22)
GOLD = Material((1.0, .80, .43), 'hvd_raylight', (.93, .66, .25), alpha=.90)
GOLD_MIST = Material((1.0, .71, .30), 'hvd_raylight', (.71, .42, .16), alpha=.21)


def aperture(m, radius, spring, crown, y, material, foot=.02):
    profile = [(radius*cos(i*pi/24), y, spring+(crown-spring)*sin(i*pi/24))
               for i in range(25)]
    profile.extend(((-radius,y,foot), (radius,y,foot)))
    uv = [(.5+x/(2*radius), z/crown) for x, _, z in profile]
    m.polygon(material, profile, uv)
    m.polygon(material, profile[::-1], uv[::-1])


def brass_rim(m, radius, spring, crown, y, material, size=.05):
    contour = [(radius*cos(i*pi/24), y, spring+(crown-spring)*sin(i*pi/24))
               for i in range(25)]
    contour.insert(0, (radius,y,.06))
    contour.append((-radius,y,.06))
    for a,b in zip(contour,contour[1:]):
        m.tube(material,a,b,size,sides=7)


def preview_steps(m, *, start, run, width, rise, count, base=0, sky=True):
    """A far-side continuation, placed beyond the area-change trigger."""
    for i in range(count):
        y = start+(i+.5)*run
        z = base+rise*(i+1)
        m.box(MASONRY,0,y,-.12,width,run+.007,z+.12)
        m.box(SLATE,0,y,z-.055,width+.12,run+.008,.055)
        for side in (-1,1):
            x = side*(width/2+.11)
            m.box(LIMESTONE,x,y,z-.025,.23,run+.02,.21)
            m.tube(GILT,(x,y-run/2,z+.13),(x,y+run/2,z+.13),.024,sides=6)
            if i in (0,count-1):
                m.box(MASONRY,x,y,z,.36,.30,.59)
                m.box(TRIM,x,y,z+.55,.41,.34,.105)
    if sky:
        end = start+run*count+.07
        aperture(m,width*.69,2.56,3.92,end,NIGHT,foot=base+rise*count-.02)


def dome_shutter():
    m = Mesh()
    aperture(m,2.92,2.19,3.80,.055,BASALT)
    brass_rim(m,2.87,2.18,3.75,-.017,BRASS,.064)
    for x in (-2.32,-1.55,-.78,0,.78,1.55,2.32):
        m.box(DARK,x,-.006,.13,.06,.13,2.63)
        for z in (.29,2.38):
            m.disc(BRASS,(x,-.063,z),(x,-.123,z),.054,sides=8)
    for z in (.29,2.36):
        m.box(TRIM,0,-.026,z,5.77,.21,.13)
    m.disc(BRASS,(0,-.12,1.69),(0,-.18,1.69),.50,sides=12)
    rosette(m,0,-.202,1.69,.32)
    return m


def stair_portal():
    m = Mesh()
    brass_rim(m,2.77,2.17,3.78,-.025,PALE_MIST,.13)
    brass_rim(m,2.75,2.17,3.79,-.048,COLD,.039)
    m.disc(BRASS,(0,.01,3.94),(0,-.28,3.94),.27,sides=12)
    m.disc(COLD,(0,-.255,3.94),(0,-.307,3.94),.16,sides=16)
    preview_steps(m,start=1.31,run=.52,width=4.24,rise=.197,count=6)
    return m


def dome_ray():
    m = Mesh()
    source = (0,2.72,3.201)
    receiver = (0,STAIR_PORTAL[1]-REFRACTOR[1]-.28,3.94)
    m.tube(COLD,source,receiver,.063,.076,sides=10,open_ends=True)
    m.tube(PALE_MIST,source,receiver,.25,.33,sides=14,open_ends=True)
    m.disc(COLD,(0,2.705,3.20),(0,2.745,3.202),.75,sides=24)
    return m


def gate_preview():
    m = Mesh()
    preview_steps(m,start=1.42,run=.72,width=3.98,rise=.194,count=6,sky=False)
    return m


def last_tower():
    m = Mesh()
    m.tube(BASALT,(0,0,-3.4),(0,0,5.6),3.04,2.83,sides=12)
    m.tube(MASONRY,(0,0,5.55),(0,0,9.12),2.82,2.78,sides=12)
    for level in (5.53,6.0,8.87,9.10):
        m.disc(TRIM,(0,0,level),(0,0,level+.16),2.97,sides=12)
    for i in range(12):
        a = (i+.5)*tau/12
        x,y = 2.83*cos(a),2.83*sin(a)
        m.box(BRASS,x,y,7.01,.27,.24,1.17)
    for low,high,bottom,top in ((9.15,10.4,2.96,2.40),(10.4,11.24,2.40,1.28),
                                (11.24,11.57,1.28,.29)):
        m.tube(CROWN,(0,0,low),(0,0,high),bottom,top,sides=12)
        m.disc(BRASS,(0,0,low),(0,0,low+.047),bottom+.024,sides=12)
    m.tube(BRASS,(0,0,11.55),(0,0,12.39),.15,.035,sides=10)
    m.box(LIMESTONE,2.74,0,7.52,.51,1.61,.35)
    m.disc(DARK,(2.60,0,8.38),(2.83,0,8.38),.61,sides=16)
    m.disc(BRASS,(2.79,0,8.38),TOWER_LENS,.54,sides=20)
    m.disc(ICE,TOWER_LENS,(2.95,0,8.38),.45,sides=18)
    return m


def last_lantern():
    m = Mesh()
    m.disc(BASALT,(0,0,0),(0,0,.22),.88,sides=8)
    m.box(MASONRY,0,0,.17,1.08,1.03,1.45)
    m.box(LIMESTONE,0,0,1.51,1.31,1.24,.20)
    rosette(m,0,-.53,1.04,.31)
    m.box(BRASS,0,0,1.70,.83,.82,.15)
    m.box(DARK,0,0,1.86,.55,.55,.78)
    for x in (-.34,.34):
        for y in (-.34,.34):
            m.box(BRASS,x,y,1.83,.072,.074,.88)
    m.tube(BRASS,(0,0,2.67),(0,0,3.03),.56,.17,sides=8)
    m.disc(GILT,(0,0,3.01),(0,0,3.16),.106,sides=12)
    # The handle is bolted to the same pedestal as the glass it closes.
    m.tube(BRASS,(.55,-.23,1.24),(.74,-.46,1.66),.064,sides=9)
    m.tube(WOOD,(.65,-.47,1.68),(.83,-.47,1.68),.084,sides=8)
    return m


def lantern_ray():
    m = Mesh()
    source = (LAST_TOWER[0]+TOWER_LENS[0]-LAST_LANTERN[0],
              LAST_TOWER[1]-LAST_LANTERN[1],LAST_TOWER[2]+TOWER_LENS[2]-LAST_LANTERN_HEIGHT)
    m.tube(GOLD,source,LANTERN_GLASS,.062,.13,sides=14,open_ends=True)
    m.tube(GOLD_MIST,source,LANTERN_GLASS,.29,.40,sides=16,open_ends=True)
    m.box(GOLD,0,0,1.914,.61,.61,.70)
    m.disc(GOLD_MIST,(0,0,1.76),(0,0,2.74),.50,sides=14)
    return m


def lantern_closed():
    m = Mesh()
    m.box(BRASS,-.387,0,1.85,.072,.76,.81)
    for y in (-.26,.26):
        m.box(TRIM,-.428,y,2.12,.068,.083,.35)
    m.box(DARK,0,-.367,1.88,.68,.066,.77)
    return m


def wing_walls():
    m = Mesh()
    for side in (-1,1):
        x = side*5.12
        m.box(BASALT,x,.29,-.24,3.13,3.60,.65)
        m.box(MASONRY,x,.44,.27,3.01,3.35,2.91)
        m.box(LIMESTONE,x,.40,3.12,3.18,3.42,.30)
        m.box(TRIM,x,-1.26,.31,3.12,.23,.29)
        m.box(BRASS,x,-1.30,1.11,.83,.27,1.32)
        m.box(ICE,x,-1.46,1.25,.62,.063,1.00)
        m.box(TRIM,x,-1.42,1.68,.75,.09,.12)
    return m


def quarry_mouth():
    m = Mesh()
    for x in (-2.96,2.96):
        m.box(BASALT,x,.49,-.48,1.20,2.78,.81)
        m.box(MASONRY,x,.49,.23,.91,2.62,2.02)
        m.box(LIMESTONE,x,-.69,1.97,1.08,.43,.31)
    arch(m,2.52,1.90,-.67,.55,.43,MASONRY,masonry=True)
    arch(m,2.51,1.90,1.56,.51,.36,BASALT)
    aperture(m,2.52,1.90,4.43,1.79,VOID,foot=.03)
    for i in range(12):
        a,b=pi*i/12,pi*(i+1)/12
        x0,x1=3.01*cos(a),3.01*cos(b)
        z0,z1=1.90+3.01*sin(a),1.90+3.01*sin(b)
        m.polygon(MASONRY,((x0,-.47,z0),(x0,1.75,z0),(x1,1.75,z1),(x1,-.47,z1)))
    preview_steps(m,start=-.87,run=.43,width=4.45,rise=.136,count=5,sky=False)
    return m


def bridge_rail():
    m = Mesh()
    # Native bridge tiles level off across the crown. This rail carries that profile.
    stations = ((-9, .66), (-6.2,1.31), (-3.1,1.65), (0,1.76),
                (3.1,1.65), (6.2,1.31), (9,.66))
    for x in (-1.78,1.78):
        for y,z in stations:
            m.box(BASALT,x,y,z-.29,.29,.31,.46)
            m.box(LIMESTONE,x,y,z+.15,.21,.22,.71)
            m.box(TRIM,x,y,z+.80,.31,.30,.11)
        for (y,z),(y2,z2) in zip(stations,stations[1:]):
            for h,r in ((.31,.057),(.81,.119)):
                m.tube(LIMESTONE,(x,y,z+h),(x,y2,z2+h),r,sides=7)
    return m


SCENERY = {
    'hvd_lighttower': ('Věž návratového objektivu', last_tower),
    'hvd_signallamp': ('Poslední lucerna s ruční clonou', last_lantern),
    'hvd_flankwalls': ('Boční opěry horské pozorovatelny', wing_walls),
    'hvd_quarry': ('Ostění servisní cesty ve skále', quarry_mouth),
    'hvd_bridgeedge': ('Zábradlí visutého ochozu', bridge_rail),
}

VISUALS = {
    'hvd_optcover': ('Uzávěr Schodů do nebe', dome_shutter),
    'hvd_stairview': ('První schody pod září portálu', stair_portal),
    'hvd_domelight': ('Paprsek seřízeného refraktoru', dome_ray),
    'hvd_topview': ('Schody za Bránou tří paprsků', gate_preview),
    'hvd_lampray': ('Trvalý odraz u poslední lucerny', lantern_ray),
    'hvd_lampclosed': ('Sklopená clona poslední lucerny', lantern_closed),
}
