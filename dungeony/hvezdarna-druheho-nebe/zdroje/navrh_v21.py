"""Service rooms, shrine approaches and optical paths for the v21 proposal."""

from dataclasses import dataclass
from itertools import product


FILTER_FLOOR = ((33.0,21.5,41.98,39.0), (41.98,21.5,46.0,25.05), (41.98,31.25,46.0,39.0))
FILTER_ROOM = ((33.0,21.5), (46.0,21.5), (46.0,25.05), (41.98,25.05),
               (41.98,31.25), (46.0,31.25), (46.0,39.0), (33.0,39.0))
MIXING_ROOM = ((18.0, 21.5), (31.5, 21.5), (31.5, 39.0), (12.0, 39.0),
               (12.0, 26.4), (18.0, 26.4))
MIXING_FLOOR = ((18.0,21.5,31.5,39.0), (12.0,26.4,18.0,39.0))
HALL_ACCESS = (42.55, 25.6, 47.0, 27.7)
ACCESS_TURN = (42.55, 27.7, 44.85, 32.25)
HALL_PREVIEW = (41.0, 31.25, 44.85, 34.40)
SERVICE_PREVIEW = (47.0, 25.6, 50.4, 27.7)
R1_FRAME = (43.7, 30.0)
R1_WIDTH = ACCESS_TURN[2] - ACCESS_TURN[0]
R1_TRIGGER = (ACCESS_TURN[0], 29.35, ACCESS_TURN[2], 30.20)
R1_SAFE_RETURN = (48.58, 26.65, 0)
BREACH = (31.5, 28.5, 33.0, 30.9)
OPTICAL_SLOT = (32.25, 24.5)
ACCESS_DOOR = (46.5, 26.65)
ACCESS_SIGN = (46.95, 23.55)
REPAIR_PASSAGES = (
    ('halls', 'service', 'Do světelného servisu', R1_TRIGGER, (43.7, 30.73, 90)),
    ('service', 'halls', 'Zpět do Chodeb clon', R1_TRIGGER, (43.7, 28.68, 270)),
)
R1_APPROACH = ((49.9,26.65), ACCESS_DOOR, (43.7,26.65), R1_FRAME)
SERVICE_WALK = (R1_FRAME, (43.7,32.52), (41.0,32.45), (35.35,29.7), (32.25,29.7),
                (29.3,29.7), (25.7,31.4), (21.45,33.4), (17.6,33.4))
HALL_PANEL = (13.0, 23.5)
SERVICE_ROOMS = (*FILTER_FLOOR, *MIXING_FLOOR, HALL_ACCESS, ACCESS_TURN, SERVICE_PREVIEW, BREACH)
BEAM_HEIGHT = 2.62
SLOT_WIDTH = .88
RUBBLE_HIT = (36.95, 35.7)

RUBBLE = (
    ((33.0, 33.35), (35.4, 33.15), (37.85, 34.55), (37.35, 36.55),
     (35.85, 37.6), (33.0, 38.5)),
    ((31.5, 33.0), (27.1, 33.05), (26.65, 34.8), (27.8, 36.6),
     (29.7, 38.3), (31.5, 38.6)),
)

SOURCE = (44.1, 35.7)
SOURCE_LIP = .692
Z1 = (40.5, 35.7)
Z2 = (39.0, 24.5)
PRISM = (27.25, 24.5)
RED = (20.5, 24.5)
GREEN = (26.35, 29.4)
BLUE = (28.8, 28.2)
MIXER = (22.4, 35.15)
PILOT = (13.95, 30.2)
DEFLECTOR = (18.45, 36.55)
OUTLET = (12.85, 36.55)
IRIS = (14.35, 36.55)
PILOT_IRIS = (13.3, 33.75)
PILOT_STAR = (16.9, 31.65)
OUTLET_PANEL = (12.22, 34.52)
LANTERN = (38.15, 55.5)
ITHREN = (35.0, 50.82)

