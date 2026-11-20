"""Draw the route overview and local plans for an exported Hvězdárna module."""

from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from math import atan2, cos, hypot, radians, sin
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from aurora import TYPE, erf_index, gff_decode
from interiors import PLANS
from layout import areas
from routes import THRESHOLDS


WIDTH, HEIGHT = landscape(A3)
BG = '#10222d'
PANEL = '#193440'
RULE = '#31505b'
TEXT = '#f0f2eb'
SUB = '#afc4cb'
GOLD = '#eed08d'
BLUE = '#83cbd6'
RETURN = '#e7a696'
MAIN = ('rim', 'halls', 'works', 'dome', 'steps', 'walks', 'gate', 'top')
TITLES = {
    'rim': ('Výstupová římsa', 'Nocleh a rozpis hlídky'),
    'halls': ('Chodby clon', 'Příjmová síň, paprsková chodba a archiv'),
    'works': ('Dílny', 'Dolní dílna, servisní lávka a Pečeť kotvy'),
    'dome': ('Kopule', 'Refraktor a clony'),
    'steps': ('Schody do nebe', 'Tři ramena a bouřná podesta'),
    'walks': ('Visuté ochozy', 'Dvě ramena a horní výstup k bráně'),
    'gate': ('Předbraní', 'Dvůr pečetí a Brána tří paprsků'),
    'top': ('Poslední stupeň', 'Ithren a návratová lucerna'),
    'study': ('Pracovna správkyně', 'Skrytá komora za archivem'),
    'eave': ('Římsa pod schody', 'Spodní servisní lávka se dvěma vstupy'),
}

# Both directions carry the same number on the overview and on the floor plans.
LINKS = (
    ('rim_halls','halls_rim'), ('halls_works','works_halls'), ('works_dome','dome_works'),
    ('dome_steps','steps_dome'), ('steps_walks','walks_steps'), ('walks_gate','gate_walks'),
    ('gate_top','top_gate'), ('halls_dome','dome_halls'), ('works_rim','rim_works'),
    ('halls_study','study_halls'), ('study_dome','dome_study'), ('steps_eave','eave_steps'),
    ('steps_eaveup','eave_up'), ('gate_dome','dome_short'), ('top_rim',),
)
REQUIREMENTS = {
    'hvd_aligned': 'Seřídit refraktor v kopuli',
    'hvd_gate_open': 'Otevřít Bránu tří paprsků',
    'hvd_work_link': 'Odjistit z dílen',
    'hvd_study_open': 'Uvolnit západku v archivu',
    'hvd_study_link': 'Odjistit z pracovny',
    'hvd_eave_open': 'Uvolnit táhlo pod opěrou schodů',
    'hvd_shortcut': 'Odjistit z Předbraní',
    'hvd_won': 'Uzavřít lucernu po střetu s Ithrenem',
}


@dataclass(frozen=True)
class Passage:
    source: str
    target: str
    x: float
    y: float
    required: str


def read_module(path):
    resources = erf_index(path)

    def read(name, kind):
        return gff_decode(resources[name, TYPE[kind]], 'cp1250')

    info = read('module', 'ifo')
    names = [a.value('Area_Name') for a in info.value('Mod_Area_list')]
    waypoints, triggers = {}, {}
    for name in names:
        area = name.removeprefix('hvd_')
        git = read(name, 'git')
        for spot in git.value('WaypointList'):
            waypoints[spot.value('Tag')] = area
        for entry in git.value('TriggerList'):
            tag = entry.value('Tag')
            if tag.startswith('hvt_'):
                triggers[tag[4:]] = area, entry
    if set(triggers) != {key for link in LINKS for key in link}:
        raise ValueError('The map and module have different sets of threshold tags')
    passages = {}
    for key, (area, entry) in triggers.items():
        settings = {v.value('Name'): v.value('Value') for v in entry.value('VarTable')}
        x,y = entry.value('XPosition'),entry.value('YPosition')
        sill = THRESHOLDS[key]
        if hypot(sill.x-x,sill.y-y) > .01:
            raise ValueError(f'Use the mapping sources for this module version: {key}')
        passages[key] = Passage(area,waypoints[settings['target']],x,y,settings.get('require',''))
    for a,b in (link for link in LINKS if len(link) == 2):
        if passages[a].target != passages[b].source or passages[b].target != passages[a].source:
            raise ValueError(f'Expected reciprocal routes: {a} and {b}')
    return info.value('Mod_Version'), passages


