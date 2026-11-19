"""Architectural pieces and furnishings for the observatory."""

from math import cos, pi, sin, tau
import random
import struct

from art import AMBER, BLUE, BRASS, CROWN, DARK, GILT, STONE, TRIM, Material, Mesh, add, arch, star


MASONRY = Material((.91, .88, .82), "hvd_ashlar")
LIMESTONE = Material((.98, .95, .88), "hvd_ashlar")
BASALT = Material((.51, .61, .72), "hvd_rough")
SLATE = Material((.48, .56, .70), "hvd_paving")
INDIGO = Material((.45, .56, .78), "hvd_mosaic")
WARM = Material((.79, .65, .52), "hvd_paving")
WOOD = Material((.80, .68, .50), "hvd_oak")
OLDWOOD = Material((.50, .43, .37), "hvd_oak")
PARCHMENT = Material((.93, .82, .59), "hvd_paper")
PAPER = Material((.92, .91, .80), "hvd_paper")
CLOTH = Material((.31, .40, .67), "hvd_weave")
CLOTH_WARM = Material((.68, .31, .24), "hvd_weave")
SNOW = Material((.90, .95, 1.0), "hvd_frost")
ICE = Material((.46, .72, .97), "hvd_frost", (.115, .20, .33))
PALE = Material((.76, .89, 1.0), "hvd_glass", (.40, .56, .77))
GLINT = Material((.91, .71, .93), "hvd_glass", (.25, .30, .54), alpha=.74)
VORTEX = Material((.59, .78, 1.0), "hvd_glass", (.41, .58, .88), alpha=.29)
VEIL = Material((.72, .83, 1.0), "hvd_clouds", (.24, .35, .59), alpha=.62)


def surface(m, material, x0, y0, x1, y1, z, repeat=1.0):
    m.polygon(material, ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)),
              ((0, 0), ((x1 - x0) * repeat, 0), ((x1 - x0) * repeat, (y1 - y0) * repeat),
               (0, (y1 - y0) * repeat)))


def rosette(m, x, y, z, radius, mat=GILT, spokes=8):
    # A standing relief faces the approaching player.
    for i in range(spokes):
        a = i * tau / spokes
        tip = (x + radius * cos(a), y, z + radius * sin(a))
        left = (x + radius * .30 * cos(a - .34), y, z + radius * .30 * sin(a - .34))
        right = (x + radius * .30 * cos(a + .34), y, z + radius * .30 * sin(a + .34))
        m.polygon(mat, (left, tip, right))
    m.disc(BRASS, (x, y + .018, z), (x, y - .023, z), radius * .23, sides=12)


def pillar(m, x, y, height=4.25, z=0.0, radius=.42):
    for offset, size, depth, mat in ((.0, 1.9, .23, BASALT), (.23, 1.64, .14, LIMESTONE),
                                      (.37, 1.42, .15, MASONRY), (.52, 1.14, .13, BRASS),
                                      (height - .43, 1.24, .17, MASONRY),
                                      (height - .26, 1.59, .11, LIMESTONE),
                                      (height - .15, 1.86, .15, MASONRY)):
        m.box(mat, x, y, z + offset, size * radius * 2, size * radius * 2, depth)
    m.tube(MASONRY, (x, y, z + .59), (x, y, z + height - .39), radius, radius * .86, sides=12)
    for theta in (pi / 4, 3 * pi / 4, 5 * pi / 4, 7 * pi / 4):
        dx, dy = cos(theta) * radius * .98, sin(theta) * radius * .98
        m.tube(LIMESTONE, (x + dx, y + dy, z + .65),
               (x + dx * .87, y + dy * .87, z + height - .39), radius * .10, sides=6)


def tall_pier():
    m = Mesh()
    pillar(m, 0, 0, 5.55, radius=.49)
    rosette(m, 0, -.46, 3.95, .24)
    return m


def broken_pier():
    m = Mesh()
    pillar(m, 0, 0, 2.65, radius=.41)
    m.box(BASALT, .38, -.29, 2.55, .37, .30, .19)
    m.box(DARK, -.19, -.10, 2.67, .52, .60, .24)
    return m


def dado(upper=True):
    m = Mesh()
    h = 2.50 if upper else 1.02
    m.box(MASONRY, 0, 0, .03, 4.92, .49, h)
    for z, thickness in ((.03,.15), (.22,.08), (h - .02,.10), (h + .11,.095)):
        m.box(TRIM, 0, 0, z, 4.99, .67, thickness)
    for x in (-1.63, 0.0, 1.63):
        m.box(DARK, x, -.266, .39, 1.08, .075, h - .40 if upper else .42)
        m.box(SLATE, x, -.31, .45, .91, .11, h - .56 if upper else .30)
        if upper:
            rosette(m, x, -.388, 1.36, .31)
    return m


def window():
    m = Mesh()
    m.box(MASONRY, 0, .05, 0, 2.65, .45, 4.2)
    m.box(BASALT, 0, -.25, .74, 1.66, .15, 2.73)
    arch(m, .70, 2.24, -.43, .11, .18, LIMESTONE)
    m.box(AMBER, 0, -.382, .95, 1.18, .025, 2.02)
    for x in (-.40, 0, .40):
        m.box(BRASS, x, -.42, .92, .04, .08, 2.11)
    for z in (1.55, 2.24):
        m.box(BRASS, 0, -.426, z, 1.22, .07, .036)
    m.box(TRIM, 0, -.20, .79, 1.79, .78, .16)
    rosette(m, 0, -.47, 3.12, .40)
    return m


