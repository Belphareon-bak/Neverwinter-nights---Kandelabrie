"""North-up Toolset grid for the main observatory route."""

from dataclasses import dataclass


VERSION = 12
TILE = 10
THRESHOLD_INSET = 1.55
LANDING_INSET = 5.0
PASSAGE_WIDTH = 4.8
SECRET_LEVEL = 38
DIRECTIONS = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}


@dataclass(frozen=True)
class ZonePlan:
    title: str
    origin: tuple[int, int]
    size: tuple[int, int]
    rooms: tuple[tuple[float, float, float, float], ...]
    interior: bool = False
    bridges: tuple[int, ...] = ()
    stairs: tuple[tuple[int, int], ...] = ()

    def world(self, x, y):
        return self.origin[0] * TILE + x, self.origin[1] * TILE + y

    def local(self, x, y):
        return x - self.origin[0] * TILE, y - self.origin[1] * TILE

    @property
    def tiles(self):
        if self.interior:
            return [(0, 0, *self.size)]
        return list(self.rooms)

    @property
    def floor(self):
        if self.interior:
            return self.rooms
        terraces = [tuple(edge * TILE for edge in room) for room in self.rooms]
        spans = [(x - 1.95, 20, x + 1.95, 50) for x in self.bridges]
        return (*terraces, *spans)

    def contains(self, x, y):
        for row in {row for _, row in self.stairs}:
            if TILE*row < y < TILE*(row+1):
                return any(stair_row == row and abs(x - TILE*(col+.5)) <= 3.25
                           for col, stair_row in self.stairs)
        return any(l <= x <= r and low <= y <= high for l, low, r, high in self.floor)


ZONES = {
    'camp': ZonePlan('Horský tábor', (4, 0), (5, 3), ((1, 0, 4, 3),)),
    'rim': ZonePlan('Výstupová římsa', (4, 3), (9, 4), (
        (1, 0, 5, 3), (1, 2, 2, 4), (3, 2, 5, 4),
        (5, 1, 7, 2), (6, 2, 9, 3),
    )),
    'halls': ZonePlan('Chodby clon', (6, 7), (7, 6), (
        (8, 9, 24, 23), (15.05, 0, 20.95, 9),
        (24, 12.55, 48, 17.45), (48, 10.5, 64.2, 38.7),
        (53.15, 38.7, 57.95, 47.8), (25.5, 42.2, 53.15, 47.8),
        (7, 39.5, 25.5, 59.4), (0, 52.2, 7, 57.8),
        (64.2, 22.1, 70, 27.9),
    ), interior=True),
    'works': ZonePlan('Dílny a servisní lávka', (0, 7), (6, 8), (
        (1, 1, 6, 2), (4, 0, 6, 1), (1, 5, 5, 7), (5, 5, 6, 6), (2, 7, 4, 8),
    ), bridges=(25,)),
    'dome': ZonePlan('Kopule', (0, 15), (6, 6), (
        (13.2, 21.8, 46.8, 42.2), (18.3, 17, 41.7, 21.8),
        (18.3, 42.2, 41.7, 46), (27, 0, 33, 17),
        (8.2, 23.1, 13.2, 29), (46.8, 23.2, 51.4, 29),
        (26.8, 46, 33.2, 60), (38.3, 12.25, 48, 17),
    ), interior=True),
    'steps': ZonePlan('Schody do nebe', (0, 21), (7, 10), (
        (1, 1, 6, 8), (0, 2, 7, 3), (0, 4, 7, 5), (0, 6, 7, 7),
        (2, 0, 7, 1), (2, 8, 4, 9), (2, 9, 3, 10),
    ), stairs=((2, 2), (4, 4), (3, 6))),
    'walks': ZonePlan('Visuté ochozy', (7, 20), (8, 11), (
        (0, 1, 8, 2), (7, 0, 8, 1), (0, 5, 8, 6), (1, 6, 7, 7),
        (0, 7, 8, 8), (1, 8, 6, 9), (0, 9, 8, 10), (1, 10, 2, 11),
    ), bridges=(25, 55), stairs=((2, 5), (5, 5), (4, 7), (1, 9))),
    'gate': ZonePlan('Předbraní', (2, 31), (7, 7), (
        (1, 1, 6, 4), (0, 1, 1, 3), (6, 1, 7, 3), (2, 4, 5, 6), (0, 4, 7, 5),
        (0, 0, 1, 1), (6, 0, 7, 1), (3, 6, 4, 7),
    ), stairs=((3, 4),)),
    'top': ZonePlan('Poslední stupeň', (2, 38), (7, 7), (
        (2, 1, 5, 3), (1, 3, 6, 5), (2, 5, 5, 6), (0, 2, 7, 3), (3, 0, 4, 1),
    ), stairs=((2, 2),)),
    'study': ZonePlan('Pracovna správkyně', (13, 4), (3, 16), (
        (0, 12.1, 11.4, 17.9), (5.4, 17.9, 11.4, 31),
        (5, 31, 27, 44), (14, 44, 19.8, 47), (5, 47, 27, 58), (0, 52.1, 5, 57.9),
        (20, 58, 26, 83), (26, 72, 28.8, 80), (10, 83, 26, 89),
        (10, 89, 16, 117), (6.5, 99, 10, 107), (10, 117, 23, 123),
        (17, 123, 23, 144), (23, 130, 28.5, 141), (12, 144, 23, 150),
        (12, 150, 18, 160),
    ), interior=True),
}


