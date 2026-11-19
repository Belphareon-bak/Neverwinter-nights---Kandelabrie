"""Original observatory architecture and instruments for the bundled art HAK."""

from collections import defaultdict
from dataclasses import dataclass
from math import cos, pi, sin, sqrt, tau
import random
import struct


@dataclass(frozen=True)
class Material:
    tint: tuple
    texture: str
    glow: tuple = (0, 0, 0)
    alpha: float = 1.0
    shadow: int = 0


STONE = Material((.76, .79, .88), "hvd_stone")
TRIM = Material((.91, .84, .70), "hvd_stone")
DARK = Material((.51, .56, .69), "hvd_stone")
CROWN = Material((.59, .74, .72), "hvd_copper")
BRASS = Material((.94, .73, .40), "hvd_brass", (.07, .045, .014))
GILT = Material((1, .76, .37), "hvd_brass", (.36, .21, .066), shadow=0)
BLUE = Material((.51, .68, 1), "hvd_glass", (.30, .45, .86), shadow=0)
AMBER = Material((.98, .73, .37), "hvd_glass", (.70, .40, .10), shadow=0)
RIFT = Material((.63, .75, 1), "hvd_glass", (.45, .54, .86), alpha=.72, shadow=0)
FOG = Material((.70, .79, .95), "hvd_clouds", (.48, .52, .66), alpha=.88, shadow=0)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, s):
    return tuple(x * s for x in a)


def cross(a, b):
    x, y, z = a
    u, v, w = b
    return (y * w - z * v, z * u - x * w, x * v - y * u)


def unit(a):
    return scale(a, 1 / sqrt(sum(x * x for x in a)))