FEED_RAY = ((SOURCE[0] - SOURCE_LIP, SOURCE[1]), Z1)
FILTER_DETOUR = (Z1, Z2)
WHITE_TO_PRISM = (Z2, PRISM)
WHITE_TO_RUBBLE = (Z1, RUBBLE_HIT)
WHITE_TO_GAUGE = (Z2, (36.45, 22.35))
RED_TO_MIX = (RED, (19.75, 34.1), MIXER)
RED_TO_GAUGE = (RED, (20.5, 22.1))
GREEN_TO_PILOT = (GREEN, PILOT)
GREEN_TO_MIX = (GREEN, MIXER)
BLUE_TO_MIX = (BLUE, (24.75, 30.7), MIXER)
BLUE_TO_RUBBLE = (BLUE, (28.8, 33.65))
bx, by = BLUE_TO_RUBBLE[-1]
RUBBLE_BLOCKS = (
    (RUBBLE_HIT[0]-.78, RUBBLE_HIT[1]-.535, RUBBLE_HIT[0], RUBBLE_HIT[1]+.535, 2.79),
    (bx-.565, by, bx+.565, by+.74, 2.75),
)
MIXED_RAY = (MIXER, DEFLECTOR)
PURPLE_TO_OUTLET = (DEFLECTOR, OUTLET)
PURPLE_TO_GAUGE = (DEFLECTOR, (15.25, 38.1))

R, G, B, WHITE = 1, 2, 4, 7


@dataclass(frozen=True)
class Aim:
    title: str
    mode: int
    rays: tuple


def aim(title, path, color=WHITE, mode=0):
    return Aim(title, mode, ((color, path),))


@dataclass(frozen=True)
class Optic:
    label: str
    center: tuple[float, float]
    approach: tuple[float, float]
    initial: int
    aims: tuple[Aim, Aim, Aim]


# Mode 1 reaches the next station. Mode 2 sends green to the mixer.
# A prism in mode 4 only sends blue to the corresponding mirror.
OPTICS = (
    Optic('Z1 · Přívodní zrcadlo', Z1, (41.25, 34.55), 0, (
        aim('zasypané vedení', WHITE_TO_RUBBLE),
        aim('obchvat k Z2', FILTER_DETOUR, mode=1),
        aim('kontrolní destička', (Z1, (39.4, 38.1))),
    )),
    Optic('Z2 · Zrcadlo u průzoru', Z2, (39.5, 25.85), 2, (
        aim('zkušební stupnice', WHITE_TO_GAUGE),
        aim('průzor k hranolu', WHITE_TO_PRISM, mode=1),
        aim('jižní záchyt', (Z2, (41.55, 22.25))),
    )),
    Optic('Hranol · Rozklad světla', PRISM, (26.95, 25.8), 0, (
        Aim('zkušební spektrum', 0, ((R, (PRISM, (25.0, 22.65))), (G, (PRISM, (26.15, 22.4))),
                                     (B, (PRISM, (27.2, 22.3))))),
        Aim('odchylka k modrému kanálu', 4, ((R, (PRISM, (25.0, 22.65))), (G, (PRISM, (26.15, 22.4))),
                                             (B, (PRISM, BLUE)))),
        Aim('tři servisní kanály', 1, ((R, (PRISM, RED)), (G, (PRISM, GREEN)), (B, (PRISM, BLUE)))),
    )),
    Optic('Trojúhelník · Červené zrcadlo', RED, (21.3, 25.45), 0, (
        aim('jižní stupnice', RED_TO_GAUGE, R),
        aim('směšovač přes západní odraz', RED_TO_MIX, R, 1),
        aim('zkušební sklo', (RED, (23.8, 26.25)), R),
    )),
    Optic('Čtverec · Zelené zrcadlo', GREEN, (25.6, 30.45), 0, (
        aim('směšovač', GREEN_TO_MIX, G, 2),
        aim('zrcadlo pojistky', GREEN_TO_PILOT, G, 1),
        aim('severní stupnice', (GREEN, (27.35, 31.9)), G),
    )),
    Optic('Kruh · Modré zrcadlo', BLUE, (29.65, 29.35), 2, (
        aim('zasypaný průzor', BLUE_TO_RUBBLE, B),
        aim('obchvat do směšovače', BLUE_TO_MIX, B, 1),
        aim('východní stupnice', (BLUE, (30.75, 26.25)), B),
    )),
    Optic('Směšovač barev', MIXER, (22.2, 33.95), 1, (
        aim('zkušební sklo směsi', (MIXER, (24.9, 36.7)), 0),
        aim('severní záchyt', (MIXER, (20.15, 37.82)), 0),
        aim('výstupní zrcadlo', MIXED_RAY, 0, 1),
    )),
    Optic('Zelená pojistka výstupu', PILOT, (15.15, 30.15), 2, (
        aim('spodní zkušební deska', (PILOT, (16.8, 28.2)), G),
        aim('čidlo Slunce', (PILOT, PILOT_IRIS), G, 1),
        aim('čidlo Hvězda', (PILOT, PILOT_STAR), G, 2),
    )),
    Optic('Výstup do světlovodu', DEFLECTOR, (18.3, 35.4), 0, (
        aim('zkušební deska výstupu', PURPLE_TO_GAUGE, 0),
        aim('bezpečný záchyt', (DEFLECTOR, (20.65, 36.7)), 0),
        aim('světlovod k lucerně', PURPLE_TO_OUTLET, 0, 1),
    )),
)
SOLUTION = (1, 1, 2, 1, 1, 1, 2, 1, 2)


