"""Draw the north-up Toolset plan and verify a built module against it."""

from argparse import ArgumentParser
from math import isclose
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from aurora import TYPE, erf_index, gff_decode
from plan import (DIRECTIONS, JOINS, LANDING_INSET, LANDMARKS, PASSAGE_WIDTH, SECRET_LEVEL,
                  SECRET_WALKS, THRESHOLD_INSET, TILE, VERSION, WALKS, WORK_YARD_WALLS, ZONES, check_plan)

PAPER = '#f5f2e9'
INK = '#211f2e'
MUTED = '#57546a'
GRID = '#c7c3ca'
FRAME = '#777287'
ROUTE = '#805008'
ROUTE_BED = '#f0d595'
HIGH_ROUTE = '#513d82'
HIGH_BED = '#d6c6f2'
DOME_ROUTE = '#20596c'
DOME_BED = '#a9d6d9'
DOOR = '#194c67'
WALL = '#858394'
HIDDEN = '#286852'
FLOORS = {
    'camp': '#d8e2e3', 'rim': '#d8e2e3', 'halls': '#e4d8bd', 'works': '#d7dbe4', 'dome': '#e4d8bd',
    'steps': '#dcd8ec', 'walks': '#d7dcea', 'gate': '#ded8e8', 'top': '#e2d8e7',
    'study': '#cfdfd3',
}

SCALE = 3.56
ZERO = (235, 85)
SIZE = (1105, 1810)


def px(x, y):
    return ZERO[0] + x * SCALE, ZERO[1] + y * SCALE


def validate_module(path):
    resources = erf_index(path)

    def record(name, kind):
        return gff_decode(resources[name, TYPE[kind]], 'cp1250')

    info = record('module', 'ifo')
    if info.value('Mod_Version') != VERSION:
        raise ValueError(f'Expected a version {VERSION} module')
    keys = {area.value('Area_Name') for area in info.value('Mod_Area_list')}
    if keys != {f'hvd_{code}' for code in ZONES}:
        raise ValueError('The module has different areas from the Toolset plan')
    triggers, landings = {}, {}
    for key in keys:
        code = key[4:]
        area, git = record(key, 'are'), record(key, 'git')
        if (area.value('Width'), area.value('Height')) != ZONES[code].size:
            raise ValueError(f'Wrong Toolset dimensions for {code}')
        for entry in git.value('TriggerList'):
            tag = entry.value('Tag')
            if tag.startswith('hvt_'):
                if tag in triggers:
                    raise ValueError(f'Duplicate transition {tag}')
                triggers[tag] = code, entry
        for entry in git.value('WaypointList'):
            tag = entry.value('Tag')
            if tag.startswith('hvd_land_'):
                if tag in landings:
                    raise ValueError(f'Duplicate landing {tag}')
                landings[tag] = code, entry

    def coordinates(entry):
        return entry.value('XPosition'), entry.value('YPosition')

    def same(a, b):
        return all(isclose(x, y, abs_tol=.01) for x, y in zip(a, b))

    if info.value('Mod_Entry_Area') != 'hvd_camp':
        raise ValueError('The starting area must be the camp')
    elevations = {'camp': 0.0}
    for join in JOINS:
        sides = []
        for source, target, _, _, required in join.destinations():
            tag = 'hvt_' + join.route(source, target)
            destination = 'hvd_land_' + join.route(target, source)
            area, sill = triggers.pop(tag)
            zone, spawn = landings.pop(destination)
            settings = {row.value('Name'): row.value('Value') for row in sill.value('VarTable')}
            expected_facing = DIRECTIONS[join.heading(source)]
            facing = spawn.value('XOrientation'), spawn.value('YOrientation')
            outline = [(vertex.value('PointX'), vertex.value('PointY')) for vertex in sill.value('Geometry')]
            dimensions = tuple(max(axis) - min(axis) for axis in zip(*outline))
            width = dimensions[0] if expected_facing[1] else dimensions[1]
            if (area != source or zone != target or settings.get('target') != destination
                    or settings.get('require', '') != required
                    or settings.get('minimum_level', 0) != (SECRET_LEVEL if join.secret else 0)
                    or not same(coordinates(sill), join.point(source, THRESHOLD_INSET))
                    or not same(coordinates(spawn), join.point(target, LANDING_INSET))
                    or not isclose(width, PASSAGE_WIDTH, abs_tol=.01)
                    or not same(facing, expected_facing)):
                raise ValueError(f'Transition or arrival disagrees with the map at {tag}')
            sides.append((sill.value('ZPosition'), spawn.value('ZPosition')))
        first, second = sides
        if not same(first, second[::-1]):
            raise ValueError(f'Uneven landing at {join.first} / {join.second}')
        level = elevations[join.first] + first[0] - first[1]
        if not isclose(elevations.setdefault(join.second, level), level, abs_tol=.01):
            raise ValueError(f'The two paths to {join.second} finish at different heights')
    if triggers or landings:
        raise ValueError('The module contains transitions outside the drawing')