class Mesh:
    def __init__(self):
        self.faces = defaultdict(list)

    def polygon(self, material, points, uv=None):
        self.faces[material].append((tuple(points), uv))

    def box(self, material, x, y, z, w, d, h):
        bottom = [(x + dx * w / 2, y + dy * d / 2, z)
                  for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        top = [add(p, (0, 0, h)) for p in bottom]
        self.polygon(material, top)
        self.polygon(material, list(reversed(bottom)))
        for i in range(4):
            j = (i + 1) % 4
            self.polygon(material, (bottom[i], bottom[j], top[j], top[i]))

    def tube(self, material, a, b, ra, rb=None, sides=16, open_ends=False):
        axis = unit(tuple(y - x for x, y in zip(a, b)))
        u = unit(cross((0, 0, 1) if abs(axis[2]) < .95 else (0, 1, 0), axis))
        v = cross(axis, u)
        rb = ra if rb is None else rb
        rings = []
        for center, radius in ((a, ra), (b, rb)):
            rings.append([add(center, add(scale(u, cos(tau * i / sides) * radius),
                                          scale(v, sin(tau * i / sides) * radius))) for i in range(sides)])
        start, end = rings
        for i in range(sides):
            j = (i + 1) % sides
            self.polygon(material, (start[i], start[j], end[j], end[i]))
        if not open_ends:
            self.polygon(material, list(reversed(start)))
            self.polygon(material, end)

    def disc(self, material, a, b, radius, sides=24):
        self.tube(material, a, b, radius, sides=sides)

    def ring(self, material, radius, width, z, sides=48, x=0, y=0):
        for i in range(sides):
            a, b = tau * i / sides, tau * (i + 1) / sides
            self.polygon(material, [(x + r * cos(t), y + r * sin(t), z)
                                   for t, r in ((a, radius + width), (b, radius + width),
                                                (b, radius), (a, radius))])

    def trace(self, material, a, b, width=.04):
        u = unit(cross((0, 0, 1), tuple(y - x for x, y in zip(a, b))))
        offset = scale(u, width / 2)
        self.polygon(material, (add(a, offset), add(a, scale(offset, -1)),
                                add(b, scale(offset, -1)), add(b, offset)))

    def mdl(self, name):
        lines = [f"newmodel {name}", f"setsupermodel {name} NULL", "classification Other",
                 "setanimationscale 1.0", f"beginmodelgeom {name}", f"node dummy {name}",
                 "  parent NULL", "endnode"]
        for index, (mat, polygons) in enumerate(self.faces.items()):
            vertices, texture, faces = [], [], []
            for polygon, uv in polygons:
                start = len(vertices)
                vertices.extend(polygon)
                if uv is None:
                    uv = [(x * .28 + y * .08, (y + z) * .26) for x, y, z in polygon]
                texture.extend(uv)
                faces.extend((start, start + j, start + j + 1)
                             for j in range(1, len(polygon) - 1))
            tint = " ".join(map(str, mat.tint))
            glow = " ".join(map(str, mat.glow))
            lines.extend([f"node trimesh {name}_{index}", f"  parent {name}",
                          "  position 0 0 0", "  orientation 0 0 1 0", f"  ambient {tint}",
                          f"  diffuse {tint}", f"  selfillumcolor {glow}", f"  bitmap {mat.texture}",
                          "  render 1", f"  shadow {mat.shadow}", f"  alpha {mat.alpha}",
                          f"  transparencyhint {int(mat.alpha < 1)}", f"  verts {len(vertices)}"])
            lines.extend("    %.5f %.5f %.5f" % point for point in vertices)
            lines.append(f"  tverts {len(texture)}")
            lines.extend("    %.5f %.5f 0" % point for point in texture)
            lines.append(f"  faces {len(faces)}")
            lines.extend("    %d %d %d 0 %d %d %d 0" % (face * 2) for face in faces)
            lines.append("endnode")
        lines.extend([f"endmodelgeom {name}", f"donemodel {name}", ""])
        return "\n".join(lines).encode("ascii")


def arch(mesh, radius, spring, y, thickness, depth, material, *, masonry=False):
    steps = 12
    for i in range(steps):
        a, b = pi * (i + (.035 if masonry else 0)) / steps, pi * (i + 1 - (.035 if masonry else 0)) / steps
        front = [(r * cos(t), y - depth / 2, spring + r * sin(t))
                 for r, t in ((radius + thickness, a), (radius + thickness, b), (radius, b), (radius, a))]
        back = [add(p, (0, depth, 0)) for p in front]
        mesh.polygon(material, front)
        mesh.polygon(material, list(reversed(back)))
        for j in range(4):
            k = (j + 1) % 4
            mesh.polygon(material, (front[k], front[j], back[j], back[k]))
    for sign in (-1, 1):
        mesh.box(material, sign * (radius + thickness / 2), y, 0, thickness, depth, spring)


def star(mesh, x, y, z, r, mat, facets=8):
    points = [(x + cos(i * pi / facets) * r * (1 if i % 2 == 0 else .29),
               y + sin(i * pi / facets) * r * (1 if i % 2 == 0 else .29), z)
              for i in range(2 * facets)]
    for i in range(len(points)):
        mesh.polygon(mat, ((x, y, z), points[i], points[(i + 1) % len(points)]))


def observatory():
    m = Mesh()
    wall, radius, sectors = 4.4, 6.1, 16
    # Raised lower plinth. The south bay stays open at the entrance.
    for i in range(sectors):
        a, b = -pi / 2 + (i - .5) * tau / sectors, -pi / 2 + (i + .5) * tau / sectors
        def corner(theta, r, z):
            return (r * cos(theta), r * sin(theta), z)
        if i not in (15, 0, 1):
            for z0, z1, r, material in ((0, .42, 6.35, TRIM), (.42, 3.8, radius, STONE),
                                        (3.8, 4.12, 6.27, TRIM), (4.12, wall, 6.43, DARK)):
                m.polygon(material, (corner(a, r, z0), corner(b, r, z0),
                                     corner(b, r, z1), corner(a, r, z1)))
            middle = (a + b) / 2
            if i % 2 == 0:
                span = .069
                m.polygon(BRASS, (corner(middle - span, 6.19, 1.1), corner(middle + span, 6.19, 1.1),
                                  corner(middle + span, 6.19, 3.12), corner(middle - span, 6.19, 3.12)))
                m.polygon(AMBER, (corner(middle - .043, 6.21, 1.25), corner(middle + .043, 6.21, 1.25),
                                  corner(middle + .043, 6.21, 2.94), corner(middle - .043, 6.21, 2.94)))
            m.tube(DARK, corner(a, 6.1, 0), corner(a, 6.1, 3.9), .20, .13, sides=8)
        for j in range(7):
            p, q = j * pi / 14, (j + 1) * pi / 14
            def roof(t, u):
                return corner(t, 6.47 * cos(u), wall + 4.4 * sin(u))
            m.polygon(CROWN if i % 3 else DARK, (roof(a, p), roof(b, p), roof(b, q), roof(a, q)))
            if i % 2 == 0 and j < 6:
                m.tube(BRASS, roof(a, p), roof(a, q), .050, sides=6)
    m.disc(BRASS, (0, 0, 8.58), (0, 0, 8.99), .65)
    m.tube(BRASS, (0, 0, 8.8), (0, 0, 10.35), .13, .052, sides=10)
    m.tube(BRASS, (-1.35, 0, 9.67), (1.35, 0, 9.67), .06, sides=8)
    for x in (-1.37, 1.37):
        m.disc(AMBER, (x, 0, 9.55), (x, 0, 9.79), .15, sides=10)
    arch(m, 2.63, 2.35, -6.0, .55, 1.0, TRIM, masonry=True)
    arch(m, 2.68, 2.35, -6.56, .083, .09, BRASS)
    for x in (-3.4, 3.4):
        m.box(DARK, x, -5.85, 0, .55, .75, 2.8)
        m.box(TRIM, x, -5.85, 2.8, .79, .98, .24)
    # Recess the actual threshold between the walls of the vestibule.
    for side in (-1, 1):
        m.box(DARK, 2.31 * side, -3.46, 0, 1.49, .35, 4.45)
        m.box(STONE, 1.80 * side, -2.01, 0, .40, 2.75, 3.57)
    m.box(DARK, 0, -3.46, 3.47, 3.15, .35, .98)
    m.box(DARK, 0, -.63, 0, 3.98, .35, 3.60)
    m.box(DARK, 0, -2.0, 3.43, 3.58, 2.77, .16)
    m.box(TRIM, 0, -1.98, -.05, 3.13, 2.94, .09)
    arch(m, 1.58, 1.85, -3.83, .18, .21, BRASS)
    m.box(TRIM, 0, -4.24, 0, 5.45, 1.55, .18)
    return m


def plinth():
    m = Mesh()
    m.tube(DARK, (0, 0, 0), (0, 0, .22), 2.0, 1.9, sides=16)
    m.tube(STONE, (0, 0, .22), (0, 0, .95), 1.54, 1.13, sides=12)
    m.disc(TRIM, (0, 0, .91), (0, 0, 1.12), 1.46)
    m.disc(BRASS, (0, 0, 1.10), (0, 0, 1.31), 1.30)
    for x in (-.97, .97):
        m.tube(BRASS, (x, 0, 1.27), (x, .10, 2.58), .25, .18, sides=10)
        m.disc(DARK, (x - .33, .10, 2.58), (x + .33, .10, 2.58), .33, sides=12)
        m.disc(GILT, (x - .36, .10, 2.58), (x + .36, .10, 2.58), .16, sides=12)
    return m


def refractor():
    m = Mesh()
    def center(t):
        return (0, -2.46 + 5.14 * t, 2.45 + 1.19 * t)
    for t0, t1, r0, r1, mat in ((0, .15, .21, .45, BRASS), (.15, .49, .45, .56, DARK),
                                (.49, .78, .56, .72, CROWN), (.78, .97, .72, .87, BRASS),
                                (.97, 1, .91, .91, TRIM)):
        m.tube(mat, center(t0), center(t1), r0, r1, open_ends=True, sides=24)
    for t, r in ((.15, .48), (.28, .54), (.49, .60), (.63, .68), (.78, .76), (.93, .89), (.985, .94)):
        m.tube(BRASS, center(t - .014), center(t + .014), r, sides=24, open_ends=True)
    m.disc(GILT, center(-.037), center(0), .23)
    m.disc(BLUE, center(.983), center(1.005), .80)
    for x in (-.42, .42):
        m.tube(GILT, add(center(.47), (x, 0, .36)), add(center(.92), (x, 0, .58)), .053, sides=8)
    m.tube(BRASS, (.47, -1.43, 3.18), (.52, .59, 3.65), .13, .17)
    return m


def dial(console=False):
    m = Mesh()
    m.disc(DARK, (0, 0, 0), (0, 0, .18), .77, sides=10)
    m.tube(STONE, (0, 0, .18), (0, 0, .94), .47, .37, sides=10)
    m.disc(TRIM, (0, 0, .92), (0, 0, 1.10), .64)
    m.tube(BRASS, (0, 0, 1.11), (0, 0, 1.26), .58, .45, sides=18)
    m.ring(GILT, .49, .048, 1.27)
    if console:
        m.disc(DARK, (0,0,1.258), (0,0,1.274), .475, sides=24)
        for i in range(3):
            a = pi/2 + i*tau/3
            m.trace(GILT, (.40*cos(a), .40*sin(a), 1.28),
                    (.48*cos(a), .48*sin(a), 1.28), .045)
    else:
        m.trace(GILT, (-.28, -.22, 1.275), (.36, .27, 1.275), .11)
        m.tube(BRASS, (.35, .28, 1.25), (.38, .29, 1.60), .065, .09)
    m.disc(BLUE, (0, 0, 1.25), (0, 0, 1.33), .17)
    return m


def needle():
    m = Mesh()
    m.trace(BRASS, (0, -.11, 1.35), (0, .34, 1.35), .10)
    m.polygon(AMBER, ((-.11, .26, 1.36), (.11, .26, 1.36), (0, .44, 1.36)))
    return m


def fitted_mirror():
    m = Mesh()
    m.tube(BRASS, (0,0,1.23), (0,0,1.61), .145, .08, sides=10)
    m.disc(BRASS, (0,.05,1.86), (0,-.065,1.86), .36, sides=20)
    m.disc(BLUE, (0,-.063,1.86), (0,-.083,1.86), .306, sides=20)
    return m


def colonnade():
    m = Mesh()
    arch(m, 3.0, 2.84, 0, .32, .72, STONE, masonry=True)
    arch(m, 3.03, 2.84, -.391, .05, .070, BRASS)
    for x in (-3.26, 3.26):
        for z in (.06, .35, 2.54, 2.75):
            m.box(TRIM, x, 0, z, .66, .98, .14)
    return m


def sealed_arch():
    m = Mesh()
    arch(m, 2.49, 3.0, 0, .81, 1.63, STONE, masonry=True)
    arch(m, 3.30, 3.0, -.97, .20, .36, TRIM)
    arch(m, 2.56, 3.0, -.98, .08, .14, BRASS)
    arch(m, 2.65, 3.0, -.98, .06, .10, GILT)
    for x in (-3.46, 3.46):
        m.box(DARK, x, .16, 0, .87, 1.97, 2.68)
        for z in (.12, .36, 2.55, 2.75):
            m.box(TRIM, x, .16, z, 1.04, 2.13, .12)
        m.box(BRASS, x, -1.00, 1.31, .17, .14, 1.10)
        m.disc(BLUE, (x, -1.11, 1.89), (x, -1.22, 1.89), .19, sides=12)
    for i in range(5):
        a = pi * (i + 1) / 6
        x, z = 2.94 * cos(a), 3 + 2.94 * sin(a)
        m.disc(BRASS, (x, -.93, z), (x, -1.03, z), .14, sides=8)
    m.disc(GILT, (0, -.99, 6.26), (0, -1.12, 6.26), .37, sides=8)
    m.disc(BLUE, (0, -1.11, 6.26), (0, -1.15, 6.26), .22, sides=8)
    return m


def portal():
    m = Mesh()
    arch(m, 2.27, 3.0, 0, .16, .15, BLUE)
    arch(m, 2.40, 3.0, -.07, .07, .075, GILT)
    contour = [(2.23 * cos(i * pi / 24), -.045, 3 + 2.23 * sin(i * pi / 24))
               for i in range(25)] + [(-2.23, -.045, .15), (2.23, -.045, .15)]
    for viewing_side in (contour, list(reversed(contour))):
        m.polygon(RIFT, viewing_side, [(x / 4.7 + .5, z / 5.3) for x, _, z in viewing_side])
    m.ring(GILT, 2.22, .075, .045)
    m.ring(BLUE, 1.91, .035, .047)
    return m


def seal_stand():
    m = Mesh()
    m.disc(DARK, (0, 0, 0), (0, 0, .17), .74, sides=8)
    m.tube(STONE, (0, 0, .16), (0, 0, .97), .53, .37, sides=8)
    m.tube(TRIM, (0, 0, .95), (0, 0, 1.18), .64, .67, sides=8)
    m.disc(BRASS, (0, 0, 1.18), (0, 0, 1.24), .57)
    m.ring(GILT, .40, .040, 1.253)
    m.disc(DARK, (0, 0, 1.22), (0, 0, 1.266), .27)
    return m


def lamp():
    m = Mesh()
    m.disc(DARK, (0, 0, 0), (0, 0, .29), .68, sides=8)
    m.tube(STONE, (0, 0, .26), (0, 0, 1.54), .49, .31, sides=8)
    m.disc(BRASS, (0, 0, 1.55), (0, 0, 1.72), .49, sides=12)
    m.disc(AMBER, (0, 0, 1.70), (0, 0, 2.52), .28, sides=12)
    for i in range(6):
        a = tau * i / 6
        x, y = .335 * cos(a), .335 * sin(a)
        m.tube(BRASS, (x, y, 1.67), (x, y, 2.51), .052, sides=6)
    m.tube(TRIM, (0, 0, 2.50), (0, 0, 2.83), .54, .10, sides=8)
    m.tube(BRASS, (0, 0, 2.79), (0, 0, 3.05), .13, .055, sides=8)
    return m


def star_chart():
    m = Mesh()
    for radius, width in ((2.20, .055), (3.82, .053), (5.59, .08), (5.95, .039), (6.59, .076)):
        m.ring(GILT, radius, width, .015)
    for i in range(48):
        a = i * tau / 48
        start = 5.61 if i % 4 == 0 else 6.0
        m.trace(GILT, (start * cos(a), start * sin(a), .017), (6.59 * cos(a), 6.59 * sin(a), .017),
                .048 if i % 4 == 0 else .029)
    constellation = [(-5, .6), (-3.2, 2.4), (-1.0, 1.7), (1.1, 3.4), (3.1, 2.25), (4.85, .6)]
    for i, (x,y) in enumerate(constellation):
        star(m, x, y, .025, .22 if i % 2 else .29, BLUE, 4)
        if i:
            m.trace(GILT, (*constellation[i-1], .019), (x, y, .019), .027)
    for i in range(4):
        a = tau * i / 4
        star(m, 6.93 * cos(a), 6.93 * sin(a), .024, .30, GILT, 4)
    return m


def railing():
    m = Mesh()
    m.box(DARK, 0, 0, 0, 4.85, .34, .17)
    for i in range(7):
        x = -2.3 + i * (4.6 / 6)
        m.tube(STONE, (x, 0, .15), (x, 0, .77), .126, .086, sides=8)
    m.box(STONE, 0, 0, .75, 4.85, .29, .15)
    m.box(TRIM, 0, 0, .90, 4.96, .37, .11)
    return m


def beam_strip():
    m = Mesh()
    for x in (-.82, .82):
        m.trace(GILT, (x, -3.6, .022), (x, 3.6, .022), .063)
    for y in (-3.3, -1.6, 0, 1.6, 3.3):
        m.trace(BLUE, (-.78, y - .21, .025), (0, y + .17, .025), .05)
        m.trace(BLUE, (0, y + .17, .025), (.78, y - .21, .025), .05)
    return m


def threshold():
    m = Mesh()
    for x in (-1.65, 1.65):
        star(m, x, 0, .018, .22, GILT, 4)
    m.ring(BLUE, .61, .027, .022, 24)
    star(m, 0, 0, .026, .39, GILT, 4)
    return m


def sector(sign):
    m = Mesh()
    m.ring(GILT, .58, .030, .018, 24)
    for i in range(sign):
        m.trace(BLUE if sign == 2 else GILT, ((i - (sign - 1) / 2) * .21, -.25, .023),
                ((i - (sign - 1) / 2) * .21, .25, .023), .056)
    return m


def cloud_shelf():
    m = Mesh()
    r = 65
    m.polygon(FOG, [(-r, -r, 0), (r, -r, 0), (r, r, 0), (-r, r, 0)],
              [(0, 0), (1, 0), (1, 1), (0, 1)])
    return m


MODELS = {
    "hvd_octagon": ("Kopule observatoře", observatory),
    "hvd_plinth": ("Podstavec refraktoru", plinth),
    "hvd_refractor": ("Mosazný refraktor", refractor),
    "hvd_dial": ("Ruční ovládání clony", dial),
    "hvd_columnade": ("Oblouk s mosaznou lištou", colonnade),
    "hvd_gatearch": ("Kamenná brána tří pečetí", sealed_arch),
    "hvd_gateway": ("Otevřená nebeská brána", portal),
    "hvd_sealstand": ("Podstavec pečeti", seal_stand),
    "hvd_beacon": ("Návratová lucerna", lamp),
    "hvd_starmap": ("Mosazná mapa oblohy", star_chart),
    "hvd_rail": ("Kamenná balustráda", railing),
    "hvd_beamstrip": ("Značení mezí výboje", beam_strip),
    "hvd_threshold": ("Vložený znak přechodu", threshold),
    "hvd_sector1": ("Jedna ryska", lambda: sector(1)),
    "hvd_sector2": ("Dvě rysky", lambda: sector(2)),
    "hvd_sector3": ("Tři rysky", lambda: sector(3)),
    "hvd_cloudbed": ("Vrstva mraků pod mosty", cloud_shelf),
}

INTERACTIVE_MODELS = {
    "hvd_console": ("Pevná stupnice clony", lambda: dial(True)),
    "hvd_needle": ("Mosazný ukazatel stupnice", needle),
    "hvd_mirror_set": ("Usazené zkušební zrcadlo", fitted_mirror),
}


def texture(name, size, base, seed, *, slabs=False):
    rng = random.Random(seed)
    stars = {(rng.randrange(size), rng.randrange(size)): rng.randrange(70, 158) for _ in range(280)}
    pixels = bytearray()
    depth = 32 if name == "hvd_clouds" else 24
    for y in range(size):
        for x in range(size):
            wave = sin(x * .11 + sin(y * .07) * 3) * 7 + cos(y * .27 - x * .035) * 5
            grain = rng.randrange(-9, 10)
            star_power = stars.get((x, y), 0) if name == "hvd_glass" else 0
            if slabs:
                row, seam_y = divmod(y, 32)
                column, seam_x = divmod(x + 16 * (row % 2), 32)
                wave += 6 * sin(column * 2 + row)
                if seam_x == 0 or seam_y == 0:
                    wave -= 27
                elif seam_x == 1 or seam_y == 1:
                    wave += 16
            colors = [max(0, min(255, int(channel + wave + grain + star_power))) for channel in base]
            pixels.extend(reversed(colors))
            if depth == 32:
                cloud = (sin(x * .038 + cos(y * .067)) + cos(y * .047 + sin(x * .069)) +
                         .55 * sin((x + y) * .072) + .37 * cos((x - y) * .103))
                pixels.append(max(18, min(207, int(109 + 43 * cloud))))
    return struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, size, size, depth, 8 if depth == 32 else 0) + pixels