def cloister():
    m = Mesh()
    arch(m, 2.16, 2.72, 0, .44, .58, MASONRY, masonry=True)
    arch(m, 2.10, 2.73, -.345, .065, .09, BRASS)
    for x in (-2.42, 2.42):
        pillar(m, x, -.04, 2.81, radius=.26)
        m.box(BASALT, x, .04, .12, .81, 1.12, .13)
    rosette(m, 0, -.36, 5.14, .29)
    return m


def shutter_window():
    m = Mesh()
    m.box(BASALT, 0, 0, .24, 2.87, .40, 4.32)
    m.box(MASONRY, 0, -.27, .43, 2.48, .24, 3.85)
    m.box(INDIGO, 0, -.45, .89, 1.88, .20, 2.81)
    arch(m, .94, 2.92, -.61, .15, .15, TRIM)
    for z in (1.07, 1.40, 1.73, 2.07, 2.39, 2.71):
        m.box(BRASS if z == 2.07 else DARK, 0, -.62, z, 1.81, .19, .180)
        m.box(BLUE, 0, -.722, z + .171, 1.61, .019, .033)
    for x in (-1.13, 1.13):
        m.tube(BRASS, (x, -.74, .7), (x, -.74, 3.26), .069, sides=8)
    rosette(m, 0, -.54, 4.04, .24, PALE)
    return m


def shutter_track():
    m = Mesh()
    for x in (-.24, .27):
        m.tube(BRASS, (x, -2.42, 0), (x, 2.42, 0), .039, sides=6)
    for y in (-2.15, -1.08, 0, 1.08, 2.15):
        m.box(MASONRY, 0, y, -.048, .83, .27, .059)
        m.box(DARK, 0, y, .012, .85, .11, .035)
    return m


def facade():
    m = Mesh()
    m.box(MASONRY, 0, 0, 0, 5.7, .47, 4.95)
    for x in (-2.43, 2.43):
        pillar(m, x, -.24, 5.13, radius=.28)
    m.box(BASALT, 0, -.27, .69, 3.23, .19, 2.72)
    for x in (-.97, 0, .97):
        m.box(INDIGO, x, -.387, .84, .75, .10, 2.37)
        m.box(BLUE, x, -.447, 2.50, .43, .025, .57)
        m.box(BRASS, x, -.469, 1.22, .074, .067, 1.94)
    m.box(TRIM, 0, -.13, 4.22, 5.77, .73, .14)
    rosette(m, 0, -.30, 3.82, .38, GILT, 12)
    return m


def field_shelter(workbench=False):
    m = Mesh()
    sx = 3.38 if workbench else 3.74
    for x, y in ((-sx,-1.75), (sx,-1.75), (-sx,1.72), (sx,1.72)):
        m.box(BASALT, x, y, 0, .83, .78, .32)
        m.box(WOOD, x, y, .30, .29, .31, 2.98)
        m.tube(OLDWOOD, (x, y, 2.53), (x * .83, y *.91, 3.13), .095, sides=8)
    m.box(MASONRY if workbench else OLDWOOD, 0, 1.83, 0, sx * 2.09, .41, 2.52)
    for z in (.30, 1.05, 1.80, 2.48):
        m.box(TRIM if workbench else WOOD, 0, 1.59, z, sx * 2.08, .105, .109)
    m.box(WOOD, 0, 1.58, 3.01, sx * 2.33, .35, .31)
    m.box(OLDWOOD, 0, -1.65, 2.96, sx * 2.33, .35, .32)
    roof_mat = CROWN if workbench else CLOTH_WARM
    for direction in (-1,1):
        a, b = direction * 2.27, 0.0
        roof = [(-sx - .32, a, 3.24), (sx + .32, a, 3.24),
                (sx + .32, b, 4.31), (-sx - .32, b, 4.31)]
        m.polygon(roof_mat, roof if direction < 0 else list(reversed(roof)))
        m.polygon(OLDWOOD, list(reversed(roof)) if direction < 0 else roof)
        for x in (-2.87, -.96, .96, 2.87):
            m.tube(WOOD, (x, a, 3.265), (x, b, 4.33), .045, sides=6)
        m.tube(TRIM, (-sx-.38, a, 3.24), (sx+.38, a, 3.24), .085, sides=8)
    m.tube(CROWN, (-sx-.38, 0, 4.32), (sx+.38, 0, 4.32), .105, sides=10)
    return m


def rock_mound(seed, snow, spread, height):
    m = Mesh()
    rng = random.Random(seed)
    for x,y,w,h in ((0, 0, spread, height), (-spread * .64, 1.0, spread * .49, height * .54),
                    (spread * .68, -.96, spread * .53, height * .67)):
        sides = 8
        rings = []
        angles = [tau * i / sides + rng.uniform(-.15,.15) for i in range(sides)]
        factors = [rng.uniform(.74,1.23) for _ in angles]
        for layer,r in enumerate((1.0,.83,.64,.32,.04)):
            z = (-.23,.22*h,.51*h,.82*h,h)[layer]
            rings.append([(x + cos(a)*w*f*r + layer*.14, y + sin(a)*w*f*r*.75,
                           z + rng.uniform(-.07,.07)*h) for a,f in zip(angles,factors)])
        for level in range(len(rings)-1):
            for i in range(sides):
                j = (i+1)%sides
                lower, upper = rings[level], rings[level+1]
                material = SNOW if snow and (level == 3 or (level==2 and i%3!=0)) else (BASALT if i%3 else SLATE)
                m.polygon(material, (lower[i], lower[j], upper[j]))
                m.polygon(material if i%2 else (SNOW if snow and level==3 else SLATE),
                          (lower[i], upper[j], upper[i]))
        m.polygon(SNOW if snow else BASALT, rings[-1])
    return m


