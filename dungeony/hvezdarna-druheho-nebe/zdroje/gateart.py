"""Station seals, the brass projector court and its changing optics."""

from math import cos, hypot, pi, sin, tau
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, PALE, SLATE, pillar, rosette
from art import BRASS, DARK, GILT, TRIM, Material, Mesh, arch, star


SOCKETS = ((27.8,29.45), (31.75,32.15), (41.0,29.45))
SHUTTER = (39.35,36.7)
GATE = (35.0,53.3)
GATE_HEIGHT = 10.0
SEAL_MODELS = (241, 242, 243, 244)

# The same raised device appears on the carried seal and the mounted impression.
SEAL_MARKS = (
    (((0,-.52),(0,.52)), ((-.36,.17),(.36,.17)),
     ((-.56,-.14),(-.45,-.35),(-.26,-.50),(0,-.55),(.26,-.50),(.45,-.35),(.56,-.14)),
     ((-.56,-.14),(-.56,-.33)), ((.56,-.14),(.56,-.33))),
    (((-.52,-.51),(.01,.33),(.50,.59),(.43,.23),(.23,-.10),(-.52,-.51)),
     ((-.33,-.22),(.30,.38)), ((-.15,-.11),(.38,.28)), ((.01,.01),(.25,.075))),
    (((-.31,-.59),(.22,.22)), ((.08,.20),(.46,.57),(.42,.06),(.08,.20)),
     ((-.11,-.28),(.015,-.35))),
    (((-.35,-.44),(.35,-.44),(.29,.20),(-.29,.20),(-.35,-.44)),
     ((-.41,.20),(0,.43),(.41,.20)), ((-.12,.43),(0,.58),(.12,.43)),
     ((0,-.39),(-.13,-.15),(0,.015),(.14,-.15),(0,-.39))),
)

ENAMELS = ((47,89,119), (87,51,117), (39,98,91), (131,75,37))
FILTER_COLORS = ((.69,.54,1.0), (.43,.83,1.0), (1.0,.69,.26))


def circle(radius, width=24, x=0, y=0):
    return tuple((x+radius*cos(tau*i/width),y+radius*sin(tau*i/width)) for i in range(width+1))


def segment_distance(x, y, a, b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    distance=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
    return hypot(x-a[0]-distance*dx,y-a[1]-distance*dy)


def seal_icon(sign):
    size=64
    header=pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,32,8)
    strokes=[(a,b) for path in SEAL_MARKS[sign-1] for a,b in zip(path,path[1:])]
    body=bytearray()
    for row in range(size):
        y=(row+0.5-size/2)/(size*.5)
        for col in range(size):
            x=(col+0.5-size/2)/(size*.5)
            edge=(abs(x)**3.5+abs(y)**3.5)**(1/3.5)
            if edge>.89:
                body.extend((0,0,0,0))
                continue
            if edge>.79:
                base=(180,126,63) if y+x<.59 else (237,190,101)
            elif edge>.69:
                base=(83,52,34)
            elif any(segment_distance(x,y,a,b)<.072 for a,b in strokes):
                base=(255,218,143)
            else:
                base=ENAMELS[sign-1]
            light=round(14*y-11*x+4*sin(row*.77+col*.41))
            body.extend([max(0,min(255,c+light)) for c in reversed(base)])
            body.append(255)
    return header+body


def seal(sign, *, mounted):
    m=Mesh()
    tint=tuple(c/255 for c in ENAMELS[sign-1])
    enamel=Material(tuple(.26+c*.70 for c in tint),'hvd_brass',(.047,.061,.085))
    z=1.22 if mounted else .05
    y=-.27 if mounted else 0
    m.disc(BASALT,(0,y,z),(0,y,z+.069),.47,sides=8)
    m.disc(BRASS,(0,y,z+.063),(0,y,z+.119),.45,sides=8)
    m.disc(enamel,(0,y,z+.119),(0,y,z+.135),.375,sides=24)
    for a,b in zip(circle(.397),circle(.397)[1:]):
        m.tube(GILT,(a[0],y+a[1],z+.134),(b[0],y+b[1],z+.134),.012,sides=5)
    for path in SEAL_MARKS[sign-1]:
        for a,b in zip(path,path[1:]):
            m.tube(GILT,(a[0]*.522,y+a[1]*.522,z+.147),(b[0]*.522,y+b[1]*.522,z+.147),.021,sides=6)
    return m


