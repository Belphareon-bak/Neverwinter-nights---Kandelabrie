"""Stonework and optical instruments for the restoration of the watch light."""

from math import atan2, cos, degrees, sin, tau
from random import Random

from architecture import BASALT, LIMESTONE, MASONRY
from art import BRASS, GILT, TRIM, Material, Mesh
from navrh_v21 import (B, BEAM_HEIGHT as HEIGHT, BLUE_TO_MIX, FEED_RAY, G, IRIS,
                       OPTICAL_SLOT, OPTICS, OUTLET, OUTLET_PANEL, PILOT, PILOT_IRIS, PILOT_STAR, R, RED_TO_MIX,
                       RUBBLE, RUBBLE_BLOCKS, SOURCE, SOURCE_LIP, WHITE, WHITE_TO_RUBBLE, BLUE_TO_RUBBLE)


LIGHT_TONES = {
    R: (1, .18, .18), G: (.24, 1, .42), B: (.28, .62, 1),
    R | G: (1, .91, .29), R | B: (.98, .36, 1), G | B: (.27, .94, 1),
    WHITE: (1, .95, .72),
}
CRYSTAL = Material((.82,.94,1),"hvd_glass",(.26,.39,.51))
DEBRIS = Material((.71,.67,.62),"hvd_rough",shadow=1)
IRON = Material((.24,.24,.26),"hvd_brass")
DAY = Material((1,.86,.53),"hvd_raylight",(.98,.69,.25),alpha=.28)


def glowing(color, alpha=.97):
    rgb=LIGHT_TONES[color]
    return Material(rgb, "hvd_raylight", rgb, alpha=alpha)


def beam(mesh, a, b, color, radius=.055):
    mesh.tube(glowing(color),a,b,radius,radius*.83,sides=9,open_ends=True)
    mesh.tube(glowing(color,.24),a,b,radius*2.1,radius*1.6,sides=9,open_ends=True)


def ray_mesh(origin, rays, color=0, *, sealed=False):
    mesh=Mesh()
    ox,oy=origin
    for spectrum,path in rays:
        if sealed:
            path=path[:-1]+(IRIS,)
        hue=spectrum or color
        for (x,y),(u,v) in zip(path,path[1:]):
            beam(mesh,(x-ox,y-oy,HEIGHT),(u-ox,v-oy,HEIGHT),hue,
                 .071 if hue not in (R,G,B) else .058)
        x,y=path[-1]
        u,v=path[-2]
        length=((x-u)**2+(y-v)**2)**.5
        end=(x-ox,y-oy,HEIGHT)
        just_before=(end[0]-.045*(x-u)/length,end[1]-.045*(y-v)/length,HEIGHT)
        mesh.disc(glowing(hue),just_before,end,.085,sides=9)
    return mesh


def heading(aim):
    _,path = aim.rays[-1] if aim.mode==4 else aim.rays[0]
    (x,y),(u,v)=path[:2]
    # Aurora reports a placeable's facing in whole degrees.
    return float(round(degrees(atan2(v-y,u-x))) % 360)


def stand():
    mesh=Mesh()
    mesh.disc(BASALT,(0,0,0),(0,0,.24),.53,sides=10)
    mesh.tube(MASONRY,(0,0,.24),(0,0,1.31),.36,.28,sides=10)
    mesh.disc(TRIM,(0,0,1.29),(0,0,1.42),.40,sides=12)
    for side in (-1,1):
        mesh.tube(BRASS,(0,side*.29,1.37),(0,side*.39,HEIGHT-.13),.077,sides=8)
    mesh.tube(IRON,(0,0,1.42),(-.37,0,1.27),.062,sides=8)
    mesh.disc(GILT,(-.43,0,1.27),(-.35,0,1.27),.095,sides=10)
    return mesh