def inset(warm=False, narrow=False):
    m = Mesh()
    w,x = (1.48, 2.49) if narrow else (2.39, 2.46)
    surface(m, WARM if warm else INDIGO, -w, -x, w, x, .013, .41)
    for py in (-x+.11,x-.11):
        m.trace(GILT, (-w+.03,py,.022), (w-.03,py,.022), .026)
    for px in (-w+.03,w-.03):
        m.trace(BRASS, (px,-x+.11,.022), (px,x-.11,.022), .032)
        for y in (-x+.29,x-.29):
            star(m,px*.83,y,.025,.142,PALE if not warm else GILT,4)
    m.ring(BRASS, .43, .035,.025,24)
    star(m,0,0,.027,.30,GILT,4)
    return m


def stone_landing():
    m = Mesh()
    surface(m, SLATE, -6, -4.20, 6, 4.20, .029, .22)
    for x in (-5.93, 5.93):
        m.box(TRIM, x, 0, -.05, .16, 8.4, .105)
    for y in (-4.13, 4.13):
        m.box(TRIM, 0, y, -.05, 12.15, .16, .105)
    for x in (-4.8, 0.0, 4.8):
        star(m, x, -3.27, .037, .22, GILT, 4)
    return m


def banner(warm, long=False):
    m = Mesh()
    w, h = (.47, 2.19) if long else (.49, 1.59)
    mat = CLOTH_WARM if warm else CLOTH
    m.tube(BRASS, (-w-.22, 0, h + .08), (w+.22,0,h+.08), .047, sides=8)
    for sign in (-1,1):
        m.disc(GILT, (sign*(w+.19),0,h+.08), (sign*(w+.245),0,h+.08), .079, sides=8)
    columns = 10
    for i in range(columns):
        low, high = -w + 2*w*i/columns, -w + 2*w*(i+1)/columns
        def point(x,z):
            return (x, -.08 + .081 * sin(x*13), z)
        top = [point(low,h),point(high,h)]
        bottom = [point(low,.23 + abs(low)*.72),point(high,.23 + abs(high)*.72)]
        for pair in ((bottom[0],bottom[1],top[1],top[0]), (bottom[1],bottom[0],top[0],top[1])):
            m.polygon(mat,pair)
        m.tube(BRASS,bottom[0],bottom[1],.021,sides=6)
    rosette(m,0,-.19,h*.66,.38)
    return m


def worktools():
    m=Mesh()
    for x, y, l in ((-.38,-.27,.27),(.03,.18,.42),(.43,-.16,.32)):
        m.tube(WOOD,(x,y,.027),(x+l,y+.09,.027),.038,sides=8)
        m.box(BRASS,x+l,y+.074,.017,.13,.137,.07)
    m.disc(DARK,(-.38,.25,.011),(-.38,.25,.081),.19,sides=10)
    m.disc(ICE,(-.38,.25,.081),(-.38,.25,.103),.13,sides=10)
    m.box(BASALT,.40,.15,.01,.19,.17,.07)
    return m


def open_book():
    m = Mesh()
    m.box(OLDWOOD,0,0,.018,.68,.49,.052)
    for i in (-1,1):
        m.polygon(PARCHMENT, ((i*.02,-.23,.082),(i*.33,-.23,.123),
                             (i*.33,.23,.123),(i*.02,.23,.082))[::i])
        for y in (-.15,-.09,-.035,.03,.091,.147):
            m.trace(DARK,(i*.075,y,.098),(i*(.27 if y < .10 else .20),y,.13),.008)
    m.trace(GILT,(0,-.24,.087),(0,.24,.087),.027)
    return m


def supply_crate():
    m = Mesh()
    m.box(OLDWOOD,0,0,0,1.12,.75,.64)
    for y in (-.354,.34):
        m.box(WOOD,0,y,.605,1.16,.095,.066)
        for x in (-.435,.435):
            m.box(WOOD,x,y,.055,.117,.097,.548)
            m.box(BRASS,x,y*1.218,.38,.132,.024,.10)
    m.box(WOOD,0,0,.625,1.15,.76,.09)
    return m


def shelf():
    m = Mesh()
    for x in (-.96,.96):
        m.box(OLDWOOD,x,0,.06,.14,.66,2.12)
    m.box(BASALT,0,.24,.14,1.87,.13,1.99)
    for level,z in enumerate((.070,.70,1.37,2.11)):
        m.box(WOOD,0,0,z,2.09,.72,.13)
        if level < 3:
            for i,x in enumerate((-.74,-.49,-.235,.47,.68)):
                h=.28+((i*17+level*13)%5)*.04
                m.box((INDIGO, PARCHMENT, OLDWOOD, CLOTH_WARM)[(i+level)%4], x, .01,z+.145,.194,.43,h)
                m.box(BRASS,x,-.229,z + h*.68+.145,.17,.025,.024)
    m.box(TRIM,0,0,2.23,2.25,.84,.08)
    return m


