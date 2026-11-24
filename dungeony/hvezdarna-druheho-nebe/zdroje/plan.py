"""North-up Toolset grid for the main observatory route."""

from dataclasses import dataclass
from navrh_v21 import (ACCESS_TURN, HALL_ACCESS, HALL_PREVIEW, R1_APPROACH, R1_FRAME, R1_SAFE_RETURN,
                       REPAIR_PASSAGES, SERVICE_PREVIEW, SERVICE_ROOMS, SERVICE_WALK, SHRINES,
                       check_ray_paths)


VERSION = 30
TILE = 10
THRESHOLD_INSET = 1.55
LANDING_INSET = 5.0
PASSAGE_WIDTH = 4.8
SECRET_LEVEL = 38
STAIR_EDGE = .9
NARROW_STAIR_INSET = 1.74
SKY_OPENING = 6.52
SKY_DECKS = ('steps', 'walks', 'gate', 'top')
SKY_JOINS = ('06', '07', '08', '09')
DIRECTIONS = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}
ENTRY_X = 51.075
RIM_ENTRY_X = ENTRY_X - 40
SPEAR_POST, LANTERN_POST = (shrine.seal for shrine in SHRINES)
WING_POST = (46.35,57.94)
STORM_CABINET = (55.65,59.26)
STORM_WICKTABLE = (51.07,58.93)
GATE_WEST_BAY = (12.52,34.35)
GATE_EAST_BAY = (56.15,12.52)
GATE_CLERK = (GATE_WEST_BAY[0]-.20, GATE_WEST_BAY[1]+.05)
GATE_REST = (GATE_EAST_BAY[0]-.42, GATE_EAST_BAY[1]-.07)
TEMPLE_AXIS = 35.0
TEMPLE_FRONT = 33.55
TEMPLE_REAR = 46.15
TEMPLE_FACE = (21.45,26.25,31.05,38.95,43.75,48.55)
TEMPLE_SIDES = (TEMPLE_FRONT,37.75,41.95,TEMPLE_REAR)
TEMPLE_ORIGIN = (TEMPLE_AXIS,(TEMPLE_FRONT+TEMPLE_REAR)/2)
TEMPLE_EAVES = (20.25,32.43,49.75,47.27)
TOP_MIRROR = (54.65,17.05)
TOP_COLUMNS = (
    *((x,y) for x in (TEMPLE_FACE[0],TEMPLE_FACE[-1]) for y in TEMPLE_SIDES),
    *((x,y) for x in TEMPLE_FACE[1:-1] for y in (TEMPLE_FRONT,TEMPLE_REAR)),
)
TOP_GUARDS = tuple((x,y) for x in (15.2,54.8) for y in (33.9,38.4,42.9))

# Cross sections of the shelves and their connecting ridges. Each row gives
# a northing and the left and right edges of the same patch of rock.
WALK_BANDS = (
    ((0,72,78),(4,71.78,78.26),(7.5,70.85,79.28),(11,68.85,79.65)),
    ((11,0,79.8),(13,0,80),(17,0,80),(19,0,79.45),(21.5,3.2,77.42),(24,11.8,70)),
    ((24,18.1,32),(30,20.24,34.6),(35,22,35.4),(40,21.3,33),
     (46,17.3,31),(52,15.6,29),(57,16.2,30.2),(62,13.3,32.9)),
    ((24,47.55,63.65),(29,45.7,60.7),(34,45.4,59.9),(39,48.75,63.3),
     (45,50.5,65.2),(51.5,52.12,66.72),(57,50,63.3),(62,48,68.5)),
    ((62,10.57,69.91),(66,10.90,69.4),(68,8.0,73.2),(69,7.0,74.0),
     (71,5.0,75.5),(72,5.0,76.25)),
    ((72,5.0,20.0),(81,5.0,20.0),(83,12.33,17.33),(84,15.78,16.17)),
    ((72,60.0,76.25),(73,60.0,77.0),(78,60.,77.),(80,60.5,77.),
     (82,61.,74.5),(84,71.78,72.18)),
    ((72,37,52.9),(77,36.4,51.2),(83,31.1,45.5),(88,21.45,38.81),
     (92,14.6,28),(96,11,24.2),(101,8.8,22.2),(105,10.5,19.5),(110,10.4,19.6)),
)
WALK_HEIGHTS = ((0,5),(22,5),(25,5.42),(34,7.5),(44,9.25),(53,11.35),
                (62,13.20),(84,13.20),(91,15.7),(100,18.8),(105,20),(110,20))