def optic_head(index):
    mesh=Mesh()
    depth=.115 if index in (3,7) else .064
    mesh.disc(BRASS,(-depth,0,HEIGHT),(depth,0,HEIGHT),.435,sides=20)
    mesh.disc(CRYSTAL,(depth,0,HEIGHT),(depth+.047,0,HEIGHT),.345,sides=20)
    mesh.disc(TRIM,(-depth-.04,0,HEIGHT),(-depth,0,HEIGHT),.371,sides=20)
    mesh.tube(GILT,(.10,0,HEIGHT+.39),(.61,0,HEIGHT+.39),.036,.084,sides=7)
    if index in (3,4,5,6,7,8,9):
        marks = {3:(R,G,B),4:(R,),5:(G,),6:(B,),7:(R,G,B),8:(G,),9:(R|B,)}[index]
        for i,hue in enumerate(marks):
            y=(i-(len(marks)-1)*.5)*.17
            mesh.disc(glowing(hue,1.0),(.17,y,HEIGHT),(.21,y,HEIGHT),.071,sides=8)
    return mesh


def solar_receiver():
    mesh=Mesh()
    mesh.disc(BASALT,(0,0,0),(0,0,.24),.74,sides=12)
    mesh.tube(MASONRY,(0,0,.24),(0,0,1.98),.51,.49,sides=12)
    mesh.disc(BRASS,(0,0,1.98),(0,0,2.18),.71,sides=20)
    mesh.tube(TRIM,(0,0,2.18),(0,0,HEIGHT),.52,.63,sides=16)
    mesh.disc(CRYSTAL,(0,0,HEIGHT),(0,0,HEIGHT+.10),.49,sides=20)
    mesh.disc(BRASS,(-.67,0,HEIGHT),(-.43,0,HEIGHT),.27,sides=14)
    mesh.disc(glowing(WHITE,1.0),(-SOURCE_LIP,0,HEIGHT),(-.67,0,HEIGHT),.208,sides=14)
    return mesh


def lightwell():
    mesh=Mesh()
    for i in range(12):
        a,b=tau*i/12,tau*(i+1)/12
        def p(angle,radius,z):
            return radius*cos(angle),radius*sin(angle),z
        lo,hi=3.78,7.1
        mesh.polygon(MASONRY,(p(a,1.37,lo),p(a,1.24,hi),p(b,1.24,hi),p(b,1.37,lo)))
        mesh.polygon(MASONRY,(p(a,1.94,lo),p(b,1.86,hi),p(a,1.86,hi)))
        mesh.polygon(MASONRY,(p(a,1.94,lo),p(b,1.94,lo),p(b,1.86,hi)))
        for z in (3.78,7.1):
            outer=1.94 if z < 4 else 1.86
            inner=1.37 if z < 4 else 1.24
            mesh.polygon(LIMESTONE,(p(a,inner,z),p(a,outer,z),p(b,outer,z),p(b,inner,z)))
        mesh.tube(TRIM,p(a,1.53,3.82),p(b,1.53,3.82),.115,sides=6)
        mesh.tube(LIMESTONE,p(a,1.58,7.14),p(b,1.58,7.14),.163,sides=7)
        mesh.tube(BRASS,p(a,1.28,7.23),p(b,1.28,7.23),.05,sides=7)
    # The exterior crown is open. The daylight enters above it from the cliff side.
    mesh.disc(CRYSTAL,(0,0,7.10),(0,0,7.20),.86,sides=30)
    mesh.box(MASONRY,1.66,0,3.63,1.18,2.39,.41,tile_uv=.31)
    mesh.box(LIMESTONE,1.57,0,3.96,1.37,2.91,.17,tile_uv=.31)
    # This strip rests on the east wall and the two stone piers below the shaft.
    mesh.box(MASONRY,1.64,0,4.02,.64,5.01,.29,tile_uv=.30)
    mesh.box(LIMESTONE,1.54,0,4.29,.81,5.02,.13,tile_uv=.31)
    for side in (-1,1):
        mesh.box(BASALT,1.67,side*.94,0,.52,.58,.27,tile_uv=.37)
        mesh.box(MASONRY,1.67,side*.94,.27,.44,.51,3.39,tile_uv=.30)
        mesh.box(LIMESTONE,1.65,side*.94,3.5,.57,.64,.26,tile_uv=.34)
    return mesh