def lantern_cage():
    m = Mesh()
    m.disc(DARK,(0,0,-.20),(0,0,-.105),.26,sides=8)
    m.disc(AMBER,(0,0,-.11),(0,0,.31),.14,sides=12)
    for i in range(6):
        a=tau*i/6
        x,y=.20*cos(a),.20*sin(a)
        m.tube(BRASS,(x,y,-.13),(x,y,.34),.024,sides=6)
    m.tube(CROWN,(0,0,.31),(0,0,.53),.255,.06,sides=8)
    m.tube(BRASS,(0,0,.46),(0,0,.79),.035,sides=6)
    return m


def lectern():
    m=Mesh()
    pillar(m,0,0,1.02,radius=.20)
    m.box(WOOD,0,0,.97,.86,.55,.14)
    m.box(BRASS,0,-.28,1.09,.89,.07,.085)
    m.box(PARCHMENT,.05,0,1.115,.60,.39,.025)
    return m


def armillary():
    m = Mesh()
    pillar(m,0,0,.99,radius=.23)
    center=(0,0,1.80)
    m.disc(BRASS,(0,0,1.01),(0,0,1.16),.36,sides=16)
    for plane in (0,.89,1.56):
        last=None
        for i in range(33):
            az=i*tau/32
            p=(.74*cos(az),.74*sin(az)*cos(plane),.74*sin(az)*sin(plane))
            p=add(center,p)
            if last:
                m.tube(BRASS if plane != .89 else GILT,last,p,.034,sides=5)
            last=p
    m.tube(DARK,(0,0,1.19),(0,0,2.58),.047,sides=8)
    m.tube(GLINT,(0,0,1.59),(0,0,2.02),.23,.17,sides=16)
    return m


def curved_rib():
    m = Mesh()
    # Profile for an open cupola. Point the foot toward the centre when dressing the room.
    pillar(m,0,0,4.90,radius=.43)
    last=(0,0,4.86)
    prev=(.0,-.25,4.86)
    for i in range(1,17):
        a=i*pi/34
        p=(0, 9*(1-cos(a)),4.86+5.15*sin(a))
        q=(0,p[1]-.27,p[2]-.13)
        m.tube(CROWN,last,p,.26,sides=8)
        m.tube(BRASS,prev,q,.043,sides=6)
        last,prev=p,q
    return m


def refractor_housing():
    m = Mesh()
    for ang in range(10):
        a=ang*tau/10
        x,y=1.71*cos(a),1.71*sin(a)
        m.box(TRIM,x,y,.21,.24,.20,.43)
        m.disc(BRASS,(x,y,.52),(x,y,.63),.139,sides=8)
    m.ring(GILT,1.77,.060,.045,40)
    m.ring(BLUE,1.98,.024,.035,40)
    for x in (-.75,.75):
        m.tube(BRASS,(x,-.72,0),(x,-1.13,1.48),.065,sides=8)
    return m


def bridge_face():
    m=Mesh()
    # Decorative masonry spans below the native bridge's walking surface.
    for column in range(16):
        y0 = -7.31 + column*.916
        y1 = y0+.916
        def floor(y):
            return min(1.63, 2.09 - .014*y*y)
        def arch_base(y):
            return -3.6 + 4.45 * max(0., 1 - (y/7.32)**2) ** .53
        for x in (-1.42,1.42):
            for order in (1,-1):
                m.polygon(MASONRY, [(x,y0,floor(y0)),(x,y0,arch_base(y0)),
                                    (x,y1,arch_base(y1)),(x,y1,floor(y1))][::order])
            m.tube(TRIM,(x,y0,arch_base(y0)),(x,y1,arch_base(y1)),.10,sides=7)
            m.tube(TRIM,(x,y0,floor(y0)),(x,y1,floor(y1)),.071,sides=7)
    for y in (-7.05,7.05):
        m.box(BASALT,0,y,-5.7,3.40,1.9,4.66)
        m.box(TRIM,0,y,-1.04,3.59,1.99,.28)
    return m


def finial(warm=False):
    m=Mesh()
    pillar(m,0,0,1.89,radius=.17)
    m.tube(BRASS,(0,0,1.88),(0,0,2.02),.26,.16,sides=10)
    colour=AMBER if warm else PALE
    m.tube(colour,(0,0,2.01),(0,0,2.20),.18,.105,sides=8)
    return m


def sentry_alcove():
    m=Mesh()
    arch(m,1.58,2.03,-.3,.20,.68,MASONRY,masonry=True)
    for x in (-1.79,1.79):
        pillar(m,x,0,2.51,radius=.22)
    m.box(BASALT,0,1.65,.12,3.68,.35,2.42)
    m.box(MASONRY,0,1.55,2.72,3.88,.88,.26)
    m.box(CROWN,0,.58,3.70,4.1,2.92,.16)
    rosette(m,0,-.72,3.76,.31)
    return m


def wall_brazier():
    m=Mesh()
    m.box(BASALT,0,.1,-.23,.54,.36,.65)
    m.tube(BRASS,(0,.12,-.16),(0,-.43,.21),.072,sides=8)
    m.tube(DARK,(0,-.45,.14),(0,-.45,.34),.17,.34,sides=12)
    m.disc(GILT,(0,-.45,.32),(0,-.45,.40),.30,sides=12)
    m.tube(AMBER,(0,-.45,.39),(0,-.45,.79),.16,.027,sides=10)
    return m


