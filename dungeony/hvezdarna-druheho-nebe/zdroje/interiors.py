"""The original stone floor plans for the observatory's three interiors."""

from math import cos, pi, radians, sin
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, surface
from art import TRIM, Material, Mesh, arch
from flights import as_tile


TILESET = 'hvd_interior'
# World-space footprints. Touching rectangles share the open width of their common edge.
HALLS = (
    (8,9,24,23), (15.2,6.5,20.35,9), (13,23,17.8,39.5), (24,12.55,48,17.45),
    (48,10.5,64.2,38.7), (53.1,38.7,58,44.5), (7,39.5,25.5,55.6),
    (3.2,42.7,7,47.1), (20.45,55.6,25.35,60.8),
)
DOME = (
    (13.2,21.8,46.8,42.2), (18.3,17,41.7,21.8), (18.3,42.2,41.7,46),
    (27,12.2,33,17), (8.2,23.1,13.2,29), (46.8,23.2,52.9,29), (26.8,46,33.2,51),
    (38.3,12.25,50.4,17),
)
STUDY = (
    (3.15,8.2,15.1,21.0), (6.6,3.1,10.35,8.2), (15.1,16.1,19.25,21.0),
    (15.25,21.0,19.25,25.0),
)

# Frames are part of the tile model and share the jambs of a real opening.
# Each row is center, angle and clear opening.
PLANS = {
    'hvd_halls': ((7,7), HALLS, 3.35,
                  ((17.775,9,0,5.15),(15.4,23,0,4.8),(24,15,90,4.9),
                   (48,15,90,4.9),(15.4,39.5,0,4.8),(7,44.9,90,4.4),(55.55,38.7,0,4.9))),
    'hvd_dome': ((6,6), DOME, 3.85,
                 ((30,17,0,6),(13.2,26.05,90,5.9),(46.8,26.1,90,5.8),
                  (30,46,0,6.4))),
    'hvd_study': ((2,3), STUDY, 3.13,
                  ((8.475,8.2,0,3.75),(15.1,18.55,90,4.90))),
}

ENDS = {
    'hvd_halls': ((17.775,6.57,180,3.85),(3.27,44.9,90,3.58),(55.55,44.43,0,3.85)),
    'hvd_dome': ((30,12.27,180,4.2),(8.27,26.05,90,4.15),(52.83,26.1,270,4.15),
                 (30,50.93,0,4.25)),
    'hvd_study': ((8.475,3.17,180,3.03),),
}

FLOOR = Material((.65,.65,.64),'hvd_paving')
WALL = Material((.69,.69,.70),'hvd_ashlar',shadow=1)
PASSAGE = Material((.105,.12,.145),'hvd_rough')


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


def frame(mesh,x,y,angle,width,height,passage=False):
    details=Mesh()
    radius=width*.5-.025
    arch(details,radius,2.25,0,.23,.49,TRIM,masonry=True)
    if passage:
        shade=[(radius*cos(pi*i/18),.025,2.25+radius*sin(pi*i/18)) for i in range(19)]
        shade.extend(((-radius,.025,.03),(radius,.025,.03)))
        details.polygon(PASSAGE,shade)
    for sign in (-1,1):
        details.box(BASALT,sign*(radius+.105),0,0,.27,.59,.28)
        details.box(LIMESTONE,sign*(radius+.115),0,2.10,.31,.65,.15)
    a=radians(angle)
    for material,polygons in details.faces.items():
        for verts,uv in polygons:
            mesh.polygon(material,[(x+u*cos(a)-v*sin(a),y+u*sin(a)+v*cos(a),
                                    z if z <= 2.25 else 2.25 + (z-2.25)*(height-2.25)/(radius+.23))
                                   for u,v,z in verts],uv)


def chamber_tile(tx,ty,occupied,height,frames,ends):
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
            masonry(mesh,a,b,height)
            quad(((*b,0),(*a,0),(*a,height),(*b,height)),2)
    for x,y,angle,width in frames:
        if int(x//10)==tx and int(y//10)==ty:
            frame(mesh,x-cx,y-cy,angle,width,height)
    for x,y,angle,width in ends:
        if int(x//10)==tx and int(y//10)==ty:
            frame(mesh,x-cx,y-cy,angle,width,height,passage=True)
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
        _,_,height,frames=PLANS[area]
        model,wok,cells=chamber_tile(x,y,occupied[area],height,frames,ENDS[area])
        resources.update(as_tile(name,model,wok))
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