def sunlight():
    mesh=Mesh()
    # An oblique sunbeam from the exposed exterior strikes the roof lens.
    # A second beam drops from that same lens down the open stone shaft.
    crown=(0,0,7.23)
    for a,b,radius in (((3.42,1.88,12.1),crown,.155),(crown,(0,0,HEIGHT+.11),.205)):
        beam(mesh,a,b,WHITE,radius)
        mesh.tube(DAY,a,b,radius*3,radius*1.7,sides=10,open_ends=True)
    return mesh


def conduit():
    mesh=Mesh()
    # Mounted into the west wall. The luminous line ends at its glass mouth.
    mesh.box(BASALT,-.40,0,HEIGHT-.66,.81,1.81,1.31,tile_uv=.40)
    mesh.disc(BRASS,(-.10,0,HEIGHT),(.18,0,HEIGHT),.56,sides=21)
    mesh.disc(CRYSTAL,(.15,0,HEIGHT),(.20,0,HEIGHT),.40,sides=21)
    return mesh


def iris(opened):
    mesh=Mesh()
    for i in range(12):
        a,b=tau*i/12,tau*(i+1)/12
        inner=.40 if opened else .025
        points=tuple((0,r*cos(t),HEIGHT+r*sin(t)) for r,t in ((.54,a),(.54,b),(inner,b),(inner,a)))
        mesh.polygon(TRIM if opened or i%2 else IRON,points)
        mesh.polygon(TRIM if opened or i%2 else IRON,points[::-1])
    if not opened:
        mesh.disc(IRON,(-.035,0,HEIGHT),(0,0,HEIGHT),.12,sides=12)
    mesh.disc(BRASS,(-.11,0,HEIGHT+.64),(.113,0,HEIGHT+.64),.125,sides=12)
    mesh.disc(glowing(G if opened else R,1.0),(.106,0,HEIGHT+.64),(.131,0,HEIGHT+.64),.084,sides=12)
    mesh.disc(glowing(G if opened else R,1.0),(-.131,0,HEIGHT+.64),(-.106,0,HEIGHT+.64),.084,sides=12)
    return mesh


def iris_stand():
    mesh=Mesh()
    mesh.disc(BASALT,(0,0,0),(0,0,.23),.49,sides=10)
    mesh.tube(MASONRY,(0,0,.22),(0,0,HEIGHT-.52),.33,.26,sides=10)
    for i in range(16):
        a,b=tau*i/16,tau*(i+1)/16
        p=(0,.57*cos(a),HEIGHT+.57*sin(a))
        q=(0,.57*cos(b),HEIGHT+.57*sin(b))
        mesh.tube(BRASS,p,q,.075,sides=7)
    for x,y in (PILOT_IRIS,PILOT_STAR):
        for side in (-.06,.06):
            mesh.tube(GILT,(side,.04,.055),(x-IRIS[0]+side,y-IRIS[1],.055),.021,sides=6)
    return mesh


def pilot_emblem(mesh, route, origin, horizontal, material, radius):
    count=20 if route==1 else 10
    x,y,z=origin
    for index in range(count):
        corners=[]
        for vertex in (index, index+1):
            angle=tau*vertex/count
            r=radius if route==1 or vertex%2==0 else radius*.45
            corners.append((x+horizontal[0]*r*cos(angle),y+horizontal[1]*r*cos(angle),z+r*sin(angle)))
        mesh.polygon(material,(origin,*corners))
        mesh.polygon(material,(origin,*corners[::-1]))


def pilot_receiver(route):
    mesh=Mesh()
    mesh.disc(BASALT,(0,0,0),(0,0,.19),.32,sides=9)
    mesh.tube(MASONRY,(0,0,.19),(0,0,HEIGHT-.16),.126,.10,sides=8)
    mesh.box(BRASS,0,0,HEIGHT-.29,.58,.21,.58)
    mesh.box(TRIM,0,0,HEIGHT-.235,.47,.23,.47)
    green_glass=Material((.18,.61,.39),'hvd_glass',(.10,.34,.18))
    mesh.box(green_glass,0,0,HEIGHT-.195,.39,.26,.39)
    for face in (-.137,.137):
        pilot_emblem(mesh,route,(0,face,HEIGHT),(1,0),GILT,.155)
    return mesh