def ink(c, color, width=1):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)


def fill(c, color):
    c.setFillColor(HexColor(color))


def text(c, x, y, content, size, *, color=INK, bold=False, align='left'):
    fill(c, color)
    c.setFont('Bold' if bold else 'Regular', size)
    draw = {'left': c.drawString, 'center': c.drawCentredString, 'right': c.drawRightString}[align]
    draw(x, y, content)


def path(c, points):
    line = c.beginPath()
    line.moveTo(*points[0])
    for point in points[1:]:
        line.lineTo(*point)
    c.drawPath(line)


def arrow(c, x, y, dx, dy, color):
    tip = c.beginPath()
    tip.moveTo(x, y)
    for sign in (1, -1):
        tip.lineTo(x - 6 * dx + sign * 3 * dy, y - 6 * dy - sign * 3 * dx)
    tip.close()
    fill(c, color)
    c.drawPath(tip, stroke=0, fill=1)


def floor(c, code, secrets):
    zone = ZONES[code]
    boxes = zone.floor
    if not secrets:
        if code == 'rim':
            boxes = tuple(r for r in boxes if r[0] < 50)
        if code == 'walks':
            boxes = tuple(r for r in boxes if r[:2] != (70, 0))
    xs = sorted({v for l, _, r, _ in boxes for v in (l, r)})
    ys = sorted({v for _, lo, _, hi in boxes for v in (lo, hi)})
    cells = {}
    for i, (l, r) in enumerate(zip(xs, xs[1:])):
        for j, (b, t) in enumerate(zip(ys, ys[1:])):
            if any(left <= (l+r)/2 <= right and low <= (b+t)/2 <= high
                   for left, low, right, high in boxes):
                cells[i, j] = l, b, r, t
    fill(c, FLOORS[code])
    for l, b, r, t in cells.values():
        c.rect(*px(*zone.world(l, b)), (r-l)*SCALE, (t-b)*SCALE, fill=1, stroke=0)
    if zone.enclosed:
        fill(c, '#b6c7ce')
        for l, b, r, t in zone.enclosed:
            c.rect(*px(*zone.world(l,b)), (r-l)*SCALE, (t-b)*SCALE, fill=1, stroke=0)
    ink(c, WALL, .8)
    for (i, j), (l, b, r, t) in cells.items():
        for neighbor, p, q in (
            ((i-1,j), (l,b), (l,t)), ((i+1,j), (r,b), (r,t)),
            ((i,j-1), (l,b), (r,b)), ((i,j+1), (l,t), (r,t)),
        ):
            if neighbor not in cells:
                c.line(*px(*zone.world(*p)), *px(*zone.world(*q)))
    if code == 'works':
        ink(c,WALL,1.65)
        for a,b in WORK_YARD_WALLS:
            c.line(*px(*zone.world(*a)),*px(*zone.world(*b)))
    for row in sorted({row for _, row in zone.stairs}):
        left, bottom = px(*zone.world(0, row*TILE))
        step = TILE * SCALE
        if code != 'steps':
            fill(c, '#b0adc4')
            c.rect(left, bottom, zone.size[0]*step, step, fill=1, stroke=0)
        for xmin, xmax in zone.flights(row):
            edge = left + xmin*SCALE
            span = (xmax-xmin)*SCALE
            fill(c, '#ede8ee')
            c.rect(edge, bottom, span, step, fill=1, stroke=0)
            ink(c, FRAME, .68)
            for i in range(1, 8):
                y = bottom + i*step/8
                c.line(edge, y, edge + span, y)


