"""Draw the full observatory proposal and the optical detail on a single sheet."""

from argparse import ArgumentParser
from functools import partial
from math import hypot
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

import mapa_hvezdarny as base
import navrh_v21 as plan
from plan import LANDMARKS, TILE, WALKS, ZONES
from shrines import COLUMNS, POST_RADIUS, ROOF_EDGE, polar


SIZE = (1660, 1810)
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
ACCENT = '#166760'
SERVICE = '#d9ede7'
SANCTUARY = '#efe1ca'
ROCK = '#cfb190'
ROCK_LINE = '#90623e'
BLUE = '#235e9b'
RED = '#a83e4f'
GREEN = '#277453'
PURPLE = '#8c4289'
PANEL = '#faf7f0'


def local(zone, x, y):
    return base.px(*ZONES[zone].world(x, y))


def scaled(x0, y0, origin_x, origin_y, scale):
    return lambda x, y: (x0 + (x - origin_x)*scale, y0 + (y - origin_y)*scale)


def corners(box):
    x1, y1, x2, y2 = box
    return ((x1, y1), (x2, y1), (x2, y2), (x1, y2))


def surface(c, convert, coords, color, stroke):
    shape = c.beginPath()
    shape.moveTo(*convert(*coords[0]))
    for point in coords[1:]:
        shape.lineTo(*convert(*point))
    shape.close()
    base.fill(c, color)
    base.ink(c, stroke or color, 1)
    c.drawPath(shape, fill=1, stroke=int(stroke is not None))
    return shape


def rubble(c, convert, coords):
    shape = surface(c, convert, coords, ROCK, ROCK_LINE)
    xs, ys = zip(*(convert(*point) for point in coords))
    x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
    c.saveState()
    c.clipPath(shape, stroke=0, fill=0)
    base.ink(c, ROCK_LINE, .5)
    for offset in range(-int(y2-y1), int(x2-x1)+1, 6):
        x = x1 + offset
        c.line(x, y1, x+y2-y1, y2)
    c.restoreState()


def label(c, x, y, value, color=ACCENT):
    base.fill(c, PANEL)
    base.ink(c, color, 1.0)
    width = max(21, 9 + pdfmetrics.stringWidth(value, 'Bold', 8))
    c.roundRect(x-width/2, y-6.5, width, 13, 3, fill=1, stroke=1)
    base.text(c, x, y-2.8, value, 8, color=color, bold=True, align='center')


def stroke_path(c, convert, coords, color, width, *, dash=(), tip=False):
    pixels = tuple(convert(*point) for point in coords)
    base.ink(c, color, width)
    if dash:
        c.setDash(dash)
    base.path(c, pixels)
    if dash:
        c.setDash()
    if tip:
        (x1, y1), (x2, y2) = pixels[-2:]
        length = hypot(x2 - x1, y2 - y1)
        base.arrow(c, x2, y2, (x2-x1)/length, (y2-y1)/length, color)


def opening(c, convert, center, width, direction, identifier, *, caption_shift=(0, 0)):
    x, y = center
    dx, dy = direction
    half = width/2
    x1, y1 = convert(x-dy*half, y+dx*half)
    x2, y2 = convert(x+dy*half, y-dx*half)
    px, py = convert(x, y)
    base.ink(c, PANEL, 4.2)
    c.line(x1, y1, x2, y2)
    base.ink(c, ACCENT, 1.8)
    c.line(x1, y1, x2, y2)
    for side in (-1, 1):
        base.arrow(c, px+side*dx*8, py+side*dy*8, side*dx, side*dy, ACCENT)
    label(c, px+caption_shift[0], py+caption_shift[1], identifier)


def service_floor(c, convert):
    surface(c, convert, plan.FILTER_ROOM, SERVICE, ACCENT)
    surface(c, convert, plan.MIXING_ROOM, SERVICE, ACCENT)
    for box in (plan.HALL_ACCESS, plan.ACCESS_TURN, plan.BREACH):
        surface(c, convert, corners(box), SERVICE, None)
    for coords in plan.RUBBLE:
        rubble(c, convert, coords)