def slot():
    mesh=Mesh()
    for side in (-1,1):
        mesh.box(BRASS,0,side*.455,HEIGHT-.35,1.52,.085,.70)
        mesh.box(TRIM,0,0,HEIGHT+side*.35,1.52,1.0,.085)
    return mesh


def stop():
    mesh=Mesh()
    mesh.disc(BASALT,(0,0,0),(0,0,.13),.21,sides=9)
    mesh.tube(BRASS,(0,0,.13),(0,0,HEIGHT-.08),.063,sides=8)
    mesh.disc(BRASS,(0,-.04,HEIGHT),(0,.044,HEIGHT),.25,sides=12)
    mesh.disc(CRYSTAL,(0,-.075,HEIGHT),(0,.071,HEIGHT),.19,sides=12)
    return mesh


def passive():
    mesh=stop()
    mesh.disc(CRYSTAL,(0,-.09,HEIGHT),(0,.090,HEIGHT),.204,sides=14)
    return mesh


def rubble_origin(poly):
    return tuple(sum(p[i] for p in poly)/len(poly) for i in range(2))


def collapsed(poly):
    mesh=Mesh()
    rng=Random(794)
    ox,oy=rubble_origin(poly)
    ring=[(x-ox,y-oy) for x,y in poly]
    heights=[rng.uniform(.7,2.4) for _ in ring]
    peak=(.1,-.24,2.55)
    for i,((x,y),(u,v)) in enumerate(zip(ring,ring[1:]+ring[:1])):
        top=(x*.83,y*.85,heights[i])
        neighbor=(u*.83,v*.85,heights[(i+1)%len(ring)])
        mesh.polygon(DEBRIS,((x,y,0),(u,v,0),neighbor,top))
        mesh.polygon(MASONRY,(top,neighbor,peak))
    for i,(x,y) in enumerate(ring):
        x,y=x*.70,y*.74
        size=rng.uniform(.3,.72)
        base=[(x+cos(j*tau/6+i)*size,y+sin(j*tau/6+i)*size,.0) for j in range(6)]
        top=(x-.082,y+.11,rng.uniform(.34,1.12))
        for a,b in zip(base,base[1:]+base[:1]):
            mesh.polygon(DEBRIS,(a,b,top))
    mesh.tube(BRASS,(-1.12,-.49,1.6),(.42,-1.02,.36),.085,sides=7)
    mesh.tube(IRON,(.54,-1.10,.30),(1.31,-1.32,.15),.087,sides=7)
    # A snapped facing block interrupts the beam at the height of its old duct.
    west = poly == RUBBLE[0]
    left,bottom,right,top,height=RUBBLE_BLOCKS[0 if west else 1]
    mesh.box(DEBRIS,(left+right)*.5-ox,(bottom+top)*.5-oy,0,right-left,top-bottom,height,tile_uv=.36)
    x,y = WHITE_TO_RUBBLE[-1] if west else BLUE_TO_RUBBLE[-1]
    x,y = x-ox,y-oy
    if west:
        mesh.box(MASONRY,x-.48,y,.63,.55,1.18,.73,tile_uv=.33)
    else:
        mesh.box(MASONRY,x+.16,y+.45,.42,1.34,.51,.88,tile_uv=.33)
    return mesh


def glyphs(*, quiet=False):
    mesh=Mesh()
    mesh.box(MASONRY,0,0,1.08,.18,2.52,1.55,tile_uv=.40)
    for index,(hue,sides) in enumerate(((R,3),(B,16),(R|B,6),(G,4))):
        y=-.85+index*.56
        mesh.disc(GILT,(.095,y,1.99),(.142,y,1.99),.235,sides=sides)
        tint = Material(LIGHT_TONES[hue],"hvd_glass") if quiet else glowing(hue,1)
        mesh.disc(tint,(.145,y,1.99),(.172,y,1.99),.155,sides=sides)
    return mesh


