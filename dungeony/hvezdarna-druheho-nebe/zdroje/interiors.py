"""Native interior tiles and the stone passages between the two lower wings."""

from math import copysign, cos, pi, radians, sin, sqrt
from struct import pack

from architecture import BASALT, LIMESTONE, MASONRY, PALE, SLATE, SNOW, surface
from art import BRASS, CROWN, TRIM, Material, Mesh, arch, star
from flights import as_tile, parapet
from navrh_v21 import ACCESS_DOOR, BEAM_HEIGHT, BREACH, OPTICAL_SLOT, R1_FRAME, R1_WIDTH, SLOT_WIDTH
from plan import (DIRECTIONS, ENTRY_X, JOINS, THRESHOLD_INSET, TILE,
                  WORK_BRIDGE_LANDING, WORK_SHELF, WORK_YARD_WALLS, ZONES)


TILESET = 'hvd_interior'
WING_HEIGHT = 3.84
WORK_CELLS = ((4,0),(5,0),(4,1),(5,1),(5,5),(2,7),(3,7))
SHELF_COL, SHELF_ROW, SHELF_END_COL, SHELF_END_ROW = WORK_SHELF
SHELF_CELLS = tuple((x,y) for y in range(SHELF_ROW,SHELF_END_ROW)
                    for x in range(SHELF_COL,SHELF_END_COL))
SHELF_RECT = tuple(edge*TILE for edge in WORK_SHELF)
SHELF_LANDING = (WORK_BRIDGE_LANDING[0],SHELF_RECT[1]-TILE,
                 WORK_BRIDGE_LANDING[1],SHELF_RECT[1])
