"""Broad axial stairs on the existing five-metre terrace height increments."""

import re
import struct
from dataclasses import dataclass

from architecture import BASALT, LIMESTONE, MASONRY, PALE, SLATE, surface
from art import BRASS, TRIM, Material, Mesh
from plan import STAIR_EDGE


FLIGHT = "hvd_flight"
PAVING = "hvd_flagstone"
TERRACE = "hvd_stcourt"
AIR = "hvd_air"
WIDE = ("hvd_wide_l", "hvd_wide_r")
# The original terrace tiles have their floor five metres above the tile origin.
LOW, HIGH = 5.0, 10.0
START, END = -4.36, 4.36
INNER, OUTER = 3.26, 3.78
COUNT = 20
COURT_STONE = Material((.79,.82,.90),'hvd_paving')


def stair_model():
    mesh = Mesh()
    surface(mesh, SLATE, -5, -5, 5, START, LOW, .30)
    surface(mesh, SLATE, -5, END, 5, 5, HIGH, .30)
    run = (END - START) / COUNT
    rise = (HIGH - LOW) / COUNT
    for i in range(COUNT):
        y = START + i * run
        z = LOW + i * rise
        mesh.box(MASONRY if i % 5 else LIMESTONE, 0, y + run/2, z - .25, INNER*2, run+.008, .25)
        mesh.box(TRIM, 0, y + .028, z - .045, INNER*2, .067, .046)
    # Close the last riser where the flight meets the upper landing.
    mesh.polygon(MASONRY, ((-INNER, END, HIGH-rise), (INNER, END, HIGH-rise),
                           (INNER, END, HIGH), (-INNER, END, HIGH)),
                 ((0, 0), (.6*INNER, 0), (.6*INNER, .3*rise), (0, .3*rise)))
    for side in (-1,1):
        x = side * (INNER + OUTER) / 2
        x0, x1 = sorted((side * INNER, side * 5))
        center = (x0 + x1) / 2
        mesh.box(MASONRY,center,2.22,LOW-.11,x1-x0,4.44,HIGH-LOW+.11)
        mesh.box(SLATE,center,-2.21,LOW-.32,x1-x0,4.42,.32)
        # Carved blocks support the stair and carry a continuous rail above it.
        for i in range(5):
            y0 = -4.97 + i*1.97
            y1 = y0 + 1.93
            z0 = LOW + i
            mesh.box(MASONRY, x, (y0+y1)/2, LOW-.22, OUTER-INNER, y1-y0, z0-LOW+.80)
        for y,z in ((-4.76,LOW),(.0,LOW+2.5),(4.76,HIGH)):
            mesh.box(BASALT,x,y,z-.05,.72,.66,.23)
            mesh.box(LIMESTONE,x,y,z+.17,.51,.54,.77)
            mesh.box(TRIM,x,y,z+.91,.62,.62,.14)
        mesh.tube(TRIM,(x,-4.6,LOW+.87),(x,4.6,HIGH+.87),.185,sides=6)
        mesh.tube(BRASS,(x,-4.6,LOW+1.00),(x,4.6,HIGH+1.00),.044,sides=6)
        mesh.tube(PALE,(x,-4.47,LOW+1.045),(x,4.47,HIGH+1.045),.022,sides=6)
    return mesh


@dataclass(frozen=True)
class TerraceTiles:
    flight: int
    paving: int
    court: int
    air: int
    wide: tuple[int, int]


def wide_stair(side):
    """One half of a stair, with the central joint open to the other half."""
    mesh = Mesh()
    inner = side*(5.0-STAIR_EDGE)
    edge = side*5.0
    xmin, xmax = sorted((inner, -edge))
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
    for y in range(size):
        for x in range(size):
            color = (84,101,124)
            if is_flight and 10 < x < 53:
                color = (129,150,184) if y%4 else (91,115,151)
            if is_flight and x in (10,53):
                color = (151,164,199)
            if not is_flight and (y%16==0 or (x+8*(y//16))%20==0):
                color = (74,88,112)
            if empty:
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
    raw = raw[:found.start(2)] + str(number+6+len(workshop)) + raw[found.end(2):]
    cursor = re.search(r"(?im)^\[GROUPS\]",raw).start()
    ids = TerraceTiles(number,number+1,number+2,number+3,(number+4,number+5))
    rows = (set_row(ids.flight,FLIGHT,1) + set_row(ids.paving,PAVING,0) +
            set_row(ids.court,TERRACE,0) + set_row(ids.air,AIR,0,"chasm") +
            ''.join(set_row(i,name,1) for i,name in zip(ids.wide,WIDE,strict=True)))
    workshop_ids = {}
    for index,(cell,(name,_)) in enumerate(workshop.items(),number+6):
        workshop_ids[cell] = index,0
        rows += set_row(index,name,0)
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
        **as_tile(FLIGHT,stair_model(),floor_mesh(),True),
        **as_tile(PAVING,paving,flat),
        **as_tile(TERRACE,court,flat),
        **as_tile(AIR,Mesh(),void,empty=True),
    }
    for name, side in zip(WIDE,(-1,1),strict=True):
        resources.update(as_tile(name,*wide_stair(side),True))
    for _,pieces in workshop.values():
        resources.update(pieces)
    return ids, workshop_ids, resources