def assets(game, scenery):
    table = game.read("placeables", "2da").decode("cp1252").rstrip()
    first = int(table.splitlines()[-1].split()[0]) + 1
    appearances, resources = {}, {}
    rows = []
    for appearance, (name, (_, build_mesh)) in enumerate((MODELS | scenery | INTERACTIVE_MODELS).items(), first):
        appearances[name] = appearance
        rows.append(f"{appearance} {name} 8932 {name} **** **** **** **** 0 1 0 **** **** 1")
        resources[f"{name}.mdl"] = build_mesh().mdl(name)
    resources["placeables.2da"] = (table + "\r\n" + "\r\n".join(rows) + "\r\n").encode("cp1252")
    for name, size, base, seed in (
        ("hvd_stone", 128, (163, 169, 185), 31),
        ("hvd_copper", 128, (101, 153, 143), 41),
        ("hvd_brass", 128, (208, 165, 93), 53),
        ("hvd_glass", 128, (99, 123, 213), 71),
        ("hvd_clouds", 256, (188, 201, 223), 83),
    ):
        resources[f"{name}.tga"] = texture(name, size, base, seed)
    # Original stone surfaces for the Castle Exterior chasm tiles in this module.
    # The game continues to supply the tile models and their walkmeshes.
    for stem, base, seed, slabs in (
        ("cobble01", (148, 155, 177), 113, True),
        ("grass01", (114, 123, 154), 131, False),
        ("grassrim01", (117, 124, 153), 137, False),
        ("grassrim02", (120, 126, 154), 139, False),
        ("cliff01", (89, 103, 136), 149, False),
        ("cliff02", (101, 115, 146), 151, False),
    ):
        resources[f"tcm02_{stem}.tga"] = texture(stem, 128, base, seed, slabs=slabs)
    # A single transparent DXT3 block removes the modeled vegetation from the cloud terraces.
    invisible = struct.pack("<4If", 4, 4, 4, 16, 0) + bytes(16)
    for stem in ("pt_grass01", "leaf01", "fern", "fern01", "treefol03", "treefol04", "bush01",
                 "plants", "bark01", "bark02"):
        resources[f"tcm02_{stem}.dds"] = invisible
    return appearances, resources