WORK_OPENINGS = ((0,40,12.1,17.9),(0,50,52.2,57.8),(1,70,20,40))
WORK_FRAMES = (
    (ENTRY_X,2.85,0,5.75),(ENTRY_X,7.25,0,15.95),(ENTRY_X,11.7,0,15.95),
    (41.55,15,90,5.75),(59.38,15,90,5.75),
    (51.55,55,90,5.55),(58.45,55,90,5.55),(30,73.15,0,5.78),
)
WORK_ROOFS = {
    (5,1): ((59.58,15,90,5.8,.84),),
    (5,5): ((58.55,55,90,5.6,2.9),),
}
HALL_ROOFS = {(0,y//10): ((1.95,y,90,width,3.9),) for y,width in ((15,5.8),(55,5.6))}
DOME_ROOFS = {(3,0): ((30,3.94,0,6.0,7.88),)}
R1_VAULT = {(4,3): ((*R1_FRAME,0,R1_WIDTH,3.15),)}
INTERIOR_ROOFS = {'hvd_halls': HALL_ROOFS | R1_VAULT, 'hvd_dome': DOME_ROOFS, 'hvd_service': R1_VAULT}
YARD_MODELS = {f'hvd_yardw{index}': span for index,span in enumerate(WORK_YARD_WALLS)}

# Frames share the width of an actual corridor and appear on its walkmesh.
def chamber(code, height, frames):
    zone = ZONES[code]
    return zone.size, zone.rooms, height, frames


PLANS = {
    'hvd_halls': chamber('halls', WING_HEIGHT,
        ((1.55,15,90,5.7),(7,15,90,5.7),
         (21,15,90,4.9),(23.6,15,90,4.9),(29.9,15,90,4.9),
         (37.35,15,90,4.9),(44.65,15,90,4.9),(47,15,90,4.9),(49.85,37.15,0,5.6),
         (24,45,90,5.6),(1.55,55,90,5.5),(*ACCESS_DOOR,90,2.1),(*R1_FRAME,0,R1_WIDTH))),
    'hvd_study': chamber('study', 3.32,
        ((8.8,31,0,5.5),(17.9,42.9,0,5.5),(23,58.6,0,5.5),(15,158.9,0,5.7))),
    'hvd_dome': chamber('dome', 3.85,
        ((30,1.55,0,5.8),(30,17,0,6),(13.2,26.05,90,5.9),
         (46.8,26.1,90,5.8),(30,46,0,6.4))),
    'hvd_service': chamber('service', WING_HEIGHT, ((*ACCESS_DOOR,90,2.1),(*R1_FRAME,0,R1_WIDTH))),
}

FLOOR = Material((.65,.65,.64),'hvd_paving')
WALL = Material((.69,.69,.70),'hvd_ashlar',shadow=1)


def tile_assignments(key):
    return {(x,y):(number,0) for number,(area,x,y) in enumerate(all_cells()) if area==key}


def all_cells():
    yield from ((area,x,y) for area,((width,height),_,_,_) in PLANS.items()
                for y in range(height) for x in range(width))


def grid(size, rooms, *, y_cuts=()):
    width,height=size
    xs=sorted(set(range(0,10*width+1,10)) | {edge for x0,_,x1,_ in rooms for edge in (x0,x1)})
    ys=sorted(set(range(0,10*height+1,10)) | set(y_cuts)
              | {edge for _,y0,_,y1 in rooms for edge in (y0,y1)})
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


def optical_wall(mesh, a, b, height):
    bottom, top = BEAM_HEIGHT-.35, BEAM_HEIGHT+.35
    masonry(mesh, a, b, bottom)
    side = copysign(1, b[1]-a[1])
    mesh.box(WALL, a[0]+side*.255, (a[1]+b[1])/2, top, .51, abs(b[1]-a[1]),
             height-top, tile_uv=.31)


def broken_lintel(mesh, cx, cy):
    left,bottom,right,top=BREACH
    left,right,bottom,top=left-cx,right-cx,bottom-cy,top-cy
    crown=((bottom-.04,2.29),(bottom+.31,2.58),(bottom+.69,2.72),
           (top-.61,2.66),(top-.27,2.49),(top+.04,2.24))
    for (a,za),(b,zb) in zip(crown,crown[1:]):
        def face(x):
            return ((x,a,za),(x,b,zb),(x,b,WING_HEIGHT),(x,a,WING_HEIGHT))
        mesh.polygon(WALL,face(left-.018)[::-1])
        mesh.polygon(WALL,face(right+.018))
        mesh.polygon(BASALT,((left,b,zb),(right,b,zb),(right,a,za),(left,a,za)))
        mesh.box(LIMESTONE,(left+right)/2,(a+b)/2,WING_HEIGHT-.14,right-left+.16,b-a,.14,tile_uv=.32)
    for side,y in ((1,bottom),(-1,top)):
        mesh.box(BASALT,(left+right)/2,y+side*.070,0,right-left+.095,.27,.29,tile_uv=.33)
        mesh.box(MASONRY,(left+right)/2,y+side*.028,.29,right-left+.08,.15,2.11,tile_uv=.29)
        tip=(left+.42,y+side*.16,.19)
        mesh.polygon(TRIM,((left-.13,y,0),(right-.13,y,0),tip))


def frame(mesh,x,y,angle,width,height):
    details=Mesh()
    radius=width*.5-.025
    spring = 3.18 if width > 10 else 2.25
    arch(details,radius,spring,0,.23,.49,TRIM,masonry=True)
    if width > 10:
        arch(details,radius,spring,-.28,.073,.11,LIMESTONE)
    for sign in (-1,1):
        details.box(BASALT,sign*(radius+.105),0,0,.27,.59,.28)
        details.box(LIMESTONE,sign*(radius+.115),0,spring-.15,.31,.65,.15)
    a=radians(angle)
    for material,polygons in details.faces.items():
        for verts,uv in polygons:
            mesh.polygon(material,[(x+u*cos(a)-v*sin(a),y+u*sin(a)+v*cos(a),
                                    z if z <= spring else spring+(z-spring)*(height-spring)/(radius+.23))
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


def chamber_tile(tx,ty,occupied,height,frames,size,*,wing=False,elevated=False,
                 openings=(),roofs=(),balustrade=False,optical=False):
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
            mesh.box(MASONRY,(x0+x1)/2,(y0+y1)/2,-4.40,x1-x0,y1-y0,4.398,tile_uv=.30)
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
            opening = any(a[axis]==b[axis] and abs(a[axis]+(cx,cy)[axis]-edge)<.001 and
                lo-.001<=min(a[1-axis],b[1-axis])+(cy,cx)[axis]<=max(a[1-axis],b[1-axis])+(cy,cx)[axis]<=hi+.001
                for axis,edge,lo,hi in openings)
            if on_set_edge or opening:
                continue
            if balustrade:
                direction = (270,0,90,180)[k]
                across,along = (1,0) if k%2==0 else (0,1)
                start,end = sorted((a[along],b[along]))
                parapet(mesh,direction,a[across],start,end,base=0)
                barrier_height = 1.18
            else:
                barrier_height = WING_HEIGHT if wing and min(a[0],b[0])+cx>=59.15 else height
                passthrough = (optical and a[0] == b[0] and
                    any(abs(a[0]+cx-edge)<.001 for edge in (31.5,33.0)) and
                    max(abs(a[1]+cy-OPTICAL_SLOT[1]), abs(b[1]+cy-OPTICAL_SLOT[1])) <= SLOT_WIDTH/2+.001)
                if passthrough:
                    optical_wall(mesh,a,b,barrier_height)
                else:
                    masonry(mesh,a,b,barrier_height,wing=wing)
            quad(((*b,0),(*a,0),(*a,barrier_height),(*b,barrier_height)),2)
    for x,y,angle,width in frames:
        if int(x//10)==tx and int(y//10)==ty:
            frame(mesh,x-cx,y-cy,angle,width,height if width > 10 or not wing else WING_HEIGHT)
    if optical and (tx,ty)==(3,2):
        broken_lintel(mesh,cx,cy)
    for x,y,angle,width,length in roofs:
        barrel_strip(mesh,x-cx,y-cy,angle,width,length)
    if not room_cells:
        quad(((-5,-5,-10),(5,-5,-10),(5,5,-10),(-5,5,-10)),7)
    return mesh,(vertices,faces,materials),room_cells


def work_tile(x,y):
    zone = ZONES['works']
    if (x,y) in SHELF_CELLS:
        # Include the bridge landing and adjacent rooms when deciding which edges need a rail.
        connected = grid(zone.size,(*zone.enclosed,SHELF_RECT,SHELF_LANDING))
        return chamber_tile(x,y,connected,WING_HEIGHT,(),zone.size,elevated=True,balustrade=True)
    mesh,floor,cells = chamber_tile(x,y,grid(zone.size,zone.enclosed),6.23 if y<2 else WING_HEIGHT,
                                   WORK_FRAMES,zone.size,wing=True,elevated=True,openings=WORK_OPENINGS,
                                   roofs=WORK_ROOFS.get((x,y),()))
    if (x,y)==(5,1):
        cx,cy = ENTRY_X-55,14.82-15
        mesh.disc(SLATE,(cx,cy,.009),(cx,cy,.027),2.72,sides=32)
        for i in range(24):
            a,b = i*pi/12,(i+1)*pi/12
            mesh.trace(BRASS,(cx+2.63*cos(a),cy+2.63*sin(a),.031),
                       (cx+2.63*cos(b),cy+2.63*sin(b),.031),.083)
        star(mesh,cx,cy,.033,2.22,PALE,8)
    if (x,y)==(3,7):
        dome_crown(mesh,-5,1.50)
    return mesh,floor,cells


def dome_crown(mesh,x,y):
    """Close the ceremonial drum over the ashlar vestibule."""
    def point(i,j):
        theta=i*pi/10
        phi=j*pi/16
        u,v=cos(theta),sin(theta)
        return (x+3.46*copysign(sqrt(abs(u)),u)*cos(phi),
                y+3.77*copysign(sqrt(abs(v)),v)*cos(phi),3.71+3.12*sin(phi))

    for i in range(20):
        for j in range(8):
            a,b,c,d=point(i,j),point(i+1,j),point(i+1,j+1),point(i,j+1)
            face=(a,b,c) if j==7 else (a,b,c,d)
            mesh.polygon(CROWN if i%5 else SLATE,face)
            mesh.polygon(SLATE,face[::-1])
            if i%4==0:
                mesh.tube(BRASS,a,d,.050,sides=6)
        mesh.tube(LIMESTONE,point(i,0),point(i+1,0),.18,sides=8)
    mesh.disc(BRASS,(x,y,6.68),(x,y,6.92),.48,sides=12)
    mesh.tube(BRASS,(x,y,6.91),(x,y,7.84),.096,.045,sides=8)
    mesh.disc(PALE,(x,y,7.62),(x,y,7.84),.19,sides=12)


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
    for number,(x,y) in enumerate((*WORK_CELLS,*SHELF_CELLS)):
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
    ('00','camp'): (),
    ('00','rim'): (),
    ('03','works'): ((4,0),(5,0),(4,1),(5,1)),
    ('03','rim'): (),
    ('01','halls'): ((0,1),(1,1),(1,2)),
    ('01','works'): ((5,0),(5,1),(4,1)),
    ('02','halls'): ((0,5),),
    ('02','works'): ((5,5),(4,5)),
    ('04','dome'): ((2,0),(3,0)),
    ('04','works'): ((2,7),(3,7)),
    ('S2','study'): ((1,15),),
}
VIEW_MODELS = {key: f'hvd_link{i}' for i,key in enumerate(SHARED_VIEWS)}


def link_mesh(join,target,squares):
    """Project the same facing of the next wing beyond the transition edge."""
    output = Mesh()
    if target in ('rim','camp'):
        start = THRESHOLD_INSET
        surface(output,SNOW,-4.5,start,4.5,start+7.9,-.075,.29)
        surface(output,SLATE,-2.32,start,2.32,start+7.9,.009,.37)
        return output

    dx,dy = DIRECTIONS[(join.heading(target)+180)%360]
    ex,ey = join.point(target)
    openings=()
    if target != 'works':
        size,rooms,height,frames = PLANS['hvd_'+target]
        if join.label=='02' and target=='halls':
            neck=next(room for room in rooms if room[0]==0 and room[1]<ey<room[3])
            rooms=(neck,)
            openings=((0,neck[2],neck[1],neck[3]),)
        cells = grid(size,rooms)
    for x,y in squares:
        if target == 'works':
            drawn,_,_ = work_tile(x,y)
        else:
            roofs=INTERIOR_ROOFS.get('hvd_'+target,{}).get((x,y),())
            drawn,_,_ = chamber_tile(x,y,cells,height,frames,size,wing=target=='halls',
                                     elevated=True,roofs=roofs,openings=openings)
        ox,oy = TILE*(x+.5)-ex,TILE*(y+.5)-ey
        for material,polygons in drawn.faces.items():
            for points,uv in polygons:
                output.polygon(material,
                    [((a+ox)*dy-(b+oy)*dx,(a+ox)*dx+(b+oy)*dy+THRESHOLD_INSET,c)
                     for a,b,c in points],uv)
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
    slot_edges = tuple(OPTICAL_SLOT[1]+side*SLOT_WIDTH/2 for side in (-1,1))
    occupied={area:grid(size,rooms,y_cuts=slot_edges if area=='hvd_service' else ())
              for area,(size,rooms,_,_) in PLANS.items()}
    resources={}
    for i,(area,x,y) in enumerate(indices):
        name=f'hvd_i{i:02d}'
        size,_,height,frames=PLANS[area]
        optical = area=='hvd_service'
        model,wok,cells=chamber_tile(x,y,occupied[area],height,frames,size,
                                    wing=optical or area=='hvd_halls', optical=optical,
                                    roofs=INTERIOR_ROOFS.get(area,{}).get((x,y),()))
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