def gate_crest():
    m=Mesh()
    for z,w in ((5.68,6.95),(5.93,6.75),(6.38,6.31)):
        m.box(MASONRY,0,0,z,w,.72,.19)
    m.box(DARK,0,.13,6.48,4.4,.41,1.41)
    m.box(TRIM,0,.11,7.86,4.82,.74,.19)
    m.disc(MASONRY,(0,.05,7.16),(0,-.49,7.16),.78,sides=16)
    m.disc(BASALT,(0,-.46,7.16),(0,-.57,7.16),.67,sides=16)
    rosette(m,0,-.615,7.16,.57,GILT,12)
    for x in (-2.12,2.12):
        m.box(TRIM,x,-.06,6.45,.38,.89,1.59)
        m.disc(BRASS,(x,0,8.04),(x,0,8.18),.37,sides=12)
        m.tube(PALE,(x,0,8.18),(x,0,8.61),.21,.028,sides=10)
    return m


def service_hoist():
    m=Mesh()
    for x in (-1.47,1.47):
        m.box(BASALT,x,0,0,.65,.74,.45)
        m.box(WOOD,x,0,.40,.27,.30,3.48)
        m.tube(OLDWOOD,(x,0,2.25),(x*.54,0,3.73),.098,sides=8)
    m.box(WOOD,0,0,3.66,3.7,.39,.38)
    m.tube(BRASS,(-.25,0,3.32),(.25,0,3.32),.22,sides=12)
    m.tube(OLDWOOD,(.13,-.02,3.41),(.13,-.02,1.17),.042,sides=8)
    m.tube(BRASS,(.13,-.02,1.18),(.13,-.25,1.06),.091,.064,sides=8)
    m.box(DARK,.14,-.13,1.0,.17,.08,.18)
    return m


def lattice():
    m = Mesh()
    for x in (-2.0, 2.0):
        m.box(BASALT,x,0,0,.37,.51,.19)
        m.box(MASONRY,x,0,.17,.23,.31,2.44)
    for z in (.20,1.32,2.53):
        m.box(TRIM,0,0,z,4.15,.40,.103)
    for x in (-1.60,-1.19,-.8,-.4,0,.4,.8,1.19,1.60):
        m.tube(BRASS,(x,0,.29),(x,0,2.52),.029,sides=6)
    for x in (-1.33,0,1.33):
        rosette(m,x,-.073,1.94,.27)
    return m


def altar():
    m=Mesh()
    for z,width,depth,h,mat in ((0,5.0,2.71,.18,BASALT),(.18,4.73,2.48,.16,TRIM),
                               (.34,4.20,1.98,.39,MASONRY),(.73,4.45,2.15,.12,TRIM)):
        m.box(mat,0,0,z,width,depth,h)
    for x in (-1.38,0,1.38):
        rosette(m,x,-1.025,.52,.158)
    return m


def pavilion():
    m=Mesh()
    for x,y in ((-5,0),(5,0),(-5,3.3),(5,3.3)):
        pillar(m,x,y,5.70,radius=.35)
    for y in (0,3.3):
        arch(m,4.65,5.41,y,.36,.62,MASONRY,masonry=True)
        arch(m,4.45,5.44,y-.42,.064,.08,BRASS)
    for x in (-5,5):
        m.box(TRIM,x,1.65,5.41,.65,3.99,.22)
    rosette(m,0,-.449,10.30,.42)
    return m


def eddy():
    m=Mesh()
    for layer in range(5):
        turns=1.70 + .05*layer
        phase=layer*1.16
        last=None
        for i in range(65):
            t=i/64
            yaw=phase+turns*tau*t
            radius=1.15+1.67*t + .30*sin(t*11+phase)
            p=(radius*cos(yaw),radius*sin(yaw),.33+t*(6.35+layer*.31))
            off=(.12*cos(yaw),.12*sin(yaw),.175+.09*(1-t))
            if last:
                m.polygon(VORTEX,(last[0],p,add(p,off),add(last[0],last[1])))
                m.polygon(VORTEX,(add(last[0],last[1]),add(p,off),p,last[0]))
            if layer < 2 and last and 7 < i < 53 and i % 3:
                m.tube(GLINT,last[0],p,.048,sides=6)
            last=p,off
    for radius in (1.31,2.11,2.42):
        m.ring(BLUE,radius,.044,.053,48)
    return m


def mist_bank():
    m=Mesh()
    for layer,(width,depth,height) in enumerate(((40,27,.16),(33,23,1.7),(25,18,3.3))):
        surface(m,VEIL,-width/2,-depth/2,width/2,depth/2,height,.053+.005*layer)
    return m


def wall_chart():
    m = Mesh()
    m.box(WOOD,0,.075,1.13,3.82,.19,2.24)
    m.box(INDIGO,0,-.046,1.26,3.55,.052,1.98)
    for z in (1.14,3.36):
        m.box(BRASS,0,-.063,z,3.91,.115,.054)
    for x in (-1.87,1.87):
        m.box(BRASS,x,-.067,1.14,.065,.12,2.25)
    routes = ((-1.48,1.73),(-.77,2.04),(-.16,1.80),(.42,2.51),(1.42,2.86),(.98,2.36))
    for i,(x,z) in enumerate(routes):
        rosette(m,x,-.083,z,.13 if i in (0,3) else .10,PALE,4)
        if i:
            ox,oz=routes[i-1]
            m.tube(BRASS,(ox,-.087,oz),(x,-.087,z),.018,sides=5)
    return m