def shrine_floor(c, convert, shrine):
    surface(c, convert, shrine.footprint, SANCTUARY, ROCK_LINE)
    surface(c, convert, corners(shrine.corridor), SANCTUARY, None)


def shrine_columns(c, convert, shrine):
    x,y=shrine.center
    px,py=convert(x,y)
    r=abs(convert(x+ROOF_EDGE,y)[0]-px)
    base.ink(c,ROCK_LINE,.85)
    c.circle(px,py,r,fill=0,stroke=1)
    base.fill(c,ROCK_LINE)
    for angle in COLUMNS:
        dx,dy,_=polar(POST_RADIUS,angle+shrine.entrance+90)
        c.circle(*convert(x+dx,y+dy),r*.088,fill=1,stroke=0)


def overview(c):
    for key in ZONES:
        if key != 'service':
            base.floor(c, key, True)
    halls = partial(local, 'halls')
    walks = partial(local, 'walks')
    service_floor(c, halls)
    for shrine in plan.SHRINES:
        shrine_floor(c, walks, shrine)
    base.grid(c, True)
    base.route(c, True, routes=WALKS | {'walks':WALKS['walks'][:2]})
    opening(c, halls, plan.R1_FRAME, plan.R1_WIDTH, (0, 1), 'R1', caption_shift=(12, 10))
    x, y = halls(32.25, 29.7)
    label(c, x, y+10, 'R2')
    for shrine in plan.SHRINES:
        shrine_columns(c, walks, shrine)
        stroke_path(c, walks, shrine.approach, ROCK_LINE, 1.8)
        opening(c, walks, shrine.door, 3.4, (0, 1), shrine.key, caption_shift=(12, -2))
        mark_x, mark_y = walks(*shrine.seal)
        base.fill(c, ROCK_LINE)
        c.circle(mark_x, mark_y, 2.6, fill=1, stroke=0)
    landmarks = LANDMARKS | {
        'halls': ((*plan.HALL_PANEL, 'Rozvaděč'), (15.5, 50, 'Archiv'), (36, 15, 'Clony'),
                  (56.3, 24.0, 'Stará filtrovna')),
        'walks': (),
        'top': ((*LANDMARKS['top'][0][:2], 'Chrám'), (*plan.LANTERN, 'Strážní lucerna')),
    }
    base.captions(c, True, descriptions={
        'halls': 'Za R1 servis ochranné lucerny',
        'walks': 'Svatyně Kopí a Lucerny v samostatných odbočkách',
        'top': 'Chrám, Ithren a ochrana horské stezky',
    }, landmarks=landmarks)
    x, y = local('top', *plan.ITHREN)
    base.fill(c, base.INK)
    c.circle(x, y, 2.0, fill=1, stroke=0)
    base.text(c, x-7, y-2, 'Ithren', 8.6, bold=True, align='right')
    for y, color, name, levels, info in (
        (346, base.ROUTE, 'Dolní okruh', '34–38', 'Dílny a Chodby clon'),
        (1336, base.HIGH_ROUTE, 'Horní okruh', '37–40', 'Schody a Ochozy se svatyněmi'),
    ):
        base.text(c, 43, y, name, 16, color=color, bold=True)
        base.text(c, 43, y-29, levels, 21, color=color, bold=True)
        base.text(c, 43, y-49, info, 9.3, color=base.MUTED)


def detail_grid(c, convert, left, bottom, right, top):
    base.ink(c, base.GRID, .46)
    for x in range(left, right+1, TILE):
        c.line(*convert(x, bottom), *convert(x, top))
    for y in range(bottom, top+1, TILE):
        c.line(*convert(left, y), *convert(right, y))


def station(c, convert, point, name, offset, color=ACCENT):
    x, y = convert(*point)
    base.fill(c, PANEL)
    base.ink(c, color, 1.15)
    c.circle(x, y, 3.3, fill=1, stroke=1)
    base.text(c, x+offset[0], y+offset[1], name, 8.2, color=color, bold=True)