def receptacle(m):
    m.disc(TRIM,(0,-.27,1.108),(0,-.27,1.203),.55,sides=12)
    m.disc(DARK,(0,-.27,1.192),(0,-.27,1.218),.454,sides=8)
    for x in (-.49,.49):
        m.box(BRASS,x,-.27,1.186,.083,.24,.146)


def post(shutter=False):
    m=Mesh()
    m.disc(BASALT,(0,0,0),(0,0,.24),.94,sides=8)
    m.tube(MASONRY,(0,0,.22),(0,0,.99),.68,.51,sides=8)
    m.disc(LIMESTONE,(0,0,.91),(0,0,1.13),.78,sides=8)
    receptacle(m)
    if shutter:
        for x in (-.62,.62):
            pillar(m,x,.38,1.89,z=.26,radius=.16)
        m.box(BASALT,0,.45,1.37,1.22,.25,.73)
        for x in (-.51,.51):
            m.box(BRASS,x,.26,1.52,.081,.14,.47)
        return m
    for x in (-.52,.52):
        pillar(m,x,.37,1.30,z=1.11,radius=.13)
    m.tube(BASALT,(-.76,.43,2.47),(.76,.43,2.47),.156,sides=8)
    m.disc(DARK,(0,.47,2.47),(0,.76,2.47),.69,sides=16)
    m.disc(BRASS,(0,.33,2.47),(0,.47,2.47),.67,sides=16)
    m.disc(DARK,(0,.315,2.47),(0,.332,2.47),.565,sides=20)
    m.disc(BRASS,(0,.76,2.47),(0,.82,2.47),.33,sides=12)
    return m


def filter_mark(index):
    if index==1:
        outer=[(-.055+.39*cos(-1.65-i*3.20/20),.39*sin(-1.65-i*3.20/20)) for i in range(21)]
        inner=[(-.055+.27*cos(1.43+i*3.1/20),.39*sin(1.43+i*3.1/20)) for i in range(21)]
        return (tuple(outer+inner+[outer[0]]),)
    if index==2:
        rim=[((.43 if i%2==0 else .143)*cos(i*pi/4),(.43 if i%2==0 else .143)*sin(i*pi/4)) for i in range(8)]
        return (tuple(rim+[rim[0]]),)
    rays=[((.31*cos(a),.31*sin(a)),(.43*cos(a),.43*sin(a))) for a in (tau*i/8 for i in range(8))]
    return (circle(.234,20),*rays)


def cell(index):
    m=Mesh()
    tint=FILTER_COLORS[index-1]
    bright=Material(tint,'hvd_glass',tuple(.54*a for a in tint))
    glass=Material(tuple(.23+a*.30 for a in tint),'hvd_copper',tuple(.12*a for a in tint))
    m.disc(glass,(0,.213,2.47),(0,.318,2.47),.528,sides=24)
    for path in filter_mark(index):
        for a,b in zip(path,path[1:]):
            m.tube(bright,(a[0],.192,2.47+a[1]),(b[0],.192,2.47+b[1]),.026,sides=6)
    angle=pi*(.84-(index-1)*.39)
    x,z=.58*cos(angle),2.47+.58*sin(angle)
    m.tube(GILT,(x*.92,.21,2.47+(z-2.47)*.92),(x*1.15,.21,2.47+(z-2.47)*1.15),.045,sides=7)
    return m


def filter_handle():
    m=Mesh()
    m.box(DARK,0,0,0,.40,.45,.58)
    m.tube(BRASS,(0,0,.42),(0,-.25,.68),.062,sides=8)
    m.disc(GILT,(0,-.255,.64),(0,-.255,.77),.136,sides=8)
    return m


def clamp_bar(opened):
    m=Mesh()
    z=1.96 if opened else 1.55
    m.tube(BRASS,(-.60,.12,z),(.60,.12,z),.072,sides=8)
    m.box(GILT,0,.12,z-.105,.18,.22,.23)
    m.tube(PALE if opened else DARK,(0,-.026,z-.06),(0,-.026,z+.049),.065,sides=8)
    return m


def ignition():
    m=Mesh()
    m.disc(BASALT,(0,0,0),(0,0,.21),.75,sides=8)
    m.box(MASONRY,0,0,.17,.73,.79,1.05)
    m.box(BRASS,0,0,1.09,1.03,.86,.22)
    m.tube(BRASS,(0,-.25,1.30),(0,.14,1.64),.080,sides=8)
    m.tube(GILT,(-.275,.14,1.65),(.275,.14,1.65),.085,sides=8)
    return m


