"""Broad axial stairs on the existing five-metre terrace height increments."""

import re
import struct
from dataclasses import dataclass
from math import sqrt

from architecture import BASALT, LIMESTONE, MASONRY, PALE, SLATE, surface
from art import BRASS, TRIM, Material, Mesh
from scree import band_height, ledge_tile, minimap as ledge_minimap, terrain, textures as ledge_textures
from plan import DIRECTIONS, JOINS, SKY_DECKS, SKY_OPENING, STAIR_EDGE, THRESHOLD_INSET, TILE, ZONES


FLIGHT = "hvd_flight"
PAVING = "hvd_flagstone"
TERRACE = "hvd_stcourt"
AIR = "hvd_air"
WIDE = ("hvd_wide_l", "hvd_wide_r")
MIDDLE = "hvd_wide_mid"
# The original terrace tiles have their floor five metres above the tile origin.
LOW, HIGH = 5.0, 10.0
START, END = -4.36, 4.36
INNER, OUTER = 3.26, 3.78
COUNT = 20
COURT_STONE = Material((.79,.82,.90),'hvd_paving')


def stair_model():
    mesh = Mesh()
    surface(mesh, SLATE, -INNER, -5, INNER, START, LOW, .30)
    mesh.box(MASONRY,0,-4.68,-3.55,2*INNER,.64,LOW+3.55,tile_uv=.33)
    mesh.box(MASONRY,0,4.68,-3.55,2*INNER,.64,HIGH+3.55,tile_uv=.33)
    run = (END - START) / COUNT
    rise = (HIGH - LOW) / COUNT
    for i in range(COUNT):
        y = START + i * run
        z = LOW + i * rise
        mesh.box(MASONRY,0,y+run/2,-3.55,2*INNER,run,z+3.55,tile_uv=.33)
        surface(mesh,LIMESTONE if i % 5 else SLATE,-INNER,y,INNER,y+run,z+.008,.33)
        mesh.box(TRIM, 0, y + .028, z - .045, INNER*2, .067, .046)
    # Close the last riser where the flight meets the upper landing.
    mesh.polygon(MASONRY, ((-INNER, END, HIGH-rise), (INNER, END, HIGH-rise),
                           (INNER, END, HIGH), (-INNER, END, HIGH)),
                 ((0, 0), (.6*INNER, 0), (.6*INNER, .3*rise), (0, .3*rise)))
    for side in (-1,1):
        x = side * (INNER + OUTER) / 2
        for i in range(20):
            y = -4.75+i*.5
            z = LOW + max(0,min(5,(y-START)*5/(END-START)))
            mesh.box(BASALT,x,y,-3.55,OUTER-INNER,.5,z+3.69,tile_uv=.34)
            mesh.box(LIMESTONE,x,y,z-.44,OUTER-INNER+.06,.5,.12)
        for y,z in ((-4.76,LOW),(-2.5,LOW+1.06),(0,LOW+2.5),(2.5,LOW+3.94),(4.76,HIGH)):
            mesh.box(BASALT,x,y,z-.05,.72,.66,.23)
            mesh.box(LIMESTONE,x,y,z+.17,.51,.54,.77)
            mesh.box(TRIM,x,y,z+.91,.62,.62,.14)
        for stone,z,radius in ((TRIM,.87,.185),(BRASS,1.02,.048),(PALE,1.067,.024)):
            mesh.tube(stone,(x,-5,LOW+z),(x,5,HIGH+z),radius,sides=7)
    return mesh


@dataclass(frozen=True)
class TerraceTiles:
    flight: int
    paving: int
    court: int
    air: int
    wide: tuple[int, int]
    decks: dict


