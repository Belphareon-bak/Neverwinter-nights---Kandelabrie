"""Frozen topsoil, climbable ledges and cliffs for the Visuté ochozy."""

from collections import Counter, defaultdict
from functools import lru_cache
from math import ceil, cos, hypot, sin, tau
from random import Random
from struct import pack

from architecture import BASALT, LIMESTONE
from art import BRASS, DARK, Material, Mesh
from plan import JOINS, SKY_OPENING, TILE, WALKS, WALK_BANDS, WALK_HEIGHTS, ZONES, height_at, linear


GROUND = Material((.89,.91,.94),'hvd_soil')
TRACK = Material((.89,.90,.93),'hvd_packed')
FROST_GRASS = Material((.55,.53,.46),'hvd_packed',shadow=0)
STONE = Material((.83,.86,.91),'hvd_rough')
EDGE_TRIM = Material((.68,.74,.79),'hvd_rough')
HARD_STONE = Material((.57,.64,.72),'hvd_rough')


def textures():
    return {
        'hvd_soil.tga': frozen_soil(228,(114,105,92),.36),
        'hvd_packed.tga': frozen_soil(183,(93,87,78),.68),
    }


def frozen_soil(seed,earth,crust_threshold):
    size=256
    rng=Random(seed)
    grids={n:[[rng.random() for _ in range(n)] for _ in range(n)] for n in (4,11,28)}

    def noise(x,y,n):
        u,v=x*n/size,y*n/size
        i,j=int(u),int(v)
        u,v=u-i,v-j
        u,v=u*u*(3-2*u),v*v*(3-2*v)
        grid=grids[n]
        a,b=grid[j][i],grid[j][(i+1)%n]
        c,d=grid[(j+1)%n][i],grid[(j+1)%n][(i+1)%n]
        return (a+(b-a)*u)*(1-v)+(c+(d-c)*u)*v

    pixels=bytearray()
    frost=(176,185,190)
    for y in range(size):
        for x in range(size):
            large,small,grain=(noise(x,y,n) for n in (4,11,28))
            crust=min(.83,max(0,(.54*large+.46*small-crust_threshold)*1.68))
            flecks=(grain-.5)*21+(rng.random()-.5)*20
            rgb=[max(0,min(255,int(a+(b-a)*crust+flecks))) for a,b in zip(earth,frost)]
            pixels.extend(reversed(rgb))
    return pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,24,0)+pixels


def clip(ring,axis,value,side):
    out = []
    for a,b in zip(ring,ring[1:]+ring[:1]):
        inside_a = side*(a[axis]-value) >= 0
        inside_b = side*(b[axis]-value) >= 0
        if inside_a:
            out.append(a)
        if inside_a != inside_b:
            t = (value-a[axis])/(b[axis]-a[axis])
            p = list(a[i]+t*(b[i]-a[i]) for i in range(2))
            p[axis] = value
            out.append(tuple(p))
    return tuple(dict.fromkeys(tuple(round(k,4) for k in point) for point in out))


Y_CUTS = sorted({y for band in WALK_BANDS for y,_,_ in band} |
                {y for y,_ in WALK_HEIGHTS} | set(range(0,111,10)))


def sides(band,y):
    for (y0,l0,r0),(y1,l1,r1) in zip(band,band[1:]):
        if y0<=y<=y1:
            return linear(y,y0,y1,l0,l1),linear(y,y0,y1,r0,r1)
    raise ValueError(y)


def edges(ring):
    return zip(ring,ring[1:]+ring[:1])


def edge_key(a,b):
    return tuple(sorted((a,b)))