def court_inlay():
    m=Mesh()
    for radius,width in ((2.45,.084),(3.13,.041),(4.32,.062)):
        m.ring(BRASS,radius,width,.031)
    star(m,0,0,.035,1.18,GILT,4)
    for i,(x,y) in enumerate(SOCKETS,1):
        x,y=x-35.0,y-29.6
        m.trace(BRASS,(x,y,.031),(0,0,.031),.085)
        m.trace(GILT,(x,y-2.15,.033),(x,y-1.33,.033),.065)
        for tick in range(i):
            dx=(tick-(i-1)/2)*.26
            m.trace(GILT,(x+dx,y-2.05,.036),(x+dx,y-1.44,.036),.11)
    m.trace(BRASS,(0,0,.032),(0,9.15,.032),.098)
    return m


def ray(slot, index):
    x,y=SOCKETS[slot-1]
    origin=(x-GATE[0],y-GATE[1]+.82,5+2.47-GATE_HEIGHT)
    dest=(0,-.23,4.85)
    tint=FILTER_COLORS[index-1]
    core=Material(tint,'hvd_raylight',tuple(.78*c for c in tint),alpha=.89)
    haze=Material(tint,'hvd_raylight',tuple(.40*c for c in tint),alpha=.29)
    m=Mesh()
    m.tube(core,origin,dest,.046,.08,sides=8,open_ends=True)
    m.tube(haze,origin,dest,.19,.32,sides=8,open_ends=True)
    return m


def zenith_gate():
    m=Mesh()
    daybreak=Material((.60,.78,1.0),'hvd_glass',(.20,.36,.65),alpha=.30)
    inner=Material((.76,.92,1.0),'hvd_glass',(.63,.78,.95),alpha=.87)
    contour=[(2.19*cos(i*pi/32),-.105,3+2.19*sin(i*pi/32)) for i in range(33)]
    contour.extend(((-2.19,-.105,.13),(2.19,-.105,.13)))
    for face in (contour,contour[::-1]):
        m.polygon(daybreak,face,[(x/4.40+.5,z/5.20) for x,_,z in face])
    for y in (-.15,.12):
        arch(m,2.16,3.0,y,.056,.065,inner)
        arch(m,2.28,3.0,y,.065,.067,GILT)
    for i in range(34):
        a=pi*i/33
        pos=(2.11*cos(a),-.19,3+2.11*sin(a))
        m.disc(GILT,pos,(pos[0],.17,pos[2]),.045 if i%4 else .08,sides=7)
    for idx,radius in enumerate((.48,.86,1.18)):
        points=circle(radius,42)
        for a,b in zip(points,points[1:]):
            m.tube(inner if idx==1 else GILT,(a[0],-.25,2.92+a[1]),(b[0],-.25,2.92+b[1]),.023,sides=5)
    for sign in (-1,1):
        rosette(m,sign*2.32,-.27,4.39,.23,inner,8)
    m.ring(GILT,2.09,.090,.043)
    m.ring(inner,1.84,.052,.044)
    return m


def gate_models():
    scenery={
        'hvd_gate_pod': ('Optický sloup s paticí',post),
        'hvd_clamp_pod': ('Závora převodu',lambda:post(True)),
        'hvd_filter_arm': ('Páčka optické clony',filter_handle),
        'hvd_gatepull': ('Spoušť soustavy',ignition),
        'hvd_gateinlay': ('Mosazné vedení pod třemi sloupy',court_inlay),
    }
    visuals={
        'hvd_zenith':('Brána tří paprsků',zenith_gate),
        'hvd_clamp_down':('Spuštěná závora',lambda:clamp_bar(False)),
        'hvd_clamp_up':('Zvednutá závora',lambda:clamp_bar(True)),
    }
    for i in range(1,5):
        visuals[f'hvd_stamp{i}']=('Vložená pečeť',lambda i=i:seal(i,mounted=True))
    for i in range(1,4):
        visuals[f'hvd_lens{i}']=('Clona v okruží',lambda i=i:cell(i))
        for slot in range(1,4):
            visuals[f'hvd_ray{slot}{i}']=('Paprsek optického sloupu',lambda i=i,slot=slot:ray(slot,i))
    return scenery,visuals


def seal_assets():
    # A neutral texture keeps the three rays independent of the tinted glass.
    light_header=pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,4,4,24,0)
    resources={'hvd_raylight.tga':light_header+bytes((252,249,242))*16}
    for face,number in enumerate(SEAL_MODELS,1):
        name=f'it_smlmisc_{number:03d}'
        resources[f'{name}.mdl']=seal(face,mounted=False).mdl(name).replace(b'classification Other',b'classification Item')
        resources[f'i{name}.tga']=seal_icon(face)
    return resources