def grid(c, secrets):
    for code, zone in ZONES.items():
        if code == 'study' and not secrets:
            continue
        x, y = px(*zone.world(0, 0))
        w, h = zone.size
        step = TILE * SCALE
        ink(c, GRID, .40)
        for col in range(1, w):
            c.line(x + col*step, y, x + col*step, y + h*step)
        for row in range(1, h):
            c.line(x, y + row*step, x + w*step, y + row*step)
        ink(c, FRAME, .85)
        c.setDash(3, 2)
        c.rect(x, y, w*step, h*step)
        c.setDash()
        # Height dimension line is outside the area. The halls share their
        # western boundary with the workshops, so their dimension is east.
        east = code in ('halls', 'walks')
        edge = x+w*step if east else x
        dim = edge+11 if east else edge-11
        for yy in (y, y+h*step):
            c.line(edge, yy, dim, yy)
            c.line(dim-3, yy-3, dim+3, yy+3)
        c.line(dim, y, dim, y+h*step)
        c.saveState()
        c.translate(dim-4, y+h*step*.5)
        c.rotate(90)
        text(c, 0, 0, str(h), 9, color=MUTED, align='center')
        c.restoreState()


def route(c, secrets):
    for code, walks in WALKS.items():
        if code == 'dome':
            bed, line = DOME_BED, DOME_ROUTE
        elif code in ('camp', 'rim', 'halls', 'works'):
            bed, line = ROUTE_BED, ROUTE
        else:
            bed, line = HIGH_BED, HIGH_ROUTE
        for color, width in ((bed, 8.0), (line, 2.2)):
            ink(c, color, width)
            for walk in walks:
                path(c, tuple(px(*ZONES[code].world(*point)) for point in walk))
    if secrets:
        ink(c, HIDDEN, 2.25)
        c.setDash(5,3)
        for code, walks in SECRET_WALKS.items():
            for walk in walks:
                path(c, tuple(px(*ZONES[code].world(*point)) for point in walk))
        c.setDash()
    for join in JOINS:
        if join.secret and not secrets:
            continue
        x, y = px(*join.edge)
        dx, dy = DIRECTIONS[join.facing]
        span = (PASSAGE_WIDTH / 2 + .6) * SCALE
        ink(c, PAPER, 5.4)
        c.line(x-dy*span,y+dx*span,x+dy*span,y-dx*span)
        color = HIDDEN if join.secret else DOOR
        ink(c, color, 2.4)
        c.line(x-dy*span,y+dx*span,x+dy*span,y-dx*span)
        arrow(c, x+dx*13, y+dy*13, dx, dy, color)
        arrow(c, x-dx*13, y-dy*13, -dx, -dy, color)
        bx, by = x + 21*dy, y - 21*dx
        fill(c, PAPER)
        ink(c, color, 1.0)
        c.circle(bx, by, 8.3, fill=1, stroke=1)
        text(c, bx, by-3.1, join.label, 8.3, color=color, bold=True, align='center')


def captions(c, secrets):
    detail = {
        'camp': (1.45, True, 'Zásoby a jediná stezka na římsu'),
        'rim': (4.1, True, 'Jediná veřejná brána do Zkušebny'),
        'halls': (9.4, True, 'Z jižní síně do horní dílny'),
        'works': (11.4, False, 'Zděná síň, dvory a servisní lávka'),
        'dome': (17.7, False, 'Refraktor mezi oběma okruhy'),
        'steps': (25.3, False, 'Tři ramena široká 18,2 m, dvě mezipodesty'),
        'walks': (25.3, True, 'Dva mosty a horní výstup'),
        'gate': (33.3, True, 'Místo, kde se obě ramena setkají'),
        'top': (40.6, True, 'Ithren a návratová lucerna'),
        'study': (14.35, True, 'Archiv a služební výstup 38+'),
    }
    for code, (row, east, description) in detail.items():
        if code == 'study' and not secrets:
            continue
        zone = ZONES[code]
        x, y = px((zone.origin[0] + (zone.size[0] if east else 0))*TILE, row*TILE)
        if code in ('rim', 'halls') and secrets:
            x = px(160,0)[0]
        label_x = 824 if east else 43
        ink(c, FRAME, .65)
        if east:
            c.line(x+4,y,label_x-12,y)
        else:
            c.line(label_x,y-35,x-14,y-35)
        text(c,label_x,y+8,zone.title,14.5,bold=True)
        w,h = zone.size
        text(c,label_x,y-10,f'{w} × {h} dlaždic  ·  {w*TILE} × {h*TILE} m',10.7,color=DOOR,bold=True)
        text(c,label_x,y-26,description,9.6,color=MUTED)
    for code, markers in LANDMARKS.items():
        if code == 'study' and not secrets:
            continue
        for x, y, label in markers:
            x, y = px(*ZONES[code].world(x, y))
            fill(c, INK)
            c.circle(x, y, 2.0, fill=1, stroke=0)
            shift = 11 if label in ('Clony', 'Vstupní síň') else -12
            text(c,x,y+shift,label,8.8,bold=True,align='center')


