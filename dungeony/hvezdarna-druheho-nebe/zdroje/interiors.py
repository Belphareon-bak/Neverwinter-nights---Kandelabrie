"""The original stone floor plans for the observatory's three interiors."""

from math import cos, pi, radians, sin
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, surface
from art import TRIM, Material, Mesh, arch
from flights import as_tile
from plan import ZONES


TILESET = 'hvd_interior'
# Frames share the width of an actual corridor and appear on its walkmesh.
def chamber(code, height, frames):
    zone = ZONES[code]
    return zone.size, zone.rooms, height, frames


PLANS = {
    'hvd_halls': chamber('halls', 3.35,
        ((18,1.55,0,5.7),(18,9,0,5.7),(24,15,90,4.9),
         (48,15,90,4.9),(55.55,38.7,0,4.8),(25.5,45,90,5.6),(1.55,55,90,5.5))),
    'hvd_study': chamber('study', 3.32,
        ((8.5,31,0,5.5),(16.9,45.6,0,5.5),(23,58,0,5.5),(15,158.35,0,5.55))),
    'hvd_dome': chamber('dome', 3.85,
        ((30,1.55,0,5.8),(30,17,0,6),(13.2,26.05,90,5.9),
         (46.8,26.1,90,5.8),(30,46,0,6.4))),
}

FLOOR = Material((.65,.65,.64),'hvd_paving')
WALL = Material((.69,.69,.70),'hvd_ashlar',shadow=1)


def tile_assignments(key):
    return {(x,y):(number,0) for number,(area,x,y) in enumerate(all_cells()) if area==key}


def all_cells():
    yield from ((area,x,y) for area,((width,height),_,_,_) in PLANS.items()
                for y in range(height) for x in range(width))


def grid(size, rooms):
    width,height=size
    xs=sorted(set(range(0,10*width+1,10)) | {edge for x0,_,x1,_ in rooms for edge in (x0,x1)})
    ys=sorted(set(range(0,10*height+1,10)) | {edge for _,y0,_,y1 in rooms for edge in (y0,y1)})
    occupied={}
    for i,(x0,x1) in enumerate(zip(xs,xs[1:])):
        for j,(y0,y1) in enumerate(zip(ys,ys[1:])):
            x=(x0+x1)/2
            y=(y0+y1)/2
            if any(l<x<r and low<y<high for l,low,r,high in rooms):
                occupied[i,j] = (x0,y0,x1,y1)
    return occupied


def masonry(mesh,a,b,height):
    dx,dy=b[0]-a[0],b[1]-a[1]
    width=abs(dx or dy)
    nx,ny=dy/width,-dx/width
    cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
    first=len(mesh.faces[WALL])
    mesh.box(WALL,cx+nx*.255,cy+ny*.255,0,width if dx else .51,
             width if dy else .51,height-.19)
    wall_axis=0 if dx else 1
    for i,(vertices,_) in enumerate(mesh.faces[WALL][first:],first):
        if any(v[2]!=vertices[0][2] for v in vertices[1:]):
            mesh.faces[WALL][i]=(vertices,[(v[wall_axis]*.29,v[2]*.32) for v in vertices])
    for z,t,protrusion,stone in ((0,.38,.14,BASALT),(.38,.12,.085,TRIM),
                                 (height-.22,.22,.11,LIMESTONE)):
        mesh.box(stone,cx+nx*.04,cy+ny*.04,z,width if dx else 2*protrusion,
                 width if dy else 2*protrusion,t)


def frame(mesh,x,y,angle,width,height):
    details=Mesh()
    radius=width*.5-.025
    arch(details,radius,2.25,0,.23,.49,TRIM,masonry=True)
    for sign in (-1,1):
        details.box(BASALT,sign*(radius+.105),0,0,.27,.59,.28)
        details.box(LIMESTONE,sign*(radius+.115),0,2.10,.31,.65,.15)
    a=radians(angle)
    for material,polygons in details.faces.items():
        for verts,uv in polygons:
            mesh.polygon(material,[(x+u*cos(a)-v*sin(a),y+u*sin(a)+v*cos(a),
                                    z if z <= 2.25 else 2.25 + (z-2.25)*(height-2.25)/(radius+.23))
                                   for u,v,z in verts],uv)