def text(c, x, y, value, size=12, color=TEXT, bold=False, centered=False):
    c.setFont('MapBold' if bold else 'MapText', size)
    c.setFillColor(HexColor(color))
    (c.drawCentredString if centered else c.drawString)(x,y,value)


def fill(c, color):
    c.setFillColor(HexColor(color))


def stroke(c, color, width):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)


def page(c, title, sub, index, version):
    fill(c,BG)
    c.rect(0,0,WIDTH,HEIGHT,fill=1,stroke=0)
    text(c,47,HEIGHT-61,title,31,bold=True)
    text(c,48,HEIGHT-85,sub,12,SUB)
    text(c,WIDTH-185,HEIGHT-59,f'VERZE {version}   /   {index:02}–03',11,GOLD,True)
    stroke(c,RULE,.8)
    c.line(46,HEIGHT-99,WIDTH-46,HEIGHT-99)


def badge(c, x, y, label, color):
    fill(c,BG)
    stroke(c,color,1)
    c.circle(x,y,9.0,fill=1,stroke=1)
    text(c,x,y-3.3,label,8.2,color,True,True)


def arrow(c, tail, head, color):
    phi = atan2(head[1]-tail[1],head[0]-tail[0])
    x,y = head
    p = c.beginPath()
    p.moveTo(x,y)
    for a in (phi-.49,phi+.49):
        p.lineTo(x-8*cos(a),y-8*sin(a))
    p.close()
    fill(c,color)
    c.drawPath(p,fill=1,stroke=0)


def connection(c, points, color, marker, badge_position, *, onward_only=False):
    stroke(c,color,2.0 if color==GOLD else 1.45)
    if color != GOLD:
        c.setDash(5,3)
    p=c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    c.drawPath(p)
    c.setDash()
    arrow(c,points[-2],points[-1],color)
    if not onward_only:
        arrow(c,points[1],points[0],color)
    badge(c,*badge_position,marker,color)


def overview(c, version):
    page(c,'Hvězdárna druhého nebe',
         'Mapa spojení mezi lokacemi. Čísla vedou ke stejným prahům v půdorysech.',1,version)
    cx, west, east = 596,481,711
    rows={key:121+83*i for i,key in enumerate(MAIN)}
    for i,(a,b) in enumerate(zip(MAIN,MAIN[1:]),1):
        y,y2=rows[a]+24,rows[b]-24
        connection(c,((cx,y),(cx,y2)),GOLD,f'{i:02}',(cx,(y+y2)/2))
    text(c,612,411,'Seřídit refraktor',10,GOLD)
    text(c,612,661,'Otevřít Bránu tří paprsků',10,GOLD)
    connections=(
        ('08',((481,204),(448,204),(448,370),(481,370)),(448,259)),
        ('09',((711,287),(778,287),(778,121),(711,121)),(778,170)),
        ('10',((481,191),(404,191),(404,287),(382,287)),(404,228)),
        ('11',((382,313),(404,313),(404,383),(481,383)),(404,349)),
        ('12',((481,442),(415,442),(415,450),(382,450)),(433,442)),
        ('13',((481,467),(415,467),(415,476),(382,476)),(433,467)),
        ('14',((711,619),(863,619),(863,370),(711,370)),(863,541)),
    )
    for marker, points, pos in connections:
        connection(c,points,BLUE,marker,pos)
    connection(c,((711,702),(1091,702),(1091,105),(711,105)),RETURN,'15',(1091,541),onward_only=True)
    for x,y,label in (
        (790,166,'Otevřít z dílen'),(197,373,'08  Chodbami přímo do kopule'),
        (197,357,'Pečeť kotvy je v dílnách.'),(879,539,'Otevřít z Předbraní'),
        (899,522,'do kopule a zpět'),(916,574,'Po střetu návrat do noclehu'),
        (197,250,'10  Otevřít z archivu'),(197,236,'11  Odjistit v pracovně'),
        (197,410,'12  Vstup u paty schodů'),(197,396,'13  Vstup z bouřné podesty'),
    ):
        text(c,x,y,label,10,SUB)
    nodes = [(key,cx,y,230) for key,y in rows.items()] + [('study',275,300,214),('eave',275,463,214)]
    for key,x,y,w in nodes:
        fill(c,PANEL)
        stroke(c,GOLD if key in ('rim','top') else RULE,1)
        c.roundRect(x-w/2,y-24,w,48,7,fill=1,stroke=1)
        title,detail=TITLES[key]
        text(c,x,y+3,title,15,bold=True,centered=True)
        text(c,x,y-13,detail,9.0,SUB,centered=True)
    stroke(c,RULE,.75)
    c.line(46,75,WIDTH-46,75)
    for i,(label,color) in enumerate((('Trasa výpravy',GOLD),('Odbočka nebo zkratka',BLUE),
                                       ('Jednosměrný návrat',RETURN))):
        x=48+241*i
        stroke(c,color,2)
        c.line(x,53,x+30,53)
        text(c,x+38,49,label,11,TEXT)
    text(c,807,48,'Přehled spojení je schematický.',10,SUB)
    c.showPage()