def draw(target, module, fonts, secrets):
    for name, font in (('Regular','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')):
        pdfmetrics.registerFont(TTFont(name, str(fonts/font)))
    check_plan()
    if module:
        validate_module(module)
    c = Canvas(str(target), pagesize=SIZE, invariant=1)
    c.setTitle('Hvězdárna druhého nebe — plán v dlaždicích')
    c.setLineCap(1)
    c.setLineJoin(1)
    fill(c, PAPER)
    c.rect(0, 0, *SIZE, stroke=0, fill=1)
    text(c, 43, 1765, 'Hvězdárna druhého nebe', 32, bold=True)
    subtitle = 'Dva okruhy · zděné spoje · služební štola' if secrets else 'Dva okruhy a zděné spoje'
    text(c, 44, 1735, subtitle, 15, color=MUTED)
    text(c, 1060, 1772, f'V{VERSION:02}', 13, color=DOOR, bold=True, align='right')
    arrow(c, 1050, 1739, 0, 1, INK)
    ink(c, INK, .9)
    c.line(1050, 1722, 1050, 1736)
    text(c,1050,1745,'S',10,bold=True,align='center')
    ink(c, GRID, 1)
    c.line(43, 1712, 1060, 1712)
    for code in ZONES:
        if code != 'study' or secrets:
            floor(c,code,secrets)
    grid(c,secrets)
    route(c,secrets)
    captions(c,secrets)
    for y, color, name, levels, line in (
        (346, ROUTE, 'Dolní okruh', '35–37', 'Dílny a Chodby clon uvnitř hvězdárny'),
        (1336, HIGH_ROUTE, 'Horní okruh', '38–40', 'Schody a Ochozy vedou k bráně'),
    ):
        text(c,43,y,name,16,color=color,bold=True)
        text(c,43,y-29,levels,21,color=color,bold=True)
        text(c,43,y-49,line,9.3,color=MUTED)
    ink(c, GRID, 1)
    c.line(43, 70, 1060, 70)
    text(c,43,49,'1 čtvereček = 1 × 1 v Toolsetu = 10 × 10 m',11.6,bold=True)
    text(c,43,28,'00–09   Obousměrné přechody na společné hraně',10.2,color=DOOR)
    if secrets:
        text(c,510,28,'S1 a S2   Skryté služební průchody 38+',10.2,color=HIDDEN)
    text(c,1060,49,'05  Seřídit refraktor',10.2,color=MUTED,align='right')
    text(c,1060,28,'09  Otevřít Bránu tří paprsků',10.2,color=MUTED,align='right')
    c.showPage()
    c.save()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path, help='verify the plan against an exported module')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--font-dir', type=Path, default=Path('/usr/share/fonts/truetype/dejavu'))
    parser.add_argument('--player-map', action='store_true', help='omit the hidden routes')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == '.pdf':
        draw(args.output, args.module, args.font_dir, not args.player_map)
    elif args.output.suffix == '.png':
        with TemporaryDirectory() as work:
            pdf = Path(work)/'pudorys.pdf'
            draw(pdf, args.module, args.font_dir, not args.player_map)
            run(['pdftoppm', '-singlefile', '-scale-to', '5700', '-png',
                 str(pdf), str(args.output.with_suffix(''))], check=True)
    else:
        parser.error('output must be a PDF or PNG')


if __name__ == '__main__':
    main()