def optical_detail(c):
    convert = scaled(1138, 1260, 10, 20, 10.55)
    for x1, y1, x2, y2 in ZONES['halls'].floor:
        l, b, r, t = max(x1, 10), max(y1, 20), min(x2, 56), min(y2, 40)
        if l < r and b < t:
            surface(c, convert, corners((l, b, r, t)), '#e6e3d9', None)
    service_floor(c, convert)
    detail_grid(c, convert, 10, 20, 56, 40)
    stroke_path(c, convert, plan.R1_APPROACH[:-1]+plan.SERVICE_WALK, ACCENT, 1.05, dash=(.65, 3.2))
    for ray in (plan.FEED_RAY, plan.FILTER_DETOUR, plan.WHITE_TO_PRISM):
        stroke_path(c, convert, ray, base.DOOR, 3.9)
        stroke_path(c, convert, ray, '#fff9df', 2.1)
    for ray, color in (
        ((plan.PRISM, plan.RED), RED), ((plan.PRISM, plan.GREEN), GREEN), ((plan.PRISM, plan.BLUE), BLUE),
        (plan.RED_TO_MIX, RED), (plan.GREEN_TO_PILOT, GREEN), (plan.BLUE_TO_MIX, BLUE),
        ((plan.PILOT,plan.PILOT_IRIS), GREEN), (plan.MIXED_RAY, PURPLE),
        (plan.PURPLE_TO_OUTLET, PURPLE),
    ):
        stroke_path(c, convert, ray, color, 2.0)
    for ray, color in (
        (plan.WHITE_TO_RUBBLE, ROCK_LINE), (plan.WHITE_TO_GAUGE, ROCK_LINE),
        (plan.RED_TO_GAUGE, RED), (plan.GREEN_TO_MIX, GREEN),
        (plan.BLUE_TO_RUBBLE, BLUE), (plan.PURPLE_TO_GAUGE, PURPLE),
        ((plan.PILOT,plan.PILOT_STAR), GREEN),
    ):
        stroke_path(c, convert, ray, color, 1.25, dash=(3, 2))
    for point, name, offset, color in (
        (plan.SOURCE, 'Zdroj', (-6, 13), base.DOOR), (plan.Z1, 'Z1', (-12, 10), base.DOOR),
        (plan.Z2, 'Z2', (4, -12), base.DOOR),
        (plan.PRISM, 'Hranol', (-19, -15), base.DOOR), (plan.RED, 'Č', (-11, 7), RED),
        (plan.GREEN, 'Z', (-7, -12), GREEN), (plan.BLUE, 'M', (6, -6), BLUE),
        (plan.MIXER, 'Směšovač', (-7, 13), PURPLE), (plan.PILOT, 'Pojistka', (-12, -14), GREEN),
        (plan.PILOT_IRIS, 'Slunce', (-15, 10), GREEN), (plan.PILOT_STAR, 'Hvězda', (6, -7), GREEN),
        (plan.IRIS, 'Clona', (-13, 9), PURPLE),
        (plan.DEFLECTOR, 'Výstup', (-12, 13), PURPLE),
    ):
        station(c, convert, point, name, offset, color)
    stroke_path(c, convert, (plan.OUTLET, (11.0, 36.55)), PURPLE, 2, tip=True)
    label(c, *convert(plan.OPTICAL_SLOT[0], plan.OPTICAL_SLOT[1]-1.1), 'Okénko', base.DOOR)
    opening(c, convert, plan.ACCESS_DOOR, 2.1, (-1,0), 'Zámek', caption_shift=(8,-12))
    opening(c, convert, plan.R1_FRAME, plan.R1_WIDTH, (0,1), 'R1', caption_shift=(15,7))
    opening(c, convert, (32.25, 29.7), 2.4, (-1, 0), 'R2', caption_shift=(1, 13))
    for x, y, name in ((14, 40.8, 'Sál skládání'), (34, 40.8, 'Filtrovna světla')):
        base.text(c, *convert(x, y), name, 11, bold=True)
    base.text(c, *convert(47.8, 33.0), 'Z východní', 8.0, bold=True, color=base.MUTED)
    base.text(c, *convert(47.8, 31.7), 'chodby', 8.0, bold=True, color=base.MUTED)
    base.text(c, 1138, 1230, 'R1  Práh v zalomené chodbě za kamennými dveřmi.', 10.2, bold=True)
    base.text(c, 1138, 1211, 'R2  Průlez v příčce 2,4 × 2,7 m, obousměrný', 10.2, bold=True)
    base.text(c, 1138, 1192, 'Okénkem v příčce vede paprsek k hranolu.', 10.2)
    base.text(c, 1138, 1169, 'Plný tah ukazuje funkční paprsek, přerušovaný jiný odraz.', 10.0)
    base.text(c, 1138, 1151, 'Šrafy označují sesuv. Tečky v podlaze vedou pěší cestu.', 10.0)
    base.text(c, 1138, 1131, 'Č + M   purpurová k lucerně', 10.4, color=PURPLE, bold=True)
    base.text(c, 1420, 1131, 'Z   na čidlo podle tabulky', 10.4, color=GREEN, bold=True)


