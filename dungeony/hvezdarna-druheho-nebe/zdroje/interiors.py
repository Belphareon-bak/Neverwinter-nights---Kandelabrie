"""Native interior tiles and the stone passages between the two lower wings."""

from math import cos, pi, radians, sin
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, SLATE, SNOW, surface
from art import BRASS, CROWN, TRIM, Material, Mesh, arch
from flights import as_tile
from plan import DIRECTIONS, JOINS, THRESHOLD_INSET, TILE, WORK_YARD_WALLS, ZONES


TILESET = 'hvd_interior'
WING_HEIGHT = 3.84
WORK_CELLS = ((4,0),(5,0),(4,1),(5,1),(5,5))
WORK_OPENINGS = ((40,12.1,17.9),(50,52.2,57.8))
WORK_FRAMES = (
    (53,2.85,0,5.75),(53,9.6,0,5.75),
    (41.55,15,90,5.75),(58.45,15,90,5.75),
    (51.55,55,90,5.55),(58.45,55,90,5.55),
)
WORK_ROOFS = {
    (5,0): ((53,1.9,0,5.8,3.8),),
    (5,1): ((58.05,15,90,5.8,3.9),),
    (5,5): ((57.94,55,90,5.6,4.12),),
}
HALL_ROOFS = {(0,y//10): ((1.95,y,90,width,3.9),) for y,width in ((15,5.8),(55,5.6))}
YARD_MODELS = {f'hvd_yardw{index}': span for index,span in enumerate(WORK_YARD_WALLS)}

# Frames share the width of an actual corridor and appear on its walkmesh.
def chamber(code, height, frames):
    zone = ZONES[code]
    return zone.size, zone.rooms, height, frames


PLANS = {
    'hvd_halls': chamber('halls', WING_HEIGHT,
        ((1.55,15,90,5.7),(7,15,90,5.7),(13,20.5,0,5.7),
         (21,15,90,4.9),(23.6,15,90,4.9),(29.9,15,90,4.9),
         (37.35,15,90,4.9),(44.65,15,90,4.9),(47,15,90,4.9),(49.85,37.15,0,5.6),
         (24,45,90,5.6),(1.55,55,90,5.5))),
    'hvd_study': chamber('study', 3.32,
        ((8.8,31,0,5.5),(17.9,42.9,0,5.5),(23,58.6,0,5.5))),
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


def masonry(mesh,a,b,height,*,wing=False):
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
    if wing:
        mesh.box(TRIM,cx+nx*.02,cy+ny*.02,2.74,width if dx else .19,
                 width if dy else .19,.09,tile_uv=.31)
        mesh.trace(BRASS,(a[0]-nx*.23,a[1]-ny*.23,.018),
                   (b[0]-nx*.23,b[1]-ny*.23,.018),.048)


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


def barrel_strip(mesh,x,y,angle,width,length):
    # Leave the full chamber open above. The short vault covers the actual seam.
    a = radians(angle)
    def position(u,v,z):
        return (x+u*cos(a)-v*sin(a),y+u*sin(a)+v*cos(a),z)

    span = width/2+.28
    for i in range(14):
        first,last = i*pi/14,(i+1)*pi/14
        start,end = [(span*cos(p),WING_HEIGHT-.08+sin(p)*1.31) for p in (first,last)]
        points = (position(start[0],-length/2,start[1]),position(start[0],length/2,start[1]),
                  position(end[0],length/2,end[1]),position(end[0],-length/2,end[1]))
        mesh.polygon(CROWN,points,[(0,0),(0,length*.30),(1,length*.30),(1,0)])
        mesh.polygon(SLATE,points[::-1],[(1,0),(1,length*.30),(0,length*.30),(0,0)])
        for v in (-length/2,length/2):
            mesh.tube(TRIM,position(start[0],v,start[1]),position(end[0],v,end[1]),.079,sides=6)
    mesh.tube(BRASS,position(0,-length/2,WING_HEIGHT+1.24),
              position(0,length/2,WING_HEIGHT+1.24),.045,sides=7)


def chamber_tile(tx,ty,occupied,height,frames,size,*,wing=False,elevated=False,openings=(),roofs=()):
    mesh=Mesh()
    vertices=[]
    index={}
    faces=[]
    materials=[]
    room_cells=[]
    cx,cy=TILE*tx+TILE/2,TILE*ty+TILE/2

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
        if elevated:
            mesh.box(MASONRY,(x0+x1)/2,(y0+y1)/2,-3.25,x1-x0,y1-y0,3.24,tile_uv=.30)
        # Use the same phase of the paving texture on neighboring tiles.
        mesh.polygon(FLOOR,((x0,y0,0),(x1,y0,0),(x1,y1,0),(x0,y1,0)),
                     [((x+cx)*.30,(y+cy)*.30) for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))])
        corners=((x0,y0),(x1,y0),(x1,y1),(x0,y1))
        quad([(*p,0) for p in corners],4)
        for k,adjacent in enumerate(((i,j-1),(i+1,j),(i,j+1),(i-1,j))):
            if adjacent in occupied:
                continue
            a,b=corners[k],corners[(k+1)%4]
            w,h=size
            on_set_edge = ((a[0]==b[0] and a[0]+cx in (0,10*w))
                           or (a[1]==b[1] and a[1]+cy in (0,10*h)))
            opening = a[0]==b[0] and any(abs(a[0]+cx-x)<.001 and
                lo-.001<=min(a[1],b[1])+cy<=max(a[1],b[1])+cy<=hi+.001
                for x,lo,hi in openings)
            if on_set_edge or opening:
                continue
            masonry(mesh,a,b,height,wing=wing)
            quad(((*b,0),(*a,0),(*a,height),(*b,height)),2)
    for x,y,angle,width in frames:
        if int(x//10)==tx and int(y//10)==ty:
            frame(mesh,x-cx,y-cy,angle,width,height)
    for x,y,angle,width,length in roofs:
        barrel_strip(mesh,x-cx,y-cy,angle,width,length)
    if not room_cells:
        quad(((-5,-5,-10),(5,-5,-10),(5,5,-10),(-5,5,-10)),7)
    return mesh,(vertices,faces,materials),room_cells


def work_tile(x,y):
    zone = ZONES['works']
    return chamber_tile(x,y,grid(zone.size,zone.enclosed),WING_HEIGHT,WORK_FRAMES,zone.size,
                        wing=True,elevated=True,openings=WORK_OPENINGS,roofs=WORK_ROOFS.get((x,y),()))


def yard_wall(span):
    (x,y),(xx,yy) = span
    a,b = ((x-xx)/2,(y-yy)/2),((xx-x)/2,(yy-y)/2)
    mesh = Mesh()
    masonry(mesh,a,b,WING_HEIGHT-.42,wing=True)
    return mesh


def yard_wall_assets():
    return {model:('Obvodová stěna dílen', lambda span=span: yard_wall(span))
            for model,span in YARD_MODELS.items()}


def workshop_tiles():
    tiles = {}
    for number,(x,y) in enumerate(WORK_CELLS):
        mesh,(vertices,faces,materials),cells = work_tile(x,y)
        # Castle Exterior places the adjoining decks 5 m above the tile origin.
        shifted = Mesh()
        for material,polygons in mesh.faces.items():
            for points,uv in polygons:
                shifted.polygon(material,[(a,b,c+5) for a,b,c in points],uv)
        vertices = [(a,b,c+5) for a,b,c in vertices]
        name = f'hvd_wing{number}'
        resources = as_tile(name,shifted,(vertices,faces,materials))
        resources[f'mi_{name}.tga'] = minimap(cells)
        tiles[x,y] = name, resources
    return tiles


SHARED_VIEWS = {
    ('03','works'): ((5,0),(5,1)),
    ('03','rim'): (),
    ('01','halls'): ((0,1),(1,1),(1,2)),
    ('01','works'): ((5,0),(5,1),(4,1)),
    ('02','halls'): ((0,5),(1,5),(1,4)),
    ('02','works'): ((5,5),),
}
VIEW_MODELS = {key: f'hvd_link{i}' for i,key in enumerate(SHARED_VIEWS)}


def link_mesh(join,target,squares):
    """Project the same facing of the next wing beyond the transition edge."""
    output = Mesh()
    if target == 'rim':
        start = THRESHOLD_INSET
        surface(output,SNOW,-4.5,start,4.5,start+7.9,-.075,.29)
        surface(output,SLATE,-2.30,start,2.30,start+7.9,.009,.37)
        return output

    dx,dy = DIRECTIONS[(join.heading(target)+180)%360]
    ex,ey = join.point(target)
    if target == 'halls':
        size,rooms,height,frames = PLANS['hvd_halls']
        cells = grid(size,rooms)
    for x,y in squares:
        if target == 'works':
            drawn,_,_ = work_tile(x,y)
        else:
            drawn,_,_ = chamber_tile(x,y,cells,height,frames,size,wing=True,elevated=True,
                                     roofs=HALL_ROOFS.get((x,y),()))
        ox,oy = TILE*(x+.5)-ex,TILE*(y+.5)-ey
        for material,polygons in drawn.faces.items():
            for points,uv in polygons:
                output.polygon(material,
                    [((a+ox)*dy-(b+oy)*dx,(a+ox)*dx+(b+oy)*dy+THRESHOLD_INSET,c)
                     for a,b,c in points],uv)
    if (join.label,target)==('02','works'):
        start = TILE+THRESHOLD_INSET
        surface(output,SLATE,-3.12,start,3.12,start+5.4,0,.34)
    return output


def shared_view_assets():
    joins = {join.label: join for join in JOINS}
    return {VIEW_MODELS[label,target]:('Zdivo za průchodem',
              lambda j=joins[label], dst=target, tiles=squares:link_mesh(j,dst,tiles))
            for (label,target),squares in SHARED_VIEWS.items()}


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
        is_hall = area=='hvd_halls'
        model,wok,cells=chamber_tile(x,y,occupied[area],height,frames,size,wing=is_hall,
                                    roofs=HALL_ROOFS.get((x,y),()) if is_hall else ())
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