def wall_lining():
    m = Mesh()
    m.box(MASONRY,0,.31,0,5.03,.59,3.04)
    m.box(BASALT,0,.11,0,5.03,.27,.59)
    m.box(LIMESTONE,0,.14,.56,5.01,.25,.13)
    m.box(MASONRY,0,.16,2.78,5.01,.28,.19)
    m.box(BRASS,0,.012,2.95,5.0,.038,.043)
    for x in (-1.25,1.25):
        m.box(DARK,x,.011,.19,1.89,.049,.22)
        rosette(m,x,-.019,.30,.105,GILT,4)
    return m


def apse_wall():
    m=wall_lining()
    for x in (-1.62,1.62):
        pillar(m,x,.14,3.0,radius=.21)
    m.box(BASALT,0,.15,3.06,5.04,.93,.32)
    m.box(LIMESTONE,0,.08,3.38,5.05,1.06,.13)
    return m


def lens_rack():
    m = Mesh()
    m.box(OLDWOOD,0,.18,.26,2.85,.35,2.49)
    m.box(WOOD,0,.13,.26,2.93,.48,.095)
    for x in (-1.39,1.39):
        m.box(WOOD,x,.11,.25,.16,.52,2.69)
    for z in (1.04,1.93,2.66):
        m.box(WOOD,0,-.06,z,2.95,.70,.10)
        m.box(BRASS,0,-.419,z+.04,2.86,.055,.047)
    for x,z,r in ((-.97,1.40,.26),(-.27,1.35,.23),(.48,1.32,.18),(1.06,1.30,.16),
                  (-.94,2.27,.20),(.02,2.30,.26),(.9,2.27,.20)):
        m.disc(BRASS,(x,.03,z),(x,-.164,z),r,sides=16)
        m.disc(PALE,(x,-.161,z),(x,-.18,z),r*.77,sides=16)
    m.box(TRIM,0,.16,2.89,2.99,.55,.15)
    return m


def ring_handle():
    m = Mesh()
    m.box(DARK,0,.14,0,.61,.29,1.46)
    m.box(BRASS,0,-.056,1.23,.24,.16,.27)
    for i in range(16):
        a,b=i*tau/16,(i+1)*tau/16
        m.tube(BRASS,(.132*cos(a),-.233,1.20+.132*sin(a)),
                    (.132*cos(b),-.233,1.20+.132*sin(b)),.028,sides=6)
    m.tube(GILT,(0,-.231,1.34),(0,-.048,1.35),.035,sides=8)
    return m


def concealed_panel(books=False):
    m = Mesh()
    # The top and bottom rails run into the matching wall lining at each end.
    width = 4.88
    m.box(OLDWOOD if books else MASONRY,0,0,0,width,.38,3.43)
    m.box(TRIM,0,-.02,.0,width+.07,.50,.24)
    m.box(TRIM,0,-.02,3.23,width+.05,.49,.20)
    for x in (-2.19,0,2.19):
        m.box(WOOD if books else BASALT,x,-.22,.21,.13,.19,2.97)
    if books:
        for row,z in enumerate((.58,1.36,2.09)):
            m.box(WOOD,0,-.22,z,4.40,.41,.11)
            for i in range(17):
                x=-2.05+i*.243
                if (i+row*3)%9==0:
                    continue
                height=.24+.04*((i*7+row)%5)
                m.box((INDIGO,OLDWOOD,PARCHMENT,CLOTH_WARM)[(i+row)%4],
                      x,-.323,z+.10,.172,.22,height)
    else:
        for x in (-1.16,1.16):
            rosette(m,x,-.213,2.01,.28)
        m.box(BRASS,0,-.212,1.04,3.83,.054,.086)
    return m


def sky_portal():
    m=Mesh()
    arch(m,2.52,3.32,0,.43,.74,LIMESTONE,masonry=True)
    arch(m,2.49,3.32,-.429,.068,.085,BRASS)
    for x in (-2.79,2.79):
        pillar(m,x,0,3.38,radius=.35)
        m.box(BASALT,x,0,0,1.37,1.01,.20)
        m.box(INDIGO,x,-.47,1.38,.37,.12,.99)
        rosette(m,x,-.55,2.34,.24,PALE)
        m.tube(BRASS,(x,-.363,2.12),(x,-.72,2.23),.052,sides=7)
        m.tube(PALE,(x,-.69,2.21),(x,-.69,2.81),.126,.065,sides=12)
    rosette(m,0,-.413,6.06,.325,GILT,12)
    return m


def sky_parapet():
    m=Mesh()
    m.box(MASONRY,0,0,0,4.92,.63,.35)
    for x in (-2.01,0,2.01):
        m.box(LIMESTONE,x,0,.31,.34,.67,.82)
        rosette(m,x,-.333,.70,.148,PALE)
    for x in (-1.65,-1.10,-.54,.54,1.10,1.65):
        m.tube(DARK,(x,0,.31),(x,0,1.01),.093,sides=8)
        m.disc(BRASS,(x,0,.63),(x,0,.73),.116,sides=8)
    m.box(TRIM,0,0,1.03,5.03,.74,.16)
    m.box(BRASS,0,-.357,1.14,4.91,.045,.029)
    return m


