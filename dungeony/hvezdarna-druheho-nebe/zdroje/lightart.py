"""Optical paths and architectural glimpses beyond the observatory's thresholds."""

from math import cos, hypot, pi, sin, tau

from architecture import (BASALT, ICE, LIMESTONE, MASONRY, SLATE, SNOW, WOOD, cliff_course,
                          entry_walls, hall_bulkhead, rosette, service_slab)
from art import BRASS, CROWN, DARK, GILT, TRIM, Material, Mesh
from plan import GATE_JOIN, OPTICS_JOIN, PASSAGE_WIDTH, THRESHOLD_INSET, TILE, WALKS, ZONES


REFRACTOR = (30.0, 31.0)
STAIR_PORTAL = OPTICS_JOIN.point('dome', THRESHOLD_INSET)
LAST_TOWER = (16.0, 54.8, 4.0)
LAST_LANTERN = (38.15, 55.5)
LAST_LANTERN_HEIGHT = 10.0
TOWER_LENS = (2.92, 0.0, 8.38)
LANTERN_GLASS = (0.0, 0.0, 2.24)

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


def preview_approach(m, join):
    """Use the actual landing and first stair of the next area in the aperture."""
    target = join.second
    zone = ZONES[target]
    _, row = zone.stairs[0]
    left, right = next(zone.flights(row))
    stair_x, stair_y = (left+right)/2, TILE*row
    origin, _ = join.point(target)
    approach = [(x-origin, y + THRESHOLD_INSET) for x,y in WALKS[target][0] if y < stair_y]
    approach.append((stair_x-origin, stair_y+THRESHOLD_INSET))
    for (x0,y0), (x1,y1) in zip(approach,approach[1:]):
        m.polygon(SLATE,((x0-2.72,y0,.012),(x0+2.72,y0,.012),
                         (x1+2.72,y1,.012),(x1-2.72,y1,.012)))
        for offset in (-2.66,2.66):
            m.trace(LIMESTONE,(x0+offset,y0,.07),(x1+offset,y1,.07),.20)
    x = stair_x-origin
    width = right-left
    for i in range(20):
        y = stair_y + THRESHOLD_INSET + (i+.5)*.5
        z = .25*(i+1)
        m.box(MASONRY,x,y,-.08,width,.5,z+.08)
        m.box(LIMESTONE,x,y-.22,z-.04,width,.067,.04)


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


def adjoining_landing(*, enclosed):
    """Draw the first part of the neighboring floor beyond an ordinary threshold."""
    m = Mesh()
    start, length = THRESHOLD_INSET, 7.4
    half = PASSAGE_WIDTH / 2 + .35
    center = start + length / 2
    m.box(MASONRY, 0, center, -.24, 2 * half, length, .23)
    m.box(SLATE, 0, center, -.025, 2 * half, length, .034)
    for edge in (-half, half):
        if enclosed:
            m.box(MASONRY, edge, center, -.01, .26, length, 3.28)
            m.box(LIMESTONE, edge, center, .03, .39, length, .29)
        else:
            for y in (start + 1.9, start + 5.1):
                m.box(MASONRY, edge, y, -1.48, .32, .34, 2.17)
                m.box(TRIM, edge, y, .67, .42, .48, .12)
            m.box(LIMESTONE, edge, center, .57, .24, length, .15)
    return m


def service_view(outside):
    """A rock-cut threshold continues into snow on one side and the adit on the other."""
    m = Mesh()
    start = THRESHOLD_INSET - .06
    end = start + 6.25
    m.box(SNOW if outside else MASONRY,0,(start+end)/2,-.32,5.75,end-start,.32,tile_uv=.31)
    for side in (-1,1):
        lower = [(side*2.8,start,0),(side*2.71,start+1.52,0),
                 (side*2.42,start+3.41,0),(side*(2.02 if side>0 else 3.6),end,0)]
        upper = [(x + side*.2*(i%2),y,3.47+.33*(i%3)) for i,(x,y,_) in enumerate(lower)]
        for a,b,c,d in zip(lower,lower[1:],upper,upper[1:]):
            m.polygon(BASALT,(a,b,d,c),[(y*.30,z*.31) for _,y,z in (a,b,d,c)])
            m.polygon(BASALT,(c,d,b,a),[(y*.30,z*.31) for _,y,z in (c,d,b,a)])
            m.tube(SNOW if outside else SLATE,(a[0],a[1],.11),(b[0],b[1],.13),.16,sides=6)
    if not outside:
        m.box(SLATE,.72,end-.12,0,4.06,.39,3.92,tile_uv=.32)
    return m