def deck_bounds(code, col, row):
    """Real floor and stair widths in the tile's own coordinates."""
    zone = ZONES[code]
    if not (0 <= col < zone.size[0] and 0 <= row < zone.size[1]):
        return None
    if (col,row) in zone.stairs:
        left,right = next((l,r) for l,r in zone.flights(row) if l < 10*col+5 < r)
        return max(-5,left-10*col-5),-5,min(5,right-10*col-5),5
    if 2 <= row <= 4 and 10*col+5 in zone.bridges:
        return -INNER,-5,INNER,5
    if any(l <= col < r and b <= row < t for l,b,r,t in zone.rooms):
        return -5,-5,5,5
    return None


def deck_edges(code,col,row,bounds):
    """Guard the exposed part of each edge, leaving only real connections."""
    l,b,r,t = bounds
    for direction,edge,first,last in ((0,r,b,t),(90,t,l,r),(180,l,b,t),(270,b,l,r)):
        dx,dy = DIRECTIONS[direction]
        other = deck_bounds(code,col+dx,row+dy)
        opening = None
        if other:
            if dy:
                opening = other[0],other[2]
            elif abs(edge) == 5 and other[0 if dx>0 else 2] == -edge:
                opening = other[1],other[3]
        elif abs(edge) == 5:
            for join in JOINS:
                if code not in (join.first,join.second) or join.heading(code)!=direction:
                    continue
                x,y = join.point(code)
                u,v = x-10*col-5,y-10*row-5
                center = u if dy else v
                if abs(u*dx+v*dy-5)<.01 and first <= center <= last:
                    half = SKY_OPENING/2
                    opening = center-half,center+half
        spans = ((first,last),) if opening is None else (
            (first,min(last,opening[0])),(max(first,opening[1]),last))
        for start,end in spans:
            if end-start > .01:
                yield direction,edge,start,end


def parapet(mesh,direction,edge,start,end,*,base=LOW):
    dx,dy = DIRECTIONS[direction]

    def course(stone,along,z,length,width,height):
        at = edge-(dx+dy)*.21
        x,y = (along,at) if dy else (at,along)
        mesh.box(stone,x,y,z,length if dy else width,width if dy else length,height,tile_uv=.34)

    mid,length = (start+end)/2,end-start
    course(BASALT,mid,base-.49,length,.45,.72)
    course(LIMESTONE,mid,base+.23,length,.46,.13)
    course(LIMESTONE,mid,base+1.01,length,.48,.15)
    course(BRASS,mid,base+1.16,length,.22,.031)
    count = max(1,round(length/.82))
    for i in range(count):
        x = start+length*(i+.5)/count
        course(LIMESTONE,x,base+.33,min(.24,length/count),.32,.70)
        if i % 3 == 0:
            course(TRIM,x,base+.63,min(.29,length/count),.36,.11)