def sky_shelter():
    m=Mesh()
    m.box(MASONRY,0,1.78,0,6.9,.48,3.04)
    for x in (-3.18,3.18):
        pillar(m,x,-.70,3.04,radius=.30)
        m.box(LIMESTONE,x,1.32,0,.44,1.15,3.00)
        m.box(MASONRY,x,.61,2.58,.66,3.05,.47)
        m.box(TRIM,x,.54,2.98,.89,3.60,.15)
    arch(m,2.73,2.95,-.69,.57,.67,LIMESTONE,masonry=True)
    arch(m,2.73,2.95,-1.056,.075,.074,BRASS)
    arch(m,2.76,2.95,1.69,.51,.61,MASONRY)
    for i in range(16):
        a,b=pi*i/16,pi*(i+1)/16
        x1,z1=3.34*cos(a),2.97+3.27*sin(a)
        x2,z2=3.34*cos(b),2.97+3.27*sin(b)
        m.polygon(CROWN if i%4 else DARK,
                  ((x1,-1.11,z1),(x1,2.24,z1),(x2,2.24,z2),(x2,-1.11,z2)))
        m.polygon(MASONRY,((0,1.99,2.94),(x1,1.99,z1),(x2,1.99,z2)))
        for y in (-1.13,1.01,2.24):
            m.tube(BRASS,(x1,y,z1),(x2,y,z2),.042,sides=6)
    for x in (-2.00,0,2.0):
        m.box(INDIGO,x,1.48,1.32,1.43,.16,1.73)
        rosette(m,x,1.36,2.40,.30,PALE)
    m.box(BASALT,0,1.98,0,6.98,.38,.30)
    return m


def eave_arch():
    m=Mesh()
    for x in (-3.13,3.13):
        m.box(BASALT,x,0,-7.05,2.44,3.88,7.25)
        m.box(MASONRY,x,0,.15,2.44,3.87,2.91)
        m.box(LIMESTONE,x,0,2.48,2.65,4.13,.53)
        m.box(BASALT,x,0,5.8,2.50,4.05,1.27)
    for y in (-1.84,1.84):
        arch(m,2.36,2.38,y,.65,.53,LIMESTONE,masonry=True)
        arch(m,2.37,2.38,y+.21,.12,.09,BRASS)
    arch(m,2.38,2.39,0,1.23,3.8,MASONRY)
    m.box(MASONRY,0,0,5.76,9.07,4.2,1.29)
    m.box(TRIM,0,0,6.97,9.24,4.44,.24)
    m.box(BASALT,0,0,7.20,9.25,4.45,.28)
    rosette(m,0,-2.203,6.48,.29,PALE)
    return m


def beacon_tower():
    m=Mesh()
    m.disc(LIMESTONE,(0,0,0),(0,0,.39),2.07,sides=12)
    m.tube(MASONRY,(0,0,.4),(0,0,5.93),1.55,1.28,sides=12)
    m.disc(LIMESTONE,(0,0,5.88),(0,0,6.2),1.76,sides=12)
    m.disc(BASALT,(0,0,6.13),(0,0,6.47),1.69,sides=12)
    for i in range(8):
        a=i*tau/8
        x,y=1.30*cos(a),1.30*sin(a)
        pillar(m,x,y,2.48,6.44,.13)
        m.tube(BRASS,(x,y,7.04),(1.30*cos(a+tau/8),1.30*sin(a+tau/8),7.04),.044,sides=6)
    m.tube(PALE,(0,0,6.74),(0,0,8.61),.52,.32,sides=12)
    m.disc(TRIM,(0,0,8.84),(0,0,9.01),1.78,sides=12)
    m.tube(CROWN,(0,0,8.98),(0,0,10.35),1.70,.19,sides=12)
    m.tube(BRASS,(0,0,10.26),(0,0,11.01),.11,.05,sides=8)
    for y,z in ((-1.32,2.3),(-1.31,4.28)):
        m.box(BASALT,0,y,z,.59,.24,1.04)
        m.box(INDIGO,0,y-.12,z+.15,.36,.16,.67)
    return m


def hanging_pier():
    m=Mesh()
    m.tube(BASALT,(0,0,-7.6),(0,0,-.38),.97,1.82,sides=12)
    m.disc(LIMESTONE,(0,0,-.90),(0,0,-.20),2.18,sides=12)
    m.disc(DARK,(0,0,-4.44),(0,0,-3.88),1.31,sides=12)
    m.disc(BRASS,(0,0,-4.18),(0,0,-3.98),1.39,sides=12)
    m.disc(PALE,(0,0,-7.91),(0,0,-7.42),.36,sides=10)
    return m


def sky_inlay():
    m=Mesh()
    surface(m,SLATE,-1.70,-2.485,1.70,2.485,.022,.31)
    for x in (-1.51,1.51):
        m.trace(BRASS,(x,-2.50,.032),(x,2.50,.032),.047)
        m.trace(PALE,(x*.92,-2.50,.033),(x*.92,2.50,.033),.020)
    star(m,0,0,.040,.34,GILT,4)
    return m


def sky_orrery():
    m=Mesh()
    for z,r in ((0,2.46),(.20,2.30),(.36,1.91)):
        m.disc(LIMESTONE,(0,0,z),(0,0,z+.20),r,sides=12)
    for x in (-1.21,1.21):
        pillar(m,x,0,3.75,radius=.25)
    m.tube(BRASS,(-2.00,0,3.91),(2.00,0,3.91),.10,sides=10)
    for index,(r,tilt) in enumerate(((2.76,.02),(2.25,.57),(1.51,1.02))):
        pts=[(r*cos(i*tau/48),r*sin(i*tau/48)*sin(tilt),3.91+r*sin(i*tau/48)*cos(tilt))
             for i in range(49)]
        for i,(pa,pb) in enumerate(zip(pts,pts[1:])):
            m.tube(BRASS if index!=1 else PALE,pa,pb,.079 if index==0 else .048,sides=6)
            if i%12==0:
                m.disc(GILT,add(pa,(0,0,-.10)),add(pa,(0,0,.12)),.14,sides=8)
    m.disc(PALE,(0,0,3.60),(0,0,4.22),.38,sides=16)
    return m