def floor(c, plan, x0, y0, scale):
    if plan.key in PLANS:
        rooms=PLANS[plan.key][1]
    else:
        rooms=[tuple(v*10 for v in rect) for rect in plan.rooms]
        for (x,y),(tile,_) in plan.special_tiles.items():
            if tile in (895,818):
                rooms.append((x*10+3.05,y*10,x*10+6.95,(y+1)*10))
    xs=sorted({edge for left,_,right,_ in rooms for edge in (left,right)})
    ys=sorted({edge for _,low,_,high in rooms for edge in (low,high)})
    cells={}
    for i,(left,right) in enumerate(zip(xs,xs[1:])):
        for j,(low,high) in enumerate(zip(ys,ys[1:])):
            mid_x,mid_y=(left+right)/2,(low+high)/2
            if any(l<mid_x<r and b<mid_y<t for l,b,r,t in rooms):
                cells[i,j]=(left,low,right,high)
    def pixel(x,y):
        return x0+x*scale,y0+y*scale
    fill(c,'#567781' if plan.key in PLANS else '#506b72')
    for left,low,right,high in cells.values():
        c.rect(*pixel(left,low),(right-left)*scale,(high-low)*scale,stroke=0,fill=1)
    stroke(c,'#93acb0',.76)
    for (i,j),(l,b,r,t) in cells.items():
        for other,a,z in (((i-1,j),(l,b),(l,t)),((i+1,j),(r,b),(r,t)),
                          ((i,j-1),(l,b),(r,b)),((i,j+1),(l,t),(r,t))):
            if other not in cells:
                c.line(*pixel(*a),*pixel(*z))
    for row, columns in plan.stair_columns.items():
        fill(c,'#293e49')
        c.rect(*pixel(0,row*10),plan.width*10*scale,10*scale,stroke=0,fill=1)
        for col in columns:
            x=col*10+5
            fill(c,'#607d89')
            c.rect(*pixel(x-3.25,row*10),6.5*scale,10*scale,stroke=0,fill=1)
            stroke(c,'#b4c7c8',.5)
            for i in range(1,7):
                y=row*10+i*10/7
                c.line(*pixel(x-3.25,y),*pixel(x+3.25,y))
    return pixel


