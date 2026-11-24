"""The Last Step's Doric temple, open to the sky above the processional aisle."""

from math import cos, sin, tau

from architecture import INDIGO, LIMESTONE, MASONRY, WARM
from art import BRASS, DARK, GILT, TRIM, Material, Mesh
from plan import TEMPLE_EAVES, TEMPLE_FACE, TEMPLE_FRONT, TEMPLE_ORIGIN, TEMPLE_REAR


PLINTH_WIDTH = 1.80
CAPITAL = 5.62
EAVE = 7.02
RIDGE = 10.57
MARBLE = Material((.98,.94,.84),"hvd_stone",shadow=1)
ROOF_TILE = Material((.75,.62,.48),"hvd_copper",shadow=1)


def doric_column():
    mesh = Mesh()
    for z,width,height,stone in ((0,PLINTH_WIDTH,.16,MASONRY),(.16,1.64,.19,LIMESTONE)):
        mesh.box(stone,0,0,z,width,width,height,tile_uv=.38)
    mesh.tube(TRIM,(0,0,.35),(0,0,.48),.75,.70,sides=24)

    # Flutes are cut into the shaft profile. The lower third has gentle entasis.
    profiles = ((.46,.71),(1.67,.716),(3.37,.645),(4.98,.566),(5.15,.56))
    flute = (1,.925,.865,.925)
    samples = 20*len(flute)
    rings = [
        [(radius*flute[i%4]*cos(i*tau/samples),radius*flute[i%4]*sin(i*tau/samples),z)
         for i in range(samples)]
        for z,radius in profiles
    ]
    for lower,upper in zip(rings,rings[1:]):
        for i in range(samples):
            j=(i+1)%samples
            mesh.polygon(MARBLE,(lower[i],lower[j],upper[j],upper[i]))

    mesh.disc(TRIM,(0,0,5.135),(0,0,5.239),.629,sides=24)
    mesh.tube(MARBLE,(0,0,5.22),(0,0,5.44),.62,.795,sides=24)
    mesh.box(LIMESTONE,0,0,5.43,1.67,1.67,CAPITAL-5.43,tile_uv=.38)
    return mesh


def entablature(mesh, cx, cy, length, along_x, divisions):
    def course(stone, along, out, z, span, depth, height):
        a,b = (cx+along,cy+out) if along_x else (cx+out,cy+along)
        mesh.box(stone,a,b,z,span if along_x else depth,depth if along_x else span,
                 height,tile_uv=.38)

    course(MARBLE,0,0,CAPITAL,length,1.76,.52)
    course(TRIM,0,0,6.14,length,1.91,.092)
    course(INDIGO,0,0,6.232,length,1.70,.495)
    course(LIMESTONE,0,0,6.727,length+.06,1.98,.236)
    course(BRASS,0,0,6.963,length+.06,2.03,.058)
    bay=length/divisions
    for i in range(divisions):
        x=-length/2+bay*(i+.5)
        for sign in (-1,1):
            course(MARBLE,x,sign*.87,6.274,bay*.34,.14,.42)
            for flute in (-.195,0,.195):
                course(TRIM,x+flute,sign*.963,6.289,.066,.072,.382)
            if i < divisions-1:
                course(GILT,x+bay*.5,sign*.884,6.426,.228,.058,.125)


def pediment(mesh, y, facing, half):
    def triangle(stone, width, bottom, top, plane):
        corners=((-width,plane,bottom),(width,plane,bottom),(0,plane,top))
        mesh.polygon(stone,corners if facing<0 else corners[::-1])

    triangle(MARBLE,half,EAVE,RIDGE,y)
    triangle(INDIGO,half-.78,EAVE+.115,RIDGE-.36,y+.031*facing)
    for side in (-1,1):
        a=(side*half,y,EAVE+.055)
        b=(0,y,RIDGE+.067)
        mesh.tube(LIMESTONE,a,b,.222,sides=8)
        mesh.tube(GILT,(a[0],y+.25*facing,a[2]),(b[0],y+.25*facing,b[2]),.058,sides=7)

    # The observatory's star occupies the tympanum above the central bay.
    z=EAVE+1.37
    mesh.disc(TRIM,(0,y,z),(0,y+.115*facing,z),.89,sides=24)
    mesh.disc(DARK,(0,y+.112*facing,z),(0,y+.143*facing,z),.737,sides=24)
    plane=y+.151*facing
    vertices=[(r*cos(i*tau/16),plane,z+r*sin(i*tau/16))
              for i in range(16) for r in (.696 if i%2==0 else .278,)]
    for i in range(16):
        corners=((0,plane,z),vertices[i],vertices[(i+1)%16])
        mesh.polygon(GILT,corners if facing<0 else corners[::-1])
    for side in (-1,1):
        for x, height in ((2.16,.86),(3.53,.68),(5.07,.53),(6.85,.38)):
            mesh.disc(BRASS,(side*x,y,EAVE+height),(side*x,y+.093*facing,EAVE+height),
                      min(.23,height*.48),sides=12)


def temple_canopy():
    mesh=Mesh()
    ox,oy=TEMPLE_ORIGIN
    west,front,east,rear=TEMPLE_EAVES
    half=(east-west)/2
    south,north=front-oy,rear-oy
    for world_y in (TEMPLE_FRONT,TEMPLE_REAR):
        entablature(mesh,0,world_y-oy,half*2-.36,True,12)
    for world_x in (TEMPLE_FACE[0],TEMPLE_FACE[-1]):
        entablature(mesh,world_x-ox,0,TEMPLE_REAR-TEMPLE_FRONT-1.26,False,6)

    def roof_height(x):
        return RIDGE-(RIDGE-EAVE)*abs(x)/half

    # Full end roofs and narrow covered side galleries frame an open central court.
    spans=((south,south+3.0,0),(north-2.56,north,0),(south+3.0,north-2.56,11.08))
    for y0,y1,indent in spans:
        for side in (-1,1):
            x0,x1=sorted((side*indent,side*half))
            quad=((x0,y0,roof_height(x0)),(x1,y0,roof_height(x1)),
                  (x1,y1,roof_height(x1)),(x0,y1,roof_height(x0)))
            uv=tuple((x*.37,y*.39) for x,y,_ in quad)
            mesh.polygon(ROOF_TILE,quad,uv)
            mesh.polygon(MASONRY,quad[::-1],uv[::-1])
            for i in range(1,round((y1-y0)/.40)):
                y=y0+.40*i
                if y>=y1-.08:
                    break
                mesh.tube(TRIM,(x0,y,roof_height(x0)+.046),(x1,y,roof_height(x1)+.046),
                          .047,sides=5)
            if indent:
                x=side*indent
                mesh.tube(MARBLE,(x,y0,roof_height(x)),(x,y1,roof_height(x)),.14,sides=6)
    for side in (-1,1):
        x=side*half
        mesh.tube(LIMESTONE,(x,south,EAVE),(x,north,EAVE),.159,sides=8)
    pediment(mesh,south,-1,half)
    pediment(mesh,north,1,half)
    return mesh


SCENERY = {
    'hvd_doric': ('Kanelovaný dórský sloup',doric_column),
    'hvd_temple': ('Průčelí a střecha Chrámu posledního stupně',temple_canopy),
}