@dataclass(frozen=True)
class Join:
    first: str
    second: str
    edge: tuple[float, float]
    facing: int
    names: tuple[str, str]
    signs: tuple[str, str]
    required: str = ''
    secret: bool = False

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
    Join('camp', 'rim', (66, 30), 90, ('Na Výstupovou římsu', 'Zpět do tábora'),
         ('VYSTUPOVA RIMSA', 'TABOR')),
    Join('rim', 'halls', (78, 70), 90, ('Vedlejší vchod do Chodeb clon', 'Zpět na Výstupovou římsu'),
         ('CHODBY CLON', 'VYSTUPOVA RIMSA')),
    Join('halls', 'works', (60, 125), 180, ('Do dílen', 'Do chodeb clon'),
         ('DILNY', 'CHODBY CLON')),
    Join('works', 'rim', (53, 70), 270, ('Zpět na Výstupovou římsu', 'Hlavní vstup do Zkušebny'),
         ('VYSTUPOVA RIMSA', 'ZKUSEBNA')),
    Join('works', 'dome', (30, 150), 90, ('Do kopule', 'Zpět do dílen'),
         ('KOPULE', 'DILNY')),
    Join('dome', 'steps', (30, 210), 90, ('Na Schody do nebe', 'Sestoupit do kopule'),
         ('SCHODY DO NEBE', 'KOPULE'), 'hvd_aligned'),
    Join('steps', 'walks', (70, 215), 0, ('K visutým ochozům', 'K patě Schodů do nebe'),
         ('OCHOZY', 'SCHODY DO NEBE')),
    Join('steps', 'gate', (25, 310), 90, ('K západnímu vchodu Předbraní', 'Na Schody do nebe'),
         ('PREDBRANI', 'SCHODY DO NEBE')),
    Join('walks', 'gate', (85, 310), 90, ('K východnímu vchodu Předbraní', 'Zpět na visuté ochozy'),
         ('PREDBRANI', 'OCHOZY')),
    Join('gate', 'top', (55, 380), 90, ('Na Poslední stupeň', 'Ústup do předbraní'),
         ('POSLEDNI STUPEN', 'PREDBRANI'), 'hvd_gate_open'),
    Join('rim', 'study', (130, 55), 0, ('Skalní spára do Pracovny', 'Skalní spára na Výstupovou římsu'),
         ('PRACOVNA', 'VYSTUPOVA RIMSA'), 'hvd_secret_rim', True),
    Join('halls', 'study', (130, 95), 0, ('Za knihovnou do Pracovny', 'Za knihovnou do Chodeb clon'),
         ('PRACOVNA', 'CHODBY CLON'), 'hvd_secret_halls', True),
    Join('study', 'walks', (145, 200), 90, ('Služební výstup na Visuté ochozy', 'Služební sestup do Pracovny'),
         ('OCHOZY', 'PRACOVNA'), 'hvd_secret_exit', True),
)