def deck_tile(code,col,row):
    zone = ZONES[code]
    bounds = deck_bounds(code,col,row)
    l,b,r,t = bounds
    mesh = Mesh()
    bridge = 10*col+5 in zone.bridges and 2 <= row <= 4
    if bridge:
        # A single span is cut from the same arch along all three tiles.
        for i in range(20):
            u = 10*row-20+(i+.5)*.5
            bottom = -4.9+7.15*sqrt(max(0,1-((u-15)/15)**2))
            y = -4.75+i*.5
            mesh.box(MASONRY,0,y,bottom,r-l,.50,LOW-.39-bottom,tile_uv=.33)
            mesh.box(LIMESTONE,0,y,bottom,r-l+.024,.50,.30,tile_uv=.30)
    else:
        mesh.box(BASALT,(l+r)/2,(b+t)/2,-4.6,r-l,t-b,9.10,tile_uv=.29)
    mesh.box(MASONRY,(l+r)/2,(b+t)/2,4.50,r-l,t-b,.47,tile_uv=.35)
    mesh.polygon(COURT_STONE,((l,b,LOW),(r,b,LOW),(r,t,LOW),(l,t,LOW)),
                 [((10*col+x)*.34,(10*row+y)*.34) for x,y in ((l,b),(r,b),(r,t),(l,t))])
    if bridge:
        for x in (-2.37,2.37):
            mesh.trace(BRASS,(x,b,LOW+.009),(x,t,LOW+.009),.058)
            mesh.trace(SLATE,(x*.90,b,LOW+.008),(x*.90,t,LOW+.008),.15)
    if code=='gate' and col==3 and row in (1,2):
        start = -2.7 if row==1 else -5
        end = 2.5 if row==2 else 5
        surface(mesh,SLATE,-2.08,start,2.08,end,LOW+.012,.38)
        for x in (-1.96,1.96):
            mesh.trace(BRASS,(x,start,LOW+.018),(x,end,LOW+.018),.049)
        if row==1:
            mesh.trace(LIMESTONE,(-2.08,start,LOW+.016),(2.08,start,LOW+.016),.068)
    if code == 'top' and col == 3:
        surface(mesh,SLATE,-2.43,b,2.43,t,LOW+.012,.36)
        for x in (-2.34,2.34):
            mesh.trace(BRASS,(x,b,LOW+.018),(x,t,LOW+.018),.035)
    if code == 'top':
        for direction,edge in ((-1,b),(1,t)):
            for left,right in zone.flights(row+direction):
                for position in (left-.31,right+.31):
                    x = position-TILE*col-TILE/2
                    if l <= x <= r:
                        y = edge-direction*.27
                        mesh.box(BASALT,x,y,LOW-.21,.82,.71,.45)
                        mesh.box(LIMESTONE,x,y,LOW+.21,.58,.62,.98)
                        mesh.box(TRIM,x,y,LOW+1.16,.72,.73,.18)
    for direction,edge,start,end in deck_edges(code,col,row,bounds):
        parapet(mesh,direction,edge,start,end)
        if not bridge:
            dx,dy = DIRECTIONS[direction]
            half = (start+end)/2
            at = edge+(dx+dy)*.069
            x,y = (half,at) if dy else (at,half)
            length=end-start
            mesh.box(LIMESTONE,x,y,LOW-1.03,length if dy else .24,
                     .24 if dy else length,.132,tile_uv=.34)
            if length > 6.0:
                mesh.box(MASONRY,x,y,LOW-6.92,.83 if dy else .63,
                         .63 if dy else .83,5.98,tile_uv=.34)
                mesh.box(LIMESTONE,x,y,LOW-1.55,1.0 if dy else .75,
                         .75 if dy else 1.0,.26,tile_uv=.34)
    floor = ([(l,b,LOW),(r,b,LOW),(r,t,LOW),(l,t,LOW)],[(0,1,2),(0,2,3)])
    return mesh,floor


