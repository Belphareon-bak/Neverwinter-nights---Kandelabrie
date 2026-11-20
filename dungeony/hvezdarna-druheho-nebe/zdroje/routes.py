"""Doorway positions, navigation inlays and their native transition volumes."""

from dataclasses import dataclass
from struct import pack

from architecture import BASALT, LIMESTONE
from art import GILT, Material, Mesh
from aurora import bite


@dataclass(frozen=True)
class Threshold:
    x: float
    y: float
    facing: int
    width: float
    label: str

    @property
    def bearing(self):
        return (self.facing - 90) % 360

    @property
    def bounds(self):
        # The transition starts at the front edge of the metal band.
        cross = self.width / 2
        dx, dy = (cross, .44) if self.facing in (90, 270) else (.44, cross)
        return self.x - dx, self.y - dy, self.x + dx, self.y + dy


# A sill sits between actual jambs, with its inscription on the approach side.
THRESHOLDS = {
    'rim_halls': Threshold(40, 57.10, 90, 3.15, 'CHODBY CLON'),
    'rim_works': Threshold(57.58, 24, 0, 5.20, 'DILNY'),
    'halls_study': Threshold(22.9, 58.87, 90, 4.00, 'PRACOVNA'),
    'halls_rim': Threshold(17.775, 7.90, 270, 4.25, 'NOCLEH'),
    'halls_works': Threshold(4.62, 44.90, 180, 3.50, 'DILNY'),
    'halls_dome': Threshold(55.55, 42.32, 90, 4.10, 'KOPULE'),
    'works_halls': Threshold(25, 10.92, 270, 4.50, 'CHODBY CLON'),
    'works_dome': Threshold(25, 61.34, 90, 4.00, 'KOPULE'),
    'works_rim': Threshold(39.63, 15, 0, 5.25, 'NOCLEH'),
    'dome_study': Threshold(48.43, 14.65, 0, 3.55, 'PRACOVNA'),
    'dome_halls': Threshold(30, 14.38, 270, 5.10, 'CHODBY CLON'),
    'dome_works': Threshold(10.03, 26.05, 180, 4.85, 'DILNY'),
    'dome_steps': Threshold(30, 47.05, 90, 5.00, 'SCHODY DO NEBE'),
    'dome_short': Threshold(51.12, 26.08, 0, 4.80, 'PREDBRANI'),
    'steps_dome': Threshold(35, 11.35, 270, 4.95, 'KOPULE'),
    'steps_walks': Threshold(35, 80, 90, 4.95, 'OCHOZY'),
    'steps_eave': Threshold(14.31, 16.65, 180, 3.08, 'SPODNI RIMSA'),
    'steps_eaveup': Threshold(56.68, 54, 0, 4.35, 'SPODNI RIMSA'),
    'study_halls': Threshold(8.475, 4.31, 270, 3.03, 'CHODBY CLON'),
    'study_dome': Threshold(17.25, 23.77, 90, 3.17, 'KOPULE'),
    'eave_steps': Threshold(25, 11.80, 270, 3.80, 'PATA SCHODU'),
    'eave_up': Threshold(25, 80.45, 90, 3.80, 'BOURNA PODESTA'),
    'walks_steps': Threshold(40, 11.56, 270, 4.95, 'BOURNA PODESTA'),
    'walks_gate': Threshold(45, 87.38, 90, 4.95, 'PREDBRANI'),
    'gate_walks': Threshold(35, 12.00, 270, 4.95, 'OCHOZY'),
    'gate_dome': Threshold(56.15, 22, 0, 3.80, 'KOPULE'),
    'gate_top': Threshold(35, 53.51, 90, 4.28, 'POSLEDNI STUPEN'),
    'top_gate': Threshold(35, 11.75, 270, 4.95, 'PREDBRANI'),
    'top_rim': Threshold(35, 58.70, 90, 4.95, 'NOCLEH'),
}

NAMES = {route: f'hvd_sill{index:02}' for index, route in enumerate(THRESHOLDS)}

LETTERS = {
    'A': (14, 17, 17, 31, 17, 17, 17), 'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14), 'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31), 'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (31, 4, 4, 4, 4, 4, 31), 'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31), 'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17), 'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16), 'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30), 'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14), 'V': (17, 17, 17, 17, 17, 10, 4),
    'Y': (17, 17, 10, 4, 4, 4, 4), 'Z': (31, 1, 2, 4, 8, 16, 31),
    ' ': (0,) * 7,
}


def label_texture(label):
    width, height = 256, 32
    start = (width - (6 * len(label) - 1) * 2) // 2
    body = bytearray(bytes((40, 31, 20)) * (width * height))
    for i, letter in enumerate(label):
        for y, row in enumerate(LETTERS[letter]):
            for x in range(5):
                if row & (1 << (4 - x)):
                    for dy in range(2):
                        p = ((22 - 2 * y - dy) * width + start + (6 * i + x) * 2) * 3
                        body[p:p + 6] = bytes((161, 216, 244)) * 2
    return pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, width, height, 24, 0) + body


LABELS = {label: f'hvd_dir{index:02}' for index, label in enumerate(
    dict.fromkeys(sill.label for sill in THRESHOLDS.values()))}


def sill_model(sill):
    mesh = Mesh()
    half = sill.width / 2
    mesh.box(BASALT, 0, 0, -.027, sill.width, .88, .066)
    for y in (-.39, .39):
        mesh.box(LIMESTONE, 0, y, .022, sill.width, .095, .024)
    ink = Material((1, 1, 1), LABELS[sill.label], (.30, .28, .22))
    sign_width = min(sill.width - .18, .76 + .206 * len(sill.label))
    mesh.box(GILT, 0, -.81, -.020, sign_width + .11, .65, .061)
    mesh.polygon(ink, ((-sign_width / 2, -1.11, .045), (sign_width / 2, -1.11, .045),
                       (sign_width / 2, -.51, .045), (-sign_width / 2, -.51, .045)),
                 ((0, 0), (1, 0), (1, 1), (0, 1)))
    for x in (-half + .35, 0, half - .35):
        for d in (-1, 1):
            mesh.trace(GILT, (x + d * .21, -.16, .047), (x, .16, .047), .069)
    return mesh


def route_assets():
    appearances = {NAMES[route]: (f'Práh · {sill.label}', lambda sill=sill: sill_model(sill))
                   for route, sill in THRESHOLDS.items()}
    textures = {f'{resource}.tga': label_texture(label) for label, resource in LABELS.items()}
    return appearances, textures


def transition(area, name, tag, target, *, require='', flag=''):
    route = tag.removeprefix('hvt_')
    sill = THRESHOLDS[route]
    area.transition(name, tag, sill.bounds, target, require=require, flag=flag)
    asset = NAMES[route]
    if not require:
        area.prop(area.art[asset], name, sill.x, sill.y, bearing=sill.bearing)
    # The waypoint gives the real destination on the map, at the same location as the sill.
    # CreateObject takes a compass facing. The static placeable bearing is offset by 90 degrees.
    area.point('hvd_route', sill.x, sill.y, sill.facing, f'Přechod · {name}',
               required=require, resource=asset)
    if require:
        area.waypoints[-1].fields['MapNoteEnabled'] = bite(0)