def shrine_details(c):
    for x, shrine, left in ((1139, plan.SHRINES[0], 4), (1400, plan.SHRINES[1], 59)):
        convert = scaled(x, 795, left, 64, 9.4)
        shrine_floor(c, convert, shrine)
        detail_grid(c, convert, left, 64, left+20, 84)
        shrine_columns(c, convert, shrine)
        for box in shrine.furnishings:
            surface(c, convert, corners(box), '#d9bd9b', ROCK_LINE)
        stroke_path(c, convert, shrine.approach[2:], ROCK_LINE, 1.9)
        opening(c, convert, shrine.door, 3.4, (0, 1), shrine.key, caption_shift=(15, -4))
        station(c, convert, shrine.stand, shrine.guardian, (-19, -13), ROCK_LINE)
        station(c, convert, shrine.seal, 'Pečeť', (-18, 10), ROCK_LINE)
        base.text(c, x, 1010, shrine.name, 13, bold=True)
        dimension = '15 × 16 m' if shrine.key == 'K' else '17 × 15 m'
        base.text(c, x, 992, dimension, 9.8, color=base.MUTED)
        base.text(c, x, 770, 'Z horního sedla · vstup ze jihu', 9.6, color=base.MUTED)
    base.text(c, 1138, 743, 'Každý strážce má vlastní svatyni a pečeť.', 10.2, bold=True)


def section(c, y, header):
    base.ink(c, base.GRID, .75)
    c.line(1138, y, 1620, y)
    base.text(c, 1138, y-27, header, 19.5, bold=True)


def steps(c):
    for y, number, title, first, second in (
        (628, '1', 'Výstup k Ithrenovi', 'S pečetěmi seřiď Bránu tří paprsků a vystup k Ithrenovi.',
         'Při přijetí opravy Ithren předá klíč od dveří R1.'),
        (549, '2', 'Sestup k poruše', 'Trasa zpět vede přes Předbraní, Schody, Kopuli a Dílny.',
         'Z horního dvora vstupem 02 do Archivu a na východ.'),
        (470, '3', 'Obnova světla', 'Zrcadla obejdou sesuv. Průlez R2 vede k hranolu.',
         'Složené světlo projde světlovodem vzhůru k lucerně.'),
        (391, '4', 'Návrat na Poslední stupeň', 'Na stezce už nevznikají noví větrní elementálové.',
         'Opravu ohlásíš Ithrenovi u rozsvícené lucerny.'),
    ):
        label(c, 1149, y+3, number)
        base.text(c, 1170, y, title, 12, bold=True)
        base.text(c, 1170, y-17, first, 10.4)
        base.text(c, 1170, y-34, second, 10.4)