def terrace_view(join,target):
    """Use the destination's actual stonework at the other side of the seam."""
    x,y = join.point(target)
    dx,dy = DIRECTIONS[(join.heading(target)+180)%360]
    col0,row0 = int((x+dx)//10),int((y+dy)//10)
    ramps = {row for _,row in ZONES[target].stairs}
    mesh = Mesh()
    rocky = target=='walks'
    patches = terrain()[0] if rocky else {}
    for step in range(3):
        col,row = col0+step*dx,row0+step*dy
        ox,oy = 10*col+5-x,10*row+5-y
        if rocky:
            if (col,row) not in patches:
                break
            drawn,_=ledge_tile(col,row)
            z=-band_height(y)
        else:
            if not deck_bounds(target,col,row):
                break
            z = 5*(sum(r<row for r in ramps)-sum(r<row0 for r in ramps))-LOW
            if (col,row) in ZONES[target].stairs:
                drawn = wide_stair(0)[0] if target=='top' else stair_model()
            else:
                drawn,_ = deck_tile(target,col,row)
        for material,polygons in drawn.faces.items():
            for points,uv in polygons:
                mesh.polygon(material,
                    [((a+ox)*dy-(b+oy)*dx,(a+ox)*dx+(b+oy)*dy+THRESHOLD_INSET,c+z)
                     for a,b,c in points],uv)
    return mesh


def wide_stair(side):
    """An outer or middle section of a stair with open joints across its width."""
    mesh = Mesh()
    inner = side*(5.0-STAIR_EDGE)
    edge = side*5.0
    xmin, xmax = sorted((inner, -edge)) if side else (-5,5)
    center = (xmin+xmax)/2
    run, rise = (END-START)/COUNT, (HIGH-LOW)/COUNT
    surface(mesh, LIMESTONE, xmin,-5,xmax,START,LOW,.28)
    surface(mesh, LIMESTONE, xmin,END,xmax,5,HIGH,.28)
    for i in range(COUNT):
        y = START + i*run
        z = LOW + i*rise
        mesh.box(MASONRY,center,y+run*.5,-3.55,xmax-xmin,run,z+3.55,tile_uv=.33)
        mesh.box(LIMESTONE,center,y+.028,z-.048,xmax-xmin,.061,.051)
        # The narrow gilded trim reads as a course of stone at game zoom.
        if i in (0, 5, 10, 15):
            mesh.trace(BRASS,(xmin,y+.12,z+.006),(xmax,y+.12,z+.006),.068)
    mesh.box(MASONRY,center,4.68,-3.55,xmax-xmin,.64,HIGH+3.55,tile_uv=.33)
    if not side:
        return mesh,floor_mesh(xmin,xmax,edge_access=False)
    for i in range(10):
        y = -4.5+i
        z = max(LOW,min(HIGH,LOW+(y-START)*(HIGH-LOW)/(END-START)))
        mesh.box(BASALT,(inner+edge)/2,y,-3.65,STAIR_EDGE,.999,z+4.0,tile_uv=.34)
        mesh.box(LIMESTONE,(inner+edge)/2,y,z-1.10,STAIR_EDGE+.04,.999,.11,tile_uv=.32)
        if i in (0, 3, 6, 9):
            mesh.box(MASONRY,(inner+edge)/2,y,z+.29,.57,.59,.92)
            mesh.box(LIMESTONE,(inner+edge)/2,y,z+1.18,.70,.67,.15)
    x = inner+side*.31
    mesh.tube(LIMESTONE,(x,-4.68,LOW+1.03),(x,4.68,HIGH+1.03),.18,sides=8)
    mesh.tube(BRASS,(x,-4.68,LOW+1.18),(x,4.68,HIGH+1.18),.048,sides=7)
    return mesh, floor_mesh(xmin,xmax,edge_access=False)


def floor_mesh(xmin=-INNER, xmax=INNER, *, edge_access=True):
    vertices, triangles = [], []

    def vertex(x, y, z):
        point = x, y, z
        if point in vertices:
            return vertices.index(point)
        vertices.append(point)
        return len(vertices)-1

    def ribbon(x0, x1, y0, y1, z0, z1):
        a = vertex(x0,y0,z0)
        b = vertex(x1,y0,z0)
        c = vertex(x1,y1,z1)
        d = vertex(x0,y1,z1)
        triangles.extend(((a,b,c),(a,c,d)))

    edges = ((-5,xmin),(xmin,xmax),(xmax,5)) if edge_access else ((xmin,xmax),)
    for x0,x1 in edges:
        ribbon(x0,x1,-5,START,LOW,LOW)
        ribbon(x0,x1,END,5,HIGH,HIGH)
    ribbon(xmin,xmax,START,END,LOW,HIGH)
    return vertices, triangles


def aabb_tree(vertices, triangles, faces):
    points = [vertices[index] for face in faces for index in triangles[face]]
    low = [min(p[d] for p in points) for d in range(3)]
    high = [max(p[d] for p in points) for d in range(3)]
    bounds = " ".join(f"{value:.4f}" for value in low+high)
    if len(faces) == 1:
        return [bounds + f" {faces[0]}"]
    axis = max(range(2), key=lambda d: high[d]-low[d])
    ordered = sorted(faces,key=lambda f: sum(vertices[k][axis] for k in triangles[f]))
    middle = len(ordered)//2
    return ([bounds+" -1"] + aabb_tree(vertices,triangles,ordered[:middle])
            + aabb_tree(vertices,triangles,ordered[middle:]))


def floor_node(name, vertices, triangles, materials=None):
    lines = ["node aabb walkmesh", f"  parent {name}", "  position 0 0 0", "  bitmap NULL",
             "  orientation 0 0 0 0", "  render 0", "  shadow 0", f"  verts {len(vertices)}"]
    lines.extend("    %.5f %.5f %.5f" % p for p in vertices)
    lines.append(f"  faces {len(triangles)}")
    if materials is None:
        materials = [4] * len(triangles)
    lines.extend("    %d %d %d 0 0 0 0 %d" % (*face, material)
                 for face, material in zip(triangles, materials, strict=True))
    tree = aabb_tree(vertices,triangles,list(range(len(triangles))))
    lines.append("  aabb " + tree[0])
    lines.extend("    " + row for row in tree[1:])
    lines.append("endnode")
    return "\n".join(lines) + "\n"


def set_row(number, name, upper_height, terrain="cobble"):
    return (
        f"\r\n[TILE{number}]\r\nModel={name}\r\nWalkMesh=msb01\r\n"
        f"TopLeft={terrain}\r\nTopLeftHeight={upper_height}\r\nTopRight={terrain}\r\nTopRightHeight={upper_height}\r\n"
        f"BottomLeft={terrain}\r\nBottomLeftHeight=0\r\nBottomRight={terrain}\r\nBottomRightHeight=0\r\n"
        "Top=\r\nRight=\r\nBottom=\r\nLeft=\r\nMainLight1=1\r\nMainLight2=1\r\n"
        "SourceLight1=1\r\nSourceLight2=1\r\nAnimLoop1=1\r\nAnimLoop2=1\r\nAnimLoop3=1\r\n"
        f"Doors=0\r\nSounds=0\r\nPathNode={'A' if terrain=='chasm' else 'F'}\r\nOrientation=0\r\nVisibilityNode=A\r\n"
        f"VisibilityOrientation=0\r\nImageMap2D=mi_{name}\r\n\r\n"
    )


def as_tile(name, mesh, floor, is_flight=False, *, empty=False):
    node = floor_node(name, *floor).encode("ascii")
    model = mesh.mdl(name).replace(b"classification Other",b"classification Tile")
    model = model.replace(b"endmodelgeom",node+b"endmodelgeom",1)
    walk = f"#MAXWALKMESH ASCII\nbeginwalkmeshgeom {name}\n".encode("ascii") + node
    walk += f"endwalkmeshgeom {name}\n".encode("ascii")
    size = 64
    header = struct.pack("<BBBHHBHHHHBB",0,0,2,0,0,0,0,0,size,size,24,0)
    pixels = bytearray()
    vertices = floor[0]
    left,right = min(x for x,_,_ in vertices),max(x for x,_,_ in vertices)
    for y in range(size):
        for x in range(size):
            color = (84,101,124)
            if is_flight and 10 < x < 53:
                color = (129,150,184) if y%4 else (91,115,151)
            if is_flight and x in (10,53):
                color = (151,164,199)
            if not is_flight and (y%16==0 or (x+8*(y//16))%20==0):
                color = (74,88,112)
            u = (x+.5)*10/size-5
            if empty or not left <= u <= right:
                color = (7,8,17)
            pixels.extend(color)
    return {f"{name}.mdl":model, f"{name}.wok":walk, f"mi_{name}.tga":header+pixels}


def tile_assets(game, workshop):
    raw = game.read("tcm02","set").decode("latin-1")
    raw = raw.replace("Border=Cobble", "Border=Chasm", 1)
    # This is the sky outside the authored islands, including area border
    # tiles drawn by the client beyond the editable grid.
    raw = re.sub(r"(?m)^(Model=)(tcm02_v05_\d+)(\r?)$", rf"\g<1>{AIR}\3", raw)
    found = re.search(r"(?im)^(\[TILES\]\r?\nCount=)(\d+)",raw)
    if not found:
        raise ValueError("Castle Exterior tileset has no tile count")
    number = int(found[2])
    layouts = {code:{} for code in SKY_DECKS}
    deck_models = {}
    middle_cells = []
    ledges = terrain()[0]
    for code, layout in layouts.items():
        zone = ZONES[code]
        for row in range(zone.size[1]):
            columns = sorted(c for c,y in zone.stairs if row==y)
            for col in range(zone.size[0]):
                if code=='walks':
                    if (col,row) not in ledges:
                        layout[col,row] = number+3,0
                        continue
                    index = number+6+len(workshop)+len(deck_models)
                    name = f'hvd_ledge{col}{row:02}'
                    pieces = as_tile(name,*ledge_tile(col,row))
                    pieces[f'mi_{name}.tga'] = ledge_minimap(col,row)
                    deck_models[index] = name,pieces
                    layout[col,row] = index,0
                    continue
                if col in columns:
                    if len(columns)==1:
                        layout[col,row] = number,0
                    elif col in (columns[0],columns[-1]):
                        layout[col,row] = number + (4 if col==columns[0] else 5),0
                    else:
                        middle_cells.append((layout,col,row))
                    continue
                if not deck_bounds(code,col,row):
                    layout[col,row] = number+3,0
                    continue
                index = number+6+len(workshop)+len(deck_models)
                name = f'hvd_deck{len(deck_models):03}'
                deck_models[index] = (name,as_tile(name,*deck_tile(code,col,row)))
                layout[col,row] = index,0
    middle = number+6+len(workshop)+len(deck_models)
    for layout,col,row in middle_cells:
        layout[col,row] = middle,0
    raw = raw[:found.start(2)] + str(middle+1) + raw[found.end(2):]
    cursor = re.search(r"(?im)^\[GROUPS\]",raw).start()
    ids = TerraceTiles(number,number+1,number+2,number+3,(number+4,number+5),layouts)
    rows = (set_row(ids.flight,FLIGHT,1) + set_row(ids.paving,PAVING,0) +
            set_row(ids.court,TERRACE,0) + set_row(ids.air,AIR,0,"chasm") +
            ''.join(set_row(i,name,1) for i,name in zip(ids.wide,WIDE,strict=True)))
    workshop_ids = {}
    for index,(cell,(name,_)) in enumerate(workshop.items(),number+6):
        workshop_ids[cell] = index,0
        rows += set_row(index,name,0)
    for index,(name,_) in deck_models.items():
        rows += set_row(index,name,0)
    rows += set_row(middle,MIDDLE,1)
    raw = raw[:cursor] + rows + raw[cursor:]
    paving = Mesh()
    surface(paving, MASONRY, -5,-5,5,5,LOW,.30)
    court = Mesh()
    court.box(BASALT,0,0,-4.4,10,10,8.9,tile_uv=.28)
    court.box(MASONRY,0,0,4.47,10,10,.53,tile_uv=.33)
    surface(court,COURT_STONE,-5,-5,5,5,LOW+.004,.34)
    triangles = [(0,1,2),(0,2,3)]
    flat = ([(-5,-5,LOW),(5,-5,LOW),(5,5,LOW),(-5,5,LOW)], triangles)
    void = ([(-5,-5,-32),(5,-5,-32),(5,5,-32),(-5,5,-32)], triangles, [7,7])
    resources = {
        "tcm02.set":raw.encode("latin-1"),
        **ledge_textures(),
        **as_tile(FLIGHT,stair_model(),floor_mesh(edge_access=False),True),
        **as_tile(PAVING,paving,flat),
        **as_tile(TERRACE,court,flat),
        **as_tile(AIR,Mesh(),void,empty=True),
        **as_tile(MIDDLE,*wide_stair(0),True),
    }
    for name, side in zip(WIDE,(-1,1),strict=True):
        resources.update(as_tile(name,*wide_stair(side),True))
    for _,pieces in workshop.values():
        resources.update(pieces)
    for _,pieces in deck_models.values():
        resources.update(pieces)
    return ids, workshop_ids, resources