@lru_cache(maxsize=1)
def terrain():
    """Split the actual bank outlines on the Toolset grid and stitch the walkmesh."""
    patches = defaultdict(list)
    divisions = {
        y: sorted({round(x,4) for band in WALK_BANDS if band[0][0]<=y<=band[-1][0]
                   for x in sides(band,y)})
        for y in Y_CUTS
    }
    counts = Counter()
    for bottom,top in zip(Y_CUTS,Y_CUTS[1:]):
        row = int(bottom//TILE)
        for band in WALK_BANDS:
            if not band[0][0]<=bottom<top<=band[-1][0]:
                continue
            l,r = sides(band,bottom)
            lt,rt = sides(band,top)
            strip = ((l,bottom),(r,bottom),(rt,top),(lt,top))
            for col in range(int(min(l,lt)//TILE),min(8,int(max(r,rt)//TILE)+1)):
                ring = clip(clip(strip,0,col*TILE,1),0,(col+1)*TILE,-1)
                if len(ring)<3:
                    continue
                stitched = []
                for a,b in edges(ring):
                    stitched.append(a)
                    if a[1]==b[1]:
                        left,right=sorted((a[0],b[0]))
                        xs = [x for x in divisions[a[1]] if left<x<right]
                        stitched.extend((x,a[1]) for x in (xs if a[0]<b[0] else xs[::-1]))
                patches[col,row].append(tuple(stitched))
                counts.update(edge_key(a,b) for a,b in edges(tuple(stitched)))
    return dict(patches), {key for key,count in counts.items() if count==1}


def exposed(a,b):
    """Leave the companion passage open at each authored threshold."""
    for join in JOINS:
        if 'walks' not in (join.first,join.second):
            continue
        x,y=join.point('walks')
        half = SKY_OPENING*.5
        if join.heading('walks') in (0,180) and a[0]==b[0]==x:
            axis,center=1,y
        elif join.heading('walks') in (90,270) and a[1]==b[1]==y:
            axis,center=0,x
        else:
            continue
        low,high=sorted((a[axis],b[axis]))
        positions=(low,max(low,min(high,center-half)),min(high,max(low,center+half)),high)
        if a[axis]>b[axis]:
            positions=positions[::-1]
        for u,v in (positions[:2],positions[2:]):
            if abs(u-v)>.001:
                yield ((x,u),(x,v)) if axis else ((u,y),(v,y))
        return
    yield a,b


def band_height(y):
    return height_at(WALK_HEIGHTS,y)


def trail_strips(path,width):
    normals=[]
    for (x,y),(nx,ny) in zip(path,path[1:]):
        length=hypot(nx-x,ny-y)
        normals.append(((y-ny)/length,(nx-x)/length))
    borders=[]
    for i,(x,y) in enumerate(path):
        a=normals[max(0,i-1)]
        b=normals[min(len(normals)-1,i)]
        dx,dy=a[0]+b[0],a[1]+b[1]
        offset=width/(dx*b[0]+dy*b[1])
        borders.append(((x+dx*offset,y+dy*offset),(x-dx*offset,y-dy*offset)))
    detailed=[]
    for (a,b),(c,d) in zip(borders,borders[1:]):
        steps=max(1,ceil(hypot(c[0]-a[0],c[1]-a[1])/1.8))
        for step in range(steps):
            t=step/steps
            left=tuple(u+(v-u)*t for u,v in zip(a,c))
            right=tuple(u+(v-u)*t for u,v in zip(b,d))

            def scuff(p,q):
                variation=.07*sin(p[0]*1.38+p[1]*.91)+.04*cos(p[1]*2.51)
                return tuple(u+(v-u)*variation for u,v in zip(p,q))

            detailed.append((scuff(left,right),scuff(right,left)))
    detailed.append(borders[-1])
    return tuple((a,b,d,c) for (a,b),(c,d) in zip(detailed,detailed[1:]))


PATHS = tuple(shape for path in WALKS['walks'] for shape in trail_strips(path,1.57))
PATH_EDGES = tuple((start,end) for path in WALKS['walks'] for start,end in zip(path,path[1:]))


def trail_distance(x,y):
    distances=[]
    for (u,v),(a,b) in PATH_EDGES:
        dx,dy=a-u,b-v
        t=max(0,min(1,((x-u)*dx+(y-v)*dy)/(dx*dx+dy*dy)))
        distances.append(hypot(x-u-t*dx,y-v-t*dy))
    return min(distances)


def ledge_tile(col,row):
    patches,boundary=terrain()
    rings=patches[col,row]
    cx,cy=TILE*(col+.5),TILE*(row+.5)
    mesh=Mesh()
    vertices=[]
    index={}
    triangles=[]

    def point(p,offset=0):
        x,y=p
        return (round(x-cx,4),round(y-cy,4),round(band_height(y)+offset,4))

    def vertex(p):
        p=point(p)
        if p not in index:
            index[p]=len(vertices)
            vertices.append(p)
        return index[p]

    for ring in rings:
        inner=tuple(sum(p[i] for p in ring)/len(ring) for i in range(2))
        c=vertex(inner)
        for a,b in edges(ring):
            triangles.append((c,vertex(a),vertex(b)))
            mesh.polygon(GROUND,(point(inner),point(a),point(b)),
                         [(x*.17,y*.17) for x,y in (inner,a,b)])
            if edge_key(a,b) in boundary:
                for left,right in exposed(a,b):
                    cliff(mesh,left,right,point)

    for trail in PATHS:
        clipped=clip(clip(trail,0,cx-5,1),0,cx+5,-1)
        if len(clipped)<3:
            continue
        for low,high in zip(Y_CUTS,Y_CUTS[1:]):
            if low//TILE!=row:
                continue
            ribbon=clip(clip(clipped,1,low,1),1,high,-1)
            if len(ribbon)>=3:
                mesh.polygon(TRACK,[point(p,.014) for p in ribbon],
                             [(x*.42,y*.42) for x,y in ribbon])
    dress_ground(mesh,col,row,point)
    return mesh,(vertices,triangles)


def dress_ground(mesh,col,row,point):
    rng=Random(475+col+row*17)
    floor=ZONES['walks']
    for _ in range(32):
        x,y=(col+rng.random())*TILE,(row+rng.random())*TILE
        if y<11 or y>=102 or 63<y<70 or not all(
            floor.contains(x+dx,y+dy) for dx,dy in ((0,0),(-.43,0),(.43,0),(0,-.43),(0,.43))
        ):
            continue
        offset=trail_distance(x,y)
        if 1.60<offset<1.92 and rng.random()<.54:
            scale=rng.uniform(.12,.24)
            corners=[(x+scale*cos(i*tau/6),y+scale*.62*sin(i*tau/6)) for i in range(6)]
            top=point((x,y),rng.uniform(.045,.112))
            for a,b in edges(corners):
                mesh.polygon(STONE,(top,point(a,.012),point(b,.012)))
        elif offset>2.20 and rng.random()<.43:
            for i in range(3):
                direction=rng.uniform(0,tau)
                dx,dy=.10*cos(direction),.10*sin(direction)
                root=(x+i*.07,y-i*.04)
                a,b=point((root[0]-dx,root[1]-dy)),point((root[0]+dx,root[1]+dy))
                top=point((root[0]+dy*.9,root[1]-dx*.9),rng.uniform(.18,.39))
                mesh.polygon(FROST_GRASS,(a,b,top))
                mesh.polygon(FROST_GRASS,(top,b,a))


def cliff(mesh,start,end,point):
    a,b=point(start),point(end)
    x0,y0=start
    x1,y1=end
    length=hypot(x1-x0,y1-y0)
    if length<.015:
        return

    def profile(p,xy):
        x,y=xy
        return (p,(p[0]+.36*sin(x*.39+y*.24),p[1]+.35*cos(x*.27-y*.17),p[2]-1.02),
                (p[0]+2.1*sin(x*.28+y*.19),p[1]+1.58*cos(x*.24-y*.17),p[2]-5.6-1.5*cos(y*.33+x)),
                (p[0]+1.02*sin(y*.19),p[1]+1.82*cos(x*.16),p[2]-15.5-2.8*sin(x*.25+y*.34)))

    sides_a,sides_b=profile(a,start),profile(b,end)
    for i,stone in enumerate((EDGE_TRIM,STONE,HARD_STONE)):
        face=(sides_a[i],sides_a[i+1],sides_b[i+1],sides_b[i])
        uv=((0,face[0][2]*.29),(0,face[1][2]*.29),(length*.33,face[2][2]*.29),
            (length*.33,face[3][2]*.29))
        mesh.polygon(stone,face,uv)
    # The footings straddle the lip and are set into the rock below it.
    nx,ny=(y0-y1)/length,(x1-x0)/length
    c=(a[0]+nx*.15,a[1]+ny*.15,a[2])
    d=(b[0]+nx*.15,b[1]+ny*.15,b[2])
    for height,radius,stone in ((.21,.105,BASALT),(.57,.046,DARK),(.96,.074,EDGE_TRIM)):
        mesh.tube(stone,(c[0],c[1],c[2]+height),(d[0],d[1],d[2]+height),radius,sides=6)
    posts=max(1,round(length/2.4))
    for i in range(posts):
        t=(i+.50)/posts
        x,y,z=(c[k]+(d[k]-c[k])*t for k in range(3))
        mesh.box(BASALT,x,y,z-.20,.47,.47,.42)
        mesh.box(STONE,x,y,z+.19,.25,.25,.78)
        mesh.box(LIMESTONE,x,y,z+.88,.33,.34,.17)
        mesh.box(BRASS,x,y,z+.72,.275,.275,.072)
    if length>.46:
        for t in (.18,.82):
            x,y,z=(c[k]+(d[k]-c[k])*t for k in range(3))
            mesh.box(DARK,x,y,z+.22,.087,.087,.73)


def minimap(col,row):
    size=64
    pixels=bytearray()
    for j in range(size):
        y=10*row+10*(j+.5)/size
        for i in range(size):
            x=10*col+10*(i+.5)/size
            filled=ZONES['walks'].contains(x,y)
            pixels.extend((105,112,123) if filled else (5,9,15))
    return pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,24,0)+pixels