WORK_YARD_WALLS = (
    ((10.46,10.40),(40,10.40)), ((40,10.40),(40,12.10)),
    ((40,17.90),(40,19.62)), ((40,19.62),(27.66,19.62)),
    ((22.31,19.62),(10.46,19.62)), ((10.46,19.62),(10.46,10.40)),
)
WORK_SHELF = (1, 5, 5, 7)
WORK_BRIDGE_LANDING = (22.31, 27.66)
WORK_STATIONS = {
    'intake': (35.75, 18.42),
    'forge': (33.18, 12.30),
    'anvil': (30.56, 12.30),
    'grind': (18.63, 11.79),
    'desk': (12.65, 14.75),
    'dispatch': (43.65, 64.65),
    'inspection': (14.90, 65.53),
}


def linear(y, y0, y1, a, b):
    return a+(b-a)*(y-y0)/(y1-y0)


def height_at(profile,y):
    for (y0,z0),(y1,z1) in zip(profile,profile[1:]):
        if y <= y1:
            return linear(max(y,y0),y0,y1,z0,z1)
    return profile[-1][1]


def bank_outline(band):
    return tuple((left,y) for y,left,_ in band)+tuple((right,y) for y,_,right in reversed(band))


@dataclass(frozen=True)
class ZonePlan:
    title: str
    origin: tuple[int, int]
    size: tuple[int, int]
    rooms: tuple[tuple[float, float, float, float], ...]
    interior: bool = False
    bridges: tuple[int, ...] = ()
    bridge_width: float = 3.9
    stairs: tuple[tuple[int, int], ...] = ()
    enclosed: tuple[tuple[float, float, float, float], ...] = ()
    banks: tuple = ()
    relief: tuple = ()

    def world(self, x, y):
        return self.origin[0] * TILE + x, self.origin[1] * TILE + y

    def local(self, x, y):
        return x - self.origin[0] * TILE, y - self.origin[1] * TILE

    @property
    def tiles(self):
        if self.interior or self.banks:
            return [(0, 0, *self.size)]
        return list(self.rooms)

    @property
    def floor(self):
        if self.interior:
            return self.rooms
        terraces = [tuple(edge * TILE for edge in room) for room in self.rooms]
        half = self.bridge_width / 2
        spans = [(x - half, 20, x + half, 50) for x in self.bridges]
        return (*terraces, *spans, *self.enclosed)

    def contains(self, x, y):
        if self.banks:
            return any(y0<=y<=y1 and linear(y,y0,y1,l0,l1)<=x<=linear(y,y0,y1,r0,r1)
                       for band in self.banks for (y0,l0,r0),(y1,l1,r1) in zip(band,band[1:]))
        row = int(y // TILE)
        if TILE*row < y < TILE*(row+1) and any(stair_row == row for _, stair_row in self.stairs):
            return any(left <= x <= right for left, right in self.flights(row))
        return any(l <= x <= r and low <= y <= high for l, low, r, high in self.floor)

    def flights(self, row):
        columns = {col for col, stair_row in self.stairs if stair_row == row}
        for first in sorted(columns):
            if first - 1 in columns:
                continue
            last = first
            while last + 1 in columns:
                last += 1
            inset = NARROW_STAIR_INSET if first == last else STAIR_EDGE
            yield TILE*first + inset, TILE*(last + 1) - inset


ZONES = {
    'camp': ZonePlan('Horský tábor', (4, -1), (7, 4), ((1, 0, 6, 3), (2, 3, 3, 4))),
    'rim': ZonePlan('Výstupová římsa', (4, 3), (9, 4), (
        (1, 0, 5, 2), (1, 2, 4, 3), (1, 2, 2, 4),
        (5, 1, 7, 2), (6, 2, 9, 3), (0, 3, 2, 4),
    )),
    'halls': ZonePlan('Chodby clon', (6, 7), (7, 6), (
        (0, 12.1, 7, 17.9), (7, 10.6, 21, 20.5), (9, 20.5, 17, 24.2),
        (21, 12.55, 47, 17.45), (30.8, 17.45, 34.1, 20.2), (38, 9.6, 41.35, 12.55),
        (47, 11.35, 52.7, 37.15), (52.7, 18.3, 59.0, 26), (46.8, 37.15, 55, 48.2),
        (24, 42.2, 46.8, 47.8), (9, 39.7, 24, 49.1), (7, 49.1, 19.5, 59.4),
        (19.5, 50.6, 23.0, 57.9), (0, 52.2, 7, 57.8), HALL_ACCESS, ACCESS_TURN, HALL_PREVIEW,
    ), interior=True),
    'works': ZonePlan('Dílny a servisní lávka', (0, 7), (6, 8), (
        (1, 1, 4, 2), WORK_SHELF,
    ), bridges=(25,), enclosed=(
        (ENTRY_X-2.9, 0, ENTRY_X+2.9, 4.3), (43, 4.3, 59.15, 19.6),
        (40, 12.1, 43, 17.9), (59.15, 12.1, 60, 17.9),
        (50, 50, 57.1, 60), (57.1, 52.2, 60, 57.8),
        (20, 70, 40, 73), (27, 73, 33, 80),
    )),
    'dome': ZonePlan('Kopule', (0, 15), (6, 6), (
        (13.2, 21.8, 46.8, 42.2), (18.3, 17, 41.7, 21.8),
        (18.3, 42.2, 41.7, 46), (27, 0, 33, 17),
        (8.2, 23.1, 13.2, 29), (46.8, 23.2, 51.4, 29),
        (26.8, 46, 33.2, 60), (38.3, 12.25, 48, 17),
    ), interior=True),
    'steps': ZonePlan('Schody do nebe', (0, 21), (7, 10), (
        (2, 0, 7, 1), (1, 1, 5, 2), (2, 2, 4, 3),
        (1, 3, 6, 4), (3, 4, 5, 5), (1, 5, 6, 6),
        (2, 6, 4, 7), (1, 7, 5, 9), (2, 9, 3, 10),
    ), stairs=((2, 2), (3, 2), (3, 4), (4, 4), (2, 6), (3, 6))),
    'walks': ZonePlan('Visuté ochozy', (7, 20), (8, 11), (), banks=WALK_BANDS, relief=WALK_HEIGHTS),
    'gate': ZonePlan('Předbraní', (2, 31), (7, 7), (
        (1, 1, 6, 4), (0, 1, 1, 3), (6, 1, 7, 3), (3, 4, 4, 5), (2, 5, 5, 6),
        (0, 0, 1, 1), (6, 0, 7, 1), (3, 6, 4, 7),
    ), stairs=((3, 4),)),
    'top': ZonePlan('Poslední stupeň', (2, 38), (7, 7), (
        (3, 0, 4, 1), (1, 1, 6, 2), (2, 2, 5, 3), (1, 3, 6, 5), (2, 5, 5, 6),
    ), stairs=((2, 2),(3, 2),(4, 2))),
    'study': ZonePlan('Pracovna správkyně', (13, 4), (3, 16), (
        (0, 12.1, 6, 17.9), (6, 11.2, 11.6, 18.3), (6, 18.3, 11.6, 31),
        (5.2, 31, 22, 42.9), (22, 35.1, 26.5, 41.7),
        (15, 42.9, 20.8, 52.5), (15, 52.5, 25, 58.6),
        (20, 58.6, 26, 83), (26, 72, 28.8, 80), (10, 83, 26, 89),
        (10, 89, 16, 117), (6.5, 99, 10, 107), (10, 117, 23, 123),
        (17, 123, 23, 144), (23, 130, 28.5, 141), (12, 144, 23, 150),
        (12, 150, 18, 160),
    ), interior=True),
    # A separate client area projected into the empty core of Chodby clon.
    'service': ZonePlan('Světelný servis', (6, 7), (6, 4), SERVICE_ROOMS, interior=True),
}


@dataclass(frozen=True)
class Join:
    label: str
    first: str
    second: str
    edge: tuple[float, float]
    facing: int
    names: tuple[str, str]
    signs: tuple[str, str]
    required: str = ''
    secret: bool = False
    branch: str = ''

    def route(self, source, target):
        return f'{source}_{target}_{self.branch}' if self.branch else f'{source}_{target}'

    def heading(self, zone):
        return self.facing if zone == self.first else (self.facing + 180) % 360

    def point(self, zone, inset=0):
        dx, dy = DIRECTIONS[self.heading(zone)]
        x, y = ZONES[zone].local(*self.edge)
        return x - inset * dx, y - inset * dy

    def destinations(self):
        yield self.first, self.second, self.names[0], self.signs[0], self.required
        yield self.second, self.first, self.names[1], self.signs[1], self.required if self.secret else ''


JOINS = (
    Join('00', 'camp', 'rim', (66, 30), 90, ('Na Výstupovou římsu', 'Zpět do tábora'),
         ('VYSTUPOVA RIMSA', 'TABOR')),
    Join('03', 'rim', 'works', (ENTRY_X, 70), 90, ('Do vstupní síně hvězdárny', 'Zpět na Výstupovou římsu'),
         ('VSTUPNI SIN', 'VYSTUPOVA RIMSA')),
    Join('01', 'works', 'halls', (60, 85), 0, ('Do Chodeb clon', 'Do Zkušebny'),
         ('CHODBY CLON', 'ZKUSEBNA'), branch='lab'),
    Join('02', 'halls', 'works', (60, 125), 180, ('Do horní dílny', 'Do archivu clon'),
         ('DILNY', 'ARCHIV CLON')),
    Join('04', 'works', 'dome', (30, 150), 90, ('Do kopule', 'Zpět do dílen'),
         ('KOPULE', 'DILNY')),
    Join('05', 'dome', 'steps', (30, 210), 90, ('Na Schody do nebe', 'Sestoupit do kopule'),
         ('SCHODY DO NEBE', 'KOPULE'), 'hvd_aligned'),
    Join('06', 'steps', 'walks', (70, 215), 0, ('K visutým ochozům', 'K patě Schodů do nebe'),
         ('OCHOZY', 'SCHODY DO NEBE')),
    Join('07', 'steps', 'gate', (25, 310), 90, ('K západnímu vchodu Předbraní', 'Na Schody do nebe'),
         ('PREDBRANI', 'SCHODY DO NEBE')),
    Join('08', 'walks', 'gate', (85, 310), 90, ('K východnímu vchodu Předbraní', 'Zpět na visuté ochozy'),
         ('PREDBRANI', 'OCHOZY')),
    Join('09', 'gate', 'top', (55, 380), 90, ('Na Poslední stupeň', 'Ústup do předbraní'),
         ('POSLEDNI STUPEN', 'PREDBRANI'), 'hvd_gate_open'),
    Join('S1', 'rim', 'study', (130, 55), 0, ('Skalní spára do Pracovny', 'Skalní spára na Výstupovou římsu'),
         ('PRACOVNA', 'VYSTUPOVA RIMSA'), 'hvd_secret_rim', True),
    Join('S2', 'study', 'walks', (145, 200), 90, ('Služební výstup na Visuté ochozy', 'Služební sestup do Pracovny'),
         ('OCHOZY', 'PRACOVNA'), 'hvd_secret_exit', True),
)

OPTICS_JOIN = next(join for join in JOINS if join.required == 'hvd_aligned')
GATE_JOIN = next(join for join in JOINS if join.required == 'hvd_gate_open')


# The route stays on the authored lanes. The two arms of the Ochozy share
# their landings and lead to the same north exit.
WALKS = {
    'camp': (((27,16),(28.5,23),(26,31),(26,40)),),
    'rim': (((26,0),(26,9),(26,12),(19,17),(15,25),(RIM_ENTRY_X,34),(RIM_ENTRY_X,40)),),
    'halls': (((0,15),(7,15),(16,15),(49.9,15),(49.9,43),(46.8,45),(15.5,45),(14,55),(0,55)),),
    'works': (((ENTRY_X,0),(ENTRY_X,15),(42,15),(25,17),(25,52),(34,55),(60,55)),
              ((ENTRY_X,15),(60,15)),
              ((34,55),(30,65),(30,80))),
    'dome': (((30,0),(30,19),(36,24),(36,37),(30,44),(30,60)),),
    'steps': (((30,0),(30,7),(28,16),(28,32),(39.5,36.5),(40,53.1),
               (30,58.0),(30,76),(25,86),(25,100)),
              ((30,7),(46,7),(57,5),(70,5))),
    'walks': (((0,15),(6.3,15),(16.5,16.3),(24,19.5),(24.6,25.5),(28.9,35.5),
               (24.5,45.3),(21.8,55.4),(24.8,63.8),(31,66.4),(41,68.8),(46,72.2),
               (44,78),(37,84),(28,87),(20.5,92.8),(15,101.4),(15,110)),
              ((24,19.5),(39,17.4),(54.5,17.3),(55.5,25),(52.4,33.5),(57.2,43.7),
               (59.2,51.8),(55.1,60.1),(58,64.8),(48.3,67.6),(41,68.8)),
              *(shrine.approach for shrine in SHRINES)),
    'gate': (((5,0),(5,13),(12,20),(24,34),(35,39.2),(35,70)),
             ((65,0),(65,17),(55,24),(48,32),(47.5,38.9),(35,39.2))),
    'top': (((35,0),(35,15.5),(35,31.8),(35,54)),),
}
SECRET_WALKS = {
    'halls': (R1_APPROACH,),
    'service': (SERVICE_WALK,),
    'rim': (((26,12),(32,13.6),(43,14.8),(55,15),(64.2,15.7),(65.4,24.6),
             (72.5,26),(77.2,23.7),(82,23.7),(85.4,25),(90,25)),),
    'study': (((0,15),(8.5,15),(8.5,36),(17.8,38.8),(17.9,46),(17.9,54.8),(23,55.9),
               (23,86),(13,86),(13,120),(20,120),(20,147),(15,147),(15,160)),),
    'walks': (((75,0),(75,11),(66,15.5),(54.5,17.3)),),
}
LANDMARKS = {
    'camp': ((16.8,22.5,'Nocleh'), (38.0,24.3,'Zásoby')),
    'rim': ((23,14.2,'Rozcestí'),),
    'halls': ((13,23.5,'Ohlašovna'), (15.5,50,'Archiv'), (36,15,'Clony'), (54.6,24.0,'Filtrovna')),
    'works': ((17.1,17.6,'Zkušebna'), (*WORK_STATIONS['forge'],'Kovárna'),
              (ENTRY_X,15.8,'Vstupní síň'), (18,57,'Kotva'), (*WORK_STATIONS['dispatch'],'Expedice')),
    'dome': ((30,31,'Refraktor'),),
    'steps': ((*WING_POST,'Křídlo'),),
    'walks': ((*SPEAR_POST,'Kopí'), (*LANTERN_POST,'Lucerna')),
    'top': ((*TEMPLE_ORIGIN,'Chrám'), (38.15,55.5,'Lucerna')),
    'study': ((20.7,39.7,'Záložní Kotva'),),
}


def check_plan():
    check_ray_paths()
    routes = [join.route(source, target) for join in JOINS
              for source, target, _, _, _ in join.destinations()]
    if len(routes) != len(set(routes)) or len(JOINS) != len({join.label for join in JOINS}):
        raise ValueError('Every threshold needs a unique route and map label')
    occupied = set()
    for code, zone in ZONES.items():
        x, y = zone.origin
        w, h = zone.size
        tiles = {(a, b) for a in range(x, x + w) for b in range(y, y + h)}
        if code != 'service':
            if occupied & tiles:
                raise ValueError(f'Overlapping Toolset areas at {code}')
            occupied.update(tiles)
        for l, low, r, high in zone.floor:
            if not (0 <= l < r <= TILE * w and 0 <= low < high <= TILE * h):
                raise ValueError(f'Floor outside Toolset bounds at {code}')
        if zone.banks:
            for band in zone.banks:
                if not all(0 <= y <= TILE*h and 0 <= left < right <= TILE*w for y,left,right in band):
                    raise ValueError(f'Rock shelf outside Toolset bounds at {code}')
                if any(a[0]>=b[0] for a,b in zip(band,band[1:])):
                    raise ValueError(f'Overlapping sections of rocky terrain at {code}')
        for walk in (*WALKS.get(code, ()), *SECRET_WALKS.get(code, ())):
            for start, end in zip(walk, walk[1:]):
                for i in range(65):
                    p = tuple(a + (b - a) * i/64 for a, b in zip(start, end))
                    if not zone.contains(*p):
                        raise ValueError(f'Walking line leaves the floor at {code}: {p}')
    halls, service = ZONES['halls'], ZONES['service']
    if (halls.origin != service.origin or not halls.contains(*R1_FRAME)
            or not service.contains(*R1_FRAME) or not halls.contains(*R1_SAFE_RETURN[:2])):
        raise ValueError('R1 needs a common turn and a safe return on the same floor')
    for room in halls.floor:
        for hidden in service.floor:
            left,bottom = max(room[0],hidden[0]),max(room[1],hidden[1])
            right,top = min(room[2],hidden[2]),min(room[3],hidden[3])
            if left < right and bottom < top:
                if room not in (HALL_ACCESS, ACCESS_TURN, HALL_PREVIEW) and hidden != SERVICE_PREVIEW:
                    raise ValueError('Only the R1 vestibule may overlap a public hallway')
    for source,target,_,(x0,y0,x1,y1),(x,y,_) in REPAIR_PASSAGES:
        if not all(ZONES[source].contains(xx,yy) for xx in (x0,x1) for yy in (y0,y1)) or not ZONES[target].contains(x,y):
            raise ValueError(f'R1 is outside the walkable floor at {source}')
    for join in JOINS:
        for origin, _, _, _, _ in join.destinations():
            zone = ZONES[origin]
            x, y = join.point(origin)
            dx, dy = DIRECTIONS[join.heading(origin)]
            w, h = (value * TILE for value in zone.size)
            on_side = {0: x == w, 90: y == h, 180: x == 0, 270: y == 0}
            if not on_side[join.heading(origin)]:
                raise ValueError(f'{origin} does not meet the shared map edge')
            lanes = SECRET_WALKS if join.secret else WALKS
            if not any((x, y) in (walk[0], walk[-1]) for walk in lanes[origin]):
                raise ValueError(f'{origin} has no walking line to the shared edge')
            for inset in (0, THRESHOLD_INSET, LANDING_INSET):
                px, py = join.point(origin, inset)
                for side in (-PASSAGE_WIDTH / 2, 0, PASSAGE_WIDTH / 2):
                    if not zone.contains(px - dy * side, py + dx * side):
                        raise ValueError(f'Passage around {origin} is missing floor')