def outlet_board():
    mesh=glyphs(quiet=True)
    mesh.box(BASALT,.055,0,2.49,.25,1.19,.50,tile_uv=.32)
    mesh.disc(BRASS,(.15,0,2.73),(.198,0,2.73),.214,sides=16)
    mesh.disc(IRON,(.194,0,2.73),(.208,0,2.73),.172,sides=16)
    return mesh


def board_emblem(route):
    mesh=Mesh()
    pilot_emblem(mesh,route,(.212,0,2.73),(0,1),glowing(R|G,.94),.153)
    return mesh


def board_signal(hue, position, sides):
    mesh=Mesh()
    mesh.disc(glowing(hue,1),(.171,position,1.99),(.20,position,1.99),.159,sides=sides)
    mesh.disc(glowing(hue,.38),(.199,position,1.99),(.205,position,1.99),.209,sides=sides)
    return mesh


def ward_glow(color=R|B):
    mesh=Mesh()
    mesh.disc(glowing(color),(0,0,1.93),(0,0,2.21),.245,sides=15)
    mesh.tube(glowing(color,.22),(0,0,2.07),(0,0,3.37),.29,.085,sides=10)
    return mesh


FREE_ENDPOINTS = {optic.center for optic in OPTICS} | {WHITE_TO_RUBBLE[-1], BLUE_TO_RUBBLE[-1], OUTLET, PILOT_IRIS, PILOT_STAR}
ENDPOINTS = {path[-1]: path[-2] for optic in OPTICS for choice in optic.aims
             for _,path in choice.rays if path[-1] not in FREE_ENDPOINTS}

SCENERY = {
    'hvd_sunstand': ('Ložisko natáčecí optiky',stand),
    'hvd_suncatch': ('Pevný přijímač denního světla',solar_receiver),
    'hvd_sunshaft': ('Otevřený skalní světlík se sběrnou čočkou',lightwell),
    'hvd_daylight': ('Denní světlo ze šachty',sunlight),
    'hvd_sun_feed': ('Paprsek z přijímače denního světla',lambda: ray_mesh(SOURCE,((WHITE,FEED_RAY),))),
    'hvd_sunout': ('Ústí světlovodu k lucerně',conduit),
    'hvd_irisstand': ('Kamenná patka výstupní clony',iris_stand),
    'hvd_green_eye': ('Čidlo pojistky · Slunce',lambda: pilot_receiver(1)),
    'hvd_green_star': ('Čidlo pojistky · Hvězda',lambda: pilot_receiver(2)),
    'hvd_outlet_board': ('Tabulka u světlovodu',outlet_board),
    'hvd_sunslot': ('Mosazný průzor v příčce',slot),
    'hvd_teststop': ('Plocha pro zkušební odraz',stop),
    'hvd_fixedoptic': ('Pevný odrazný hranol',passive),
    'hvd_sunglyph': ('Rytina barevných kanálů',glyphs),
    **{f'hvd_collapse{i}': ('Rozlomený blok po sesuvu',lambda shape=shape: collapsed(shape))
       for i,shape in enumerate(RUBBLE)},
}
VISUALS = {
    'hvd_iris_closed': ('Zavřená výstupní clona',lambda: iris(False)),
    'hvd_iris_open': ('Otevřená výstupní clona',lambda: iris(True)),
    'hvd_board_sun': ('Zapojeno · Slunce',lambda: board_emblem(1)),
    'hvd_board_star': ('Zapojeno · Hvězda',lambda: board_emblem(2)),
    'hvd_board_green': ('Zelená kontrolka clony',lambda: board_signal(G,.83,4)),
    'hvd_board_purp': ('Purpurová kontrolka světlovodu',lambda: board_signal(R|B,.27,6)),
    'hvd_wardglow': ('Světlo ochrany horské stezky',ward_glow),
    **{f'hvd_rm{index}': (optic.label,lambda index=index: optic_head(index))
       for index,optic in enumerate(OPTICS,1)},
    **{f'hvd_rp{index}{mark}{suffix}': (choice.title,
          lambda position=optic.center, rays=choice.rays, hue=hue: ray_mesh(position,rays,hue))
       for index,optic in enumerate(OPTICS,1)
       for mark,choice in enumerate(optic.aims)
       for suffix,hue in (tuple((str(n),n) for n in LIGHT_TONES) if index in (7,9) else (('',0),))},
    **{f'hvd_rq{color}': ('Odraz do zavřené clony',
          lambda color=color: ray_mesh(OPTICS[8].center,OPTICS[8].aims[2].rays,color,sealed=True))
       for color in LIGHT_TONES},
}