def stair_approach():
    m = Mesh()
    m.box(SLATE,0,0,.006,5.48,11.4,.022,tile_uv=.35)
    for x in (-2.69,2.69):
        m.trace(TRIM,(x,-5.7,.031),(x,5.7,.031),.096)
        for y in (-5.1,-3.9,-2.7,2.7,3.9,5.1):
            m.trace(BRASS,(x,y,.032),(x*.76,y,.032),.074)
    for r in (.79,1.51):
        m.ring(BRASS,r,.047,.036)
    rosette(m,0,0,.038,.66,TRIM,8)
    return m


def mountain_roads():
    m = Mesh()
    origin = (26, 12)
    for road in WALKS['rim']:
        normals = []
        for (x, y), (nx, ny) in zip(road, road[1:]):
            length = hypot(nx-x, ny-y)
            normals.append(((y-ny)/length, (nx-x)/length))
        sides = []
        for i, (x, y) in enumerate(road):
            left = normals[max(0,i-1)]
            right = normals[min(i,len(normals)-1)]
            mx,my = left[0]+right[0], left[1]+right[1]
            scale = 2.32/(mx*right[0]+my*right[1])
            x,y = x-origin[0],y-origin[1]
            sides.append(((x+mx*scale,y+my*scale,.037),(x-mx*scale,y-my*scale,.037)))
        for (a,b),(c,d) in zip(sides,sides[1:]):
            vertices = (a,b,d,c)
            m.polygon(SLATE,vertices,[(x*.37,y*.37) for x,y,_ in vertices])
            if hypot(a[0],a[1])>4 or hypot(c[0],c[1])>4:
                m.trace(LIMESTONE,a,c,.064)
                m.trace(LIMESTONE,b,d,.064)
    m.disc(SLATE,(0,0,.032),(0,0,.052),2.74,sides=12)
    m.disc(TRIM,(0,0,.048),(0,0,.073),.44,sides=10)
    return m


def stair_portal():
    m = Mesh()
    brass_rim(m,2.77,2.17,3.78,-.025,PALE_MIST,.13)
    brass_rim(m,2.75,2.17,3.79,-.048,COLD,.039)
    m.disc(BRASS,(0,.01,3.94),(0,-.28,3.94),.27,sides=12)
    m.disc(COLD,(0,-.255,3.94),(0,-.307,3.94),.16,sides=16)
    preview_approach(m,OPTICS_JOIN)
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
    preview_approach(m,GATE_JOIN)
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
    'hvd_rim_roads': ('Dlážděné rozcestí', mountain_roads),
    'hvd_lighttower': ('Věž návratového objektivu', last_tower),
    'hvd_signallamp': ('Poslední lucerna s ruční clonou', last_lantern),
    'hvd_flankwalls': ('Boční opěry horské pozorovatelny', wing_walls),
    'hvd_bridgeedge': ('Zábradlí visutého ochozu', bridge_rail),
    'hvd_entrywalls': ('Nosné zdivo vstupní síně', entry_walls),
    'hvd_talus': ('Zasněžené vrstvy skalního hřbetu', lambda: cliff_course(6.3,5.45,271)),
    'hvd_bulkhead': ('Kamenný rám s vedením clon', hall_bulkhead),
    'hvd_stairaxis': ('Dlažba poledníku', stair_approach),
}

VISUALS = {
    'hvd_join_deck': ('Podesta za prahem', lambda: adjoining_landing(enclosed=False)),
    'hvd_join_hall': ('Chodba za prahem', lambda: adjoining_landing(enclosed=True)),
    'hvd_sliprock': ('Zvětralý líc skalního hřbetu', lambda: cliff_course(5.94,5.08,622)),
    'hvd_serviceslab': ('Kamenná vyzdívka', service_slab),
    'hvd_rift_in': ('Pokračování do skalní štoly',lambda: service_view(False)),
    'hvd_rift_out': ('Zasněžené závětří před štolou',lambda: service_view(True)),
    'hvd_optcover': ('Uzávěr Schodů do nebe', dome_shutter),
    'hvd_stairview': ('První schody pod září portálu', stair_portal),
    'hvd_domelight': ('Paprsek seřízeného refraktoru', dome_ray),
    'hvd_topview': ('Schody za Bránou tří paprsků', gate_preview),
    'hvd_lampray': ('Trvalý odraz u poslední lucerny', lantern_ray),
    'hvd_lampclosed': ('Sklopená clona poslední lucerny', lantern_closed),
}