OPTICS_JOIN = next(join for join in JOINS if join.required == 'hvd_aligned')
GATE_JOIN = next(join for join in JOINS if join.required == 'hvd_gate_open')


# The route stays on the authored lanes. The two arms of the Ochozy share
# their landings and lead to the same north exit.
WALKS = {
    'camp': (((23,16),(26.2,23.8),(26,30)),),
    'rim': (((26,0),(26,9),(26,12)), ((26,12),(33,16),(38,22),(38,40)),
            ((26,12),(19,17),(15,25),(13,32),(13,40))),
    'halls': (((18,0),(18,15),(55.55,15),(55.55,45),(14,45),(14,55),(0,55)),),
    'works': (((53,0),(53,15),(42,16.5),(25,17),(25,52),(34,55),(60,55)),
              ((34,55),(30,65),(30,80))),
    'dome': (((30,0),(30,19),(36,24),(36,37),(30,44),(30,60)),),
    'steps': (((30,0),(30,7),(25,14.5),(25,32),(33,35),(45,36),(45,51.6),
               (41,57.3),(35,59.5),(35,77),(25,85),(25,100)),
              ((30,7),(46,7),(57,5),(70,5))),
    'walks': (((0,15),(25,15),(25,62),(28,65),(45,66),(45,83.9),(15,85),(15,110)),
              ((25,15),(55,16),(55,62),(58,64),(56,66),(45,66))),
    'gate': (((5,0),(5,13),(12,20),(24,34),(35,39.2),(35,70)),
             ((65,0),(65,17),(55,24),(48,32),(47.5,38.9),(35,39.2))),
    'top': (((35,0),(35,9),(25,15.5),(25,31.8),(32,39),(35,54)),),
}
SECRET_WALKS = {
    'rim': (((33,16),(43,16),(55,15),(64.8,16),(65.4,23.5),(73,26),(80,25),(90,25)),),
    'halls': (((55.55,25),(62.5,25),(70,25)),),
    'study': (((0,15),(8.5,15),(8.5,38),(16.9,41),(16.9,49),(12.7,53),(23,54),(23,86),(13,86),(13,120),
               (20,120),(20,147),(15,147),(15,160)),
              ((0,55),(7,55),(12.7,53))),
    'walks': (((75,0),(75,13),(66,15),(55,16)),),
}
LANDMARKS = {
    'camp': ((23,16,'Nocleh'),),
    'rim': ((26,12,'Rozcestí'),),
    'halls': ((15.5,50,'Archiv'), (36,15,'Clony')),
    'works': ((17,16,'Zkušebna'), (18,57,'Kotva')),
    'dome': ((30,31,'Refraktor'),),
    'steps': ((45.1,56.5,'Křídlo'),),
    'walks': ((19,62.7,'Kopí'), (63,62.7,'Lucerna')),
    'top': ((38.15,55.5,'Lucerna'),),
    'study': ((20.7,39.7,'Záložní Kotva'),),
}


def check_plan():
    occupied = set()
    for code, zone in ZONES.items():
        x, y = zone.origin
        w, h = zone.size
        tiles = {(a, b) for a in range(x, x + w) for b in range(y, y + h)}
        if occupied & tiles:
            raise ValueError(f'Overlapping Toolset areas at {code}')
        occupied.update(tiles)
        for l, low, r, high in zone.floor:
            if not (0 <= l < r <= TILE * w and 0 <= low < high <= TILE * h):
                raise ValueError(f'Floor outside Toolset bounds at {code}')
        for walk in (*WALKS.get(code, ()), *SECRET_WALKS.get(code, ())):
            for start, end in zip(walk, walk[1:]):
                for i in range(65):
                    p = tuple(a + (b - a) * i/64 for a, b in zip(start, end))
                    if not zone.contains(*p):
                        raise ValueError(f'Walking line leaves the floor at {code}: {p}')
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