def draw(target, module):
    for name, font in (('Regular', 'DejaVuSans.ttf'), ('Bold', 'DejaVuSans-Bold.ttf')):
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / font)))
    base.check_plan()
    base.validate_module(module)
    plan.check_solution()
    c = Canvas(str(target), pagesize=SIZE, invariant=1)
    c.setTitle(f'Hvězdárna druhého nebe – půdorys v{base.VERSION}')
    c.setLineCap(1)
    c.setLineJoin(1)
    base.fill(c, base.PAPER)
    c.rect(0, 0, *SIZE, stroke=0, fill=1)
    base.text(c, 43, 1766, 'Hvězdárna druhého nebe', 34, bold=True)
    base.text(c, 44, 1736, 'Dva výstupové okruhy, oprava lucerny a svatyně pečetí', 15, color=base.MUTED)
    base.text(c, 1620, 1766, f'V{base.VERSION}', 14, bold=True, color=ACCENT, align='right')
    base.text(c, 1620, 1736, 'Půdorys a přechody modulu', 11, color=base.MUTED, align='right')
    base.ink(c, base.GRID, .85)
    c.line(43, 1712, 1620, 1712)
    c.line(1095, 82, 1095, 1698)
    base.arrow(c, 1019, 1680, 0, 1, base.INK)
    c.line(1019, 1661, 1019, 1674)
    base.text(c, 1019, 1689, 'S', 11, bold=True, align='center')
    overview(c)
    base.fill(c, PANEL)
    c.roundRect(1120, 1111, 519, 566, 6, fill=1, stroke=0)
    base.text(c, 1138, 1641, 'Servis ochranné lucerny', 22, bold=True)
    base.text(c, 1138, 1612, 'Samostatná oblast za R1 · 6 × 4 dlaždice · společná výška podlah', 11, color=base.MUTED)
    base.text(c, 1138, 1588, 'Filtrovna 13 × 17,5 m · Sál skládání 19,5 × 17,5 m', 10.5, color=base.MUTED)
    base.text(c, 1138, 1548, 'Denní světlo vstupuje otevřeným skalním světlíkem.', 10.4, bold=True)
    base.text(c, 1138, 1529, 'Devět pohyblivých uzlů, tři směry u každého z nich.', 10.4, color=base.MUTED)
    optical_detail(c)
    section(c, 1080, 'Dvě svatyně na Visutých ochozech')
    shrine_details(c)
    section(c, 699, 'Cesta k opravě a zpět')
    steps(c)
    section(c, 305, 'Rozvaděč v ohlašovně')
    base.text(c, 1138, 253, 'Paprsková chodba · Filtrovna · Archiv', 11.7, bold=True)
    base.text(c, 1138, 230, 'Zvolená větev míří do záchytu ve spodní liště panelu.', 10.4)
    base.text(c, 1138, 210, 'Clony dané větve se zakryjí, dvě ostatní zůstanou v provozu.', 10.4)
    base.text(c, 1138, 190, 'Stav ukáže panel i každá zakrytá čočka.', 10.4)
    base.ink(c, base.GRID, .8)
    c.line(43, 70, 1620, 70)
    base.text(c, 43, 49, '1 čtvereček = 1 × 1 v Toolsetu = 10 × 10 m', 11, bold=True)
    base.text(c, 43, 28, '00–09  Obousměrné prahy na společných hranách', 10, color=base.DOOR)
    base.text(c, 490, 28, 'S1/S2  Služební průchody 38+', 10, color=base.HIDDEN)
    base.text(c, 1150, 49, 'R1/R2  Opravárenská větev', 10.1, color=ACCENT, bold=True)
    base.text(c, 1420, 49, 'K/L  Svatyně pečetí', 10.1, color=ROCK_LINE, bold=True)
    c.showPage()
    c.save()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == '.pdf':
        draw(args.output, args.module)
    elif args.output.suffix == '.png':
        with TemporaryDirectory() as directory:
            pdf = Path(directory) / 'mapa.pdf'
            draw(pdf, args.module)
            run(['pdftoppm', '-singlefile', '-scale-to', '5800', '-png',
                 str(pdf), str(args.output.with_suffix(''))], check=True)
    else:
        parser.error('output must be a PDF or PNG')


if __name__ == '__main__':
    main()
