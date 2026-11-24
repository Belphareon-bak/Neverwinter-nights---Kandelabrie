"""Two circular sanctuaries built with the summit temple's Doric details."""

from math import cos, hypot, radians, sin, tau

from architecture import INDIGO, LIMESTONE, MASONRY, WARM
from art import BRASS, DARK, GILT, TRIM, Mesh
from temple import MARBLE, ROOF_TILE, doric_column


COLUMNS = (-66,-31,4,39,74,109,144,179,214,247)
POST_RADIUS = 4.25
COLUMN_SCALE = .596
ROOF_EDGE = 5.19
BACK_RADIUS = 4.75


def polar(radius, angle, z=0.0):
    theta=radians(angle)
    return radius*cos(theta),radius*sin(theta),z


def border_segments():
    return [(polar(BACK_RADIUS,angle)[:2],polar(BACK_RADIUS,angle+10)[:2])
            for angle in range(-66,244,10)]


def footprint():
    columns=[]
    half=.90*COLUMN_SCALE
    for angle in COLUMNS:
        x,y,_=polar(POST_RADIUS,angle)
        columns.append(((x-half,y-half),(x+half,y-half),(x+half,y+half),(x-half,y+half)))
    for (x,y),(u,v) in border_segments():
        length=hypot(u-x,v-y)
        dx,dy=(y-v)*.25/length,(u-x)*.25/length
        columns.append(((x-dx,y-dy),(u-dx,v-dy),(u+dx,v+dy),(x+dx,y+dy)))
    return tuple(columns)


def floor_ring(mesh):
    mesh.disc(MASONRY,(0,0,-.18),(0,0,.027),4.97,sides=44)
    mesh.disc(MARBLE,(0,0,.027),(0,0,.038),4.74,sides=44)
    for radii,color in (((3.56,.10),DARK),((3.71,.075),BRASS),((4.72,.11),TRIM)):
        mesh.ring(color,*radii,.043,sides=66)
    for angle in (-117,-63):
        x,y,_=polar(5.02,angle)
        mesh.box(LIMESTONE,x,y,-.17,.72,.66,.218,tile_uv=.31)


def colonnade(mesh):
    column=doric_column()
    for angle in COLUMNS:
        x,y,_=polar(POST_RADIUS,angle)
        for material,faces in column.faces.items():
            for points,uv in faces:
                mesh.polygon(material,[(x+a*COLUMN_SCALE,y+b*COLUMN_SCALE,.035+c*COLUMN_SCALE)
                                       for a,b,c in points],uv)
    for (x,y),(u,v) in border_segments():
        mesh.tube(MASONRY,(x,y,.36),(u,v,.36),.31,sides=6)
        mesh.tube(LIMESTONE,(x,y,.72),(u,v,.72),.17,sides=6)
        mesh.tube(BRASS,(x,y,.83),(u,v,.83),.048,sides=6)


def canopy(mesh,tint):
    for i in range(40):
        a,b=9*i,9*(i+1)
        for z,radius,material,trim in ((3.42,4.56,MARBLE,.24),(3.67,4.64,tint,.21),
                                        (3.91,4.75,LIMESTONE,.13),(4.06,5.03,BRASS,.068)):
            mesh.tube(material,polar(radius,a,z),polar(radius,b,z),trim,sides=6)
        points=(polar(ROOF_EDGE,a,4.115),polar(ROOF_EDGE,b,4.115),
                polar(1.89,b,5.32),polar(1.89,a,5.32))
        mesh.polygon(ROOF_TILE,points)
        mesh.polygon(TRIM,points[::-1])
        mesh.tube(TRIM,*points[1:3],.053,sides=5)
        mesh.tube(LIMESTONE,points[3],points[2],.115,sides=7)
        if i%2==0:
            x,y,_=polar(4.81,a)
            mesh.box(MARBLE,x,y,3.62,.13,.13,.277)
    mesh.tube(BRASS,(-1.90,-4.61,3.995),(1.90,-4.61,3.995),.095,sides=8)


def crest(mesh,tint,lamp):
    face=-4.78
    points=((-1.74,face,4.005),(1.74,face,4.005),(0,face,5.13))
    mesh.polygon(tint,points)
    mesh.polygon(tint,points[::-1])
    for p,q in zip(points,points[1:]+points[:1]):
        mesh.tube(LIMESTONE,p,q,.103,sides=7)
    if lamp:
        mesh.disc(BRASS,(0,face,4.39),(0,face-.16,4.39),.264,sides=16)
        mesh.disc(GILT,(0,face-.15,4.39),(0,face-.185,4.39),.196,sides=16)
    else:
        mesh.tube(GILT,(0,face-.115,4.19),(0,face-.115,4.56),.046,sides=7)
        mesh.polygon(GILT,((-.134,face-.15,4.48),(.134,face-.15,4.48),(0,face-.15,4.78)))


def tholos(lamp=False):
    mesh=Mesh()
    tint=WARM if lamp else INDIGO
    floor_ring(mesh)
    colonnade(mesh)
    canopy(mesh,tint)
    crest(mesh,tint,lamp)
    return mesh


SCENERY = {
    'hvd_tholos_k': ('Dórská svatyně Kopí',tholos),
    'hvd_tholos_l': ('Dórská svatyně Lucerny',lambda: tholos(True)),
}