def furnish(area):
    def prop(asset, name, point, **settings):
        area.prop(area.art[asset],name,*point,**settings)

    # CreateObject treats a facing of 90 as the model's authored bearing of zero.
    area.point('hvd_sun_iris',*IRIS,90)
    area.point('hvd_outlet_panel',*OUTLET_PANEL,90)
    prop('hvd_suncatch','Pevný přijímač denního světla',SOURCE,action='read',
         text='Světlo přichází sběrnou čočkou v otevřeném skalním světlíku. Pevné ložisko vede paprsek k Z1.')
    prop('hvd_sunshaft','Skalní světlík Filtrovny',SOURCE)
    prop('hvd_daylight','Sluneční paprsky ve světlíku',SOURCE)
    prop('hvd_sun_feed','Stálý paprsek do přívodního zrcadla Z1',SOURCE,tag='hvd_sun_feed')
    prop('hvd_sunout','Světlovod ochranné lucerny',OUTLET,action='repair_outlet',tag='hvd_repair_outlet')
    prop('hvd_irisstand','Kamenná patka výstupní clony',IRIS)
    for asset, label, sensor in (('hvd_green_eye','Slunce',PILOT_IRIS),('hvd_green_star','Hvězda',PILOT_STAR)):
        bearing=degrees(atan2(PILOT[1]-sensor[1],PILOT[0]-sensor[0]))-90
        prop(asset,'Čidlo výstupní clony · '+label,sensor,bearing=bearing)
    prop('hvd_sunslot','Průzor z Filtrovny do Sálu skládání',OPTICAL_SLOT)
    prop('hvd_outlet_board','Tabulka u světlovodu',OUTLET_PANEL,action='repair_outlet',tag='hvd_optic_board',
         text='Trojúhelník a kruh dávají purpurovou. Horní znak určuje aktivní čidlo zelené pojistky.')
    for index,shape in enumerate(RUBBLE):
        prop(f'hvd_collapse{index}','Rozbitý průzor a sesuté zdivo',rubble_origin(shape))
    for (x,y),(px,py) in sorted(ENDPOINTS.items()):
        facing=degrees(atan2(py-y,px-x))-90
        prop('hvd_teststop','Destička pro kontrolní odraz',(x,y),bearing=facing)
    for point in (RED_TO_MIX[1],BLUE_TO_MIX[1]):
        prop('hvd_fixedoptic','Pevný hranol na obchvatu',point)
    for index,optic in enumerate(OPTICS,1):
        active={'mode'+str(mark):choice.mode for mark,choice in enumerate(optic.aims)}
        labels={'aim'+str(mark):choice.title for mark,choice in enumerate(optic.aims)}
        angles={'angle'+str(mark):heading(choice) for mark,choice in enumerate(optic.aims)}
        area.point(f'hvd_rep_m{index}',*optic.center,90,initial=optic.initial,**active,**labels,**angles)
        # Face the use nodes along the free side of the pedestal.
        x,y=optic.center
        dx,dy=optic.approach[0]-x,optic.approach[1]-y
        bearing=degrees(atan2(dy,dx))
        prop('hvd_sunstand',optic.label,optic.center,tag=f'hvd_rep_ctl{index}',
             action='repair_turn',mirror=index,bearing=bearing)