def light_result(settings, pilot_line=1):
    z1, z2, prism, red, green, blue, mixer, pilot, exit_ = (
        optic.aims[mark].mode for optic, mark in zip(OPTICS, settings, strict=True)
    )
    if not z1 or not z2:
        return 0, False
    mixed = (R if prism == 1 and red == 1 else 0) | (G if prism == 1 and green == 2 else 0)
    if prism and blue == 1:
        mixed |= B
    opens = prism == 1 and green == 1 and pilot == pilot_line
    return mixed, opens and bool(mixer and exit_) and mixed == R | B


def check_solution():
    for pilot_line in (1, 2):
        expected = SOLUTION[:7]+(pilot_line,)+SOLUTION[8:]
        valid = [marks for marks in product(range(3), repeat=len(OPTICS)) if light_result(marks,pilot_line)[1]]
        if valid != [expected]:
            raise ValueError(f'Expected one path for pilot line {pilot_line}, got {valid}')
    return 3**len(OPTICS)


def check_ray_paths():
    slot_y = OPTICAL_SLOT[1]
    beam_space = (*FILTER_FLOOR, *MIXING_FLOOR, (31.5, slot_y-SLOT_WIDTH/2, 33.0, slot_y+SLOT_WIDTH/2))
    paths = [FEED_RAY, (DEFLECTOR, IRIS)]
    paths.extend(path for optic in OPTICS for choice in optic.aims for _, path in choice.rays)
    for path in paths:
        for (x,y),(u,v) in zip(path,path[1:]):
            for step in range(129):
                xx, yy = x+(u-x)*step/128, y+(v-y)*step/128
                if not any(l <= xx <= r and b <= yy <= t for l,b,r,t in beam_space):
                    raise ValueError(f'Optical path leaves the rooms or misses the slot: {path}')
                if any(l < xx < r and b < yy < t and height > BEAM_HEIGHT
                       for l,b,r,t,height in RUBBLE_BLOCKS):
                    raise ValueError(f'Optical path continues into the rock face: {path}')


@dataclass(frozen=True)
class Shrine:
    key: str
    name: str
    guardian: str
    seal: tuple[float, float]
    stand: tuple[float, float]
    door: tuple[float, float]
    corridor: tuple[float, float, float, float]
    footprint: tuple[tuple[float, float], ...]
    approach: tuple[tuple[float, float], ...]
    furnishings: tuple[tuple[float, float, float, float], ...]
    center: tuple[float, float]
    entrance: float


SHRINES = (
    Shrine('K', 'Svatyně Kopí', 'Kopiník', (11.45, 78.5), (13.35, 76.7),
           (17.55, 68.0), (15.85, 65.6, 19.25, 69.0),
           ((5, 71), (8, 68), (20, 68), (20, 81), (16, 84), (5, 81)),
           ((24.8, 63.8), (22.15, 66.5), (17.55, 67.6), (17.55, 71.0),
            (15.62, 72.85), (13.85, 76.35), (11.85, 77.25)),
           ((6.0, 72.8, 7.25, 74.9), (6.0, 76.8, 7.25, 79.0)), (12.9, 76.3), -52.0),
    Shrine('L', 'Svatyně Lucerny', 'Světlonoš', (70.6, 78.65), (68.3, 76.65),
           (64.3, 69.0), (62.6, 65.6, 66.0, 70.0),
           ((60, 69), (74, 69), (77, 73), (77, 80), (72, 84), (61, 82), (60, 78)),
           ((58, 64.8), (62.75, 66.5), (64.3, 68.0), (64.3, 71.45),
            (66.03, 73.0), (68.25, 77.0), (70.05, 77.7)),
           ((74.75, 74.2, 75.85, 75.7), (74.75, 77.0, 75.85, 78.5)), (68.5, 76.5), -125.0),
)