def atlas(c, plans, passages, keys, index, version):
    page(c,'Půdorysy a směry',
         'Sever je nahoře. Šipka míří z lokace přes práh. Kruh označuje spojení z hlavní mapy.',index,version)
    cols,card_w,card_h=3,348,323
    ids={key:f'{i:02}' for i, link in enumerate(LINKS,1) for key in link}
    # Keep labels next to their exits when two doors share a small room.
    shifts={'halls_study':(13,7),'dome_steps':(0,5),'works_rim':(9,-3),'gate_top':(0,7),
            'steps_eaveup':(11,-2),'dome_study':(14,-7),'top_rim':(0,9)}
    for i,key in enumerate(keys):
        plan=plans[key]
        x=48+(i%cols)*375
        y=49+(1-i//cols)*348
        fill(c,PANEL); stroke(c,RULE,.8)
        c.roundRect(x,y,card_w,card_h,8,stroke=1,fill=1)
        text(c,x+13,y+298,TITLES[key][0],16,bold=True)
        text(c,x+13,y+279,TITLES[key][1],9.8,SUB)
        scale=min(264/(plan.width*10),171/(plan.height*10))
        p=floor(c,plan,x+(card_w-plan.width*10*scale)/2,y+102,scale)
        local=[(tag,door) for tag,door in passages.items() if door.source==key]
        for tag,door in local:
            facing=radians(THRESHOLDS[tag].facing)
            dx,dy=cos(facing),sin(facing)
            px,py=p(door.x,door.y)
            color=GOLD if not door.required else BLUE
            stroke(c,color,2)
            c.line(px-dy*4,py+dx*4,px+dy*4,py-dx*4)
            tip=(px+dx*12,py+dy*12)
            c.line(px,py,*tip)
            arrow(c,(px,py),tip,color)
            xx,yy=shifts.get(tag,(0,0))
            badge(c,px+dx*18+xx-dy*7,py+dy*18+yy+dx*7,ids[tag],color)
        if key=='rim':
            px,py=p(23,16)
            fill(c,GOLD)
            c.circle(px,py,3.25,fill=1,stroke=0)
            text(c,px+7,py-3,'Start',8,GOLD)
        stroke(c,SUB,.8)
        c.line(x+15,y+112,x+15+10*scale,y+112)
        text(c,x+15,y+119,'10 m',7.6,SUB)
        text(c,x+card_w-30,y+252,'N ↑',8.5,SUB)
        for n,(tag,door) in enumerate(local):
            label=TITLES[door.target][0]
            if tag=='eave_steps': label='Pata Schodů do nebe'
            if tag=='eave_up': label='Bouřná podesta'
            if tag.startswith('steps_eave'): label='Spodní římsa · '+('horní' if tag.endswith('up') else 'dolní')+' vstup'
            text(c,x+13,y+83-n*15,ids[tag],9.5,BLUE if door.required else GOLD,True)
            text(c,x+39,y+83-n*15,label,9.5)
            if door.required:
                text(c,x+card_w-19,y+83-n*15,'*',10,BLUE)
    x=798
    text(c,x,339,'Podmínky přechodů',17,bold=True)
    text(c,x,320,'* Platí ve směru označeném v půdorysu.',10,SUB)
    for n,(flag,label) in enumerate(REQUIREMENTS.items()):
        links=sorted({ids[tag] for tag,door in passages.items() if door.required==flag})
        if links:
            y=293-22*n
            text(c,x,y,' / '.join(links),10,BLUE,True)
            text(c,x+50,y,label,10,TEXT)
    c.showPage()


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--module',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--font-dir',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    args=parser.parse_args()
    for name,file in (('MapText','DejaVuSans.ttf'),('MapBold','DejaVuSans-Bold.ttf')):
        pdfmetrics.registerFont(TTFont(name,str(args.font_dir/file)))
    version,passages=read_module(args.module)
    plans={zone.key[4:]:zone for zone in areas(defaultdict(int),99000)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    c=Canvas(str(args.output),pagesize=(WIDTH,HEIGHT),invariant=1)
    c.setTitle('Hvězdárna druhého nebe — mapa průchodů')
    overview(c,version)
    atlas(c,plans,passages,('rim','halls','works','dome','study'),2,version)
    atlas(c,plans,passages,('steps','walks','gate','top','eave'),3,version)
    c.save()


if __name__=='__main__':
    main()