def chamber_tile(tx,ty,occupied,height,frames,size):
    mesh=Mesh()
    vertices=[]
    index={}
    faces=[]
    materials=[]
    room_cells=[]
    cx,cy=10*tx+5,10*ty+5

    def quad(corners,material):
        indices=[]
        for point in corners:
            rounded=tuple(round(v,4) for v in point)
            if rounded not in index:
                index[rounded]=len(vertices)
                vertices.append(rounded)
            indices.append(index[rounded])
        a,b,c,d=indices
        faces.extend(((a,b,c),(a,c,d)))
        materials.extend((material,material))

    for (i,j),(x0,y0,x1,y1) in occupied.items():
        if not (10*tx <= x0 < 10*(tx+1) and 10*ty <= y0 < 10*(ty+1)):
            continue
        x0,y0,x1,y1=x0-cx,y0-cy,x1-cx,y1-cy
        room_cells.append((x0,y0,x1,y1))
        surface(mesh,FLOOR,x0,y0,x1,y1,0,.30)
        corners=((x0,y0),(x1,y0),(x1,y1),(x0,y1))
        quad([(*p,0) for p in corners],4)
        for k,adjacent in enumerate(((i,j-1),(i+1,j),(i,j+1),(i-1,j))):
            if adjacent in occupied:
                continue
            a,b=corners[k],corners[(k+1)%4]
            w,h=size
            on_set_edge = ((a[0]==b[0] and a[0]+cx in (0,10*w))
                           or (a[1]==b[1] and a[1]+cy in (0,10*h)))
            if on_set_edge:
                continue
            masonry(mesh,a,b,height)
            quad(((*b,0),(*a,0),(*a,height),(*b,height)),2)
    for x,y,angle,width in frames:
        if int(x//10)==tx and int(y//10)==ty:
            frame(mesh,x-cx,y-cy,angle,width,height)
    if not room_cells:
        quad(((-5,-5,-10),(5,-5,-10),(5,5,-10),(-5,5,-10)),7)
    return mesh,(vertices,faces,materials),room_cells


def minimap(cells):
    size=64
    pixels=bytearray()
    for j in range(size):
        y=(j+.5)*10/size-5
        for i in range(size):
            x=(i+.5)*10/size-5
            filled=any(l<=x<r and low<=y<high for l,low,r,high in cells)
            pixels.extend((109,112,139) if filled else (2,3,5))
    return pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,24,0)+pixels


def tileset(game):
    original=game.read('tni02','set').decode('latin-1')
    header=original[original.index('[GENERAL]'):original.index('[TILES]')]
    header=header.replace('Name=tni02','Name='+TILESET).replace('UnlocalizedName=TNO: Castle Interior',
                                                              'UnlocalizedName=Observatory interiors')
    indices=list(all_cells())
    settings=[header,f'[TILES]\r\nCount={len(indices)}\r\n']
    occupied={area:grid(size,rooms) for area,(size,rooms,_,_) in PLANS.items()}
    resources={}
    for i,(area,x,y) in enumerate(indices):
        name=f'hvd_i{i:02d}'
        size,_,height,frames=PLANS[area]
        model,wok,cells=chamber_tile(x,y,occupied[area],height,frames,size)
        resources.update(as_tile(name,model,wok))
        if area == 'hvd_halls' and (x, y) == (6, 2):
            cells = [(l,b,min(r,-.8),t) for l,b,r,t in cells if l < -.8]
        resources[f'mi_{name}.tga']=minimap(cells)
        corners=''.join(f'{corner}=stone\r\n{corner}Height=0\r\n' for corner in (
            'TopLeft','TopRight','BottomLeft','BottomRight'))
        settings.append(f'\r\n[TILE{i}]\r\nModel={name}\r\nWalkMesh=msb01\r\n'+corners
                        +'Top=\r\nRight=\r\nBottom=\r\nLeft=\r\nDoors=0\r\nSounds=0\r\n'
                        +'MainLight1=1\r\nMainLight2=1\r\nSourceLight1=1\r\nSourceLight2=1\r\n'
                        +'AnimLoop1=1\r\nAnimLoop2=1\r\nAnimLoop3=1\r\nPathNode=F\r\nOrientation=0\r\n'
                        +f'ImageMap2D=mi_{name}\r\nVisibilityNode=A\r\nVisibilityOrientation=0\r\n')
    settings.append('\r\n[GROUPS]\r\nCount=0\r\n')
    resources[f'{TILESET}.set']=''.join(settings).encode('latin-1')
    return resources