MODELS = {
    "hvd_tallpier": tall_pier, "hvd_brokpier": broken_pier,
    "hvd_wallpanel": dado, "hvd_wallfoot": lambda: dado(False),
    "hvd_window": window, "hvd_cloister": cloister, "hvd_shutwin": shutter_window,
    "hvd_guide": shutter_track, "hvd_facade": facade,
    "hvd_campshell": field_shelter, "hvd_shoproof": lambda: field_shelter(True),
    "hvd_crag": lambda: rock_mound(412, True, 6.3, 14.7),
    "hvd_snowbank": lambda: rock_mound(389, True, 2.05, 2.45),
    "hvd_isle": lambda: rock_mound(877, False, 4.7, 4.35),
    "hvd_rubble": lambda: rock_mound(42, False, .61, .78),
    "hvd_pave_n": inset, "hvd_pave_w": lambda: inset(True), "hvd_runner": lambda: inset(False, True),
    "hvd_bluebann": lambda: banner(False, True), "hvd_goldbann": lambda: banner(True, True),
    "hvd_tools": worktools, "hvd_openbook": open_book, "hvd_crate": supply_crate, "hvd_shelf": shelf,
    "hvd_oillamp": lantern_cage, "hvd_lectern": lectern, "hvd_armillary": armillary,
    "hvd_cupolarib": curved_rib, "hvd_mounttrim": refractor_housing, "hvd_bridgewall": bridge_face,
    "hvd_bluepost": finial, "hvd_amberpost": lambda: finial(True),
    "hvd_sentrybay": sentry_alcove, "hvd_sconce": wall_brazier, "hvd_gatecrest": gate_crest,
    "hvd_hoist": service_hoist, "hvd_grille": lattice, "hvd_altarbase": altar,
    "hvd_pavilion": pavilion, "hvd_eddy": eddy, "hvd_mistbank": mist_bank,
    "hvd_landing": stone_landing,
}

SKY_MODELS = {
    "hvd_wallchart": wall_chart, "hvd_lining": wall_lining, "hvd_lensrack": lens_rack,
    "hvd_wallring": ring_handle, "hvd_bookpanel": lambda: concealed_panel(True),
    "hvd_stonepanel": concealed_panel, "hvd_skyport": sky_portal,
    "hvd_skyrail": sky_parapet, "hvd_skybay": sky_shelter, "hvd_hangpier": hanging_pier,
    "hvd_skywalk": sky_inlay, "hvd_orrery": sky_orrery, "hvd_apsewall": apse_wall,
    "hvd_eavearch": eave_arch, "hvd_beactower": beacon_tower,
}


def painted_texture(seed, base, form, size=256):
    rng=random.Random(seed)
    pixels=bytearray()
    for y in range(size):
        for x in range(size):
            grain=(rng.random()-.5)*12
            n=(8*sin(x*.056 + 3*cos(y*.04))+5*sin(x*.24-y*.09)+4*cos(x*.42+y*.25)
               + 3*cos(y*.88+x*.184))
            if form in ("ashlar","paving"):
                step_y = 42 if form=="ashlar" else 64
                step_x = 64 if form=="ashlar" else 85
                row,joint_y=divmod(y,step_y)
                index,joint_x=divmod(x+step_x//2*(row%2),step_x)
                n+=9*sin(index*2.12+row*1.62)
                edge=min(joint_x,joint_y,step_x-joint_x,step_y-joint_y)
                n+= -35 if edge<2 else 15 if edge==2 else 4 if edge==3 else 0
            elif form=="mosaic":
                n+=12*cos(x*pi/31)*cos(y*pi/31)
                if (x%16<1 or y%16<1):
                    n-=18
            elif form=="wood":
                n+=12*sin(x*.35+2*sin(y*.02))+12*sin(x*.88+2.1*sin(y*.06))
                if x%51<2:
                    n-=26
            elif form=="paper":
                n+=6*cos(x*.055)*cos(y*.07)
                if (x%31==0 or y%31==0):
                    n-=22
            elif form=="weave":
                n+=7*((x+y)%3==0)+7*((x-y)%3==0)+13*cos(x*pi/128)*cos(y*pi/128)
            pixels.extend(max(0,min(255,int(value+n+grain))) for value in reversed(base))
    return struct.pack("<BBBHHBHHHHBB",0,0,2,0,0,0,0,0,size,size,24,0)+pixels


def architecture_textures():
    return {f"{name}.tga":painted_texture(seed,base,form)
            for name,seed,base,form in (
                ("hvd_ashlar",49,(163,153,146),"ashlar"), ("hvd_rough",59,(125,129,145),"rough"),
                ("hvd_paving",61,(151,149,154),"paving"), ("hvd_mosaic",67,(112,121,149),"mosaic"),
                ("hvd_oak",73,(122,89,69),"wood"), ("hvd_paper",79,(196,169,110),"paper"),
                ("hvd_weave",83,(126,129,147),"weave"), ("hvd_frost",97,(191,202,219),"rough"),
                ("tcm02_cobble01",101,(122,121,132),"paving"), ("tcm02_wall03",107,(120,114,117),"ashlar"),
                ("tcm02_wall03b",109,(129,121,126),"ashlar"),
            )}
