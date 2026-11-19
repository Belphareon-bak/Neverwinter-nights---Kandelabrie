"""Native sky models and painted panoramas for the two sides of the observatory."""

from math import cos, exp, pi, sin, tau
import random
import struct

from art import Material, Mesh


def panorama(seed, upper, width=1024, height=512):
    """Paint a seamless longitude/elevation map with a cloud bank and a star band."""
    rng = random.Random(seed)
    stars = {}
    for i in range(2350 if upper else 1050):
        x, y = rng.randrange(width), rng.randrange(86 if upper else 119, height)
        hot = rng.randrange(43, 200)
        stars[x, y] = hot
        if i % 17 == 0:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                stars[(x + dx) % width, y + dy] = hot * .58

    angular = [tau * x / width for x in range(width)]
    ridge = [(.33 + .083 * sin(a + .31) + .041 * cos(2 * a - .33),
              .17 + .026 * sin(a * 3 + .37) + .022 * cos(a * 9)
              + .008 * sin(a * 19))
             for a in angular]
    pixels = bytearray()
    for y in range(height):
        v = y / (height - 1)
        horizon = exp(-((v - .215) * 6.2) ** 2)
        for x, theta in enumerate(angular):
            band, bank = ridge[x]
            folds = (.62 + .20 * sin(theta * 13 + sin(v * 37))
                     + .19 * sin(theta * 23 - v * 17))
            galaxy = exp(-((v - band) * 17.2) ** 2) * max(.05, folds) if upper else 0.0
            cloud = exp(-((v - bank) * 28.0) ** 2) * (.72 + .21 * sin(16 * theta + 17 * v)
                                                     + .11 * cos(31 * theta - 39 * v))
            light = stars.get((x, y), 0) * (1 - min(.91, cloud * .93))
            grain = (rng.random() - .5) * 3.5
            rgb = (11 + 17 * horizon + cloud * 91 + galaxy * 83 + light,
                   14 + 22 * horizon + cloud * 86 + galaxy * 61 + light,
                   30 + 36 * horizon + cloud * 100 + galaxy * 112 + light)
            pixels.extend(max(0, min(255, int(channel + grain))) for channel in reversed(rgb))
    header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, width, height, 24, 0)
    return header + pixels


def sky_model(name, bitmap):
    mesh = Mesh()
    material = Material((1, 1, 1), bitmap, (1, 1, 1))
    columns, rows, radius = 48, 26, 195.0
    low, high = -pi / 6, pi / 2
    def point(u, v):
        azimuth = u * tau
        elevation = low + (high - low) * v
        return (radius * cos(elevation) * cos(azimuth),
                radius * cos(elevation) * sin(azimuth),
                radius * sin(elevation))
    for j in range(rows):
        for i in range(columns):
            a, b, c, d = i / columns, (i + 1) / columns, j / rows, (j + 1) / rows
            uv = ((a, c), (a, d), (b, d), (b, c))
            mesh.polygon(material, [point(*pair) for pair in uv], uv)
    return mesh.mdl(name).replace(b"classification Other", b"classification Effect")


def sky_assets(game):
    base = game.read("skyboxes", "2da").rstrip()
    first = int(base.splitlines()[-1].split()[0]) + 1
    descriptions, resources, rows = {}, {}, []
    for index, (key, label) in enumerate((("rim", "Hvezdarna_Hory"), ("upper", "Hvezdarna_DruheNebe"))):
        ident = first + index
        model, bitmap = f"hvd_sky_{key}", f"hvd_pan_{key}"
        descriptions[key] = ident
        rows.append(f"{ident} {label} **** 0 {model} {model} {model} {model}")
        resources[f"{model}.mdl"] = sky_model(model, bitmap)
        resources[f"{bitmap}.tga"] = panorama(734 + index * 23, key == "upper")
    resources["skyboxes.2da"] = base + b"\r\n" + "\r\n".join(rows).encode("ascii") + b"\r\n"
    return descriptions, resources
